# 2023 source-validator integration queue — 2026-11-22

Roadmap package: **P0.2 / E1.1**, `2023-corpus-completion` dependency audit.
Baseline: `origin/main` `6d7cc5e`, checked 2026-11-22 11:30
Europe/Madrid. This is a repository and GitHub metadata audit, not a source,
rights, editorial or release decision.

## Why this queue needs reconciliation

The [current source register](../content/sources/register.json) has four
`es-gen-2023` pilot rows. All four are `published-unverified` with rights
`not_reviewed`; they do not define an approved 2023 candidature denominator.
The same register has 19 separate `es-gen-2026` source rows after the merged
2026 import. Those rows do not close the 2023 inventory or approve 2023 reuse.

Eight open validator PRs below each edit both
`src/elecciones2026/source_register.py` and
`tests/test_source_register.py`. Eight also edit the same MVP OpenSpec
`tasks.md`; #253 edits the register schema; #275 edits the provenance spec.
GitHub's mergeability result is a snapshot against current main, not a review
of a combined validator or a guarantee after another PR lands.

| PR | Scope in title | Current GitHub state | Head CI boundary |
|---|---|---|---|
| [#253](https://github.com/c2ventures/elecciones2026/pull/253) | register update date | conflicting | prior checks green |
| [#256](https://github.com/c2ventures/elecciones2026/pull/256) | supplied source hash | mergeable | prior checks green |
| [#258](https://github.com/c2ventures/elecciones2026/pull/258) | source URL shape | draft, conflicting | prior checks green |
| [#259](https://github.com/c2ventures/elecciones2026/pull/259) | malformed register entries | conflicting | prior checks green |
| [#260](https://github.com/c2ventures/elecciones2026/pull/260) | publication-date order | mergeable | Docker parity failed; later gate skipped |
| [#262](https://github.com/c2ventures/elecciones2026/pull/262) | attribution fields | conflicting | Docker parity failed; later gate skipped |
| [#271](https://github.com/c2ventures/elecciones2026/pull/271) | required register IDs | conflicting | Docker parity failed; later gate skipped |
| [#275](https://github.com/c2ventures/elecciones2026/pull/275) | replacement-chain integrity | draft, mergeable | prior checks green |

The exact cause of the three Docker failures was not investigated in this
package. A green historical check does not test a rebased or combined head.
The [latest main CI](https://github.com/c2ventures/elecciones2026/actions/runs/44930014014)
passed on `6d7cc5e`; it does not validate any of these open PRs.

[PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains a
draft, conflicting PP/ERC pilot editorial PR at `f8506a1`. It also edits
`source_register.py`, the register and statement schemas, the MVP task file,
and six 2023 pilot statements. Its October green checks predate current main.
The separate [post-import audit PR #276](https://github.com/c2ventures/elecciones2026/pull/276)
addresses its editorial integration drift. This queue does not resolve #101
or duplicate that audit.

## Reviewable integration handoff

1. Keep #101's political-content and rights decisions in its human editorial
   lane. Do not use a validator PR or CI result to approve its six statements.
2. Before accepting any validator PR, rebase it on then-current main and
   resolve the shared parser, tests and OpenSpec task history. Review the
   combined behavior, not just each PR's isolated green check. Re-run focused
   source-register tests and the current full CI, including Docker parity.
3. Preserve explicit pending and missing 2023 states. Check fictional cases
   for invalid IDs, hashes, URLs, dates, attribution and replacement chains
   without changing real 2023 source rights or source status. Recheck source
   isolation after each integration; the 2026 import cannot become a 2023
   coverage numerator or denominator.
4. After the owner approves the 2023 inclusion rule and manifest, reconcile
   the real document set under the reviewed P0 contract. Until then, display
   pilot scope only; do not calculate a completeness percentage or infer a
   party position from a missing row.

This audit makes no merge-order approval, source authenticity finding, rights
decision, editorial review mark, code change or public-release claim. PR
metadata can change; refresh it when the queue is acted on.

Reproduction: `git rev-parse --short origin/main`; inspect the two election
partitions in `content/sources/register.json`; query each linked PR's `files`,
`isDraft`, `mergeable`, `statusCheckRollup` and `headRefOid`; inspect the main
CI run linked above. No private PDF or political-answer data was opened.
