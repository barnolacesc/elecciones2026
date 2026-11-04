# Coalición por Canarias 23J document-discovery handoff

Roadmap package: **P0.15**, `2023-corpus-completion` (proposal-only).
Checked on 2026-11-04 against `origin/main` `488b6f5`, the publisher pages
and HTTP response headers below. This is a source lead, not an approved
candidature, a complete programme inventory, an authenticated PDF version,
a rights decision, a political summary or permission to publish.

## Reconciled baseline

- `content/sources/register.json` has four `es-gen-2023` pilot rows (PP, ERC,
  PNV and Sumar). All four are `published-unverified`, have an unknown
  publication date and have rights `not_reviewed`. There is no Coalición
  Canaria 2023 row or approved 2023 candidature denominator. The nine 2026
  placeholder rows are a different election and cannot fill this gap.
- Open PR [#101](https://github.com/c2ventures/elecciones2026/pull/101)
  remains conflicting and unreviewed. Its current-main replacement
  [#166](https://github.com/c2ventures/elecciones2026/pull/166) merged on
  2026-11-01. Neither is evidence of this document's applicability or rights.

## Publisher evidence and version ambiguity

| Lead | Observation on 2026-11-04 | Boundary |
|---|---|---|
| [Publisher's agreements page](https://coalicioncanaria.org/acuerdos/) and [26 June 2023 article](https://coalicioncanaria.org/cc-firma-con-otras-10-fuerzas-politicas-el-manifiesto-un-objetivo-comun-la-defensa-de-canarias/) | The site labels the linked item a *Manifiesto Coalición Por Canarias Elecciones Generales Julio 2023*. The article describes a multi-organisation manifesto for 23J. | A manifesto is not automatically a complete electoral programme. Signing or supporting it does not, by itself, establish an officially proclaimed joint ballot list, document applicability to each list, or a party-wide position. |
| [PDF linked from agreements](https://coalicioncanaria.org/wp-content/uploads/2023/06/COALICION_POR_CANARIAS.pdf) | The web viewer identified a 14-page PDF with a 26 June 2023 date on its opening page. `HEAD` returned `200`, `application/pdf`, `Content-Length: 219682`, and `Last-Modified: Mon, 26 Jun 2023 10:44:09 GMT`. | The page date and server timestamp are leads, not a verified publication date or immutable historical byte identity. No bytes or page text were copied into this repository. |
| [PDF linked from the programme archive](https://coalicioncanaria.org/wp-content/uploads/cc-pdf/programas-electorales/00_COALICION%20POR%20CANARIAS.pdf) | The [archive page](https://coalicioncanaria.org/programas-electorales/) labels it `00_COALICION POR CANARIAS`; the web viewer identified 14 pages. `HEAD` returned `200`, `application/pdf`, `Content-Length: 221025`, and `Last-Modified: Thu, 20 Jul 2023 06:01:44 GMT`. | The two endpoints have different reported byte lengths. Do not treat them as the same version, a replacement chain, or independent documents without private byte/hash and publisher review. The archive's introductory copy refers to a 26 June election, so it cannot by itself establish the 2023 document's scope. |

The publisher article and PDF establish a **candidate document lead**, not
the full 2023 programme set or permission to paraphrase, quote or redistribute.
The archive listing and its later server timestamp do not prove when or why
the second PDF bytes changed. No topic search or policy-position extraction
was performed.

## Private P0 review handoff

1. Under an owner-approved 2023 rule, reconcile the corrected official
   Congress/Senate proclamation rows and constituencies with any Coalición
   Canaria, Coalición por Canarias, member-party or supporting-list identity.
   Review the manifesto's applicability to each list; do not infer one list
   or one document from the signatories.
2. Acquire both candidate PDFs only through the authorised private archive.
   Retain dated landing/direct URL and redirect evidence, exact byte hashes,
   page counts, source versions and any publisher explanation of the two
   endpoints. Search separately for other general programmes, territorial
   annexes and replacements; preserve unresolved leads. Do not infer a
   publication date from the URL, cover date or `Last-Modified` alone.
3. Have named humans decide source authenticity, document role and
   candidature applicability, then rights for linking, reviewed paraphrase,
   short quotation and PDF redistribution per exact version. P1 topic search,
   statement review and relationship review are separate gates.
4. Until those decisions and the full candidature manifest exist, retain
   `denominator_unresolved`. This lead creates no `not stated` conclusion,
   comparison, quiz item or public coverage percentage.

## Validation and limits

Publisher HTML and both PDF links were opened through the web viewer; both
PDF endpoints returned the `HEAD` metadata above from this workspace.
Repository assertions checked the four 2023 pilot rows and their pending
rights. `git diff --check` passed. No PDF bytes, private evidence, source
register row, political content, rights status, public build, routing or
deployment changed. Hosted CI and human editorial review are separate gates.
