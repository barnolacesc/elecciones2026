const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');

function node(value = '') {
  const attributes = new Map();
  return {
    value, hidden: true, children: [], handlers: {}, attributes, style: {},
    replaceChildren(...children) { this.children = children; },
    append(...children) { this.children.push(...children); },
    addEventListener(type, handler) { this.handlers[type] = handler; },
    setAttribute(name, val) { attributes.set(name, val); },
    removeAttribute(name) { attributes.delete(name); },
    focus() {}
  };
}

async function pilot(href) {
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

test('provisional quiz discards answers and results on exit and cached restore', async () => {
  const nodes = Object.fromEntries(['pilot-quiz', 'pilot-results', 'pilot-progress',
    'pilot-question', 'pilot-statement', 'pilot-next', 'pilot-answer-error']
    .map(id => [id, node()]));
  nodes['pilot-quiz'].reset = () => {};
  nodes['pilot-quiz'].querySelector = () => ({ value: 'agree' });
  const listeners = {};
  const data = {
    election_id: 'es-gen-2023', status: 'historical-provisional-private',
    topics: [{ id: 'housing', name: 'Vivienda' }],
    positions: [1, 2].map(id => ({ party: 'pp', topic: 'housing', summary: `Fixture ${id}` }))
  };
  const document = {
    getElementById(id) { return nodes[id] || null; },
    createElement() { return node(); },
    createTextNode(value) { const text = node(); text.textContent = value; return text; }
  };
  const window = { addEventListener(type, listener) { listeners[type] = listener; } };
  const context = vm.createContext({ document, window, navigator: {},
    location: { pathname: '/cuestionario/', href: 'https://private.test/cuestionario/' },
    URL, URLSearchParams, fetch: async () => ({ ok: true, json: async () => data }) });
  await vm.runInContext(fs.readFileSync('site/pilot-2023.js', 'utf8'), context);
  const submit = () => nodes['pilot-quiz'].handlers.submit({ preventDefault() {} });
  assert.equal(nodes['pilot-progress'].textContent, 'Propuesta 1 de 2');
  submit();
  assert.equal(nodes['pilot-progress'].textContent, 'Propuesta 2 de 2');
  listeners.pagehide();
  assert.equal(nodes['pilot-progress'].textContent, 'Propuesta 1 de 2');
  assert.equal(nodes['pilot-results'].children.length, 0);
  assert.equal(nodes['pilot-quiz'].hidden, false);
  submit(); submit();
  assert.equal(nodes['pilot-quiz'].hidden, true);
  const summary = nodes['pilot-results'].children[0].children[1].textContent;
  assert.match(summary, /2 propuestas/);
  listeners.pageshow({ persisted: true });
  assert.equal(nodes['pilot-progress'].textContent, 'Propuesta 1 de 2');
  assert.equal(nodes['pilot-results'].children.length, 0);
  assert.equal(nodes['pilot-quiz'].hidden, false);
});
