# Proposal: Official budget context

## Why

Readers may want to understand the size and share of official spending policies. A sourced budget view can provide context without claiming that a party caused an amount or outcome. The approved 2023 PGE is the first bounded dataset. It is not a statement of current 2026 allocations.

## What Changes

- Import the official 2023 approved-budget, chapters 1–8 consolidated policy-by-section table offline and generate a static, Spanish-language budget page.
- Show policy totals and the official section breakdown. A section is not always a ministry. Add programme-level detail only from a separately verified official table.
- Show amounts, shares, year, coverage, unit, source, and update date.
- Use a mobile-first ranked bar list and an equivalent table. Treat a treemap as an optional secondary view.
- Keep approved or extended budget figures separate from execution figures. Do not publish 2023 amounts as current 2026 amounts.

## Capabilities

### New Capabilities

- `budget-source-register`: Record the official dataset, version, scope, checksum, and review state.
- `budget-context-view`: Show a traceable expenditure breakdown and its denominator.

### Modified Capabilities

- `static-publication`: Add generated budget pages without a public API.

## Impact

This is a separate post-MVP release, but source and UI work can start in parallel with the comparator. It does not block the comparator, quiz, simulator, or CIS work. Public release requires its own source and measurement review. No chart or number is approved by this proposal.
