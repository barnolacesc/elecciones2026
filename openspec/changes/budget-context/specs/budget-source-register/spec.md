# Budget source register

## Purpose

Retain a verifiable chain from official budget sources and measurement decisions to every published amount and share.

## ADDED Requirements

### Requirement: Bounded first dataset
The first release SHALL use the official approved 2023 PGE consolidated expenditure table by spending policy and section, chapters 1–8. It SHALL identify the exact institutional sector, source unit, year, and approved status. It SHALL NOT present these values as 2026 allocations or as total public spending in Spain.

#### Scenario: Historical source
- **WHEN** a reader opens the budget page
- **THEN** its heading and measurement note identify PGE 2023, approved credits, the covered sector, chapters 1–8, and the official source.

### Requirement: Immutable source record
The register SHALL retain the publisher, source and table URLs, table ID, publication date or explicit unknown state, retrieval date, byte count, SHA-256, encoding, version, year, units, coverage, chapters, consolidation, accounting basis, rights, and review state. Raw files SHALL remain outside public output; public-repository retention requires rights and size review.

#### Scenario: Source changes
- **WHEN** a retrieved file has a different checksum
- **THEN** it becomes a new draft version and cannot silently replace reviewed values.

#### Scenario: Source unavailable or conflicting
- **WHEN** the live source disappears or its HTML and CSV disagree
- **THEN** the register records the gap or conflict, preserves the pinned version, and blocks a replacement until human review resolves it.

### Requirement: Reviewed measurement contract
Publication SHALL require a rights decision and human financial-data approval of the source, denominator, basis, scope, and rounding rules, plus human editorial approval of Spanish labels and mappings. Agents SHALL NOT create approval marks. Approval SHALL bind to exact source and derived-data versions; changes SHALL invalidate dependent approvals.

#### Scenario: Review pending
- **WHEN** a source, measurement contract, or mapping is draft, rejected, or invalidated
- **THEN** the public build rejects the affected budget publish set without a partial release.

### Requirement: Exact arithmetic and reconciliation
Validation SHALL preserve official codes and reconcile cells, policy totals, and section totals independently to the same official denominator. Shares SHALL use unrounded values. Thousand euros SHALL convert to million euros by division by 1,000. Margins SHALL NOT be added to leaf cells; tolerances SHALL be explicit and justified by source precision.

#### Scenario: Duplicate or inconsistent totals
- **WHEN** duplicate cell keys, incompatible units, or totals outside the declared tolerance occur
- **THEN** validation fails and identifies the source rows and failed reconciliation.

#### Scenario: Rounded shares
- **WHEN** independently rounded displayed shares do not sum to exactly 100 percent
- **THEN** the view explains rounding and does not adjust any value to force a total.

### Requirement: Missing values and source zero
Import SHALL preserve the distinction between explicit zero, blank, unavailable, and invalid cells. It SHALL NOT estimate, impute, or silently convert missing cells to zero. An official blank convention can be applied only when documented and reviewed; incomplete numeric coverage SHALL block affected totals and shares.

#### Scenario: Blank source cell
- **WHEN** a blank cell has no reviewed source convention
- **THEN** it remains unavailable, and an aggregate requiring it cannot be published.

### Requirement: Correct classification labels
Publication SHALL distinguish spending policies, administrative sections, ministries, and programmes. Section names SHALL match the official source or a separately reviewed section dictionary for the same year. No section SHALL be called a ministry without verification; policy totals SHALL NOT become programme amounts.

#### Scenario: Non-ministry section
- **WHEN** a row belongs to a non-ministry section
- **THEN** the view retains its verified official section name and classification.
