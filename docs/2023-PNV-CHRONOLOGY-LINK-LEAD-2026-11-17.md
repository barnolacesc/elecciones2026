# EAJ-PNV 23J announcement-to-PDF chronology lead

Roadmap package: **P0.9**, `2023-corpus-completion` (proposal-only).
Checked on 2026-11-17 against `origin/main` `d13ba68`, the open PR queue,
the source register and the publisher pages below. This is evidence for a
private source-version review, not a publication-date, rights, authenticity,
coverage or editorial decision. No PDF bytes or political text entered Git.

## Reconciled baseline

- `src-2023-pnv-v1` is one of four 2023 pilot rows. It records the [current
  publisher document page](https://www.eaj-pnv.eus/es/documentos/20945/con-voz-propia-programa-electoral-23-j),
  a direct PDF URL under `/es/adjuntos-documentos/`, and a previously recorded
  SHA-256. Its `publication_date` is `null`, its status is
  `published-unverified`, and its rights state is `not_reviewed`. The four
  rows are not an approved 2023 candidature or document denominator.
- [PR #210](https://github.com/c2ventures/elecciones2026/pull/210) separately
  records a Basque-language document lead. This note concerns the dated
  *Spanish* announcement and its different PDF path, not language equivalence.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  draft and conflicting, with no GitHub reviews. Its old green checks do not
  test the combined current tree or approve a PNV source. Its integration
  candidate [PR #166](https://github.com/c2ventures/elecciones2026/pull/166)
  was merged; neither establishes this version's chronology or rights.

## Publisher evidence observed

| Observation | Boundary |
|---|---|
| The [EAJ-PNV announcement](https://abb.eaj-pnv.eus/es/noticias/54787/aitor-esteban-presenta-un-programa-electoral-desde) displays **07/07/2023**, says the party presented its 23J programme, and links the labelled programme to `https://www.eaj-pnv.eus/adjuntos/pnvDocumentos/20945_archivo.pdf`. | The date belongs to the announcement. A current link does not prove which exact bytes were served on that day. The announcement is a candidate provenance/chronology lead, not a hash-bound publication record. |
| A 2026-11-17 HEAD request to that legacy PDF URL returned `200`, `application/pdf`, `Content-Length: 3602932`, and `Last-Modified: Fri, 07 Jul 2023 09:05:44 GMT`. | These are current server responses. `Last-Modified` is not independently verified historical publication evidence. No bytes were captured in this package. |
| A 2026-11-17 HEAD request to the registered `/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j` URL returned the same status, type, length and `Last-Modified` value. | Matching headers do not prove that the two URLs serve identical bytes, that either matches the registered SHA-256, or that neither changed after 2023. |

The [current document page](https://www.eaj-pnv.eus/es/documentos/20945/con-voz-propia-programa-electoral-23-j)
and the dated announcement are both publisher pages, but their different
PDF paths must not be silently collapsed into one verified source version.
The page's `23 Julio 2023` label denotes the election context; it is not an
accepted publication date for the current PDF hash.

## Private P0 handoff

1. Preserve dated evidence of the announcement, its actual link target and
   current document-page link. Through the authorised private archive, compare
   exact bytes and hashes for the legacy URL, current URL and registered
   `src-2023-pnv-v1` file; record redirects and retrieval times separately.
2. If hashes match, ask the human source owner whether the 2023 announcement
   adequately binds that exact version to a pre-election publication event.
   If they differ, retain separate version candidates and investigate
   replacement history and affected page locators. Do not overwrite the
   existing row or copy its review state to another version.
3. Obtain independent human authenticity and permitted-use decisions for the
   exact version. Rights for linking, paraphrase, quotation and PDF
   redistribution remain separate. Reconcile the Basque-language lead and
   candidature applicability under the approved P0 inventory rule before
   claiming document or topic coverage.

No source record, statement, relationship, rights mark, OpenSpec readiness
state, public artifact, routing or deployment was changed. The existing P0.9
design/spec/tasks remain drafts; this lead does not authorize implementation.

## Validation

The four-row 2023 register baseline and PNV pending fields were parsed
locally. The publisher announcement and both PDF HEAD responses were checked
on 2026-11-17. `git diff --check` passed. No PDF hash comparison, historical
web archive verification, private rights review or political-content review
was performed. Main's latest CI run at `d13ba68` succeeded; that engineering
result does not establish source identity or human approval.
