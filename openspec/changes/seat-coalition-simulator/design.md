# Design: Seat and coalition simulator

Roadmap package: **E5.1**. Planning only; human rule/method/copy acceptance and G6 remain open.

## Context

See [proposal.md](proposal.md) for purpose and the two capability specs for observable behavior. The current generator in `src/elecciones2026/generator.py` builds static Spanish routes, shares a base renderer, and fingerprints quiz assets. `site/quiz-engine.js` and `site/quiz-ui.js` separate arithmetic from browser controls. No simulator exists. Preserve the comparator, budget, quiz, source, and recovery paths.

## Goals / Non-Goals

**Goals:** a small auditable arithmetic module; one immutable reviewed chamber profile; accessible input and equivalent seat views; reproducible static integration; no dependence on political programmes.

**Non-Goals:** official candidacy registration, real-result presets, a vote model, remote computation, persistent scenarios, or personalized sharing. The first implementation has no second-ballot model.

## Decisions

### 1. One rule profile and explicit scope

Use Congress only. Do not offer a configurable chamber total or majority type: those would require additional sourced rules and acceptance cases. The proposed profile uses 350 seats, with absolute threshold `floor(350 / 2) + 1 = 176`. A 175-seat sum lacks one seat for this arithmetic threshold; 176 meets it; 177 exceeds it by one.

Official sources consulted on 2026-10-12:

