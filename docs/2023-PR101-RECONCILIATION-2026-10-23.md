# PR #101 reconciliation handoff — 2026-10-23

Roadmap package: P0–P1 review-gate audit (`2023-corpus-completion`, existing
P0 owner/editorial and P1 review tasks). This is a **documentation-only**
handoff, not a conflict resolution, rights decision, editorial approval, or
release. It is separate from draft PR #124's official-candidature evidence.

## Reproducible baseline

- `origin/main`: `fe5e05e` (2026-10-22); PR #101 head: `f8506a1`, draft and
  GitHub `DIRTY` on 2026-10-23. `git merge-tree --write-tree origin/main
  origin/pr-101` reports **nine content conflicts**: six PP/ERC statement JSON
  records, `docs/pilot-review/2023/README.md`,
  `openspec/changes/mvp-programme-comparison/tasks.md`, and
  `src/elecciones2026/generator.py`. No merge was attempted in this branch.
- Current main's register has four `es-gen-2023` pilot sources (PP, ERC, PNV,
  Sumar); each is `published-unverified`, has rights `not_reviewed`, and has
  no evidenced publication date in the record. Eight 2023 statement examples
  are six `under_review` and two `draft`. These counts are not a candidature
  denominator, topic coverage, or publishable position count.
- PR #101's 2026-10-12 CI jobs passed, with release skipped. Its head predates
  the later four-party pilot copy and source-contract drafts on main. Current
  main CI run `39740313719` passed on `fe5e05e`; neither run tests a resolved
  PR #101 candidate or supplies human editorial review.

## Conflict decisions for the PR #101 owner

| Conflict group | Concrete divergence | Safe reconciliation criterion |
|---|---|---|
| Six PP/ERC JSON records | Main records `2026-10-12` as `review_date` for owner-reported decisions; PR #101 changes actual review dates to `null`, records `reported_date`, and binds fingerprints to exact candidate content. | Preserve the distinction between report date and actual review date. Check fingerprints against the unchanged six candidates and private evidence; do not manufacture dates or promote `under_review`. A content change requires renewed human review. |
| `generator.py` | Main's private 2023 home names four registered pilot sources and keeps an absent position neutral; PR #101's conditional copy reverts the visible scope to PP/ERC and adds publish-state wording. Main also adds a 2026 feedback navigation variable beside PR #101's footer edit. | Retain the current four-source pilot scope and navigation behavior while keeping publication-pending language accurate for zero approved claims. Test both empty and fictional approved states; no source count becomes an “all 2023” claim. |
| Review README and MVP tasks | PR #101 appends a source-specific rights/date handoff and task evidence; main has subsequent editorial and product-history entries. | Preserve both histories with explicit dates and outstanding gates. Do not mark P0 source rights, P1 claims/relationships, or release tasks complete from PR #101's CI. |

The branch also proposes quote-free `link_only` summaries with version-bound
rights evidence. Its own `reuse-handoff.md` says the PP/ERC source-specific
human decisions, actual review dates, private archive/page recheck and exact
PDF publication-date evidence (or an explicit policy resolution) are pending.
That proposed use must be decided by the rights owner; an official link and a
matching hash do not grant reuse permission. This audit does not adjudicate
the legal scope or change source, programme, statement, or relationship data.

## Reviewable exit check

The PR #101 owner should resolve the nine conflicts on **that PR's branch**,
then rerun current-main CI and the focused schema/editorial, default-build,
empty/approved-state browser and four-party-copy tests against the resolved
head. Check that zero real 2023 claims or relationships enter the publish set
until version-bound rights, exact-source and human review gates pass. Record
the human decisions separately; passing CI is not their substitute. The
approved 2023 candidature rule and complete document inventory remain P0
work under `2023-corpus-completion`, not part of this PR repair.

Evidence commands for this audit: `git merge-tree --write-tree origin/main
origin/pr-101`; inspection of `content/sources/register.json` and the eight
`content/examples/statements/*2023*` records on `fe5e05e`; GitHub PR #101,
PR #124 and CI metadata. No private PDFs or reviewer evidence were opened.

## 2026-10-26 integration-readiness recheck

Roadmap package: **E1.4**. This is a dated refresh of the conflict and release
gate evidence above, not a new rights decision, source inventory, review or
resolved PR candidate. The 2023-first product roadmap still puts P0 source
scope and rights before P1 proposal publication.

- `origin/main` is `8e2fab4`; draft PR #101 remains at `f8506a1`, with zero
  GitHub reviews and GitHub `CONFLICTING`/`DIRTY` merge state. A fresh
  `git merge-tree --write-tree origin/main origin/audit-pr101` reports the
  same **nine content-conflict paths** listed above. The merge was simulated;
  no files on PR #101 were changed. Its four successful CI jobs date from
  2026-10-12, before these main-branch changes, and its private-release job
  was skipped. Those checks do not test the combined tree.
- Current main still has four `es-gen-2023` source rows (PP, ERC, PNV, Sumar),
  all `published-unverified`, all with `rights_review.status=not_reviewed`,
  and all with `publication_date=null`. Its eight 2023 statement examples are
  six `under_review` and two `draft`; its six 2023 relationship examples are
  `invalidated`. These are repository record counts, not a complete
  candidature/document inventory, topic-search result, or publishable corpus.
- Open PRs #149, #150, #151 and #155 separately draft rights withdrawal,
  multi-document scope, relationship-collision and source-identity gates.
  They do not resolve PR #101's conflicts or grant editorial approval. Avoid
  carrying their proposed semantics into the PR #101 merge without a reviewed
  decision and a fresh test run.
- Latest checked main CI run
  [40179863768](https://github.com/c2ventures/elecciones2026/actions/runs/40179863768)
  on `8e2fab4` has an overall failure: the fork-PR/deploy-credential job
  failed before any steps. Its GitHub check-run annotation states that the
  job was not started because recent account payments failed or the spending
  limit needs to be increased; it directs the account owner to Billing &
  plans. The test, rendered-browser and Docker parity jobs passed; private
  release was skipped. Do not call main wholly green or attribute the
  account-level job block to PR #101.
- This audit's draft PR #156 triggered
  [run 40300408011](https://github.com/c2ventures/elecciones2026/actions/runs/40300408011).
  Its test and rendered-browser jobs likewise did not start; their check-run
  annotations report the same account payment/spending-limit block. Downstream
  jobs were skipped. Thus PR #156 has no CI test result, not a failing test.

**Next integration gate:** resolve PR #101 on its own branch, preserve the
four-source pilot scope and unknown review/publication dates, then rerun the
focused editorial/build/browser checks and full CI on the *resolved* head.
The GitHub account owner must resolve the Actions billing/spending-limit block
before relying on new hosted CI. Private source-page
recheck, version-bound rights and lawful summary-use decisions, actual human
review evidence, and an approved 2023 scope/coverage rule remain human gates.
No passing test, conflict-free merge or link-only label substitutes for them.
