# 2023 source PR integration queue — 2026-11-10

Package: P0.2 inventory reconciliation handoff. This is a private, documentation-only audit of integration dependencies. It is not a source, rights, editorial, OpenSpec or release approval.

## Observed baseline

- `origin/main` was `488b6f5cc1617e3538bf0b730dc2ea070ac858ad` at 2026-11-10 09:30 Europe/Madrid. PR #113 is merged; `docs/PRODUCT-ROADMAP-2023-2026.md` is on main. The 2026-11-01 top-level roadmap directs completion of the ten-force, eight-topic 2023 comparator before other feature work.
- `content/sources/register.json` on that commit has four `es-gen-2023` pilot rows: PP, ERC, PNV and Sumar. Each has `published-unverified` source status and `not_reviewed` rights status. These rows do not establish the full party/document denominator or rights for broader use.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is still draft and GitHub reports `CONFLICTING`. Its four successful checks are from 2026-10-12, not checks against today's main. [Issue #100](https://github.com/c2ventures/elecciones2026/issues/100) remains open. [PR #219](https://github.com/c2ventures/elecciones2026/pull/219) is a separate draft disposition audit; it does not close or approve PR #101.
- The latest main [CI run 41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201) failed. Its logs identify failures in `tests/test_delivery.py::...wrong_actor`, `tests/test_provisional_2023.py::...source_links`, and Docker readiness errors in parity tests; the rendered job also failed an assertion (`actual: 3`, `expected: 2`). These are engineering blockers independent of editorial review. Do not infer that a documentation PR caused them merely because its CI also fails.

## Open PR collision map

GitHub file lists and mergeability were checked on 2026-11-10. All PRs below target `main`; mergeability is a point-in-time GitHub calculation, not review approval.

| Integration lane | Open PRs | Shared-path consequence |
| --- | --- | --- |
| PR #101 disposition | [#207](https://github.com/c2ventures/elecciones2026/pull/207), [#219](https://github.com/c2ventures/elecciones2026/pull/219) | Both discuss PR #101. Resolve one current disposition after rechecking the actual PR #101 diff; neither substitutes for rights/editorial decisions. |
| Standalone source/discovery audits | [#202](https://github.com/c2ventures/elecciones2026/pull/202), [#210](https://github.com/c2ventures/elecciones2026/pull/210), [#215](https://github.com/c2ventures/elecciones2026/pull/215), [#220](https://github.com/c2ventures/elecciones2026/pull/220), [#221](https://github.com/c2ventures/elecciones2026/pull/221) | These add distinct documents without editing the OpenSpec task ledger. They can be reviewed for evidence and scope individually; their current CI failures remain unresolved. |
| Discovery audits sharing the task ledger | [#200](https://github.com/c2ventures/elecciones2026/pull/200), [#201](https://github.com/c2ventures/elecciones2026/pull/201), [#208](https://github.com/c2ventures/elecciones2026/pull/208), [#209](https://github.com/c2ventures/elecciones2026/pull/209), [#211](https://github.com/c2ventures/elecciones2026/pull/211), [#212](https://github.com/c2ventures/elecciones2026/pull/212), [#213](https://github.com/c2ventures/elecciones2026/pull/213), [#217](https://github.com/c2ventures/elecciones2026/pull/217), [#218](https://github.com/c2ventures/elecciones2026/pull/218) | Every listed PR edits `openspec/changes/2023-corpus-completion/tasks.md`. A mergeable label today does not mean later merges will preserve all task entries. Rebase and compare the cumulative ledger after each accepted PR. |
| Proposal-only requirement/design deltas | [#203](https://github.com/c2ventures/elecciones2026/pull/203), [#205](https://github.com/c2ventures/elecciones2026/pull/205), [#216](https://github.com/c2ventures/elecciones2026/pull/216), [#222](https://github.com/c2ventures/elecciones2026/pull/222), [#223](https://github.com/c2ventures/elecciones2026/pull/223) | These touch the same provenance or editorial spec/design files, with several also editing `tasks.md`. Reconcile requirements and scenario semantics as a single reviewed delta before implementation; do not select one solely by PR number or green checks. |

The map is a routing aid, not a verdict on the authenticity of any linked document. It intentionally leaves party-specific source findings in their original PRs, and does not copy PDF bytes, extracts or political claims into this audit.

## Review handoff

1. Triage the main CI failure separately from corpus reviews. Re-run the affected checks on an updated head before treating a PR's checks as current. Passing CI remains technical evidence only.
2. Resolve PR #101's supersession/conflict using the actual diff and the two existing disposition audits. Keep issue #100's source rights, exact-content review and publication decisions open until their human owners record evidence.
3. For each source/discovery audit, validate its claimed document identity, election/coalition scope, link/retrieval evidence and rights boundary. Merge only approved findings; do not create `es-gen-2023` source rows or a completeness denominator from this queue map.
4. Before any OpenSpec implementation package, rebase the accepted P0/P1 proposal deltas together, preserve all non-duplicate task entries and scenarios, and obtain the owner/editorial decisions enumerated in the proposal. Keep public build and 2026 routing unchanged.

No OpenSpec task checkbox or source record changes here: the shared ledger is being edited by several open PRs, and the underlying P0 decisions are still pending. This audit should be refreshed or retired after the queue changes materially.
