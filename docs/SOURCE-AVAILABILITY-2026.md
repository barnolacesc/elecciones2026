# Election programme source check and versioned tracking — 2026-10-09

## Result

The [official election decree](https://www.boe.es/eli/es/rd/2026/10/05/806) confirms a Spanish general election on 29 November 2026. In this audit check, no complete **2026 general-election programme** was verified on the official party sources listed below. This is a bounded search result, not proof that no party has published one. The election was called on 5 October 2026. The official candidate list and final coalition names require a separate check after publication by the electoral authorities.

Do not use a 2023 general-election programme or a 2026 regional-election programme as a 2026 general-election programme. Do not convert a press statement into a programme without a separate content policy and clear public label.

Machine-readable tracking is maintained in the versioned source register at [`content/sources/register.json`](../content/sources/register.json), with schema definition at [`content/sources/register.schema.json`](../content/sources/register.schema.json).

## 2026 Candidacy and programme tracking register

The table below summarizes the tracked candidacies for the 2026 general election (`election_id: es-gen-2026`), their official discovery URLs, retrieval status as of 2026-10-09, rights review status, cryptographic hash, and replacement history.

| Formation / Party | Scope | Official discovery URL | Retrieval date | Publication status | Rights review | SHA-256 hash | Replacement history |
|---|---|---|---|---|---|---|---|
| PSOE | General | [PSOE Transparencia](https://www.psoe.es/transparencia/informacion-politica-organizativa/programa/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| PP | General | [PP Elecciones Generales](https://www.pp.es/categoria/elecciones-generales/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| VOX | General | [VOX Programa](https://www.voxespana.es/programa/programa-electoral-Vox) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| Movimiento Sumar | General | [Sumar 23J Archive](https://movimientosumar.es/programa-electoral-23j/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| ERC | General | [ERC Transparència](https://www.esquerra.cat/transparencia/programes-electorals/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| EAJ-PNV | General | [EAJ-PNV Documentos](https://www.eaj-pnv.eus/es/documentos/20945/con-voz-propia-programa-electoral-23-j) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| EH Bildu | General | [EH Bildu Oficial](https://ehbildu.eus/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| Junts per Catalunya | General | [Junts Oficial](https://junts.cat/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |
| BNG | General | [BNG Oficial](https://www.bng.gal/) | 2026-10-09 | `missing` | `not_reviewed` | None | None |

This is **not** a final candidacy inventory. Do not infer inclusion from the 2023 election. Check the official 2026 proclamations, then search each proclaimed candidacy and official coalition site. The official party site is the preferred primary source. A third-party index is only a discovery hint, not evidence for publication.

## 2023 Pilot rehearsal sources (Task 1.2)

Four historical 2023 programme records (`election_id: es-gen-2023`) are registered for technical rehearsal. The [2026-10-10 audit](PILOT-2023-AUDIT.md) rechecked PP and ERC PDF hashes but withdrew unsupported human and rights approvals. Task 1.2 remains open. PNV and Sumar retain earlier register entries; this audit does not verify their rights or editorial approvals.

| Formation / Party | Document title | Official URL / Direct PDF link | Retrieval date | Status | Rights review | Verified SHA-256 hash |
|---|---|---|---|---|---|---|
| Partido Popular (PP) | *Programa Electoral PP 23J* | [Direct PDF](https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf) via [PP Generales](https://www.pp.es/categoria/elecciones-generales/) | 2026-10-10 | `published-unverified` | `not_reviewed` | `c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108` |
| Esquerra Republicana de Catalunya (ERC) | *Programa Electoral 2023* | [Direct PDF](https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf) via [ERC Transparència](https://www.esquerra.cat/transparencia/programes-electorals/) | 2026-10-10 | `published-unverified` | `not_reviewed` | `760db25e48422b74a9b0c3172cab16cf39d010345849e50b921ff8bf61be2854` |
| EAJ-PNV | *Con voz propia. Programa Electoral 23-J* | [Direct PDF](https://www.eaj-pnv.eus/es/adjuntos-documentos/20945/pdf/con-voz-propia-programa-electoral-23-j) via [EAJ-PNV Documentos](https://www.eaj-pnv.eus/es/documentos/20945/con-voz-propia-programa-electoral-23-j) | 2026-10-09 | `verified` | `link_and_short_quote` | `46fec3a017cdc5c4e506fa5e228b97690071d5a03dfd3d8128392aa20f57d132` |
| Movimiento Sumar | *Un Programa para ti* | [Direct PDF](https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf) via [Sumar 23J Archive](https://movimientosumar.es/programa-electoral-23j/) | 2026-10-09 | `verified` | `link_and_short_quote` | `d5ccdac0d20f1b93a5f703f180d086041bd988835072dd5cb5d1378bf0195820` |

### Election scoping and isolation

The register enforces strict separation between elections:
- Every 2026 record has `election_id: "es-gen-2026"`.
- Every 2023 pilot record has `election_id: "es-gen-2023"`.
- The data validator and static build reject any comparison mixing sources from different election IDs. A 2023 source cannot appear in a 2026 comparison.

## Acquisition and tracking procedure

1. **Confirm candidature:** Confirm the 2026 candidacy and exact coalition name against official electoral publications in the *Boletín Oficial del Estado* (BOE).
2. **Search official channels:** Search the candidacy's official website, transparency archive, campaign website linked by that official website, and verified official announcement for a complete general-election programme.
3. **Register record:** Record the landing-page URL (`official_url`), direct document download URL (`direct_url`), publisher, publication date, retrieval date, scope, language, version label, SHA-256 hash, rights review, and replacement history in `content/sources/register.json`.
4. **Lifecycle status:**
   - `missing`: No programme published or found on official paths. SHA-256 and direct URL must be null.
   - `announced`: The party announced a programme, but complete text is not yet available.
   - `partial`: Only an excerpt, summary, or partial chapter is published.
   - `published-unverified`: A document is available but pending verification against official sources.
   - `verified`: Complete official programme verified on official channel, downloaded, and hashed.
   - `replaced`: Document superseded by a newer version or errata.
5. **Rights review and quotation boundaries (Package E0.2 / ADR-0002):**
   - Rights status must be one of: `not_reviewed`, `link_only`, `link_and_short_quote`, `public_domain`, `permission_denied`.
   - **Legal Framework:** Pursuant to Spanish intellectual property law (*Real Decreto Legislativo 1/1996, de 12 de abril, por el que se aprueba el texto refundido de la Ley de Propiedad Intelectual* - TRLPI, art. 32), the platform reproduces excerpts strictly under the statutory right of quotation (*derecho de cita*) for civic research, factual commentary, and public comparison.
   - **Prohibition of Full PDF Redistribution:** Hosting, mirroring, or redistributing full PDF documents is strictly prohibited. The platform provides outbound HTTPS links pointing directly to the official party download URLs.
   - **Quotation Limits:** Verbatim quotations extracted from verified sources must satisfy:
     - Maximum **40 words** per quotation.
     - Maximum **300 characters** per quotation.
     - Mandatory locators: non-empty `page` or `section`.
     - Strict operative policy substance (numerical targets, dates, fiscal percentages, administrative instruments); rhetorical slogans and campaign appeals are excluded.
   - **Pilot Sources:** PP and ERC quotation rights are `not_reviewed` after issue #42 removed unsupported generic approvals. No pilot claim or quote may be published until rights and two human reviews are documented. Existing PNV/Sumar register entries are outside this audit; their recorded status must not be treated as fresh approval evidence.
   - **Monitored 2026 Sources:** All nine monitored 2026 sources remain in `missing` and `not_reviewed` status. No quotations may be extracted or published until the complete official documents are retrieved, verified against SHA-256 hashes, and approved by editorial reviewers.
6. **Replacement history and invalidation:**
   - If a party releases a revised programme or errata, register the new version.
   - Mark the earlier version as `replaced`, and add a `ReplacementRecord` with `prior_version`, `superseded_by`, `replacement_date`, and `reason`.
   - Automatically invalidate dependent comparisons derived from the prior document in accordance with the editorial statements specification and ADR-0002.
7. **Cadence and integrity:**
   - Recheck official paths at a measured cadence and after public announcements. Avoid aggressive automated scraping.
   - Verify SHA-256 hashes offline. Reject oversized files (>50 MB) and do not execute embedded macros or scripts.

## Verification tooling

Run register validation via the Python tool:
```bash
python3 -m elecciones2026.source_register validate content/sources/register.json
```

Run test suite:
```bash
python3 -m unittest discover tests
```
