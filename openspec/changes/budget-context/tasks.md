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
- [x] 2.6 Implement correction invalidation and atomic build binding; verify source, measurement, taxonomy, or mapping changes invalidate dependent reviews, mixed versions fail, and a rejected bundle leaves the preceding artifact intact.
- [x] 2.7 Verify security boundaries with hostile labels, source-directed URLs, oversized files, unsafe archive paths, and export formula strings; document import limits, inert rendering, private archive retention, and rights/size prerequisites for any repository data.

## 3. E10.3 — Spanish static context and mobile view (#50)

Dependencies: E10.2 accepted and E2.1 issue #6 or merged equivalent accepted. E10.4 and execution implementation are not required for the policy/section view.

- [ ] 3.1 Generate `/presupuestos/2023/` from one reviewed bundle with ranked policy bars, verified section details, and an equivalent table; verify figures reconcile and every amount/share resolves to source, version, and exact denominator.
- [x] 3.2 Add one shared topic-context region beside or immediately after comparative measures using selected-topic projections; verify all eight topics have context or explicit Spanish gaps and changing party selections cannot change official figures or emphasis.
- [ ] 3.3 Add reviewed Spanish year/status, scope, denominator, unit, rounding, historical, partial-mapping, and proposal-cost notes with accurate canonical/share metadata; verify central health/education amounts are not labelled total Spanish public spending and no party responsibility is implied.
- [ ] 3.4 Verify 360/390/430 CSS px, long labels, no horizontal overflow, 44-px controls, keyboard focus/disclosure state, semantic table headers, and screen-reader order; record human accessibility review and no-script/no-chart readability results.
- [ ] 3.5 Compare baseline and candidate home/topic/comparison network traces and mobile delivery; verify zero bulk bundle/archive requests, no prefetch/service worker, and bounded selected-topic context. Record bytes, request counts, and results against agreed performance targets.
- [ ] 3.6 Verify deterministic full static builds, escaped output, source-link resolution, and static Docker smoke checks; rehearse rollback of HTML plus matching bundle, including withdrawal of an unsafe version, and record financial/editorial/G10 sign-off before any later release operation.

- [x] 3.7 Add a plain-language overview of every official policy before expanded detail and explicit image sharing; verify unrounded proportional areas, complete policy labels, source-bearing SVG/PNG, private draft notices, native-share cancellation/fallback/error behavior, CSP compatibility, bounded assets, and no background chart/full-bundle downloads.
- [x] 3.8 Add stable policy colours and the user-requested health/education versus pensions comparison; verify contrast, shared colours, exact sum and named denominator, common bar scale, missing/zero-reference behavior, adjacent coverage/source notes, mobile/no-script access, and exported-image consistency.

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

## E10.3 layout correction evidence — 2026-10-12

Roadmap package: **E10.3**. Branch: `fix/budget-chart-layout`. The user reported truncated chart labels, a crowded key, and mobile readability concerns. This corrects the existing overview without changing financial data or review gates.

- The current loopback preview served `budget.css` with `max-age=31536000, immutable`. The screenshot is consistent with an older stylesheet lacking overview selectors; the user's actual browser cache was not inspected. Both renderers now link to content-hashed stylesheet paths, and builds copy matching asset bytes. A regression test confirms corrected CSS changes its URL and that generated HTML references an existing hashed asset.
- Limited the chart to 520 CSS pixels, added a side-by-side desktop key at 960 pixels, retained a single mobile column, and separated code/name/amount columns with wrapping, row spacing, and dividers. Chart and share-image labels use complete names when they fit, otherwise source policy codes; full names remain in keys and SVG titles. No shortened political labels or changed values are introduced.
- `PYTHONPATH=src /tmp/elecciones2026-budget-test-env/bin/python -m unittest discover -s tests -v`: 351 tests passed, 4 skipped. New regressions cover immutable stylesheet URLs and complete-name/code tile labels. Budget-enabled fixture build determinism continues to pass.
- `PYTHONPATH=src ELECTIONS_TEST_BUDGET_BROWSER=1 /tmp/elecciones2026-budget-test-env/bin/python -m unittest discover -s tests -p test_budget_view_browser.py -v`: both browser tests passed under the serving CSP, including computed key-grid styles, 360/390/430-pixel layouts, disclosures, comparison context, and image sharing/download/error behavior.
- Refreshed the private pinned-source Docker preview on loopback port 43829. Chromium screenshots at 360/390/430/1280 pixels were inspected; no horizontal overflow, all rendered SVG text bounding boxes stay inside their tiles, and the stylesheet loads with the intended key layout. Actual PNG download passed and the exported image was inspected. Private sources, images, and screenshots remain outside version control.
- Ruff critical checks and `git diff --check` passed. Native real-device sharing, Spanish editorial review, human accessibility acceptance, financial/rights approval, live performance targets, and G10 release remain pending. No merge or public release occurred.

