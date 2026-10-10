/* E3.4: deterministic reader schedules with bounded, persistent HTTP connections. */
'use strict';
const http = require('node:http');
const https = require('node:https');
const fs = require('node:fs');
const { performance, monitorEventLoopDelay } = require('node:perf_hooks');
const { Worker, isMainThread, parentPort, workerData } = require('node:worker_threads');

function percentile(values, fraction = 0.95) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.ceil(sorted.length * fraction) - 1];
}
function random(seed) {
  let state = seed >>> 0;
  return () => { state = (Math.imul(1664525, state) + 1013904223) >>> 0; return state / 4294967296; };
}
function validate(config) {
  const target = new URL(config.target);
  if (!['http:', 'https:'].includes(target.protocol) || target.username || target.password ||
      target.search || target.hash || target.pathname !== '/') throw new Error('Target must be an HTTP(S) origin');
  if (config.environment !== 'approved-live' && !['127.0.0.1', '[::1]', 'localhost'].includes(target.hostname)) {
    throw new Error('Local rehearsal accepts only a loopback target');
  }
  if (config.environment === 'approved-live' && (!config.authorization_reference || target.protocol !== 'https:')) {
    throw new Error('Live runs require HTTPS and an authorization reference');
  }
  const integers = ['readers', 'max_inflight', 'request_timeout_ms'];
  for (const key of integers) if (!Number.isInteger(config[key]) || config[key] < 1) throw new Error(`Invalid ${key}`);
  if (config.readers > 10000 || config.max_inflight > 2048 || !Number.isFinite(config.scenario.seconds) || config.scenario.seconds > 600 ||
      config.scenario.seconds <= 0) throw new Error('Run exceeds bounded workload limits');
  const [low, high] = config.think_seconds;
  if (!(low >= 5 && high >= low && high <= 10)) throw new Error('Reader intervals must be within 5–10 seconds');
  if (!(config.asset_reload_fraction >= 0 && config.asset_reload_fraction <= 1)) throw new Error('Invalid resource reload fraction');
  if (!Number.isFinite(config.scenario.start_spread_seconds) || config.scenario.start_spread_seconds < 0 ||
      config.scenario.start_spread_seconds >= config.scenario.seconds) throw new Error('Invalid start spread');
  for (const path of [...config.pages, ...config.assets]) {
    if (!path.startsWith('/') || path.startsWith('//') || path.includes('#') || path.includes('..')) throw new Error('Invalid workload path');
  }
  if (!config.pages.length || !config.assets.length) throw new Error('Workload paths are required');
  return target;
}

