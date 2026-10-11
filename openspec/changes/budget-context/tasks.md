# Tasks: Official budget context

Planning package: **E10.2 specification portion · Gate G10**. This file covers future E10.1–E10.5 delivery. Artifact completion is not implementation acceptance or human publication approval. E10.1 tasks 1.1–1.3 have technical evidence below; task 1.4 remains open. E10.2 technical development is authorised; publication remains blocked.

Read `proposal.md`, `design.md`, and the five capability specs. Preserve issue scopes: E10.4 is programme-detail audit; E10.5 is execution decision. The additional offline-distribution decision is independent. No task authorises merge, deployment, or publication.

## 1. E10.1 — Source and measurement contract (#48)

Dependencies: verify planning PR #47 is merged before implementation. Source audit has no UI dependency.

- [x] 1.1 Register the exact official 2023 SEPG chapters 1–8 CSV, corresponding HTML, and compatible section dictionary in the private source archive; verify URLs, dates, bytes, SHA-256, encoding, year, sector, chapters, consolidation, and units against the retrieved source.
- [x] 1.2 Deliver the measurement contract with official denominator, accounting basis, blank/zero conventions, decimal precision, and explicit tolerances; verify independent policy/section totals and document any HTML/CSV conflict and its resolution.
- [x] 1.3 Draft all eight topic coverage records against the pinned taxonomy, with source codes/locators, direct versus broad context, Spanish notes, and unmapped/overlapping policy inventory; verify no inferred fractions or additive eight-topic total.
- [ ] 1.4 Record rights/reuse and financial-data review of source, contract, and mappings plus human Spanish editorial review; verify real review evidence binds to the exact versions and keep pending/rejected records non-public.

## 2. E10.2 — Schemas, offline import, and bundle audit (#49)

Dependencies: specification review and E10.1 accepted. Use labelled synthetic fixtures for technical tests; no fixture becomes an approved source.

- [x] 2.1 Implement separate budget source, measurement, cell/margin, mapping, review, correction, manifest, and decision schemas with English keys; verify strict fields, decimal/null states, unique codes, taxonomy hashes, basis allowlists, and references using valid and invalid fixtures.
- [x] 2.2 Implement bounded offline parsing of the pinned source; verify encoding, decimal comma, malformed values, duplicate cells, unexpected headers, missing cells, source hash changes, resource limits, and network-disabled operation fail or succeed as specified.
- [x] 2.3 Implement independent cell/policy/section reconciliation, unit conversion, unrounded shares, and display rounding; verify inconsistent totals, wrong units, margin double counting, tiny positive values, overlapping rows, and invalid topic splits are rejected or labelled correctly.
- [x] 2.4 Produce normalized values, reviewed mapping/notes, audit reports, and canonical integrity manifest; verify exact source locators, taxonomy/transform versions, per-file bytes/hashes, deterministic identity without circular hashing, and exclusion of raw sources, secrets, and personal data.
- [x] 2.5 Document the runnable reproduction command and pinned environment; verify two runs with networking disabled produce identical manifests and output bytes from the same input/configuration/build date.
- [ ] 2.6 Implement correction invalidation and atomic build binding; verify source, measurement, taxonomy, or mapping changes invalidate dependent reviews, mixed versions fail, and a rejected bundle leaves the preceding artifact intact.
- [ ] 2.7 Verify security boundaries with hostile labels, source-directed URLs, oversized files, unsafe archive paths, and export formula strings; document import limits, inert rendering, private archive retention, and rights/size prerequisites for any repository data.

## 3. E10.3 — Spanish static context and mobile view (#50)

Dependencies: E10.2 accepted and E2.1 issue #6 or merged equivalent accepted. E10.4 and execution implementation are not required for the policy/section view.

