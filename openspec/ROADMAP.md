# Project delivery roadmap

## E1.4-2026 technical package (2026-11-11)

`E1.4-2026` — 2026 corpus intake and election-scoped publication, under
`election-corpus-refresh`. The owner now requests the current-election view.
Its specs, design and tasks define technical preparation and incremental
loading. Private extraction, complete point coverage, human editorial review
and release are separate tracked steps; no approval is implied.
The technical preparation was merged in PR #237; task 2.3 (source-use and
editorial decisions for publishable records) remains open. The merge does not
establish a reviewed 2023 corpus or authorize a public 2026 release.

## 2023-first OpenSpec alignment (2026-10-19)

The [current product priority](../docs/PRODUCT-ROADMAP-2023-2026.md) is a
complete, reviewed `es-gen-2023` comparator before a 2026 corpus. The table
below maps **every phase** to an OpenSpec change. It supersedes the delivery
order later in this file where they conflict; old G0–G10 gates and package
history remain as audit context, not claims of completion.

| Phase | OpenSpec change | Readiness / required next artifact |
|---|---|---|
| P0–P1: 2023 coverage, initiatives, comparisons | `2023-corpus-completion` plus existing `mvp-programme-comparison` | Draft proposal, specs, design and tasks exist; owner/editorial review and the approved inclusion, source-rights and comparison decisions remain open. Not implementation-ready. The existing technical pipeline does not establish complete editorial coverage. |
| P2: mobile comparator | `mvp-programme-comparison` | Existing implementation; audit and test actual phone flow against P2 acceptance. New bounded changes require updated tasks/specs. |
| P3: reviewed quiz | `programme-alignment-quiz` | Mock foundation exists; reviewed 2023 question set and G5 release decision remain pending. |
| P4: 2026 refresh and budget reuse | `election-corpus-refresh` plus existing `budget-context` | Draft refresh specs/design/tasks exist and technical preparation is merged; source-use and editorial task 2.3 remains open. This is not publication approval. Budget values require period/source reconciliation. |
| P5: multi-source polls | `multi-source-poll-observatory` superseding CIS-only scope of `cis-data-observatory` | New proposal only; define a comparable, rights-safe method before implementation. |
| P6: pactometer/hemicycle | `seat-coalition-simulator` | Existing private manual simulator foundation; reviewed rule/UX release gate remains. |

