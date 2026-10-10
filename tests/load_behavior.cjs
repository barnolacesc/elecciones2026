const { test } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { run, percentile, validate } = require('../ops/load/client.cjs');

function config(target) {
  return { target, environment: 'local-rehearsal', readers: 4, think_seconds: [5, 10],
    seed: 19, asset_reload_fraction: 0, max_inflight: 4, request_timeout_ms: 100,
    scenario: { name: 'fixture', seconds: 0.1, start_spread_seconds: 0 },
    pages: ['/'], assets: ['/styles.css'] };
}
async function fixture(handler, execute) {
  const server = http.createServer(handler);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try { await execute(`http://127.0.0.1:${server.address().port}`); }
  finally { server.closeAllConnections(); await new Promise(resolve => server.close(resolve)); }
}

test('p95 uses the nearest-rank definition and empty observations stay unknown', () => {
  assert.equal(percentile([]), null);
  assert.equal(percentile(Array.from({ length: 100 }, (_, i) => i + 1)), 95);
});
test('defaults cannot direct a local rehearsal to a public target or a different origin path', () => {
  for (const url of ['https://public.example', 'http://127.0.0.1/path', 'http://user:pass@localhost',
    'http://127.0.0.1/?vote=secret']) assert.throws(() => validate(config(url)));
  assert.throws(() => validate({ ...config('https://approved.example'), environment: 'approved-live' }));
});
test('HTTP metrics distinguish hits, missing cache evidence, redirects, and error responses', async () => {
  for (const [status, cache] of [[200, 'HIT'], [200, null], [503, 'MISS'], [302, 'BYPASS']]) {
    let requests = 0;
    await fixture((req, resp) => {
      requests++;
      resp.writeHead(status, { ...(cache ? { 'X-Load-Cache': cache } : {}), Location: 'https://other.example' });
      resp.end('bytes');
    }, async target => {
      const result = await run(config(target));
      assert.equal(result.offered, 4); assert.equal(result.completed, 4);
      assert.equal(result.status[status], 4);
      assert.equal(result.cache[cache || 'UNKNOWN'], 4);
      assert.equal(result.body_bytes, 20); assert.equal(result.readers_served, 4);
      assert.equal(requests, 4); // No redirects, retries, or extra probes.
    });
  }
});
test('absolute request deadline records failed requests; overload cannot silently reduce demand', async () => {
  await fixture(() => {}, async target => {
    const result = await run({ ...config(target), max_inflight: 1, request_timeout_ms: 20 });
    assert.equal(result.offered, 4); assert.equal(result.sent, 1);
    assert.equal(result.dropped, 3); assert.equal(result.network_errors, 1);
    assert.equal(result.completed, 0); assert.equal(result.cache_hit_p95_ms, null);
  });
});

test('distributed generators preserve the total reader population and merge raw latency observations', async () => {
  const { runDistributed } = require('../ops/load/client.cjs');
  await fixture((req, resp) => { resp.writeHead(200, { 'X-Load-Cache': 'HIT' }); resp.end('bytes'); }, async target => {
    const result = await runDistributed({ ...config(target), readers: 8, generators: 2 });
    assert.equal(result.readers, 8); assert.equal(result.readers_served, 8);
    assert.equal(result.offered, 8); assert.equal(result.completed, 8);
    assert.equal(result.cache.HIT, 8); assert.equal(result.body_bytes, 40);
    assert.equal(result.dropped, 0); assert.equal(result.generators, 2);
    assert.ok(result.response_p95_ms >= 0);
    assert.ok(result.peak_inflight_upper_bound <= 8);
  });
});