- [ ] 3.1 Generate `/presupuestos/2023/` from one reviewed bundle with ranked policy bars, verified section details, and an equivalent table; verify figures reconcile and every amount/share resolves to source, version, and exact denominator.
- [x] 3.2 Add one shared topic-context region beside or immediately after comparative measures using selected-topic projections; verify all eight topics have context or explicit Spanish gaps and changing party selections cannot change official figures or emphasis.
- [ ] 3.3 Add reviewed Spanish year/status, scope, denominator, unit, rounding, historical, partial-mapping, and proposal-cost notes with accurate canonical/share metadata; verify central health/education amounts are not labelled total Spanish public spending and no party responsibility is implied.
- [ ] 3.4 Verify 360/390/430 CSS px, long labels, no horizontal overflow, 44-px controls, keyboard focus/disclosure state, semantic table headers, and screen-reader order; record human accessibility review and no-script/no-chart readability results.
- [ ] 3.5 Compare baseline and candidate home/topic/comparison network traces and mobile delivery; verify zero bulk bundle/archive requests, no prefetch/service worker, and bounded selected-topic context. Record bytes, request counts, and results against agreed performance targets.
- [ ] 3.6 Verify deterministic full static builds, escaped output, source-link resolution, and static Docker smoke checks; rehearse rollback of HTML plus matching bundle, including withdrawal of an unsafe version, and record financial/editorial/G10 sign-off before any later release operation.

- [x] 3.7 Add a plain-language overview of every official policy before expanded detail and explicit image sharing; verify unrounded proportional areas, complete policy labels, source-bearing SVG/PNG, private draft notices, native-share cancellation/fallback/error behavior, CSP compatibility, bounded assets, and no background chart/full-bundle downloads.

## 4. E10.4 — Programme source audit and claim boundaries (#51)

Dependencies: E10.1 accepted. Audit may run in parallel with E10.2 and the execution decision.

- [ ] 4.1 Inventory official programme-level 2023 tables and rights, then deliver year/sector/chapters/consolidation/unit compatibility and join-key evidence; verify exact policy/section/programme codes with reproducible unmatched/duplicate-row and total reports.
- [ ] 4.2 Record a human-reviewed programme-detail go/no-go; verify no-go preserves policy/section views and go specifies source-row traceability, correction propagation, and non-duplicated parent/child totals before any detail implementation.
- [ ] 4.3 Verify that party claims and cost estimates cannot enter official budget cells, mappings, shares, or denominators; use invalid input fixtures and UI review to confirm lawful approved political statements stay in a separate cited region and no affordability/performance inference is generated.

## 5. E10.5 — Separate execution decision (#52)

Dependencies: E10.1 accepted. Not required for the first 2023 approved-budget view.

- [ ] 5.1 Inventory official IGAE execution sources, dates, bodies, breakdowns, units, chapters, consolidation, and accounting basis; deliver a compatibility matrix against E10.1 with cited evidence for missing and incompatible dimensions.
- [ ] 5.2 Record a human-reviewed execution go/no-go; verify no-go gives explicit reasons and any go creates a separately scoped OpenSpec execution proposal with dates, denominators, methodology, and approval gates rather than adding execution figures here.
- [ ] 5.3 Verify first-bundle validation rejects extended/modified credits, recognised obligations, and payments, and that no planned/executed chart or progress ratio is generated; document accounting-basis separation with negative fixtures and view checks.

## 6. E10.2 / E10.5 extension — Offline-distribution evaluation

Dependencies: E10.2 bundle evidence and E10.3 performance baseline. This user-requested evaluation does not replace the E10.5 execution decision or commit to a public download feature.

- [ ] 6.1 Evaluate a separate candidate archive with reviewed HTML/data/styles, integrity manifest, source notes, year/version/review date, and correction/freshness notice; verify disconnected readability, local asset resolution, external-link limitations, safe paths, and absence of raw sources, personal answers, or tracking.
- [ ] 6.2 Measure compressed/uncompressed sizes, explicit-download bandwidth/cost, cache hit ratio, p95, errors, origin request rate, and memory under baseline, cold-cache, and burst workloads; verify no automatic download and no failure of agreed primary-site targets on the 2-vCPU/8-GB target. Record local/live limits separately.
- [ ] 6.3 Deliver an independent rights/security/accessibility/performance go/no-go decision with evidence; verify no-go leaves the online view deliverable and go requires review of distribution details and G10 approval before adding a public export link.

