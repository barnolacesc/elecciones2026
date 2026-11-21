# 2026 production corpus — E1.4-2026

This directory is the production input for the 2026 CLI and container build.
It is intentionally empty of political claims until source and editorial
reviews are complete. The source inventory is in `content/sources/register.json`.

Add reviewed records incrementally under `programmes/`, `statements/`,
`relationships/`, and `corrections/`. Use the existing schemas. Optional
`parties.json` can supply reviewed display names for registered parties; it
cannot introduce fixtures or unregistered parties. Empty directories have no
political meaning and never activate the examples corpus.

Statements require exact source URL, version and page/section, matching
programme/source hash, a verified source with a dated reuse decision and
evidence reference. A summary without a verbatim quotation requires one
named human approval. A verbatim quotation or comparison relationship requires
two independent human approvals. Relationships must resolve to approved
statements from this election. Store unreviewed originals and
draft points in the private archive outside Git. Do not create approval records
to make a build pass.

Build with:

```sh
PYTHONPATH=src python3 -m elecciones2026.generator build \
  --output-dir dist --election-id es-gen-2026 --build-date 2026-11-11
```

`ELECTION_ID=es-gen-2023 docker compose build` remains an explicit private
historical rehearsal. Deployment and public release require separate approval.

An editorially accepted election-specific `taxonomy.json` can extend the shared
core taxonomy. It must retain the core topic IDs, have stable numeric versioning
and match this election. Draft versions and unknown topic/subtopic combinations
are rejected. The private 12-topic proposal is not installed here automatically;
its classifications and the existing assignments need editorial acceptance.

The offline `elecciones2026.corpus_staging` utility prepares draft statement
records in an explicit directory outside the repository. These records retain
empty human reviews and cannot pass the strict production build. Keep their
private evidence sidecars and source decisions outside public serving artifacts.

## Approve a batch of summaries

1. Prepare a private list with the batch ID, each statement ID, the exact
   summary and qualifications, and the source version, page or section.
2. Review the list against the original documents. Reply with the batch ID,
   your name, the review date, and the approved statement IDs. State which
   IDs need changes if you approve only part of the batch.
3. Record the decision reference and each approved statement fingerprint.
   Record the source identity, publication date, and reuse decision for each
   source before importing the approved statements. Run the strict build.
   Review any statement again if its fingerprint changes.
