# PSOE 23J source acquisition recheck — 2026-11-08

Roadmap package: **P0.11-A**, `2023-corpus-completion` (proposal only).
This rechecks the access gap in the [2026-10-29 discovery](2023-PSOE-SOURCE-DISCOVERY-2026-10-29.md). It does not acquire a PDF, verify a source version, decide rights, approve a candidature or change public content.

## Reconciled repository and PR baseline

- `origin/main` is `488b6f5`. `content/sources/register.json` still has four `es-gen-2023` pilot source rows (PP, ERC, PNV, Sumar), all `published-unverified`, all with rights `not_reviewed` and `publication_date: null`. There is no 2023 PSOE row or approved candidature/document denominator. The separate `src-2026-psoe-v0` placeholder cannot be reused as a 2023 source.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is draft and `CONFLICTING`/`DIRTY`, with no GitHub reviews. Its four successful CI jobs ran on 2026-10-12, before this main branch; the release job was skipped. They do not establish an integrated gate or human approval.
- [PR #113](https://github.com/c2ventures/elecciones2026/pull/113) is merged; its 2023-first roadmap and proposal-only OpenSpec boundary apply here. Open PRs #213 and #215 audit PP and VOX source access respectively; this package concerns PSOE's distinct acquisition failure and a generic state contract, not those records.

## Rechecked publisher path and acquisition outcome

On 2026-11-08 the PSOE [programme archive](https://www.psoe.es/transparencia/informacion-politica-organizativa/programa/) still listed “Programa electoral – Elecciones generales julio 2023”. Its link and the PDF link in the [2023-07-07 publisher announcement](https://www.psoe.es/actualidad/noticias-actualidad/programa-electoral-del-psoe-para-el-23j/) both resolved in the web source viewer to [the same direct URL](https://www.psoe.es/media-content/2023/07/PROGRAMA_ELECTORAL-GENERALES-2023.pdf). That viewer reported `application/pdf`, 272 pages. These observations establish a current discovery path in that viewer, not privately acquired bytes or the exact file's 2023 publication date.

From this runner, `curl` over HTTP/2 `HEAD` failed with `PROTOCOL_ERROR` (exit 92). An HTTP/1.1 range `GET` to the same direct URL returned `200 text/html`, 949 bytes, beginning with an HTML `NOINDEX, NOFOLLOW` page—not `%PDF`. The October discovery reported a similar HTML response. A successful status code therefore cannot be treated as successful PDF acquisition; the two access paths have different outcomes. No PDF body, hash, page locator, exact-byte chronology or rights evidence was captured in this PR.

## P0 review handoff

Keep candidate-document discovery, acquisition-attempt outcome, captured immutable version, publisher authenticity, chronology and use rights separate. For an authorised private acquisition, record method, timestamp, requested/final URL, response media type, byte signature, size and failure/challenge state. Only a verified PDF capture may receive a private archive reference and hash. If an alternate route obtains bytes, bind that exact version to the publisher link and review redirects/mirrors; do not infer equivalence from the URL or viewer metadata. Retain blocked attempts without converting them into `missing programme`, `not stated`, or a rights decision.

The owner/source reviewers must settle acceptable acquisition and identity evidence, recheck cadence, historical-version handling and authorised private storage under the approved inclusion rule. This PR changes only the draft OpenSpec contract and this audit. It does not alter source, statement, relationship, quiz, public build, deployment or routing records.
