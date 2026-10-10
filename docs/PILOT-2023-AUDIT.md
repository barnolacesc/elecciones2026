# 2023 pilot source and review audit

Package: E1.4. Issue: [#42](https://github.com/c2ventures/elecciones2026/issues/42).
Audit date: 2026-10-10. Election: `es-gen-2023`.
Status: automated source inspection completed; human editorial and rights approval pending.

## Result

Neither pilot statement has evidence of two distinct human approvals. The old
`rev-pilot-1` and `rev-pilot-2` entries were fixtures, including a secondary review
dated 2026-10-11. Both statements are now drafts with empty review lists and no
last-reviewed date. Their comparison is invalidated. No pilot political position
or comparison enters generated HTML or the browser comparator.

The prior generic `editorial-team` quotation-rights entries are also unsupported.
PP and ERC source and programme records are `published-unverified`, with rights
`not_reviewed`/`pending`. Their coverage records show zero approved statements.
This does not mean either programme lacks a proposal. It means the editorial
gate has not passed. Previously recorded publication dates are removed pending
evidence; a PDF filename, upload directory, or creation timestamp is not proof
of its original publication date. `23J-v1` is the local source-version identifier,
not a publisher's asserted revision label.

## Source checks

Both registered direct URLs returned PDF bytes without redirect on 2026-10-10.
The files matched their existing hashes; no source-version replacement is needed.
The registered PP discovery page returned HTTP 200. The registered ERC discovery
page returned HTTP 403 to this audit client; its direct PDF remained accessible.
That access restriction does not establish a missing programme. Both observations
are retained with timestamps in the audit record.

| Party | Original PDF | Bytes | SHA-256 |
|---|---|---:|---|
| PP | [Official-domain PDF](https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf) | 8,214,497 | `c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108` |
| ERC | [Official-domain PDF](https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf) | 1,228,157 | `760db25e48422b74a9b0c3172cab16cf39d010345849e50b921ff8bf61be2854` |

Page-preserving extraction used local Poppler `pdftotext -layout`. The relevant
pages were also rendered with `pdftoppm` and visually inspected. Each corrected
excerpt occurs in its cited page after whitespace normalization. Neither previous
quotation occurs verbatim in the normalized whole-document extraction. This is an
automated audit observation, not a signed human review or a legal conclusion.

| Record | Previous locator | Corrected draft locator | Finding |
|---|---|---|---|
| `stmt-pilot-pp-housing-2023` | Page 48 | PDF page 34, printed page 32, measure 91 | The cited PDF page concerns healthcare. The housing measure describes mortgage credit up to 95% of the property price. The prior 15% guarantee summary and first-home, appraisal, ICO, and application-age qualifications are unsupported by that measure. |
| `stmt-pilot-erc-housing-2023` | Page 32 | PDF page 114, printed page 113, housing section c), first bullet | The cited PDF page concerns secularism. The replacement draft represents one proposal about regional powers to regulate urban leases, with its competence and constitutional conditions. The previous combined rental/vacancy quotation and qualifications are not supported by the cited page. |
| `rel-pilot-2023-housing-pp-erc-divergence` | Both old claims | Invalidated | Different instruments were grouped as one measure. Deposit guarantees and a claim of no price intervention are not established by PP measure 91. A new comparison needs a separate human audit. |

## Audit trail and private-source interface

`content/audits/2023-pilot-2026-10-10.json` retains the previous statements,
programme/coverage states, review claims, comparison, source rights entries,
retrieval metadata, findings, and corrected draft states. It explicitly states
that no human approval or publication permission is recorded. It is an internal
audit log, not an approved `CorrectionRecord`; inventing two reviewers to approve
the correction would repeat the original error. Git retains the earlier versions.

Full originals, extracted text, and page renders were kept outside the checkout
under `~/.local/share/elecciones2026/private-source-audit/issue-42/`. That directory
is not an input to the static build and contains no public artifact. The audit JSON
contains metadata and bounded excerpts, not full PDFs or full extracted text.

[Issue #43](https://github.com/c2ventures/elecciones2026/issues/43) owns the reusable
private archive and deterministic extraction workflow. Keep its interface keyed
by `src-2023-pp-v1`/`src-2023-erc-v1`, `es-gen-2023`, `23J-v1`, and the full hashes
above. Preserve both the one-based PDF page index and printed page label. A
different hash needs a source-version decision and re-review; it must not silently
replace the audited bytes. CI must not download political documents by default.

## Publication checks and human handoff

For the 2023 pilot, each approved review must identify a human reviewer and an
`evidence_ref` to retained approval evidence. Placeholder IDs, automated reviews,
missing evidence, future dates, impossible dates, repeated reviewer identities,
and fixture-labelled political approvals fail validation. The last-reviewed date
must match the latest recorded approval. A human evidence reference is a traceable
record to inspect, not proof that a model's assertion of human approval is true.
Human reviewers remain responsible for the underlying authenticity and signoff.

The generator selects repository drafts outside the publish set and fails if a
caller explicitly tries to publish them. Approved pilot records must pass review,
source URL/version/election, programme/hash, and quotation-rights checks even when
the generic strict option is disabled. Removing draft HTML alone is insufficient:
the old hardcoded browser comparison was removed too. All pilot pages carry the
visible label `Generales 2023 (piloto)` and a pending-review notice.

Before any claim is displayed, two distinct human reviewers must inspect the
original page, source version and hash, quotation accuracy, summary, qualifications,
neutrality, and rights decision. Record their actual approvals and retained evidence
references. Review comparability separately before restoring the relationship.
The project owners must approve the release under
[issue #44](https://github.com/c2ventures/elecciones2026/issues/44). This audit does
not satisfy G2 for 2026 and does not authorize publication or deployment.
