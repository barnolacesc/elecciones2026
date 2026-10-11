# Budget context view

## Purpose

Explain reviewed historical official allocations in Spanish through accessible static pages and shared context beside comparative measures.

## ADDED Requirements

### Requirement: Spanish historical measurement labels
The view SHALL show year, approved status, scope, chapters, consolidation, units, exact denominator, rounding, source/version, and review/update date. Public labels and explanatory notes SHALL use reviewed Spanish. It SHALL explain that this PGE sector does not include all autonomous-community and local-government expenditure.

#### Scenario: Health or education context
- **WHEN** a reader opens either topic
- **THEN** the scope note is adjacent to the figures and states that these allocations are not total Spanish public expenditure on that function.

### Requirement: Traceable amount and share
Each numeric policy or section row SHALL show million euros and share of the named consolidated denominator, with an official source locator and dataset version. Section shares SHALL use that same denominator; a share within a policy requires a separately named denominator and label. Chart and table SHALL use the same reviewed values.

#### Scenario: Row verification
- **WHEN** a reviewer recomputes a displayed share from the pinned unrounded values
- **THEN** it matches within the stated display precision and resolves to the cited official row or cells.

### Requirement: Accessible mobile breakdown
At 360, 390, and 430 CSS px, ranked policy bars, section details, and an equivalent table SHALL remain readable without horizontal scrolling or zoom. Controls SHALL support keyboard operation and 44 CSS px touch targets. Text SHALL convey amounts without colour or scripts. A supplementary treemap SHALL NOT replace the list or table.

#### Scenario: Styling or scripting unavailable
- **WHEN** CSS bars or JavaScript do not render
- **THEN** labels, figures, denominator, scope, and source links remain readable in semantic HTML.

#### Scenario: Keyboard reader
- **WHEN** a reader opens section details using the keyboard
- **THEN** the control has visible focus and an announced expanded state, and the table has row and column headers.

### Requirement: Shared context beside measures
A topic or two-party comparison SHALL show one shared budget-context region beside or immediately after its comparative measures. It SHALL show only reviewed topic mappings and distinguish broad policy context from the cost of a measure. Changing party selection SHALL NOT change the official figures, ordering, or emphasis for the same topic and dataset.

#### Scenario: Party selection changes
- **WHEN** a reader selects a different pair of parties for the same topic
- **THEN** the same budget context remains visible and is not duplicated as a party-specific allocation.

#### Scenario: Budget mapping absent
- **WHEN** the selected topic has no publishable mapping
- **THEN** a Spanish gap note appears, the comparison remains usable, and no zero or estimated budget appears.

### Requirement: Neutral public interpretation
The view SHALL use neutral colours and SHALL NOT score party performance, responsibility, honesty, or policy feasibility. It SHALL NOT imply that historical allocations finance a proposed measure. Any party claim already approved for the comparison SHALL remain in its separate source-linked political statement region.

#### Scenario: Proposed increase
- **WHEN** a party statement proposes more spending or contains a cost claim
- **THEN** the historical context stays separate and no funding gap, affordability ratio, or execution percentage is inferred.

### Requirement: Stable crawlable historical route
The feature SHALL expose `/presupuestos/2023/` as static Spanish HTML with a canonical URL, accurate year/status metadata, source links, and a topic navigation path. Shared titles SHALL retain 2023 and historical approved-budget status without visitor identifiers or tracking tokens.

#### Scenario: Crawler access
- **WHEN** a crawler requests the budget route without executing JavaScript
- **THEN** it receives reviewed figures, scope, source references, and historical metadata.
