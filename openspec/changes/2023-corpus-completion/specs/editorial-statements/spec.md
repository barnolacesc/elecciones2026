# Editorial statements — 2023 corpus delta

Status: draft requirement delta for human/OpenSpec review; not implementation
approval. Election scope: `es-gen-2023`. This extends the unarchived MVP
`editorial-statements` capability without approving real content.

## ADDED Requirements

### Requirement: Review assignment eligibility before counting a verdict

For `es-gen-2023`, a human review verdict SHALL count toward a statement,
topic-absence or cross-party relationship decision only when a separate,
current human-authorized eligibility disposition covers that reviewer, role,
exact record revision, election, candidature and territorial assignment under
an approved 2023 recusal policy. A relationship assignment SHALL cover both
operand candidatures. Distinct reviewer IDs, a verdict, or a declaration for a
different assignment SHALL NOT establish eligibility. Eligibility and
conflict disclosures SHALL remain private; public records and routine CI logs
SHALL contain no political-affiliation details. A pending, withdrawn, expired
or disputed eligibility decision SHALL fail closed for affected publication
and preserve prior decisions for audit. This requirement is proposal-only;
the 2023 policy and adjudicator require owner approval.

#### Scenario: Distinct reviewers without eligibility evidence

- **WHEN** two fictional people approve the same statement revision but one
  assignment has no current eligibility disposition
- **THEN** the dual-review gate remains unmet despite distinct reviewer IDs.

#### Scenario: Relation reviewer covers only one party

- **WHEN** a fictional relationship reviewer is eligible for one operand's
  candidature but has no decision for the other under the approved scope
- **THEN** the relation remains unpublished without changing either
  independently reviewed statement.

#### Scenario: Recusal after a prior verdict

- **WHEN** a reviewer recuses or an eligibility decision is withdrawn for an
  exact assignment after its verdict was counted
- **THEN** affected statements, absence findings, relationships and quiz
  dependencies enter a private impact/re-review queue; an unrelated verdict
  remains separately traceable and no political disclosure enters the build.

#### Scenario: New revision and stale attestation

- **WHEN** a statement or relationship revision changes, or an attestation
  expires before a subsequent review
- **THEN** a prior assignment decision is not silently reused for the new
  review, even if the summary text or reviewer ID appears unchanged.

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

### Requirement: Review applicability across relevant documents

Before publishing a 2023 initiative, the system SHALL account for relevant
general, territorial, coalition and replacement documents under the approved
candidature/document scope. It SHALL bind each candidate to its exact source
version, speaker and territorial applicability, and retain potentially
overlapping candidates and their review disposition. No document role,
apparent date or URL order SHALL automatically resolve a material conflict or
establish that one text supersedes another. An unresolved material conflict
SHALL block an unqualified synthesized position and any relationship using
that position; unaffected approved statements MAY remain eligible with a
reviewed scope limitation. The precedence, attribution and conflict-review
rules require human editorial approval before implementation.

#### Scenario: Territorial qualification differs

- **WHEN** a general document and a territorial annex address the same measure
  with different eligibility in one constituency
- **THEN** the difference enters review and neither an election-wide summary
  nor a cross-party relation silently erases the territorial qualification.

#### Scenario: Unproven replacement

- **WHEN** a second URL appears newer but no evidenced replacement chain exists
- **THEN** the earlier source remains traceable and neither source is treated
  as automatically superseded.

#### Scenario: Coalition attribution unresolved

- **WHEN** a coalition document and a member-party document overlap but their
  speaker-to-candidature mapping is not approved
- **THEN** the system withholds a merged candidature position rather than
  attributing both texts to the same approved speaker.

#### Scenario: Conflict affects only one initiative

- **WHEN** one candidate has unresolved material terms and a separate
  non-conflicting candidate has all publication approvals
- **THEN** the unresolved candidate remains in the private accounting while
  the approved candidate can be shown only under the reviewed scope rule.

#### Scenario: Applicability decision changes

- **WHEN** a reviewed source-scope or precedence decision is corrected
- **THEN** dependent statements and comparison relationships are invalidated
  until re-reviewed against the corrected decision.

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

### Requirement: Reviewable initiative identity across source occurrences

The private 2023 extraction queue SHALL distinguish a source occurrence, a
candidate measure and a reviewed initiative identity. Each occurrence SHALL
retain its exact source version/hash and locator. A proposed split, grouping or
duplicate disposition SHALL retain all contributing occurrence IDs, rationale,
reviewer decision and superseded candidate IDs. Text similarity, repeated
extraction runs or a shared topic SHALL NOT merge candidates or count one
initiative twice. A change to the operative action, beneficiary, jurisdiction,
condition, amount or timing SHALL remain unresolved until a human reviewer
decides whether it is the same initiative, a qualification, a distinct
initiative or a conflict under the document-applicability protocol. Public
summaries SHALL NOT inherit approval from an earlier candidate grouping.

#### Scenario: Repeated extraction of one passage

- **WHEN** two runs find the same measure at the same source version and locator
- **THEN** both extraction events remain auditable, but the proposed coverage
  count does not become two initiatives solely because of the repeated run.

#### Scenario: One sentence, two independent measures

- **WHEN** one passage states two separately actionable instruments
- **THEN** reviewers may split it into two candidate initiatives sharing the
  occurrence, with a recorded split rationale and separate review paths.

#### Scenario: Same measure in programme and annex

