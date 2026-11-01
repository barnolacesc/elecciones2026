# Programme comparison

## Purpose
Help readers compare concrete policy positions across candidatures without hiding differences, source gaps or editorial uncertainty.

## ADDED Requirements

### Requirement: Topic and party selection
The MVP SHALL let users select exactly two parties and one topic at a time, restricted to the 8 core topics defined in taxonomy version 1.0.0, and SHALL provide a mobile- and keyboard-usable comparison view grouped by measure. Each measure section SHALL show both parties before the next measure.

#### Scenario: Valid selection
- **WHEN** the reader selects two parties and housing
- **THEN** the site shows each reviewed housing position with source links and caveats.


#### Scenario: Phone comparison
- **WHEN** the reader opens a measure at a phone-sized viewport
- **THEN** both party positions and their source links appear in one vertical section without switching tabs.

#### Scenario: External source navigation in the private 2023 pilot
- **WHEN** a reader follows a programme citation from a static or interactive pilot card
- **THEN** the link text states that the source opens in a new tab before navigation.

#### Scenario: No approved comparison for the selected pair
- **WHEN** no approved measure is available for the selected topic and parties
- **THEN** the empty state explains that absence is not support or opposition and offers a keyboard-accessible route to source coverage and method, including without JavaScript.

#### Scenario: Keyboard submission reaches results
- **WHEN** the reader submits a valid topic and party selection
- **THEN** the result heading names that selection and receives keyboard focus before the measure content.

#### Scenario: Invalid selection clears result context
- **WHEN** the selection becomes invalid
- **THEN** the previous result heading and measure content no longer describe the old selection.

### Requirement: Evidence-based agreement and difference
The site SHALL show an agreement only when reviewers have approved a specific comparable measure; it SHALL show relevant scope, funding or timing differences beside any shared headline.

#### Scenario: Similar slogans but different measures
- **WHEN** two programmes share a broad aim but propose different instruments
- **THEN** no exact agreement is asserted and the difference is explained.

#### Scenario: Matched measure with caveat
- **WHEN** two positions share a measure but differ in eligibility
- **THEN** the common measure and eligibility difference both appear.

### Requirement: Transparent ordering and methodology
The site SHALL use neutral/stable ordering, disclose comparison rules and coverage, and SHALL not rank parties by an undisclosed score.

#### Scenario: Reader opens methodology
- **WHEN** the reader requests the methodology
- **THEN** criteria, review roles, source dates and correction process are available.

#### Scenario: Private pilot reader opens the source index
- **WHEN** the reader follows a document link from the private 2023 pilot source index
- **THEN** its destination comes from that party's registered document URL, independent of measure ordering, while individual measure citations retain their own page locators and provisional review limits remain visible.
