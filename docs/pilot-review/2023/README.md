# 2023 pilot human review pack

Roadmap package: **E1.4**. Issues: [#70](https://github.com/c2ventures/elecciones2026/issues/70) and [#42](https://github.com/c2ventures/elecciones2026/issues/42).
Inspection date: 2026-10-12. Election: `es-gen-2023`.
Status: preparation only; owner selection, source rights and human reviews are pending.

This pack gives reviewers a verified local source inventory and starting locations for housing, health and social services, and education. It contains no new political summaries, quotations, relationship assertions or approval records. The owners have not selected the two parties. Inventorying all four available originals does not select a pilot pair or approve coverage.

## Verified inputs

[inventory.json](inventory.json) records metadata for the four registered originals. Each original passed `private_archive.verify_original`; each extraction passed `private_archive.verify_extraction` with the retained worker image `sha256:cd68be1fcb3953aa9160f19f415f40004b0adc33003d647b97a882a88797e8a5` on `linux/arm64`. These checks verify local byte integrity and page mapping. They do not prove source authenticity, a publication date, quotation rights or editorial acceptance. No network request or extraction run was needed.

| Party | Source ID | Physical PDF pages | Language | Rights review |
|---|---|---:|---|---|
| PP | `src-2023-pp-v1` | 112 | Spanish | Pending |
| ERC | `src-2023-erc-v1` | 132 | Catalan | Pending |
| Sumar | `src-2023-sumar-v1` | 182 | Spanish | Pending |
| PNV | `src-2023-pnv-v1` | 52 | Spanish | Pending |

Use the owner-only archive configured in [the private archive guide](../../PRIVATE-SOURCE-ARCHIVE.md). Resolve an object as `<archive>/es-gen-2023/<source_id>/<source_sha256>/`. Its `original.pdf` is the visual reference. Its extraction is under `extractions/<worker_image_id_without_sha256_prefix>/`. Full PDFs, text, page renders and approval evidence must stay outside Git and public artifacts. The static build does not read this pack or the archive.

## Topic starting locations

These physical PDF page ranges are search candidates, not accepted citations or complete coverage. They were selected from extracted section headings and surrounding pages. Reviewers must inspect the original page and adjacent context. The ranges can overlap where a section covers multiple subjects.

| Party | Housing | Health and social services | Education |
|---|---|---|---|
| PP | 33–34 | 45–49 | 50–52 |
| ERC | 113–115 | 60–64 | 126–129 |
| Sumar | 75–79 | 89–92 | 154–158 |
| PNV | 45–46 | 45–47 | 48–49 |

The inventory includes each candidate page's text checksum and extraction anchor. Printed page labels are deliberately unset until visual review. An extracted page number is not a printed label. Empty or incomplete extracted text does not establish an absent proposal. These starting ranges do not support a `not_found` record; that requires an agreed search scope and human review of the whole relevant source.

## Review sequence

1. Owners select exactly two parties. Record the reason and scope without altering source rights or review status.
2. Owners identify two distinct human reviewers and a rights decision owner. Retain real identities and evidence through an approved private access mechanism. The drafter cannot serve as the secondary reviewer.
3. Review the source identity, immutable election, version, checksum, language and publication-date evidence. Leave an unknown publication date unset. A filename or upload directory is insufficient.
4. Select specific operative proposals for the three topics. Inspect the original page and surrounding qualifications. Do not fill a quota. Check the existing housing drafts against the original instead of treating them as evidence; the [withdrawal audit](../../PILOT-2023-AUDIT.md) explains their limits.
5. Use [review-form.md](review-form.md) for each candidate. Write a concise Spanish summary and preserve eligibility, timing, competence, funding and uncertainty. Use the approved taxonomy and subtopic. Keep statement records as `draft`, with `reviews: []` and `last_reviewed_date: null`, until authentic review occurs.
6. Obtain a source-rights decision before publishing a quotation. A verified local PDF is not quotation permission. Repository quotation ceilings do not replace a rights decision.
7. Have both humans review each statement separately. Retain approvals that bind the statement text, qualifications, exact page/section and source version/hash. Only the authorized editorial workflow can enter authentic approvals and evidence references.
8. Review relationships separately. Shared goals, different instruments or silence do not establish agreement or opposition. Keep unsupported relationships invalidated or absent.
9. Verify the approved set in static HTML and the browser at 360, 390 and 430 CSS px, with source links and without JavaScript. Record evidence in the MVP task record. Issue #44 owns preview release acceptance; issue #71 owns hosted delivery.

## Open decisions and exit limits

- Two-party selection, two real reviewers, private approval retention/access and source-rights decisions are missing.
- Original page visual review, printed labels, publication-date evidence, Spanish summaries and relationship review are incomplete.
- No new statement draft is created before party selection. No source status, rights flag, review mark or invalidated relationship is restored by this pack.

Issue #70 and MVP task 1.2 remain open. This historical pilot does not pass G2 for 2026. No claim is authorized for publication, and no deployment is performed.

## Preparation checks

The 2026-10-12 local check verified four original objects and four extraction objects, then compared all 43 candidate page anchors and text hashes with their private `pages.json` records. Source versions, original byte counts, aggregate extraction hashes, pending rights status and all local documentation links matched. `git diff --check` passed. This is a documentation and inventory change; no application behavior changed.

An authorized editor can recheck each object with the documented archive CLI:

```sh
for source in src-2023-pp-v1 src-2023-erc-v1 src-2023-sumar-v1 src-2023-pnv-v1; do
  PYTHONPATH=src python3 -m elecciones2026.private_archive verify \
    --archive "$ELECTIONS_PRIVATE_ARCHIVE" --source-id "$source" \
    --image sha256:cd68be1fcb3953aa9160f19f415f40004b0adc33003d647b97a882a88797e8a5
done
```

This command needs the private archive, but does not run Docker or contact a network. CI must not acquire these originals. The OpenSpec CLI was unavailable; the existing roadmap and MVP artifacts were read directly. No OpenSpec completion checkbox was changed.