Draft artifacts do not make a proposal-only change implementation-ready. Each
scheduled development run
selects one bounded package, links its PR to the applicable change and tasks,
and records evidence. Editorial approval, merge and release are distinct gates;
automated runs cannot grant them. See the [daily development contract](../docs/PRODUCT-ROADMAP-2023-2026.md#daily-development-contract).

**Delivery status (2026-10-12):** Comparator, source-processing tools, private IONOS hosting, budget view implementation, and the mock quiz foundation are merged. Unsupported 2023 approvals are withdrawn pending real review. Public release, live capacity/recovery, and real quiz content remain open. Use [GitHub task index #78](https://github.com/c2ventures/elecciones2026/issues/78) for remaining work.

**Plan status:** planning draft. This file orders work across OpenSpec changes. It is not an OpenSpec change artifact. Each feature receives its own proposal, specs, design, and tasks before an agent implements it. Do not mark a future proposal as implementation-ready.

**Source of truth:** [root roadmap](../ROADMAP.md) defines product scope. This file defines delivery sequence and work packages. The [Stitch review](../docs/STITCH-REVIEW.md) is a visual reference, not a data source or codebase.

## Release order and gates

| Gate | Phase | Release evidence | Change |
|---|---|---|---|
| G0 | Project contract | Name and copyright holder, domain, candidate inclusion, source rights, editorial owner, correction contact, and release targets agreed | None |
| G1 | MVP specification | Reviewed OpenSpec proposal, specs, design, tasks, and mobile flow | `mvp-programme-comparison` |
| G2 | Two-programme pilot | Two lawful source documents; reviewed claims, source links, coverage states, and corrections | `mvp-programme-comparison` |
| G3 | MVP preview | Local Docker run; static build; mobile, accessibility, security, and editorial tests | `mvp-programme-comparison` |
| G4 | Public MVP | Cloudflare/IONOS, measured load, monitoring, rollback, source coverage, and launch approval | `mvp-programme-comparison` |
| G5 | Quiz | Reviewed question set, local scoring, bias/privacy checks, and user tests | `programme-alignment-quiz` |
| G6 | Seat simulator | Verified parliamentary rules, seat arithmetic, accessible chart/table, and scenario tests | `seat-coalition-simulator` |
| G7 | CIS observatory | Official studies, method comparison rules, accessible trends, and source audit | `cis-data-observatory` |
| G8 | Localization | Reviewed Catalan; English only if demand and review capacity exist | `reviewed-localization` |
| G9 (exploratory) | Prior commitment follow-through | Evidence feasibility, attribution rules, and publication go/no-go reviewed | `commitment-follow-through` |
| G10 (optional) | Official budget context | Official table, denominator and coverage audit, accessible mobile view, and publication review | `budget-context` |

Source feedback reporting is an optional post-MVP workstream. It has no fixed gate or release date. It must not delay G5 (quiz) or G6 (seat simulator).

G5 follows G4 because the quiz needs a reviewed programme corpus. G6 and G7 can be prepared in parallel after G4, but this plan places the user-facing quiz first. G8 is independent of G6/G7 after the Spanish site is stable.

## Epic E0 — Product and editorial contract

**Outcome:** an approved boundary for claims, parties, sources, and publication. **Gate:** G0.

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E0.1 | Define candidate inclusion, party naming, programme status, and topic taxonomy. | Versioned policy; test examples for official, partial, replaced, and missing programmes. | None |
| E0.2 | Define source rights, quotation limits, reviewer roles, and internal correction process. | Editorial policy signed off by project owners; no unsupported quote can pass review. | E0.1 |
| E0.3 | Define language, domain, privacy notice, release service levels, and cost ceiling. | Decision record with explicit p95/error/cache targets and owners. | None |
| E0.4 | Track official 2026 candidacies and programme publication. | Versioned source register with official URLs, status, retrieval date, hash, rights review, and replacement history. | None |

**Human gate:** Cesc and the project partner must approve these policy decisions. Agents can draft options and evidence but cannot decide political coverage or rights by themselves.

**Source check:** [2026-10-09 audit](../docs/SOURCE-AVAILABILITY-2026.md) found official discovery paths and older general-election programmes, but no verified complete 2026 general-election programme among the checked sources. Recheck before E1.4; do not pass old or regional programmes off as 2026 general-election sources.

**Work start:** technical packages that use fictional fixtures may start in a local branch after G1 review. Real programme claims, external publication, and release still need G0 and later gates. The present plan is a draft, not recorded human approval.

## Epic E1 — MVP data and trust pipeline

**Outcome:** source records can become reviewed public claims without invented or untraceable content. **Gates:** G1–G2. **OpenSpec:** `mvp-programme-comparison`.

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E1.1 | Implement schemas for programme, statement, relationship, coverage, and correction records. | Versioned examples and validator tests for required provenance and invalid records. | E0.1 |
| E1.2 | Implement isolated offline source import and hash checks. | PDF/URL size, type, time, network, and failure tests; no source code execution. | E1.1 |
| E1.3 | Implement editorial approval gates and correction invalidation. | Build rejects unreviewed/uncited claims and invalidated comparisons. | E1.1 |
| E1.4 | Prepare two real pilot programmes and reviewed positions. | Each published claim resolves to a lawful source, version, page/section, and reviewer. | E0.2, E1.1–E1.3 |

**Parallel work:** E1.2 and the first UI implementation can run after E1.1, but pilot publication waits for E1.4. Do not use Stitch's fictional quotations, dates, IDs, or review badges as source data.

**Rehearsal:** two official 2023 general-election programmes can support a separate, private, clearly labelled proof of concept after rights/editorial review. It does not satisfy G2 for the 2026 release. The data model must bind every source, statement, and generated page to an immutable election ID and reject cross-election comparisons. See the [source check](../docs/SOURCE-AVAILABILITY-2026.md).

## Epic E2 — Mobile MVP experience

**Outcome:** a reader can compare one topic and two parties on a phone and inspect each source. **Gate:** G3. **OpenSpec:** `mvp-programme-comparison`.

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E2.1 | Convert the approved Stitch flow to an accessible component plan and local design tokens. | Phone wireframes at 360/390/430 px, component states, no profile UI or fake verification claims. | E0.1 |
| E2.2 | Build Spanish home and one-topic/two-party selection. | Touch/keyboard flow, no account, 44-px targets, no horizontal overflow. | E2.1 |
| E2.3 | Build comparison grouped by measure, with a short summary and both party positions per measure. | Source link and qualifications visible; no tab switch required; missing data is explicit. | E1.1, E2.1 |
| E2.4 | Build concise sources/method/corrections page. | Inclusion rule, source coverage, update date, and correction policy are readable on mobile; no working report form is implied. | E0.1–E0.2, E2.1 |
| E2.5 | Run mobile usability and accessibility tests. | Measured task success, focus/reader checks, mobile network timing, and recorded design fixes. | E2.2–E2.4 |
| E2.6 | Add neutral share controls and stable home/topic/comparison URLs. | Native share or copy-link works on tested phones; opened comparison link restores valid choices; no personal or vote-answer data enters the URL. | E2.2–E2.4, E3.1 |

**Not in G3:** separate statement-detail page, tabs, full source matrix, accounts, PDF hosting, quiz, polls, and seat forecast. Add them only through a later change and evidence.

## Epic E3 — Static build, security, and public operation

**Outcome:** a reproducible public release that withstands a measured traffic target. **Gates:** G3–G4. **OpenSpec:** `mvp-programme-comparison`.

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E3.1 | Build deterministic Python 3.14 generation and crawlable Spanish HTML. | Same approved input gives same output; source-linked pages work without JavaScript; sitemap/canonical data are accurate. | E1.1, E2.1 |
| E3.1a | Build neutral Open Graph previews and canonical metadata for shareable pages. | Public link previews show the correct topic/site context and approved local image; no invented claim appears. | E3.1, E2.6 |
| E3.1b | Build Schema.org JSON-LD structured data, snippet controls, and AI/LLM discoverability. | Valid Schema.org graphs on all routes; standard robots snippet directives; RFC 9116 security/crawler headers in nginx; llms.txt and llms-full.txt conforming to spec; determinism verified. | E3.1, E3.1a |
| E3.2 | Build local/production Docker path and least-privilege CI. | Same static artifact in both; pinned/scanned base for release; no deploy secret in fork PR. | E3.1 |
| E3.3 | Configure the owner-selected IONOS origin, Cloudflare DNS/proxy/cache, TLS, monitoring, and rollback. | Proven origin protection where feasible; safe headers; tested rollback and restore. | E3.2, E0.3 |
| E3.4 | Define and run burst, cold-cache, and 10,000-concurrent-visitor scenarios. | Record p95, error rate, cache-hit ratio, origin load, bandwidth/cost; meet approved targets or change capacity. | E3.3, E0.3 |
| E3.5 | Complete editorial, security, accessibility, and controlled-language release reviews. | Signed release record; no claim of strict ASD-STE100 compliance without a qualified review. | E1–E3 |

**Security boundary:** Stitch HTML and scripts are reference material only. Do not deploy external Tailwind CDN, Google-hosted fonts/images, invented political data, or a generated form without independent review.

## Epic E4 — Programme alignment quiz

**Outcome:** a voluntary, transparent statement-alignment tool. **Gate:** G5. **OpenSpec:** `programme-alignment-quiz` (proposal draft only).

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E4.1 | Specify item selection, source coverage, balance, scoring, skip behavior, and uncertainty. | Reviewed specs/design/tasks plus bias audit protocol. | G4, E1.4 |
| E4.2 | Build reviewed question set and a local-only score engine. | Unit tests cover ties, missing parties, skipped answers, and weight changes. | E4.1 |
| E4.3 | Build phone quiz/result flow with source links and plain scoring explanation. | Users can inspect why a result changed; no vote recommendation. | E4.2 |
| E4.4 | Verify privacy and fairness. | No answer upload, account, persistent political profile, or analytics event; editorial bias review recorded. | E4.2–E4.3 |

Political-preference answers are sensitive. Keep them in browser memory by default and do not log them.

## Epic E5 — Seat and coalition simulator

**Outcome:** transparent arithmetic for user-entered seat scenarios. **Gate:** G6. **OpenSpec:** `seat-coalition-simulator` (proposal draft only).

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E5.1 | Verify chamber and majority rules; complete specs/design/tasks. | Rule citations, edge cases, and non-forecast wording approved. | G4 |
| E5.2 | Build manual seat input, total validation, and coalition sums. | Tests cover invalid totals, thresholds, ties, and multi-party sums. | E5.1 |
| E5.3 | Build accessible hemicycle and equivalent table. | Phone and screen-reader tests; result is labeled arithmetic, not political likelihood. | E5.2 |
| E5.4 | Add privacy-safe scenario sharing only if URL review passes. | No server profile; payload limits and malformed-link tests. | E5.2 |

Vote-to-seat prediction is a separate future change, not part of E5.

## Epic E6 — CIS observatory

**Outcome:** auditable, method-aware official study trends. **Gate:** G7. **OpenSpec:** `cis-data-observatory` (proposal draft only).

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E6.1 | Check official data access, rights, and comparable indicators; complete specs/design/tasks. | Source and method inventory with series-break rules. | G4 |
| E6.2 | Build offline import and versioned metadata records. | Source hash/version and field dates survive rebuild; invalid records fail. | E6.1 |
| E6.3 | Build chart, table, and method notes. | Accessible trend view; no poll/election or estimate/direct-response conflation. | E6.2 |

## Epic E7 — Reviewed localization

**Outcome:** Spanish stays authoritative while reviewed translations expand access. **Gate:** G8. **OpenSpec:** `reviewed-localization` (proposal draft only).

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E7.1 | Define string and claim translation workflow; complete specs/design/tasks. | Clear source language, reviewer, version, and correction rules. | G4 |
| E7.2 | Add reviewed Catalan interface and content. | Bilingual editorial and accessibility review; source wording stays identifiable. | E7.1 |
| E7.3 | Consider English only after demand and reviewer capacity are approved. | Explicit go/no-go decision; no implied release commitment. | E7.1 |

## Optional epic E8 — Source feedback reporting

**Outcome:** a reader can submit a short source or citation report without an account or email. **Gate:** separate privacy/security approval after G4. **OpenSpec:** `source-feedback-reporting` (proposal draft only). It does not block E4 or E5.

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|
| E8.1 | Decide if a write API and database are justified; complete specs/design/tasks and a retention/privacy decision. | Approved threat model covers spam, DoS, stored XSS, PII, SQL injection, reviewer access, and backup. | G4 |
| E8.2 | Build a small validated FastAPI endpoint and persistent report record. | Tests reject invalid IDs, excess text, unsafe input, and abusive rates; parameterized access prevents SQL injection. | E8.1 |
| E8.3 | Add a statement-linked mobile report flow and private review queue. | Submission returns a receipt, does not ask for email, and cannot change public content automatically. | E8.2 |
| E8.4 | Operate and audit the service. | Retention, monitoring, backup/restore, abuse review, and incident response have named owners. | E8.2–E8.3 |

## Exploratory epic E9 — Prior commitment follow-through

**Outcome:** decide whether a neutral, evidence-based view of earlier commitments is possible. **Gate:** G9. **OpenSpec:** `commitment-follow-through` (proposal draft only). This epic does not block the MVP, quiz, simulator, or CIS work.

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E9.1 | Define a commitment unit, election and observation periods, measurable outcomes, inclusion rules, and an explicit unknown state. | Pilot methodology and examples reviewed by independent editors. | G4 |
| E9.2 | Map each sampled commitment to official programme text, official acts or statistics where relevant, and counter-evidence; record source dates and coalition/competence context. | Evidence dossier distinguishes an act, an outcome, a partial result, and unavailable evidence. | E9.1 |
| E9.3 | Test inter-reviewer agreement, corrections, sampling bias, and denominator stability. Decide whether any aggregate is defensible. | Published go/no-go decision. If evidence is weak, reject percentages or the feature. | E9.2 |
| E9.4 | Only after approval, complete specs/design/tasks and prototype a mobile evidence view. | Every status has a source trail, a review date, uncertainty, and a correction path; no "lies" label. | E9.3, human approval |

## Optional epic E10 — Official budget context

**Outcome:** explain official spending-policy amounts and shares without attributing them to parties. **Gate:** G10. **OpenSpec:** `budget-context` (proposal draft only). This does not block the MVP or E4–E9. See [source research](../docs/BUDGET-SOURCE-RESEARCH.md).

| Package | Agent-ready assignment | Deliverable and acceptance | Depends on |
|---|---|---|---|
| E10.1 | Register the approved 2023 PGE table and define year, institutional scope, chapters, consolidation, units, denominator, rights, debt treatment, and review owner. | Reviewed source and measurement contract; explain the chapters 1–8 denominator and distinguish interest from principal. No 2023 value is presented as a verified 2026 value. | None |
| E10.2 | Complete specs/design/tasks and build a versioned, offline import with total and share checks. | Reproducible snapshot, source checksum, rounding rules, and failure tests. | E10.1 |
| E10.3 | Build a Spanish mobile ranked-bar view with policy and section details and an equivalent accessible table. | 360/390/430-px checks; amounts and shares link to the source and show the exact denominator. | E10.2, E2.1 |
| E10.4 | Check official programme-level tables and an auditable join for initiative detail. | Publish only validated programme amounts; otherwise keep section and policy views without invented drill-down. | E10.1 |
| E10.5 | Decide whether to add a separate execution view using IGAE data. | Go/no-go based on compatible coverage, dates, and accounting basis; no mixed budget/execution chart. | E10.1 |

## Delegation contract for each package

Give one agent one bounded package and its dependencies. The assignment must state file scope, required test evidence, editorial source limits, and whether it may change deployment. Ask the agent to return changed files, commands/results, risks, and unresolved decisions. A second review lane checks political claims, security, and UX as appropriate. No agent can publish political claims, change source rights, deploy, or merge without the relevant human release gate.

Keep package status in the matching OpenSpec `tasks.md`. Keep milestone status in this roadmap. Do not mark an epic complete because one package is complete.
