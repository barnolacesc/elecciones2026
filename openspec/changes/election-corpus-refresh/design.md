# Design

## Context

See proposal.md for motivation. E0.4 registered eight private documents. No
2026 claims have human editorial or reuse approval. The existing generator
loads test examples and Compose defaults to the 2023 rehearsal.

## Goals / Non-Goals

Prepare package E1.4-2026: a separate records directory for 2026, the current
source inventory, exact provenance gates, and incremental approved records.
Do not change source rights, infer approval, publish originals, or deploy.
Budget, quiz and historical content remain outside this package.

## Decisions

- Add an explicit records-directory input to the generator. Keep the existing
  examples path for fixture tests and historical rehearsal. Container builds
  select production records for 2026. This avoids copying private text into
  the serving image or relabelling 2023 records.
- Apply the existing real-source provenance and rights gates to production
  2026 records, including independently reviewed relationships. Empty production
  directories produce an explicit pending state, never fixture fallback.
- Filter source and party output to the requested election. Historical records
  remain in Git for audit; no historical programme inventory is rendered in the
  2026 source view.
- Use the existing networkless private PDF worker for extraction. Retain
  page-level text outside Git. Initial intake quarantines rejected documents.
  Under the owner's subsequent remediation/delegation request, a coordinator
  can review a private route pinned to one exact source hash. Keep shared
  limits and the global active-content scanner unchanged. Coalición Canaria
  uses a 75 MiB private worker with bounded scratch space. SALF uses an audited
  false-positive exception plus isolated structural JavaScript/attachment
  checks. Neither route changes source identity, reuse or editorial approval.

## Risks / Trade-offs

- Extraction is not a complete point inventory or editorial review → retain
  separate completion tasks and require exact page/section citations.
- ERC and Frente Obrero edition identity is unresolved → retain unverified
  status. Do not assert a 2026 position from these documents.
- Empty approved corpus → show pending review and original source coverage.
- Docker may be unavailable locally → record the verification limit; do not
  substitute unisolated parsing for the existing worker.
- A proposed stream-masking regex can miss actual PDF structures → do not
  change the global scanner based on a single document. Retain exact-hash
  private exceptions, independent byte evidence and networkless parsing.

## Migration Plan

Change the local 2026 build input, run source/generator tests, and compare two
build hashes. Keep 2023 rehearsal selectable explicitly. Release approval and
deployment remain separate; rollback uses the prior immutable serving artifact.

## Owner continuation — 2026-11-12

Prepare the same 2026 approved-record input in the existing authenticated staging
candidate workflow. CI builds the current election rather than the provisional
2023 pilot. Candidate validation accepts a distinct 2026 record mode while
retaining exact historical candidate compatibility. Classification remains
private-staging; neither public routing nor content approvals are inferred.
The owner requested public delivery, but source/human decisions and G4 evidence
remain prerequisites. Live unauthenticated endpoint observations on 2026-11-12:
apex and www resolve through Cloudflare and return 521; preview returns 401.
Do not describe DNS as absent or infer the origin's exact configuration from
these responses.

## Taxonomy compatibility

Production records can provide a versioned election-specific `taxonomy.json`.
Validate its election, stable numeric version, core topic retention and structural
integrity before checking each statement/relationship's topic and subtopic.
The shared historical taxonomy remains unchanged. Schema validation without an
explicit taxonomy retains the original core topic policy. This capability does
not turn the private proposed taxonomy or its classifications into approved
content; editorial acceptance and harmonization remain outstanding.
