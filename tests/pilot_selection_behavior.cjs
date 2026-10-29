const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function node(value = '') {
  const attributes = new Map();
  return {
    value, hidden: true, children: [], handlers: {}, attributes,
    replaceChildren() { this.children = []; },
    append(child) { this.children.push(child); },
    addEventListener(type, handler) { this.handlers[type] = handler; },
    setAttribute(name, val) { attributes.set(name, val); },
    removeAttribute(name) { attributes.delete(name); }
  };
}

async function pilot(href) {
  const nodes = {
    'pilot-topic': node('housing'), 'pilot-a': node('pp'),
    'pilot-b': node('erc'), 'pilot-comparison': node(), 'pilot-error': node(),
    'pilot-link-error': node()
  };
  const location = { href, pathname: '/', search: new URL(href).search };
  const history = { replaceState(_state, _title, url) {
    location.href = String(url);
    location.search = new URL(location.href).search;
  } };
  const data = {
    election_id: 'es-gen-2023', status: 'historical-provisional-private',
    topics: [{ id: 'housing', name: 'Vivienda' }], positions: []
  };
  const document = {
    getElementById(id) { return nodes[id] || null; },
    createElement() { return node(); }
  };
  const context = vm.createContext({
    document, location, history, URL, URLSearchParams,
    fetch: async () => ({ ok: true, json: async () => data })
  });
  await vm.runInContext(fs.readFileSync('site/pilot-2023.js', 'utf8'), context);
  return { nodes, location };
}

test('duplicate pilot parties clear stale comparison URL and describe the error', async () => {
  const { nodes, location } = await pilot(
    'https://private.test/?topic=housing&partyA=pp&partyB=erc#old'
  );
  assert.equal(location.href, 'https://private.test/?topic=housing&partyA=pp&partyB=erc');
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

test('valid pilot deep link restores the exact topic and party pair', async () => {
  const { nodes, location } = await pilot('https://private.test/?topic=housing&partyA=erc&partyB=pp');
  assert.equal(nodes['pilot-a'].value, 'erc');
  assert.equal(nodes['pilot-b'].value, 'pp');
  assert.equal(nodes['pilot-link-error'].hidden, true);
  assert.equal(nodes['pilot-comparison'].children.length, 1);
  assert.equal(location.href, 'https://private.test/?topic=housing&partyA=erc&partyB=pp');
});

test('malformed pilot deep links show no comparison until a new selection', async () => {
  for (const query of [
    'topic=housing&partyA=pp&partyB=pp',
    'topic=housing&partyA=pp&partyA=erc&partyB=erc',
    'topic=housing&partyA=constructor&partyB=erc',
    'topic=housing&partyA=pp',
    'topic=unknown&partyA=pp&partyB=erc'
  ]) {
    const { nodes, location } = await pilot('https://private.test/?' + query);
    assert.equal(nodes['pilot-link-error'].hidden, false, query);
    assert.equal(nodes['pilot-comparison'].children.length, 0, query);
    assert.equal(location.href, 'https://private.test/', query);
    nodes['pilot-b'].handlers.change();
    assert.equal(nodes['pilot-link-error'].hidden, true, query);
    assert.equal(nodes['pilot-comparison'].children.length, 1, query);
  }
});