async function run(config) {
  const target = validate(config);
  const transport = target.protocol === 'https:' ? https : http;
  const agent = new transport.Agent({ keepAlive: true, maxSockets: config.max_inflight, maxFreeSockets: 64 });
  const rng = random(config.seed);
  const started = performance.now() + Math.max(0, (config.start_epoch_ms || Date.now()) - Date.now());
  const ends = started + config.scenario.seconds * 1000;
  const lag = monitorEventLoopDelay({ resolution: 10 });
  lag.enable();
  let active = 0, peak = 0;
  const pending = new Set();
  const totals = { offered: 0, sent: 0, completed: 0, dropped: 0, network_errors: 0,
    body_bytes: 0, status: {}, cache: {}, classes: {}, peak_inflight: 0 };
  const latencies = [], scheduledLatencies = [], schedulingLag = [], hitLatencies = [];
  const buckets = {};
  const arrivals = [];
  for (let reader = 0; reader < config.readers; reader++) {
    const interval = (config.think_seconds[0] + rng() * (config.think_seconds[1] - config.think_seconds[0])) * 1000;
    const offset = rng() * config.scenario.start_spread_seconds * 1000;
    for (let due = offset; due < config.scenario.seconds * 1000; due += interval) {
      const page = config.pages[Math.floor(rng() * config.pages.length)];
      arrivals.push({ due, path: page, kind: 'html', reader });
      if (rng() < config.asset_reload_fraction) {
        for (const path of config.assets) arrivals.push({ due, path, kind: 'asset', reader });
      }
    }
  }
  arrivals.sort((a, b) => a.due - b.due);
  const readersServed = new Set();
  function dispatch(event) {
    totals.offered++;
    const now = performance.now();
    const late = Math.max(0, now - started - event.due);
    schedulingLag.push(late);
    if (active >= config.max_inflight) { totals.dropped++; return; }
    totals.sent++; active++; peak = Math.max(peak, active); readersServed.add(event.reader);
    let resolve;
    const done = new Promise(r => { resolve = r; });
    pending.add(done);
    let settled = false, received = 0;
    const requestStart = performance.now();
    const finish = (status, cache) => {
      if (settled) return;
      settled = true;
      active--; pending.delete(done);
      const duration = performance.now() - requestStart;
      latencies.push(duration); scheduledLatencies.push(duration + late);
      if (!status) totals.network_errors++;
      else {
        totals.completed++; totals.status[status] = (totals.status[status] || 0) + 1;
        totals.cache[cache] = (totals.cache[cache] || 0) + 1;
        const counts = totals.classes[event.kind] ||= { responses: 0, hits: 0, unknown: 0 };
        counts.responses++;
        if (cache === 'HIT') { counts.hits++; hitLatencies.push(duration); }
        if (cache === 'UNKNOWN') counts.unknown++;
      }
      totals.body_bytes += received;
      const second = Math.floor((requestStart - started) / 1000);
      const bucket = buckets[second] ||= { requests: 0, body_bytes: 0, errors: 0 };
      bucket.requests++; bucket.body_bytes += received;
      if (!status || status >= 400) bucket.errors++;
      resolve();
    };
    const req = transport.get(new URL(event.path, target), { agent,
      headers: { 'User-Agent': 'elecciones2026-load-rehearsal/1', 'Accept-Encoding': 'gzip' } }, resp => {
      const cache = String(resp.headers[config.environment === 'approved-live' ? 'cf-cache-status' : 'x-load-cache'] || 'UNKNOWN').toUpperCase();
      resp.on('data', chunk => { received += chunk.length; });
      resp.on('end', () => finish(resp.statusCode, cache));
      resp.on('error', () => finish(0, 'UNKNOWN'));
    });
    // Absolute deadline includes queued connection and TLS time. Never retry or follow redirects.
    const timeout = setTimeout(() => req.destroy(new Error('Request deadline exceeded')), config.request_timeout_ms);
    req.on('error', () => finish(0, 'UNKNOWN'));
    req.on('close', () => clearTimeout(timeout));
  }
  let next = 0;
  await new Promise(resolve => {
    const tick = () => {
      const now = performance.now();
      while (next < arrivals.length && arrivals[next].due <= now - started) dispatch(arrivals[next++]);
      if (next >= arrivals.length || now >= ends) { resolve(); return; }
      setTimeout(tick, Math.min(5, Math.max(1, arrivals[next].due - (now - started))));
    };
    tick();
  });
  await Promise.all([...pending]);
  agent.destroy(); lag.disable();
  totals.peak_inflight = peak;
  return { ...totals, scenario: config.scenario, readers: config.readers, readers_served: readersServed.size,
    measurement_seconds: config.scenario.seconds, elapsed_seconds: (performance.now() - started) / 1000,
    offered_rps: totals.offered / config.scenario.seconds, achieved_rps: totals.completed / config.scenario.seconds,
    response_p95_ms: percentile(latencies), scheduled_response_p95_ms: percentile(scheduledLatencies),
    cache_hit_p95_ms: percentile(hitLatencies), scheduling_lag_p95_ms: percentile(schedulingLag),
    event_loop_p95_ms: lag.percentile(95) / 1e6, body_mbps: totals.body_bytes * 8 / config.scenario.seconds / 1e6,
    seconds: buckets, generator_rss_bytes: process.memoryUsage().rss,
    ...(config.capture_samples ? { _samples: { latencies, scheduledLatencies, schedulingLag, hitLatencies } } : {}) };
}
async function runDistributed(config) {
  validate(config);
  const count = config.generators || 1;
  if (!Number.isInteger(count) || count < 1 || count > 8 || count > config.readers ||
      count * config.max_inflight > 4096) throw new Error('Invalid generator capacity');
  if (count === 1) return { ...await run(config), generators: 1 };
  const workers = [];
  const start = Date.now() + 500;
  try {
    const results = await Promise.all(Array.from({ length: count }, (_, shard) => new Promise((resolve, reject) => {
      const readers = Math.floor(config.readers / count) + (shard < config.readers % count ? 1 : 0);
      const worker = new Worker(__filename, { workerData: { ...config, readers, seed: config.seed + shard,
        start_epoch_ms: start, capture_samples: true } });
      workers.push(worker);
      worker.once('message', resolve);
      worker.once('error', reject);
      worker.once('exit', code => { if (code !== 0) reject(new Error(`Generator exited ${code}`)); });
    })));
    const merged = { scenario: config.scenario, readers: config.readers, generators: count,
      measurement_seconds: config.scenario.seconds, elapsed_seconds: (Date.now() - start) / 1000,
      status: {}, cache: {}, classes: {}, seconds: {}, generator_rss_bytes: process.memoryUsage().rss,
      peak_inflight_upper_bound: results.reduce((sum, r) => sum + r.peak_inflight, 0),
      max_worker_event_loop_p95_ms: Math.max(...results.map(r => r.event_loop_p95_ms)) };
    for (const key of ['offered', 'sent', 'completed', 'dropped', 'network_errors', 'body_bytes', 'readers_served']) {
      merged[key] = results.reduce((sum, result) => sum + result[key], 0);
    }
    for (const key of ['status', 'cache']) {
      for (const result of results) for (const [name, value] of Object.entries(result[key])) {
        merged[key][name] = (merged[key][name] || 0) + value;
      }
    }
    for (const key of ['classes', 'seconds']) {
      for (const result of results) for (const [name, values] of Object.entries(result[key])) {
        const target = merged[key][name] ||= {};
        for (const [metric, value] of Object.entries(values)) target[metric] = (target[metric] || 0) + value;
      }
    }
    for (const [metric, sample] of Object.entries({ response_p95_ms: 'latencies',
      scheduled_response_p95_ms: 'scheduledLatencies', scheduling_lag_p95_ms: 'schedulingLag', cache_hit_p95_ms: 'hitLatencies' })) {
      merged[metric] = percentile(results.flatMap(result => result._samples[sample]));
    }
    merged.offered_rps = merged.offered / config.scenario.seconds;
    merged.achieved_rps = merged.completed / config.scenario.seconds;
    merged.body_mbps = merged.body_bytes * 8 / config.scenario.seconds / 1e6;
    return merged;
  } finally { await Promise.all(workers.map(worker => worker.terminate())); }
}
if (require.main === module) {
  if (!isMainThread) {
    run(workerData).then(result => parentPort.postMessage(result)).catch(error => { throw error; });
  } else {
    const config = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    runDistributed(config).then(result => fs.writeFileSync(process.argv[3], JSON.stringify(result, null, 2) + '\n'))
      .catch(error => { process.stderr.write(error.message + '\n'); process.exitCode = 1; });
  }
}
module.exports = { run, runDistributed, percentile, validate };
