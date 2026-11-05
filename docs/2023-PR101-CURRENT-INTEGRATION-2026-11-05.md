# PR #101 current-main integration gate — 2026-11-05

Roadmap package: **P0/P1 integration-readiness audit** under
`2023-corpus-completion` and the existing `mvp-programme-comparison` E1.4
tasks. This is a proposal-only, repository-evidence handoff. It neither
resolves PR #101 nor approves a source, right, statement, relationship or
release. The earlier [PR #101 handoff](2023-PR101-RECONCILIATION-2026-10-23.md)
records an older main-branch conflict set; its counts must not be reused as a
current merge result.

## Reconciled inputs

- Fetched `origin/main` is `488b6f5` (2026-11-05). PR #113 is merged, so
  `docs/PRODUCT-ROADMAP-2023-2026.md` is on main. Its P0/P1 sequence and the
  2026-11-01 comparator priority in `ROADMAP.md` govern this handoff.
- Draft [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is
  still open at `f8506a1`, with zero GitHub reviews and `CONFLICTING` merge
  state. Its four successful CI jobs ran on 2026-10-12, before current main;
  release was skipped. They do not test a reconciled tree or constitute human
  review. [Issue #100](https://github.com/c2ventures/elecciones2026/issues/100)
  remains open.
- Current main has four `es-gen-2023` source rows (PP, ERC, PNV, Sumar): all
  `published-unverified`, all rights `not_reviewed`, and none with an evidenced
  `publication_date` in the register. The eight 2023 example statements are
  six `under_review` and two `draft`; six example relationships are
  `invalidated`. Four coverage examples are source-status examples, not the
  approved candidature denominator or topic-search completion. These are
  counts of repository records, not a claim that other parties lack programmes.
- Open PRs #200–#206 already address distinct source discovery, rights,
  coverage, locator, result-cross-check and relationship-review questions.
  This audit does not edit their files or infer that their drafts are approved.

## Current PR #101 collision

`git merge-tree --write-tree origin/main origin/audit-pr101` reports **six**
conflicted paths against the fetched PR head, not the nine in the older
handoff:

| Path group | Current conflict | Required reconciliation on PR #101's branch |
|---|---|---|
| `docs/pilot-review/2023/README.md`, `reuse-handoff.md` | Review/source-use histories diverge; the latter is now an add/add conflict. | Preserve dated evidence and the distinction between reported and actual review dates. Do not turn a proposed `link_only` use into a rights decision. |
| `openspec/changes/mvp-programme-comparison/tasks.md` | Task history diverges. | Preserve current tasks and PR #101's still-open E1.4 gates; do not check off P0 inventory or P1 publication from old CI. |
| `src/elecciones2026/generator.py` | Private pilot copy and publish-state paths diverge. | Preserve the four-source pilot context and fail-closed zero-published-claim state. Test empty and fictional approved states after resolving. |
| `tests/test_pilot_editorial_audit.py`, `tests/test_pilot_preview_acceptance.py` | Current-main test expectations conflict with PR #101's gate tests. | Keep both rights/editorial regression coverage and current preview acceptance; rerun them against the actual resolved head. |

The six PP/ERC statement files are **not** in today's conflict list. That
does not validate their review fingerprints, dates, source pages, rights or
political meaning. PR #101's own handoff still requires a private archive/page
recheck, actual review dates, source-specific human reuse decisions and
publication-date evidence or an explicit policy resolution. Source identity,
rights, statement approval and relationship approval remain separate gates.
Do not copy private PDFs, extracted text or reviewer evidence into Git to
resolve a conflict.

## Test and decision handoff

1. The PR #101 owner resolves these six paths **on that PR**, preserving the
   current four-party pilot and version-bound gates. Compare the resulting
   diff to main for unrelated source, statement and relationship changes.
2. Run focused source-register/editorial, pilot, static-build and browser
   checks plus full CI on the resolved head. Verify the generated 2023 publish
   set still has zero real statements/relationships until the separate human
   decisions are recorded. CI success would be engineering evidence only.
3. Owner/editorial reviewers independently decide the 2023 candidature rule,
   source authenticity/date, per-version use rights, exact candidate content
   and any comparison relation. P0 coverage and P1 topic-search counts cannot
   be asserted from this four-row pilot or a conflict-free merge.

The latest checked [main CI run](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
on `488b6f5` is red: test job failures include delivery/provisional assertions
and Docker readiness errors; rendered-mobile also fails an assertion. This is
pre-existing main-branch failure, not evidence that PR #101 caused it. Old
green PR checks cannot replace a fresh combined-tree run. This audit changes
no implementation or public artifact.

Reproduction: `git fetch origin --prune`; fetch `pull/101/head` to a local
audit ref; inspect PR #101 reviews/checks and current open PRs/issues;
`git merge-tree --write-tree origin/main origin/audit-pr101`; count
`es-gen-2023` rows in the current source register and example records. No
remote publisher page or private source was opened for this audit.

Local validation on this branch: `git diff --check` passed and
`PYTHONPATH=src python3 -m unittest tests.test_source_register
tests.test_editorial_gates -q` passed 29 tests. The local Python 3.11 runtime
cannot import `generator.py` because that module uses newer f-string syntax;
therefore the pilot editorial tests were not run locally. Neither the focused
tests nor structural checks verify the unresolved PR #101 merge, publisher
evidence, source rights or political content. Full CI on this branch is
pending and current-main CI is already red as noted above.
