/* Assigned generic groups only. No official results or personal scenarios. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const engine = require('../site/simulator-engine.js');
const row = (id, seats, label = `Group ${id}`) => ({id, label, seats: String(seats)});
const code = (result, expected) => result.errors.some(error => error.code === expected);

test('zero allocation is incomplete and has no selected coalition', () => {
  const result = engine.calculate([row('a', 0)]);
  assert.equal(result.status, 'incomplete');
  assert.equal(result.assigned, 0);
  assert.equal(result.unassigned, 350);
  assert.equal(result.coalition, null);
});

test('one and thirty groups are supported; invalid group counts fail closed', () => {
  assert.equal(engine.validateScenario([row('a', 350)]).status, 'complete');
  assert.equal(engine.validateScenario(Array.from({length: 30}, (_, i) => row(`g${i}`, 0))).status, 'incomplete');
  for (const input of [null, {}, 'groups', [], Array.from({length: 31}, (_, i) => row(`g${i}`, 0))]) {
    const result = engine.calculate(input);
    assert.equal(result.status, 'invalid');
    assert.ok(code(result, 'group-count'));
    assert.equal(result.coalition, null);
  }
});

test('seat input accepts ASCII digits and outer whitespace without mutating raw text', () => {
  const input = [row('a', ' 00175 '), row('b', '0')];
  const before = structuredClone(input);
  const result = engine.calculate(input, ['a']);
  assert.equal(result.coalition.seats, 175);
  assert.equal(result.groups[0].rawSeats, ' 00175 ');
  assert.deepEqual(input, before);
});

test('blank, signed, decimal, exponent, non-ASCII, and non-string counts are rejected', () => {
  for (const value of ['', ' ', '-1', '+1', '1.5', '1.0', '1e2', '0x10', 'NaN', 'Infinity',
    '１２', '١٢', '1 2', '1\n2', true, false, 1, 0, null, undefined, {}, []]) {
    const result = engine.calculate([{id: 'a', label: 'Group A', seats: value}], ['a']);
    assert.equal(result.status, 'invalid');
    assert.ok(code(result, 'invalid-count'));
    assert.equal(result.assigned, null);
    assert.equal(result.unassigned, null);
    assert.equal(result.coalition, null);
    assert.equal(result.groups[0].rawSeats, value);
  }
});

test('counts above the chamber and unsafe numeric magnitudes are rejected', () => {
  for (const value of ['351', '99999999999999999999999', '9'.repeat(400)]) {
    const result = engine.calculate([row('a', value)], ['a']);
    assert.equal(result.status, 'invalid');
    assert.ok(code(result, 'count-range'));
    assert.equal(result.coalition, null);
  }
});

test('individual upper boundary is allowed but combined excess is invalid', () => {
  assert.equal(engine.calculate([row('a', 350)], ['a']).coalition.seats, 350);
  const result = engine.calculate([row('a', 350), row('b', 1)], ['a']);
  assert.equal(result.status, 'invalid');
  assert.ok(code(result, 'total-exceeds-chamber'));
  assert.equal(result.assigned, null);
  assert.equal(result.coalition, null);
});

test('labels are trimmed and measured as Unicode code points', () => {
  assert.equal(engine.validateScenario([row('a', 0, '  Group A  ')]).groups[0].label, 'Group A');
  assert.equal(engine.validateScenario([row('a', 0, '😀'.repeat(60))]).status, 'incomplete');
  for (const label of ['', ' \n ', '😀'.repeat(61), 'a'.repeat(61), null, 1]) {
    const result = engine.calculate([row('a', 1, label)], ['a']);
    assert.equal(result.status, 'invalid');
    assert.ok(code(result, 'invalid-label'));
    assert.equal(result.coalition, null);
  }
});

test('duplicate labels use NFC normalization and case-insensitive comparison', () => {
  const result = engine.calculate([row('a', 10, ' ÉQUIPO '), row('b', 20, 'e\u0301quipo')], ['a']);
  assert.equal(result.status, 'invalid');
  assert.deepEqual(result.errors.filter(e => e.code === 'duplicate-label').map(e => e.index), [0, 1]);
  assert.equal(result.coalition, null);
});

test('hostile and prototype-like labels remain plain strings with no special identity', () => {
  const label = '<img src=x onerror=alert(1)>';
  const input = [row('__proto__', 176, label), row('constructor', 0, '__proto__')];
  const result = engine.calculate(input, ['__proto__']);
  assert.equal(result.groups[0].label, label);
  assert.equal(result.coalition.seats, 176);
  assert.equal(engine.calculate([row('a', 1, 'constructor'), row('b', 1, 'CONSTRUCTOR')]).status, 'invalid');
});

test('malformed groups and missing or duplicate identities fail closed', () => {
  for (const input of [[null], [[]], ['row'], [{label: 'A', seats: '1'}],
    [{id: ' ', label: 'A', seats: '1'}], [row('a', 1), row('a', 1, 'B')]]) {
    const result = engine.calculate(input);
    assert.equal(result.status, 'invalid');
    assert.equal(result.coalition, null);
  }
});

test('175, 176, and 177 seats yield exact deficit and surplus boundaries', () => {
  for (const [seats, deficit, surplus, reachesThreshold] of [
    [175, 1, 0, false], [176, 0, 0, true], [177, 0, 1, true]]) {
    const result = engine.calculate([row('a', seats), row('b', 350 - seats)], ['a']);
    assert.equal(result.status, 'complete');
    assert.deepEqual(result.coalition, {seats, threshold: 176, deficit, surplus, reachesThreshold});
  }
});

test('incomplete distribution retains unassigned seats and an inspectable selected sum', () => {
  const result = engine.calculate([row('a', 120), row('b', 80)], ['a', 'b']);
  assert.equal(result.status, 'incomplete');
  assert.equal(result.assigned, 200);
  assert.equal(result.unassigned, 150);
  assert.equal(result.coalition.seats, 200);
  assert.equal(result.coalition.surplus, 24);
});

test('no selection differs from selecting a group with zero seats', () => {
  assert.equal(engine.calculate([row('a', 0)]).coalition, null);
  assert.deepEqual(engine.calculate([row('a', 0)], ['a']).coalition,
    {seats: 0, threshold: 176, deficit: 176, surplus: 0, reachesThreshold: false});
});

test('repeated selection counts a group once and unknown selection fails closed', () => {
  assert.equal(engine.calculate([row('a', 100), row('b', 76)], ['a', 'a', 'b']).coalition.seats, 176);
  for (const selected of [['missing'], [1], [null], {}, null, 'a']) {
    const result = engine.calculate([row('a', 176)], selected);
    assert.equal(result.status, 'invalid');
    assert.equal(result.coalition, null);
  }
});

test('edits, removal, and reselection replace the previous sum without retaining state', () => {
  const groups = [row('a', 100), row('b', 76), row('c', 174)];
  const original = engine.calculate(groups, ['a', 'b']);
  const edited = groups.map(g => g.id === 'b' ? {...g, seats: '75'} : g);
  assert.equal(engine.calculate(edited, ['a', 'b']).coalition.deficit, 1);
  const removed = groups.filter(g => g.id !== 'b');
  assert.equal(engine.calculate(removed, ['a']).coalition.seats, 100);
  assert.equal(engine.calculate(removed, ['a', 'c']).coalition.seats, 274);
  assert.equal(engine.calculate(removed, ['a', 'b']).coalition, null);
  assert.equal(engine.calculate([row('a', 0)]).coalition, null);
  assert.equal(original.coalition.seats, 176);
  assert.deepEqual(groups, [row('a', 100), row('b', 76), row('c', 174)]);
});

test('a later invalid edit cannot carry a prior valid sum', () => {
  const groups = [row('a', 176), row('b', 174)];
  assert.equal(engine.calculate(groups, ['a']).coalition.reachesThreshold, true);
  for (const seats of ['', '175.5', '177']) {
    const result = engine.calculate([{...groups[0], seats}, groups[1]], ['a']);
    assert.equal(result.status, 'invalid');
    assert.equal(result.coalition, null);
  }
});

test('every row permutation and selection order preserves arithmetic', () => {
  const rows = [row('a', 100), row('b', 76), row('c', 174)];
  const expected = engine.calculate(rows, ['a', 'b']);
  for (const indices of [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]]) {
    const result = engine.calculate(indices.map(i => rows[i]), ['b', 'a']);
    assert.equal(result.assigned, expected.assigned);
    assert.equal(result.unassigned, expected.unassigned);
    assert.deepEqual(result.coalition, expected.coalition);
  }
});

test('exhaustive two-group splits preserve chamber and coalition totals', () => {
  for (let seats = 0; seats <= 350; seats++) {
    const groups = [row('a', seats), row('b', 350 - seats)];
    const one = engine.calculate(groups, ['a']);
    const both = engine.calculate(groups, ['b', 'a']);
    assert.equal(one.assigned, 350);
    assert.equal(one.unassigned, 0);
    assert.equal(one.coalition.seats, seats);
    assert.equal(one.coalition.reachesThreshold, seats >= 176);
    assert.equal(one.coalition.deficit, Math.max(0, 176 - seats));
    assert.equal(one.coalition.surplus, Math.max(0, seats - 176));
    assert.equal(both.coalition.seats, 350);
  }
});

test('browser export works without DOM, storage, network, or telemetry APIs', () => {
  const context = vm.createContext({});
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../site/simulator-engine.js'), 'utf8'), context);
  assert.equal(context.SimulatorEngine.calculate([row('a', 176)], ['a']).coalition.seats, 176);
  assert.equal(Object.isFrozen(context.SimulatorEngine), true);
  assert.equal(Object.isFrozen(context.SimulatorEngine.limits), true);
});
