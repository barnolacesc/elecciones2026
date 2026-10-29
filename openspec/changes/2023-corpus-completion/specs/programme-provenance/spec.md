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

### Requirement: Version-bound temporal provenance

The inventory SHALL distinguish a document's evidenced publication date from
the dates on which a URL was observed, bytes were retrieved or archived, and a
human reviewed a source or reuse decision. A claimed publication date SHALL
identify its evidence, the exact document version or hash to which it applies,
and the human decision accepting that evidence. Unknown publication dates SHALL
remain unknown. A URL path, filename, PDF metadata, filesystem timestamp or
later retrieval date alone SHALL NOT establish that the same bytes were public
before the 2023 election. Source authenticity, chronology, reuse rights and
editorial approval SHALL remain independent decisions.

#### Scenario: Later retrieval of a 2023-labelled file

- **WHEN** a file whose URL or title contains `2023` was retrieved in 2026 but
  no evidence dates publication of its exact version
- **THEN** the inventory retains the retrieval date and an unknown publication
  date; it does not claim pre-election availability.

#### Scenario: Dated page does not identify exact bytes

- **WHEN** a publisher page has a date but its link may have served a revised
  file at the same URL
- **THEN** that page is recorded as candidate chronology evidence, not an
  automatic publication date for the current hash.

#### Scenario: Replacement at a stable URL

- **WHEN** a newly retrieved file at the same URL has a different hash
- **THEN** the prior version and its dated evidence remain traceable, and the
  new version's chronology is pending until separately reviewed; previous
  statement and locator approvals are not inherited.

#### Scenario: Rights review without date evidence

- **WHEN** a human approves a limited source use but the version's publication
  date remains unknown
- **THEN** the rights decision does not fill the date or prove historical
  availability; the publication policy handles that uncertainty separately.
