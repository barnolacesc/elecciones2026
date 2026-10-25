const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function node(value = '') {
  const attributes = new Map();
  return {
    value, hidden: true, children: [], handlers: {}, attributes,
    replaceChildren(...children) { this.children = children; },
    append(child) { this.children.push(child); },
    addEventListener(type, handler) { this.handlers[type] = handler; },
    setAttribute(name, val) { attributes.set(name, val); },
    removeAttribute(name) { attributes.delete(name); }
  };
}

async function pilot(href, response) {
  const nodes = {
    'pilot-topic': node('housing'), 'pilot-a': node('pp'),
    'pilot-b': node('erc'), 'pilot-comparison': node(), 'pilot-error': node()
  };
  const location = { href, pathname: '/' };
  const history = { replaceState(_state, _title, url) { location.href = String(url); } };
  const data = {
    election_id: 'es-gen-2023', status: 'historical-provisional-private',
    topics: [{ id: 'housing', name: 'Vivienda' }], positions: []
  };
  const summary = node();
  summary.focus = () => { summary.focused = true; };
  const staticList = node();
  staticList.querySelector = () => summary;
  nodes['pilot-comparison'].nextElementSibling = staticList;
  const document = {
    getElementById(id) { return nodes[id] || null; },
    createElement() { return node(); }
  };
  const context = vm.createContext({
    document, location, history, URL, URLSearchParams,
    fetch: async () => response || ({ ok: true, json: async () => data })
  });
  await vm.runInContext(fs.readFileSync('site/pilot-2023.js', 'utf8'), context);
  return { nodes, location, staticList, summary };
}

test('unavailable private data offers the static source list without active selectors', async () => {
  const { nodes, staticList, summary } = await pilot('https://private.test/', { ok: false });
  for (const id of ['pilot-topic', 'pilot-a', 'pilot-b']) assert.equal(nodes[id].disabled, true);
  const [alert, button] = nodes['pilot-comparison'].children;
  assert.equal(alert.attributes.get('role'), 'alert');
  assert.match(alert.textContent, /No se ha podido cargar/);
  assert.equal(button.textContent, 'Ver todas las medidas');
  button.handlers.click();
  assert.equal(staticList.open, true);
  assert.equal(summary.focused, true);
});

test('duplicate pilot parties clear stale comparison URL and describe the error', async () => {
  const { nodes, location } = await pilot(
    'https://private.test/?topic=housing&partyA=pp&partyB=erc#old'
  );
  assert.equal(location.href, 'https://private.test/?topic=housing&partyA=pp&partyB=erc#old');
  assert.equal(nodes['pilot-error'].hidden, true);
  assert.equal(nodes['pilot-comparison'].children.length, 1);

  nodes['pilot-b'].value = 'pp';
  nodes['pilot-b'].handlers.change();
  assert.equal(nodes['pilot-error'].hidden, false);
  assert.equal(nodes['pilot-comparison'].children.length, 0);
  assert.equal(location.href, 'https://private.test/');
  for (const id of ['pilot-a', 'pilot-b']) {
    assert.equal(nodes[id].attributes.get('aria-invalid'), 'true');
    assert.equal(nodes[id].attributes.get('aria-describedby'), 'pilot-error');
  }

  nodes['pilot-b'].value = 'erc';
  nodes['pilot-b'].handlers.change();
  assert.equal(nodes['pilot-error'].hidden, true);
  assert.equal(nodes['pilot-comparison'].children.length, 1);
  assert.equal(location.href, 'https://private.test/?topic=housing&partyA=pp&partyB=erc');
  for (const id of ['pilot-a', 'pilot-b']) {
    assert.equal(nodes[id].attributes.has('aria-invalid'), false);
    assert.equal(nodes[id].attributes.has('aria-describedby'), false);
  }
});
