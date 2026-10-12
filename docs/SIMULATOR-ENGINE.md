# Manual seat engine

Roadmap package: **E5.2**, tasks 2.1–2.2 of `seat-coalition-simulator`.

Status: technical implementation for private fixture work. The owner requested continuation after the E5.1 planning PR was presented. This permits the local engine work; it does not provide human rule, rights, Spanish copy, or G4/G6 release evidence. The engine is not included in generated site output and adds no active simulator route.

## Input and state contract

Load `site/simulator-engine.js` as `SimulatorEngine` in a browser, or require it in Node. Both exports provide the same pure functions. No DOM, network, logging, storage, or module dependency is required. Inputs are not modified, and the engine retains no scenario between calls. The future interface owns its in-memory rows and selections.

`validateScenario(groups)` accepts an array of 1–30 records:

```js
{id: 'group-a', label: 'Grupo A', seats: '175'}
```

IDs are nonempty strings, distinct within the scenario. Treat them as opaque identities; changing labels or row order must not change them. Labels are trimmed, nonempty plain text with at most 60 Unicode code points. Duplicate labels are compared after NFC normalization and Unicode lowercase conversion. Labels, including markup-like text, stay strings. The interface must render them with text nodes, not HTML insertion.

Seat counts are strings from text controls. After trimming outer whitespace, only ASCII digits are accepted; leading zeroes are allowed. Values must be integers from 0 through 350. Blank, signed, decimal, exponent, non-ASCII digit, boolean, numeric, and other non-string inputs are invalid. Parsed counts never replace raw text. Each returned group preserves `rawSeats`; the caller keeps the original label text for editing.

Returned scenarios contain `status`, `groups`, `errors`, `assigned`, and `unassigned`. Status is `complete` at exactly 350 assigned seats, `incomplete` below 350, or `invalid`. Incomplete scenarios retain the visible remainder. Invalid scenarios have null totals and no usable calculation. Each error has a `scope`, `field`, `code`, and row `index` or null for a scenario-wide error; messages are supplied by the future Spanish interface. Error codes contain no user-entered payload.

| Error code | Meaning |
|---|---|
| `group-count` | Groups are not an array of 1–30 rows. |
| `invalid-group` | A row is not a record. |
| `invalid-id`, `duplicate-id` | A stable identity is missing or repeated. |
| `invalid-label`, `duplicate-label` | A label fails length/content rules or duplicates another label. |
| `invalid-count`, `count-range` | A count fails the string grammar or the 0–350 range. |
| `total-exceeds-chamber` | Valid individual counts sum to more than 350. |
| `invalid-selection`, `unknown-group` | Selection input is malformed or refers to an absent group. |

## Coalition arithmetic

`calculate(groups, selectedIds = [])` returns the scenario plus `coalition`. Selected IDs must be an array of strings that refer to current groups. Repeating an ID counts that group once. Unknown IDs invalidate the result. No selection returns `coalition: null`; selecting a zero-seat group is a valid selection with a zero sum.

A coalition contains `seats`, `threshold: 176`, `deficit`, `surplus`, and `reachesThreshold`. Deficit and surplus are nonnegative. The threshold is a technical fixture constant for the proposed 350-seat profile. Profile/source validation and public activation belong to the separate integration tasks; calling this engine does not approve a public rule.

```js
const engine = require('./site/simulator-engine.js');
const groups = [
  {id: 'group-a', label: 'Grupo A', seats: '100'},
  {id: 'group-b', label: 'Grupo B', seats: '76'}
];
const result = engine.calculate(groups, ['group-a', 'group-b']);
// status: incomplete; assigned: 176; unassigned: 174
// coalition: {seats: 176, threshold: 176, deficit: 0,
//             surplus: 0, reachesThreshold: true}
```

These are generic assigned fixtures, not a real seat distribution or personal scenario. A sum of 175 lacks one seat for this threshold; 176 meets it; 177 exceeds it by one. An incomplete scenario can show a selected sum, but the interface must retain its incomplete label and unassigned count. The engine makes no claim about unassigned seats, actual votes, second-ballot outcomes, official parties, or agreements.

After an edit, call `calculate` with the current rows and selection; replace the previous result. After removal, remove that ID from selections before recalculation. Stale selected IDs fail closed. After reset, use one generic zero-seat row with an empty selection. The engine does not maintain a previous result or reconstruct selections.

## Verification

From the repository root:

```sh
node --check site/simulator-engine.js
node --test tests/simulator_behavior.cjs
```

The numeric suite uses generic groups only. It checks input limits and grammar, Unicode normalization and label length, duplicate IDs/labels, malformed rows, 0/350 boundaries, total excess, incomplete remainders, 175/176/177 thresholds, edits/removal/reselection, duplicate/unknown selections, input immutability, row permutation invariance, and all 351 two-group chamber splits. A VM check loads the browser export without browser/IO APIs. CI runs this suite independently of the existing quiz tests.

The interface, diagram, browser privacy, reviewed rule profile, build modes, and Docker parity remain E5.3/integration work. These unit checks do not establish accessibility, provider privacy, parliamentary review, or release approval. See the [simulator task record](../openspec/changes/seat-coalition-simulator/tasks.md).
