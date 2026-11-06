# Frente Obrero 23J: document-role discovery handoff

Roadmap package: **P0.16**, `2023-corpus-completion` (proposal-only).
Observed 2026-11-06 against `origin/main` `488b6f5`. This is a bounded
source-discovery audit, not an inclusion, source-authenticity, rights, editorial
or publication decision. No programme bytes or political positions are stored
in this repository.

## Reconciled boundary

- `content/sources/register.json` has four `es-gen-2023` pilot rows (PP, ERC,
  PNV, Sumar), all with `not_reviewed` rights. It has no Frente Obrero 2023
  row. The 2023 inclusion rule and candidature denominator remain unapproved.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is open,
  conflicting with current main and has no GitHub reviews. Its old green CI
  predates main and does not review this candidature or source. The latest
  checked main CI run, [41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201),
  failed; passing checks would not supply editorial approval in any case.
- Other open P0 source-discovery PRs address different publishers. This note
  does not amend the source register, their findings or PR #101's records.

## Evidence and the false-positive risk

| Evidence | Observation | Limit |
|---|---|---|
| [BOE-A-2023-15066](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-15066) | The 2023 proclaimed-candidature notice contains **FRENTE OBRERO (FO)** under `CONGRESO DE LOS DIPUTADOS`, for example in the Alicante section. | This is one candidature lead, not a reconciled constituency manifest or approval of the final inclusion rule. Corrections and constituency scope still need review. |
| [Publisher's current programme page](https://frenteobrero.es/nuestro-programa-2/) | The publisher calls its download a *programa político*. On 2026-11-06 its link resolved to a [PDF under `/2026/10/`](https://frenteobrero.es/wp-content/uploads/2026/10/Programa.pdf). Local HEAD returned `200`, `application/pdf`, 1,202,338 bytes for that URL. | The current page and URL path do not establish a 2023 election document or a 2023 publication date. The file was not downloaded, hashed or archived here. |
| [Current publisher PDF](https://frenteobrero.es/wp-content/uploads/2026/10/Programa.pdf) | Browser extraction of PDF page 6 reports the document's own qualification: “no pretende ser un programa electoral”. | Text extraction is a discovery signal, not a visual review or a rights decision. It does not prove that no separate 23J document existed. |

The current publisher download must **not** be silently mapped to a 23J
electoral programme. A political programme, a later revision, and an election
programme are distinct possible document roles. Nor does failure to find a
23J file in this bounded check justify `not stated`, opposition, or a claim
that no such file exists.

## Private review queue

1. Under the owner-approved inclusion rule, reconcile FO's exact 2023
   Congress candidature names and constituencies against BOE proclamations,
   corrections and, if needed, certified results. Keep the denominator pending.
2. Search publisher-controlled 2023 archives and dated campaign entry points
   for an election-specific file, territorial document, or statement. Record
   search paths and unresolved access; do not substitute the current programme.
3. For every candidate document, privately preserve landing-to-file linkage,
   retrieval/redirect evidence, immutable bytes/hash, version, publication-date
   evidence or unknown, document role and candidature applicability. A human
   decides authenticity and relevance to 23J.
4. Obtain separate human decisions for outbound linking, paraphrase, quotation
   and redistribution for the exact version. Only after those gates propose a
   reviewed `es-gen-2023` inventory/coverage record. P1 topic search,
   statements and comparisons have separate review gates.

No source row, PDF, political statement, coverage conclusion, public artifact,
routing, merge or release was changed by this package.
