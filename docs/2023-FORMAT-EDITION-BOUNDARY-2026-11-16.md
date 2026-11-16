# P0.17 parallel-format edition boundary

Status: proposal-only repository audit for `2023-corpus-completion`, election
`es-gen-2023`. Baseline: `origin/main` `d13ba68` on 2026-11-16. No publisher
site or private programme bytes were inspected for this packet.

## Observed contract

- The main source register has four 2023 pilot rows (PP, ERC, PNV, Sumar),
  all `published-unverified`, rights `not_reviewed`, publication date null.
  This is neither an approved inclusion denominator nor a verified rendition
  inventory. The register schema has one `official_url`/`direct_url`, filename
  and SHA-256 per source, but no rendition-to-edition equivalence decision.
- E1.2's private acquisition and extraction workflow accepts registered PDFs.
  It does not determine whether a publisher's HTML, accessible or print
  rendition carries the same content as a PDF. P0.4 handles same-byte mirrors;
  P0.9 handles chronology; P0.10 handles attribution to candidatures. None
  establishes cross-format content equivalence or transfers rights/locators.
- Draft PR #101 remains open, conflicting with main and without GitHub reviews.
  Its historical checks succeeded on its old head; they do not validate a
  resolved candidate or grant source rights. PR #250 covers its rights-grant
  integration, not parallel-format identity. Main's latest check runs passed,
  but passing CI is not human source or editorial review.

## Review handoff

Treat each format/version as a candidate rendition. Keep one reviewed edition
count only after a human compares exact scoped content and records evidence;
otherwise retain variants and an unresolved coverage state. A same-title
HTML page could be a full edition, abridgement or companion. The source owner
must decide which, not a hash/text heuristic. Exact passage locators and
rights decisions remain format/version-specific. If a web rendition changes,
retain the earlier capture and invalidate only dependent decisions; do not
quietly promote the unchanged PDF's review to the new page.

The OpenSpec delta supplies four fictional scenarios and a private ledger
design. It does not change the register, PDF worker, political statements,
rights or review marks, public build, routing or deployment. Owners must settle
edition scope, evidence, rights, reviewer and coverage wording before schema
or ingestion work. No claim is made that any of the four pilot sources has a
parallel format.
