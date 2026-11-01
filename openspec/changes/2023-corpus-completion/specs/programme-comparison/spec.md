# Programme comparison — 2023 corpus delta

Status: draft requirement delta for human/OpenSpec review; not implementation
approval. Election scope: `es-gen-2023`. This extends the unarchived MVP
`programme-comparison` capability; it does not approve real relationships.

## ADDED Requirements

### Requirement: Match a specific policy question

A cross-party relationship SHALL identify the policy question and the exact
approved statement versions being compared within one election. Reviewers
SHALL document why the action/instrument and affected population/scope are
comparable, plus any material differences in jurisdiction, eligibility,
magnitude, financing and timing where the sources state them. Topic or slogan
similarity alone SHALL NOT establish agreement.

#### Scenario: Similar aspiration, different instruments

- **WHEN** two statements name the same broad goal but different measures
- **THEN** the site does not label an exact agreement without reviewed grounds.

#### Scenario: Shared instrument, different eligibility

- **WHEN** two measures use the same instrument but restrict different groups
- **THEN** any approved agreement or partial overlap displays that difference
  beside the shared element.

### Requirement: Independent relationship approval

An active public relationship SHALL have its own human approval evidence for
its exact statement pair, grounds, type and caveats, separate from statement
approvals. A relation referencing an unapproved, invalidated or cross-election
statement SHALL fail closed. The final reviewer quorum and segregation rule
remain an editorial decision before implementation.

#### Scenario: Approved statements, unreviewed relation

- **WHEN** both party statements are approved but their proposed relation is
  still a draft
- **THEN** the statements may appear individually if other gates pass, but no
  agreement, divergence or partial-overlap claim appears.

#### Scenario: Changed operand

- **WHEN** the meaning or version of either linked statement changes
- **THEN** the former relationship is invalidated and cannot reappear without
  approval of the new exact pair.

### Requirement: Distinguish no comparison from disagreement

The comparison SHALL distinguish a reviewed difference, a single-party
measure, a reviewed absence conclusion and an unresolved coverage gap.
`not_found` SHALL NOT be an operand for agreement or divergence. Counts and
coverage labels SHALL state the approved candidature/document/topic
denominator and review stage; they SHALL NOT imply exhaustive coverage while
required sources or searches are unresolved.

#### Scenario: Only one approved statement

- **WHEN** only one party has a reviewed statement for a policy question
- **THEN** the comparison may show that statement with the other side's honest
  coverage state, but it does not infer opposition or a relationship.

#### Scenario: No approved 2023 denominator

- **WHEN** the candidature manifest or relevant document scope is not approved
- **THEN** the site does not publish a percentage or claim that all 2023
  programmes or topics were covered.

### Requirement: Account for the full reviewed comparison set

For a selected election, topic and two candidatures, the comparison SHALL
account for every eligible, publishable statement version in the reviewed
topic scope. A relationship SHALL describe only its exact operands and policy
question; it SHALL NOT stand in for all measures from either candidature.
Unpaired measures SHALL remain visible as single-party measures or have an
explicit, reviewable exclusion reason and a reader-facing scope limitation.
The method SHALL disclose the included statement set, unmatched measures and
the review stage before any aggregate or topic-wide agreement claim. If the
source/topic coverage or this accounting is incomplete, the view SHALL use
bounded wording about the measures shown, not an exhaustive comparison claim.

#### Scenario: One reviewed relation and one unmatched measure

- **WHEN** candidature A has two publishable measures in a topic, candidature
  B has one, and a reviewed relation covers only one A/B pair
- **THEN** the other A measure is not silently discarded and the relation is
  not described as agreement or divergence across the whole topic.

#### Scenario: Several measures answer one policy question

- **WHEN** one candidature has multiple reviewed measures for a policy
  question that the current display can represent with only one position
- **THEN** the extra measures remain in the accounting and publication is
  blocked or clearly limited until reviewers choose a lossless grouping rule;
  the renderer does not select one silently.

#### Scenario: Pending source scope

- **WHEN** a required annex or topic search remains unreviewed
- **THEN** the displayed comparison may describe its reviewed measures but
  does not claim complete topic coverage or party-wide agreement.

### Requirement: Resolve duplicate relationship decisions before publication

For an election and exact unordered pair of approved statement versions, the
comparison SHALL have at most one effective, human-reviewed relationship
decision for a policy question. The publication gate SHALL detect competing
active decisions even when their IDs, labels or review dates differ. It SHALL
not choose a winner by file order, ID, recency or relationship type. Historical
invalidated decisions remain traceable but are not effective decisions. If
reviewers intend distinct policy questions for the same pair, they SHALL
record and approve that distinction before either can be displayed. A single
statement may participate in different reviewed pairs; that alone is not a
collision. This requirement does not decide which political interpretation is
correct or approve a real relationship.

#### Scenario: Conflicting classifications for one exact pair

- **WHEN** two active relationship records use the same election and exact
  statement versions but one says agreement and the other says divergence
- **THEN** neither is selected by the renderer and the affected comparison
  fails closed pending human resolution.

#### Scenario: Duplicate classification with different IDs

- **WHEN** two active records for the same exact pair and policy question both
  say partial overlap but have different IDs or caveats
- **THEN** the duplicate still requires reconciliation; matching type alone
  does not establish one approved effective decision.

#### Scenario: Historical decision and replacement

- **WHEN** the earlier decision is explicitly invalidated with a retained
  correction trail and a new exact-pair decision is independently approved
- **THEN** only the new decision may be effective; the old one remains in the
  audit history and cannot reappear in a later build.

#### Scenario: One statement in two distinct pairs

- **WHEN** a reviewed statement is paired separately with two different
  reviewed statements under approved policy questions
- **THEN** the distinct pairs are retained for set accounting rather than
  rejected as duplicate decisions.

### Requirement: Close correction dependencies before publication

For `es-gen-2023`, a correction to a source version, locator, taxonomy
assignment, statement or relationship SHALL produce a version-bound impact
set before the static and browser publish sets are built. The impact set SHALL
include affected topic-search/absence decisions, statements, relationships,
comparison-set accounting and quiz citations, where present. Each affected
derived claim SHALL be withheld until its own applicable human review is
renewed; an omitted or unresolved dependency SHALL fail closed. Withheld
content SHALL NOT be rendered as `not stated` or as disagreement. Correction
history SHALL retain prior versions without exposing private evidence, source
bytes or political answers. The precise review roles and public notice policy
remain owner/editorial decisions.

#### Scenario: Corrected statement in a paired measure

- **WHEN** one approved statement in a reviewed pair is retracted or changed
- **THEN** its relationship and any set-wide conclusion are withheld until
  the exact new pair is reviewed; an unrelated approved measure is not
  automatically described as absent.

#### Scenario: Source replacement with an old page locator

- **WHEN** an in-scope source version changes but a dependent statement still
  points to the old page locator
- **THEN** publication fails closed for that statement and its dependents,
  even if the visible summary text did not change.

#### Scenario: Correction omitted from one projection

- **WHEN** the static and browser publish sets disagree about an invalidated
  relationship or topic-coverage conclusion
- **THEN** the build fails instead of reviving the claim in one view.