## E10.3 actual amounts and total-scale evidence — 2026-10-12

Roadmap package: **E10.3**. Branch: `feat/budget-amount-chart`. The user requested percentages, actual amounts, chart priority, and a total-based scale where a 40-percent policy occupies 40 percent of the plot. This supersedes the earlier per-100 framing and tile-code fallback; publication acceptance remains pending.

- The overview and shared image now show percentages of the consolidated denominator and actual million-euro allocations, with M€ explained in Spanish. Removed visible policy codes and per-100 figures from the overview/export. Codes remain in expanded source/accounting detail. Every policy has a complete name and both figures in the visible key, including small or zero-area rows; positive values below precision remain explicit.
- Preserved unrounded squarified geometry for every official policy, independent of overlapping topic mappings. Added a regression asserting that a 40-percent policy occupies 40 percent of the total area at both page and export dimensions. No largest-policy normalisation, invented grouping, estimates, or changed source values are introduced.
- Prioritised the chart at up to 960 CSS pixels, with the complete key underneath and sharing controls directly below the graph. Tile labels omit content that cannot fit rather than introducing codes or fragments. Shared images retain the unchanged source, denominator, scope, approved-versus-executed distinction, review state, and private draft watermark. Content-hashed stylesheet delivery remains in use.
- Full unit suite: 352 tests passed, 4 skipped. Chart tests cover percentage and million-euro formatting, positive values below precision, proportional area, absence of codes/per-100 framing, complete coverage, deterministic bounded exports, and hostile labels. Budget-enabled build determinism passes.
- Opt-in Playwright suite: 2 tests passed under the existing CSP, covering mobile layouts, disclosure/keyboard/table behavior, comparison context, image saving/native-share fallback/cancellation/errors, and no background image requests. Native sharing remains mocked rather than real-device acceptance.
- Refreshed the private pinned-source Docker preview on loopback port 43829. Screenshots at 360/390/430/1280 pixels show no horizontal overflow or tile text extending outside its rectangle; actual PNG saving succeeds. The final graph and export retain the draft notice. Raw data, previews, screenshots, and downloaded images remain outside Git.
- Ruff critical checks, strict OpenSpec validation, and `git diff --check` pass. Financial/rights/Spanish editorial review, human accessibility and real-device sharing, live performance acceptance, and G10 publication approval remain pending. No merge or public release occurred.
- Follow-up cache check: private preview SVGs also now use a content-hashed path, preventing the one-year immutable image cache from downloading the previous per-100 chart. Public SVGs already used hashed paths. The preview regression verifies that HTML links to the generated hashed image; the complete 352-test suite and actual private-preview PNG download pass after this correction.

## E10.3 adaptive label evidence — 2026-10-12

Roadmap package: **E10.3**. Branch: `feat/adaptive-budget-labels`. The user requested larger type for pensions and progressively smaller type to fit more information in smaller rectangles.

- Added area-based type ceilings and bounded font fitting for both the page and exported image. Fit complete names, percentages, and actual allocations before falling back to fewer lines. Preserve full words, exact geometry, source values, titles, complete key, source-bearing exports, private draft notices, and existing cache/CSP behavior. Amount and unit can wrap onto separate lines.
- `PYTHONPATH=src /tmp/elecciones2026-budget-test-env/bin/python -m unittest discover -s tests -v`: 354 tests passed, 4 skipped. New regressions verify shrinking preserves complete names and figures, relative type sizes, minimum-size fallback, and unchanged rectangle coordinates. Existing 40-percent-area, deterministic build/export, hostile-label, byte/dimension, source-gate, and formatting tests pass.
- Opt-in Playwright suite: 2 tests passed under the serving CSP. Includes phone layout, keyboard/table/context behavior, PNG saving, mocked native sharing/fallback/cancellation/errors, and no automatic chart-image fetch.
- Refreshed the loopback-only private pinned-source Docker preview at port 43829. Browser checks at 360/390/430/1280 CSS pixels passed: no horizontal overflow and every rendered text bounding box fits its tile. Inspected mobile and desktop chart screenshots. Pensions retains the largest type; transfer, debt, general-services, and unemployment names now appear inside the plot. Actual PNG download passed. Private screenshots, image exports, and raw data remain outside Git.
- Ruff critical checks, strict OpenSpec validation, and `git diff --check` passed. Small tiles may still omit text within the minimum font bound; the complete key retains every name and figure. Real-device sharing, financial/rights/Spanish editorial review, human accessibility acceptance, performance targets, and G10 release remain pending. No merge or public release occurred.

