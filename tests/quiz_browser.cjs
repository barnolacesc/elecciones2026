/* Complete mock flow regression. This is not a WCAG conformance audit. */
const assert = require('node:assert/strict');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.QUIZ_TEST_URL || 'http://127.0.0.1:48775';
const widths = [320, 360, 390, 430];
const displayCases = [
  ...widths.map(height => ({name: `landscape 844x${height}`, width: 844, height})),
  {name: '200% root text size', width: 390, height: 844, css: 'html { font-size: 200% !important; }'},
  {name: 'text spacing', width: 390, height: 844, css: `
    .quiz-shell * { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; }
    .quiz-shell p { margin-bottom: 2em !important; }`},
  {name: '320px reflow with text spacing', width: 320, height: 256, css: `
    .quiz-shell * { line-height: 1.5 !important; letter-spacing: .12em !important; word-spacing: .16em !important; }
    .quiz-shell p { margin-bottom: 2em !important; }`}
];
const layout = () => {
  const scope = document.querySelector('.quiz-shell');
  const visible = e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().height > 0;
  return {
    clipped: [...scope.querySelectorAll('*')].filter(visible).filter(e => {
      const r = e.getBoundingClientRect(); return r.left < -1 || r.right > innerWidth + 1;
    }).map(e => e.tagName),
    short: [...scope.querySelectorAll('button,select,input,a,summary')].filter(visible).filter(e => {
      const r = e.getBoundingClientRect(); return r.height < 43.5 || r.width < 43.5;
    }).map(e => e.tagName),
    scroll: document.documentElement.scrollWidth
  };
};
async function checkLayout(page, name, width) {
  const observed = await page.evaluate(layout);
  assert.deepEqual(observed.clipped, [], `${name}: overflow`);
  assert.deepEqual(observed.short, [], `${name}: targets below 44px`);
  assert.ok(observed.scroll <= width, `${name}: horizontal scrolling`);
}
async function checkKeyboard(page) {
  await page.locator('#quiz-app h1').focus();
  const visited = new Set();
  for (let i = 0; i < 150; i++) {
    await page.keyboard.press('Tab');
    const focused = await page.evaluate(() => {
      const e = document.activeElement;
      if (!e.closest('.quiz-shell')) return null;
      const r = e.getBoundingClientRect();
      const x = Math.max(0, Math.min(innerWidth - 1, r.left + r.width / 2));
      const y = Math.max(0, Math.min(innerHeight - 1, r.top + r.height / 2));
      const top = document.elementFromPoint(x, y);
      const style = getComputedStyle(e);
      return {key: [...document.querySelectorAll('*')].indexOf(e),
        visible: r.bottom > 0 && r.top < innerHeight && (top === e || e.contains(top)),
        outline: style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) > 0};
    });
    if (!focused) break;
    if (visited.has(focused.key)) break;
    visited.add(focused.key);
    assert.equal(focused.visible, true, 'Keyboard focus must be visible and unobscured');
    assert.equal(focused.outline, true, 'Keyboard focus must have a visible outline');
  }
  assert.ok(visited.size > 0, 'Keyboard traversal must reach quiz controls');
}
(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.QUIZ_CHROMIUM ? {executablePath: process.env.QUIZ_CHROMIUM} : {})});
  try {
    for (const width of widths) {
      const context = await browser.newContext({viewport: {width, height: 844}, hasTouch: true});
      const page = await context.newPage();
      const requests = [], errors = [], output = [];
      page.on('request', r => requests.push(r.url()));
      page.on('pageerror', e => errors.push(String(e)));
      page.on('console', m => output.push(m.text()));
      await page.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
      assert.match(await page.locator('.quiz-notice').innerText(), /ficticios/);
      const initialRequests = requests.length;
      await page.getByRole('button', {name: 'Empezar', exact: true}).click();
      for (let i = 0; i < 8; i++) {
        await page.getByRole('radio', {name: 'Totalmente de acuerdo', exact: true}).check();
        assert.match(await page.locator('.quiz-kicker').innerText(), new RegExp(`Pregunta ${i + 1} de 16`));
        const observed = await page.evaluate(layout);
        assert.deepEqual(observed.clipped, [], `${width}: question overflow`);
        assert.deepEqual(observed.short, [], `${width}: target size`);
        assert.ok(observed.scroll <= width);
        await page.getByRole('button', {name: 'Siguiente', exact: true}).click();
      }
      for (let i = 8; i < 15; i++) {
        await page.getByRole('button', {name: 'No lo sé / Omitir', exact: true}).click();
      }
      await page.getByRole('button', {name: 'Ver resultado', exact: true}).click();
      assert.equal(await page.locator('.quiz-review').count(), 0, 'Finishing must not require review');
      assert.equal(await page.locator('.quiz-score').count(), 2);
      if (width === 390 && process.env.QUIZ_SCREENSHOT) await page.screenshot({path: process.env.QUIZ_SCREENSHOT});
      assert.match(await page.locator('.quiz-result').last().innerText(), /Cobertura insuficiente/);
      await page.getByText('Cambiar el peso de los temas', {exact: true}).click();
      await page.locator('#weight-housing').selectOption('2');
      assert.equal(await page.locator('#weight-housing').evaluate(e => e === document.activeElement), true);
      await page.getByRole('button', {name: 'Cambiar respuestas', exact: true}).click();
      assert.equal(await page.locator('.quiz-review li').count(), 16);
      await page.getByRole('button', {name: 'Cambiar pregunta 1', exact: true}).click();
      await page.getByRole('radio', {name: 'Totalmente en desacuerdo', exact: true}).check();
      await page.getByRole('button', {name: 'Revisar respuestas', exact: true}).click();
      await page.getByRole('button', {name: 'Continuar y ver resultado', exact: true}).click();
      assert.match(await page.locator('.quiz-result').first().innerText(), /Antes:.*Ahora:/);
      await page.locator('.quiz-result summary').first().click();
      const explanation = await page.locator('.quiz-result').first().innerText();
      assert.match(explanation, /Tu respuesta: Totalmente en desacuerdo/);
      assert.match(explanation, /Posición de Ejemplo A \(ficticio\): A favor \(dato ficticio\)/);
      assert.match(explanation, /Ha bajado/);
      assert.match(explanation, /Coincidencia en esta pregunta: 0 %/);
      assert.match(explanation, /este tema representa el 40 % del cálculo/);
      assert.doesNotMatch(explanation, /tu respuesta -1|posición 1/);
      const observed = await page.evaluate(layout);
      assert.deepEqual(observed.clipped, [], `${width}: result overflow`);
      assert.deepEqual(observed.short, [], `${width}: result targets`);
      assert.equal(requests.length, initialRequests, 'Answers and scoring must not generate requests');
      assert.equal(new URL(page.url()).search, ''); assert.equal(new URL(page.url()).hash, '');
      assert.deepEqual(await page.evaluate(() => ({local: localStorage.length, session: sessionStorage.length})), {local: 0, session: 0});
      assert.deepEqual(await page.evaluate(async () => ({databases: await indexedDB.databases(),
        caches: await caches.keys(), workers: (await navigator.serviceWorker.getRegistrations()).length,
        history: history.state})), {databases: [], caches: [], workers: 0, history: null});
      assert.deepEqual(await context.cookies(), []);
      assert.deepEqual(errors, []); assert.deepEqual(output, []);
      const second = await context.newPage(); await second.goto(`${base}/cuestionario/`);
      assert.equal(await second.locator('.quiz-score').count(), 0); await second.close();
      await page.getByRole('button', {name: 'Borrar respuestas', exact: true}).click();
      assert.equal(await page.locator('.quiz-score').count(), 0);
      await page.getByRole('button', {name: 'Empezar', exact: true}).click();
      assert.equal(await page.locator('input:checked').count(), 0);
      assert.match(await page.locator('#quiz-app').innerText(), /sin responder se contarán como omitidas/);
      await page.getByRole('button', {name: 'Ver resultado', exact: true}).click();
      assert.equal(await page.locator('.quiz-review').count(), 0);
      assert.match(await page.locator('#quiz-app').innerText(), /No hay respuestas suficientes/);
      await page.getByRole('button', {name: 'Cambiar respuestas', exact: true}).click();
      await page.getByRole('button', {name: 'Cambiar pregunta 16', exact: true}).click();
      await page.getByRole('button', {name: 'No lo sé / Omitir', exact: true}).click();
      assert.equal(await page.locator('.quiz-review').count(), 0, 'Skipping the last item must open results directly');
      await page.getByRole('button', {name: 'Cambiar respuestas', exact: true}).click();
      await page.getByRole('button', {name: 'Cambiar pregunta 1', exact: true}).click();
      await page.getByRole('radio', {name: 'Totalmente de acuerdo', exact: true}).check();
      await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true})));
      assert.equal(await page.getByRole('button', {name: 'Empezar', exact: true}).count(), 1);
      await page.reload(); assert.equal(await page.locator('.quiz-score').count(), 0);
      await page.getByRole('button', {name: 'Empezar', exact: true}).click();
      await page.getByRole('radio', {name: 'Totalmente de acuerdo', exact: true}).check();
      await page.goto(`${base}/metodo/`); await page.goBack();
      assert.equal(await page.getByRole('button', {name: 'Empezar', exact: true}).count(), 1);
      await context.close();
      console.log(`PASS ${width}px: direct finish/early finish/optional review/edit/weights/result/reset, targets, no overflow, no interaction requests, storage, tab isolation, restore/reload.`);
    }
    for (const display of displayCases) {
      const context = await browser.newContext({viewport: {width: display.width, height: display.height}, reducedMotion: 'reduce'});
      const page = await context.newPage();
      await page.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
      const initialTextSize = await page.locator('#quiz-app p').first().evaluate(e => parseFloat(getComputedStyle(e).fontSize));
      if (display.css) await page.addStyleTag({content: display.css});
      if (display.name === '200% root text size') {
        const resized = await page.locator('#quiz-app p').first().evaluate(e => parseFloat(getComputedStyle(e).fontSize));
        assert.equal(resized, initialTextSize * 2, 'Text must actually double in size');
      }
      const check = async stage => {
        await checkLayout(page, `${display.name}: ${stage}`, display.width);
        if (display.name === 'text spacing') await checkKeyboard(page);
      };
      await check('introduction');
      await page.getByRole('button', {name: 'Empezar', exact: true}).click();
      await page.locator('#quiz-app details').evaluateAll(elements => elements.forEach(e => { e.open = true; }));
      await check('question with sources');
      await page.getByRole('button', {name: 'Ver resultado', exact: true}).click();
      await check('insufficient answers');
      await page.getByRole('button', {name: 'Cambiar respuestas', exact: true}).click();
      await check('optional review');
      await page.getByRole('button', {name: 'Cambiar pregunta 1', exact: true}).click();
      for (let i = 0; i < 8; i++) {
        await page.getByRole('radio', {name: 'Totalmente de acuerdo', exact: true}).check();
        await page.getByRole('button', {name: 'Siguiente', exact: true}).click();
      }
      await page.getByRole('button', {name: 'Ver resultado', exact: true}).click();
      await page.locator('.quiz-shell details').evaluateAll(elements => elements.forEach(e => { e.open = true; }));
      await check('results with weights, explanations, sources, and method');
      if (display.name === '320px reflow with text spacing') {
        await page.getByRole('button', {name: 'Cambiar respuestas', exact: true}).click();
        await page.getByRole('button', {name: 'Cambiar pregunta 9', exact: true}).click();
        for (let i = 8; i < 16; i++) {
          await page.getByRole('radio', {name: 'Totalmente de acuerdo', exact: true}).check();
          await page.getByRole('button', {name: i === 15 ? 'Ver resultado' : 'Siguiente', exact: true}).click();
        }
        assert.match(await page.locator('.quiz-result').first().innerText(), /Has respondido las 16 preguntas/);
        assert.doesNotMatch(await page.locator('.quiz-result').first().innerText(), /Si completas las/);
        await check('complete answers without skipped-item scenarios');
      }
      await context.close();
      console.log(`PASS ${display.name}: introduction/question/sources/insufficient answers/review/expanded results/method, targets and reflow.`);
    }
    const context = await browser.newContext({javaScriptEnabled: false});
    const page = await context.newPage(); await page.goto(`${base}/cuestionario/`);
    assert.match(await page.locator('noscript').innerText(), /JavaScript/);
    await page.locator('#quiz-method summary').click();
    assert.match(await page.locator('#quiz-method').innerText(), /16 preguntas|8 respuestas/);
    await context.close();
    console.log('PASS no-script method and source coverage fallback. Manual accessibility/editorial reviews remain open.');
    const invalidContext = await browser.newContext({viewport: {width: 320, height: 844}});
    const invalidPage = await invalidContext.newPage();
    const invalidErrors = [];
    invalidPage.on('pageerror', error => invalidErrors.push(String(error)));
    await invalidPage.route('**/quiz-data.*.js', async route => {
      const response = await route.fetch();
      const original = await response.text();
      const corrupted = original.replace('"schema_version":"1.0.0"', '"schema_version":"invalid-test-version"');
      assert.notEqual(corrupted, original, 'Corrupt-bundle fixture must change the data');
      await route.fulfill({response, body: corrupted});
    });
    await invalidPage.goto(`${base}/cuestionario/`, {waitUntil: 'networkidle'});
    assert.match(await invalidPage.locator('#quiz-app').innerText(), /No se puede abrir este cuestionario/);
    assert.equal(await invalidPage.locator('#quiz-app input, .quiz-score').count(), 0);
    await invalidPage.locator('#quiz-method summary').click();
    assert.match(await invalidPage.locator('#quiz-method').innerText(), /No es una medida de confianza estadística/);
    await checkLayout(invalidPage, 'invalid bundle fallback', 320);
    assert.deepEqual(invalidErrors, []);
    await invalidContext.close();
    console.log('PASS corrupt bundle: no answers or partial score, readable error and method at 320px.');
    if (process.env.QUIZ_UNAVAILABLE_URL) {
      const unavailableContext = await browser.newContext({viewport: {width: 320, height: 844}});
      const unavailablePage = await unavailableContext.newPage();
      const unavailableRequests = [];
      unavailablePage.on('request', request => unavailableRequests.push(request.url()));
      await unavailablePage.goto(process.env.QUIZ_UNAVAILABLE_URL, {waitUntil: 'networkidle'});
      assert.match(await unavailablePage.locator('.quiz-shell').innerText(), /aún no está disponible/);
      assert.equal(await unavailablePage.locator('.quiz-shell input, .quiz-shell button, .quiz-score').count(), 0);
      assert.equal(await unavailablePage.getByRole('link', {name: 'Consultar el método editorial', exact: true}).count(), 1);
      assert.equal(await unavailablePage.getByRole('link', {name: 'Consultar las fuentes', exact: true}).count(), 1);
      assert.equal(unavailableRequests.some(url => /quiz-(data|engine|ui)\./.test(url)), false);
      await checkLayout(unavailablePage, 'unavailable set fallback', 320);
      await unavailableContext.close();
      console.log('PASS unavailable set: no scoring bundle or dead answer controls, method and sources reachable at 320px.');
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
