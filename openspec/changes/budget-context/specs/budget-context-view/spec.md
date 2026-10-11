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


### Requirement: Plain-language shareable overview
The page SHALL prioritise an area chart of all official policies, scaled by unrounded shares of the consolidated total. Overview figures SHALL show percentage and actual amount in million euros, without source codes or euros-per-100 framing. A readable key SHALL show all names and both figures. It SHALL NOT partition overlapping topics. Full source notes and tables SHALL remain available in a native disclosure.

#### Scenario: Understand the distribution
- **WHEN** a visitor opens the budget page
- **THEN** the chart appears before its policy key and expanded detail, every official policy is included, and colour or scripts are not required to read names, percentages, and actual amounts.

#### Scenario: Understand the scale
- **WHEN** a policy represents 40 percent of the unrounded consolidated total
- **THEN** it occupies 40 percent of the chart area at every viewport size, without normalising the largest policy to the full plot.

### Requirement: Area-adaptive chart labels
Chart and exported-image labels SHALL use larger type in larger areas and reduce type within bounded minimum sizes to fit complete names, percentages, and actual amounts. They SHALL preserve allocation geometry, never introduce source codes or truncated names, and retain every complete name and both figures in the readable key when a tile cannot fit them.

#### Scenario: Fit a smaller policy
- **WHEN** a policy tile cannot fit its complete name and figures at its initial type size
- **THEN** the renderer reduces type before omitting content, without changing the tile area or clipping text.

### Requirement: Source-bearing image sharing
An explicitly shared image SHALL retain year, approved-budget status, scope/exclusions, exact denominator, rounding context, source/table/version, update/review state, and bundle identity. It SHALL distinguish approved allocations from executed spending and proposal costs. Private preview images SHALL retain a visible draft notice. Native image sharing SHALL have a PNG download fallback and a standalone SVG alternative.

#### Scenario: Share an image
- **WHEN** a visitor shares or saves the chart
- **THEN** the image retains measurement and source context, native sharing is used where supported, and cancellation does not trigger an unwanted download.

### Requirement: Consistent policy colours
Each official policy SHALL have a stable distinct colour in the area chart, complete key, and shared image. Colours SHALL identify policies rather than parties, rankings, or value judgements. White tile text SHALL have contrast of at least 4.5:1. Names and figures SHALL remain readable without colour.

#### Scenario: Policy order changes
- **WHEN** policy amounts or order change
- **THEN** each policy retains its colour and the plot area still follows its unrounded allocation.

### Requirement: Traceable magnitude comparison
The view and shared image SHALL compare the official health and education margins, individually and summed, against pensions. Bars SHALL use one common scale with explicit pension-relative percentages, exact unrounded arithmetic, adjacent coverage notes, and source locators. They SHALL NOT imply total Spanish health/education expenditure or party performance. Missing rows or a zero pension denominator SHALL omit the comparison without imputation.

#### Scenario: Compare with pensions
- **WHEN** the three official margins are available and the pension amount is positive
- **THEN** the summed bar equals the two individual bars combined, labels name pensions as the denominator, and the note explains the regional/local coverage limitation.

#### Scenario: Combined amount exceeds pensions
- **WHEN** health plus education exceed the pension amount
- **THEN** a common scale accommodates the full sum without clipping, while percentage labels remain relative to pensions.

### Requirement: Bounded user-initiated image delivery
Image preparation SHALL occur only after a user action with bounded local assets and the existing publication gate. It SHALL work within the existing serving CSP and SHALL NOT require a chart library, image service, prefetch, service worker, or full-data archive. Preparation/sharing errors SHALL leave the chart and expanded detail usable.

#### Scenario: Image unavailable
- **WHEN** image preparation or sharing fails
- **THEN** an honest failure message appears and the chart, SVG alternative, and full detail remain usable.
