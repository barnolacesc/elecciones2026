# PR #101 integration drift after the 2026 import — 2026-11-22

Roadmap package: **P0.2 / E1.4**, under the proposal-only
`2023-corpus-completion` change and the existing MVP editorial gate. This is a
repository-evidence handoff, not a merge resolution, a rights or editorial
decision, or a release approval. The [2026-11-20 baseline
draft](https://github.com/c2ventures/elecciones2026/pull/264) covers the earlier
source-isolation snapshot; this note narrows to subsequent PR #101 integration
drift. No political source bytes or positions were re-reviewed here.

## Reconciled snapshot

- Fetched `origin/main` is `6d7cc5ebce678210dc2f594b000d5ac43c13b4ff`.
  The 2023-first product roadmap from [PR #113](https://github.com/c2ventures/elecciones2026/pull/113)
  is merged. Main also includes the later [2026 corpus import](https://github.com/c2ventures/elecciones2026/pull/267).
- The checked-in source register has **four** `es-gen-2023` pilot rows (PP, ERC,
  PNV, Sumar), all `published-unverified`, with `not_reviewed` rights and null
  publication dates. It has **19** separately scoped `es-gen-2026` rows. The
  2023 examples remain eight statements (six `under_review`, two `draft`), six
  `invalidated` relationships and four `published-unverified` coverage rows.
  These are file counts, not an approved 2023 candidature denominator, a topic
  coverage result, or publication permission.
- Draft [PR #101](https://github.com/c2ventures/elecciones2026/pull/101)
  remains at `f8506a10b6784edf597e9e315f4c000dc0d341af`, with zero GitHub
  reviews and GitHub merge state `dirty`. Its five completed checks date from
  its old head; the private release check was skipped. Current-main Actions
  [run 44930546571](https://github.com/c2ventures/elecciones2026/actions/runs/44930546571)
  completed successfully on `6d7cc5e`; neither run tests a resolved PR #101
  integration candidate. CI is engineering evidence, not human review.

## PR #101 integration delta

`git merge-tree --write-tree origin/main origin/pr-101` reports **seven**
conflicted paths: `docs/pilot-review/2023/README.md`,
`docs/pilot-review/2023/reuse-handoff.md`,
`openspec/changes/mvp-programme-comparison/tasks.md`,
`src/elecciones2026/generator.py`, `src/elecciones2026/schemas.py`,
`tests/test_pilot_editorial_audit.py` and
`tests/test_pilot_preview_acceptance.py`. This is a simulated merge, not a
resolved branch or a test result.

Eight of PR #101's 21 changed paths are already byte-identical to current
main: its six PP/ERC 2023 statement examples,
`content/schemas/programme.schema.json`, and the MVP editorial-statements
spec. In particular, the six examples still have null actual review dates,
separate reported dates and `under_review` status. Copying those records again
would not establish the missing review evidence.

The other 13 paths differ; a wholesale PR-head copy is unsafe. For example,
main's `source_register.py` now validates `archived_url` and its
`methodology.py` validates taxonomy ID shape and supports controlled topic
extensions; the old PR #101 snapshots lack those later rules. Main's editorial
gate also passes the taxonomy into statement validation, unlike the older PR
snapshot. These differences do **not** prove the simulated merge would remove
every rule; they identify concrete regression checks for any conflict
resolution or cherry-pick. The `schemas.py` conflict is new relative to the
six-path 2026-11-20 snapshot, after the 2026 corpus model changed. Preserve
both the 2023 actual-date/fingerprint gate and the newer 2026 review contract;
neither election's records may inherit the other's approval rule.

## Reviewable disposition and limits

The PR #101 owner should decide whether to supersede its already-integrated
parts or resolve the seven conflicts on that branch. Before treating a
resolved head as merge-ready, compare it against current main and run schema,
source-register, editorial, pilot-preview, 2026 corpus and full CI checks on
the **resolved** head. Keep the four-source 2023 pilot wording and the newer
2026 production-record path intact. The source-rights owner and human editors
must separately decide exact-version source use, actual review evidence,
statement and relationship approvals; an agent cannot infer them from an
official link, hash, old check or clean merge. The P0 2023 inclusion and
document inventory remain open under `2023-corpus-completion`.

Verification for this documentation package: fetched Git objects and GitHub
PR/check metadata; parsed checked-in JSON by election ID; compared PR #101's
21 paths with main; simulated the merge; `PYTHONPATH=src python3 -m unittest
tests.test_schemas tests.test_source_register -q` passed 36 tests on Python
3.11. The generator-dependent pilot audit could not run locally: main uses
Python 3.14 f-string syntax rejected by Python 3.11. No private PDFs, review
store, publisher pages, production routing, or public artifact were inspected
or changed.
