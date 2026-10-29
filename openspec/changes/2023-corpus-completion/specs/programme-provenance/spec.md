# 2023 corpus inventory and rights delta

Status: draft requirement delta for `2023-corpus-completion`, P0.1. Review and
approve this change before implementation. Existing MVP provenance and
editorial gates remain in force.

## ADDED Requirements

### Requirement: Review shared-document applicability per candidature

The 2023 inventory SHALL distinguish an immutable document version from each
proposed applicability edge to an included candidature. An edge SHALL identify
the approved manifest/rule revision, exact document version/hash, election,
candidature and constituency scope, document role, evidence and independent
human disposition. A shared file, URL, publisher or coalition name alone SHALL
NOT establish applicability to every related ballot list or member party.
Pending or disputed edges SHALL remain visible in private coverage accounting
but SHALL NOT establish reviewed source coverage, proposal attribution or a
public claim. Counts SHALL label distinct documents and candidatures
separately. This is a proposal-only requirement pending owner review.

#### Scenario: One source proposed for two ballot lists

- **WHEN** one fictional document version is proposed for two included
  constituency-level candidatures but only one edge is evidenced and reviewed
- **THEN** the document is counted once, the reviewed candidature may use its
  scoped source, and the other candidature remains pending rather than
  inheriting coverage or statements.

#### Scenario: Coalition document and member party

- **WHEN** a fictional coalition programme is linked to a coalition ballot
  candidature and a member party has no separately reviewed applicability edge
- **THEN** the member party receives no independent position or coverage from
  coalition membership alone.

#### Scenario: Applicability withdrawn or source replaced

- **WHEN** an approved edge is withdrawn, its scope changes, or its exact
  source version is replaced
- **THEN** affected candidature coverage, topic searches, statements and
  relationships enter re-review; unaffected edges retain their own decisions.

#### Scenario: Same bytes at different URLs

- **WHEN** two publisher URLs serve equal bytes but have different claimed
  candidature or territorial scopes
- **THEN** byte equality alone neither merges applicability decisions nor
  grants rights, and unresolved scope stays pending.

### Requirement: Approved 2023 inclusion denominator

The system SHALL derive claims of 2023 candidature completeness only from a
versioned, human-approved `es-gen-2023` inclusion rule and an evidenced
candidature manifest. The rule SHALL specify eligibility, territorial and
coalition handling, official evidence and exceptions. A pilot source list
SHALL NOT be treated as that denominator.

#### Scenario: Rule or manifest pending
- **WHEN** no approved rule or reconciled manifest exists
- **THEN** the corpus reports scope as unresolved and does not claim all 2023
  candidatures or programmes are covered.

#### Scenario: Included candidature without a document
- **WHEN** a candidature qualifies but no programme has been verified
- **THEN** it remains in the manifest with discovery evidence and an explicit
  missing/unverified state; no policy position or opposition is inferred.

#### Scenario: Proclamation corrected after publication
- **WHEN** an official correction changes a Congress candidature's
  proclamation status or exact ballot name
- **THEN** the manifest preserves the original and corrected values with
  constituency, chamber and both evidence references; coverage counts remain
  unresolved until the correction is applied and reviewed under the approved
  inclusion rule.

### Requirement: Distinct document and rights records

The system SHALL inventory each candidate general programme, territorial
annex, coalition document and replacement as a separately scoped source
version. It SHALL preserve publisher, official URL, language, dated retrieval
evidence, publication-date evidence or unknown, checksum and private archive
reference when bytes exist, source verification state, and replacement links.
Rights SHALL be decided separately per exact source/version and proposed use.

#### Scenario: Integrity without reuse approval
- **WHEN** a local PDF hash verifies but rights are `not_reviewed`
- **THEN** the inventory may report byte integrity but cannot label quotation,
  redistribution or publication approved.

#### Scenario: Unproven date or replacement
- **WHEN** a filename implies a date or a newer PDF is discovered
- **THEN** the date remains unknown until evidenced; the old version remains
  traceable and dependent anchors enter re-review rather than being replaced
  in place.

### Requirement: Reproducible coverage accounting

The system SHALL reconcile included candidatures to document-discovery rows
and source-coverage states under a recorded rule version and input revision.
It SHALL expose unresolved and partial states separately from verified source
coverage. Topic-level absence SHALL require an approved search scope and human
review of the relevant source, not merely no extracted candidate.

#### Scenario: New source changes the denominator or evidence
- **WHEN** a qualifying candidature or relevant programme is added
- **THEN** the prior coverage report is invalidated and counts are rebuilt;
  previously reviewed statements are not automatically approved for the new
  source version.

#### Scenario: Empty extraction
- **WHEN** extraction finds no initiative for a topic
- **THEN** the topic remains unreviewed/unknown, not `not stated` or opposed.
