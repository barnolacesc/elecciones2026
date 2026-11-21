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

## Cutover preflight — 2026-11-21

The exact comparator candidate is `aaee54c162f5dd6cca6725d6a1c09f38414fb837`
from [PR #267](https://github.com/c2ventures/elecciones2026/pull/267).
[PR CI](https://github.com/c2ventures/elecciones2026/actions/runs/44895647753)
passed schema and security checks, rendered mobile and keyboard regression,
Docker serving parity and fork isolation. Candidate publication was skipped
because this was a pull-request run. The latest successful main artifact
is `d13ba683888de17714ad958a8034916168889cc3` and has private-staging
classification. It is not the comparator candidate above.

A local Docker build from the exact comparator revision returned HTTP 200
with the expected content and headers on ten endpoints. These included
education, the Junts and Frente Obrero pages, sources, method, corrections,
the sitemap and the comparator bundle. The sitemap and comparison pages
use the public canonical host. The quiz remains unavailable in this
candidate. This arm64 loopback build is not the hosted release digest.

The PR load artifact recorded scheduled p95 of 502 ms steady, 503 ms cold,
and 1,450 ms burst on its merge test revision. Origin peak reached
732, 680 and 833 requests/s respectively, above the 200 requests/s target.
The burst also dropped requests. The fixture does not represent Cloudflare
or the live IONOS host and does not meet the load acceptance gate.

The apex and www currently return Cloudflare 521. The preview returns 401
with authentication, no-store and noindex. The precise public origin fault
is unverified. Keep preview authentication active during public cutover.
The staging and public nginx templates each own a default server, so a
configuration that retains both hostnames needs a single default server
and distinct published and staging upstreams. Exposing the existing staging
upstream would permit a later private delivery to replace public content.

The owner has requested the public cutover. The signoff matrix still lists
the Project Partner role. Record its replacement or explicitly amend the
matrix before treating the request as complete G4 signoff. Confirm the
release engineering review and infrastructure measurements on the same
published digest before exposing it.

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
