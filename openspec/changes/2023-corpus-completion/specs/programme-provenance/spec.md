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

### Requirement: Current rights decision and withdrawal propagation

For each exact 2023 source version and proposed use, the publication projection
SHALL depend on the current, human-attributed rights decision, not only a
historical approval or the source hash. A withdrawal, narrower use decision,
expiry, or credible unresolved challenge SHALL retain the prior decision for
audit, mark affected uses pending or denied, and invalidate dependent public
statements, quotations, comparisons and quiz items for release review. A
decision for outbound linking SHALL NOT authorize paraphrase, quotation or PDF
redistribution. A changed rights decision SHALL NOT erase a separately
reviewed source-integrity or editorial record, but neither record overrides the
current use restriction. CI SHALL NOT infer or self-approve a new permission.

#### Scenario: Same bytes, narrower permission
- **WHEN** the rights owner narrows permission for an unchanged source hash
  from short quotation to outbound linking only
- **THEN** quotations and any other no-longer-permitted uses leave the next
  publish set, their prior decisions remain auditable, and unaffected links
  remain subject to their own current decision and editorial gates.

#### Scenario: Approval challenged without a final decision
- **WHEN** a credible challenge to a version-bound use decision is recorded
  but the human rights owner has not resolved it
- **THEN** affected uses are withheld from the next publish set and no prior
  approval is silently reused.

#### Scenario: Existing served artifact
- **WHEN** an affected claim is already in a served static artifact
- **THEN** the system records affected artifact and dependency IDs for an
  owner-controlled correction or withdrawal release; a passing rebuild alone
  SHALL NOT be reported as removal from the served site.

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

### Requirement: Unambiguous source-use scope for 2023 summaries

The future 2023 source-use contract SHALL distinguish an outbound-link-only
decision from a human decision that explicitly permits a neutral paraphrase
for the exact source version. A link-only decision SHALL NOT authorize a
summary, quote or redistribution. A summary-plus-link decision SHALL NOT
authorize a quote or redistribution. The source register, programme status,
validator, public label and tests SHALL use the same reviewed meaning; an
ambiguous status name or free-text note SHALL NOT widen a permission. A
withdrawal or narrower decision SHALL withhold dependent claims pending
release review. This is a proposal-only requirement; it does not approve a
legal use, status migration, real source or publication.

#### Scenario: Link-only decision and a reviewed statement

- **WHEN** a fictional exact source version has only a human outbound-link
  decision and a statement has completed editorial review
- **THEN** the outbound link may be eligible for display under its own gates,
  but the statement summary, quotation and PDF copy remain ineligible.

#### Scenario: Explicit summary decision without quotation permission

- **WHEN** a fictional source version has a separate human decision for
  neutral paraphrase and outbound link but no quotation permission
- **THEN** a quote-free statement may proceed to the remaining provenance and
  editorial gates; a verbatim quote and PDF copy remain ineligible.

#### Scenario: Ambiguous legacy status

- **WHEN** a source has an old `link_only` label without an explicit
  version-bound decision for paraphrase
- **THEN** no migration or public label silently treats it as permission for
  a summary.

#### Scenario: Narrowed use after a summary was approved

- **WHEN** the human rights owner narrows a fictional source version from
  summary-plus-link to outbound-link-only use
- **THEN** the affected summary and dependent comparison are withheld from
  the next publish set, prior decisions remain auditable, and an existing
  served artifact enters owner-controlled correction or withdrawal review.
