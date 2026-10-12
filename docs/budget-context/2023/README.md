# E10.1 — Historical 2023 PGE source and measurement audit

Status: **draft technical audit; human acceptance pending**. Gate G10. Issue [#48](https://github.com/c2ventures/elecciones2026/issues/48). Planning [PR #47](https://github.com/c2ventures/elecciones2026/pull/47) was confirmed merged at 2026-10-11T11:02:17Z.

This directory contains internal audit metadata, a draft measurement contract, and draft taxonomy references. It contains no raw source files or production snapshot. The static generator does not consume these records. No financial figure, mapping, rights decision, or Spanish note has human approval. Do not move these files into a publish set until E10.1 is accepted.

## Reviewable records

- `source-register.json`: five exact acquisition records, source identity, retrieval/transport metadata, scope, and unresolved rights/reviewer states.
- `section-dictionary.json`: all 38 matrix sections joined by official code to the same approved-2023 publication index. Section 60 is identified through the index's Social Security branch. The source labels identify 22 ministries and 16 other sections; never label every section a ministry.
- `measurement.json`: official denominator, historical/accounting scope, explicit-zero/missing-cell policy, zero reconciliation tolerance, proposed display rounding, and draft Spanish notes.
- `reconciliation.json`: exact offline CSV/HTML matrix comparison and independent policy/section reconciliation results.
- `topic-mapping.json`: eight draft taxonomy coverage records, exact CSV locators, all unmapped policies, and repeated references. No topic amount, weight, estimated split, or eight-topic aggregate is generated.

All metadata and public draft copy bind to source versions and hashes. Rights/financial/editorial review fields remain empty or pending. The review owner must be assigned by a human; this audit does not nominate or impersonate a reviewer.

## Official evidence and scope

The [SEPG approved-budget index](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/N_23_E_R_6_2_R.htm) links the chosen [CSV](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/doc/CSV/N_23_E_R_6_2_R_1_1.CSV) and [HTML table](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/doc/HTM/N_23_E_R_6_2_R_1_1.HTM). Section identities come from its [publication index](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/Indice.htm). Exact bytes, hashes, retrieval times, and URLs are in the register; the matrix CSV hash starts `c796efe9208f`, and its size is 4,729 bytes.

The source is approved 2023 expenditure credits, consolidated chapters 1–8, in thousand euros. It covers the State, autonomous agencies, other state administrative public-law entities with limiting budgets, and Social Security. It is not execution, the 2026 extended budget, all Spanish public expenditure, or a party's programme cost. Chapter 9 is excluded; chapter 8 is included. Do not relabel the total as non-financial expenditure.

The publisher release date has not been established. HTTP `Last-Modified` is acquisition evidence, not proof of the law's approval date or dataset release date. The register explicitly leaves `publication_date` unknown. Retrieval is dated 2026-10-11; that does not change the budget year.

## Reconciliation findings

The pinned CSV and HTML matrix match in every header, label, blank, and numeric cell after trimming source label whitespace. The HTML uses CSS table divs with span cells, not HTML `tr`/`td` rows; the audit checks that exact layout without running scripts or loading external entities.

| Observation | Result |
|---|---|
| Policy rows | 27 |
| Section columns | 38 |
| Explicit numeric cross-tab cells | 110 |
| Blank cross-tab cells | 916 |
| Explicit source zero cells | 0 |
| Official grand total, thousand euros | 485985812.22 |
| Sum of official policy margins, thousand euros | 485985812.22 |
| Sum of official section margins, thousand euros | 485985812.22 |
| Maximum present-cell/margin reconciliation difference | 0.00 thousand euros |
| CSV/HTML disagreement | None in the pinned matrices |

No blank becomes an inferred zero. The audit sums only present numeric cells and observes that they agree with every official margin. This observation does not establish the semantic value of each blank. The draft contract stores those cells as unavailable and blocks any cell-derived published aggregate that requires them until a financial reviewer accepts an official convention or the publication uses separately sourced, reviewed margins. E10.2 must not silently relax this rule.

The full official denominator retains policies not mapped to a topic: 22, 33, 41, 44, 46, 49, 94, and 95. Policy 42 appears as broad related context for both economy-work-tax and climate-energy. These are repeated references, not duplicated allocated money. Immigration refers only to broad policy 29; no isolated immigration amount is asserted. All eight mappings remain draft.

Amounts will convert from thousand euros to million euros by division by 1,000. Shares use unrounded values and the official denominator. Half-up rounding to two decimals is a proposed display rule, not an observed publisher rounding method. No nonzero reconciliation tolerance is necessary for this snapshot. A new source version must be audited again; it must not inherit these findings or approvals automatically.

## Reuse evidence and required human decisions

The publisher's [Spanish legal notice](https://www.sepg.pap.hacienda.gob.es/sitios/sepg/es-ES/Ayuda/Paginas/AvisoLegal.aspx), reproduction paragraph, permits total or partial reproduction with express attribution of origin. The exact notice is pinned privately and identified in the source register. This is evidence for the project rights reviewer, not an agent-issued rights approval or a declaration that every file is public domain.

The proposed attribution is stored in Spanish in `source-register.json`. Human rights review must confirm applicability to the exact budget table, derived public figures, section labels, repository retention, and any later offline redistribution. Raw-source redistribution remains unapproved.

Before E10.1 acceptance, record the following against hashes of the reviewed records:

1. Assign a financial-data review owner. Confirm institutional coverage, chapters, consolidation, denominator, missing-cell treatment, classification joins, and display rounding.
2. Record the project rights decision and attribution requirement. Keep raw-file retention/redistribution separate from permission to display derived figures.
3. Review Spanish labels, historical/scope notes, all eight mapping rationales, and broad-policy warnings. Resolve or retain gaps explicitly.
4. Bind actual reviewer identity, role, date, decision, evidence, and file hashes to the accepted versions. Do not fabricate approval entries.

E10.2 depends on accepted E10.1. E10.3 additionally needs accepted E10.2 and the E2.1 baseline. G10 publication remains a later gate. This package makes no live site changes and performs no deployment.

## Reproduce the audit offline

Raw objects live outside Git and serving directories under the operator-owned archive. The archive directory is mode `0700`; each source/acquisition record is mode `0600`. Each object has a SHA-256 directory and a source filename listed in the register. `acquisition.json` retains its first retrieval metadata. No absolute private path is committed.

With the five pinned objects present:

```sh
python3 tools/budget-audit/audit.py \
  --archive "$HOME/Library/Application Support/elecciones2026/private-sources/budget-context" \
  --register docs/budget-context/2023/source-register.json \
  --check-records
```

This command performs no network requests and checks every source's bytes/hash. It rechecks the matrix, denominator, section dictionary, taxonomy hash, mapping locators, unmapped policies, and repeated references. It emits an audit report, not a normalized production bundle or approval. Match the output to `reconciliation.json`. Run it with network access disabled for independent review.

To obtain a private copy on another reviewer machine, retrieve only the five explicit HTTPS URLs in the register with a 20-second timeout and 4-MiB byte limit, preserve original bytes and transport metadata, and compare the listed SHA-256/byte count before using the object. Do not follow document-supplied links automatically. A changed hash requires a new source version and review, not an update to pass the check. Source acquisition is distinct from this offline audit command.

Synthetic rejection tests need no archive or external network:

```sh
python3 -m unittest discover -s tests -p test_budget_source_audit.py -v
```

Tests cover exact decimal reconciliation, blank versus zero, CSV/HTML disagreement, invalid numbers, wrong year/units, duplicate policies/sections, policy/section/grand-total mismatches, altered pinned bytes, symlinks, and deterministic reports. Actual snapshot findings are technical observations pending human financial/editorial review. Public UI, importer, Docker, browser, and load checks belong to later packages.

## E10.2 offline importer

The importer can consume these draft contracts for private development. It cannot publish them. The generator accepts only a hash-verified bundle whose source, measurement, mapping, and section dictionary have financial, rights, and editorial reviews bound to their exact canonical hashes. Synthetic fixtures are always rejected by the public build gate.

Reproduce with Python 3.14.3, the pinned source archive, and the versioned contracts in this branch. No third-party runtime dependency or network request is required. Use the same explicit build date for repeated runs:

```sh
PYTHONPATH=src python3 -m elecciones2026.budget import \
  --source "$HOME/Library/Application Support/elecciones2026/private-sources/budget-context/c796efe9208fa9badc1894d0e0334024c75fbb5e00b8de4b30cb25145e695e7a/policy-section.csv" \
  --contract docs/budget-context/2023/measurement.json \
  --mapping docs/budget-context/2023/topic-mapping.json \
  --register docs/budget-context/2023/source-register.json \
  --output-dir "$HOME/Library/Application Support/elecciones2026/private-sources/budget-bundles" \
  --build-date 2026-10-11 --draft
```

The command prints the immutable bundle directory. Inspect it with `PYTHONPATH=src python3 -m elecciones2026.budget validate /private/bundle/<manifest-sha256> --draft`. Without `--draft`, missing human reviews fail validation. Reproduction tests disable socket creation and compare every output file across two independent directories.

Each bundle contains source, measurement, values, sections, mapping, reviews, corrections, decisions, and a canonical manifest. The directory name is the manifest SHA-256; the manifest lists payload hashes and sizes without hashing itself. Blank cells remain null. Policy and section margins reconcile independently, and shares use the official denominator before display rounding.

Input limits are 4 MiB per file, 16 MiB per bundle, 256 policy rows, 128 columns, and 4,096 cross-tab cells. Hashes, duplicate JSON keys, numeric syntax, source headers, taxonomy, locators, coverage, and version relationships are checked before output. Labels remain text in JSON and are escaped in the existing HTML and SVG renderers. Source URLs are outbound references only: import and bundle validation require credential-free HTTPS, a host, and the default HTTPS port. Control characters and backslashes are rejected. The importer makes no network requests and does not extract archives. Acquisition still requires its separate official-source allowlist. No CSV or spreadsheet export exists; formula prefixes remain inert text in JSON, HTML, and SVG. A later CSV export must prevent spreadsheet formula interpretation before it is enabled.

Use `--reviews`, `--corrections`, `--decisions`, and `--supersedes` only with actual review and correction records. Changed canonical subjects invalidate prior reviews; corrections can explicitly invalidate review IDs. No review identity is generated by the importer. Old immutable bundles are retained. Do not use a draft bundle as rollback output for a public release.

The optional generator `--budget-bundle /reviewed/bundle/<manifest-sha256>` validates before building, binds the copy to the same manifest used for pages, and stages a matching bundle under `static/budget/<manifest-sha256>/`. E10.3 adds the Spanish budget page, static topic context, and bounded selected-topic requests. Default builds without a bundle retain no budget request or route. Validation failure preserves existing output; whole-site atomic release and rollback remain deployment responsibilities and require G10 evidence. Raw sources stay in the operator-owned private archive, with retention governed by the source/rights review. Repository admission of normalized data still needs rights and size approval.

## E10.3 Spanish view and private review

The optional reviewed-bundle build now generates `/presupuestos/2023/`, ranked policy amounts, section disclosures, policy/section tables, historical measurement notes, and one shared topic context after comparison measures. Topic context cannot depend on party selection. A missing or failed context request leaves programme comparison usable and shows an explicit gap.

The public build continues to reject draft and synthetic bundles. For financial/editorial review of draft figures, use a new private directory outside the repository:

```sh
PYTHONPATH=src python3 -m elecciones2026.budget_view \
  /private/budget-bundles/<manifest-sha256> \
  --private-preview /private/budget-preview-2023
```

This writes a clearly marked, no-index private page and local styles. It is not a production build or publication approval. Existing output directories are rejected. No raw source or normalized budget JSON is copied into that preview.

Review Spanish copy in `src/elecciones2026/budget_view.py`, `site/budget-context.js`, the measurement contract, and every topic mapping. Confirm historical year, approved credits versus execution, scope exclusions, denominator/rounding, blank states, section names, broad topic coverage, and the proposal-cost boundary. No review identities or approved states have been added.

Budget styles and context script are conditional. Default site styles are unchanged. A selected-topic projection is limited to 16 KiB both during generation and during streamed browser reading. The full bundle is not requested, prefetched, or cached by a service worker. Shared context uses text nodes for fetched labels and cancels stale topic requests. Projection URLs use a hash of the canonical projections, including explanatory notes, so corrections change the immutable URL.

Automated UI reproduction uses synthetic data and explicitly mocks the publication gate only inside tests:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p test_budget_view.py -v
PYTHONPATH=src ELECTIONS_TEST_BUDGET_BROWSER=1 python3 -m unittest discover -s tests -p test_budget_view_browser.py -v
```

The browser command needs Playwright 1.63.0 and Chromium. It writes `build/budget-view-e10-3.json`, which CI retains. Human financial/rights/editorial/accessibility reviews, agreed performance targets, whole-artifact rollback/withdrawal, and G10 release acceptance remain open. Do not interpret synthetic browser checks or private previews as those approvals.


## E10.3 simple chart and explicit image sharing

The budget page now opens with a proportional area chart and euros-per-100 policy key. All official policy margins are included; the eight overlapping taxonomy topics are not used as an additive partition. The prior accounting view is under “Ver detalle completo y fuentes”. The key gives complete official labels in sentence case; abbreviated chart labels retain complete labels in SVG titles and in the key.

“Compartir gráfico” uses native PNG-file sharing where available and downloads PNG otherwise. “Guardar imagen (PNG)” explicitly downloads it. A standalone SVG alternative works without JavaScript. The image retains historical/approved status, source/table/version, scope exclusions, exact denominator, rounding, build/review state, and bundle identity. Private exported images include the draft notice in the image itself. Cancelling native sharing does not initiate a download.

The SVG is deterministic and has a content-hashed public URL. Rasterization happens only after a click, with the existing CSP, a 128-KiB SVG limit, and 1080-by-8192 maximum dimensions. No rasterization service or new Python dependency is added. PNG bytes can differ across browser/font implementations; the underlying SVG and numeric values remain pinned. This explicit image export does not implement the deferred offline data archive, and publication still requires the source and G10 review gates.


## E10.2 correction and security acceptance

Bundle loading parses each file once from the exact bytes checked against its manifest. Canonical JSON is required. Copying writes the validated in-memory snapshot into a temporary directory, then renames it into the site staging tree. It does not reread source files during copying. A manifest change after page validation stops the build. Source, measurement, mapping, section, or taxonomy changes require renewed applicable reviews; old reviews cannot approve corrected data. Previous bundles are immutable and remain available for audit.

Keep raw sources, acquisition records, and draft bundles in the operator-owned private archive outside Git and serving directories. Directory permissions are `0700`; source and private bundle files use `0600`. Do not set an arbitrary deletion date: the rights decision and editorial correction needs must define retention. Retain the source version, correction trail, and last safe release artifact until that decision is recorded. Withdrawal prevents publication; a retained unsafe artifact is audit evidence and must not be selected for rollback.

Repository admission requires an explicit reuse-rights decision, human financial/editorial review, a documented retention decision, and a measured size review. The importer permits at most 4 MiB per input or normalized file, 16 MiB of normalized payload, 256 source lines, 128 section columns, and 4,096 cells. These technical bounds do not grant repository or redistribution rights. Archive extraction and CSV export remain unavailable; adding them requires safe relative paths, file-count and decompressed-byte limits, no symlinks/executables, and formula-safe spreadsheet cells. JSON bundle paths are restricted to the fixed eight payload names plus `manifest.json`.

Synthetic checks: `PYTHONPATH=src python3 -m unittest discover -s tests -p test_budget_import_security.py -v`. They cover stale reviews, taxonomy rebinding, synthetic withdrawal, source-directed URLs without network use, formula/HTML labels, read/copy races, invalid source/measurement binding, byte limits, symlinks, and unsafe archive paths. Task 2.6 remains open until whole-site publication replaces the artifact together and restores the previous artifact after a late publication failure. These checks do not approve real budget records or G10.

Public acceptance also requires a direct binding between normalized allocations and retained human review evidence. The current manifest binds `values.json` bytes to bundle identity, but the review subjects cover source, measurement, mapping, and section records rather than normalized allocations. Recomputed allocations that preserve reconciled totals can receive a new manifest without changing those review subjects. Manifest integrity alone does not prove human approval of derived values. This remains an open task 2.6 acceptance requirement; do not approve a public budget release until that binding is implemented and verified.
