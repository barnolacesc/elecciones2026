# Proposal: Complete the reviewed 2023 programme corpus

Status: proposal for editorial and OpenSpec review; not implementation-ready.
Roadmap phases: P0–P1. Election ID: `es-gen-2023`.

## Why

The existing four-party pilot and approved records do not cover every relevant
2023 general-election programme or proposal topic. Readers need transparent
coverage, source-linked initiatives and reviewed comparisons, not apparent
completeness inferred from a working UI.

## What Changes

- Define and approve an eligible-candidacy rule, an enumerated source register,
  versioned topic taxonomy and explicit missing/partial/replaced states.
- Extend the private source-to-review pipeline to produce candidate initiatives
  across all in-scope programmes and their topics. Require exact version/page,
  qualifications, rights state and human review for published summaries.
- Review relationships only between measures addressing the same question;
  record disagreement, agreement, gaps and corrections without false equivalence.
- Expose coverage and limitations in the existing mobile comparator. Keep PDFs
  and extracted text outside the public build and prevent cross-election mixing.

## Capabilities

### Modified Capabilities

- `programme-provenance`: add complete 2023 inventory/coverage contract.
- `editorial-statements`: add reviewed initiative breadth and audit trail.
- `programme-comparison`: add reviewed topic/measure coverage indicators.

These capabilities are defined by the existing unarchived MVP change. Do not
edit its published artifacts without first reconciling current contracts.

## Impact and gates

Affected areas: private source register/archive, `content/`, offline validator,
static generation, mobile coverage views and tests. The first implementation
package must follow reviewed specs, design and tasks for this change. Cesc and
the editorial owners decide party inclusion, source rights and political claims.
An agent-generated extraction or passing CI is not approval or public release.
