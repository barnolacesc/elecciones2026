# Budget source register

## Purpose

Retain a verifiable chain from official budget data to each published amount.

## ADDED Requirements

### Requirement: Bounded first dataset
The first budget release SHALL use the official approved 2023 PGE consolidated expenditure table by spending policy and section, chapters 1–8. It SHALL identify the budget year as 2023 and SHALL NOT label the amounts as current 2026 allocations.

#### Scenario: Reader opens the 2023 page
- **WHEN** the page loads
- **THEN** it states “PGE 2023”, approved-budget status, the covered public sector, chapters 1–8, and the official source link.

### Requirement: Immutable source record
The import SHALL retain the source URL, retrieval date, source checksum, source table identifier, source year, amount unit, coverage, accounting basis, and review status. It SHALL keep the original source outside the public runtime and SHALL NOT publish an unreviewed dataset.

#### Scenario: Source changes
- **WHEN** a newly retrieved file has a different checksum
- **THEN** the import SHALL create a new source version and require review instead of silently replacing published amounts.

### Requirement: Official classification and totals
The importer SHALL preserve official policy and section codes. It SHALL calculate policy totals and section totals from the official table without counting the same cross-tabulation cell twice. It SHALL compare computed totals with the official consolidated total using a declared rounding tolerance.

#### Scenario: Reconciliation fails
- **WHEN** the computed total differs from the official total beyond tolerance
- **THEN** the build SHALL fail and SHALL NOT publish a partial chart.

### Requirement: Correct scope labels
The published view SHALL distinguish spending policies, administrative sections, ministries, and programmes. It SHALL NOT call every section a ministry or infer a programme-level amount from a policy total.

#### Scenario: Non-ministry section
- **WHEN** a section is not a ministry
- **THEN** the view SHALL display its official section name and SHALL NOT relabel it as a ministry.
