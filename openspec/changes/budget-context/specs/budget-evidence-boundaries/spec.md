# Budget evidence boundaries

## Purpose

Prevent official allocations, observed execution, and political claims from being combined into misleading amounts or performance conclusions.

## ADDED Requirements

### Requirement: Accounting and claim separation
Records SHALL distinguish approved credits, extended credits, modified credits, recognised obligations, payments, and party claims or cost estimates. The first bundle SHALL accept only official approved 2023 credits. Claims and estimates SHALL NOT enter official records, sums, shares, charts, denominators, or mappings; existing political statements retain their own editorial gates.

#### Scenario: Claim supplied as official value
- **WHEN** a party cost estimate is supplied as a budget allocation
- **THEN** validation rejects it regardless of whether the claim has political-content approval.

#### Scenario: Execution supplied to first bundle
- **WHEN** an execution, modified-credit, or extended-budget record enters the first publish set
- **THEN** validation rejects the mixed basis instead of rendering a combined chart.

### Requirement: Programme-detail audit gate
Programme detail SHALL require a compatible official 2023 source, rights and financial/editorial review, preserved classification codes, an auditable join, and reconciliation to the selected policy/section basis. Unmatched, duplicate, or incompatible rows SHALL block affected detail. A no-go SHALL preserve the policy/section view without inferred initiative amounts.

#### Scenario: No reliable programme join
- **WHEN** source coverage or consolidation cannot reconcile programme rows to the approved contract
- **THEN** E10.4 records no-go with the incompatibilities and no programme amount or fabricated drill-down is displayed.

#### Scenario: Validated programme detail
- **WHEN** the source and join pass review
- **THEN** each displayed programme amount resolves to an official source row and is not added again to its parent policy total.

### Requirement: Separate execution decision
E10.5 SHALL record a go/no-go matrix comparing official IGAE coverage, periods, reporting entities, classification, units, chapters, consolidation, and accounting basis with the PGE contract. A go SHALL require a separate OpenSpec change and human review before execution publication. No execution amount or inferred progress ratio SHALL enter the first approved-budget view.

#### Scenario: Coverage differs
- **WHEN** execution covers a narrower administration or another accounting basis
- **THEN** that incompatibility is recorded and no direct budget-to-execution ratio is shown.

#### Scenario: Execution feasible
- **WHEN** a compatible later execution view is approved for planning
- **THEN** its separately scoped proposal defines dates, denominators, method, and review gates without changing the first bundle's approved-credit basis.
