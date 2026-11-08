# Junts 23J programme: source-discovery handoff — 2026-11-08

Roadmap package: **P0.15** (`es-gen-2023`). This is an acquisition lead, not an authenticated source record, rights decision, reviewed political content or inclusion decision. No PDF bytes are committed.

## Reconciled boundary

`origin/main` at `488b6f5` still has four 2023 pilot source rows (PP, ERC, PNV, Sumar), all `published-unverified` with `not_reviewed` rights. It has no Junts 2023 row or approved candidature denominator. Draft PR #101 remains open, conflicting with main and without GitHub reviews; its six PP/ERC summaries remain unpublished. Open PRs on 2026-11-08 already address other party-source leads and adjacent P0/P1 gates; merged main also has BNG and EH Bildu discovery handoffs. The open-PR inventory contains no Junts-specific source-discovery PR. The repository's 2023-corpus-completion change remains proposal-only.

## Observations (2026-11-08 UTC check)

| Location | Direct observation | What it does not establish |
|---|---|---|
| [betevé article](https://beteve.cat/politica/programa-junts-eleccions-generals-2023/) | HTTP 200. Its current HTML identifies a Junts 23J programme and links to the PDF below; `article:published_time` and `datePublished` both say `2023-07-19T16:30:00+02:00`. | The current HTML metadata is not a retained 2023 capture, and the article is not the party's publication/rights decision. |
| [betevé-hosted PDF](https://img.beteve.cat/wp-content/uploads/2023/07/programa-junts-per-catalunya-eleccions-generals-2023.pdf) | HTTP 200, `application/pdf`, 562,594 retrieved bytes beginning `%PDF-1.4`; SHA-256 of the response bytes: `7f73e138b6020f9a12ff260f7baeb3aa2807b60903e91052435f7e0ded7d938b`. | An accessible press copy is not, by itself, proof of byte identity with a party-hosted version, a pre-election publication date for these exact bytes, completeness, programme applicability or reuse permission. |
| `https://janhihaprou.cat/app/uploads/2023/07/Programa-Electoral.pdf` | DNS lookup failed (`Name or service not known`) in this run. This historic campaign-URL lead appears in a later [research paper's bibliography](https://www.nature.com/articles/s44168-024-00183-5), not in an observed live publisher page. | The failure does not prove the 2023 document never existed, nor authenticate the press copy. |
| `https://junts.cat/wp-content/uploads/2023/08/Programa-Electoral-Definitiu-def.pdf` | HTTP 404 in this run. This is a separately reported URL lead, not a verified publisher link in this audit. | It cannot supply the source bytes, publisher chain or publication chronology. |

The PDF hash identifies **only the betevé response checked on this date**. The URL's `/2023/07/` path, the article's date metadata and a PDF's internal dates must not be substituted for version-bound publication evidence. No source text, political position, quotation or page locator was extracted or approved.

## Decision and acquisition queue

1. Under the owner-approved 2023 inclusion rule, establish the precise Congress candidature/coalition identity and whether this programme applies to it; do not create a party-wide position from a name match.
2. Seek a retained publisher-to-document link or a reviewable historic capture of the campaign site. Compare exact bytes/versions against the press copy without assuming equivalence from title or pagination. Record each location and any replacement separately.
3. Retain private acquisition evidence and exact-byte hash, then ask the source-authenticity and rights owners for separate, use-specific decisions (link, paraphrase, quotation, redistribution). An accessible PDF is not a grant of any of those uses.
4. Only after source scope, chronology, rights and editorial gates are resolved, consider a register row, topic search or statement review. Keep unresolved states visible; do not call a missing initiative `not stated`.

Validation scope: direct response/metadata checks and repository-row assertions only. No private archive, page review, full-document search, approval, source-register change, build or public publication occurred. CI, when it runs, remains engineering evidence rather than human review.
