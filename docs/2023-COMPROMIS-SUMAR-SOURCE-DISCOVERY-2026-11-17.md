# Compromís–Sumar 23J source lead — 2026-11-17

Roadmap package: **P0.1**, `2023-corpus-completion` (proposal-only source
discovery). Election: `es-gen-2023`. This note records publisher-linked leads,
not an approved candidature, source, rights decision, comparison or publication.
No PDF bytes or political statements are copied into the repository.

## Reconciled boundary

- `origin/main` is `d13ba683` at this check. Its 2023 source register has four
  pilot rows: PP, ERC, PNV and Sumar. All four are `published-unverified`, have
  `rights_review.status=not_reviewed` and `publication_date=null`. The Sumar row
  points to Movimiento Sumar's general 23J programme, not to the separate
  Compromís–Sumar campaign page below. These rows are not a complete or
  owner-approved 2023 candidature/document denominator.
- Draft PR #101 remains open without GitHub reviews and reports `DIRTY` against
  current main. Its 2026-10-12 checks do not test the combined tree. A local
  `git merge-tree --write-tree origin/main origin/pr-101` on 2026-11-17 reports
  six conflict paths (review README, reuse handoff, MVP tasks, generator, and
  two pilot tests). This source lead does not resolve that PR or its human gates.
- Open PRs #211 and #220 concern Sumar's general source link and a PSC document
  boundary, respectively. This note concerns a distinct Compromís–Sumar 23J
  campaign source; it does not change the Sumar register row or assume that a
  coalition member receives its own comparison entry.

## Publisher-linked evidence checked on 2026-11-17

| Lead | Observed fact | Limit |
|---|---|---|
| [Compromís–Sumar 23J campaign page](https://sumar.compromis.net/cas) | The page identifies a 23J electoral programme and links separate Valencian and Castilian downloads. HTTP HEAD returned `200` and `text/html`. | Current availability does not establish the original 2023 publication date, the exact historical edition or rights to reuse text. |
| [Castilian download](https://sumar.compromis.net/docs/programa-cas.pdf) | The campaign page's Castilian link leads to this PDF; HTTP HEAD returned `200` and `application/pdf`. | No private acquisition, hash, page audit, equivalence review or reuse decision was performed here. |
| [Valencian download](https://sumar.compromis.net/docs/programa-val.pdf) | The same page links this separate PDF; HTTP HEAD returned `200` and `application/pdf`. | It must not be silently substituted for, or counted twice with, the Castilian edition. Translation/edition equivalence is pending. |
| [Movimiento Sumar general 23J page](https://movimientosumar.es/programa-electoral-23j/) | A distinct publisher page for the already registered Sumar pilot source remains available. | Neither page alone establishes whether one document supplements, replaces or is inapplicable to a particular ballot list. |

The `sumar.compromis.net` page is the publisher campaign landing page for this
lead. Its programme links are stronger discovery evidence than a search snippet,
but an official-domain link is not a source-use grant. The similarly named
[Compromís 28M programme](https://28m.compromis.net/programa) is labelled for
the 2023 regional/local election campaign; do not import it as a 23J programme
without separate election-specific evidence.

## Review handoff before any register or coverage change

1. Reconcile the exact 23J Congress ballot-list name, constituencies and
   coalition/member attribution against the approved P0 inclusion rule and
   official corrected candidature enumeration. Do not infer inclusion from the
   campaign domain or a candidate shown on its page.
2. Record the two download links as candidate document/edition rows, then
   acquire only through the approved private archive workflow. Bind retrieval
   time, bytes and SHA-256; check source authenticity, historical publication
   chronology, language, document role, scope and any replacement relation.
3. Obtain a source/version-specific human rights decision, with evidence, for
   each intended use. Keep `not_reviewed` until then; a HEAD response, link or
   checksum cannot authorize paraphrase, quotation or redistribution.
4. Decide with the editorial owner whether this is a distinct territorial
   supplement to the general Sumar programme, an alternative edition or an
   inapplicable source for a given candidature. Only an approved document join
   can affect the P0 coverage register or P1 topic-search denominator. No
   absent position or comparison follows from this discovery.

This handoff adds no source row, PDF, extracted text, statement, relationship,
review mark, public page, routing change or release approval. Its links and
HTTP observations are discovery evidence only; CI cannot settle the pending
identity, rights or editorial decisions.