## Planning validation record

The record below covers artifacts only, not implementation, source acceptance, or release approval.

- Read AGENTS.md, both roadmaps, current budget drafts, taxonomy, source research, build boundaries, and open issues #48–#52 through authenticated GitHub reads.
- Confirmed the official SEPG index and chapters 1–8 HTML table as planning references. No real dataset was imported or marked approved.
- `npm exec --yes --package @fission-ai/openspec -- openspec validate budget-context --strict`: passed.
- `npm exec --yes --package @fission-ai/openspec -- openspec status --change budget-context`: 4/4 planning artifacts complete.
- `git diff --check`: passed. Diff review confirms only this change's planning artifacts are edited; five capabilities had matching specs and all 26 delivery tasks were unchecked at proposal completion.
- Application, importer, browser, load, and deployment tests are not run for this documentation-only package. Their required evidence remains in the unchecked tasks above.

## E10.1 application evidence — 2026-10-11

Branch: `docs/audit-pge-budget-source`. Tasks 1.1–1.3 delivered; task 1.4 remains open. E10.1 is **not accepted** until real human financial, rights, and Spanish editorial reviews are recorded. E10.2 technical implementation is recorded below; E10.3–E10.5 remain unimplemented.

- Verified issue #48 scope and planning PR #47 merged with `gh pr view 47 --json number,state,mergedAt,url` and `gh issue view 48 --json body,state,url`.
- Acquired five explicit official HTTPS sources with a 20-second timeout and 4-MiB limit into the operator-owned private archive outside Git. SHA-256, exact bytes, UTC retrieval/transport metadata, and encoding are recorded in `docs/budget-context/2023/source-register.json`. Raw objects and their acquisition records remain private at directory/file modes 0700/0600.
- Delivered [source audit and review checklist](../../../docs/budget-context/2023/README.md), draft measurement contract, complete section dictionary, exact reconciliation report, and eight draft topic mappings. No approval identities, raw source files, public charts, party claims, or inferred amounts are added.
- Offline check: `python3 tools/budget-audit/audit.py --archive "$HOME/Library/Application Support/elecciones2026/private-sources/budget-context" --register docs/budget-context/2023/source-register.json --check-records` passed. CSV/HTML matrices match; all 27 policies and 38 sections reconcile independently to the official denominator with zero discrepancy. Blank cells remain unavailable pending review.
- Two audits with Python socket creation disabled produced identical report bytes and matched `reconciliation.json`; all five source hashes, section labels, taxonomy hash, eight mapping locators, unmapped/repeated references, and private archive permissions passed verification.
- `python3 -m unittest discover -s tests -p test_budget_source_audit.py -v`: 11 synthetic tests passed; covers arithmetic, disagreement, malformed input, duplicate codes, year/units, altered bytes, symlinks, blanks/zero, and determinism. No real sources are downloaded in tests or CI.
- Scope limits: source blank semantics and publisher rounding convention are not established; rights applicability, review-owner assignment, and human financial/editorial approval remain pending. Publication date is explicitly unknown rather than inferred from HTTP metadata. No source is treated as current 2026 data.
- Application/UI, importer, Docker, browser, load, deployment, and human release checks are outside this bounded audit package. No commit, merge, deployment, or publication is performed.

## Workflow follow-up

- Obtain specification review before requesting a bounded implementation package; do not interpret CLI artifact completeness as approval.
- Each future package records exact commands/results, fixture versus real-source limits, and human review evidence here. Keep release evidence in CI and this task record.
- Archive only after the implemented scope and applicable review requirements are satisfied. No archive, merge, deployment, or publication occurs in this planning package.

## E10.2 technical implementation evidence — 2026-10-11

Roadmap package: **E10.2**, with the preceding E10.1 audit supplied for review. Branch: `feat/import-official-budget-data`. The user's “ok its fine. what now can you build it” authorises technical implementation; it is not recorded as financial, rights, editorial, or G10 publication approval. Task 1.4 remains open. This is a draft review package; no public budget data is enabled.

