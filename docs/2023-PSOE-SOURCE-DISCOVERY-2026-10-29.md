# PSOE 2023 programme discovery evidence — 2026-10-29

Roadmap package: **P0.11** (`2023-corpus-completion`, proposal-only). This is
one candidate-document discovery handoff, not an approved 2023 candidature,
source record, rights decision, topic search, political claim or release.

## Reconciled baseline

`origin/main` at `8e2fab4` contains four `es-gen-2023` pilot source rows
(PP, ERC, PNV and Sumar) in `content/sources/register.json`, all with rights
`not_reviewed`. It contains no 2023 PSOE source row. Its separate
`src-2026-psoe-v0` row points to the PSOE archive and says only the July 2023
programme was located at its last check; that 2026 placeholder must not be
relabelled as a 2023 source. No approved 2023 candidature manifest or complete
document denominator exists. Draft PR #101 remains conflicting and has no
human review; PR #166 is a separate proposed integration of its editorial
gate. Neither resolves this document's identity, rights or coverage.

## Official-publisher discovery

| Observation on 2026-10-29 | Evidence | Limit |
|---|---|---|
| The PSOE [programme archive](https://www.psoe.es/transparencia/informacion-politica-organizativa/programa/) labels a link “Programa electoral – Elecciones generales julio 2023”. | The archive's 2023 general-election entry links to the [PDF URL](https://www.psoe.es/media-content/2023/07/PROGRAMA_ELECTORAL-GENERALES-2023.pdf). | An archive entry establishes a discovery path, not the current PDF's original publication date or byte identity. |
| The PSOE [programme announcement](https://www.psoe.es/actualidad/noticias-actualidad/programa-electoral-del-psoe-para-el-23j/) is dated 2023-07-07 and describes its linked PDF as the programme for the 23 July election. | The announcement links to the same PDF URL. | The article date belongs to the article; it is not independently verified as the publication date of the exact PDF bytes available today. |
| Opening that link through the web retrieval tool identified a PDF with 272 pages and a cover naming the 23 July 2023 general election. | Both publisher landing paths resolved to the same direct URL. | No private byte capture, SHA-256 comparison, page-level verification or review of the complete document was performed in this package. |

An independent HTTP/1.1 `curl -I -L` from this runner returned `200 OK` with
`Content-Type: text/html` and a short anti-bot response, not PDF headers.
Do not interpret that HTTP status as a successful source import. The web
retrieval and runner have different access paths; neither supplies a private
archive hash for the repository pipeline.

## Candidate inventory handoff, not a register mutation

- Election context: `es-gen-2023`; publisher: PSOE; candidate role: general
  programme; landing paths and direct URL: links above. The PDF's apparent
  language is Spanish, subject to document review.
- Leave candidature ID/applicability, exact source version, SHA-256, private
  archive reference, retrieval evidence, exact-byte publication date,
  replacement/annex search, authenticity and all reuse permissions unresolved.
  Do not copy values from the 2026 placeholder or fictional commitment data.
- Under the future reviewed P0 protocol, capture the bytes privately through
  an approved acquisition path, hash them, bind the publisher landing evidence
  to that version, check for annexes/replacements, and request separate human
  authenticity and rights decisions. The owner must first approve the 2023
  inclusion unit and document-to-candidature applicability.
- No source row, political summary, relationship, coverage percentage,
  `not stated` finding, quote permission or PDF was added to the repository.
  This one discovery cannot establish complete 2023 coverage.

## Validation and outstanding gates

Repository inspection and two official-publisher landing paths support the
discovery observation only. `git diff --check` validates this documentation
change; no software test can approve identity, rights, editorial meaning or
the 2023 denominator. Current GitHub CI runs on other PRs have jobs with zero
steps and a billing/spending-limit annotation, so their failure is not a test
result for this source. Reconcile this handoff with the reviewed P0 OpenSpec
design/tasks before implementing a source-register row. Owner and editorial
review remain pending.
