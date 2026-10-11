# Quiz question set

## Purpose

Provide a balanced, human-reviewed set of programme measures that visitors can inspect without inferred political positions.

## ADDED Requirements

### Requirement: Fixed eight-topic balance
Each public set SHALL contain 16 items, exactly two per approved taxonomy topic. The set SHALL use one election ID, taxonomy version, set version, and fixed item order. It SHALL NOT adapt to visitor answers or party scores.

#### Scenario: Complete set
- **WHEN** a set is validated for publication
- **THEN** it contains two items each for `housing`, `education`, `health-social-services`, `economy-work-tax`, `immigration`, `foreign-policy-eu`, `climate-energy`, and `institutions-rights`.
- **AND** items have unique IDs and measure IDs, with no repeated measure in a second topic.

#### Scenario: Topic lacks evidence
- **WHEN** a topic cannot supply two eligible measures
- **THEN** the quiz remains unavailable with a Spanish coverage explanation; other topics cannot fill its quota.

### Requirement: Source-based item eligibility
Each item SHALL express one specific measure in neutral Spanish. Two distinct human reviewers SHALL approve its wording, qualifications, response scale, topic, and each party-position mapping. Slogans, speculative conduct, bundled measures, and unresolved conditional positions SHALL NOT become scored items.

#### Scenario: Draft selection
- **WHEN** editors select an item from verified programmes
- **THEN** they record its policy instrument, scope, relevant conditions, selection rationale, rejected alternatives, and source-supported mapping to the same measure for every covered party.
- **AND** neither automated extraction nor a visual mockup counts as approval.

#### Scenario: Ambiguous measure
- **WHEN** a condition cannot be preserved in the question or two measures require different answers
- **THEN** editors reject that item or revise it and obtain fresh dual approval before selection.

### Requirement: Exact lawful provenance
Each scored position SHALL reference an approved statement and a verified official programme for the target election. Its public trace SHALL expose the official URL, programme ID, version, SHA-256, page or section, relevant qualification, rights status, and review date. Review evidence SHALL be auditable without exposing private reviewer details.

#### Scenario: Source inspected
- **WHEN** a visitor opens an item's source details
- **THEN** the party position and its precise locator remain visible alongside a link to the original document.
- **AND** quotation limits and approved reuse rights are respected; a full source file is not republished by default.

#### Scenario: Invalid source
- **WHEN** a record has a missing citation, unapproved rights, unverified programme, wrong election, fabricated reviewer, or rehearsal-only source
- **THEN** the build rejects its use in the target-election quiz.

### Requirement: Explicit comparable coverage
The set SHALL publish a party-by-item coverage matrix for every party in the approved inclusion register. A party SHALL receive a score only if it has a reviewed position on all 16 items. At least two parties SHALL qualify before the quiz is available. Missing evidence SHALL NOT be assigned any numeric position.

#### Scenario: Incomplete party
- **WHEN** a party has a partial, absent, or ambiguous position on one or more items
- **THEN** its card says that coverage is insufficient, shows the gaps and source status, and has no aggregate score.
- **AND** it remains in the coverage matrix and is not described as opposed.

#### Scenario: Common denominator unavailable
- **WHEN** fewer than two parties have complete reviewed coverage
- **THEN** no quiz result is offered; visitors can still inspect the coverage and methodology.

### Requirement: Conflict and correction invalidation
A conflicting source, replaced programme, or substantive correction SHALL invalidate dependent item text and mappings. The build SHALL reject a set that uses invalidated records until fresh dual review and a new immutable set version are recorded.

#### Scenario: Conflicting positions
- **WHEN** verified sources give incompatible positions on the same measure
- **THEN** editors record the conflict and resolve it with exact evidence before assigning a numeric position; unresolved conflicts remain unscored gaps.

#### Scenario: Source replaced
- **WHEN** a programme is superseded or a statement is corrected
- **THEN** all dependent items and mappings require re-review, with a dated correction trail and updated set version.

### Requirement: Neutral Spanish draft guidelines
Public drafting SHALL use `es-ES`, one short measure per item, defined technical terms, and identical response labels. It SHALL preserve source conditions and avoid emotive language, party slogans, double negatives, leading questions, and unsupported political text. Guidelines and UI drafts SHALL remain unapproved until human editorial review.

#### Scenario: Wording reviewed
- **WHEN** editors review the public draft
- **THEN** they apply these Spanish guidelines: “Una medida por pregunta. Usa frases breves. Conserva las condiciones de la fuente. Explica los términos técnicos. Evita lemas, juicios de valor y preguntas que sugieran una respuesta.”
- **AND** no example question is invented to fill a source gap.

### Requirement: Audited selection fairness
Editors SHALL publish the selection method, topic quotas, coverage limits, scoring policy, and set date. Before G5, a second review lane SHALL audit each selected and rejected candidate for framing, party coverage, duplicate measures, and asymmetric evidence standards. Unresolved substantive bias SHALL block release.

#### Scenario: Selection audit
- **WHEN** the G5 review evaluates a proposed set
- **THEN** it checks the two-item quota, all-party matrix, neutral ordering, qualifications, and the selection/rejection register using the same evidence standard for every party.
- **AND** the review records findings and resolutions rather than claiming neutrality from equal question counts alone.

### Requirement: Private mock preview isolation
A private mock preview SHALL require explicit opt-in, use a separate fixture election ID, and label all examples as fictional. It SHALL have no political claims, official citations, or editorial approval marks. Mock pages SHALL be excluded from indexing and the sitemap. The default build SHALL not activate mock scoring, and reviewed mode SHALL reject mock data.

#### Scenario: Technical rehearsal before source review
- **WHEN** a developer explicitly enables the authorized local mock preview
- **THEN** generic test items and fictional party vectors exercise the real quiz structure without implying verified programme content.
- **AND** a default rebuild removes its generated mock scoring bundle and shows an unavailable quiz until reviewed data is supplied.