- Implemented strict budget schemas, bounded offline import, decimal reconciliation/conversion, exact source locators, taxonomy coverage checks, section dictionary, canonical manifests, private draft bundles, hash-bound reviews, correction invalidation, and an opt-in generator bundle gate. Reproduction and limits are documented in `docs/budget-context/2023/README.md`.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 336 tests ran successfully with 2 skips on Python 3.14.3; includes 29 budget/audit tests with synthetic matrices, networking disabled for deterministic reproduction, invalid source/measurement/mapping cases, hostile labels, tampering, unsafe paths, stale reviews, and rejected-build preservation.
- `PYTHONPATH=src python3 -m elecciones2026.schemas validate-all`: 63 checks passed. Fixed root schema metadata discovered by the full suite; referenced definitions retain strict field validation.
- `PYTHONPATH=src python3 -m elecciones2026.generator check-determinism`: two independent static builds were byte-for-byte identical.
- `npm exec --yes --package @fission-ai/openspec -- openspec validate budget-context --strict`: passed. `git diff --check`: passed.
- Ruff is unavailable locally (`No module named ruff`); the existing CI syntax/lint job must supply that check. Remote CI status is not asserted in this record.
- Tasks 2.6 and 2.7 remain open for complete acceptance: importer immutability and rejected-build preservation are tested, but whole-site atomic release/rollback and later rendering/export boundaries require further evidence. No renderer or CSV export exists here. Human review gates, E10.3 UI/mobile/performance checks, E10.4/E10.5 decisions, and offline-distribution evaluation remain pending. Raw acquired files and draft normalized bundles are outside Git. No merge, deployment, or publication is performed.

- Pinned real-source private import succeeded with the documented command, producing bundle `aecc6465af87086748c101fbac6e3e6b63438cf4822c732c45c442a5f0eaab24` outside Git. This remains draft data and has no publication approval.

## E10.3 technical implementation evidence — 2026-10-12

Roadmap package: **E10.3**. Branch: `feat/spanish-budget-context`, based on the E10.2 draft PR #60. The user's “continue” authorises local technical implementation; source acceptance and publication gates remain unchanged. Task 3.2 is implemented and tested; tasks 3.1 and 3.3–3.6 retain their full human/real-source acceptance requirements.

- Added the Spanish historical budget route, ranked policies, native section disclosures, equivalent policy and section tables, source locators, exact denominator, unrounded-value shares, tiny-positive labels, mapping limitations, and proposal-cost separation. Public builds require the existing reviewed-bundle gate. A separate private renderer accepts draft data outside Git with a permanent draft notice and no-index metadata.
- Added one shared context after comparative measures and on each topic page. All eight projections contain only referenced policy rows and notes, with explicit gaps where appropriate. Party changes reuse the same context; invalid selections hide it; failed requests preserve comparisons. Projection generation and streaming reads enforce 16 KiB. Labels are escaped for static HTML and use text nodes in fetched context. Topic projection URLs use a hash of all canonical projection bytes, so corrected notes cannot reuse an immutable cache URL.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 344 tests ran successfully with 3 skips, including 7 new renderer tests. The opt-in browser check is recorded separately below. No real approval records are created in fixtures.
- `PYTHONPATH=src ELECTIONS_TEST_BUDGET_BROWSER=1 python -m unittest discover -s tests -p test_budget_view_browser.py -v`, using Playwright 1.63.0/Chromium: passed. Verified 360/390/430 px, long labels, no horizontal overflow, 44-px summaries, keyboard disclosure, table semantics, no-script/no-chart readability, unchanged figures after party swaps, and failure-state isolation. CI now retains its JSON observations.
- Throttled synthetic observations: latency 150 ms, download 200,000 bytes/s, upload 93,750 bytes/s, fresh browser contexts. Budget-disabled/enabled home: 5/7 requests and 208,521/217,710 uncompressed response bytes. Topic: 4/5 requests and 47,550/52,032 bytes. Selected-topic comparison: 5/8 requests and 208,521/219,508 bytes. Only the selected topic's JSON was requested; no full bundle or archive request occurred. One local navigation per route is not p95/load evidence or an agreed performance acceptance threshold.
- Private pinned-source preview: all 27 policies and 38 section cells per policy rendered; no horizontal overflow at 360/390/430 px. This is draft data, not a reviewed public snapshot. The raw CSV and preview remain outside Git.
- Default and synthetic budget-enabled full builds are deterministic. Schema validation: 63 checks passed. Ruff `--select E9,F63,F7,F82`: passed. Existing Node share tests: 8 passed. OpenSpec strict validation and `git diff --check`: passed.
- Docker default build succeeded; private local preview returned HTTP 200 on loopback port 43829 with runtime UID 101, read-only root filesystem, dropped capabilities, and no-new-privileges. No external deployment or publication occurred.
- Acceptance limits: actual reviewed-bundle publication, Spanish editorial review, human accessibility review, agreed performance targets/live capacity, and atomic rollback/withdrawal plus G10 sign-off remain pending. E10.4/E10.5 and offline-distribution evaluation were not implemented. Do not archive the overall change.


