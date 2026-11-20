# 2023 corpus baseline after the 2026 source import — 2026-11-20

Roadmap package: **P0.2 / E1.4**, repository-evidence handoff only. This is not
an approved candidature manifest, source-rights decision, political review,
OpenSpec implementation approval, or release authorization. It updates the
baseline after the 2026 source import on main; it does not duplicate a
source-specific discovery or decide PR #101's disposition.

## Reconciled repository boundary

- Fetched `origin/main` is `d13ba683888de17714ad958a8034916168889cc3`
  (PR #237 merged). The merged 2023-first roadmap from PR #113 remains in
  `docs/PRODUCT-ROADMAP-2023-2026.md`. Root `ROADMAP.md` also has a later
  2026-11-01 direction for the full comparator. Neither direction is evidence
  of editorial or source-use approval.
- `content/sources/register.json` contains **four** `es-gen-2023` pilot source
  rows (PP, ERC, PNV, Sumar), each `published-unverified`, with
  `rights_review.status=not_reviewed` and no evidenced `publication_date`.
  Its **14** `es-gen-2026` rows belong to a different election; eight are
  `published-unverified`, five `missing`, and one `replaced`. All 14 have
  `rights_review.status=not_reviewed`. These are repository record counts,
  not a 2023 candidature denominator or a claim that any programme is usable.
- The 2023 example set has eight statements (six `under_review`, two `draft`)
  across housing, education, and health/social services. All six 2023 example
  relationships are `invalidated`. Four example coverage records remain
  `published-unverified`. The 2026 rows cannot fill the absent 2023 source,
  topic-search, rights, statement, or comparison evidence.
- The latest checked main CI run for this SHA is [43325747158](https://github.com/c2ventures/elecciones2026/actions/runs/43325747158),
  completed successfully on 2026-11-12. Its private-image publication job
  succeeded. That is engineering/delivery evidence, not human editorial
  review, complete 2023 coverage, or permission to route a public site.

## PR #101 integration boundary

Draft [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is
still at `f8506a10b6784edf597e9e315f4c000dc0d341af`, has no GitHub
reviews, and GitHub reports it conflicting with main. A fresh
`git merge-tree --write-tree origin/main origin/pr-101` reports six conflicted
paths: the two 2023 pilot-review documents, MVP tasks, `generator.py`, and
two pilot tests. Its 2026-10-12 green checks do not test the current combined
tree. Draft [PR #219](https://github.com/c2ventures/elecciones2026/pull/219)
already proposes a supersession disposition, while [PR #238](https://github.com/c2ventures/elecciones2026/pull/238)
addresses the production-record-root merge boundary; this handoff does not
repeat either decision or alter PR #101.

## Next P0/P1 gate

Keep `es-gen-2023` accounting isolated from `es-gen-2026`. Obtain the
human-approved 2023 inclusion rule and corrected candidature manifest, then
reconcile document versions, private archive identity, exact-version rights,
topic searches, statement decisions, and independent relationship decisions
under the proposal-only `2023-corpus-completion` change. The four pilot rows
must not be presented as all 2023 parties, and the new 2026 rows must not be
used to close the 2023 coverage gap. PR #101's conflict/disposition remains
with its owner; no candidate record is promoted by this audit.

## Verification and limits

Evidence: fetched Git objects and GitHub PR/CI metadata; parsed the checked-in
JSON source, statement, relationship and coverage records by election ID;
simulated, but did not complete, PR #101's merge. No private PDF, reviewer
store, publisher page, political answer, or live deployment was inspected.
The baseline is a snapshot of `d13ba68`; later source or PR changes require
a new reconciliation. Local source-register and fixture assertions are
engineering checks only.
