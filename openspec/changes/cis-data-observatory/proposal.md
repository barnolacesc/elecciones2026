# Proposal: CIS data observatory

## Why

Readers may need a clear view of official CIS studies and historical trends. Polls, estimates, and election results use different measures and must not be merged without method checks.

## What Changes

- Import selected official CIS study releases through a versioned, reviewed process.
- Preserve field dates, sample, population, question wording, method, uncertainty, and source version.
- Display trends only when questions and methods are comparable. Mark series breaks.
- Provide an accessible chart, equivalent table, downloadable source references, and a clear data cut-off.
- Keep study import outside the public runtime. Verify access terms and machine-readable formats before choosing automation.

## Capabilities

### New Capabilities

- `cis-source-register`: Track official studies and method metadata.
- `poll-series`: Display comparable, qualified time series.

### Modified Capabilities

- `static-publication`: Add generated observatory pages and datasets.

## Impact

This is **phase 4**. It can be planned in parallel with the simulator, but data claims cannot be published before source and method review. It is not part of the MVP or quiz. The detailed specification and tasks remain a separate approval gate.
