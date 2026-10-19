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
