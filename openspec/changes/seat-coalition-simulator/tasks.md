# Tasks: Seat and coalition simulator

Planning package: **E5.1**, issue #75. Implementation packages: **E5.2–E5.3**. E5.4 sharing is deferred. Release gate: **G6**.

These are reviewable tasks, not implementation permission. The owner authorized planning before the quiz's real corpus is ready. A new implementation request and human E5.1 decisions are required before coding. G4 remains a public release prerequisite; private fixture work before G4 needs explicit permission. No human rule, rights, copy, or release approval is recorded here.

## 1. E5.1 — Human rule and method decisions

- [ ] 1.1 Obtain human review of the chamber/rule sources and permitted paraphrases. Retain exact versions or hashes, URLs, Article 162.1/99.3/171.5 locators, dates, reviewer and evidence; verify 350 seats and the derived 176 absolute threshold and record any rule conflict.
- [ ] 1.2 Obtain acceptance or revision of proposal, both specs and design. Record exact revision and decisions on Congress-only scope, arbitrary manual labels, 30-group/60-character limits, input grammar, incomplete totals, neutral diagram ordering, memory-only state, unavailable/mock/reviewed modes, and deferred sharing.
- [ ] 1.3 Obtain Spanish editorial review of scenario/result/source-limit drafts and comprehension criteria. Verify the reviewer distinguishes manual seat sums from actual votes, official results, predicted pacts, and second-ballot investiture outcomes.
- [ ] 1.4 Create linked bounded implementation issues from the accepted E5.2/E5.3 tasks, with dependencies and shared-file ownership. Verify each issue cites the accepted revision, required checks, implementation authorization and G4/G6 limits.

## 2. E5.2 — Pure seat engine

- [ ] 2.1 Implement the pure validation/state contract and a short input guide. Verify generic fixtures cover 1–30 groups, unique IDs, normalized duplicate labels, Unicode/hostile labels, empty/invalid counts, 0/350 boundaries, total excess, and preservation of raw invalid text.
- [ ] 2.2 Implement assigned/remainder and selected-sum/deficit/surplus arithmetic. Verify 175/176/177 boundaries, zero selection, zero-seat groups, incomplete distributions, removal/reselection, duplicate/unknown IDs, and invariance under row permutations; include the numeric contract in the guide.

## 3. E5.3 — Spanish phone flow

- [ ] 3.1 Implement labelled input and selection controls with error and focus handling. Verify add/edit/remove/reset behavior, stale-result withdrawal, long-label literal rendering, keyboard operation, and 44-px targets at 320/360/390/430 CSS px; document the local fixture preview.
- [ ] 3.2 Implement the hemicycle and semantic table from one validated distribution. Verify exactly 350 assigned/unassigned markers for valid scenarios, table/diagram count parity, neutral stable ordering, and complete textual access without graphics or color.
- [ ] 3.3 Verify memory-only state and static fallback with assigned fictional entries. Check zero interaction requests, no browser/URL/history persistence or console payloads, no personalized share/export, cleared reload/exit/back-forward state, and external-source no-referrer/no-opener behavior; retain sanitized evidence only.

## 4. E5.3 integration — Profile and static artifact

- [ ] 4.1 Add the versioned rule authoring/profile contract and offline validation. Verify missing/conflicting/unreviewed/stale evidence blocks reviewed activation, private fixtures have no approval marks, and correcting a rule invalidates dependent public output; document the profile and withdrawal contract.
- [ ] 4.2 Add explicit unavailable/mock/reviewed build modes and `/simulador/` integration with local fingerprinted assets, Spanish static method/source text and accurate navigation/sitemap states. Verify opt-in nonindexable mock behavior, default withdrawal of old simulator assets, hostile profile text escaping, and preservation of comparison/budget/quiz routes.
- [ ] 4.3 Add relevant CI and least-privilege Docker parity checks without delivery permission. Verify two builds of fixed approved inputs are byte-identical and the static image serves the same route/assets without a runtime API or parser; retain hashes, commands, results and limits.

## 5. G6 — Human and release acceptance

- [ ] 5.1 Complete human Spanish comprehension and full-process accessibility review, including native zoom, text spacing, keyboard, VoiceOver/Safari and NVDA/Firefox. Verify failures are fixed and affected checks repeated; retain aggregate task outcomes without personal scenarios.
- [ ] 5.2 Verify origin/edge/monitoring privacy and approved mobile/performance targets on representative infrastructure. Coordinate any actual-host test separately; record the approved workload and 1-vCPU/1-GB target limits, and reject visitor-level political-state logging.
- [ ] 5.3 Rehearse functional and rule-defect recovery using valid profiles and an unavailable artifact. Verify stale assets are withdrawn, invalidated rules never return through rollback, and retained hashes/timing meet the approved recovery target.
- [ ] 5.4 Assemble rule, method, copy, correctness, privacy, accessibility, reproducibility, recovery, G4 and G6 evidence. Verify exact-artifact human release approval before merge of a public activation, deployment or publication.

## Planning verification — 2026-10-12

The existing proposal was completed with two capability specs, design and these bounded tasks. Official BOE source pages were consulted at the exact articles listed in the design. Read-only structural, local-link, arithmetic-boundary, strict OpenSpec and whitespace checks passed. These checks validate planning consistency only; no engine, UI, Docker artifact, human approval, live test, or deployment was produced. All tracked tasks remain open.

## Workflow follow-up

- Review this planning PR and retain actual human decisions before creating implementation-ready issues.
- Start application only after a new implementation request and the applicable prerequisite decisions.
- Archive after implementation, verification and project review are complete; synchronize main specs through the approved workflow.
