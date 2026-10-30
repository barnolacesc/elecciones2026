# VOX 23J programme: source-discovery handoff

Roadmap package: **P0.12**, `2023-corpus-completion` (proposal-only).
Checked on 2026-10-30 against `origin/main` `8e2fab4`, the live GitHub PR/issue
list, and the URLs below. This is a candidate-document discovery note, **not**
a verified source, complete inventory, rights decision, political-content
review, or publication approval. No PDF bytes or programme text were copied
into the repository.

## Reconciled repository boundary

- `content/sources/register.json` contains four `es-gen-2023` pilot sources:
  PP, ERC, PNV and Sumar. None is a VOX 2023 row. All four pilot rights states
  are `not_reviewed`; the 2023 inclusion rule and candidature denominator
  remain unapproved.
- `src-2026-vox-v0` points to the VOX programme landing path but is explicitly
  an `es-gen-2026` missing-source placeholder. Its URL is **not** a 2023 source
  version or evidence that a 2026 programme exists. Keep the election IDs and
  any future source records distinct.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains open
  and conflicting with main. [PR #166](https://github.com/c2ventures/elecciones2026/pull/166)
  is a separate, mergeable integration candidate with failed CI and no reviews
  when checked. Neither PR supplies a VOX source/rights decision or approval
  for the 2023 corpus. Do not merge both as duplicate editorial gates.

## Candidate discovery evidence and limits

| Candidate | Observation on 2026-10-30 | What it does **not** establish |
|---|---|---|
| [VOX programme landing page](https://www.voxespana.es/programa/programa-electoral-Vox) | Search indexing returned an official-domain page titled “Programa Electoral de VOX 23J” whose excerpt describes a 23 July 2023 general-election programme and a download link. Direct GET and HEAD from this runner both returned HTTP 403. | No live page inspection, publication date, document version, candidature applicability or reuse permission. |
| [VOX-hosted PDF candidate](https://www.voxespana.es/wp-content/uploads/2023/07/Programa-VOX-2023-con-menos-peso.pdf) | Search indexing returned this official-domain PDF URL and a title identifying the 23J 2023 general-election programme. A HEAD request from this runner returned HTTP 403; the PDF was not downloaded. | No verified bytes, checksum, page count, text, date or rights. The `/2023/07/` path is not publication-date evidence. |
| [VOX 19 July 2023 article](https://www.voxespana.es/actualidad/equiparacion-salarial-mas-inversion-o-devolucion-de-competencias-son-algunas-de-las-medidas-en-materia-de-seguridad-y-defensa-de-vox-para-el-23j-20230719) | The official-domain indexed page identifies itself as a dated 23J campaign article and refers to an electoral programme. It is a corroborating discovery lead only; its political text was not extracted here. | The article date does not prove the PDF's publication date or that this PDF was the final/only applicable source. |

Search-result excerpts are discovery leads, not an immutable copy of the
publisher's page. The runner's 403 may be access control; it does not establish
that the links are dead. Conversely, indexing alone does not establish that the
current PDF bytes match any historical election version. No programme
position, quotation, source locator or absence claim follows from this note.

## Private review queue before any 2023 source row

1. Under an owner-approved 2023 inclusion rule, verify the exact VOX Congress
   candidature/list identity and constituency scope against the corrected BOE
   proclamation, then decide whether this national programme applies to each
   relevant list. Do not use `party_id` as a substitute for a candidature ID.
2. Recheck the publisher landing and direct PDF through an authorized access
   path. Record dated retrieval evidence, actual URL/redirects, immutable
   bytes and SHA-256 in the private archive. Search for annexes, revisions and
   replacements, retaining unresolved searches. Record a publication date
   only from adequate evidence; otherwise keep it unknown.
3. Ask the human source owner to decide authenticity and the rights owner to
   decide permitted uses for the **exact** source version. Linking, paraphrase,
   quotation and PDF redistribution are separate decisions. Keep review
   evidence and original bytes private.
4. Only after those gates, propose a separate `es-gen-2023` source record and
   coverage row for review. Topic extraction, `not stated`, cross-party
   relationships and public display require their own later P1 approvals.

This package changes no register, PDF, programme/statement/relationship record,
OpenSpec readiness flag, public output, routing or release gate. Passing a
technical check cannot replace owner, rights or editorial review.

## Validation record

Local Python assertions on 2026-10-30 passed for the four 2023 pilot IDs,
all four `not_reviewed` rights states, the distinct missing 2026 VOX
placeholder, and this handoff's candidate URLs and pending-access language.
`git diff --cached --check` passed. A direct GET and HEAD of the landing path
and HEAD of the candidate PDF returned HTTP 403. No PDF was downloaded; no
source, editorial, browser or release test is implied by this documentation
check. PR CI, if it runs, remains engineering evidence only.
