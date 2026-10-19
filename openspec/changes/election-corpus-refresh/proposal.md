# Proposal: Reuse the corpus pipeline for a separate election

Status: proposal only; not implementation-ready. Roadmap phase: P4.

## Why

The reviewed 2023 corpus should become a reusable method, not political data
silently relabelled when 2026 programmes arrive.

## What Changes

- Define election-scoped sources, statements, relationships, coverage, quiz
  items and published routes. Reject cross-election references by default.
- Import each new 2026 source version through the same hash, rights, page,
  taxonomy, review and correction gates; show unavailable content honestly.
- Audit official budget periods and measures before reusing a 2023 budget view.
  Keep approved, extended and executed amounts separate.

## Capabilities

### Modified Capabilities

- `programme-provenance`: election-scoped versioning and review.
- `static-publication`: distinct election views and corrections.
- `budget-data-bundle`: period-aware reuse, subject to budget-context review.

## Impact and gates

Complete specs/design/tasks after the P0–P1 source model is reviewed. New
political content and rights decisions need human approval; technical migration
tests alone cannot authorize publication.
