# Proposal: Reuse the corpus pipeline for a separate election

Status: technical preparation requested on 2026-11-11; editorial and release gates remain open. Roadmap phase: P4. Bounded package: E1.4-2026 (corpus intake and election-scoped publication).

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

### New Capabilities

- `programme-provenance`: election-scoped versioning and review.
- `static-publication`: distinct election views and corrections.

## Impact and gates

The owner now requests the 2026 comparator and incremental programme loading.
The accompanying specs/design/tasks define technical preparation. Budget reuse
is deferred to its existing separate change. New political content and rights
decisions need human approval; technical migration tests alone cannot authorize
publication. Unverified originals remain outside Git and public artifacts.
