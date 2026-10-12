/* Local synthetic delivery observations; no visitor instrumentation or release claim. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const {percentile} = require('../ops/load/client.cjs');
const base = process.env.QUIZ_TEST_URL || 'http://127.0.0.1:48775';
const target = new URL(base);
assert.ok(['127.0.0.1', 'localhost', '[::1]'].includes(target.hostname)
  && target.pathname === '/' && !target.search && !target.hash && !target.username && !target.password,
  'Performance checks require a loopback origin');

(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.QUIZ_CHROMIUM ? {executablePath: process.env.QUIZ_CHROMIUM} : {})});
  const report = {package: 'E4.4', environment: 'local mock synthetic browser',
    profile: {latency_ms: 150, download_kbps: 1600, upload_kbps: 750, cpu_slowdown: 4},
    delivery_target_ms: 500, measurements: [], production_acceptance: 'pending',
    limits: ['Five samples per case; p95 is the largest sample, not a population estimate.',
      'Chromium network/CPU emulation on local HTTP excludes production DNS, TLS, geography, and CDN.',
      'Mock bundle sizes do not establish delivery performance for reviewed real source records.',
      'Observed local target comparisons are not service approval or full accessibility acceptance.']};
  try {
    for (const width of [360, 390, 430]) for (const cache of ['cold', 'warm']) {
      const context = await browser.newContext({viewport: {width, height: 844}, hasTouch: true});
      await context.addInitScript(() => {
        performance.setResourceTimingBufferSize(200);
        const observer = new MutationObserver(() => {
          if (window.QuizBundle && window.QuizEngine
            && [...document.querySelectorAll('#quiz-app button')].some(e => e.textContent === 'Empezar')) {
            window.fixtureQuizReadyAt = performance.now(); observer.disconnect();
          }
        });
        observer.observe(document, {childList: true, subtree: true});
      });
      const page = await context.newPage();
      const cdp = await context.newCDPSession(page);
      await cdp.send('Network.enable');
      await cdp.send('Network.setCacheDisabled', {cacheDisabled: cache === 'cold'});
      await cdp.send('Network.emulateNetworkConditions', {offline: false, latency: 150,
        downloadThroughput: 1600 * 1000 / 8, uploadThroughput: 750 * 1000 / 8});
      await cdp.send('Emulation.setCPUThrottlingRate', {rate: 4});
      if (cache === 'warm') await page.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
      const samples = [];
      for (let i = 0; i < 5; i++) {
        await page.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
        await page.waitForFunction(() => Number.isFinite(window.fixtureQuizReadyAt));
        const observed = await page.evaluate(() => {
          const navigation = performance.getEntriesByType('navigation')[0];
          const resources = performance.getEntriesByType('resource');
          return {ready_ms: window.fixtureQuizReadyAt,
            response_start_ms: navigation.responseStart,
            dom_content_loaded_ms: navigation.domContentLoadedEventEnd,
            load_ms: navigation.loadEventEnd,
            fcp_ms: performance.getEntriesByName('first-contentful-paint')[0]?.startTime ?? null,
            transfer_bytes: navigation.transferSize + resources.reduce((sum, resource) => sum + resource.transferSize, 0),
            resources: resources.map(resource => ({path: new URL(resource.name).pathname,
              start_ms: resource.startTime, response_end_ms: resource.responseEnd,
              transferred_bytes: resource.transferSize, decoded_bytes: resource.decodedBodySize})),
            mode: window.QuizBundle.mode,
            bundle_before_ready: ['quiz-data.', 'quiz-engine.', 'quiz-ui.'].every(name =>
              resources.some(resource => resource.name.includes(name) && resource.responseEnd <= window.fixtureQuizReadyAt))};
        });
        assert.equal(observed.mode, 'mock', 'Only fictional fixtures are measured');
        assert.equal(observed.bundle_before_ready, true, 'Complete bundle must arrive before accepting answers');
        await page.getByRole('button', {name: 'Empezar', exact: true}).click();
        assert.equal(await page.getByRole('radio').count(), 5);
        samples.push(observed);
      }
      const p95 = percentile(samples.map(sample => sample.ready_ms));
      report.measurements.push({width, cache, samples, ready_p95_ms: p95, local_delivery_target_met: p95 < 500});
      console.log(`${width}px ${cache}: ready p95 ${p95.toFixed(1)} ms; local target ${p95 < 500 ? 'met' : 'not met'}.`);
      await context.close();
    }
    const output = process.env.QUIZ_PERFORMANCE_EVIDENCE || 'build/quiz-performance.json';
    fs.mkdirSync(path.dirname(output), {recursive: true});
    fs.writeFileSync(output, `${JSON.stringify(report, null, 2)}\n`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
