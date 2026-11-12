# PR #101 validation boundary — 2026-11-12

Roadmap package: **E1.4 / P0–P1 integration evidence**. This note supplements
the [PR #101 disposition](https://github.com/c2ventures/elecciones2026/pull/219)
and [integration CI inventory](https://github.com/c2ventures/elecciones2026/pull/228)
with the exact current-main failure evidence. It is not a second implementation
of PR #101, a rights decision, an editorial review or release approval.

## Reproduced boundary

- Fetched `origin/main` is `488b6f5`. PR #101 is still open and draft at
  `f8506a1`, marked non-mergeable by GitHub, with no GitHub reviews. Its old
  passing checks do not exercise a candidate against current `main`.
- `git merge-tree --write-tree origin/main origin/pr-101` exits 1 and reports
  six conflicts: `docs/pilot-review/2023/README.md`,
  `docs/pilot-review/2023/reuse-handoff.md` (add/add),
  `openspec/changes/mvp-programme-comparison/tasks.md`,
  `src/elecciones2026/generator.py`,
  `tests/test_pilot_editorial_audit.py`, and
  `tests/test_pilot_preview_acceptance.py`. This is a simulated merge only.
  The earlier nine-conflict count in the merged October audit describes a
  different base; do not use it as the current integration count.
- The four `es-gen-2023` source rows on `main` remain PP, ERC, PNV and Sumar;
  each is `published-unverified`, has `rights_review.status=not_reviewed`, and
  has `publication_date=null`. This is a pilot register, not an approved 2023
  candidature/document denominator or a publishable corpus.

## Exact current-main CI limit

The [latest main run 41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
on `488b6f5` reached the test steps. Its pytest job reported **486 passed,
2 failed, 17 skipped and 9 errors**. The failed tests were the source-index
new-tab notice (`0` found, `4` expected) and the expired private-delegation
authorization test. All nine errors came from a Docker parity fixture whose
HTTP service did not become ready. Existing open repair PRs
[#204](https://github.com/c2ventures/elecciones2026/pull/204),
[#214](https://github.com/c2ventures/elecciones2026/pull/214), and
[#225](https://github.com/c2ventures/elecciones2026/pull/225) address those
respective failures; their isolated checks do not make current `main` green.

The rendered-mobile job separately passed its provisional 2023 phone-width
step but failed in `tests/quiz_browser.cjs:253`: the long-source-metadata
fixture found **3** links with the requested accessible name where the test
expected **2**. This is a mock-quiz browser assertion, not a source-rights or
2023 editorial result. It belongs to the quiz validation gate, not a reason
to weaken PR #101's rights/review checks. The downstream Docker image,
fork-isolation and private-release jobs were skipped after upstream failure.

## Exit evidence still required

Review the existing disposition before integrating or closing PR #101; do not
replay its stale divergent files merely to clear conflicts. Review the
non-overlapping CI repairs in their own PRs, then run full CI on the exact
combined SHA. Independently, the owner/editorial team must decide the 2023
inclusion denominator, source-specific rights and exact-version evidence,
actual human statement and relationship reviews, and any release. CI cannot
grant any of those decisions. No PDF, political answer, source record,
approval, routing or public artifact was changed for this audit.

Evidence: GitHub PR/review and run/job metadata; downloaded job logs for run
`41343879201`; the local `git merge-tree` simulation; and a read-only parse of
`content/sources/register.json`. The job logs were inspected for failure
signatures only; no private source bytes or reviewer store was opened.