| Source | Exact locator | Ground for the proposed contract |
|---|---|---|
| [LOREG, BOE-A-1985-11672](https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672) | Article 162.1 | Establishes a Congress with 350 members. |
| [Constitution, BOE-A-1978-31229](https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229) | Article 99.3 | First investiture vote requires an absolute majority; the same proposal can go to a second vote after 48 hours under a simple-majority rule. |
| [Congress Rules, BOE-A-1982-5196](https://www.boe.es/buscar/act.php?id=BOE-A-1982-5196) | Article 171.5 | Confirms those first- and second-ballot rules in the parliamentary procedure. |

The 176 value is arithmetic derived from the 350-member profile and the absolute-majority rule. It is not a prediction of votes or a sufficient account of the entire investiture procedure. Selected seats are assumed only for a sum, not pledged votes. A sub-176 set cannot be labelled incapable of supporting investiture. A different law, chamber, vacancy interpretation, or vote simulation needs a separate reviewed profile or change.

The BOE consolidated pages were read directly. They are explanatory access to consolidated rules, not retained legal-signoff evidence. No human rule or reuse approval is inferred. Before public activation, retain source versions or hashes, consultation dates, exact locators, rule review, and approved public paraphrases. Recheck applicable rules; conflicting or stale evidence disables the feature.

### 2. Manual groups and pure arithmetic

Use stable page-local IDs and user labels, not the source-register candidacy list. This lets arithmetic work without asserting that a group is an official candidacy. Initial state is one editable generic group with zero seats, no selection, and 350 unassigned seats. Add up to 30 rows. Labels are trimmed plain text, capped at 60 Unicode code points; reject duplicates after Unicode NFC normalization and case-insensitive comparison. These product limits are proposed for review.

Parse only ASCII digit strings after trimming outer whitespace. Blank, signed, exponent, decimal, or nonnumeric inputs remain errors. Each row is 0–350; any sum above 350 invalidates the scenario. Retain raw text for correction; never silently coerce it. A sum below 350 remains useful as an incomplete scenario, with a visible remainder and no inference about the missing seats.

Proposed files: `site/simulator-engine.js` for pure validation and totals; `site/simulator-ui.js` for DOM state and rendering; `site/simulator.css` for the phone view. The engine returns explicit valid/incomplete/error states and a selected sum, deficit, or surplus. It never reads the DOM or network. Unknown or duplicate group IDs in an external fixture are rejected; selections use unique valid IDs. Test with generic numeric groups only.

### 3. Accessible diagram and Spanish controls

Use a semantic form and table. Build a local SVG hemicycle from the same validated counts, including neutral unassigned markers; keep it decorative when the table already conveys all facts. Use insertion order and distinguishable neutral colors plus text labels. Geometry represents counts only, without implying political left/right. A graphic interaction must have equivalent labelled controls outside the SVG.

Draft Spanish text for review:

- “Introduce un reparto hipotético de escaños. No es un resultado electoral ni una predicción.”
- “Escaños asignados”, “Escaños sin asignar”, “Selecciona grupos para sumar sus escaños”.
- “La suma alcanza 176 escaños: mayoría absoluta en este escenario.”
- “Faltan {n} escaños para alcanzar 176.”
- “Esta suma no implica un acuerdo entre los grupos ni asegura cómo votarán.”
- “La segunda votación de investidura usa otra regla. Este simulador no calcula esa votación.”
- “Tus datos se pierden al salir o recargar la página.”

Do not treat these drafts as approved publication text. Keep validation errors associated with fields, announce concise total/result changes, and preserve usable focus after adding/removing rows. Full WCAG 2.2 AA acceptance includes native zoom, screen readers, text spacing, keyboard and device checks; automated layouts do not establish conformance.

### 4. Static integration and memory boundary

Use the existing base renderer for `/simulador/`, with static purpose, method, and official source links available without scripts. Fingerprint all local assets through the existing generator pattern. Do not use a frontend framework, CDN library, or scoring API. Bundle rule metadata once; no answer-dependent resource requests exist.

Add an explicit build mode: `unavailable` by default, `mock` for authorized private fixture work, and `reviewed` only after rule/copy/release prerequisites are recorded. Mock mode is nonindexable, has no official party preset or approval mark, and requires opt-in. A default rebuild removes stale simulator scripts, data, and personalized state; preserve other routes. Reviewed builds reject unapproved profiles. Sitemap/navigation inclusion follows the actual activation mode; an unavailable static method page cannot imply an active tool.

Scenario state stays in a page-local object and clears on reset, page exit, reload and back/forward-cache restoration. No localStorage, sessionStorage, history state, URL encoding, cookies, analytics, or console logging of scenarios. Source links use `noopener noreferrer` and indicate external navigation. No custom scenario share controls enter the first version. Provider-level privacy remains a release review, not a claim established by browser tests.

### 5. Bounded packages and ownership

| Package | Scope | Dependencies and verification |
|---|---|---|
| E5.2 | Pure engine, numeric fixtures, arithmetic/input guide | Human E5.1 acceptance and implementation request; validate 175/176/177, all invalid inputs, remainder, duplicate IDs/labels, edits, and permutation invariance. |
| E5.3 | Spanish controls, SVG/table parity, local CSS, browser cases | E5.2 engine contract; mobile/keyboard semantics, long labels, stale-result removal, focus, no-script state, and memory/network checks. |
| E5.3 integration | Reviewed rule authoring/profile validation, generator/build options, routing, navigation and CI | Coordinate shared generator/Docker/CI ownership; reject unreviewed profiles, fixed-input determinism, default withdrawal and static image parity. |
| E5.4 | Sharing decision only | Deferred; no personalized URL work without a separate approved privacy/length/abuse contract. |

Keep political-source content outside these packages. Parallel integration and UI work can follow agreement on the pure engine/profile contract; shared files have one assigned owner. Create implementation issues from accepted tasks after the plan is reviewed, with prerequisites and release limits stated.

## Risks / Trade-offs

- [Seat sum mistaken for promised votes] → visible scenario scope and a separate second-ballot explanation.
- [Incomplete scenario mistaken for a full chamber] → explicit unassigned count in both diagram and table.
- [Custom labels mistaken for official groups] → no inferred candidacy metadata or default real-party distribution.
- [Source or rule defect persists through recovery] → invalidate the profile and withdraw scoring instead of restoring an unapproved rule.
- [Political scenario reaches diagnostics] → no application state logging; inspect origin/edge/monitoring policy before G6.

## Migration Plan

1. Obtain human E5.1 method, rule, rights, and Spanish draft decisions. Record the explicit scope of any private implementation permission before G4.
2. On a new implementation request, land the engine, UI, and static integration in bounded branches with relevant checks and evidence beside each task.
3. Build and benchmark off-host; use the actual 1-vCPU/1-GB IONOS target only for an authorized representative run against approved service targets. Planning does not approve traffic tests.
4. Complete G4/G6 and exact-artifact approval before deployment. Verify source links, availability mode, privacy, and route/static parity on the target.
5. Rehearse A-to-B-to-A functional recovery only with still-valid reviewed profiles. For a rule or source defect, deploy the unavailable artifact and remove stale scoring resources; never restore invalidated rules. Record hashes and timing.
