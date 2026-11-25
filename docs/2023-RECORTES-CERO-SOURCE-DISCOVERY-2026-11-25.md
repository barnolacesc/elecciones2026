# Recortes Cero 23J source-access lead — 2026-11-25

Roadmap package: **P0 source discovery** (`2023-corpus-completion`, proposal-only).
This is a bounded inventory handoff, not an approved inclusion decision, source
record, rights grant, programme review, coverage finding or publication step.

## Reconciled boundary

`origin/main` at `d49454c` has four `es-gen-2023` source rows (PP, ERC, PNV,
Sumar), each with `rights_review.status: not_reviewed`. It has no Recortes Cero
2023 row or approved 2023 candidature denominator. The open PR queue includes
other party-specific discovery leads; this handoff does not edit those files.
[PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is still a
draft, conflicting with main, with no human reviews. Its October passing CI
checks do not settle today's source identity, rights or editorial review.

## Evidence observed on 2026-11-25 (UTC)

| Evidence | Observation | Limit |
|---|---|---|
| [BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066) | The official proclamation includes `RECORTES CERO (RECORTES CERO)` among Congress lists, including an entry under the Barcelona electoral board. | An occurrence in the proclamation is not an approved project inclusion rule, complete province list or document-to-list applicability decision. |
| [Publisher-hosted indexed PDF URL](https://recortescero.es/wp-content/uploads/2023/07/PROG.-23J_05.pdf) | Search indexing identifies a PDF titled “Programa electoral Elecciones Generales 23J - 2023” at the publisher domain. | The indexed result is a discovery lead, not proof of current bytes, original publication date, completeness, rights or a live source. The `/2023/07/` path is not date evidence. |
| Publisher-domain HTTP check | The domain home page returned `200 text/html`; both `HEAD` and `GET` for the indexed PDF path returned `404 text/html` from this runner. | A 404 for this path is not proof that no programme exists or that no authorized archive can supply it. No PDF was downloaded, hashed or read. |

This is a particularly useful access distinction: a search-indexed official-domain
URL is **not** a currently retrievable PDF. Do not promote it to `verified`,
set `publication_date`, assign a hash, infer any political position, or mark
an absent topic from this observation.

## Private review handoff

1. Apply the human-approved 2023 inclusion rule to the exact Congress
   candidature/list unit. Check the corrected proclamation and territorial
   scope; do not equate a party label with all its lists.
2. Ask the source owner to locate a current publisher landing path or an
   authorized historical copy. Record retrieval/redirect evidence, exact bytes,
   SHA-256, language, version, potential annexes/replacements and a private
   archive reference. Preserve the failed URL as a dated discovery attempt.
3. Obtain distinct human authenticity and use-rights decisions for that exact
   version. Linking, neutral summary, quotation and redistribution are separate
   uses. Only then consider a reviewed source-register row and later P1 topic
   search, statement and comparison work.

No source, PDF, political claim, review mark, rights state, public output or
routing changed. `git diff --check`, a repository-boundary assertion and the
HTTP status check validate this note's technical observations only; they do
not constitute editorial review or source permission.
