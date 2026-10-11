# Tasks: official budget context

These packages can be delegated independently where dependencies allow. A checked implementation task needs evidence in this file. No package may publish the chart without the financial-data review and release gate.

## E10.1 — Source and measurement contract

- [ ] Register the exact official SEPG 2023 approved-budget policy-by-section CSV and the corresponding HTML table. Record URL, retrieved bytes, SHA-256, date, unit, institutional scope, chapters, and classification codes.
- [ ] Document the total and rounding rule. Identify non-ministry sections and the limit of central PGE figures for health and education.
- [ ] Review source reuse and public display terms. Obtain financial-data review of the denominator, consolidation, and scope labels.

## E10.2 — Offline import and validation

- [ ] Parse the reviewed file without network access in the public build. Reject altered source hashes, malformed rows, negative or missing amounts where not allowed, and inconsistent totals.
- [ ] Produce a versioned normalized snapshot with policy-by-section amounts. Reconcile policy and section totals independently against the official consolidated total.
- [ ] Add tests for conversion from thousand to million euros, decimal and encoding handling, rounding, and deterministic output. Keep the original file out of the public runtime.

## E10.3 — Mobile static view

- [ ] Generate a Spanish `/presupuestos/2023/` page with year/status/scope/denominator/source labels, ranked policy bars, section details, and an equivalent table.
- [ ] Verify source links, amount and percentage calculations, no horizontal overflow at 360/390/430 CSS px, keyboard operation, and screen-reader reading order.
- [ ] Obtain editorial and financial-data sign-off; smoke-test the immutable static artifact. Do not release before the separate G10 gate.

## E10.4 — Programme or initiative detail

- [ ] Identify an official programme-level 2023 table with amounts, year, scope, unit, and classification codes. Verify whether it reconciles with the selected policy-by-section total.
- [ ] Document an auditable join and test double-counting and unmatched codes. Add programme detail only when the join and rights review pass; otherwise keep the first release at policy and section level.

## E10.5 — Later execution decision

- [ ] Compare SEPG budget coverage with IGAE monthly execution coverage and accounting basis. Define whether a valid comparison exists.
- [ ] Record a go/no-go decision and, only if approved, create a separate execution-data change. Do not add execution numbers to the first 2023 budget chart.
