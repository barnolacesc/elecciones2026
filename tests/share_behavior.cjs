const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function browser(href = 'https://preview.test/', navigator = {}, secure = true, app = false) {
  const nodes = {};
  for (const id of ['share-button', 'share-feedback', 'share-fallback', 'share-link',
    'copy-link-button', 'selection-form', 'topic-select', 'party-a-select',
    'party-b-select', 'selection-error', 'measures-container', 'manifesto-dialog', 'label', 'banner']) {
    nodes[id] = { value: '', textContent: '', innerHTML: '', hidden: true, handlers: {},
      classList: { add() {}, remove() {} }, setAttribute() {}, removeAttribute() {},
      showModal() { this.opened = true; }, close() { this.opened = false; },
      querySelector() { return null; },
      addEventListener(event, handler) { this.handlers[event] = handler; },
      focus() { this.focused = true; }, select() { this.selected = true; } };
  }
  nodes['topic-select'].value = 'housing';
  nodes['party-a-select'].value = 'party-a';
  nodes['party-b-select'].value = 'party-b';
  const location = { href };
  const document = { readyState: 'complete', body: { dataset: {} },
    getElementById: id => nodes[id],
    querySelector: selector => selector === '.preview-banner' ? nodes.banner : nodes.label };
  const window = { location, isSecureContext: secure,
    history: { replaceState(_, __, value) { location.href = value; } } };
  const context = vm.createContext({ window, document, navigator, URL, URLSearchParams });
  vm.runInContext(fs.readFileSync('site/sharing.js', 'utf8'), context);
  if (app) vm.runInContext(fs.readFileSync('site/app.js', 'utf8'), context);
  return { window, nodes, click: () => nodes['share-button'].handlers.click() };
}

const topics = { housing: {}, education: {} };
const parties = { pp: {}, erc: {}, psoe: {} };

test('allowlisted selection restores; malformed, duplicate and prototype IDs fail closed', () => {
  const { window } = browser();
  const read = query => window.NeutralSharing.readSelection('https://preview.test/?' + query, topics, parties);
  assert.equal(read('topic=housing&partyA=pp&partyB=psoe').partyA, 'pp');
  for (const query of [
    'topic=housing&partyA=pp&partyB=pp',
    'topic=housing&partyA=pp&partyA=erc&partyB=psoe',
    'topic=constructor&partyA=pp&partyB=psoe',
    'topic=housing&partyA=__proto__&partyB=psoe',
    'topic=housing&partyA=%3Cscript%3E&partyB=psoe',
    'topic=housing&partyA=pp',
    'topic=housing&partyA=pp&partyB=erc&election=unknown',
    'topic=housing&partyA=pp&partyB=psoe&election=es-gen-2023',
    'topic=housing&partyA=pp&partyB=erc&election=2023&election=2026'
  ]) assert.equal(read(query).partyA, null, query);
  assert.equal(read('topic=housing&partyA=pp&partyB=erc&election=2023').pilot, true);
});

test('URLs discard arbitrary query state and fragments and preserve preview origin', () => {
  const { window } = browser();
  const href = 'http://localhost:44545/index.html?visitor=secret&answer=yes&utm_source=x#private';
  assert.equal(window.NeutralSharing.stableUrl(href), 'http://localhost:44545/');
  const url = window.NeutralSharing.stableUrl(href, { topic: 'housing', partyA: 'pp', partyB: 'erc', pilot: true });
  assert.equal(url, 'http://localhost:44545/?topic=housing&partyA=pp&partyB=erc&election=es-gen-2023');
  assert.equal(window.NeutralSharing.stableUrl('https://preview.test/temas/housing/?answer=yes#x'),
    'https://preview.test/temas/housing/');
});

test('home stays home; selecting a comparison round-trips through the real app', async () => {
  let shared;
  const b = browser('https://preview.test/?answer=private#x', { share: async data => { shared = data; } }, true, true);
  assert.equal(b.window.location.href, 'https://preview.test/');
  await b.click();
  assert.equal(shared.url, 'https://preview.test/');
  b.nodes['topic-select'].value = 'education';
  b.nodes['party-a-select'].value = 'pp';
  b.nodes['party-b-select'].value = 'psoe';
  b.nodes['selection-form'].handlers.submit({ preventDefault() {} });
  await b.click();
  assert.equal(shared.url, 'https://preview.test/?topic=education&partyA=pp&partyB=psoe');
  const restored = browser(shared.url, {}, true, true);
  assert.equal(restored.nodes['topic-select'].value, 'education');
  assert.equal(restored.nodes['party-a-select'].value, 'pp');
  assert.equal(restored.nodes['party-b-select'].value, 'psoe');
  assert.ok(restored.nodes['measures-container'].innerHTML.length > 0);
  restored.nodes['party-b-select'].value = 'pp';
  restored.nodes['party-b-select'].handlers.change();
  assert.equal(restored.window.location.href, 'https://preview.test/');
});

