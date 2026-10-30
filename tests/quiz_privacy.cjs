/* Fixture-only browser transport checks. No participant data or real source approvals. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.QUIZ_TEST_URL || 'http://127.0.0.1:48775';
const sourceUrl = 'https://quiz-source.invalid/transport-fixture#page=2';
const evidence = {scope: 'E4.4 fixture browser transport only', cases: [],
  limits: ['No real citation approval or participant answers.', 'No CDN, origin, monitoring, or provider privacy audit.']};

async function fill(page, label) {
  await page.getByRole('button', {name: 'Empezar', exact: true}).click();
  for (let i = 0; i < 8; i++) {
    await page.getByRole('radio', {name: label, exact: true}).check();
    await page.getByRole('button', {name: 'Siguiente', exact: true}).click();
  }
  await page.getByRole('button', {name: 'Ver resultado', exact: true}).click();
}

(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.QUIZ_CHROMIUM ? {executablePath: process.env.QUIZ_CHROMIUM} : {})});
  try {
    let referenceResources;
    for (const testCase of [
      {name: 'native share, agreement fixture', mode: 'native', answer: 'Totalmente de acuerdo'},
      {name: 'native share, opposition fixture', mode: 'native', answer: 'Totalmente en desacuerdo'},
      {name: 'native share cancelled', mode: 'cancel', answer: 'Más bien en desacuerdo'},
      {name: 'copy-link fallback', mode: 'copy', answer: 'Ni de acuerdo ni en desacuerdo'},
      {name: 'manual link fallback', mode: 'manual', answer: 'Más bien de acuerdo'}
    ]) {
      const context = await browser.newContext({viewport: {width: 390, height: 844}});
      await context.addInitScript(mode => {
        window.fixtureSharePayloads = [];
        window.fixtureCopiedLinks = [];
        Object.defineProperty(navigator, 'share', {configurable: true,
          value: ['native', 'cancel'].includes(mode) ? async payload => {
            window.fixtureSharePayloads.push(payload);
            if (mode === 'cancel') throw new DOMException('Cancelled', 'AbortError');
          } : undefined});
        Object.defineProperty(navigator, 'clipboard', {configurable: true,
          value: mode === 'copy' ? {writeText: async url => { window.fixtureCopiedLinks.push(url); }} : undefined});
      }, testCase.mode);
      const page = await context.newPage();
      const requests = [], consoleOutput = [], errors = [];
      page.on('request', request => requests.push(request));
      page.on('console', message => consoleOutput.push(message.text()));
      page.on('pageerror', error => errors.push(String(error)));
      await page.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
      const initialRequests = requests.length;
      const resources = requests.map(request => {
        const url = new URL(request.url());
        assert.equal(url.origin, new URL(base).origin, 'All delivery requests must be local');
        assert.equal(url.search, '', 'Static delivery must not include answer parameters');
        assert.equal(request.method(), 'GET');
        assert.equal(request.postData(), null);
        return url.pathname;
      }).sort();
      assert.ok(resources.some(resource => /quiz-data\./.test(resource)), 'Complete bundle must arrive before interaction');
      if (referenceResources) assert.deepEqual(resources, referenceResources, 'Resources must be independent of the fixture answer set');
      else referenceResources = resources;
      await fill(page, testCase.answer);
      await page.getByText('Cambiar el peso de los temas', {exact: true}).click();
      await page.locator('#weight-housing').selectOption('2');
      await page.getByRole('button', {name: 'Cambiar respuestas', exact: true}).click();
      await page.getByRole('button', {name: 'Cambiar pregunta 1', exact: true}).click();
      await page.getByRole('radio', {name: 'Más bien en desacuerdo', exact: true}).check();
      await page.getByRole('button', {name: 'Ver resultado', exact: true}).click();
      await page.locator('.quiz-result summary').first().click();
      const canonical = await page.locator('link[rel="canonical"]').getAttribute('href');
      const canonicalUrl = new URL(canonical);
      assert.equal(canonicalUrl.pathname, '/cuestionario/');
      assert.equal(canonicalUrl.search, ''); assert.equal(canonicalUrl.hash, '');
      await page.getByRole('button', {name: 'Compartir el cuestionario', exact: true}).click();
      const captured = await page.evaluate(() => ({shared: window.fixtureSharePayloads, copied: window.fixtureCopiedLinks}));
      if (testCase.mode === 'native' || testCase.mode === 'cancel') {
        assert.deepEqual(captured, {shared: [{title: 'Cuestionario de coincidencia', url: canonical}], copied: []});
        if (testCase.mode === 'cancel') {
          await page.getByRole('button', {name: 'Compartir el cuestionario', exact: true}).click();
          assert.equal(await page.locator('#quiz-share-fallback').count(), 1,
            'Repeated cancellation must not duplicate the fallback');
          assert.equal(await page.locator('#quiz-share-fallback').innerText(), `Enlace al cuestionario: ${canonical}`);
          assert.match(await page.locator('#quiz-status').innerText(), /No se ha compartido/);
        }
      } else if (testCase.mode === 'copy') {
        assert.deepEqual(captured, {shared: [], copied: [canonical]});
      } else {
        assert.deepEqual(captured, {shared: [], copied: []});
        assert.match(await page.locator('#quiz-app').innerText(), new RegExp(`Enlace al cuestionario: ${canonical.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`));
      }
      await page.getByRole('button', {name: 'Borrar respuestas', exact: true}).click();
      assert.equal(requests.length, initialRequests, 'Complete interaction and sharing must cause zero application requests');
      assert.equal(new URL(page.url()).search, ''); assert.equal(new URL(page.url()).hash, '');
      assert.equal(await page.locator('form, [type="password"], [type="email"]').count(), 0);
      assert.deepEqual(consoleOutput, []); assert.deepEqual(errors, []);
      evidence.cases.push({name: testCase.name, passed: true, staticResources: resources,
        interactionRequests: 0, shareContainsOnlyGenericLink: true, consoleMessages: 0});
      await context.close();
    }

    // Intercepted nonpolitical metadata exercises the production link renderer only.
    // The offline editorial validator would reject this fixture; it is never built or published.
    const context = await browser.newContext();
    const page = await context.newPage();
    let citationRequest;
    await context.route('https://quiz-source.invalid/**', async route => {
      citationRequest = route.request();
      await route.fulfill({status: 200, contentType: 'text/html',
        body: '<!doctype html><title>Transport test only</title><p>No programme or political claim.</p>'});
    });
    await page.route('**/quiz-data.*.js', async route => {
      const response = await route.fetch();
      const text = await response.text();
      const bundle = JSON.parse(text.slice(text.indexOf('=') + 1).trim().replace(/;$/, ''));
      bundle.mode = 'reviewed'; bundle.election_id = 'transport-fixture'; bundle.version = 'transport-only';
      for (const party of bundle.parties) for (const position of party.positions) {
        if (position.value !== null) position.source = {
          statement_id: 'not-a-statement', programme_id: 'not-a-programme', version: 'transport-only',
          sha256: '0'.repeat(64), page: '2', section: '', review_date: 'No editorial review: test only',
          rights_status: 'Not approved: test only', url: sourceUrl, qualifications: [],
          summary: 'Prueba de navegación. No representa un programa político.'
        };
      }
      await route.fulfill({response, body: `window.QuizBundle = ${JSON.stringify(bundle)};\n`});
    });
    await page.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
    await page.getByRole('button', {name: 'Empezar', exact: true}).click();
    await page.locator('#quiz-app summary').first().click();
    const link = page.getByRole('link', {name: 'Abrir fuente oficial (ventana nueva)', exact: true}).first();
    assert.equal(await link.getAttribute('referrerpolicy'), 'no-referrer');
    assert.equal(await link.getAttribute('rel'), 'noopener noreferrer');
    const popupPromise = context.waitForEvent('page');
    await link.click();
    const popup = await popupPromise;
    await popup.waitForLoadState();
    assert.equal(citationRequest.url(), sourceUrl.split('#')[0]);
    assert.equal(citationRequest.method(), 'GET'); assert.equal(citationRequest.postData(), null);
    assert.equal((await citationRequest.allHeaders()).referer, undefined);
    assert.equal(await popup.evaluate(() => window.opener === null), true);
    evidence.cases.push({name: 'intercepted nonpolitical source transport', passed: true,
      referrerAbsent: true, openerAbsent: true, requestContainsOnlyPublicTestPath: true});
    await context.close();
    if (process.env.QUIZ_PRIVACY_EVIDENCE) {
      const output = process.env.QUIZ_PRIVACY_EVIDENCE;
      fs.mkdirSync(path.dirname(output), {recursive: true});
      fs.writeFileSync(output, `${JSON.stringify(evidence, null, 2)}\n`);
    }
    console.log(`PASS ${evidence.cases.length} quiz privacy cases: answer-independent resources, zero interaction requests, generic sharing, and no-referrer/no-opener source transport.`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
