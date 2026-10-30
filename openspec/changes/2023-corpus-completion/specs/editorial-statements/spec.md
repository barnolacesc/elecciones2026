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

### Requirement: Version-bound topic-search evidence

Before publishing a `not_found` or equivalent absence label, the system SHALL
retain a human-reviewed search ledger bound to the exact election,
candidature, topic, taxonomy revision and relevant document-set revision. The
ledger SHALL identify each included source version, searched page/section
scope, method, reviewer, candidate dispositions and unresolved exclusions.
An approved inclusion and source-scope protocol SHALL govern which documents
must be searched. Empty extraction, a single searched document or rights
approval SHALL NOT substitute for that ledger. An absence conclusion SHALL be
scoped to the reviewed source set and SHALL NOT imply political opposition or
completeness of the entire party platform.

#### Scenario: Unsearched annex

- **WHEN** the main programme has been searched but a relevant annex has not
- **THEN** the topic remains partial and no absence label is publishable.

#### Scenario: Empty machine search without human review

- **WHEN** an extractor returns no candidates across the fixed source set but
  the search scope, method or candidate dispositions are pending human review
- **THEN** coverage remains pending; `not_found` is not publishable.

#### Scenario: Approved scoped negative finding

- **WHEN** the approved protocol and human reviewers establish that all
  relevant source ranges were searched with no supported candidate
- **THEN** any absence label identifies its reviewed source scope and cannot
  be used as an agreement or divergence operand.

#### Scenario: New relevant document or changed taxonomy

- **WHEN** an annex or replacement joins the source set, or the applicable
  taxonomy revision changes
- **THEN** the former negative finding is invalidated and unpublished until
  its exact dependencies are re-reviewed.

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

### Requirement: Approved 2023 taxonomy applicability

A 2023 proposal classification or topic-coverage claim SHALL be bound to a
versioned taxonomy that the human editorial owners explicitly approve for
`es-gen-2023`. Topic-ID membership in the existing `es-gen-2026` taxonomy,
a matching version string, or a provisional quiz label SHALL NOT substitute
for that decision. The review record SHALL identify the exact taxonomy
revision, election scope and effective corpus revision. A change to category
boundaries or subtopics SHALL preserve the prior classification and invalidate
affected statement, relationship, coverage and quiz dependencies for review.

#### Scenario: Shared IDs without 2023 approval

- **WHEN** a 2023 candidate uses a valid core topic and subtopic from the
  2026-scoped taxonomy but no 2023 applicability decision exists
- **THEN** the system treats the classification as provisional and does not
  count it as reviewed 2023 topic coverage.

#### Scenario: Taxonomy boundary revision

- **WHEN** an approved 2023 category boundary or subtopic changes
- **THEN** affected classifications and downstream coverage or comparison
  decisions remain traceable and pending review rather than inheriting the
  old approval automatically.

### Requirement: Source-bound qualification fidelity

A candidate and its proposed public summary SHALL distinguish the operative
measure from every source-stated condition, exception, affected population,
territorial limit, amount and time limit that changes its meaning. Each such
qualification SHALL have a locator in the same immutable source version, or
an explicit unresolved evidence state. A reviewer SHALL decide whether a
shorter summary preserves the measure's scope; a generated summary or a
single broad page citation SHALL NOT establish that decision. Unresolved or
disputed material qualifications SHALL block publication of that statement
and any relationship that uses it. The private evidence ledger, not the public
build, retains source wording and reviewer deliberation.

#### Scenario: Condition is separated from the headline

- **WHEN** a fictional source states a measure in one section and limits its
  eligible population in another section of the same version
- **THEN** the candidate records both locators and the public summary cannot
  present the measure as universal while the limitation is unreviewed.

#### Scenario: Exception changes the comparison

- **WHEN** a fictional measure has a source-stated exception that changes who
  is covered, but a proposed summary or relationship omits that exception
- **THEN** the statement and dependent relationship remain unpublished until
  human reviewers resolve the omission against the exact source version.

#### Scenario: No stated limit is not an unlimited promise

- **WHEN** the reviewed source range does not state an amount or deadline
- **THEN** those fields remain unknown; the summary does not assert that the
  measure has no cap or deadline.
