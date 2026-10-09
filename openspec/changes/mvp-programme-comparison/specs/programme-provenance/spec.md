# Programme provenance

## Purpose
Identify each election programme precisely, make coverage visible, and prevent unverified documents from silently entering public comparisons.

## ADDED Requirements

### Requirement: Versioned programme registration
The system SHALL register a programme only with election ID, party/candidature ID, source publisher, original URL, retrieval/publication dates, language, version, SHA-256, rights status and coverage status. The election ID SHALL identify the election type and date. A 2023 general-election programme SHALL NOT become a 2026 programme through a version update.

#### Scenario: Valid source registered
- **WHEN** a reviewer submits all mandatory metadata and a verifiable document
- **THEN** the validator records the immutable version and its hash.

#### Scenario: Missing metadata
- **WHEN** a source lacks a mandatory provenance field or its hash differs
- **THEN** publication fails with a specific diagnostic.

#### Scenario: Earlier election used for a pilot
- **WHEN** a pilot registers a 2023 general-election programme
- **THEN** its election ID remains 2023 and all generated pilot pages identify the 2023 election.

### Requirement: Election-scoped comparison
The system SHALL compare only programmes that belong to the selected election. It SHALL NOT silently mix statements from different election years or use an older programme as the current programme.

#### Scenario: Programme for another election
- **WHEN** a comparison selects a 2026 election and a 2023 programme
- **THEN** the build rejects the comparison and reports the election mismatch.

### Requirement: Transparent incomplete coverage
The public site SHALL list candidatures within the chosen official coverage scope even when a programme is missing, and SHALL distinguish absent, partial and superseded sources.

#### Scenario: Party has no verified programme
- **WHEN** a covered candidature has no verified source
- **THEN** the site marks it pending and creates no inferred position.
