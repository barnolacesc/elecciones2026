/* Unit and behavior tests for Simulator UI (E5.3). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const engineCode = fs.readFileSync(path.join(__dirname, '../site/simulator-engine.js'), 'utf8');
const uiCode = fs.readFileSync(path.join(__dirname, '../site/simulator-ui.js'), 'utf8');

function createMockElement(id = '', tag = 'div') {
  return {
    id,
    tagName: tag.toUpperCase(),
    value: '',
    textContent: '',
    innerHTML: '',
    className: '',
    hidden: false,
    disabled: false,
    dataset: {},
    handlers: {},
    attributes: {},
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return this.attributes[k] || null; },
    removeAttribute(k) { delete this.attributes[k]; },
    classList: {
      _classes: new Set(),
      add(c) { this._classes.add(c); },
      remove(c) { this._classes.delete(c); },
      contains(c) { return this._classes.has(c); }
    },
    addEventListener(event, handler) {
      if (!this.handlers[event]) this.handlers[event] = [];
      this.handlers[event].push(handler);
    },
    dispatchEvent(event) {
      const list = this.handlers[event.type] || [];
      for (const h of list) h(event);
    },
    querySelector(selector) { return null; },
    querySelectorAll(selector) { return []; },
    closest(selector) {
      if (selector === 'button' && this.tagName === 'BUTTON') return this;
      return null;
    },
    focus() { this.focused = true; },
    select() { this.selected = true; }
  };
}

function createSimulatorEnv(href = 'https://preview.test/simulador/') {
  const elements = {};
  const elementIds = [
    'simulator-app',
    'simulator-status',
    'simulator-hemicycle-chart',
    'simulator-hemicycle-legend',
    'stat-assigned',
    'stat-unassigned',
    'stat-coalition',
    'stat-threshold',
    'simulator-threshold-banner',
    'simulator-errors-container',
    'simulator-groups-tbody',
    'simulator-add-group',
    'simulator-sample',
    'simulator-reset',
    'simulator-share-btn',
    'simulator-copy-btn',
    'simulator-share-input',
    'simulator-share-feedback'
  ];

  for (const id of elementIds) {
    elements[id] = createMockElement(id);
  }

  const document = {
    readyState: 'complete',
    getElementById(id) {
      return elements[id] || null;
    },
    querySelector(sel) {
      return null;
    },
    querySelectorAll(sel) {
      return [];
    },
    addEventListener(evt, h) {}
  };

  const location = new URL(href);
  const window = {
    location,
    document,
    isSecureContext: true,
    navigator: {
      clipboard: {
        async writeText(txt) { window._copied = txt; }
      }
    },
    console
  };

  const context = vm.createContext({
    window,
    document,
    location,
    navigator: window.navigator,
    console,
    URL,
    URLSearchParams,
    Set,
    Map,
    Math,
    Number,
    String,
    Array,
    Object,
    JSON,
    Buffer,
    atob,
    btoa,
    setTimeout(fn) { fn(); }
  });

  vm.runInContext(engineCode, context);
  vm.runInContext(uiCode, context);

  return { context, window, elements };
}

test('UI initializes with starter groups and renders hemicycle with 350 seats', () => {
  const { elements, context } = createSimulatorEnv();
  const hemicycleHtml = elements['simulator-hemicycle-chart'].innerHTML;

  assert.ok(hemicycleHtml.includes('<svg'), 'Hemicycle SVG was generated');
  const dotMatches = hemicycleHtml.match(/<circle /g);
  assert.equal(dotMatches ? dotMatches.length : 0, 350, 'Hemicycle contains exactly 350 seat circles');

  const assigned = elements['stat-assigned'].textContent;
  const unassigned = elements['stat-unassigned'].textContent;
  assert.equal(Number(assigned) + Number(unassigned), 350, 'Assigned + unassigned equals 350');
});

test('UI updates coalition stats when groups are selected', () => {
  const { elements, context } = createSimulatorEnv();
  const ui = context.SimulatorUI;

  // Set scenario with 2 groups: 175 and 175
  ui.setState({
    groups: [
      { id: 'g-1', label: 'Grupo 1', seats: '175' },
      { id: 'g-2', label: 'Grupo 2', seats: '175' }
    ],
    selectedIds: ['g-1'],
    idCounter: 2
  });

  // Check stat values: coalition should have 175 seats, deficit 1 (-1)
  assert.equal(elements['stat-coalition'].textContent, '175');
  assert.equal(elements['stat-threshold'].textContent, '-1');
  assert.ok(elements['simulator-threshold-banner'].className.includes('majority-short'));

  // Now change to 176
  ui.setState({
    groups: [
      { id: 'g-1', label: 'Grupo 1', seats: '176' },
      { id: 'g-2', label: 'Grupo 2', seats: '174' }
    ],
    selectedIds: ['g-1'],
    idCounter: 2
  });

  assert.equal(elements['stat-coalition'].textContent, '176');
  assert.equal(elements['stat-threshold'].textContent, '+0');
  assert.ok(elements['simulator-threshold-banner'].className.includes('majority-reached'));

  // Now change to 177
  ui.setState({
    groups: [
      { id: 'g-1', label: 'Grupo 1', seats: '177' },
      { id: 'g-2', label: 'Grupo 2', seats: '173' }
    ],
    selectedIds: ['g-1'],
    idCounter: 2
  });

  assert.equal(elements['stat-coalition'].textContent, '177');
  assert.equal(elements['stat-threshold'].textContent, '+1');
  assert.ok(elements['simulator-threshold-banner'].className.includes('majority-reached'));
});

test('UI displays error when seat count exceeds 350 chamber limit', () => {
  const { elements, context } = createSimulatorEnv();
  const ui = context.SimulatorUI;

  ui.setState({
    groups: [
      { id: 'g-1', label: 'Grupo 1', seats: '200' },
      { id: 'g-2', label: 'Grupo 2', seats: '200' }
    ],
    selectedIds: [],
    idCounter: 2
  });

  assert.ok(elements['simulator-threshold-banner'].className.includes('chamber-overflow'));
  assert.equal(elements['simulator-errors-container'].hidden, false);
  assert.ok(elements['simulator-errors-container'].innerHTML.includes('350 escaños'));
  assert.equal(elements['stat-assigned'].textContent, '—');
});

test('UI restores scenario directly from URL query param on initialization', () => {
  // Serialize a specific scenario
  const engine = vm.runInContext('SimulatorEngine', createSimulatorEnv().context);
  const sample = [
    { id: 'url-1', label: 'Partido Alfa', seats: '150' },
    { id: 'url-2', label: 'Partido Beta', seats: '100' }
  ];
  const token = engine.serializeScenario(sample, ['url-1']);
  const shareUrl = `https://preview.test/simulador/?s=${token}`;

  const env = createSimulatorEnv(shareUrl);
  const state = env.context.SimulatorUI.getState();

  assert.equal(state.groups.length, 2);
  assert.equal(state.groups[0].label, 'Partido Alfa');
  assert.equal(state.groups[0].seats, '150');
  assert.deepEqual(state.selectedIds, ['url-1']);
});

test('Copy and share buttons generate clean URLs without tracking', async () => {
  const { elements, context, window } = createSimulatorEnv('https://preview.test/simulador/?tracker=bad#frag');
  const copyBtn = elements['simulator-copy-btn'];

  // Dispatch click
  copyBtn.dispatchEvent({ type: 'click', target: copyBtn });
  await new Promise(resolve => setTimeout(resolve, 10));

  assert.ok(window._copied, 'URL was copied to clipboard');
  assert.ok(window._copied.startsWith('https://preview.test/simulador/?s='));
  assert.ok(!window._copied.includes('tracker=bad'));
  assert.ok(!window._copied.includes('#frag'));
  assert.equal(elements['simulator-share-feedback'].textContent, 'Enlace copiado al portapapeles.');
});
