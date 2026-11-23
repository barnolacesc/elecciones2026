# 2023 document role and applicability-scope handoff

Roadmap package: **P0.16**, `2023-corpus-completion` (proposal only).
Election: `es-gen-2023`. Repository baseline: `origin/main` `bf0cdb5` on
2026-11-23. This is a schema/loader audit, not source verification, an
inclusion decision, rights advice, editorial approval or implementation.

## Observed mismatch

- The four registered 2023 pilot sources are all `scope: general`,
  `published-unverified`, rights `not_reviewed`, with unknown publication
  dates. They do not establish a complete candidature or document inventory.
- `content/sources/register.schema.json` requires `scope` and limits it to
  `general`. A territorial annex or coalition document cannot be represented
  under that checked-in source contract. The P0 inventory proposal explicitly
  needs such documents and replacements as separately scoped versions.
- `load_register_from_dict` in `source_register.py` copies `scope` with a
  default of `general` but does not validate its type or allowed values. A
  fictional source changed to `scope: territorial_annex` parsed without an
  error locally, despite the JSON schema rejecting that value. Loader success
  is therefore not evidence that a future inventory row conforms to the
  checked-in schema.
- Source document role, territorial/constituency applicability and a rights
  grant are different decisions. The existing singular `party_id` and
  `scope` string cannot by themselves establish which 2023 ballot list may
  use an annex or coalition document. The P0.10 shared-document draft covers
  candidature applicability; this handoff is limited to the document-role
  vocabulary and migration/parity gate before those edges can be reconciled.

PR #101 remains open and conflicting, with no GitHub review decision. Its
2026-10-12 successful checks predate this main baseline. PR #275 addresses
replacement-chain validation and PR #259 malformed parser containers; neither
is an approved 2023 role taxonomy or a current-main combined CI result. No
PR or check supplies source rights, 2023 inclusion or editorial approval.

## Proposed review contract

1. Owner/editorial reviewers decide the document-role vocabulary and whether
   a file can have several roles. Keep role (what the version is) separate
   from applicability (which candidature, constituency and period may use it)
   and replacement lineage (which exact version supersedes another). Do not
   infer any of those from a filename, party ID or URL alone.
2. After that decision, specify one versioned schema and loader contract.
   Both entry points must reject an unknown or malformed role and preserve
   pending applicability; they must not silently coerce an annex to `general`.
   Existing four pilot rows remain unchanged unless independently reviewed.
3. Reconcile the role migration with P0.2 inventory joins, P0.10 applicability
   edges and P1.4 document relevance. A role label alone cannot establish
   authenticity, reuse rights, topic coverage or a political position. Report
   unresolved roles/edges without a completeness percentage.
4. Use fictional general, territorial-annex, coalition, replacement and
   unknown-role fixtures to check JSON-schema/Python-loader parity and
   election-isolated coverage output. Only then consider actual 2023 rows
   under the approved inclusion and source-review workflow.

The OpenSpec design, requirement and task delta accompanying this audit is
for review, not implementation authorization. No source row, private PDF,
rights decision, political statement, public artifact or routing changed.
