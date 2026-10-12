// Execute the actual generated bundle and application; return only rendered text.
const fs = require('node:fs');
const vm = require('node:vm');
const nodes = {};
for (const id of ['selection-form', 'topic-select', 'party-a-select', 'party-b-select',
  'selection-error', 'measures-container', 'share-button', 'share-feedback', 'share-fallback',
  'share-link', 'copy-link-button', 'label']) {
  nodes[id] = { value: '', innerHTML: '', textContent: '', handlers: {},
    classList: { add() {}, remove() {} }, setAttribute() {}, removeAttribute() {},
    addEventListener(type, handler) { this.handlers[type] = handler; } };
}
nodes['topic-select'].value = 'housing';
nodes['party-a-select'].value = 'partido-ejemplo-a';
nodes['party-b-select'].value = 'partido-ejemplo-b';
const location = { href: 'https://preview.test/?topic=housing&partyA=partido-ejemplo-a&partyB=partido-ejemplo-b' };
const document = { readyState: 'complete', body: { dataset: { election: 'es-gen-2026', comparison: 'validated' } },
  getElementById: id => nodes[id], querySelector: () => nodes.label };
const window = { location, history: { replaceState(_, __, href) { location.href = href; } } };
const context = vm.createContext({ window, document, navigator: {}, URL, URLSearchParams });
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), context);
vm.runInContext(fs.readFileSync('site/sharing.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('site/app.js', 'utf8'), context);
process.stdout.write(JSON.stringify({ html: nodes['measures-container'].innerHTML, election: window.ComparisonData ? window.ComparisonData.electionId : null }));
