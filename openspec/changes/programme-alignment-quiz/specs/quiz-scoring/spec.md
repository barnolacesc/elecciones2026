# Quiz scoring

## Purpose

Calculate reproducible alignment with answered programme measures in the browser and make each contribution and limitation inspectable.

## ADDED Requirements

### Requirement: Defined answer and party scales
Visitor answers SHALL use the ordered values -1, -0.5, 0, 0.5, and 1. A skip SHALL be absent, not zero. A party position SHALL be -1 for explicit rejection or 1 for explicit support of the exact measure, with reviewed evidence. Absence, ambiguity, and conditional positions that cannot be represented faithfully SHALL have no numeric value.

#### Scenario: Neutral answer and skip differ
- **WHEN** a visitor selects “Ni de acuerdo ni en desacuerdo”
- **THEN** the answer is zero and contributes to scoring.
- **WHEN** the visitor selects “Omitir” or “No lo sé”
- **THEN** the item is excluded from the answered-item denominator.

#### Scenario: Programme silence
- **WHEN** an otherwise verified programme does not address a measure
- **THEN** no position is inferred and the party is ineligible for an aggregate score under the coverage rule.

### Requirement: Local deterministic topic-normalized score
All calculations SHALL run locally. Per-item alignment SHALL be `m = 1 - abs(answer - position) / 2`. Each answered topic SHALL contribute the mean of its answered items. The aggregate SHALL be 100 times the weighted mean of these topic means, using the same answered items and weights for every eligible party. Weights SHALL default to 1; local options SHALL be 1 or 2 per topic.

#### Scenario: Known arithmetic
- **WHEN** one answered topic has two answers equal to 1 and a party's positions are 1 and -1
- **THEN** the item alignments are 1 and 0, and that topic alignment is 50 percent.
- **AND** the aggregate remains withheld until the answer threshold is met.

#### Scenario: Weight change
- **WHEN** a visitor changes a topic weight from 1 to 2
- **THEN** all eligible party aggregates update using that same weight, with the change explained locally and no data transfer.
- **AND** an unanswered topic still has no contribution to the answered score.

#### Scenario: Reproducible result
- **WHEN** the same set, answers, and weights are evaluated twice
- **THEN** every item, topic, and unrounded aggregate value is identical; display rounding does not affect calculation.

### Requirement: Minimum answer coverage
Aggregate scores SHALL be displayed only after at least eight numeric answers across at least four topics. Below this threshold the flow SHALL show answer and topic counts, source details, and an insufficient-answer explanation without aggregate scores. This threshold SHALL be described as a method limit, not statistical confidence.

#### Scenario: Empty or narrow response
- **WHEN** all items are skipped, fewer than eight are answered, or fewer than four topics are answered
- **THEN** no aggregate or division by zero occurs, and the visitor can return to any item.

### Requirement: Stable limited-precision result presentation
Party results SHALL use alphabetical display-name order, whole-number percentages, and the label alignment with answered measures. Exact ties SHALL remain ties; a difference of at most one unrounded percentage point SHALL be labelled a small difference. Rounded equal values SHALL be explained. No winner, recommendation, or statistical significance SHALL be inferred.

#### Scenario: Tie
- **WHEN** two parties have identical unrounded scores
- **THEN** both show an explicit tie note with no priority or tie-break rule based on popularity, seats, or party identity.

#### Scenario: Small or rounded difference
- **WHEN** scores differ by at most one point or round to the same integer
- **THEN** the result explains the small difference or display rounding, without calling either party the best match.

### Requirement: Unanswered-item bounds and sensitivity
Results SHALL show bounds for each eligible party under all permitted answers to skipped items, using all 16 items and the current weights. They SHALL also show the range from removing each answered item in turn where the minimum threshold still holds. These SHALL be labelled scenario bounds and sensitivity, never probability or confidence intervals.

#### Scenario: Skipped topic
- **WHEN** both items in a topic are skipped
- **THEN** that topic is absent from the answered score but contributes its minimum and maximum possible alignment to the full-set bounds.
- **AND** overlap between parties' bounds is disclosed without claiming an ordering.

#### Scenario: Sensitivity unavailable
- **WHEN** removing any answered item would leave insufficient answer coverage
- **THEN** the result says sensitivity cannot be calculated at this coverage level, rather than presenting an empty range as certainty.

### Requirement: Inspectable contribution and revision
Each result SHALL expose the visitor answer, party position, item alignment, topic mean, topic weight, normalized contribution, included and skipped items, and excluded-party gaps. Every scored position SHALL link to its exact provenance. Editing an answer or weight SHALL replace the prior contribution and recompute the explanation.

#### Scenario: Explain a changed score
- **WHEN** a visitor edits an answer and opens “Cómo se calcula”
- **THEN** they can inspect the previous and current aggregate change in memory, the current item calculation, the affected topic mean, and its source citations.
- **AND** the explanation remains in plain Spanish, with the formula available as additional detail.

### Requirement: Fail closed on invalid scoring data
Invalid values, duplicate items, mixed set versions, or an incomplete numeric position vector for an eligible party SHALL stop scoring and show an accessible Spanish error. Stale answers SHALL NOT be applied to a different set.

#### Scenario: Corrupt bundle
- **WHEN** a set contains an out-of-range answer mapping or a claimed eligible party lacks a position
- **THEN** no partial result is shown, and the visitor can clear the session and read the static method page.
