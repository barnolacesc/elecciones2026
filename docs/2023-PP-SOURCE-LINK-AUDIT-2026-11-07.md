# PP 23J publisher-link and byte-identity audit

Roadmap package: **P0.4** (`2023-corpus-completion`, proposal-only).
Checked on 2026-11-07 against `origin/main` `488b6f5`, the open PR/issue
list, and the PP-hosted URLs below. This is a dated technical observation, not
a historical-version certification, rights decision, political-content review,
complete document inventory, or publication approval. No PDF bytes or text
were committed.

## Reconciled boundary

- The 2023 source register has four pilot rows (PP, ERC, PNV, Sumar), all
  `published-unverified`, with `publication_date: null` and
  `rights_review.status: not_reviewed`. The approved candidature denominator
  and complete document inventory remain open. In particular,
  `src-2023-pp-v1` records a `/storage/2023/07/` PDF URL and SHA-256
  `c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108`.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  draft and conflicting, with no GitHub reviews. Its 2026-10-12 passing checks
  do not test integration with current main or satisfy source, rights or
  editorial gates. [PR #207](https://github.com/c2ventures/elecciones2026/pull/207)
  separately audits that integration; this package does not alter it.
- Current-main [CI run 41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
  reports failures in the test and rendered-mobile jobs. This source audit
  neither attributes those failures to PP evidence nor claims a green baseline.

## Publisher and byte observations

| Evidence | Observation on 2026-11-07 | Limit |
|---|---|---|
| [PP's dated 23J programme article](https://www.pp.es/actualidad/articulos/programa-electoral-propone-365-medidas-reconstruccion-economica-social-e/) | HTTP 200; the page displays 04 JUL, 2023 and currently links its “Programa electoral 23J” document to the `/wp-content/uploads/2023/07/` URL below. | The article date describes the article and programme presentation, not a verified publication date for today's exact PDF bytes. |
| [Article-linked PDF](https://www.pp.es/wp-content/uploads/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf) | HTTP 200, `application/pdf`, PDF header, 8,214,497 bytes, SHA-256 `c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108`. | Current availability and byte identity only; not a historical capture or reuse grant. |
| [Registered direct PDF](https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf) | HTTP 200, `application/pdf`, PDF header, 8,214,497 bytes, the same SHA-256 as the article-linked PDF and register. | The two current URLs return matching bytes; this does not establish that either path served those bytes in July 2023. |

The current publisher article provides a direct landing-to-document link for
the article-linked path, and both current PDF paths match the registered hash.
Do **not** replace `publication_date: null`, change `published-unverified`,
grant link/summary/quote/redistribution rights, or approve any PP statement
from this observation. The PDF URLs are source references, not files to serve
from this repository.

## Private review handoff

1. Capture the landing page and exact PDF in the approved private evidence
   store, with retrieval time, redirects, digest, and a stable capture reference.
   Determine whether a dated historical capture can bind the exact digest to
   the 2023 publication period. Keep the date unknown if it cannot.
2. Search for relevant annexes, corrections and replacements under the
   owner-approved 2023 inclusion/document rule. Do not infer completeness from
   one article or two byte-identical paths.
3. Ask the human source-authenticity owner to decide version identity and the
   rights owner to decide each permitted use of that version. Statement
   locators, neutral summaries and comparison relations require separate
   editorial review. Keep PR #101 integration and release as distinct gates.

Evidence method: inspected the current article HTML link and date marker;
streamed both publisher PDFs in memory with a 20 MB limit, checking status,
content type, PDF header, byte count and SHA-256. Inspected the main-branch
register, PR #101 reviews/status, open PRs/issues and main check runs. No
programme text was extracted, no public artifact or source record changed,
and the current observation was not silently promoted to approval.
