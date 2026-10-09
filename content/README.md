# Content records, schemas, and fixtures

This directory stores structured data records, JSON schemas, and test fixtures for the election comparison platform.

## Directory layout

- `taxonomy.json`: Authoritative machine-readable definition of the 8 core topics and subtopics (taxonomy version 1.0.0).
- `schemas/`: JSON Schema (Draft 2020-12) specifications defining record contracts:
  - `programme.schema.json`: Programme provenance, coverage lifecycle states, and cryptographic verification.
  - `statement.schema.json`: Source-linked political statements with dual-review tracking and absence representation.
  - `relationship.schema.json`: Measure-based comparative relationships, qualifications, and invalidation status.
  - `coverage.schema.json`: Candidacy coverage records and election coverage snapshots.
  - `correction.schema.json`: Dated correction records with prior/new states and relationship invalidations.
- `sources/`: Versioned source register (`register.json`) and schema (`register.schema.json`) tracking official 2026 candidacies and verified 2023 pilot rehearsal programmes.
- `examples/`: Labelled test fixtures (`is_fixture: true`) used to verify schemas, validators, and pipeline behavior:
  - `parties.json`: Candidacy inclusion criteria, party naming standards, and coalition modeling.
  - `programmes/`: Programme lifecycle fixtures (`official`, `partial`, `replaced`, `missing`).
  - `statements/`: Position statement fixtures including approved proposals with dual review, explicit absence (`not_found`), qualified proposals, and 2023 pilot rehearsal statements.
  - `relationships/`: Comparative relationship fixtures demonstrating policy agreement, partial overlap with qualifications, and single-party positions.
  - `coverage/`: Election coverage snapshot and individual candidacy coverage records.
  - `corrections/`: Editorial correction records demonstrating topic reclassification and citation coordinates updates.
  - `invalid/`: Negative test fixtures verifying validator rejection of unreviewed claims, missing provenance, cross-election contamination, and single-reviewer corrections.
- `programmes/`: Production programme-level extraction and provenance records (empty until human gate approval).
- `statements/`: Production human-reviewed, topic-tagged position statements (empty until human gate approval).

## Production data policy

Real political programme records will be introduced only after:
1. Candidate inclusion criteria and source acquisition policies pass human gate G0.
2. Official candidacies are proclaimed by the *Junta Electoral Central* (JEC).
3. Primary source documents are verified with SHA-256 hashes and rights clearances.

Do not commit unreviewed political claims or unverified documents. All files in `examples/` are explicitly marked with `"is_fixture": true`.
Do not add full PDF files or unreviewed quotes without official sources and rights checks.
