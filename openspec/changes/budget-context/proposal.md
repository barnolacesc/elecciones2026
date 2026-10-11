# Proposal: Official budget context

## Why

Readers need sourced historical spending context alongside programme comparisons without treating an allocation as a party commitment, a policy cost, or an outcome. The approved 2023 PGE policy-by-section table provides a bounded starting point, subject to source, measurement, and human editorial review.

## What Changes

- Define an audited 2023 approved-PGE source and measurement contract, with exact provenance, consolidation, units, denominator, and explicit missing-data rules.
- Define a reviewed mapping to all eight core taxonomy topics and a Spanish mobile budget view, with shared macro context beside comparative measures, ranked bars, section details, and an equivalent table.
- Define versioned offline data bundles, reproducibility and correction checks, programme-detail and execution go/no-go decisions, and an optional offline-distribution evaluation that protects primary-site performance.

## Capabilities

### New Capabilities

- `budget-source-register`: Register immutable official sources, measurement contracts, rights, review, and reconciliation.
- `budget-topic-mapping`: Link official rows to the existing taxonomy without estimating topic amounts or hiding gaps.
- `budget-context-view`: Present Spanish historical macro figures and source notes alongside reviewed comparison measures.
- `budget-data-bundle`: Deliver deterministic, versioned snapshots with audit manifests and evaluate separate offline distribution.
- `budget-evidence-boundaries`: Separate statutory credits, execution, and political claims; gate programme detail and later execution views.

### Modified Capabilities

None. No main capabilities exist in `openspec/specs/` yet. The pending `mvp-programme-comparison` static-publication contract remains a dependency, not a main spec to modify.

## Impact

**Planning package:** E10.2 specification portion, Gate G10. This completes the existing draft artifacts for E10.1–E10.5; it does not complete their source audits or implementation. References: [#48](https://github.com/c2ventures/elecciones2026/issues/48), [#49](https://github.com/c2ventures/elecciones2026/issues/49), [#50](https://github.com/c2ventures/elecciones2026/issues/50), [#51](https://github.com/c2ventures/elecciones2026/issues/51), [#52](https://github.com/c2ventures/elecciones2026/issues/52).

The first product release covers only historical 2023 approved consolidated expenditure, chapters 1–8, by policy and administrative section. It is an optional post-MVP track and does not block the comparator, quiz, simulator, or CIS work. Future implementation extends the offline Python validation/build pipeline, reviewed content records, Spanish strings, and static Docker output. No public API, database, visitor data, or external runtime request is required.

Excluded: estimated or imputed official amounts, automatic party cost estimates, party performance scores, current 2026 amounts inferred from 2023, automatic execution comparisons, and programme detail without an audited compatible source. Offline distribution is an evaluation, not a service-worker or download release commitment. E10.4 remains the official programme-level audit; E10.5 remains the separate execution decision. Claim separation and offline evaluation add acceptance constraints without replacing those packages.

Editorial risks include misleading topic mappings and scope labels. Security risks include hostile source files and unsafe download archives. Privacy requires no telemetry or personal answers in bundles. Accessibility requires readable HTML, keyboard controls, and equivalent tables. Source rights, financial-data review, Spanish editorial review, and G10 publication approval remain pending; this proposal approves no figures or political claims.
