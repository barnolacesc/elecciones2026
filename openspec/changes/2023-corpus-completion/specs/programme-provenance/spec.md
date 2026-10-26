# 2023 corpus inventory and rights delta

Status: draft requirement delta for `2023-corpus-completion`, P0.1. Review and
approve this change before implementation. Existing MVP provenance and
editorial gates remain in force.

## ADDED Requirements

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

### Requirement: Publisher-bound source identity

Before a 2023 document version is marked authentic, the inventory SHALL retain
reviewable evidence connecting the claimed publisher's official entry point to
the exact retrieved bytes and hash. The evidence SHALL identify the observed
landing URL, document URL, redirect or mirror chain, access date, final content
hash and private evidence reference. A URL, matching filename, HTTP success or
locally verified hash alone SHALL NOT establish publisher authenticity. The
authenticity decision SHALL remain separate from rights and editorial review.
Multiple URLs with identical bytes SHALL remain separately evidenced locations
of one source version only after a reviewer confirms their identity; different
bytes SHALL remain distinct versions pending review.

#### Scenario: Official page and unbound document
- **WHEN** an official landing page is registered but no retained evidence binds
  it to the downloaded document version
- **THEN** byte integrity may be reported, but authenticity remains pending.

#### Scenario: Redirect to a mirror
- **WHEN** the registered document URL redirects to a different host
- **THEN** the redirect chain and final bytes are recorded for human review;
  neither the destination nor identical bytes inherit official status or rights.

#### Scenario: Same URL returns changed bytes
- **WHEN** a later retrieval from the same URL has a different hash
- **THEN** the prior version and evidence remain intact and the new bytes enter
  source-identity, locator and downstream editorial re-review before use.

#### Scenario: Duplicate locations
- **WHEN** two candidate URLs return the same hash
- **THEN** they are not counted as two programme versions or silently merged;
  the reviewer records whether they are mirrors of the same exact version.
