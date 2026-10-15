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

  const api = Object.freeze({limits, validateScenario, calculate});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.SimulatorEngine = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
