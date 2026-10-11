/* Synthetic accessibility regression evidence, not a conformance audit. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.QUIZ_TEST_URL || 'http://127.0.0.1:48775';
assert.ok(['localhost', '127.0.0.1', '[::1]'].includes(new URL(base).hostname));

async function tabTo(page, role, name) {
  const control = page.getByRole(role, {name, exact: true});
  assert.equal(await control.count(), 1, `Unique ${name} control`);
  for (let i = 0; i < 160; i++) {
    if (await control.evaluate(el => el === document.activeElement)) return control;
    await page.keyboard.press('Tab');
  }
  assert.fail(`Keyboard cannot reach ${name}`);
}

// Compute opaque text/background contrast, leaving native controls and complex
// backgrounds for manual review. Never interpret an unmeasured pair as passing.
function textContrast() {
  const rgb = value => {
    const numbers = value.match(/[\d.]+/g)?.map(Number);
    return numbers?.length >= 3 ? [...numbers.slice(0, 3), numbers[3] ?? 1] : null;
  };
  const luminance = color => color.slice(0, 3).map(x => {
    x /= 255; return x <= .04045 ? x / 12.92 : ((x + .055) / 1.055) ** 2.4;
  }).reduce((sum, x, i) => sum + x * [.2126, .7152, .0722][i], 0);
  const measured = [], unmeasured = [];
  for (const el of document.querySelectorAll('body *')) {
    const rect = el.getBoundingClientRect();
    const css = getComputedStyle(el);
    if (!rect.width || !rect.height || css.visibility !== 'visible'
      || el.classList.contains('sr-only') || el.closest('.sr-only')
      || rect.right < 0 || rect.bottom < 0
      || ![...el.childNodes].some(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim())) continue;
    let background = null, complex = false;
    for (let parent = el; parent; parent = parent.parentElement) {
      const style = getComputedStyle(parent);
      if (Number(style.opacity) !== 1 || style.backgroundImage !== 'none') complex = true;
      if (!background) {
        const candidate = rgb(style.backgroundColor);
        if (candidate?.[3] === 1) background = candidate;
        else if (candidate?.[3] > 0) complex = true;
      }
    }
    const foreground = rgb(css.color);
    const target = `${el.tagName.toLowerCase()}.${el.className}`;
    if (!background || foreground?.[3] !== 1 || complex) { unmeasured.push(target); continue; }
    const l = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
    const large = parseFloat(css.fontSize) >= 24
      || (parseFloat(css.fontSize) >= 18.6667 && Number(css.fontWeight) >= 700);
    measured.push({target, ratio: (l[0] + .05) / (l[1] + .05), required: large ? 3 : 4.5});
  }
  return {measured, unmeasured};
}

(async () => {
  const browser = await chromium.launch({headless: true,
    ...(process.env.QUIZ_CHROMIUM ? {executablePath: process.env.QUIZ_CHROMIUM} : {})});
  const evidence = {package: 'E4.3', mode: 'mock', checks: [], states: [],
    conformance: 'pending manual full-process review',
    limits: ['Chromium keyboard and opaque rendered text pairs only.',
      'No VoiceOver/Safari, NVDA/Firefox, native browser zoom, or real-source review.',
      'Native control contrast, outlines, forced colors, and all WCAG criteria require manual review.']};
  const check = (name, condition) => { assert.ok(condition, name); evidence.checks.push(name); };
  try {
    const page = await browser.newPage({viewport: {width: 390, height: 844}, reducedMotion: 'reduce'});
    async function inspect(state) {
      const observed = await page.evaluate(textContrast);
      const failures = observed.measured.filter(pair => pair.ratio < pair.required);
      if (failures.length) console.error(`${state}: contrast failures`, failures);
      check(`${state}: rendered opaque text contrast`, observed.measured.length > 0
        && observed.measured.every(pair => pair.ratio >= pair.required));
      const headings = await page.locator('#quiz-app h1').count();
      check(`${state}: one main quiz heading`, headings === 1);
      evidence.states.push({state, text_pairs: observed.measured.length,
        minimum_contrast: Math.min(...observed.measured.map(p => p.ratio)),
        unmeasured: observed.unmeasured});
    }
    await page.goto(`${base}/cuestionario/`);
    check('Spanish page language', (await page.locator('html').getAttribute('lang')).startsWith('es'));
    check('Fictional fixture only', await page.evaluate(() => window.QuizBundle.mode === 'mock'));
    await inspect('introduction');
    await page.keyboard.press('Tab');
    check('Skip link first in keyboard order', await page.locator('.skip-link').evaluate(el => el === document.activeElement));
    await page.keyboard.press('Enter');
    check('Skip link reaches main', new URL(page.url()).hash === '#contenido');
    await tabTo(page, 'button', 'Consultar método y cobertura');
    await page.keyboard.press('Enter');
    check('Method receives focus and opens', await page.locator('#quiz-method').evaluate(el =>
      el.open && el.querySelector('summary') === document.activeElement));
    await page.keyboard.press('Enter');
    await tabTo(page, 'button', 'Empezar');
    await page.keyboard.press('Enter');
    check('Question heading receives focus', await page.locator('#quiz-app h1').evaluate(el => el === document.activeElement));
    const group = page.getByRole('group', {name: 'Elige una respuesta', exact: true});
    check('Named answer group', await group.count() === 1);
    check('No answer is selected initially', await page.locator('input[type=radio]:checked').count() === 0);
    await inspect('question');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Space');
    check('Space selects first labelled answer', await page.getByRole('radio', {name: 'Totalmente en desacuerdo', exact: true}).isChecked());
    await page.keyboard.press('ArrowDown');
    check('Arrow key selects second answer without advancing', await page.getByRole('radio', {name: 'Más bien en desacuerdo', exact: true}).isChecked()
      && await page.getByRole('progressbar', {name: 'Pregunta 1 de 16', exact: true}).count() === 1);
    await page.keyboard.press('Tab');
    check('Question source disclosure receives keyboard focus', await page.locator('#quiz-app details summary').evaluate(el => el === document.activeElement));
    await page.keyboard.press('Enter');
    check('Source disclosure opens by keyboard', await page.locator('#quiz-app details').evaluate(el => el.open));
    check('Question source headings follow the main heading', await page.locator('#quiz-app details h2').count() === 3);
    await inspect('question sources');
    await page.keyboard.press('Enter');
    await tabTo(page, 'button', 'Ver resultado');
    await page.keyboard.press('Enter');
    await inspect('insufficient answers');
    check('Insufficient answers explained', (await page.locator('#quiz-app').innerText()).includes('Responde al menos 8 preguntas de 4 temas'));
    await tabTo(page, 'button', 'Cambiar respuestas');
    await page.keyboard.press('Enter');
    await inspect('optional review');
    await tabTo(page, 'button', 'Cambiar pregunta 1');
    await page.keyboard.press('Enter');
    for (let i = 0; i < 8; i++) {
      await page.keyboard.press('Tab');
      await page.keyboard.press('Space');
      await tabTo(page, 'button', 'Siguiente');
      await page.keyboard.press('Enter');
    }
    await tabTo(page, 'button', 'Ver resultado');
    await page.keyboard.press('Enter');
    await inspect('results');
    check('Results remain text, not a chart', await page.locator('.quiz-score').count() === 2);
    await tabTo(page, 'button', 'Borrar respuestas');
    // Traverse back to the disclosure through native Tab order, without pointer use.
    for (let i = 0; i < 160; i++) {
      if (await page.locator('#quiz-app details').first().locator('summary').evaluate(el => el === document.activeElement)) break;
      await page.keyboard.press('Tab');
    }
    check('Weights disclosure reachable', await page.locator('#quiz-app details').first().locator('summary').evaluate(el => el === document.activeElement));
    await page.keyboard.press('Enter');
    await page.keyboard.press('Tab');
    check('First topic has a named select', await page.getByRole('combobox', {name: 'Vivienda', exact: true}).evaluate(el => el === document.activeElement));
    // Native select type-ahead works without opening an OS-owned popup in headless runs.
    await page.keyboard.press('d');
    await page.waitForFunction(() => document.querySelector('#weight-housing').value === '2');
    check('Weight changes preserve focus and selection', await page.locator('#weight-housing').evaluate(el =>
      el === document.activeElement && el.value === '2'));
    check('Weight update exposes a polite status', await page.locator('#quiz-status').evaluate(el =>
      el.getAttribute('role') === 'status' && el.textContent.includes('actualizados')));
    await inspect('changed weights');
    await tabTo(page, 'button', 'Restablecer pesos');
    await page.keyboard.press('Enter');
    await tabTo(page, 'button', 'Borrar respuestas');
    await page.keyboard.press('Enter');
    check('Reset returns to introduction', await page.getByRole('button', {name: 'Empezar', exact: true}).count() === 1);
    check('Reset status accessible', (await page.locator('#quiz-status').innerText()) === 'Respuestas borradas.');
    const output = process.env.QUIZ_ACCESSIBILITY_EVIDENCE || 'build/quiz-accessibility.json';
    fs.mkdirSync(path.dirname(output), {recursive: true});
    fs.writeFileSync(output, `${JSON.stringify(evidence, null, 2)}\n`);
    console.log(`PASS ${evidence.checks.length} keyboard/semantic/contrast checks. Manual audit remains open.`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
