# 2023 extraction visibility: P1.7 proposal handoff

Status: proposal-only, for OpenSpec and editorial review. Snapshot:
`origin/main` `8e2fab4` on 2026-10-31. This is a repository-contract audit,
not a reinspection of any political PDF or an approval of an absence claim.

## Reconciled baseline

- `content/sources/register.json` has four `es-gen-2023` pilot rows (PP, ERC,
  PNV and Sumar). All are `published-unverified` with rights `not_reviewed`.
  These rows are not an approved inclusion denominator or source-rights set.
- E1.2's `make_artifacts` checks page count, page text type and total size and
  stores physical page number, extracted text hash, Poppler version and worker
  image/platform in the private artifact. Its synthetic test includes one
  empty extracted page. The artifact has no per-page visual inspection result.
- `docs/PRIVATE-SOURCE-ARCHIVE.md` already warns that extraction may reorder
  columns, omit image-only text or misread glyphs and requires checking the
  original PDF visually. P1.3's search ledger identifies ranges and leaves
  non-searchable-range treatment for owner review; it does not yet define how
  extraction visibility is evidenced for every required range.
- PR #101 remains open, conflicting and without GitHub reviews; PR #166 is a
  separate integration candidate. Neither is changed by this package. Recent
  PR CI jobs failed without executing steps, so hosted checks cannot be claimed
  as validation of this draft.

## Specific risk and bounded handoff

A page-count match proves only that the extractor returned the expected number
of page slots. A zero-length slot may be blank or image-only; a nonempty slot
can still omit a table, column or qualification. If either is treated as a
completed search, P1.3 could produce an unsupported `not stated` conclusion.
P1.7 proposes a private, source-hash-bound visibility observation for each
required search range, with unresolved states that block a negative finding.
It does not change the existing archive worker, search ledger, source register,
programme summaries or public UI.

The editorial owners must decide the inspection protocol, whether and how OCR
may assist, reviewer quorum, and evidence retention before implementation.
The five fictional scenarios in the OpenSpec requirement cover blank versus
image-only pages, incomplete nonempty extraction, tool changes and OCR. They
are acceptance examples, not observations about the four pilot PDFs.

No source bytes, extracted text, page images, political positions, rights
marks, reviewer approvals or personal answers are included in this PR.
