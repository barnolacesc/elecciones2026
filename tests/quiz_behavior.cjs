/* Numeric fixtures only. No political questions, party identities, or real answers. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const engine = require('../site/quiz-engine.js');
const root = path.join(__dirname, '..');
function fixture() {
  const raw = JSON.parse(fs.readFileSync(path.join(root, 'content/quiz/mock.json'), 'utf8'));
  const taxonomy = JSON.parse(fs.readFileSync(path.join(root, 'content/taxonomy.json'), 'utf8'));
  return {...raw, available: true, topics: taxonomy.topics.map(t => ({id: t.id, name: t.name_es})),
    parties: raw.parties.map(p => ({...p, eligible: p.positions.every(m => m.value !== null),
      positions: p.positions.map(m => ({...m, source: null}))}))};
}
function uniform() {
  const bundle = fixture();
  bundle.parties.slice(0, 2).forEach((party, i) => party.positions.forEach(p => {
    p.value = i === 0 ? 1 : -1; p.status = i === 0 ? 'support' : 'reject';
  }));
  return bundle;
}
const answers = (bundle, n, value = 1) => Object.fromEntries(bundle.items.slice(0, n).map(i => [i.id, value]));

test('agreement, opposition, and explicit neutral are defined', () => {
  const b = uniform();
  const r = engine.calculate(b, answers(b, 16));
  assert.equal(r.parties[0].score, 100); assert.equal(r.parties[1].score, 0);
  assert.deepEqual(engine.calculate(b, answers(b, 16, 0)).parties.filter(p => p.eligible).map(p => p.score), [50, 50]);
});
test('all skipped and seven answers withhold aggregate scores', () => {
  const b = fixture();
  assert.equal(engine.calculate(b).status, 'insufficient');
  assert.equal(engine.calculate(b, answers(b, 7)).status, 'insufficient');
  assert.equal(engine.calculate(b, answers(b, 8)).status, 'ready');
  assert.deepEqual(engine.calculate(b).parties, []);
});
test('incomplete parties receive gaps rather than scores', () => {
  const b = fixture(), r = engine.calculate(b, answers(b, 16));
  assert.equal(r.parties[2].eligible, false); assert.equal(r.parties[2].score, undefined);
  assert.equal(r.parties[2].gaps[0].status, 'missing');
});
test('topic means normalize one and two answers equally', () => {
  const b = uniform(), a = answers(b, 9);
  b.parties[0].positions[8] = {...b.parties[0].positions[8], value: -1, status: 'reject'};
  assert.equal(engine.calculate(b, a).parties[0].score, 80);
  assert.equal(engine.calculate(b, a, {[b.items[8].topic_id]: 2}).parties[0].score, 100 * 4 / 6);
});
test('skips omit topics from current score but include them in bounds', () => {
  const b = uniform(), r = engine.calculate(b, answers(b, 8));
  assert.equal(r.parties[0].score, 100); assert.equal(r.parties[0].lower, 50); assert.equal(r.parties[0].upper, 100);
  assert.equal(r.parties[1].lower, 0); assert.equal(r.parties[1].upper, 50);
  assert.equal(r.parties[0].sensitivity, null);
});
test('no skips collapse bounds and sensitivity uses valid removals', () => {
  const b = fixture(), r = engine.calculate(b, answers(b, 16));
  for (const p of r.parties.filter(p => p.eligible)) {
    assert.equal(p.lower, p.score); assert.equal(p.upper, p.score); assert.equal(p.sensitivity.count, 16);
  }
});
test('weighted bounds match all 125 permitted completions of three skips', () => {
  const b = fixture(), a = answers(b, 13, 0.5), w = {'housing': 2, 'climate-energy': 2};
  const r = engine.calculate(b, a, w), scores = [];
  for (const x of [-1,-0.5,0,0.5,1]) for (const y of [-1,-0.5,0,0.5,1]) for (const z of [-1,-0.5,0,0.5,1]) {
    const completed = {...a, [b.items[13].id]: x, [b.items[14].id]: y, [b.items[15].id]: z};
    scores.push(engine.calculate(b, completed, w).parties[0].score);
  }
  assert.equal(r.parties[0].lower, Math.min(...scores)); assert.equal(r.parties[0].upper, Math.max(...scores));
});
test('exact ties and rounded equality are disclosed without reordering', () => {
  const b = uniform(); b.parties[1].positions = structuredClone(b.parties[0].positions);
  const r = engine.calculate(b, answers(b, 16));
  assert.equal(r.parties[0].comparisons[0].tied, true);
  assert.deepEqual(r.parties.map(p => p.id), ['mock-a', 'mock-b', 'mock-c']);
});
test('changing an answer replaces its contribution and can remove eligibility', () => {
  const b = uniform(), a = answers(b, 8);
  assert.equal(engine.calculate(b, a).parties[0].score, 100);
  a[b.items[0].id] = -1;
  assert.equal(engine.calculate(b, a).parties[0].score, 87.5);
  a[b.items[0].id] = null;
  assert.equal(engine.calculate(b, a).status, 'insufficient');
});
test('invalid answers, weights, mixed versions, and corrupt vectors fail closed', () => {
  const b = fixture();
  for (const bad of [true, 2, '1', NaN]) assert.throws(() => engine.calculate(b, {[b.items[0].id]: bad}));
  assert.throws(() => engine.calculate(b, {unknown: 1}));
  for (const bad of [0, 3, '2']) assert.throws(() => engine.calculate(b, {}, {housing: bad}));
  for (const mutate of [x => x.items[0].id = x.items[1].id, x => x.method_version = 'unknown',
    x => x.parties[0].positions.pop(), x => x.parties[0].positions[0].value = 0]) {
    const damaged = fixture(); mutate(damaged); assert.throws(() => engine.calculate(damaged));
  }
});
test('polarity reversal and party permutation preserve arithmetic', () => {
  const b = fixture(), a = answers(b, 16, 0.5), original = JSON.stringify(b);
  const scores = engine.calculate(b, a).parties.filter(p => p.eligible).map(p => p.score);
  assert.equal(JSON.stringify(b), original);
  b.parties.reverse();
  assert.deepEqual(engine.calculate(b, a).parties.filter(p => p.eligible).map(p => p.score), scores);
  for (const party of b.parties) for (const p of party.positions) if (p.value !== null) {
    p.value = -p.value; p.status = p.value === 1 ? 'support' : 'reject';
  }
  assert.deepEqual(engine.calculate(b, answers(b, 16, -0.5)).parties.filter(p => p.eligible).map(p => p.score), scores);
});
