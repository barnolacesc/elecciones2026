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

test('provisional quiz discards answers and results on exit and cache restoration', async () => {
  const listeners = {};
  const nodes = Object.fromEntries([
    'pilot-quiz', 'pilot-progress', 'pilot-question', 'pilot-statement',
    'pilot-next', 'pilot-answer-error', 'pilot-results'
  ].map(id => [id, node()]));
  const quiz = nodes['pilot-quiz'];
  quiz.hidden = false;
  nodes['pilot-results'].focus = () => {};
  quiz.selected = null;
  quiz.reset = () => { quiz.selected = null; };
  quiz.querySelector = () => quiz.selected && {value: quiz.selected};
  const document = {
    getElementById(id) { return nodes[id] || null; },
    createElement() { return {...node(), style: {}, focus() {}}; },
    createTextNode(text) { return node(text); }
  };
  const data = {
    election_id: 'es-gen-2023', status: 'historical-provisional-private',
    topics: [{id: 'housing', name: 'Vivienda'}],
    positions: [{party: 'pp', topic: 'housing', summary: 'Fictional test item',
      title: 'Test item', qualification: 'Test only', page: 1,
      locator: 'Test locator', url: 'https://source.invalid/#page=1'}]
  };
  const context = vm.createContext({document, URL, URLSearchParams,
    location: {pathname: '/cuestionario/', href: 'https://private.test/cuestionario/'},
    window: {location: {reload() {}}, addEventListener(type, handler) { listeners[type] = handler; }},
    navigator: {},
    fetch: async () => ({ok: true, json: async () => data})});
  await vm.runInContext(fs.readFileSync('site/pilot-2023.js', 'utf8'), context);

  function complete() {
    quiz.selected = 'agree';
    quiz.handlers.submit({preventDefault() {}});
    assert.equal(quiz.hidden, true);
    assert.ok(nodes['pilot-results'].children.length > 0);
  }
  function expectCleared() {
    assert.equal(quiz.hidden, false);
    assert.equal(quiz.selected, null);
    assert.equal(nodes['pilot-results'].children.length, 0);
    assert.equal(nodes['pilot-progress'].textContent, 'Propuesta 1 de 1');
    quiz.handlers.submit({preventDefault() {}});
    assert.equal(nodes['pilot-answer-error'].hidden, false);
  }

  complete();
  listeners.pagehide();
  expectCleared();
  complete();
  listeners.pageshow({persisted: true});
  expectCleared();
});