## E10.3 shareable overview evidence — 2026-10-12

The user requested a simple graph before the expanded accounting view. Branch: `feat/share-budget-chart`, based on UI draft PR #63. Task 3.7 adds this authorised technical work; source, editorial, accessibility, and G10 acceptance remain open in their existing tasks.

- Added a deterministic squarified chart from all official policy margins and a complete readable policy key. Geometry uses unrounded values; Spanish proportions use euros per 100 euros of approved budget. The eight overlapping taxonomy topics are not added into a partition. Full section/table/measurement detail remains in a native disclosure.
- Added an explicit native PNG-sharing action, PNG download fallback/save action, and standalone SVG alternative. Exported images retain full policy labels, historical/approved status, scope exclusions, exact denominator, rounding, source URL/table/version, build/review state, and bundle identity. Private exported images retain a prominent draft notice. Source publication gates are unchanged.
- Added content-hashed SVG assets; rasterization runs only after a user action with no new Python dependency or remote image service. Enforced 128-KiB SVG and 1080-by-8192 image bounds. Rasterization uses the current CSP's data-image permission; CSP was not weakened.
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`: 349 tests ran successfully, 4 skipped. Four new chart tests cover proportional geometry, complete policy coverage independent of mapping, deterministic/source-bearing/inert SVG, zero-area behavior, hostile labels, and bounds. Budget-enabled fixture builds still produce identical complete file hashes.
- Opt-in Playwright suite: 2 tests passed. Checks include 360/390/430 px, native disclosures, semantic tables, no-script detail access, source-bearing PNG download, mocked native file sharing, unsupported-share PNG fallback, cancellation without download, fetch failure, and unchanged comparison-context behavior. Tests use synthetic figures and explicitly mocked publication gates. The test server now enforces the serving CSP; chart assets are not requested until an image action and are not requested during primary-site navigation.
- Private pinned-source Docker preview rendered all 27 policies. Actual PNG download succeeded under the unmodified Nginx CSP; expanded detail starts closed and the 390-px view has no horizontal overflow. SVG/PNG and screenshots remain outside Git. Runtime preview remains loopback-only, UID 101, read-only, and with dropped capabilities.
- Schemas: 63 checks passed. Ruff critical syntax checks, Node chart syntax, 8 existing Node share tests, strict OpenSpec validation, and `git diff --check` passed. CI retains browser observations and now checks the image-sharing script.
- Limits: browser PNG bytes depend on platform fonts/rasterization; deterministic identity applies to SVG and source values. Native sharing is mocked in automated tests and needs a real-device review. Financial/rights/Spanish editorial review, human accessibility, live performance acceptance, and G10 publication remain pending. No archive distribution, source acceptance, merge, deployment, or public release occurred.
