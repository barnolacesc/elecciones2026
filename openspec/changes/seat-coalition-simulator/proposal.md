# Proposal: Seat and coalition simulator

## Why

Readers may want to test parliamentary seat scenarios and see which arithmetic coalitions meet a stated threshold. This tool must not present a user scenario as an election forecast or a likely political pact.

## What Changes

- Accept manual seat counts for official candidacies and validate totals against the selected chamber and election context.
- Show an accessible hemicycle plus an equivalent text table.
- Compute coalition seat sums and explain the exact arithmetic threshold in use.
- Let a reader share a scenario through a URL without an account or stored profile, after a privacy and URL-length review.
- Keep vote-to-seat estimation and political probability out of the initial simulator.

## Capabilities

### New Capabilities

- `seat-scenario`: Validate and display a manual seat distribution.
- `coalition-arithmetic`: Calculate coalition sums under documented, verified rules.

### Modified Capabilities

- `static-publication`: Add a client-side simulator route without a new server API.

## Impact

This is **phase 3, after the quiz**, unless priorities change. Verify the applicable chamber rules against official sources before completing specs. The simulator may use the existing static deployment but needs its own accessibility and correctness tests. It must not label a coalition as politically feasible or probable.
