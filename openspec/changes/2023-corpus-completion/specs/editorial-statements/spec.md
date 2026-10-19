# Editorial statements — 2023 corpus delta

Status: draft requirement delta for human/OpenSpec review; not implementation
approval. Election scope: `es-gen-2023`. This extends the unarchived MVP
`editorial-statements` capability without approving real content.

## ADDED Requirements

### Requirement: Version-bound initiative candidates

The private extraction queue SHALL bind each candidate measure to its election,
candidature, exact document version/hash, page or stable section, extraction
run and taxonomy version. It SHALL represent one actionable measure per
candidate and distinguish explicitly stated actor, action, instrument,
beneficiary, jurisdiction, conditions, amount and timing from unknown fields.
Candidate wording and PDF text SHALL remain outside the public build.

#### Scenario: Composite source sentence

- **WHEN** a source sentence describes two distinct instruments
- **THEN** the queue retains two separately locatable candidates, not one
  combined public proposal.

#### Scenario: Unstated amount

- **WHEN** the source names an instrument but gives no amount
- **THEN** the candidate records the amount as unknown and no amount is
  supplied by an extractor or reviewer without new source evidence.

### Requirement: Reviewed proposal interpretation and summary

The system SHALL keep candidate classification, neutral statement wording and
publication approval distinct. A public 2023 statement SHALL have exact
version/page evidence, its stated qualifications, the existing independent
dual-human statement review, and a rights-compatible publication decision.
An automated extraction or a source link alone SHALL NOT approve a statement.

#### Scenario: Broad aim without an actionable measure

- **WHEN** a candidate is only a general objective or slogan
- **THEN** it is not promoted to a concrete policy proposal without an
  evidenced actor/action/instrument and editorial review.

#### Scenario: Rights remain unresolved

- **WHEN** a source is `not_reviewed` for reuse even though a summary has
  content reviews
- **THEN** publication remains blocked; no quote or paraphrase permission is
  inferred from the content reviews.

### Requirement: Audited topic search before an absence claim

For every in-scope candidature and topic, coverage SHALL identify relevant
document versions, searched page/section scope, search method, reviewer and
unresolved exclusions. `not_found` or reader-facing `not stated` SHALL be
unavailable while a required document or relevant section is unsearched or
the search has not been approved under the editorial protocol. Absence SHALL
never mean explicit opposition.

#### Scenario: Partial programme with an unsearched annex

- **WHEN** the main programme was searched but a relevant annex was not
- **THEN** topic coverage remains partial/unknown and no exhaustive absence
  claim is published.

#### Scenario: Empty extraction queue

- **WHEN** automated extraction returns no candidates for a topic
- **THEN** the result is an unreviewed search outcome, not `not_found`.

### Requirement: Correction dependency invalidation

A changed source version/hash, locator, taxonomy assignment or statement
meaning SHALL invalidate dependent absence conclusions and comparison
relationships for re-review. The correction trail SHALL retain the old version
and affected IDs; a deterministic rebuild SHALL NOT reactivate invalidated
records by omission of the correction.

#### Scenario: Programme replacement

- **WHEN** a programme is replaced with a new source hash
- **THEN** dependent page evidence and relationships stay unpublished until
  reviewed against the replacement, while the old version remains traceable.