test('private pilot keeps election context and never falls back to 2026 measures', async () => {
  let shared;
  const b = browser('https://preview.test/?topic=housing&partyA=pp&partyB=erc&election=2023',
    { share: async data => { shared = data; } }, true, true);
  assert.match(b.nodes['measures-container'].innerHTML, /Contenido pendiente de publicación/);
  assert.doesNotMatch(b.nodes['measures-container'].innerHTML, /15%|Garantir el dret/);
  await b.click();
  assert.match(shared.title, /2023/);
  assert.match(shared.url, /election=es-gen-2023/);

  for (const topic of ['housing', 'economy-work-tax', 'education', 'health-social-services',
    'climate-energy', 'institutions-rights', 'immigration', 'foreign-policy-eu']) {
    b.nodes['topic-select'].value = topic;
    b.nodes['topic-select'].handlers.change();
    const html = b.nodes['measures-container'].innerHTML;
    assert.match(html, /Contenido pendiente de publicación/);
    assert.match(html, /La falta de contenido aprobado no indica/);
    assert.doesNotMatch(html, /btn-open-manifesto|party-statement|15%|Garantir el dret/);
  }
});

test('empty-measures fallback is rendered when a topic has no registered measures', () => {
  const code = fs.readFileSync('site/app.js', 'utf8').replace("'immigration': [", "'immigration': [], '_old_immigration': [");
  const nodes = {};
  for (const id of ['share-button', 'share-feedback', 'share-fallback', 'share-link',
    'copy-link-button', 'selection-form', 'topic-select', 'party-a-select',
    'party-b-select', 'selection-error', 'measures-container', 'manifesto-dialog', 'label', 'banner']) {
    nodes[id] = { value: '', textContent: '', innerHTML: '', hidden: true, handlers: {},
      classList: { add() {}, remove() {} }, setAttribute() {}, removeAttribute() {},
      showModal() { this.opened = true; }, close() { this.opened = false; },
      querySelector() { return null; },
      addEventListener(event, handler) { this.handlers[event] = handler; },
      focus() { this.focused = true; }, select() { this.selected = true; } };
  }
  nodes['topic-select'].value = 'immigration';
  nodes['party-a-select'].value = 'pp';
  nodes['party-b-select'].value = 'erc';
  const location = { href: 'https://preview.test/?topic=immigration&partyA=pp&partyB=erc&election=2023' };
  const document = { readyState: 'complete', body: { dataset: {} },
    getElementById: id => nodes[id],
    querySelector: selector => selector === '.preview-banner' ? nodes.banner : nodes.label };
  const window = { location, isSecureContext: true,
    history: { replaceState(_, __, value) { location.href = value; } } };
  const context = vm.createContext({ window, document, navigator: {}, URL, URLSearchParams });
  vm.runInContext(fs.readFileSync('site/sharing.js', 'utf8'), context);
  vm.runInContext(code, context);
  assert.match(nodes['measures-container'].innerHTML, /Contenido pendiente de publicación/);
});

test('native share success, cancellation and rejection expose honest status and copy fallback', async () => {
  for (const error of [null, { name: 'AbortError' }, { name: 'NotAllowedError' }]) {
    let copied = false;
    const b = browser('https://preview.test/temas/housing/?vote=private', {
      share: async data => { assert.equal(data.url, 'https://preview.test/temas/housing/'); if (error) throw error; },
      clipboard: { writeText: async () => { copied = true; } }
    });
    await b.click();
    assert.equal(copied, false);
    if (error) {
      assert.equal(b.nodes['share-fallback'].hidden, false);
      await b.nodes['copy-link-button'].handlers.click();
      assert.equal(copied, true);
    } else assert.match(b.nodes['share-feedback'].textContent, /compartido/);
  }
});

test('unsupported or insecure native share uses clipboard; denied clipboard selects a manual link', async () => {
  for (const mode of ['no-share', 'insecure', 'canShare-false', 'clipboard-denied', 'no-clipboard']) {
    let copied;
    const navigator = {
      share: async () => { throw new Error('Native share must not run'); },
      canShare: () => false,
      clipboard: { writeText: async url => { if (mode === 'clipboard-denied') throw new Error('denied'); copied = url; } }
    };
    if (mode === 'no-share') delete navigator.share;
    if (mode === 'no-clipboard') delete navigator.clipboard;
    const b = browser('https://preview.test/?answer=yes', navigator, mode !== 'insecure');
    await b.click();
    if (mode === 'clipboard-denied' || mode === 'no-clipboard') {
      assert.equal(b.nodes['share-link'].value, 'https://preview.test/');
      assert.equal(b.nodes['share-link'].selected, true);
      assert.equal(b.nodes['share-link'].focused, true);
      assert.doesNotMatch(b.nodes['share-feedback'].textContent, /copiado/);
    } else assert.equal(copied, 'https://preview.test/');
  }
});

test('pending pilot content exposes no quote viewer or comparative assertion', () => {
  const b = browser('https://preview.test/?topic=housing&partyA=pp&partyB=erc&election=2023', {}, true, true);
  const html = b.nodes['measures-container'].innerHTML;
  assert.match(html, /Contenido pendiente de publicación/);
  assert.doesNotMatch(html, /btn-open-manifesto|Leer extracto|measure-context|measure-axes/);
});
