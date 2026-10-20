# 2023 corpus contract readiness audit — 2026-10-20

Roadmap package: **P0.2 readiness audit**, not P0.2 implementation or editorial sign-off. Snapshot: `origin/main` at `f6c6c8d`. Inputs were repository records, the merged P0.1/P1.1 OpenSpec drafts (PRs #114/#118), and GitHub PR/CI metadata. No external party website, private PDF, review evidence, or legal source was verified in this audit.

## Reconciled baseline

| Check | Observed | Consequence |
|---|---|---|
| Source register | Four `es-gen-2023` records (PP, ERC, PNV, Sumar), all `published-unverified` and rights `not_reviewed` | Pilot rows are not the approved candidature denominator or a rights clearance. |
| Content examples | Four 2023 programme records, eight statement records, six invalidated relationships | Record counts do not establish topic breadth or a publishable comparison. |
| Inclusion and taxonomy | No approved enumerated 2023 candidature manifest is present. `content/taxonomy.json` version `1.0.0` identifies `es-gen-2026`. | Neither complete party coverage nor a 2023 topic denominator can be calculated from current files. |
| Draft OpenSpec | P0.1 inventory/rights and P1.1 initiative/comparison deltas were merged as PRs #114 and #118. Their tasks still require human decisions and later implementation. | Do not redraft these as new work or treat a merged draft as editorial approval. |
| PR #101 | Sole open PR at inspection: draft, GitHub merge state `dirty`, no GitHub reviews; it edits six PP/ERC pilot summaries plus schema/generator gates. | Do not modify its overlapping files, treat its older green checks as a review, or silently resolve its conflicts. |
| Main CI | At `f6c6c8d`, test/schema, Docker and fork-isolation jobs passed; rendered mobile/keyboard job failed at “Check complete mock quiz flow and browser privacy boundaries”; private delivery skipped. | Main is not fully green. This audit does not diagnose or waive that separate P3 regression. |

## Field-level gap against the merged draft contract

This table describes current technical capacity, not proposed political or legal decisions.

| Draft contract need | Current evidence | Later implementation acceptance check |
|---|---|---|
| Approved 2023 rule and complete candidature manifest | `register.json` has `elections` and source rows but no inclusion-rule version, approved manifest or authoritative-list evidence. | A fictional fixture with an included candidacy but no document still appears in the denominator; unapproved rules cannot produce “all parties” claims. |
| Candidacy-to-many-document ledger | Each `SourceRecord` has one `party_id`, one `candidature_name`, and `scope: general`; JSON schema permits only `general`. There is no separate discovery/annex/coalition link. | A fictional coalition, regional annex, replacement and unlocated document remain separate and traceable; no one-PDF-per-party collapse. |
| Source identity, retrieval and private archive | Four pilot hashes and retrieval dates exist, but no source-specific archive reference or publication-date evidence field. All four publication dates are null. | Unknown dates remain null; hash/URL/byte verification are separate from authenticity, and originals never enter the public artifact. |
| Rights use and evidence | `RightsReview` stores status, reviewer, date and free-text notes; it has no immutable evidence reference or per-version permitted-use record. Four 2023 rights statuses are `not_reviewed`. | A link-only fixture cannot publish a quote; a version change invalidates its previous rights decision and leaves private evidence outside Git. |
| Reproducible source/topic coverage | No approved 2023 manifest or document/topic search matrix exists. Existing pilot pages are starting locations, not a full search. | Counts name rule/version, denominator, snapshot and unresolved rows; empty extraction never becomes `not stated` or opposition. |
| Timestamp validation | Schema says register `last_updated` is `date-time`, but the file contains `2026-10-12` (date only). Python `load_register_from_dict` checks presence, not format. | Schema and Python validator accept the same explicit representation and reject an invalid value; migration is reviewed before changing stored data. |

The last row is a schema/parser divergence, not permission to change dates in editorial records. PR #101 changes the source register schema and parser in other ways; this audit deliberately makes no schema or parser edit. Re-evaluate the matrix after that PR is revised or merged.

## Ordered handoff and test plan

1. Human owners approve or revise the 2023 eligibility rule, official enumeration evidence, coalition/territorial treatment, taxonomy scope, rights roles, private evidence contract and reviewed-search stopping rule. Existing OpenSpec tasks remain unchecked for these decisions.
2. Only then prepare a bounded P0.2 implementation design update and fictional fixtures for each acceptance case above. Reconcile against PR #101 and the current branch before editing shared schemas. No real source, quote, reviewer mark or political position is supplied by a fixture.
3. Enumerate the included candidacies and relevant documents under the approved rule, including explicit unresolved searches. Separate source, rights, topic and relation review. Publication remains a distinct human gate.

This audit changes no source register, schema, political statement, relationship, rights status, routing, build artifact or deployment. It is not evidence that P0 or P1 has passed.
