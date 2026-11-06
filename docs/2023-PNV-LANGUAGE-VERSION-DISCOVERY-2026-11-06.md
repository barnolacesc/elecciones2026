# 2023 EAJ-PNV language-version discovery — 2026-11-06

Roadmap package: **P0.1**, document inventory handoff under the proposal-only
`2023-corpus-completion` change. Election: `es-gen-2023`. This records a
publisher-hosted lead, not a verified additional programme, an approved
translation relationship, a rights decision, or a coverage count.

## Reconciled baseline

`origin/main` `488b6f5` has four 2023 pilot rows in
`content/sources/register.json`. `src-2023-pnv-v1` records the Spanish-language
EAJ-PNV landing page and PDF URL, a SHA-256 from the earlier private pilot,
`published-unverified` source status, `not_reviewed` rights, and a null
publication date. The register contains no Basque-language 2023 PNV row and
is not an owner-approved candidature or document denominator. Draft PR #101
concerns PP/ERC summaries, remains conflicting, and supplies no decision for
this PNV lead. The current-main CI run
[`41343879201`](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
failed in test and rendered-mobile jobs; it cannot establish source review.

## Publisher evidence observed on 2026-11-06

- The [Spanish EAJ-PNV document page](https://www.eaj-pnv.eus/es/documentos/20945/con-voz-propia-programa-electoral-23-j)
  returned HTTP 200 and labels itself a 23-J electoral programme. Its HTML
  links to the exact Spanish PDF URL already in the register. A HEAD request
  to that PDF URL returned `200`, `application/pdf`, and `Content-Length:
  3602932`.
- The site's [Basque-language page for document 20945](https://www.eaj-pnv.eus/eu/agiriak/20945/euskadiren-ahotsa-hauteskunde-egitaraua-u-23)
  returned HTTP 200, labels itself a U-23 electoral programme, and links to
  [a different Basque PDF URL](https://www.eaj-pnv.eus/eu/adjuntos-agiriak/20945/pdf/euskadiren-ahotsa-hauteskunde-egitaraua-u-23).
  A HEAD request to that PDF URL returned `200`, `application/pdf`, and
  `Content-Length: 3598169`.
- The pages share publisher document ID `20945`, but the PDF URLs and reported
  lengths differ. No PDF bytes were downloaded or committed in this audit.
  HTTP response headers, including `Last-Modified`, are not evidence of the
  original publication date or of the exact archived bytes.

## Private review queue and coverage boundary

1. The source owner should inspect and archive the Basque original privately,
   record its exact hash, publisher-to-file binding, date evidence, language,
   document role and replacement/translation relationship to the registered
   Spanish version. The shared page ID alone does not establish text
   equivalence, whether one version supersedes the other, or whether both
   belong in the approved inventory.
2. A human rights owner must decide permitted use for each exact version;
   the Spanish row's pending rights state cannot be copied to the Basque lead.
   Source authenticity, reuse rights and editorial interpretation remain
   separate decisions.
3. If the inclusion and document-scope rules admit both versions, review
   version-specific page locators, translation fidelity, topic search and
   deduplication before counting coverage or deriving any comparison. Do not
   count two language versions as two proposals by default, and do not infer
   topic absence from either unsearched document.

This handoff changes no source record, statement, relationship, spec approval,
rights state, public build or routing. The applicable P0 design/spec/tasks
remain draft; a human-reviewed inventory decision must precede implementation.
