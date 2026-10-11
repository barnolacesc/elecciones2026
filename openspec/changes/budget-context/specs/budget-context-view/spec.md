# Budget context view

## Purpose

Explain official budget allocations with an accessible, mobile-first static page.

## ADDED Requirements

### Requirement: Amount and share
Each displayed policy or section SHALL show its amount in million euros and its share of one explicitly named denominator. The calculation SHALL use unrounded source values and SHALL disclose the display rounding rule.

#### Scenario: Percentage check
- **WHEN** a reviewer recalculates a displayed share from source values
- **THEN** it agrees within the declared display rounding tolerance.

### Requirement: Mobile and accessible view
At 360, 390, and 430 CSS px, the page SHALL show a ranked bar list with readable labels, amounts, percentages, and source links without horizontal scrolling. It SHALL include an equivalent table. A treemap MAY supplement this view but SHALL NOT be the sole representation.

#### Scenario: Chart unavailable
- **WHEN** chart styling or script execution is unavailable
- **THEN** the amount, percentage, label, and source remain readable in HTML.

### Requirement: Neutral context
The page SHALL use neutral colours and SHALL NOT imply that a budget amount measures a party's honesty, performance, or responsibility. It SHALL explain that central-government PGE figures do not capture all expenditure by autonomous communities and local administrations.

#### Scenario: Health and education rows
- **WHEN** a reader sees a small central PGE allocation for health or education
- **THEN** the page warns that this is not the total public spending in Spain on that function.

### Requirement: Budget and execution separation
Approved or extended budget credits and IGAE execution figures SHALL appear in separately labelled datasets and views. A 2023 approved amount SHALL NOT be compared directly with a 2026 executed amount as if their scopes and accounting bases matched.

#### Scenario: Execution source not reviewed
- **WHEN** only the 2023 budget dataset is reviewed
- **THEN** no execution number or progress ratio is shown.
