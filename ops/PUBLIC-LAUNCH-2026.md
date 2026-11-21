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

[Main CI](https://github.com/barnolacesc/elecciones2026/actions/runs/44930014014)
built the optimized comparator. [Authenticated delivery](https://github.com/barnolacesc/elecciones2026/actions/runs/44930546571)
verified its exact homepage in staging. The candidate contains 5,621
approved proposals. The quiz is unavailable in this build.

An isolated IONOS container matched the build's homepage hash and served
ten verified routes. A short loopback trial completed 1,600 requests
at 200 requests/s with scheduled p95 of 2.45 ms. Sustained traffic and
Cloudflare cache checks remain open.

The apex pointed to a different origin, and www pointed to the registrar
parking service. Both proxied records now route to the intended IONOS
origin. A temporary external HTTPS probe returned its exact marker before
cleanup. The apex still has no public application route. The preview returns
401 with authentication, no-store and noindex. The launch configuration
keeps staging on port 8080 and routes the apex to a separate image on port
8081. Staging owns the default server.

Cloudflare now validates the origin certificate for the apex, www and
preview. HTTP and www requests return 308 to the HTTPS apex and preserve
the path and query. The apex-only cache rule covers GET and HEAD. It uses
origin cache headers and bypasses caching when they are absent. Two distinct
query variants of the temporary HTML probe each returned MISS then HIT.
Direct external requests to the origin's HTTPS and public-container ports
timed out from the preflight client. DNSSEC signing is enabled at Cloudflare
and awaits the DS record at the registrar.

The owner requested the public cutover. On 2026-11-21, Cesc explicitly
took responsibility for the departed Project Partner's signoff for
this launch. The infrastructure and release evidence still applies
to the same published digest.

## Routing rehearsal

The TLS fixture served different markers on the staging and public
upstreams. The apex selected port 8081. The www host returned 308 and
preserved the path and query. The preview required Basic authentication,
served port 8080, and retained no-store and noindex. Nginx rejected a
request without the fixture client certificate. IONOS has an origin
certificate with both the apex and wildcard names. The live public
configuration has not been enabled.

The operator must keep distinct Compose project names, loopback ports
and release state for staging and public traffic. Staging remains on
port 8080 with the existing state. For the public site, use port 8081
and a root-owned public state directory. Verify the approved image on
loopback before adding the public virtual host. Test the combined nginx
configuration, confirm both Cloudflare DNS targets and Full (strict) TLS,
then verify the apex response, the www redirect and the preview challenge.
Keep the public virtual host removable without changing the preview.

## First-release recovery

If the first public release fails, disable only the public nginx
virtual host and reload after a syntax check. Restore changed public
DNS and cache settings if required. Verify that preview remains
authenticated. Keep staging release state separate from public recovery.

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
