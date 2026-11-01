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

async function pilot(href, positions = []) {
  const nodes = {
    'pilot-topic': node('housing'), 'pilot-a': node('pp'),
    'pilot-b': node('erc'), 'pilot-comparison': node(), 'pilot-error': node()
  };
  const location = { href, pathname: '/' };
  const history = { replaceState(_state, _title, url) { location.href = String(url); } };
  const data = {
    election_id: 'es-gen-2023', status: 'historical-provisional-private',
    topics: [{ id: 'housing', name: 'Vivienda' }], positions
  };
  const document = {
    getElementById(id) { return nodes[id] || null; },
    createElement(tag) { return Object.assign(node(), { tagName: tag }); }
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
  assert.equal(nodes['pilot-comparison'].children.length, 2);
  assert.match(nodes['pilot-comparison'].children[0].textContent, /La ausencia no indica apoyo ni oposición/);
  assert.equal(nodes['pilot-comparison'].children[1].href, './fuentes/');
  assert.match(nodes['pilot-comparison'].children[1].textContent, /fuentes y límites/);
  assert.equal(nodes['pilot-comparison'].children[1].className, 'button');

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
  assert.equal(nodes['pilot-comparison'].children.length, 2);
  assert.equal(location.href, 'https://private.test/?topic=housing&partyA=pp&partyB=erc');
  for (const id of ['pilot-a', 'pilot-b']) {
    assert.equal(nodes[id].attributes.has('aria-invalid'), false);
    assert.equal(nodes[id].attributes.has('aria-describedby'), false);
  }
});

test('pilot citation names its new-tab behavior in the rendered comparison', async () => {
  const position = {
    topic: 'housing', party: 'pp', measure_id: 'measure-1', measure_title: 'Medida',
    title: 'Propuesta', summary: 'Texto de prueba', qualification: 'Sin matices',
    page: 3, locator: 'Página 3', url: 'https://example.test/programa.pdf#page=3'
  };
  const { nodes } = await pilot('https://private.test/', [position]);
  function descendants(node) {
    return [node, ...node.children.flatMap(descendants)];
  }
  const links = descendants(nodes['pilot-comparison']).filter(node => node.tagName === 'a');
  assert.equal(links.length, 1);
  assert.match(links[0].textContent, /PDF pág\. 3 \(se abre en otra pestaña\)/);
  assert.equal(links[0].target, '_blank');
  assert.equal(links[0].rel, 'noopener noreferrer');
  assert.equal(links[0].referrerPolicy, 'no-referrer');
});
