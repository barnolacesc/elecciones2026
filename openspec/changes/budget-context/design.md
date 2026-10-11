# Design

## Context

The site is a static, mobile-first comparator. The new budget view is separate public-finance context. The first source is an official SEPG CSV for the approved 2023 PGE. The 2026 extended budget and IGAE execution have different status or coverage and need separate review. See `docs/BUDGET-SOURCE-RESEARCH.md`.

## Goals / Non-Goals

**Goals:** official traceability; one audited denominator; reproducible offline import; policy and section breakdown; readable amounts and shares on a phone; no public API.

**Non-Goals:** automatic inference of government priorities or party responsibility; live execution data in the first release; a full public-spending account for Spain; programme-level estimates without an official programme table.

## Decisions

1. Use the SEPG 2023 approved-budget policy-by-section CSV, chapters 1–8 consolidated, as the first dataset. Its header states the year, sector, unit, and table basis. Keep the raw file and its checksum in a private source archive until redistribution rights are reviewed. Store a reviewed normalized snapshot for the static build.
2. Parse and validate offline. Keep policy and section codes and official labels. Convert thousand euros to million euros. Use decimal arithmetic and derive percentages from unrounded amounts. Reconcile both policy and section views to the same official consolidated total. Never sum policy totals and section totals together.
3. Publish a static `/presupuestos/2023/` page. Show a short scope explanation, total, ranked policy bars, an expandable section breakdown, and a table. Every row links to its official source and identifies the dataset version. Use CSS bars first; a treemap is optional after accessibility review.
4. Label administrative sections as sections. A ministry label is allowed only when it matches the official section. Programme or initiative detail requires a separate official programme-level table and an audited join; leave it out of the first release if the join is not validated.
5. Keep the 2026 extended budget and IGAE execution as separate later datasets. Each needs a scope, denominator, date, and reconciliation review. A source availability check is not approval to reuse 2023 values as 2026 values.

## Risks / Trade-offs

- [2023 data look current] → year and approved status appear in the heading, chart, table, share text, metadata, and URL.
- [Small central health or education values mislead] → explain the institutional scope and autonomous-community spending limit near the chart.
- [Cross-tab cells are double counted] → calculate one axis at a time and compare both to the official total.
- [CSV changes or encoding fails] → record checksum, detect format changes, and fail the build closed.
- [Treemap hides small policies] → keep the sorted list and table authoritative.

## Verification

Check source provenance and rights; parser fixtures for decimal comma, encoding, totals and missing cells; two-run deterministic build; policy/section reconciliation; 360/390/430-px layout; keyboard and screen-reader review; visible scope and source labels; static-container smoke check. A financial-data reviewer must approve the public snapshot.
