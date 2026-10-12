# 2023 pilot human review pack

Roadmap package: **E1.4**. Issues: [#70](https://github.com/c2ventures/elecciones2026/issues/70) and [#42](https://github.com/c2ventures/elecciones2026/issues/42).
Inspection date: 2026-10-12. Election: `es-gen-2023`.
Status: PP and ERC selected by the owner; source rights and human reviews are pending.

This pack gives reviewers a verified local source inventory and starting locations for housing, health and social services, and education. The owner selected PP and ERC in the project session on 2026-10-12. Four new quote-free statement drafts cover their health and education proposals; the existing housing drafts remain unpublished. The inventory retains the two unselected sources for traceability. Selection does not approve coverage, rights or content. No relationship assertion or approval record is added.

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

The inventory includes each candidate page's text checksum and extraction anchor. Printed page labels remain unset except for the six pages inspected in private renders by an agent. That inspection is not human editorial approval. An extracted page number is not a printed label. Empty or incomplete extracted text does not establish an absent proposal. These starting ranges do not support a `not_found` record; that requires an agreed search scope and human review of the whole relevant source.

## Review sequence

1. PP and ERC are selected. Owners must confirm the pilot scope and selection rationale without altering source rights or review status.
2. Owners identify two distinct human reviewers and a rights decision owner. Retain real identities and evidence through an approved private access mechanism. The drafter cannot serve as the secondary reviewer.
3. Review the source identity, immutable election, version, checksum, language and publication-date evidence. Leave an unknown publication date unset. A filename or upload directory is insufficient.
4. Select specific operative proposals for the three topics. Inspect the original page and surrounding qualifications. Do not fill a quota. Check the existing housing drafts against the original instead of treating them as evidence; the [withdrawal audit](../../PILOT-2023-AUDIT.md) explains their limits.
5. Use [review-form.md](review-form.md) for each candidate. Write a concise Spanish summary and preserve eligibility, timing, competence, funding and uncertainty. Use the approved taxonomy and subtopic. Keep statement records as `draft`, with `reviews: []` and `last_reviewed_date: null`, until authentic review occurs.
6. Obtain a source-rights decision before publishing a quotation. A verified local PDF is not quotation permission. Repository quotation ceilings do not replace a rights decision.
7. Have both humans review each statement separately. Retain approvals that bind the statement text, qualifications, exact page/section and source version/hash. Only the authorized editorial workflow can enter authentic approvals and evidence references.
8. Review relationships separately. Shared goals, different instruments or silence do not establish agreement or opposition. Keep unsupported relationships invalidated or absent.
9. Verify the approved set in static HTML and the browser at 360, 390 and 430 CSS px, with source links and without JavaScript. Record evidence in the MVP task record. Issue #44 owns preview release acceptance; issue #71 owns hosted delivery.

## Open decisions and exit limits

- Two-party selection is recorded. Two real reviewers, private approval retention/access and source-rights decisions are missing.
- Agent visual inspection and draft Spanish summaries are prepared for six source locations. Human review, publication-date evidence, coverage completeness and relationship review are incomplete.
- Four new statements are drafts with empty reviews. No source status, rights flag, review mark or invalidated relationship is restored by this pack.

Issue #70 and MVP task 1.2 remain open. This historical pilot does not pass G2 for 2026. No claim is authorized for publication, and no deployment is performed.

## Preparation checks

The 2026-10-12 local check verified four original objects and four extraction objects, then compared all 43 candidate page anchors and text hashes with their private `pages.json` records. Source versions, original byte counts, aggregate extraction hashes, pending rights status and all local documentation links matched. `git diff --check` passed. The subsequent selected-party preparation adds four unpublished records and removes two existing housing quotes. Application code is unchanged.

An authorized editor can recheck each object with the documented archive CLI:

```sh
for source in src-2023-pp-v1 src-2023-erc-v1 src-2023-sumar-v1 src-2023-pnv-v1; do
  PYTHONPATH=src python3 -m elecciones2026.private_archive verify \
    --archive "$ELECTIONS_PRIVATE_ARCHIVE" --source-id "$source" \
    --image sha256:cd68be1fcb3953aa9160f19f415f40004b0adc33003d647b97a882a88797e8a5
done
```

This command needs the private archive, but does not run Docker or contact a network. CI must not acquire these originals. The OpenSpec CLI was unavailable; the existing roadmap and MVP artifacts were read directly. No OpenSpec completion checkbox was changed.

## Selected draft evidence

The six pages below were rendered locally from the checksum-verified original PDFs and inspected by an agent. Private renders are named `<party>-<physical_pdf_page>.png` under the archive's `issue70-renders/` directory, outside Git. Page text hashes remain in the inventory. This is machine preparation evidence, not a human approval or rights decision.

| Statement ID | Physical PDF page | Printed label | Exact location | Preparation action |
|---|---:|---:|---|---|
| `stmt-pilot-pp-housing-2023` | 34 | 32 | Measure 91 | Existing draft checked; quote removed |
| `stmt-pilot-erc-housing-2023` | 114 | 113 | HABITATGE, c), first bullet | Existing draft checked; quote removed |
| `stmt-pilot-pp-health-2023` | 45 | 43 | Measure 120, third bullet | New draft |
| `stmt-pilot-erc-health-2023` | 61 | 60 | SALUT, c), fourth bullet | New draft |
| `stmt-pilot-pp-education-2023` | 50 | 48 | Measure 146 | New draft |
| `stmt-pilot-erc-education-2023` | 128 | 127 | EDUCACIÓ, c), fourth bullet, section continues from PDF page 127 | New draft |

Each content record links the registered original URL and local `23J-v1` version. Resolve its PDF checksum through its programme record and the inventory. Housing quotations were removed because source rights remain pending. Their previous text is retained in Git history and the existing [audit records](../../../content/audits/2023-pilot-2026-10-12.json); no approved correction is claimed. The summaries and qualification fields remain draft material.

Human reviewers must check the Catalan-to-Spanish rendering of ERC records, particularly the territorial scope and the distinction between current congressional proposals and a hypothetical republic. PP's training places are not existing clinical jobs. ERC's retirement flexibility has no stated upper age in the cited bullet. PP's education measure states free provision and joint financing; ERC's cited education bullet concerns financial transfers and does not specify free provision or an amount. These limits are retained in the drafts.

No comparison relationship is created. Different health and housing instruments do not establish opposition. Even the two education proposals need a separate review of funding, scope and qualifications before a relationship can be approved.

Selected-party checks (2026-10-12): `schemas validate-all` passed 67 checks; `editorial validate-build` passed six gate checks. A dated `es-gen-2023` static build completed with zero published statements and zero relationships. An output inspection confirmed that the six selected draft IDs and summaries were absent from generated HTML and browser scripts. Archive metadata, all candidate page hashes and local documentation links were rechecked. `git diff --check` passed. No human editorial review, source-rights decision or hosted release was performed.
