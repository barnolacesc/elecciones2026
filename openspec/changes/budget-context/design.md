# Design: Official budget context

## Context

See `proposal.md` for motivation. This is the E10.2 planning portion for G10, informed by issues #48–#52 and `docs/BUDGET-SOURCE-RESEARCH.md`. The existing `budget-context` drafts are extended in place. No application implementation or source approval is part of this change.

Observed project boundaries:

- `content/taxonomy.json` defines eight stable topic IDs, version 1.0.0, and Spanish labels.
- `content/schemas/` and `src/elecciones2026/schemas.py` define political programme, statement, relationship, review, and correction records. They do not define budget records.
- `src/elecciones2026/generator.py` validates content, renders static topic pages, and stages output atomically. Comparison interactions use `site/app.js`. No budget renderer or importer exists.
- `content/i18n/es.json` stores Spanish strings; existing tokens and E2.1 components provide the presentation baseline.
- Static Docker serving, origin rollback, and load tooling exist. Local load evidence does not establish live Cloudflare/Hetzner capacity. Architecture service targets remain subject to human approval.
- `openspec/specs/` has no main capability contracts yet. The pending MVP static-publication spec is a dependency. This change does not silently modify or archive it.

## Goals / Non-Goals

**Goals:** preserve exact official inputs; make mapping decisions auditable; keep figures separate from political content; produce small static views from a reproducible bundle; permit explicit gaps; evaluate offline distribution independently.

**Non-Goals:** a revenue/tax-cost model, estimates for unmapped topics, programme amounts inferred from ministries, execution ingestion in the first release, automatic publication, a new API, whole-site offline caching, or claims of ASD-STE100 compliance.

## Decisions

### 1. Pin the historical measurement contract

Use the [SEPG approved-budget index](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/N_23_E_R_6_2_R.htm), its [chapters 1–8 HTML table](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/doc/HTM/N_23_E_R_6_2_R_1_1.HTM), and the corresponding [CSV](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/doc/CSV/N_23_E_R_6_2_R_1_1.CSV). The table identifies 2023, consolidated chapters 1–8, and thousand euros. Its sector includes the State, autonomous agencies, other administrative public-law bodies with limiting budgets, and Social Security. Preserve that official scope in the reviewed contract. Record verified section names from a compatible official dictionary rather than assuming each section is a ministry.

E10.1 must verify actual retrieved bytes, dates, blank conventions, classification codes, source precision, rights, and denominator before accepting any production snapshot. No amount, checksum, or human approval is invented here. The 2026 extension and IGAE execution are excluded from the first source set. A live dashboard was considered; a pinned historical source is easier to reconcile, review, and reproduce.

Retain exact values as decimal strings in thousand euros, including explicit source zeros. Use decimal arithmetic. A million-euro display divides by 1,000 and rounds half-up to two decimals; shares use unrounded values and round half-up to two percentage decimals. Preserve tiny positive values with a Spanish less-than label if display rounding would suggest zero. Record that display choice in the Spanish review.

The measurement contract declares the unrounded official denominator and row/cell reconciliation tolerances in source units. Default tolerance is zero; any nonzero tolerance must follow documented source rounding precision and receive financial review. Do not use a generic percentage tolerance that could conceal missing rows. Percentage display tolerance is half the last displayed unit. Display rounding must never alter normalized values.

Distinguish cross-tab cells, policy margins, section margins, and grand total. Reconcile each axis independently; never add margins to cells or add policy and section totals together. Preserve source blank semantics. An undocumented blank is unavailable, not zero, and blocks aggregates requiring it. Conflicting HTML and CSV require a recorded resolution before a new version is accepted.

### 2. Use a reviewed relation to the taxonomy

The first mapping is a discovery and review contract, not an approved allocation of the budget across eight topics. Candidate policy codes below are visible in the linked official table. They must be checked against the pinned source and approved taxonomy by financial and editorial reviewers. No policy names are replaced with taxonomy names.