- **WHEN** two relevant documents appear to repeat a measure
- **THEN** both exact locators remain in the private lineage and the identity
  decision stays pending until source scope and a human duplicate review pass;
  neither occurrence is silently discarded.

#### Scenario: Similar wording with a material condition change

- **WHEN** two passages differ in eligibility or timing despite similar words
- **THEN** automatic deduplication is rejected and the difference enters the
  document-applicability and editorial review queue.

#### Scenario: Reclassified or split approved candidate

- **WHEN** an approved candidate is later split or grouped differently
- **THEN** its old identity and review remain traceable, while the new public
  statements, relationships and coverage counts remain pending exact-version
  review; no approval is inherited.

### Requirement: Preserve quantitative claim context

A candidate or reviewed statement that contains a quantity SHALL retain the
exact source version and locator for the value, plus its stated unit, reference
period, population or denominator, geographic scope, condition and whether it
is a commitment, target, baseline or example. Unstated context SHALL remain
unknown. A derived or converted value SHALL require a separately reviewable
calculation, input provenance, rounding rule and human approval before public
use; a tool SHALL NOT silently normalize quantities.

#### Scenario: Target mistaken for current amount

- **WHEN** a fictional source promises a future target and gives a current
  baseline in the same passage
- **THEN** the two values retain distinct roles and the summary does not
  present the target as an existing allocation or achieved result.

#### Scenario: Missing period or denominator

- **WHEN** a fictional measure gives a number without a period or denominator
- **THEN** the missing context remains unknown and no annualized or per-person
  value is inferred.

#### Scenario: Corrected quantitative source

- **WHEN** the source version, cited value or its qualifier changes
- **THEN** the prior interpretation and any derived value are invalidated for
  review, with the old source-linked version retained.

### Requirement: Source-language bridge for Spanish summaries

A Spanish public summary derived from a non-Spanish source SHALL retain an
explicitly evidenced language check bound to the exact source version and
physical locator, statement revision, source/output languages and material
qualifications. The editorial owners SHALL decide whether this check is a
distinct decision or an explicit, traceable part of the existing independent
statement reviews. A completed worksheet, source link or successful build
SHALL NOT substitute for authentic review evidence. Language review SHALL NOT
grant source reuse rights or approve the political interpretation by itself.
Private source wording and translation working notes SHALL stay outside Git
and the public artifact.

#### Scenario: Non-Spanish source without evidenced language check

- **WHEN** a Spanish candidate summary cites a Catalan-language source but no
  language check is bound to that exact source and statement revision
- **THEN** the summary remains unpublished even if its source hash matches and
  its generic statement reviews are otherwise present.

#### Scenario: Existing reviews contain the explicit check

- **WHEN** the editorial owners accept evidence that the required check was
  made within the existing independent reviews of the exact revisions
- **THEN** the bridge may refer to those decisions without inventing an
  additional reviewer, date or approval state.

#### Scenario: Material translation correction

- **WHEN** review changes the Spanish rendering of a source qualification,
  jurisdiction, amount or timing
- **THEN** the statement is versioned and dependent relationships, coverage
  presentation and quiz mappings stay pending until their exact dependencies
  are reviewed again.

#### Scenario: Source or locator changes

- **WHEN** the source bytes, version or physical locator change
- **THEN** the prior language check cannot approve the new source-to-summary
  mapping and the affected summary remains unpublished pending re-review.

#### Scenario: Spanish source without translation

- **WHEN** a Spanish summary derives directly from a Spanish-language source
- **THEN** normal source, rights and statement gates apply without requiring a
  fictitious translation decision.

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

### Requirement: Account for extraction visibility before topic-search review

For each required source version and page or section range, the private 2023
search ledger SHALL distinguish a successful text extraction from human-verified
visual readability, an extraction failure, and an uninspected range. It SHALL
bind the observation to the immutable source hash, physical page range,
extractor identity and evidence reference. A byte-valid PDF, matching page
count, nonempty machine text, or empty machine text SHALL NOT by itself prove
that all policy-relevant wording was readable or searched. Unresolved ranges
SHALL block a reviewed negative finding under the separate topic-search gate.
The visual review evidence and extracted text SHALL remain private; this
requirement grants no source rights or editorial approval.

#### Scenario: Image-only page with empty extracted text

- **WHEN** a required physical page has empty text extraction but visible text
  has not been inspected by a human reviewer
- **THEN** its visibility state remains unresolved and no topic absence can be
  approved from the machine result.

#### Scenario: Nonempty extraction loses a material column

- **WHEN** the extracted text is nonempty but a visual check finds omitted or
  reordered policy text in a second column
- **THEN** the affected range is marked extraction-incomplete and any dependent
  search conclusion waits for a documented manual or reviewed alternate pass.

#### Scenario: Blank page verified visually

- **WHEN** an empty extracted page is visually confirmed to contain no relevant
  text under the approved review protocol
- **THEN** the ledger may mark that page inspected, without treating it as a
  negative finding for the entire document or topic.

#### Scenario: Extraction tool changes

- **WHEN** a replacement extractor or new image version produces different
  text for the same source hash
- **THEN** the old and new observations remain traceable and dependent search
  conclusions are re-evaluated; the new extraction does not silently inherit
  a prior visibility decision.

#### Scenario: OCR proposed for an unreadable range

- **WHEN** an editor proposes OCR or another processing route for a range that
  could not be searched reliably
- **THEN** the range remains unresolved until the route, its output and the
  original page are reviewed; OCR text alone cannot approve a claim or absence.

