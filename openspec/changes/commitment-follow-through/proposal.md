# Proposal: Prior commitment follow-through

## Status

Exploratory proposal only. No specification, design, tasks, or implementation approval exists. A go/no-go study can reject the feature.

## Why

Readers may want to know what happened after parties made commitments in earlier election programmes. A binary truth label or one percentage can hide missing evidence, shared government responsibility, changed conditions, and different types of commitments.

## What Changes

- Test a method that links a specific prior commitment to its programme version, date, public acts, outcome evidence, and review date.
- Define separate states for fulfilled, partially fulfilled, not fulfilled, not yet assessable, and unknown. Use a state only when the method and evidence support it.
- Record whether a party held relevant office, shared power, or lacked authority to implement the commitment. Do not assume that an observed economic result proves or disproves a party action.
- Check official parliamentary, government, budget, and statistical sources as appropriate to each commitment. Record conflicting evidence and corrections.
- Do not publish a party-wide percentage unless the sampling frame, denominator, time window, and independent review make it comparable and defensible. Do not use a "lies" label.

## Capabilities

### New Capabilities

- `commitment-evidence-register`: Preserve source-linked commitments and evidence with dates and review states.
- `follow-through-method`: Define attribution, uncertainty, and aggregate eligibility rules.

## Impact

This is an optional phase after the core comparator. It requires human editorial and methodology approval. The first deliverable is a feasibility and go/no-go decision, not a public score.
