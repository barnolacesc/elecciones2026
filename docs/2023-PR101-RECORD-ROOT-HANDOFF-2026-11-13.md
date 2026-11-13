# PR #101 record-root integration handoff — 2026-11-13

Roadmap package: **E1.4 / P0–P1 integration evidence** for
`2023-corpus-completion`. This is a documentation-only audit after the 2026
corpus merge, not a resolution of PR #101, an OpenSpec approval, a source-use
decision, an editorial review or a release.

## Exact baseline

- `origin/main` is `d13ba68` (merged PR #237, 2026-11-12). PR #101 remains
  draft at `f8506a1`, with no GitHub reviews and `CONFLICTING` mergeability.
  Its successful checks ran on 2026-10-12, before the 2026 production-record
  changes. Main CI run `43325747158` passed on `d13ba68`; neither run tests a
  resolved PR #101 against this main.
- A fresh `git merge-tree --write-tree origin/main origin/pr-101-audit` exits
  with six conflict paths: the 2023 pilot review README and reuse handoff,
  MVP tasks, `src/elecciones2026/generator.py`, and the pilot editorial-audit
  and preview-acceptance tests. This is a simulated merge; no PR branch was
  modified. PR #233 already records the six-conflict and prior-CI boundary.
  The new issue here is the production record-root change in merged PR #237.
- The current register still has four `es-gen-2023` pilot rows (PP, ERC, PNV,
  Sumar), all `published-unverified`, rights `not_reviewed`, and with null
  publication dates. Its 2023 examples remain eight statements (six
  `under_review`, two `draft`) and six `invalidated` relationships. Those are
  repository counts, not an approved candidature denominator, rights decision,
  complete topic inventory or publishable political comparison.

## Narrow integration hazard

The main-branch validator now loads programmes from `record_root / "programmes"`.
`record_root` selects production records when `--records-dir` is supplied (or
when the CLI defaults a 2026 build to `content/elections/es-gen-2026`), and
otherwise selects `content/examples`. PR #101's older generator branch instead
loads `content/examples/programmes` inside the statement provenance check.
Taking that older hunk during conflict resolution would make a future 2026
production statement look for its programme in the historical example tree.
This is a code-path risk demonstrated by the two revisions, not an observed
published failure: there are currently no approved 2026 production claims.

PR #101's quote-free `link_only` and version-bound reuse checks are already
present in main's statement gate. Their presence does not grant rights: all
four 2023 source rows remain `not_reviewed`. Resolve PR #101 by comparing each
remaining change with current main, retaining the `record_root` selection and
the exact election/source/version validation. Do not restore older PP/ERC-only
copy over the four-row historical pilot or let historical examples substitute
for 2026 production records. Preserve unknown review/publication dates and
the private source-specific rights handoff; no merge strategy is approval.

## Reviewable exit evidence

1. On PR #101's resolved head, inspect the programme lookup and run the
   current `tests/test_election_corpus_refresh.py` production-record and
   election-isolation cases, plus `tests/test_pilot_2023_rehearsal.py` and
   the two conflicted pilot tests. Use fictional fixtures for any approved
   statement path. Check the default 2026 build and explicit 2023 private
   rehearsal separately; neither is a public release test.
2. Rerun full CI on the exact resolved head. PR #101's old green checks and
   current main's green run cannot validate their untested combination.
3. Keep P0 inclusion/document/rights decisions and P1 exact-source,
   statement, relationship and coverage reviews open for humans. A successful
   build cannot turn a source row into a political position or a coverage
   percentage.

Evidence: GitHub PR #101/#233/#237 metadata and main CI run `43325747158`;
read-only register/example counts; `git merge-tree`; current and PR #101
generator diffs. No private PDF, extracted text, political answer, review
store, source record or public route was changed. Local execution of the
Python build was unavailable: this host has Python 3.11, while the project
requires 3.14 and its generator uses newer f-string syntax. The relevant
merged-main CI passed, but the combined PR #101 code remains untested.
