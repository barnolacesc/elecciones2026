# P1.8 candidate-search quality handoff — 2026-11-19

Status: proposal-only audit for `2023-corpus-completion`, not approval of a search protocol, programme source, political statement, rights use or public coverage claim. Baseline: `origin/main` `d13ba68` after the 2026 corpus merge. This audit uses repository files and GitHub metadata only; it did not inspect private PDFs or political text.

## Reconciled baseline

- `content/sources/register.json` contains four `es-gen-2023` pilot rows: PP, ERC, PNV and Sumar. Each is `published-unverified` with rights `not_reviewed`. These are neither an approved 2023 candidature denominator nor a complete programme inventory.
- `src/elecciones2026/private_archive.py` verifies extraction artifacts and page mapping. P1.7's draft range-visibility gate correctly distinguishes text extraction from visual readability. P1.3's draft topic-search ledger records searched ranges and candidate dispositions. Neither currently defines an independent check for actionable measures missed *within readable, searched ranges*.
- P1.6 separately addresses duplicate source occurrences and initiative identity. P1.2 separately accounts for reviewed measures in a comparison set. A missed source measure cannot reach either set without a candidate-search quality step; this draft therefore sits between P1.3/P1.7 and proposal review. It changes no extraction code or data.
- PR #101 is open, draft and conflicting with current main; its GitHub review list contains zero reviews. Its earlier green checks apply to an older head/base and cannot approve the current 2023 publication gate. Main CI run `43325747158` on `d13ba68` passed, but passing CI is not editorial review.
- There are 61 open PRs at this snapshot, including focused P0/P1 drafts and PR #257's digest integration audit. This package does not edit PR #101's source, rights, summary, schema or generator files and does not repeat the digest audit.

## Specific method gap and review decision

A byte-valid, visually readable PDF and an auditable search range still do not prove that the search found each actionable measure. The proposed private quality pass records independently found candidates, first-pass omissions, duplicates, ambiguous classifications and unresolved disagreements against exact source versions and locators. Owners must choose a full second pass or a defined sampling frame, reviewer independence, arbitration and rework/stopping rules. A zero-miss sample is not an all-programme recall estimate; unsampled required ranges remain unresolved. Any omission requires impact review for topic coverage and dependent comparisons.

The OpenSpec requirement, design and tasks contain four fictional cases. Only after human method review and P0 source/rights decisions should a concrete ledger schema or validator be designed. Real candidates, summary wording, relations and coverage labels still need their own human decisions. No PDF, extracted text, political answer, rights mark, reviewer approval or public output is included in this change.
