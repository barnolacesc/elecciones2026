# Junts 23J document discovery — pending source review

Roadmap package: **P0 document-discovery handoff** (`2023-corpus-completion`,
proposal-only). Checked on 2026-10-31 against `origin/main` at `8e2fab4`.
This is a lead for private verification, not an approved candidature, source,
rights decision, political claim, or coverage count.

## Reconciled baseline

- `content/sources/register.json` has four `es-gen-2023` pilot rows (PP, ERC,
  PNV, Sumar), all `published-unverified` with rights `not_reviewed`; it has no
  Junts 2023 row. Its Junts row is explicitly for `es-gen-2026` and cannot be
  reused as a 2023 source.
- The 2023 inclusion rule and candidature manifest remain unapproved. The
  existing four rows cannot define a completeness denominator. Draft PR #101
  remains open, conflicting with main, and without a submitted GitHub review;
  PR #166 separately attempts its integration and is not a rights approval.
- Open PRs #183, #188, #189 and #196 address PSOE, VOX, BNG and EH Bildu
  discovery respectively. This handoff concerns Junts only and does not edit
  their documents, the source register, or shared OpenSpec tasks.

## Discovery observations and limits

| Evidence checked | Observation on 2026-10-31 | What it does **not** prove |
|---|---|---|
| [Betevé article](https://beteve.cat/politica/programa-junts-eleccions-generals-2023/) | The media outlet identifies and links a Junts programme for the 23 July 2023 general election; the page returned HTTP 200. | Party-issued provenance, exact candidature/coalition attribution, source version, or rights to republish. |
| [Betevé-hosted PDF URL](https://img.beteve.cat/wp-content/uploads/2023/07/programa-junts-per-catalunya-eleccions-generals-2023.pdf) | A HEAD request returned HTTP 200, `application/pdf`, and `content-length: 562594`. `Last-Modified` was 2023-07-19, which is server metadata only. | Document publication date, full byte integrity, equivalence to the original, page-locator stability, or quotation rights. No PDF was committed or imported. |
| [Peer-reviewed article's source citation](https://www.nature.com/articles/s44168-024-00183-5) | Its reference list cites `https://janhihaprou.cat/app/uploads/2023/07/Programa-Electoral.pdf` for the 2023 Junts programme. A HEAD request to that campaign-domain URL failed DNS resolution in this environment. | Current availability of the original, authenticity of the media copy, or permission for any use. The paper is corroborating discovery evidence, not a party-source review. |

The media copy is a **candidate document**, not a verified official source.
The campaign-domain citation is a lead for archive and provenance work, not a
substitute for the source bytes. Neither an inaccessible original nor an empty
register row means that Junts had no programme or stated no position.

## Private review tasks before an inventory row or public use

1. Under a human-approved 2023 inclusion rule, verify the Congress
   candidature's exact ballot/list name, constituency and coalition/member
   attribution against authoritative election evidence. Do not equate a party
   label or media headline with a candidature ID.
2. Find and privately preserve a pre-election campaign-domain copy or other
   publisher evidence if available. Record retrieval time, redirect chain,
   content type, size, SHA-256, private archive reference and version. Compare
   the Betevé bytes with any original **before** claiming equivalence; keep
   distinct hashes/versions if they differ. Record failed searches too.
3. Have a human review source authenticity, publication date evidence, document
   scope and each proposed reuse right separately. Leave `not_reviewed` and
   unknown dates intact until evidenced. A reachable PDF or academic citation
   is not a licence to quote or redistribute.
4. Only after these gates, reconcile the candidature-to-document join and
   topic-search scope under the OpenSpec P0/P1 contract. No initiative,
   relationship, `not stated` conclusion, percentage or public output follows
   from this discovery note.

No original PDF, extracted text, political answer, source record, review mark,
build, routing or deployment changed in this package.
