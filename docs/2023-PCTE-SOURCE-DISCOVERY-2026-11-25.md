# PCTE 23J document-role source lead — 2026-11-25

Roadmap package: **P0 inventory and document-role handoff** under the
proposal-only `2023-corpus-completion` change. This is discovery evidence, not
an inclusion decision, verified source record, rights grant, reviewed claim or
release approval. No PDF bytes, extracted political text or personal answers
were added to Git.

## Reconciled repository boundary

At `origin/main` `d49454c` on 2026-11-25, `content/sources/register.json`
contains four `es-gen-2023` pilot source rows: PP, ERC, PNV and Sumar. All are
`published-unverified` with `rights_review.status=not_reviewed`. There is no
PCTE 2023 source row. This is a count of repository records, not a complete
eligible-candidature denominator. The owner-approved 2023 inclusion unit,
document-role rule and rights decisions remain open in
`openspec/changes/2023-corpus-completion/tasks.md`.

Draft [PR #101](https://github.com/barnolacesc/elecciones2026/pull/101) is
still open and conflicting at `f8506a1`, with no recorded review decision.
Its October passing checks neither test integration with current `main` nor
approve a 2023 record. This PCTE lead is independent of that pilot-summary PR.

## Primary-source observations

| Source inspected on 2026-11-25 | Observation | Boundary |
|---|---|---|
| [BOE-A-2023-15066, Asturias Congress section](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066) | The proclaimed-candidature notice lists `PARTIDO COMUNISTA DE LOS TRABAJADORES DE ESPAÑA (PCTE)` in the Asturias `CONGRESO DE LOS DIPUTADOS` section (BOE p. 90011). | One proclaimed constituency entry does not establish the full territorial manifest or the approved inclusion unit. The same notice marks the Castellón Congress PCTE list `No proclamada` (p. 90064); do not count every occurrence as a proclaimed candidature. |
| [PCTE 23J announcement](https://www.pcte.es/notas-de-prensa/el-pcte-estara-presente-en-mas-de-una-treintena-de-provincias-el-23j/) | The publisher's page, displaying 28 June 2023 and a later 2024 update stamp, says the party expected 33 constituencies and a pending Castellón claim. | The party's aggregate is a claim, not a checked BOE enumeration or evidence that the Castellón list was later proclaimed. The page does not bind an exact document version or hash. |
| [PCTE-hosted *Programa de lucha 2023–2027* PDF](https://www.pcte.es/wp-content/uploads/2023/07/PROGRAMA%20DE%20LUCHA%202023-2027.pdf) | Its cover identifies July 2023. Its introduction explicitly says it is **not** an electoral programme, while saying it was presented in connection with the 23 July election. | A current publisher-hosted file is a relevant document-role candidate, not automatically a 23J electoral manifesto. The cover month and URL path do not prove the exact bytes were public before voting day. No local capture, hash, publisher-link chain or rights review was performed. |
| [PCTE-hosted May 2023 electoral PDF](https://www.pcte.es/wp-content/uploads/2023/05/PROGRAMA_ELECTORAL_PCTE_MAYO_2023.pdf) | Its cover identifies the **28 May municipal and regional** elections. | Do not silently import this different-election document as the 23J programme. Any cross-election applicability needs an explicit human decision and evidence. |
| [BOE correction 15548](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15548) and [correction 15828](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15828) | Correction 15548 changes a PCTE **Cuenca Senate** candidate-list numbering; a text search of correction 15828 returned no `PCTE` match. | This narrow check does not settle the Castellón claim, other subsequent changes or the complete Congress manifest. Keep chambers and constituencies separate. |

The quoted classification in the July PDF is the publisher's own document-role
statement, not an editorial judgement about the party's positions. No policy
proposal, party comparison or absence finding was derived from these sources.

## Review queue before a source-register row

1. Under the approved inclusion rule, reconcile PCTE Congress entries in the
   full proclaimed notice, corrections and any later official changes by
   constituency. Resolve Castellón with official evidence; do not substitute
   the publisher's aggregate for that check.
2. Decide whether the July *programme of struggle* is an eligible 23J source,
   a contextual document, or another role; keep the May municipal/regional PDF
   separate. Search for relevant annexes, editions and replacement documents.
3. If an eligible source is found, retain a publisher landing-to-document
   chain, exact bytes and SHA-256 in the private archive, retrieval/version
   evidence, and separately reviewed publication chronology. Do not infer
   pre-election availability from a file path or cover month.
4. Obtain independent human decisions for authenticity, permitted linking,
   neutral summaries, quotations and redistribution. Only then can source
   coverage and P1 proposal extraction be considered. No topic absence or
   public claim follows from this lead.

Validation: checked the linked BOE Congress sections and corrections, the
publisher page, both PDF covers and the July PDF introduction; reconciled
the four current 2023 register rows and PR #101 status. This audit changes no public artifact
or editorial record. CI can check document integrity, not human review.
