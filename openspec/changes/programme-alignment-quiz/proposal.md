# Proposal: Programme alignment quiz

## Why

After readers can inspect source-linked programme statements, they can use a voluntary quiz to see which party programmes are closer to their answers. The quiz must not infer a vote choice or hide how it calculates a result.

## What Changes

- Add a short, mobile-first quiz based only on reviewed statements from the published programme dataset.
- Balance question selection across parties and topics. Let readers skip questions.
- Show each statement's source before or after an answer, with a clear path to the full comparison.
- Calculate results in the browser. Show the scoring rule, weights, gaps, uncertainty, and sensitivity to skipped questions.
- Keep answers in memory only by default. Do not transmit or persist political-preference answers, identifiers, or analytics events.
- If a reader chooses to share, offer a generic link to the quiz or a neutral topic page. Do not include answers, party scores, or vote-intention text in the link by default. A personalized result share needs a separate privacy and editorial decision.
- Audit question wording and scoring for partisan bias before release.

## Capabilities

### New Capabilities

- `quiz-question-set`: Build balanced, reviewed, source-linked questions from published statements.
- `quiz-scoring`: Calculate and explain local programme proximity without a vote recommendation.
- `quiz-privacy`: Keep answers on the device and prevent collection by analytics or logs.

### Modified Capabilities

- `static-publication`: Add a quiz route and static data while keeping server-side execution and user profiles absent.

## Impact

This is **phase 2, after the MVP**. It depends on reviewed programme coverage and an approved editorial method. It does not require a new server API. The detailed specification, design, and tasks must be approved before implementation. A quiz with unequal source coverage must not imply false precision.
