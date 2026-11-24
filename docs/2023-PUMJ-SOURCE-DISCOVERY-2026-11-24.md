# PUM+J 23J programme source lead — 2026-11-24

Roadmap package: **P0.15**, `2023-corpus-completion`. This is a bounded
document-discovery handoff, not an approved 2023 inclusion decision, complete
inventory, source verification, rights finding, proposal extraction or release.
No source PDF or political answer was added to the repository.

## Reconciled repository boundary

At `origin/main` `d49454c` on 2026-11-24, the 2023 register contains four
`published-unverified` pilot rows (PP, ERC, PNV and Sumar), all with
`rights_review.status=not_reviewed`. Its eight 2023 example statements remain
six `under_review` and two `draft`. The register does not contain a PUM+J
2023 row. These counts describe repository records, not the eligible
candidature denominator or a complete document inventory.

Draft PR #101 remains open at `f8506a1` and GitHub reports a dirty merge. A
simulated merge against this main has seven conflict paths (review README,
reuse handoff, MVP tasks, generator, schemas, and two pilot tests). Its old
green checks do not test a resolved head or approve any 2023 record. This
discovery does not resolve or depend on that editorial PR.

## Primary-source observations

| Source checked 2026-11-24 | Observation | Limit |
|---|---|---|
| [BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066), Albacete Congress section | The proclaimed-candidature notice lists `POR UN MUNDO MÁS JUSTO (PUM+J)` under `CONGRESO DE LOS DIPUTADOS` in Albacete. The following Senate section is separate. | This is one constituency example, not a complete or corrected 2023 candidature manifest. The approved inclusion unit and all-territory reconciliation remain pending. |
| [Publisher-hosted programme PDF](https://www.porunmundomasjusto.es/wp-content/uploads/2023/07/Programa-Electoral-Por-Un-Mundo-Mas-Justo-Elecciones-Generales-2023.pdf) | Web retrieval returned a 39-page PDF. Its cover identifies a 2023 general-election programme and PUM+J. | A current retrievable PDF and URL path do not prove the exact bytes were available in 2023, establish its publication date, completeness, rights or candidature applicability. No private byte capture or hash was performed. |
| [BOE corrections 15548](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15548) and [15828](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15828) | Text searches for `MUNDO MÁS JUSTO` returned no match in these two known correction notices. | This narrow search is not a finality check for all later corrections or judicial changes. |

The party's [campaign archive](https://www.porunmundomasjusto.es/elecciones/)
was search-indexed but returned HTTP 403 to this web retrieval. Do not claim a
verified landing-to-PDF link from it. The direct publisher PDF is therefore a
lead requiring a separately evidenced acquisition chain.

## Review queue, not a promoted source row

1. Under the owner-approved 2023 inclusion rule, reconcile PUM+J Congress
   entries by constituency against the full BOE notice, corrections and any
   later official changes. Keep Congress and Senate units separate; do not
   infer one national candidature row from a shared ballot label.
2. Obtain a dated publisher landing/link observation or another approved
   authenticity chain. Capture the exact PDF bytes in the private archive,
   record SHA-256, retrieval evidence, language, version and page mapping;
   search for annexes and replacements. Do not put the PDF or extracted text
   in Git or the static build.
3. Have the designated humans decide document role/applicability, authenticity,
   exact-byte publication-date evidence and permitted link, summary, quotation
   and redistribution uses separately. Keep unknown dates and rights pending.
4. Only after the P0 inventory and rights gates, pass the relevant source
   scope to the P1 proposal/search review queue. No topic absence or party
   position follows from this discovery.

Validation: inspected the linked BOE sections, two known correction notices,
the publisher-hosted PDF cover and retrieval page count; checked the four-row
register and eight statement examples locally. No PDF bytes, claims, rights
or reviewer marks were changed. CI is engineering evidence only.
