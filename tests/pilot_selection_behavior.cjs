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

async function pilot(href, dataAvailable = true) {
  const nodes = {
    'pilot-topic': node('housing'), 'pilot-a': node('pp'),
    'pilot-b': node('erc'), 'pilot-comparison': node(), 'pilot-error': node()
  };
  const summary = node();
  summary.focus = () => { summary.focused = true; };
  const mobileNav = node();
  mobileNav.open = false;
  mobileNav.querySelector = selector => selector === 'summary' ? summary : null;
  const location = { href, pathname: '/' };
  const history = { replaceState(_state, _title, url) { location.href = String(url); } };
  const data = {
    election_id: 'es-gen-2023', status: 'historical-provisional-private',
    topics: [{ id: 'housing', name: 'Vivienda' }], positions: []
  };
  const document = {
    getElementById(id) { return nodes[id] || null; },
    querySelector(selector) { return selector === '.mobile-nav' ? mobileNav : null; },
    createElement() { return node(); }
  };
  const context = vm.createContext({
    document, location, history, URL, URLSearchParams,
    fetch: async () => ({ ok: dataAvailable, json: async () => data })
  });
  await vm.runInContext(fs.readFileSync('site/pilot-2023.js', 'utf8'), context);
  return { nodes, location, mobileNav, summary };
}

test('Escape closes the open mobile menu and returns focus even without pilot data', async () => {
  const { mobileNav, summary } = await pilot('https://private.test/', false);
  assert.equal(typeof mobileNav.handlers.keydown, 'function');
  mobileNav.open = true;
  let prevented = false;
  mobileNav.handlers.keydown({ key: 'Enter', preventDefault() { prevented = true; } });
  assert.equal(mobileNav.open, true);
  assert.equal(prevented, false);
  mobileNav.handlers.keydown({ key: 'Escape', preventDefault() { prevented = true; } });
  assert.equal(mobileNav.open, false);
  assert.equal(summary.focused, true);
  assert.equal(prevented, true);
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
