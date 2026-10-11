# Proposal: Programme alignment quiz

Roadmap package: **E4.1**. This planning deliverable defines future packages E4.2–E4.4 for **Gate G5**. Status: draft for human review; no implementation or release approval is recorded here.

## Why

Readers need a voluntary way to inspect alignment between their answers and verified programme measures. The method must explain each score without collecting political preferences or recommending a vote.

## What Changes

- Specify 16 reviewed items, two per taxonomy topic, with a published coverage matrix, source-linked party positions, and explicit source gaps.
- Define deterministic browser-only scoring, optional local topic weights, skip rules, coverage thresholds, ties, and bounds for unanswered items. Display parties alphabetically and explain every score.
- Define a Spanish mobile flow, full WCAG 2.2 AA acceptance, zero visitor tracking, memory-only answers, and editorial, fairness, privacy, and release checks.

## Capabilities

### New Capabilities

- `quiz-question-set`: Reviewed item selection, eight-topic balance, provenance, coverage, corrections, and neutral Spanish drafting rules.
- `quiz-scoring`: Local alignment calculation, equal comparison denominators, answer and weight changes, ties, sensitivity, and source-linked explanations.
- `quiz-mobile-flow`: Accessible introduction, question, review, result, and method states for phones.
- `quiz-privacy`: No tracking, accounts, answer transfer, persistent profiles, or personalized sharing; auditable fairness and operational privacy checks.

### Modified Capabilities

None. The main spec inventory is empty. `static-publication` is an unarchived MVP change capability, not an existing main spec. These quiz capabilities add requirements without rewriting that change. Integration must preserve its static build and publication gates.

## Impact

The implementation extends the Python 3.14 reviewed-data build and static Spanish site with `/cuestionario/`, versioned public data, and a small local script. It needs no API, database, new account system, or server score calculation. Untrusted document extraction remains offline and outside the public container. The current implementation uses an explicitly enabled private mock set; real questions remain an editorial deliverable.

The user authorized local technical implementation with mock data before G4/E1.4. The mock preview must be explicitly enabled, labelled fictional, and excluded from indexing. Real content activation still requires recorded G4 and E1.4 evidence plus editorial approval of E4.1. G5 additionally requires reviewed real items, fairness/privacy evidence, accessibility acceptance, and user tests. Historical rehearsal material cannot satisfy the target-election gate.

Exclusions: vote advice, forecasts, party leaderboards, accounts, analytics, remote inference, persistent answers, personalized exports or share links, generated political questions, automatic publication, and a source-report service.

Key risks are unequal source coverage, partisan wording, false numerical precision, inaccessible result details, and political data leaking through storage or logs. The specs require visible gaps, dual human review, limited score precision, complete-process accessibility checks, and a strict privacy audit. Existing technical-log policy must be reconciled before G5; it is not evidence of zero tracking.
