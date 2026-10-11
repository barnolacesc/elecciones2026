# Official budget data: source review

Status: research draft. Checked: 2026-10-11. This note does not approve a public chart.

## Source candidates

1. The [Secretaría de Estado de Presupuestos y Gastos (SEPG) 2026 extension](https://www.sepg.pap.hacienda.gob.es/sitios/sepg/es-ES/Presupuestos/PGE/PGE2025Prorroga/Paginas/PGE2025Prorroga.aspx) provides the official extended budget for 2026. Its page states that the figures cover the administrative public sector with a limiting budget. It links the 2023 budget for other documentation. Do not treat a 2023 amount as an unchanged 2026 amount.
2. The [SEPG 2023 approved-budget summary](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/N_23_E_R_6_2_R.htm) provides HTML, XML, and CSV for consolidated expenditure by spending policy and section. The [chapters 1–8 CSV](https://www.sepg.pap.hacienda.gob.es/Presup/PGE2023Ley/MaestroDocumentos/PGE-ROM/doc/CSV/N_23_E_R_6_2_R_1_1.CSV) was reachable on 2026-10-11. It identifies the year, units (thousand euros), coverage, and consolidated basis in its header. Cesc selected this as the first *historical* dataset, not a 2026 snapshot. A policy-by-section table can support both policy totals and administrative-section totals. It does not by itself support every programme or initiative.
3. The [Intervención General de la Administración del Estado (IGAE) monthly execution extracts](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadPublica/CPE/EjecucionPresupuestaria/Paginas/imextractoejecucion.aspx) publish PDF reports and XLS tables. As checked on 2026-10-11, the index lists 2026 months through August. These describe budget execution for the General State Administration. They are not automatically comparable with SEPG's consolidated planned expenditure.
4. The [IGAE annual COFOG report](https://www.igae.pap.hacienda.gob.es/sitios/igae/es-ES/Contabilidad/ContabilidadNacional/Publicaciones/paginas/iacogof.aspx) classifies actual expenditure across public administrations by function. The checked page lists 2020–2024 data. Its institutional scope and accounting basis differ from the PGE chart.

## Measurement contract before publication

- Show the budget year, approval or extension state, source publication date, data cut-off, unit, coverage, and exact source table beside the graphic.
- Use one declared denominator for every percentage. For the 2023 reference graphic, this is consolidated expenditure, chapters 1–8, for the stated sector. Do not call it all public spending in Spain.
- Convert source amounts in thousand euros to millions of euros by dividing by 1,000. Calculate shares from unrounded amounts. Check that leaf values sum to the official total within a documented rounding tolerance.
- Keep planned credits, modified credits, recognised obligations, and payments in separate views. Do not mix SEPG budget amounts with IGAE execution amounts in one treemap or percentage denominator.
- Preserve the original source file, retrieval date, checksum, table identifier, transformation script, and a reviewed output snapshot. Check redistribution terms before storing source files in the public repository.
- Do not infer a party's responsibility or the result of a policy from a budget line. This feature is public-finance context, not a party score.

## Mobile-first presentation

Start with a ranked list of spending policies. Each row shows a proportional bar, amount in million euros, percentage of the stated total, and a source link. Let a reader expand a policy to see its programmes. A treemap can supplement the list at larger widths but must never be the only way to read the data. Provide an equivalent accessible table, text labels, and a visible calculation note. Use neutral colours that do not imply a political party.

## Open decisions

- Complete the 2023 source-rights and measurement review before publishing the selected first dataset. A 2026 extension view needs a separate table-level reconciliation.
- Identify an official programme-level table and an auditable join before adding initiative or programme drill-down. Do not infer programme amounts from policy-by-section totals.
- Decide whether execution merits a later, separately scoped view after checking coverage comparability and update cadence.
- Have a financial-data reviewer sign off on the denominator, consolidation and double-counting rules, and any public headline number.
