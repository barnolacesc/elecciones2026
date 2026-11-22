# 2023 comparison pairwise-inference boundary — 2026-11-22

Roadmap package: **P1.8**, `2023-corpus-completion` (proposal-only). This is a
repository and method audit, not a real relationship review or implementation.

## Reconciled baseline

- `origin/main` at `6d7cc5e` has four `es-gen-2023` pilot source rows (PP,
  ERC, PNV and Sumar). All four are `published-unverified`, have rights
  `not_reviewed`, and lack an evidenced publication date in the register.
  Eight 2023 example statements are six `under_review` and two `draft`; six
  example relationships are `invalidated`. These counts are not a 2023
  candidature denominator or a publishable comparison set.
- Draft PR #101 remains conflicting and has no GitHub review; its successful
  checks are from 2026-10-12. Merged PR #166 carried forward an integration of
  its gate, not an approval of the six records. The current-main CI run
  `44930014014` passed, but neither CI run supplies source rights or editorial
  approval. Open P0/P1 PRs separately address source coverage, review,
  policy-question identity and comparison order; this handoff does not edit
  their records or decide their review questions.
- The current generator builds each relationship payload from exact
  `statement_ids` and keys it by the selected party pair. The 2023 OpenSpec
  requires independent review of an exact pair, but does not explicitly forbid
  deriving a third pair's agreement, divergence or rank from two reviewed
  edges. This is a *future-method boundary*, not a claim that the current
  two-party renderer performs such an inference.

## Proposed boundary for review

In a future full-party matrix, treat a relationship as a direct evidentiary
decision about one unordered party pair, exact statement versions, policy
question and reviewed scope. Do not close a graph transitively. Even if A–B
and B–C have reviewed agreement labels, A–C remains unreviewed until a human
checks those exact measures together; qualifications, constituency, timing or
the policy question may differ. The same prohibition applies to inferred
divergence, numeric ranking and a party-wide conclusion. An unreviewed A–C
edge may show each already publishable statement individually with honest
coverage wording, but no A–C relationship badge or summary.

A correction to B's statement should invalidate its own incident reviewed
edges and any derived display that explicitly depends on them; it must not
automatically recategorize unrelated A–C statements. The existing P1.2
comparison-set accounting remains the place to track unmatched measures.
No private review evidence or political-answer data belongs in the public
bundle.

## Decisions and fictional acceptance cases

Editors must decide whether the policy-question key is identical across all
three pairs, how to show a three-party matrix without implying pairwise
completeness, and the exact review quorum for a newly proposed A–C edge.
These decisions depend on the P0 source/rights and P1 proposal-granularity
gates. Tests should cover two A–B/B–C agreement edges with no A–C decision;
different qualifications on the three statements; mixed relationship types;
and one corrected operand. Static and browser projections must agree about
the absent edge. Fictional labels and IDs only; no real political position,
rights decision, approval, source file or public route changes here.
