# 2023 quantitative-comparability handoff — 2026-10-28

Roadmap package: P1 quantitative-comparability method
(`2023-corpus-completion`, proposal-only). This audit introduces no political
position, value, rights decision, editorial approval or public output.

## Reconciled baseline

- `origin/main` at `8e2fab4` has four registered `es-gen-2023` pilot sources:
  PP, ERC, PNV and Sumar. Each is `published-unverified`, with rights
  `not_reviewed` and no evidenced publication date in the register. This is a
  pilot source count, not the approved 2023 candidature denominator.
- The current `statement.schema.json` has a free-text `summary` and
  `qualifications` but no structured quantity role, unit, period or
  denominator. The `relationship.schema.json` has `summary` and `differences`
  but no structured comparison basis or calculation provenance. The P1 draft
  asks for stated amount/timing and reviewed comparability, without an
  explicit gate for derived values or unlike numeric bases.
- PR #101 is open and conflicting with main; PR #166 proposes a mergeable
  superseding gate but its CI did not execute tests because of a GitHub
  account billing/spending-limit block. Neither grants source rights or human
  political review. Open P1 PRs on document scope, relationship collisions,
  correction propagation and initiative lineage address distinct boundaries;
  this handoff does not edit their real records or resolve their review gates.

## Proposed boundary

Keep a version-bound, private value/basis ledger for any quantitative claim.
Distinguish a cited figure from an editorial calculation and a future target
from a current baseline. Before ranking two measures, reviewers must establish
compatible policy question, value role, unit, period, population/denominator,
geography and conditions. Unknown or mismatched bases mean no numeric ranking,
not political disagreement. Keep both source-linked statements and show their
limitations. A calculation needs explicit source inputs, formula, rounding and
separate human review; it cannot cure missing rights or source verification.

## Review and test handoff

The proposed OpenSpec delta contains fictional annual/total,
percentage/percentage-point, target/baseline, missing-denominator and
same-basis cases. No real programme quantity is reproduced here. Owners must
decide permitted transformations, materiality, review responsibility and
Spanish copy before implementation. Later implementation must test that a
changed source value or qualifier invalidates every derived claim and linked
relationship. Passing CI is not the owner/editorial decision.
