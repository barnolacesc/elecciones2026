# PSC-PSOE 23J document-applicability handoff

Roadmap package: **P0.3** (`2023-corpus-completion`, proposal-only).
Election: `es-gen-2023`. Checked on 2026-11-09 against `origin/main`
`488b6f5`, the publisher pages and BOE record linked below, open PR #101,
and the main CI run `41343879201`. This is a narrow source-discovery and
identity handoff, not an approved candidature mapping, document inventory,
rights decision, topic search, editorial review or release.

## Observed evidence and its limit

| Evidence | Observation | Does not establish |
|---|---|---|
| [BOE-A-2023-18907, Congress table II](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907) | The results table labels PSOE and `Partit dels Socialistes de Catalunya (PSC-PSOE) (PSC)` separately. | Whether the product should use one or two actor records, or which programme applies to either result label. The corrected proclamation and result-row mapping remain to be reviewed under the [results cross-check draft in PR #205](https://github.com/c2ventures/elecciones2026/pull/205). |
| [PSC 2023 general-election lists](https://www.socialistes.cat/transparencia/informacio-organitzativa-i-politica/les-nostres-llistes/eleccions-generals/) | The PSC publisher page has a `23 de juliol de 2023` section and Congress lists for Catalan constituencies. | A 23J programme, its publication date, or adoption of another publisher's document. A candidate-list page is not a programme. |
| [PSC general-election programme history](https://www.socialistes.cat/historia/eleccions/generals/) | The observed index lists 2019 and older programme links; it does not display a 2023 entry. | Proof that no 2023 PSC document exists. This page alone is not an exhaustive archive search. |
| [PSOE 23J programme announcement](https://www.psoe.es/actualidad/noticias-actualidad/programa-electoral-del-psoe-para-el-23j/) | The PSOE page dated 2023-07-07 links a PDF described as its 23 July general-election programme. | PSC-PSOE applicability, exact PDF-byte identity, source-use rights, or a distinct PSC annex. See the [PSOE discovery handoff](2023-PSOE-SOURCE-DISCOVERY-2026-10-29.md); PR #216 separately drafts an acquisition-attempt gate. |
| [PSC page titled `Programa Electoral 2023-2027`](https://www.socialistes.cat/actualitat/programa-electoral-2023-2027/) | This publisher page is dated 2023-05-25 and explicitly discusses Castelldefels as a city. | A 23J Congress programme. The title/year alone must not make this municipal material a general-election source. |

The checked `content/sources/register.json` contains four 2023 pilot rows
(PP, ERC, PNV and Sumar), with no 2023 PSC-PSOE or PSOE row. Its 2026 PSOE
placeholder is a different election and cannot fill this gap. The ten-party
product target is not an approved 2023 candidature denominator. This handoff
does not change a source, coverage, statement or relationship record and does
not claim a negative topic finding.

## Review handoff

1. Under the owner-approved inclusion rule, reconcile corrected official
   Congress candidature and result labels to product actors. Retain the
   PSC-PSOE/PSOE distinction until a human-reviewed mapping resolves it; do
   not infer shared programme applicability from a name or electoral result.
2. Search the PSC and PSOE publisher paths for a 23J-specific PSC document,
   annex, adoption statement or replacement. Record search scope and dated
   negative findings privately; this spot check is not an absence conclusion.
3. For each candidate document, review publisher-to-bytes identity, version,
   date, constituency/document scope, private archive hash and permitted uses
   independently. A PSOE programme link does not grant PSC attribution or
   quotation/republication rights.
4. Only then decide whether source rows and topic searches are needed for one
   or more reviewed actors. Keep unresolved applicability visible; do not
   duplicate a PSOE position under PSC or count the same document as two
   independent programmes without an approved attribution rule.

PR #101 remains draft and conflicting; its 2026-10-12 passing checks predate
current main and cannot resolve this mapping. PR #219 separately audits its
supersession, so this handoff does not edit that PR or its records. Main run
[41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
failed in the pytest and browser-quiz steps; no current green CI or human
review is inferred. No PDF or political answer was copied into this repository.
