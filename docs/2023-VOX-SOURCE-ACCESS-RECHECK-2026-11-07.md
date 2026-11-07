# VOX 23J source access: publisher-to-byte handoff

Roadmap package: **P0.12-R** (`2023-corpus-completion`, proposal-only).
Checked on 2026-11-07 against `origin/main` `488b6f5`, the [earlier VOX
discovery](2023-VOX-SOURCE-DISCOVERY-2026-10-30.md), current official-domain
web results, and GitHub PR/CI metadata. This is an access-path audit, not a
source registration, authenticity decision, rights clearance, political-content
review, or claim that a publisher URL has permanently disappeared.

## Reconciled boundary

The 2023 register still has four pilot sources (PP, ERC, PNV and Sumar), all
`published-unverified`, with rights `not_reviewed` and unknown publication
dates. There is no 2023 VOX row or approved candidature denominator. The
`src-2026-vox-v0` placeholder is a different election and cannot be converted
into 2023 evidence. [PR #101](https://github.com/c2ventures/elecciones2026/pull/101)
is still an open, conflicting draft with no GitHub reviews; its older passing
checks do not bind or approve this source. [PR #166](https://github.com/c2ventures/elecciones2026/pull/166)
merged an independent integration on 2026-11-01. [PR #207](https://github.com/c2ventures/elecciones2026/pull/207)
contains a separate PR #101 integration audit, so this handoff does not edit
that gate.

## Access-path observations

| Path | 2026-11-07 observation | Evidence limit |
|---|---|---|
| [Official 23J news index](https://www.voxespana.es/elecciones-generales-23j) and its [7 July 2023 economic-programme article](https://www.voxespana.es/actualidad/bajada-radical-de-impuestos-drastica-reduccion-del-gasto-politico-ineficaz-simplificacion-de-tramites-asi-es-el-programa-economico-de-vox-para-el-23j-20230707) | The web retrieval path returned the index and article, both describing a 23J economic programme. The article's rendered links did not expose the candidate full-programme PDF. | The dated article is evidence of that article and a programme reference, not of the exact candidate PDF bytes or their publication date. It is not a substitute for the full programme. |
| [Programme navigation link](https://www.voxespana.es/programa/programa-electoral-vox) | The article's current site navigation points here, but direct web retrieval returned 404. An independent runner HEAD returned 403 HTML. | These different access results do not establish a permanent 404 or identify the 2023 document. The page may be blocked, changed or removed; status remains unresolved. |
| [Previously discovered PDF URL](https://www.voxespana.es/wp-content/uploads/2023/07/Programa-VOX-2023-con-menos-peso.pdf) | Search still exposes an indexed PDF rendition of a 23J programme, but reports its crawl as about 3.3 years old. Direct URL retrieval returned 404 through the web path; runner HEAD returned 403 HTML. | A cached rendition is not a fresh byte retrieval. No current hash, redirect chain, private archive copy, source version or rights decision was obtained. |

The two retrieval paths disagree on status, while the index can return stale
content. Do not promote the candidate URL to a verified source or treat access
failure as proof that VOX had no programme. The current article does not bind
the indexed PDF to a publisher landing-to-byte chain. No programme text or PDF
was downloaded into Git, and no policy position was extracted from the article.

## Private review handoff

1. Under an approved 2023 inclusion rule, identify the relevant Congress
   candidature(s) and separately review this document's applicability. The
   national party label alone does not settle constituency or coalition scope.
2. Ask the source owner to inspect the official page and candidate PDF through
   an authorized, working access path, retaining dated page-to-URL evidence,
   redirects, exact bytes/hash and a private archive reference. If the URL has
   changed, record the old and new locations without silently equating versions.
3. Search for a replacement, annex or publisher archive entry. Keep access
   failure, missing evidence and an actual reviewed negative finding distinct.
   Leave the exact-byte publication date unknown unless independently evidenced.
4. Obtain separate human authenticity and per-use rights decisions for the
   identified version before source registration or P1 content work. Neither
   a current article, cached PDF, browser success nor CI grants reuse rights.

No source register, approval, statement, relationship, coverage count, quiz,
public route or deployment was changed. Main [CI run 41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
failed at `488b6f5`; this audit does not waive or diagnose that unrelated gate.