## E10.3 policy colours and magnitude evidence — 2026-10-12

Roadmap package: **E10.3**. Branch: `feat/budget-colors-comparison`. The user requested differentiated tiles and a visual health/education versus pensions comparison. Task 3.8 records this technical scope; source, Spanish editorial, accessibility, and G10 acceptance remain pending.

- Added 27 distinct muted policy colours, stable by official policy code and independent of amounts, ordering, taxonomy mappings, and party selection. Area-chart tiles, complete key swatches, comparison bars, and shared SVG/PNG use the same colours. Unit checks verify all colours provide at least 4.5:1 contrast with white and preserve their identity when rows reorder. No party or evaluative colour meaning is introduced.
- Added four common-scale bars for pensions, health, education, and the explicit health-plus-education sum. Percentages name pensions as their denominator; the main plot retains its consolidated-total denominator and unrounded area geometry. The sum uses decimal precision 50; stacked segments preserve individual amounts. Missing rows or zero pension amounts omit the comparison, and larger sums scale without clipping. No estimated/imputed values or topic sums are introduced.
- The comparison includes the official source URL and CSV row/column locators plus adjacent Spanish coverage notes. These PGE allocations are not total Spanish health/education expenditure and exclude some regional/local spending. The source-bearing shared image includes the same comparison, colours, denominator explanation, coverage notes, and locators, with the existing private draft watermark and publication gate.
- Full unit suite: 358 tests passed, 5 skipped. Added colour/contrast/order, unrounded sum, named denominator, stacked bar lengths, missing/zero-reference, and larger-sum bounds checks. Existing geometry, deterministic builds/exports, hostile-input, source-gate, and image-bounds tests pass.
- Opt-in Playwright suite: 3 tests passed under the serving CSP. The new no-script fixture check covers 360/390/430 pixels, complete comparison text, colour key, no overflow, and actual rendered bar-length ratios. Existing primary-context, keyboard/table, PNG/native-share mock/fallback/cancellation/error, and no-background-image checks pass.
- Refreshed the private pinned-source loopback Docker preview at port 43829. Verified 360/390/430/1280 pixels without overflow or clipped tile text. Actual health/education sum is 12,404,056.11 thousand euros, 6.504921729... percent of pensions before rounding; labels show 6,50 percent. Measured combined/pension bar lengths agree with this ratio on phone and desktop. Inspected coloured chart, mobile comparison, and downloaded PNG. Private source data and image/screenshot artifacts remain outside Git.
- Ruff critical checks, strict OpenSpec validation, and `git diff --check` pass. Colours are supplemental; 27 distinct shades do not establish colour-vision or human accessibility acceptance. Financial/rights/Spanish editorial review, real-device sharing, performance targets, and G10 release remain pending. No merge or public release occurred.

## E10.2 correction and import security evidence — 2026-10-12

Roadmap package: **E10.2**, issue **#49**, tasks 2.6–2.7. Branch: `fix/issue-49-budget-acceptance`, based on merged #79. All new data and review objects are synthetic fixtures. Real source, rights, human review, and G10 gates are unchanged.

