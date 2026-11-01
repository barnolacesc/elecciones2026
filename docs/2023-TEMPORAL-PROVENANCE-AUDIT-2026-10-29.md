# 2023 source-version chronology: baseline and proposed gate

Date: 2026-10-29. Roadmap package: P0.9, `2023-corpus-completion`.
Status: evidence-backed proposal for owner/OpenSpec review, not a source-date
decision or permission to publish. Baseline: `origin/main` at `8e2fab4`.

## Observed baseline

The source register has four `es-gen-2023` pilot rows: PP, ERC, PNV and Sumar.
All four have `publication_date: null`, `status: published-unverified` and
`rights_review.status: not_reviewed`. Their `retrieval_date` values are
2026-10-10 (PP, ERC) and 2026-10-09 (PNV, Sumar). The pilot inventory retains
hashes and private extraction-integrity observations, but neither a hash nor
a 2026 retrieval date proves when those exact bytes became public. This audit
does not inspect or redistribute source PDFs.

Open draft PR #101 is conflicting with current main and its passing CI dates
to 2026-10-12; it has no recorded PR review. Draft PR #166 proposes an
integration gate and explicitly supersedes #101 after review. Both remain
unmerged. Their source/publication-date and rights requirements cannot be
treated as an approved chronology policy. Recent PR CI jobs did not execute
steps (the account billing/spending-limit block is reported in #166); the
current checks do not establish integrated passing tests, still less human
editorial review.

## Distinct question this package resolves in specification only

An election-labelled filename, a dated landing page and a later retrieved
PDF answer different questions. A reviewer needs to know whether a date is
evidence for the *programme concept*, the linked URL, or the exact archived
version. The proposed P0.9 gate keeps observed dates separate and permits an
unknown or bounded interval until the exact-version chronology is reviewed.
It does not change the P0 inclusion denominator, source rights, candidate
positions, comparison method or any public view.

## Owner decisions and next acceptance evidence

The owner/editorial team must select admissible evidence and reviewers, decide
how date precision and revisions are expressed, and decide whether an
unresolved historical date blocks or qualifies a private 2023 comparator.
Only then can a schema and fictional tests be implemented. PR #101/#166 must
be reconciled before changing their source fields. Source-rights and content
review remain separate gates even if the chronology is established.
