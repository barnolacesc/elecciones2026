# Historical coverage projection handoff — 2026-11-13

Roadmap package: **P0.6**, proposal-only under `2023-corpus-completion`.
Baseline: `origin/main` `d13ba683`; PR #101 remains open, conflicting and
without GitHub reviews. Its 2026-10-12 green checks do not validate a
resolved candidate. Current main CI run 43325747158 passed; it does not
resolve the 2023 coverage or editorial gates.

## Reproduced repository boundary

`content/sources/register.json` has four `es-gen-2023` rows: all
`published-unverified`, all rights `not_reviewed`, and none with a publication
date. It also has 14 `es-gen-2026` rows, including one replaced version.
These are register counts, not a reviewed 2023 candidature denominator,
complete document inventory, publication chronology or rights approval.

On current main, `render_methodology_page` explicitly filters coverage cards
to `es-gen-2026` and labels the section “Elecciones 2026” even when building
the private 2023 pilot. `render_sources_page` renders the 2026 source section
above a separate 2023 pilot section. Thus a 2023-labelled artifact presents
current-election source coverage. The comparison payload's separate election
checks do not correct these source/method views.

Draft PR #230 addresses the opposite direction: remove 2023 pilot records
from the 2026 public source/method surface. It edits the same renderer and is
currently `CONFLICTING`/`DIRTY` against main. This handoff defines a distinct
2023 projection acceptance boundary; it does not duplicate or modify #230,
PR #101, source rows, rights states, political claims or serving routes.

## Required sequence

1. Editorial owners review the 2023 pilot label and coverage wording; the
   complete 2023 inclusion and document rules remain P0 decisions.
2. Reconcile #230 with main, then implement election-selected source/method
   coverage on the resolved base. Exercise mixed-election and empty historical
   fixtures; verify 2026 production behavior separately.
3. Keep #101's conflict resolution and source-specific rights, dates and
   human summary reviews independent. Neither this spec nor passing CI
   promotes any 2023 position or permits public release.

Evidence: direct inspection of the register and renderer on `d13ba683`,
GitHub PR metadata for #101/#230, and main Actions run metadata. No private
PDF, source text or political answer was opened.
