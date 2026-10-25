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