- Bundle loading now parses the exact byte snapshot verified against each file hash and length, once per file. Canonical payload JSON is required. A file replacement after the validated read cannot substitute unchecked data. Public bundle staging writes the validated in-memory snapshot through a temporary directory, bound to the page's expected manifest. The generator change is limited to that binding argument.
- Import and bundle validation enforce the same credential-free HTTPS URL rules, host/default-port requirements, and control-character/backslash rejection for source, companion, and section references. These are inert outbound references; ingestion makes no document-directed requests. Source acquisition retains its separate allowlist.
- New synthetic acceptance cases cover source/measurement/mapping/section changes, taxonomy changes even after hash rebinding, correction withdrawal, mixed source/measurement versions, stale manifest binding, staging failure preserving the preceding site, file-read/copy replacement races, byte limits, symlinks, absolute/traversal/nested archive paths, and hostile HTML/formula labels. Formula text is retained as text in JSON and escaped rendering; no CSV/spreadsheet exporter or archive extractor is enabled.
- `PYTHONPATH=src python3 -m unittest discover -s tests -q`: **419 tests passed, 5 skipped** on Python 3.14.3. The skipped checks require opt-in browser/live prerequisites. `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_budget*.py' -q`: **61 tests passed, 3 skipped**; includes 10 new import-security cases. `PYTHONPATH=src python3 -m elecciones2026.schemas validate-all`: **63 checks passed**. Ruff `--select E9,F63,F7,F82` on changed Python files and `git diff --check`: passed.
- Task **2.7 is complete** for the implemented JSON/HTML/SVG import and rendering surfaces. The README documents import bounds, inert text, private retention, and explicit rights/size prerequisites for repository data. CSV export and public archive distribution remain unavailable and need their own gates if introduced.
- Historical task **2.6 status (superseded by combined acceptance below)**: snapshot binding and validation/staging failure preservation are verified here. The existing generator still publishes with per-file copying; whole-artifact replacement and recovery from a late publication failure depend on the parallel #80 generator work and combined acceptance checks. Technical evidence does not establish release rollback, safe withdrawal, or G10 publication approval.
- No real-source acquisition, new human approvals, source-register changes, deployment, merge, public release, or existing Docker preview changes occurred. The OpenSpec CLI is absent; no project setup or package installation was performed. Existing planning artifacts were read directly.

- Historical task **2.6 acceptance limitation (superseded by direct-values binding below)**: normalized allocations in `values.json` are bound to the integrity manifest, but not directly to retained human review evidence. Existing review subjects cover source, measurement, mapping, and section records. Recomputed allocations that preserve reconciled totals can produce a new manifest while leaving those review subjects unchanged. Public acceptance requires direct review binding of normalized allocations and verification that changed values invalidate it. That schema change is outside this package; task 2.6 remains open.


## E10.2 direct normalized-values review binding — 2026-10-12

This supersedes the preceding derived-value limitation and its outside-package classification. On further review, direct normalized-value acceptance is within E10.2 correction scope. No schema migration is needed: the existing `Review.subject_id` contract supports the new `normalized-values` subject.

- Added canonical `values.json` SHA-256 and `source_version` review binding. Public validation requires financial, rights, and editorial approval for that subject; missing roles, stale hash/version, and withdrawn reviews block publication. No real approvals, source records, rights decisions, or political data were created or changed. Old bundles without values review can remain private drafts; public use now fails closed.
- Synthetic cases independently reconcile corrected allocations, recompute all manifest hashes and bundle identity, then verify that unchanged values review fails. Additional cases cover missing values approval, each missing role, changed values version, withdrawn approval, and fixture rejection even when all three synthetic roles exist.
- `PYTHONPATH=src python3 -m unittest discover -s tests -p test_budget_import_security.py -v`: **14 tests passed**. Full budget-focused checks and validation are recorded below after completion.
- Intermediate combined test status (superseded below): root had verified #80 whole-artifact publication/recovery before adding direct-values binding. The complete combined acceptance below now includes that binding. No source review or G10 public acceptance is implied.
- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_budget*.py' -q`: **65 tests passed, 3 skipped** (opt-in browser checks). `PYTHONPATH=src python3 -m elecciones2026.schemas validate-all`: **63 checks passed**. Critical Ruff on changed Python files and `git diff --check`: passed. The previous complete 419-test run covers the earlier snapshot changes; combined root verification must include this supplemental binding.


## E10.2 combined technical acceptance — 2026-10-12

Task **2.6 is technically complete** after independent root review of `c9f4d8936bf28cfb17966f01bbbcc4777aee87f0` and combined acceptance with #80/#84 and #81. **PR #84 must merge before or together with #83**: whole-artifact generation switching and recovery are supplied by that dependency. The individual #83 branch does not contain the whole-site publication implementation.

- Root reran full pytest with budget Playwright enabled on the integrated candidate: **426 passed, 10 optional Docker/private-PDF checks skipped, 214 subtests passed**. The integrated checks verify candidate generation, complete artifact switching, recovery, and withdrawal, including matching budget HTML and snapshot removal. Critical Ruff across `src`, `tests`, `ops`, and `tools`, plus `git diff --check`, passed.
- Direct normalized-values hash/version review binding, correction invalidation, mixed-version rejection, validated snapshot copying, and preservation/recovery of the preceding artifact now satisfy technical task 2.6 acceptance together. Task 2.7 remains complete for the implemented surfaces.
- Live release rollback/restore evidence, retained real financial/rights/editorial approvals, human release reviews, and G10 remain open. No real approvals, source downloads, merge, deployment, or public release were performed by this package. Historical limitations above are retained as superseded findings, not current gaps.
