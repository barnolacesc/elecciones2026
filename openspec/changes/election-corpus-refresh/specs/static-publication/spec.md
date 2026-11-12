# Spec Delta

## Purpose

Produce a 2026 comparator from approved records while keeping unavailable
programmes and pending editorial work visible to readers.

## ADDED Requirements

### Requirement: Default to the current election
The default local container preview SHALL select the 2026 production corpus.
Historical rehearsal SHALL require an explicit election selection.

#### Scenario: Default preview
- **WHEN** an operator builds the preview without an election override
- **THEN** it identifies the 2026 election and exposes no 2023 programme inventory

### Requirement: Show truthful coverage
The 2026 view SHALL list its registered parties and source states, without
fictional parties, review badges or historical source substitution. Missing
approved claims SHALL be labelled as pending review, not political opposition.

#### Scenario: Document received without editorial approval
- **WHEN** a source is registered as published-unverified
- **THEN** the view shows the document's recorded state without a reviewed position

### Requirement: Support incremental publication
New approved statements and relationships SHALL enter the same versioned
production directories and SHALL pass the same validation on each build.

#### Scenario: Repeat build
- **WHEN** records and build date remain unchanged
- **THEN** all generated file hashes remain identical

### Requirement: Bind staging candidates to the selected election
The authenticated staging pipeline SHALL build and identify the 2026 production
record mode consistently. Historical reviewed candidates MAY remain eligible
for operator-selected recovery. Candidate validation MUST reject public
classification; this path MUST NOT grant political approval or public routing.

#### Scenario: Current-election staging candidate
- **WHEN** a trusted main CI run produces a 2026 approved-record-mode candidate
- **THEN** its matching private-staging metadata passes election/mode validation

#### Scenario: Public classification in staging delivery
- **WHEN** a candidate claims public classification
- **THEN** the authenticated staging validator rejects it
