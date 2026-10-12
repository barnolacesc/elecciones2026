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

### Requirement: Topic taxonomy alignment
Every published position SHALL belong to exactly one of the 8 core topics defined in taxonomy version 1.0.0 (`housing`, `education`, `health-social-services`, `economy-work-tax`, `immigration`, `foreign-policy-eu`, `climate-energy`, `institutions-rights`) and an approved subtopic matching its primary operational instrument.

#### Scenario: Cross-cutting proposal classified
- **WHEN** a proposal touches multiple topics (e.g. rent assistance for youth workers)
- **THEN** reviewers classify it under the topic matching its primary operational mechanism (`housing`), and document the classification rationale.

### Requirement: Verbatim quotation limits and unsupported quote rejection
An explicitly reviewed `link_only` source MAY support a neutral, quote-free editorial summary and outbound link when its programme provenance, publication date, source-specific reuse decision and two version-bound human approvals pass. `not_reviewed` and `permission_denied` SHALL NOT support publication. Programme rights status SHALL agree with the source decision. This summary rule does not permit a verbatim quote.

#### Scenario: Reviewed link-only summary
- **WHEN** a verified 2023 source has a dated, evidenced `link_only` decision and matching official programme, and two humans approve the exact quote-free statement version
- **THEN** the statement may enter the private 2023 publish set, with its source locator and qualifications.

#### Scenario: Undated report is not an approval date
- **WHEN** an owner reports another review without the actual review date
- **THEN** the report and its exact-version fingerprint remain audit material, but the statement cannot become approved until the date is established.

Verbatim quotations extracted from official sources SHALL NOT exceed 40 words or 300 characters, SHALL be enclosed in quotation marks, and SHALL include exact locators (page or section). The system SHALL reject any statement containing an unsupported quote where the source is unverified, rights do not permit quotation, locators are missing, or quotation limits are exceeded.

#### Scenario: Compliant verbatim quotation
- **WHEN** an operative commitment of 25 words is extracted with page citation from a verified source with `link_and_short_quote` rights
- **THEN** the validator approves the quotation record for editorial review.

#### Scenario: Quotation exceeding word limit
- **WHEN** an extracted quote contains more than 40 words
- **THEN** the validator rejects the statement and requires shortening or neutral paraphrasing.

#### Scenario: Unsupported quote from restricted or unverified source
- **WHEN** a quote references an unverified source (`missing`, `announced`) or a source with rights status `link_only`, `permission_denied`, or `not_reviewed`
- **THEN** the build fails and rejects publication of the unsupported quote.

### Requirement: Independent dual review and reviewer segregation
Every published position SHALL require recorded approvals from at least two distinct human reviewers (`reviewed_by_1` and `reviewed_by_2`). The drafter of a proposal SHALL NOT serve as the secondary reviewer (`reviewed_by_2`).

#### Scenario: Dual review approved
- **WHEN** two distinct human reviewers audit factual citation and neutrality and record approval
- **THEN** the statement passes publication validation.

#### Scenario: Four-eyes violation
- **WHEN** a single individual is entered as both primary and secondary reviewer
- **THEN** validation fails with a Four-Eyes principle violation.

#### Scenario: Drafter acting as secondary reviewer
- **WHEN** the drafter who extracted the proposal also acts as secondary reviewer
- **THEN** validation fails with a segregation of duties violation.

### Requirement: Invalidation of dependent comparison relationships
When a source statement is corrected or marked invalidated, all comparison relationships that reference that statement ID SHALL automatically be marked `invalidated` with a documented reason, and SHALL NOT be displayed in public comparisons until re-audited.

#### Scenario: Statement correction triggers relationship invalidation
- **WHEN** a published statement is updated via a dated `CorrectionRecord`
- **THEN** all comparative relationships linking that statement are marked `status: "invalidated"` and removed from active public comparison output.
