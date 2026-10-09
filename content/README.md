# Content records and fixtures

This directory stores structured data records for the election comparison platform.

## Directory layout

- `taxonomy.json`: Authoritative machine-readable definition of the 8 core topics and subtopics (taxonomy version 1.0.0).
- `examples/`: Labelled test fixtures used to verify schemas, validators, and pipeline behavior.
  - `parties.json`: Fixture registry demonstrating candidate inclusion criteria, party naming standards, and coalition modeling.
  - `programmes/`: Fixture programme records demonstrating required coverage states:
    - `party-a-official.json`: Complete, verified official programme with SHA-256 hash and direct URL (`official` status).
    - `party-b-partial.json`: Partial manifesto / summary document (`partial` status).
    - `party-c-v1-replaced.json`: Superceded version tracking replacement reason and pointer (`replaced` status).
    - `party-c-v2-official.json`: Successor verified version (`official` status).
    - `party-d-missing.json`: Covered candidacy with no verified programme published or located (`missing` status).

## Production data policy

Real political programme records will be introduced only after:
1. Candidate inclusion criteria and source acquisition policies pass human gate G0.
2. Official candidacies are proclaimed by the *Junta Electoral Central* (JEC).
3. Primary source documents are verified with SHA-256 hashes and rights clearances.

Do not commit unreviewed political claims or unverified documents. All files in `examples/` are explicitly marked with `"is_fixture": true`.
