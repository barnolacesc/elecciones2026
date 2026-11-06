# PACMA 23J document: source-discovery handoff

Roadmap package: **P0.15 document discovery** (`2023-corpus-completion`, proposal-only). Checked on 2026-11-06 against `origin/main` `488b6f5`. This is evidence for a private inventory review, not an approved candidature, programme record, rights decision, topic search, political claim, or publication.

## Observed evidence

| Question | Evidence | Boundary |
|---|---|---|
| Is a 23J document linked by its publisher? | PACMA's [programme index](https://pacma.es/programa-electoral/) directly links [PACMA_PE_GENERALES_23J23.pdf](https://pacma.es/wp-content/uploads/2023/07/PACMA_PE_GENERALES_23J23.pdf) under its 2023 general-election entry. On 2026-11-06, the index returned HTTP 200 and the PDF returned HTTP 200 with `application/pdf` and a `%PDF-1.6` header. | A publisher link and PDF cover identify a *candidate* 23J document. They do not establish its complete scope, final version, publication date, applicable candidature, or permission to reuse text. The index also links other elections; do not substitute a municipal or autonomous programme. |
| Can these bytes be identified for later verification? | A streaming, no-file download of the linked PDF returned 1,123,643 bytes with SHA-256 `88e3f492dc2c6bcb0b904525d494313d63dad8ece524215156a88ab1d1b5b07d`. The response `Last-Modified` header was `Thu, 06 Jul 2023 19:17:15 GMT`. | This is a network-observed checksum, **not** an approved private archive hash or publication-date finding. Re-acquire and verify bytes in the authorised private store; HTTP metadata may change. No PDF bytes, extract, or political summary were committed. |
| Does the official election record settle the inventory unit? | The existing [BOE enumeration audit](2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md) identifies [BOE-A-2023-15828](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15828) as a correction that changes PACMA's Teruel Congress entry from `No proclamada` to a candidate list. | This is one corrected constituency entry, not a checked national PACMA manifest. Party, constituency candidature, Congress, and Senate are distinct units. The owner has not approved the inclusion rule or denominator. |
| Is this already in the repository's 2023 source register? | `content/sources/register.json` at `488b6f5` has four 2023 pilot rows (PP, ERC, PNV, Sumar), all `published-unverified` with rights `not_reviewed`; it has no PACMA 2023 row or approved candidature manifest. | Discovery does not change the register, coverage counts, or `denominator_unresolved` state. Absence from the pilot register is not a reviewed finding of absent programme coverage. |

## Private review handoff

1. Apply an owner-approved 2023 inclusion rule to a corrected, independently checked official candidature manifest. Map the PACMA document to each relevant Congress candidature only after the territorial and document-scope decision; keep Senate separate.
2. Re-acquire exact bytes into the authorised private archive, verify the checksum, record acquisition evidence, check landing-page provenance and other applicable versions or annexes. Leave publication date unknown until supported by evidence; neither the URL path nor `Last-Modified` is enough.
3. Route authenticity, link/paraphrase/quotation/redistribution rights, document applicability, topic-search scope, and editorial review to their separate human owners. A PDF link and hash do not authorise publication or establish `not stated` on any topic.
4. Only after those decisions, add a versioned source/discovery row and reconcile coverage against the approved denominator. Keep this document out of the public build and do not derive comparison or quiz content from it.

PR #101 is still open, draft, without human review, and conflicting with `main` as of this check. Its passing historical checks do not resolve the conflict or any editorial gate. This handoff does not modify PR #101's statement/schema scope or any open PR's source-discovery subject.
