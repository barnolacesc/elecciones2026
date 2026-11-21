# 29 November 2026 public release review

Roadmap package E3.5. The G4 gate is open. This packet applies to the
`es-gen-2026` comparator and the existing public IONOS/Cloudflare plan.

## Candidate and evidence

The [editorial task record](../openspec/changes/election-corpus-refresh/tasks.md)
identifies the exact batch that Cesc approved. The candidate contains 5,621
approved summaries across 12 topics. It covers 14 verified programmes.
UPN–PP and Frente Obrero have partial campaign coverage and source links.
The candidate contains no verbatim quotations or comparison relationships.

Local Docker served the exact expected 5,621 comparison IDs. The browser
comparison bundle was 5,959,515 bytes uncompressed and 559,813 bytes over
local HTTP with gzip. Use the full corpus for mobile delivery and load
checks. These byte counts measure size only.

Read-only HTTPS checks on 2026-11-21 returned 521 at the public apex and
www, and 401 at the authenticated preview. These responses describe the
endpoints at the time of the check.

## G4 evidence to record

| Area | Evidence required for this candidate |
| --- | --- |
| Candidate | Record the trusted CI run, Git revision, immutable image digest and scan. Run the mobile and accessibility checks against that digest. Verify comparison, coverage, citations and correction routes. |
| Public edge | Verify the approved apex and www behavior, DNSSEC, TLS, origin protection and cache policy. Preserve authentication and cache bypass on private staging. Use the [origin runbook](README.md). |
| Capacity and monitoring | Measure the approved cache and burst scenarios against the 1-vCPU IONOS origin. Record the results against the [load targets](../openspec/changes/mvp-programme-comparison/tasks.md). Verify external probes and alert receipt. |
| Recovery | Retain the prior approved digest. Verify rollback, cache purge and recovery on the target environment. Record recovery time and the origin and edge checks. |
| Signoff | Record editorial, security, accessibility and release decisions for the same digest. Resolve the applicable roles in the [G4 signoff matrix](../docs/DECISION-RECORD.md#7-decision-5-signoff-matrix-and-human-release-gates) and record the launch decision before activation. |

The existing delivery workflow deploys authenticated staging. Follow the
[server runbook](SERVER-MIGRATION.md) for the separately approved public
activation and rollback.
