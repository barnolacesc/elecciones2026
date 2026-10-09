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

### Requirement: Transparent incomplete coverage and status lifecycle
The public site SHALL list candidatures within the chosen official coverage scope even when a programme is missing, and SHALL distinguish the six defined status states: `missing`, `announced`, `partial`, `published-unverified`, `official`, and `replaced`.

#### Scenario: Party has no verified programme
- **WHEN** a covered candidature has no verified source
- **THEN** the site marks it `missing` with an explicit "Programa no disponible" banner and creates no inferred position.

#### Scenario: Replaced programme version
- **WHEN** a party publishes an updated programme replacing an earlier verified document
- **THEN** the earlier record is marked `replaced`, preserves its hash and publication date, points to the new version in `superseded_by`, and marks derived comparison records for re-evaluation.

#### Scenario: Partial programme published
- **WHEN** a party publishes a preliminary summary or partial commitment list
- **THEN** the site marks it `partial`, links the official document, and explicitly notes its partial scope.

### Requirement: Candidate inclusion and party naming standard
The system SHALL track candidacies meeting objective inclusion criteria (parliamentary representation in the outgoing legislature or European Parliament, or proclamation in constituencies with at least 50% of the electorate). Every tracked party or coalition record SHALL include an immutable kebab-case `id`, `official_name`, `display_name`, `short_name`, and explicit `coalition_members` relations.

#### Scenario: Coalition registered
- **WHEN** an electoral coalition is formed for the 2026 election
- **THEN** the validator requires `is_coalition: true`, explicit list of registered member party IDs, and does not conflate it with a prior election coalition of similar name.

