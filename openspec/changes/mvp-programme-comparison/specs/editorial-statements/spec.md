# Editorial statements

## Purpose
Represent party positions in short neutral language while preserving the exact documentary basis and a reviewable correction path.

## ADDED Requirements

### Requirement: Source-linked positions
Every published position SHALL include a stable ID, party ID, topic/subtopic, neutral summary, statement type, source version, page/section, review status and last-reviewed date.

#### Scenario: Reviewed explicit proposal
- **WHEN** two reviewers approve a source-linked proposal
- **THEN** the build may publish it with the original source link and qualifications.

#### Scenario: Unsupported draft
- **WHEN** a position is draft, uncited, or references a superseded/unknown source
- **THEN** the build rejects it rather than substituting a model-generated statement.

### Requirement: Distinguish absence from opposition
The system SHALL represent `not_found` separately from explicit opposition and SHALL show coverage limitations.

#### Scenario: Topic absent in reviewed programme
- **WHEN** no supported position is found for a topic
- **THEN** the UI says the reviewed source does not state a position, not that the party opposes it.

### Requirement: Auditable corrections
Published substantive changes SHALL retain the prior statement ID/version, correction reason and date.

#### Scenario: Misclassification reported
- **WHEN** a reviewer corrects a topic classification
- **THEN** the old classification remains traceable and affected comparisons are rebuilt.