| Existing topic ID / Spanish label | Candidate official policy references | Coverage and display rule |
|---|---|---|
| `housing` / Vivienda | 26 | Direct policy context; no cost for rent controls, guarantees, or individual proposals is inferred. |
| `education` / Educación | 32 | Direct policy context; state-sector coverage is not all education expenditure in Spain. |
| `health-social-services` / Sanidad y servicios sociales | 31, 23 | Two separate official policy rows; any optional sum requires disjoint-row review and a scoped label. |
| `economy-work-tax` / Economía, trabajo y fiscalidad | 21, 24, 25, 28, 43, 93; related 42 | Selected policy context, not a complete economy or tax-cost total. Policy 42 is broad and shared with climate-energy. |
| `immigration` / Inmigración | Related 29 | Mixed inclusion/social-security/migration context only; no isolated immigration amount until official detail supports it. |
| `foreign-policy-eu` / Política exterior y Unión Europea | 14, 12 | Separate foreign-policy and defence context; do not claim a complete EU or NATO amount. |
| `climate-energy` / Clima y energía | Related 42, 45 | Mixed industry/energy and infrastructure/ecosystem rows; no isolated climate total and no estimated split. |
| `institutions-rights` / Instituciones y derechos | Related 11, 13, 91, 92 | Separate justice, security, and institutional context; no fabricated rights-spending total. |

The complete official policy list remains authoritative on the budget page. A coverage audit lists policies not referenced by any topic and all repeated references. Unmapped policies remain in the official denominator and full ranked list. Topic mappings are not an exhaustive partition and their amounts must not be summed across topics.

A mapping references official row IDs; an optional section/programme selector must be compatible with that dataset. `mapped` means exact relevant rows, not full topic expenditure. `partial` means broad or incomplete context. `not_available` has no separable reviewed row; `not_comparable` identifies incompatible basis or scope. Missing amount is null, never a synthetic zero. A broad row can appear under two topics but cannot become two allocated fractions. No many-to-many weighted redistribution is allowed. Stable codes and pinned hashes were selected over label matching because wording changes must not silently change joins.

### 3. Define separate English record contracts

Future JSON Schemas use the repository's Draft 2020-12 convention, required keys, strict additional-property checks, ISO dates, SHA-256 values, and referential validation. Store Spanish public strings separately from English technical identifiers. No schema files or production values are added during this proposal.

| Proposed record | Required fields and constraints |
|---|---|
| `BudgetSource` | `id`, `source_version`, `publisher`, `source_url`, `table_url`, `table_id`, `publication_date` or explicit unknown reason, `retrieved_at`, `byte_count`, `sha256`, `encoding`, `budget_year`, `source_unit`, `institutional_scope`, `chapters`, `consolidation`, `accounting_basis`, `rights_status`, `review_state`, `review_refs`; first version requires 2023 and approved credits. |
| `BudgetMeasurement` | `id`, `version`, `source_ref`, `denominator_id`, `denominator_amount_thousand_eur`, `scope_note_key`, `blank_convention`, `source_precision`, `reconciliation_tolerances`, `display_unit`, `display_precision`, `rounding_mode`, `review_refs`; each tolerance states source evidence and rationale. |
| `BudgetCell` | `id`, `source_ref`, `policy_code`, `section_code`, optional `programme_code`, `amount_thousand_eur`, `value_state`, `source_locator`, `accounting_basis`; unique composite key within a source version; exact decimal or null with a reason. Official margins use a separate row type. |
| `BudgetTopicMapping` | `id`, `mapping_version`, `taxonomy_version`, `taxonomy_sha256`, `topic_id`, `coverage_state`, `row_refs`, `aggregation_mode` (`none` or `exact_sum`), `rationale`, `scope_note_key`, `review_refs`; broad context uses `none`; sums require distinct disjoint leaves. |
| `BudgetReview` | `id`, `subject_id`, `subject_version`, `subject_sha256`, `role`, `human_reviewer_id`, `decision`, `reviewed_at`, `evidence_ref`; roles distinguish financial, rights, and editorial review; states are draft, approved, rejected, or invalidated. Real approvals are entered only by authorised humans. |
| `BudgetCorrection` | `id`, `date`, `reason`, `prior_bundle`, `replacement_bundle`, `affected_record_ids`, `invalidated_review_refs`, `review_refs`; correction trail survives new versions and withdrawals. |
| `BudgetManifest` | `schema_version`, `dataset_version`, `budget_year`, `accounting_basis`, `source_refs`, `measurement_ref`, `taxonomy_sha256`, `mapping_version`, `transform_version`, `build_date`, `files` (relative path, bytes, SHA-256), `review_refs`, `supersedes`, `correction_refs`; paths cannot escape the bundle. |
| `BudgetDecision` | `id`, `package_id`, `decision` (`go`, `no_go`, `pending`), `source_refs`, `compatibility_matrix`, `evidence_refs`, `review_refs`, `decided_at`; programme, execution, and offline-delivery decisions remain independent. |

