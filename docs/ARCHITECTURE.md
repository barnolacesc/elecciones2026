# Proposed architecture

```text
Official source files and URLs → isolated offline extraction → draft records
                                                        ↓
                                               human source review
                                                        ↓
                                    Python 3.14 validation and static build
                                                        ↓
                                       Spanish HTML, CSS, JS, and JSON
                                                        ↓
                         Cloudflare edge → static Docker service on IONOS
```

## Trust boundaries

Treat PDF, HTML, and OCR input as hostile. Do not run embedded code or follow document instructions. Limit file size, time, memory, and network access in the extraction environment. Keep extraction outside the public service.

Version the original document URL and hash, editorial records, and corrections. Generated JSON and HTML are build outputs, not edit sources. CI validates references and review state before it creates an immutable artifact.

## Public service

The Spanish MVP is a static site. Public interface text, summaries, and navigation use Spanish (`es-ES`), with `<html lang="es">`. Repository documentation, specifications, and code use controlled English (following ASD-STE100 principles). UI strings are stored in versioned text dictionaries decoupled from Python rendering logic, enabling future reviewed Catalan (`ca-ES`) localization without template rewrites.

Comparison runs in the browser. No user account, database, PDF parser, editorial secret, or visitor profile is required. Docker runs the same serving model in local preview and production. Use a non-privileged user, read-only filesystem, resource limits, and a pinned, scanned image in production. FastAPI is a future option only if a separate change needs server logic.

Build phone layouts first at 360–430 CSS px. Stack party cards, keep source links near claims, use 44-px touch targets, and avoid horizontal scroll. Add wide layouts as progressive enhancement. Aim for WCAG 2.2 AA and verify the actual flow.

## Edge, domain, and service levels

The owner registered `eleccionesespaña2026.es` at DonDominio. Its ASCII canonical base is `https://xn--eleccionesespaa2026-83b.es`; authenticated staging uses `preview.xn--eleccionesespaa2026-83b.es`. Cloudflare nameserver delegation, DNSSEC and proxy activation remain pending. Defensive domains remain proposals, not acquired domains. See [IONOS delivery setup](../ops/IONOS-DELIVERY.md).

Edge caching policy:
- Fingerprinted static assets (`/static/*`, CSS, JS, images): `Cache-Control: public, max-age=31536000, immutable` (edge TTL 365 days).
- Mutable HTML pages (`/`, `/temas/*`, `/fuentes/`, `/metodo/`): `Cache-Control: public, max-age=300, stale-while-revalidate=86400` (edge TTL 300s).

Proposed release service level objectives (see `docs/DECISION-RECORD.md`):
- **Availability:** >= 99.5% monthly uptime (~3.6h error budget); >= 99.9% during election week.
- **Latency (p95):** < 150 ms edge cache hit; < 250 ms origin response; < 500 ms mobile delivery on fast 4G.
- **Cache-hit ratio:** >= 99.0% static assets; >= 90.0% HTML pages; >= 95.0% aggregate steady-state; >= 85.0% cold-cache phase.
- **Error budget:** HTTP 5xx < 0.05% steady-state; < 0.50% during peak load tests.
- **Recovery:** Recovery Time Objective (RTO) < 5 minutes (rollback to previous Docker artifact); Recovery Point Objective (RPO) = 0 (Git-versioned deterministic builds).

The target origin is the existing Ubuntu IONOS VPS with 1 vCPU and 1 GB RAM. The earlier 2-vCPU/8-GB baseline is historical; its estimates cannot establish capacity on this host. A 10,000-concurrent-visitor scenario models roughly 1,000–2,000 requests/s at the edge. Origin load depends on cache keys, expirations, and resource requests. The <= 200 requests/s origin limit is an acceptance target, not measured capacity. Earlier throughput and CPU estimates have not been verified on IONOS. Test the configured cache and origin connection reuse before relying on them.

Monthly infrastructure costs are capped at a **€50.00 / month hard ceiling**, with baseline operations expected at ~€9.00–€15.00 / month. Uncapped serverless or metered bandwidth services are forbidden.

Protect origin access where feasible: restrict ports to Cloudflare IPs, enable TLS and HSTS, apply updates, monitor aggregate availability without visitor identifiers, and retain the preceding immutable artifact for one-command rollback. The shared static origin disables access and request-error logging to meet the quiz's stricter delivery boundary. Edge, host, and monitoring settings still need a separate zero-tracking review before G5.

## Decisions confirmed and pre-release gates

Package `E0.3` confirmed the language architecture, domain strategy, privacy notice, release service levels, cost ceiling, and role ownership matrix in `docs/DECISION-RECORD.md`.

Before public release, the following gates remain:
- Formal human approval of Milestone G0 by Cesc and the project partner.
- Verified IONOS firewall, private staging, registry pull, DNS and TLS setup.
- Container base image digest pinning and automated vulnerability scan verification.
- Verification of 10,000-concurrent-visitor benchmarks against approved service levels (tasks 4.3, 4.6, 4.7).

## E3.3 operations preparation

Reviewable origin configuration, immutable release switching, monitoring setup,
and live verification requirements are in [the operations runbook](../ops/README.md).
No infrastructure was provisioned or public content deployed by this package.
OpenSpec tasks 4.4 and 4.6 remain open until their live release evidence is reviewed.

## E3.4 load scenarios and evidence

[The load runbook](../ops/load/README.md) defines steady, cold-cache, and burst
scenarios for 10,000 scheduled readers. Reader activity occurs every 5–10 seconds;
10% of views also request local resources to model browser cache reloads. Connections
are bounded separately from readers. Scheduling delays, rejected offered work, and
request failures remain visible so an overloaded generator cannot establish capacity.

The local rehearsal uses the generated serving image with a two-core origin quota
and an isolated nginx cache fixture. CI retains numeric HTTP, cache, origin CPU/memory,
bandwidth, and cost-projection reports. Local results are recorded in
[`reports/load/`](../reports/load/). They do not verify Cloudflare cache behaviour,
Spain-region HTTPS latency, the actual IONOS VPS, mobile delivery, or actual billing.

ADR-0001 is still marked proposed pending G0 approval. Its 150–300 origin req/s
cold-cache estimate conflicts with task 4.7's <= 200 req/s limit; the test uses the
stricter limit until the owners reconcile it. Missing evidence stays unmeasured.
Keep task 4.7 open until the live environment, service targets, workload, monthly
traffic assumptions, and any capacity change receive the required approval and tests.
