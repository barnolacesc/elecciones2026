# Proposal: Method-aware multi-source poll observatory

Status: proposal only; not implementation-ready. Roadmap phase: P5.

## Why

CIS alone cannot represent the range of published surveys. Readers need to see
source, fieldwork and methodology before comparing trends.

## What Changes

- Expand the existing CIS-only observatory proposal to include original studies
  from public bodies and reputable pollsters/media, with explicit inclusion,
  rights and correction rules.
- Preserve fieldwork/publication dates, sample/population, mode, sponsor,
  wording, direct response versus estimate, uncertainty and version.
- Provide accessible charts/tables with method caveats. Identify CIS accurately
  as a public institution attached to the Spanish government; neither dismiss
  nor privilege its numbers solely because of that affiliation.
- Block incomparable series and avoid a composite forecast unless separately
  specified and validated. Keep survey estimates apart from election results.

## Capabilities

### Modified Capabilities

- `cis-source-register`: extend source records beyond CIS only.
- `poll-series`: compare only methodologically compatible measures.

Names refer to the existing unarchived `cis-data-observatory` change; reconcile
its capabilities during the later spec/design phase instead of duplicating them.

## Impact and gates

Requires a source/methodology inventory, lawful use review, specs, design and
tasks before implementation. Publish no poll result without original-source
verification, date/method context and editorial review.