Review files bind immutable hashes to human decisions. To avoid circular hashing, first hash source, measurement, mapping, notes, and normalized payload files; reviews reference those hashes. The manifest then lists payload and review-file hashes, excluding itself. The bundle ID is the SHA-256 of the canonical manifest bytes and is stored in the directory name and external release record, not inside the hashed manifest; external release approval references that ID. No live timestamps, machine paths, or agent-generated approval identities enter deterministic output.

Political programme records remain in their existing schemas and namespaces. They can be referenced for navigation, never to populate `BudgetCell`. Party claims or cost estimates, when already lawfully sourced and approved, remain political statements with their own citations and reviews. Official approved credits, extended credits, modified credits, recognised obligations, and payments have distinct basis identifiers. Only approved 2023 credits pass this bundle's allowlist.

### 4. Separate acquisition, import, publication, and optional export

```text
Official source acquisition → private pinned archive → isolated offline import
                                                        ↓
                     schema + reconciliation + coverage audit → human review
                                                        ↓
                          approved immutable bundle → atomic static build
                                                        ↓
                 Spanish budget HTML + small topic projections → static Docker
                                                        ↓
                              optional explicit offline export (decision gate)
```

Proposed future layout: `content/budgets/` for reviewed contracts, mappings, notes, and normalized snapshots when rights/size review permits; `content/schemas/budget-*.schema.json` for schemas; build output under `build/budget/<bundle-id>/`; public hashed assets under `/static/budget/<bundle-id>/`. Private raw files stay outside the repository and public image. These paths are design targets, not existing implementation.

Extend the existing Python validation and atomic generator rather than introducing a server. A separate budget module keeps accounting rules out of political statement schemas. Acquisition has an allowlisted source, time/byte limits, and no document-directed requests. Offline import has no network, bounded resources, strict encoding/numeric parsing, and inert text handling. Escape labels in HTML and protect CSV exports against formula interpretation without changing numeric values. Distribution archives require bounded file counts/sizes, safe relative paths, no executable content, and no raw source inclusion without rights approval.

E10.2 must implement and document one reproduction command. Proposed CLI contract, not runnable today:

```sh
PYTHONPATH=src python -m elecciones2026.budget import --source /private/pinned-pge-2023.csv --contract content/budgets/2023/measurement.json --mapping content/budgets/2023/topics.json --build-date 2026-10-11 --output-dir build/budget
```

Pin the source, transformation version, configuration, environment, and build date. Verify two runs without network access produce identical manifests and file bytes. Import errors produce diagnostics but do not replace a reviewed bundle. Changing the source, measurement, taxonomy, or mapping invalidates dependent reviews and requires a new version. Keep previous safe immutable artifacts for atomic rollback.

### 5. Render shared Spanish context with bounded payloads

Generate `/presupuestos/2023/` with ranked policy bars, policy-section details, an equivalent semantic table, and measurement notes. Prefer CSS bars and native disclosure controls using existing tokens. A JavaScript chart library adds weight without improving the baseline; a treemap remains an optional later supplement.

Each topic page receives only its small approved context projection. For the existing client comparison flow, carry only the selected topic's context through a scoped static projection or reuse the topic page. Keep one shared region adjacent to both parties' comparative measures, stacked on phones. Party selection never changes budget values. Source links, scope, and denominator stay near each figure. A policy-wide amount is not the estimated cost of the adjacent proposal. If no mapping exists, show the gap while preserving the comparison.

Proposed Spanish copy below is draft interface text, not approved public content:

| Purpose | Draft public text |
|---|---|
| Heading | “PGE 2023: presupuesto aprobado” |
| Comparison context | “Contexto presupuestario oficial” |
| Historical warning | “Datos históricos de 2023. No representan el presupuesto de 2026.” |
| Measure boundary | “Estas cifras no indican el coste de las propuestas de los partidos.” |
| Scope limit | “Este ámbito no incluye todo el gasto de las comunidades autónomas y las entidades locales.” |
| Partial mapping | “Política de gasto relacionada; no es una cifra exclusiva de este tema.” |
| Gap | “No hay una cifra oficial desglosada y revisada para este tema en la fuente seleccionada.” |
| Share | “Porcentaje del total consolidado indicado, capítulos 1 a 8.” |
| Classification | “Política de gasto”, “Sección presupuestaria”, “Millones de euros” |
| Offline freshness | “Copia sin conexión. Comprueba la versión y la fecha de revisión antes de citarla.” |

Verify 360/390/430-px layouts, no horizontal overflow, keyboard focus, disclosure state, 44-px touch targets, meaningful row/column headers, and screen-reader order. Figures and references stay available without chart styles or scripts. Metadata and share text retain the historical year and approved-credit status. No party colours, ranking, feasibility score, or performance claim appears.

