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
const [topic = 'housing', partyA = 'partido-ejemplo-a', partyB = 'partido-ejemplo-b'] = process.argv.slice(3);
nodes['topic-select'].value = topic;
nodes['party-a-select'].value = partyA;
nodes['party-b-select'].value = partyB;
const location = { href: 'https://preview.test/?' + new URLSearchParams({ topic, partyA, partyB }) };
const document = { readyState: 'complete', body: { dataset: { election: 'es-gen-2026', comparison: 'validated' } },
  getElementById: id => nodes[id], querySelector: () => nodes.label };
const paginatedLists = [];
nodes['measures-container'].querySelectorAll = (selector) => {
  if (selector !== '.proposal-list-cards') return [];
  return Array.from(nodes['measures-container'].innerHTML.matchAll(
    /class="proposal-list-cards"[^>]*data-paginate-label="([^"]+)"/g), match => match[1]);
};
const window = { location, history: { replaceState(_, __, href) { location.href = href; } },
  EleccionesPagination: { paginate: label => paginatedLists.push(label) } };
const context = vm.createContext({ window, document, navigator: {}, URL, URLSearchParams });
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), context);
vm.runInContext(fs.readFileSync('site/sharing.js', 'utf8'), context);
vm.runInContext(fs.readFileSync('site/app.js', 'utf8'), context);
process.stdout.write(JSON.stringify({ html: nodes['measures-container'].innerHTML, paginatedLists, election: window.ComparisonData ? window.ComparisonData.electionId : null }));
