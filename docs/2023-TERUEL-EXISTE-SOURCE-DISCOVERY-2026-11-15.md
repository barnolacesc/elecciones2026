# Teruel Existe 23J document discovery — 2026-11-15

Roadmap package: **P0.1 — Inventory and rights contract**
(`2023-corpus-completion`, proposal-only). Reconciled against `origin/main`
`d13ba68` and open PRs on 2026-11-15. This is a source-discovery handoff, not
an approved candidature, complete document inventory, rights decision,
political claim, topic-coverage finding or release. No PDF bytes or programme
text are stored in Git.

## Baseline and non-overlap

- `content/sources/register.json` contains four `es-gen-2023` pilot sources
  (PP, ERC, PNV, Sumar). Each is `published-unverified` with rights
  `not_reviewed`. There is no Teruel Existe 2023 source row or approved 2023
  inclusion denominator. A missing row is not evidence that no document exists.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  draft, conflicting with main and without a submitted review. Its successful
  October CI checks do not validate the current main integration or grant
  editorial/rights approval. [PR #238](https://github.com/c2ventures/elecciones2026/pull/238)
  separately audits its production-record-root conflict. This handoff does
  not edit PR #101, the source register, shared OpenSpec contracts or routing.
- [PR #244](https://github.com/c2ventures/elecciones2026/pull/244)
  records the unresolved 2023-first versus 2026-current delivery sequence.
  This discovery is election-scoped to 2023 and does not decide that sequence.

## Observed source leads

| Evidence | Observation | Limit |
|---|---|---|
| [BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066), Teruel / Congreso section | The proclaimed-list notice names `TERUEL EXISTE-Coalición EXISTE (EXISTE)` for Teruel. The same notice separately names `ARAGÓN EXISTE - COALICIÓN EXISTE (EXISTE)` in other constituencies. | The owner has not approved the inclusion unit or a party-to-coalition document mapping. Check subsequent corrections before final enumeration. |
| [Publisher's 23J programme page](https://teruelexiste.info/programa-elecciones-generales-23j/) | The Teruel Existe site labels the page for the general election and distinguishes its on-page summary from a linked complete programme. The page links the PDF below. | The summary is a separate web presentation, not proof that its wording or scope equals the complete PDF. Page availability does not grant reuse rights. |
| [Publisher-linked complete-programme PDF](https://teruelexiste.info/wp-content/uploads/2023/07/Programa_23J-2023-_Teruel_Existe_-elecciones-generales.pdf) | A HEAD request on 2026-11-15 returned HTTP 200, `application/pdf`, 392336 bytes, and `Last-Modified: Tue, 06 Aug 2024 08:18:09 GMT`. | HEAD metadata is not a file hash, verified version, publication date, proof of pre-election bytes, page-locator review, or licence. The 2024 server timestamp must not be used as the programme's publication date. |
| [Publisher's dated campaign article](https://teruelexiste.info/vivienda-frente-a-despoblacion-objetivo-programa-teruel-existe-medidas-facilitar-alquiler-y-compra/) | The site dates the article 15 July 2023 and refers to a programme for the 2023 general election. | The article does not establish that today's PDF bytes were available on that date, nor does it replace the complete document. No policy position is extracted here. |

## Private P0 review handoff

1. Apply the owner-approved inclusion rule to the corrected Congress
   candidature record. Resolve Teruel Existe versus Aragón Existe coalition,
   constituency and speaker scope; do not infer shared document applicability
   from the common `EXISTE` ballot abbreviation.
2. Privately capture the landing page and exact PDF bytes through an
   authorized route. Retain retrieval time, redirect chain, SHA-256, private
   archive reference, language, page count and source-version history. Seek
   dated evidence for pre-election availability and any annex/replacement;
   leave unsupported dates unknown.
3. Have the source owner review authenticity and document-to-candidature
   applicability, and the rights owner decide permitted use for each exact
   version. Review the web summary separately if it is ever used. Do not copy
   the PDF or extracted text into Git or the public build.
4. Only after P0 policy and evidence review, reconcile a source/coverage row.
   P1 exact-locator statement review, absence search, comparison relations
   and publication are independent later gates. Neither this lead nor a
   reachable PDF supports a `not stated` or completeness claim.

## Validation boundary

The publisher page-to-PDF link, BOE list label, dated article and HEAD response
were checked on 2026-11-15. Local register assertions confirm the four pilot
rows and absence of a 2023 Teruel Existe row; `git diff --check` passed. These
checks do not inspect the PDF, establish rights, approve the candidature rule,
or validate political content. CI is engineering evidence, not human review.
