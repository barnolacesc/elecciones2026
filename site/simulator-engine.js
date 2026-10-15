/* Pure manual-seat arithmetic. No browser state, political data, or IO. */
(function (root) {
  'use strict';

  // Technical fixture limits; public rule approval belongs to the build profile.
  const limits = Object.freeze({totalSeats: 350, threshold: 176, maxGroups: 30, maxLabelLength: 60});

  function error(scope, field, code, index = null) {
    return {scope, field, code, index};
  }

  function invalid(groups, errors) {
    return {status: 'invalid', groups, errors, assigned: null, unassigned: null};
  }

  function validateScenario(input) {
    if (!Array.isArray(input) || input.length < 1 || input.length > limits.maxGroups) {
      return invalid([], [error('scenario', 'groups', 'group-count')]);
    }
    const errors = [];
    const ids = new Set();
    const labels = new Map();
    const groups = [];
    for (const [index, raw] of input.entries()) {
      if (!raw || typeof raw !== 'object' || Array.isArray(raw)) {
        errors.push(error('group', 'group', 'invalid-group', index));
        continue;
      }
      const {id, label, seats: rawSeats} = raw;
      if (typeof id !== 'string' || !id.trim()) {
        errors.push(error('group', 'id', 'invalid-id', index));
      } else if (ids.has(id)) {
        errors.push(error('group', 'id', 'duplicate-id', index));
      } else {
        ids.add(id);
      }

      const displayLabel = typeof label === 'string' ? label.trim() : null;
      if (displayLabel === null || !displayLabel || [...displayLabel].length > limits.maxLabelLength) {
        errors.push(error('group', 'label', 'invalid-label', index));
      } else {
        const key = displayLabel.normalize('NFC').toLowerCase();
        if (labels.has(key)) {
          const previous = labels.get(key);
          // Associate the same error with both fields so either can be corrected.
          if (!errors.some(e => e.code === 'duplicate-label' && e.index === previous)) {
            errors.push(error('group', 'label', 'duplicate-label', previous));
          }
          errors.push(error('group', 'label', 'duplicate-label', index));
        } else {
          labels.set(key, index);
        }
      }

      let seats = null;
      if (typeof rawSeats !== 'string' || !/^[0-9]+$/.test(rawSeats.trim())) {
        errors.push(error('group', 'seats', 'invalid-count', index));
      } else {
        const number = Number(rawSeats.trim());
        if (!Number.isSafeInteger(number) || number > limits.totalSeats) {
          errors.push(error('group', 'seats', 'count-range', index));
        } else {
          seats = number;
        }
      }
      groups.push({id, label: displayLabel, seats, rawSeats});
    }
    if (errors.length) return invalid(groups, errors);
    const assigned = groups.reduce((sum, group) => sum + group.seats, 0);
    if (assigned > limits.totalSeats) {
      return invalid(groups, [error('scenario', 'assigned', 'total-exceeds-chamber')]);
    }
    return {status: assigned === limits.totalSeats ? 'complete' : 'incomplete',
      groups, errors: [], assigned, unassigned: limits.totalSeats - assigned};
  }

  function calculate(input, selectedIds = []) {
    const scenario = validateScenario(input);
    if (scenario.status === 'invalid') return {...scenario, coalition: null};
    if (!Array.isArray(selectedIds)) {
      return {...invalid(scenario.groups, [error('selection', 'selectedIds', 'invalid-selection')]),
        coalition: null};
    }
    const known = new Map(scenario.groups.map(group => [group.id, group]));
    const selected = new Set();
    for (const id of selectedIds) {
      if (typeof id !== 'string' || !known.has(id)) {
        return {...invalid(scenario.groups, [error('selection', 'selectedIds', 'unknown-group')]),
          coalition: null};
      }
      selected.add(id);
    }
    if (!selected.size) return {...scenario, coalition: null};
    const seats = [...selected].reduce((sum, id) => sum + known.get(id).seats, 0);
    return {...scenario, coalition: {seats, threshold: limits.threshold,
      deficit: Math.max(0, limits.threshold - seats), surplus: Math.max(0, seats - limits.threshold),
      reachesThreshold: seats >= limits.threshold}};
  }

  function serializeScenario(input, selectedIds = []) {
    const scenario = validateScenario(input);
    if (scenario.status === 'invalid') return null;
    const cleanSelected = Array.isArray(selectedIds)
      ? selectedIds.filter(id => scenario.groups.some(g => g.id === id))
      : [];
    const payload = {
      g: scenario.groups.map(g => [g.id, g.label, String(g.seats)]),
      c: cleanSelected
    };
    const json = JSON.stringify(payload);
    let b64;
    if (typeof Buffer !== 'undefined') {
      b64 = Buffer.from(json, 'utf8').toString('base64');
    } else if (typeof btoa === 'function') {
      b64 = btoa(encodeURIComponent(json).replace(/%([0-9A-F]{2})/g, (_, p1) => String.fromCharCode('0x' + p1)));
    } else {
      return null;
    }
    return b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  function deserializeScenario(serialized) {
    if (typeof serialized !== 'string' || !serialized.trim()) return null;
    let raw = serialized.trim();
    if (raw.includes('?')) {
      const match = raw.match(/[?&]s=([^&#]+)/);
      if (!match) return null;
      raw = match[1];
    }
    let base64 = raw.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) base64 += '=';
    let json;
    try {
      if (typeof Buffer !== 'undefined') {
        json = Buffer.from(base64, 'base64').toString('utf8');
      } else if (typeof atob === 'function') {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        json = decodeURIComponent(Array.from(bytes, b => '%' + b.toString(16).padStart(2, '0')).join(''));
      } else {
        return null;
      }
      const data = JSON.parse(json);
      if (!data || typeof data !== 'object' || !Array.isArray(data.g)) return null;
      const groups = [];
      for (const item of data.g) {
        if (!Array.isArray(item) || item.length < 3) return null;
        groups.push({
          id: String(item[0]),
          label: String(item[1]),
          seats: String(item[2])
        });
      }
      const scenario = validateScenario(groups);
      if (scenario.status === 'invalid') return null;
      const selected = Array.isArray(data.c) ? data.c.map(String).filter(id => scenario.groups.some(g => g.id === id)) : [];
      return {groups, selectedIds: selected};
    } catch (_) {
      return null;
    }
  }

  function stableSimulatorUrl(href, groups, selectedIds = []) {
    const url = new URL(href);
    url.search = '';
    url.hash = '';
    url.pathname = url.pathname.replace(/index\.html$/, '');
    if (groups && groups.length) {
      const serialized = serializeScenario(groups, selectedIds);
      if (serialized) {
        url.searchParams.set('s', serialized);
      }
    }
    return url.toString();
  }

  const api = Object.freeze({limits, validateScenario, calculate, serializeScenario, deserializeScenario, stableSimulatorUrl});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SimulatorEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);

