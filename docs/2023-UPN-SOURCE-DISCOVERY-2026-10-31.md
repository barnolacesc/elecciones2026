# UPN 23J programme: source-discovery handoff

Roadmap package: **P0 document discovery** (`2023-corpus-completion`, proposal-only). Checked 2026-10-31 against `origin/main` `8e2fab4`. This is a lead for private source review, not an approved candidature, source record, rights decision, extraction, or publication.

## Observed evidence and limits

| Question | Evidence observed | Limit |
|---|---|---|
| Is there a publisher-hosted 23J document lead? | A [PDF on `www.upn.org`](https://www.upn.org/wp-content/uploads/2023/07/Programa-Generales-23J_V2-1.pdf) was returned by the web source viewer as `application/pdf`, six pages, with a cover identifying the 23 July 2023 general election. | The web viewer's rendering does not establish an archived byte hash, the publisher's publication date, a revision history, completeness, or reuse rights. The `2023/07` URL path and `V2-1` filename are not date/version decisions. No PDF bytes or extracted text were added to Git. |
| Is the election context independently visible on the party site? | [UPN's dated 13 June 2023 article](https://www.upn.org/el-consejo-politico-de-upn-aprueba-las-listas-de-candidatos-al-congreso-y-al-senado/) says its party council approved lists it intended to present for Congress and Senate on 23J. | Party intent is not an official proclamation or the project's approved inclusion rule. The article does not establish that this PDF was the final programme of an officially proclaimed candidature. |
| Could another 2023 programme be confused with this lead? | UPN's current [“Posición sobre temas” page](https://www.upn.org/posicion-sobre-temas/) links “Ver Programa Elecciones 2023” without identifying the general election in that link label. | Do not infer that this link resolves to the 23J general-election PDF, or substitute a 2023 foral/municipal programme. Resolve exact document identity and any additional applicable documents during private review. |
| What does the repository register? | `content/sources/register.json` contains four 2023 pilot rows (PP, ERC, PNV, Sumar), all `published-unverified` with rights `not_reviewed`; it has no UPN 2023 row or approved candidature manifest. | Four pilot rows are not the eligible-candidature denominator. This lead does not change any coverage count or imply that UPN has been omitted under an approved rule. |

An attempted independent HTTP `HEAD` check on 2026-10-31 could not resolve `www.upn.org` from this workspace (`curl: (6) Could not resolve host`). The web source viewer did open the URL; no response headers, size, checksum, or local archive verification are claimed here. Preserve this distinction when reviewing the lead.

## Private review handoff

1. Under a human-approved 2023 inclusion rule, match the exact officially proclaimed candidature and constituency scope to UPN; distinguish party, list, coalition, Congress and Senate units. Record the official enumeration evidence and an explicit disposition if the document's applicability is narrower than the candidature.
2. Verify the PDF's publisher path and landing-page provenance, obtain exact bytes into the authorised private archive only, record acquisition time and SHA-256, and check whether a prior or replacement version exists. Do not infer a publication date from a URL directory, file name, or the 13 June article.
3. Have the designated humans decide authenticity, rights for each proposed use, document applicability, and source/topic review scope independently. A link to an official host does not authorise quotation, redistribution, a neutral summary, or a relationship with another party's statement.
4. Only after those decisions, reconcile a candidature-to-document row and coverage status against the complete manifest. Until then, retain `denominator_unresolved`; an unsearched topic is not `not stated` and no comparison or quiz item may be derived from this lead.

PR #101 remains open, conflicting with current main and without a human review. PR #166 proposes its separate integration path. Neither PR nor this discovery establishes a rights or editorial release gate. Recent hosted CI jobs have failed before executing steps because of the GitHub account billing/spending-limit block; local document validation is the engineering evidence for this handoff, not passing hosted CI.
