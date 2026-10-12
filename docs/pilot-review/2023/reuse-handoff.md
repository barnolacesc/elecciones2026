# PP/ERC source-specific reuse handoff — 2026-10-12

Roadmap package: **E1.4**. This is a decision brief, **not** a rights approval or publication authorization. The six reviewed candidate records remain outside the publish set.

## Verified public evidence and private recheck boundary

| Programme | Official publisher evidence | Registered direct PDF | Current HTTPS response and SHA-256 | Physical PDF locators |
|---|---|---|---|---|
| PP `src-2023-pp-v1` | [PP 23J announcement](https://www.pp.es/actualidad/articulos/programa-electoral-propone-365-medidas-reconstruccion-economica-social-e/) dated 2023-07-04, with a PDF link | `https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf` | HTTP 200, 8,214,497 bytes; `c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108` matches register | 34 (measure 91), 45 (measure 120, third bullet), 50 (measure 146) |
| ERC `src-2023-erc-v1` | [ERC electoral-programme archive](https://www.esquerra.cat/transparencia/programes-electorals/) links the 2023 Corts espanyoles programme | `https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf` | HTTP 200, 1,228,157 bytes; `760db25e48422b74a9b0c3172cab16cf39d010345849e50b921ff8bf61be2854` matches register | 114 (HABITATGE c, first bullet), 61 (SALUT c, fourth bullet), 128 (EDUCACIÓ c, fourth bullet) |

The registered version is the local `23J-v1` label, not a publisher-issued edition. The current bytes match the registered originals. The private archive is not available in this workspace, so this run **did not independently reverify** `original.pdf`, extraction hashes or the six visual page locators. The [inventory](inventory.json) and [review pack](README.md) retain those evidence references and their earlier checks. An authorized editor must run `private_archive verify` for both source IDs and visually recheck those six pages and adjacent qualifications in the private archive before changing source status to `verified`.

The PP announcement establishes programme presentation on 2023-07-04 and links a PDF, but it does not establish the publication date of the exact registered PDF bytes. ERC's archive update (2024-02-20) and PDF upload path are not publication dates. Neither PDF has a publisher-attested date for its exact registered version in the checked evidence. Both `publication_date` fields therefore remain null. The source owner must find primary publisher evidence for each exact PDF edition, or obtain an explicit editorial policy decision on how to represent an evidenced availability date without mislabelling it a publication date. The current required-date gate remains in force.

## Decisions required from the human rights owner

Record **one decision per source** in the private rights store, then put only its reference, real decision owner, date, scope and status in the source register. Content approvals and affiliation declarations are not these decisions. Proposed scopes below are requests, not agent decisions.

| Source | Proposed scope for decision | Decision owner | Decision date | Evidence reference | Current outcome |
|---|---|---|---|---|---|
| PP `src-2023-pp-v1` | Neutral, human-reviewed Spanish summaries and outbound official links only; no quotation, PDF hosting or extracted-text redistribution | Human source-rights owner: **not yet identified** | Pending | Pending private source-specific decision | `not_reviewed`; no publication |
| ERC `src-2023-erc-v1` | Neutral, human-reviewed Spanish summaries and outbound official links only; no quotation, PDF hosting or extracted-text redistribution | Human source-rights owner: **not yet identified** | Pending | Pending private source-specific decision | `not_reviewed`; no publication |

If the owner approves the proposed scope, the source status can become `link_only` with `reviewed_by`, `review_date`, `evidence_ref` and decision scope in `terms_notes`; the matching programme can become `verified_link_only` only after source identity, hash, date and coverage checks pass. A quote still requires `link_and_short_quote` or `public_domain` and matching `verified_quotation_permitted` programme rights. `permission_denied` and `not_reviewed` cannot enter the publish set.

## Content-review dependency

PR [#96](https://github.com/c2ventures/elecciones2026/pull/96) reports owner and `carlesfito` approval of the six unchanged #87 candidates. This branch incorporates those records, retaining owner-attested versus direct-review provenance. Each reported decision points to private evidence and a SHA-256 fingerprint of its exact statement wording, qualifications, source URL/version and locators. The actual review dates are **not recorded**; `reported_date` is 2026-10-12 and `review_date` is null. Do not promote to `approved` or infer `last_reviewed_date` until the dates and version-bound evidence are confirmed through the authorized editorial workflow. Do not repeat review solely because there is no direct GitHub comment. Any substantive wording or qualification change requires a new human approval for the changed fingerprint.
