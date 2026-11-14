# 2023 comparison order: private method audit

Roadmap package: **P1.8**, `2023-corpus-completion` (proposal-only).
Baseline: `origin/main` `d13ba683`, 2026-11-14. This is an engineering and
methodology audit, not a political, rights, editorial or release decision.

## Observed boundary

- `build_comparison_payload` in `src/elecciones2026/generator.py` emits
  relationship-backed measure groups sorted by relationship ID, then unmatched
  statement groups sorted by statement ID. It sorts party metadata by party ID.
  These stable identifier orders support deterministic output but have no
  documented editorial meaning. The two-pass emission also puts every paired
  group before every unmatched group, regardless of policy question.
- The draft P1.2 comparison-set ledger accounts for included and unmatched
  measures; it does not yet define their display sequence or explain whether
  grouping affects the perceived importance of an initiative. This audit does
  not assert a live political skew: the four 2023 pilot sources are still
  `published-unverified`, rights `not_reviewed`, and no complete 2023
  candidature denominator is approved.
- Open PR #101 remains conflicting and lacks human review. Its October CI
  success tested its old head, not a resolved candidate against this baseline.
  Main CI run 43325747158 succeeded on `d13ba683`; this does not approve a
  comparison order or any political content. Open PRs #236 and #239 address
  cross-topic placement and historical coverage respectively, not this
  presentation-order decision.

## Proposed review handoff

Before showing a full 2023 comparator, an editorial owner should approve a
versioned ordering rule for measure groups and party columns/cards. The rule
must be independent of party favourability, relationship type, claim strength,
source availability and file/record ID. Record any user-selected sort option
and its meaning; no default may silently promote paired statements over
unmatched statements. Keep the P1.2 set ledger as the completeness authority:
ordering must not remove, merge or reclassify its entries. Stable tie-breaking
is an engineering choice only after the substantive rule is reviewed.

The owner should decide the neutral default (for example, a reviewed taxonomy
sequence with an explicit within-topic rule), how to handle multiple measures
for one policy question, whether party order can be user-controlled, and what
short Spanish method explanation a reader needs. A neutral rule cannot be
inferred from alphabetic IDs or from a passing test. This draft does not choose
the politically appropriate order.

Fictional acceptance cases: renaming only a record ID must not elevate a
measure; a paired and an unmatched measure must both remain visible under the
approved sequence; swapping party selection must preserve each party's exact
claims and qualifications; adding a newly approved measure must update the
ledger without silently pushing an unrelated measure out of scope. Test both
static and browser projections once the rule and implementation are reviewed.

No source PDFs, political positions, rights records, reviewer marks, public
copy, renderer or deployment changed in this package. The next step is human
method review, followed by a separate implementation package with fictional
fixtures and mobile comprehension checks.