### 6. Evaluate offline delivery independently of execution

Offline ingestion in E10.2 is required; offline public distribution is optional. Evaluate a separate explicit archive containing reviewed HTML, local styles, data, manifest, sources/method notes, and correction/version information. Test the candidate in disconnected mode; outbound official links identify their network requirement. Do not bundle personal answers, tracking, unreviewed claims, raw files, or secrets. An immutable copy cannot be recalled: display its year, version, review date, and where to check corrections. Publication rights must explicitly cover redistribution.

Do not add automatic prefetch, a whole-site service worker, or downloads to the core initial payload. If export is viable, delivery uses an explicit link and an immutable hashed artifact after its own review. A no-go leaves static online context intact. First-release scope requires the evaluation record, not production offline export.

Measure baseline versus candidate initial bytes/request counts on home, topic, and comparison routes. Require zero full-bundle/archive requests during normal navigation. Record scoped context bytes and mobile delivery, and verify the agreed site latency targets. Evaluate explicit-download workloads separately, including cold-cache and burst traffic, cache-hit ratio, origin request rate, p95, errors, memory, bandwidth, and projected cost. Use the repository load plan and 2-vCPU/8-GB target with the approved service/cost ceiling. The unresolved architecture-versus-load origin limits require owner resolution; use the stricter existing test limit meanwhile. Do not claim live capacity from local rehearsal.

E10.5 retains its issue #52 execution comparability decision. Attach offline-distribution evaluation as a separate user-requested decision after E10.2/E10.3 evidence, not a replacement for that accounting audit.

### 7. Keep later accounting detail conditional

E10.4 audits an official programme table with compatible year, sector, chapters, consolidation, units, and policy/section keys. Record a coverage matrix, unmatched/duplicate rows, reconciliation, and go/no-go. Do not invent programme amounts from policy margins. A go permits only reviewed, traceable detail after specification review; a no-go keeps policy/section output.

E10.5 inventories IGAE sources and compares reporting period, entities, classification, units, chapters, consolidation, and accounting basis with E10.1. Distinguish credits, obligations, and payments. Record incompatibilities and go/no-go. A go requires a separate execution change and human review. No execution numbers or budget/execution progress ratio enter the first chart. A ministry name, similar label, or shared year does not establish accounting compatibility.

## Risks / Trade-offs

- [Broad taxonomy mappings look exact] → Keep official labels, partial states, and no estimated topic splits.
- [Historical data look current] → Preserve 2023 and approved status in URLs, headings, metadata, shares, and exports.
- [Margins and repeated topic references are double counted] → Reconcile disjoint leaves by one axis and prohibit additive topic totals.
- [Rights or approvals are absent] → Draft records remain non-public; reject unapproved publish sets.
- [Hostile files or archive paths] → Isolated bounded ingestion, strict paths, escaped text, and download security review.
- [Offline copies retain corrected facts] → Version/date labels, correction trail, and explicit freshness limits.
- [Download bursts affect comparison delivery] → Separate explicit exports, measured cache/origin impact, and no-go if primary targets fail.

## Migration Plan

This planning change performs no migration or deployment. After specification review and E10.1 acceptance, implement E10.2 with fixtures and approved pinned inputs. E10.3 also requires E2.1 acceptance or its merged equivalent. Issues require planning PR #47 to be merged; verify that dependency before implementation. E10.4/E10.5 may audit in parallel after E10.1, but are not prerequisites for the first policy/section view.

Validate the approved bundle before adding routes, links, or sitemap entries. Build HTML and data in the existing staging directory. Compare candidate performance against the core baseline and verify a static-container smoke check. Record financial, rights, Spanish editorial, accessibility, and G10 release approval before publication. Deployment is outside these packages. For failure, restore the prior safe approved HTML and matching bundle through the existing immutable-artifact mechanism; test withdrawal as well as rollback.

## Open Questions

These are evidence gates with defined fallback behavior, not permission to invent values:

- Exact reviewed source bytes, reuse decision, section dictionary, blank conventions, precision, and denominator: E10.1 acceptance controls production publication.
- Final topic mappings and Spanish notes: retain explicit gaps until human review; do not change the taxonomy or allocate broad policy totals.
- Programme join feasibility: E10.4 go/no-go; no-go preserves the first view.
- Execution comparability: E10.5 go/no-go and a separate change for any go.
- Offline redistribution viability and measured size/cost: independent evaluation; no-go preserves online delivery.
