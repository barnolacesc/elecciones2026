/* Pure local arithmetic for programme-measure alignment. No browser state or IO. */
(function (root) {
  'use strict';
  const answersAllowed = new Set([-1, -0.5, 0, 0.5, 1]);
  const coreTopics = ['housing', 'education', 'health-social-services', 'economy-work-tax',
    'immigration', 'foreign-policy-eu', 'climate-energy', 'institutions-rights'];
  function assert(condition, message) { if (!condition) throw new Error(message); }

  function validate(bundle) {
    assert(bundle && bundle.schema_version === '1.0.0' && bundle.method_version === '1.0.0'
      && typeof bundle.version === 'string' && bundle.version.length > 0, 'Invalid quiz version');
    assert(['mock', 'reviewed'].includes(bundle.mode), 'Invalid quiz mode');
    assert(typeof bundle.election_id === 'string' && bundle.election_id.length > 0, 'Invalid election identity');
    assert(bundle.mode !== 'mock' || bundle.election_id === 'quiz-fixture', 'Mixed quiz identity');
    assert(Array.isArray(bundle.topics) && bundle.topics.length === 8
      && new Set(bundle.topics.map(t => t.id)).size === 8
      && coreTopics.every(id => bundle.topics.some(t => t.id === id)), 'Invalid topic set');
    assert(Array.isArray(bundle.items) && bundle.items.length === 16, 'Invalid item count');
    assert(bundle.items.every(i => /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(i.id)
      && /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(i.measure_id)
      && typeof i.text === 'string' && i.text.trim().length > 0
      && Array.isArray(i.qualifications) && i.qualifications.every(q => typeof q === 'string')), 'Invalid item');
    assert(new Set(bundle.items.map(i => i.id)).size === 16
      && new Set(bundle.items.map(i => i.measure_id)).size === 16, 'Duplicate item or measure');
    for (const topic of bundle.topics) {
      assert(bundle.items.filter(i => i.topic_id === topic.id).length === 2, 'Invalid topic quota');
    }
    assert(Array.isArray(bundle.parties) && new Set(bundle.parties.map(p => p.id)).size === bundle.parties.length,
      'Invalid party set');
    for (const party of bundle.parties) {
      assert(/^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/.test(party.id)
        && typeof party.name === 'string' && party.name.length > 0, 'Invalid party identity');
      assert(Array.isArray(party.positions) && party.positions.length === 16, 'Incomplete position vector');
      for (const [index, item] of bundle.items.entries()) {
        const p = party.positions[index];
        assert(p.item_id === item.id, 'Mixed item order');
        assert((p.status === 'support' && p.value === 1) || (p.status === 'reject' && p.value === -1)
          || (['missing', 'partial', 'conflicting', 'unverified', 'replaced'].includes(p.status)
            && p.value === null && typeof p.reason === 'string'), 'Invalid position');
        if (bundle.mode === 'mock') assert(p.source === null, 'Mock source must not be a political citation');
        if (bundle.mode === 'reviewed' && p.value !== null) {
          const source = p.source;
          assert(source && /^[a-f0-9]{64}$/.test(source.sha256)
            && (source.page || source.section) && source.programme_id && source.statement_id
            && source.version && source.review_date && source.rights_status
            && Array.isArray(source.qualifications), 'Invalid citation');
          const url = new URL(source.url);
          assert(url.protocol === 'https:' && !url.username && !url.password, 'Unsafe citation');
        }
      }
      assert(party.eligible === party.positions.every(p => p.value !== null), 'Invalid eligibility');
    }
    assert(bundle.available === (bundle.parties.filter(p => p.eligible).length >= 2), 'Invalid availability');
    return bundle;
  }

  function core(bundle, answers, weights, party) {
    const topics = bundle.topics.map(topic => {
      const details = bundle.items.flatMap((item, index) => {
        if (item.topic_id !== topic.id || answers[item.id] == null) return [];
        const answer = answers[item.id], position = party.positions[index].value;
        const quarters = 4 - Math.abs(2 * answer - 2 * position);
        return [{item, answer, position, quarters, alignment: quarters / 4,
          source: party.positions[index].source}];
      });
      const sum = details.reduce((total, d) => total + d.quarters, 0);
      return {id: topic.id, name: topic.name, weight: weights[topic.id], count: details.length,
        mean: details.length ? sum / (4 * details.length) : null,
        eighths: details.length ? sum * (2 / details.length) : 0,
        lowerQuarters: sum, upperQuarters: sum + 4 * (2 - details.length), details};
    });
    const active = topics.filter(t => t.count > 0);
    const activeWeight = active.reduce((sum, t) => sum + t.weight, 0);
    const numerator = 100 * active.reduce((sum, t) => sum + t.weight * t.eighths, 0);
    const denominator = 8 * activeWeight;
    const fullWeight = topics.reduce((sum, t) => sum + t.weight, 0);
    return {topics, numerator, denominator, score: denominator ? numerator / denominator : null,
      lower: 100 * topics.reduce((sum, t) => sum + t.weight * t.lowerQuarters, 0) / (8 * fullWeight),
      upper: 100 * topics.reduce((sum, t) => sum + t.weight * t.upperQuarters, 0) / (8 * fullWeight)};
  }

  function calculate(bundle, answers = {}, suppliedWeights = {}) {
    validate(bundle);
    assert(answers && typeof answers === 'object' && !Array.isArray(answers), 'Invalid answers');
    const ids = new Set(bundle.items.map(i => i.id));
    for (const [id, answer] of Object.entries(answers)) {
      assert(ids.has(id) && (answer === null || answersAllowed.has(answer)), 'Invalid answer or set mismatch');
    }
    for (const [id, weight] of Object.entries(suppliedWeights)) {
      assert(coreTopics.includes(id) && [1, 2].includes(weight), 'Invalid weight');
    }
    const weights = Object.fromEntries(bundle.topics.map(t => [t.id, suppliedWeights[t.id] ?? 1]));
    const answered = bundle.items.filter(i => answers[i.id] != null);
    const topicCount = new Set(answered.map(i => i.topic_id)).size;
    const ready = answered.length >= 8 && topicCount >= 4;
    const result = {status: !bundle.available ? 'unavailable' : ready ? 'ready' : 'insufficient',
      answered: answered.length, topicCount, weights, parties: [],
      skipped: bundle.items.filter(i => answers[i.id] == null).map(i => i.id)};
    if (result.status !== 'ready') return result;
    const ordered = [...bundle.parties].sort((a, b) => a.name.localeCompare(b.name, 'es') || a.id.localeCompare(b.id));
    for (const party of ordered) {
      if (!party.eligible) {
        result.parties.push({id: party.id, name: party.name, eligible: false,
          gaps: party.positions.filter(p => p.value === null)});
        continue;
      }
      const current = core(bundle, answers, weights, party);
      const removals = answered.flatMap(item => {
        const remaining = {...answers, [item.id]: null};
        const other = answered.filter(i => i.id !== item.id);
        if (other.length < 8 || new Set(other.map(i => i.topic_id)).size < 4) return [];
        return [{itemId: item.id, score: core(bundle, remaining, weights, party).score}];
      });
      const activeWeight = current.topics.filter(t => t.count).reduce((sum, t) => sum + t.weight, 0);
      result.parties.push({id: party.id, name: party.name, eligible: true, ...current,
        display: Math.floor(current.score + 0.5),
        contributions: current.topics.map(t => ({...t,
          normalizedWeight: t.count ? t.weight / activeWeight : 0,
          contribution: t.count ? 100 * t.mean * t.weight / activeWeight : 0})),
        sensitivity: removals.length ? {min: Math.min(...removals.map(r => r.score)),
          max: Math.max(...removals.map(r => r.score)), count: removals.length,
          largestChange: [...removals].sort((a, b) => Math.abs(b.score - current.score)
            - Math.abs(a.score - current.score))[0]} : null});
    }
    const scored = result.parties.filter(p => p.eligible);
    for (const party of scored) {
      party.comparisons = scored.filter(p => p.id !== party.id).map(other => ({
        id: other.id, name: other.name,
        tied: party.numerator * other.denominator === other.numerator * party.denominator,
        smallDifference: Math.abs(party.numerator * other.denominator - other.numerator * party.denominator)
          <= party.denominator * other.denominator,
        sameDisplay: party.display === other.display,
        overlappingBounds: party.lower <= other.upper && other.lower <= party.upper
      }));
    }
    return result;
  }
  const api = Object.freeze({validate, calculate});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.QuizEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
