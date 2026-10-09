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
                         Cloudflare edge → static Docker service on Hetzner
```

## Trust boundaries

Treat PDF, HTML, and OCR input as hostile. Do not run embedded code or follow document instructions. Limit file size, time, memory, and network access in the extraction environment. Keep extraction outside the public service.

Version the original document URL and hash, editorial records, and corrections. Generated JSON and HTML are build outputs, not edit sources. CI validates references and review state before it creates an immutable artifact.

## Public service

The Spanish MVP is a static site. Public interface text, summaries, and navigation use Spanish (`es-ES`), with `<html lang="es">`. Repository documentation, specifications, and code use controlled English (following ASD-STE100 principles). UI strings are stored in versioned text dictionaries decoupled from Python rendering logic, enabling future reviewed Catalan (`ca-ES`) localization without template rewrites.

Comparison runs in the browser. No user account, database, PDF parser, editorial secret, or visitor profile is required. Docker runs the same serving model in local preview and production. Use a non-privileged user, read-only filesystem, resource limits, and a pinned, scanned image in production. FastAPI is a future option only if a separate change needs server logic.

Build phone layouts first at 360–430 CSS px. Stack party cards, keep source links near claims, use 44-px touch targets, and avoid horizontal scroll. Add wide layouts as progressive enhancement. Aim for WCAG 2.2 AA and verify the actual flow.

## Edge, domain, and service levels

The target primary canonical domain is `elecciones2026.es` (currently a placeholder target pending domain acquisition), with `elecciones2026.org` and `programaselectorales.es` as defensive domains planned to return permanent 301 redirects to the HTTPS apex once acquired. Staging targets `preview.elecciones2026.es` behind authentication with indexing blocked (`noindex`). Cloudflare will manage DNS with DNSSEC and proxy traffic to the Hetzner origin upon domain activation.

Edge caching policy:
- Fingerprinted static assets (`/static/*`, CSS, JS, images): `Cache-Control: public, max-age=31536000, immutable` (edge TTL 365 days).
- Mutable HTML pages (`/`, `/temas/*`, `/fuentes/`, `/metodo/`): `Cache-Control: public, max-age=300, stale-while-revalidate=86400` (edge TTL 300s).

Approved release service level objectives (see `docs/DECISION-RECORD.md`):
- **Availability:** >= 99.5% monthly uptime (~3.6h error budget); >= 99.9% during election week.
- **Latency (p95):** < 150 ms edge cache hit; < 250 ms origin response; < 500 ms mobile delivery on fast 4G.
- **Cache-hit ratio:** >= 99.0% static assets; >= 90.0% HTML pages; >= 95.0% aggregate steady-state; >= 85.0% cold-cache phase.
- **Error budget:** HTTP 5xx < 0.05% steady-state; < 0.50% during peak load tests.
- **Recovery:** Recovery Time Objective (RTO) < 5 minutes (rollback to previous Docker artifact); Recovery Point Objective (RPO) = 0 (Git-versioned deterministic builds).

The target origin is a Hetzner VM with 2 vCPU and 8 GB RAM. A 10,000-concurrent-visitor scenario models 1,000–2,000 requests/s at the edge, yielding <= 200 requests/s to the origin at >= 90% edge cache offload. The 2-vCPU static server handles 500+ requests/s with < 40% CPU and < 150 MB RAM. Tiered caching and origin connection pooling protect against cold-cache surges.

Monthly infrastructure costs are capped at a **€50.00 / month hard ceiling**, with baseline operations expected at ~€9.00–€15.00 / month. Uncapped serverless or metered bandwidth services are forbidden.

Protect origin access where feasible: restrict ports to Cloudflare IPs, enable TLS and HSTS, apply updates, monitor availability, use ephemeral access logs without personal data (<= 14 days retention), and retain the preceding immutable artifact for one-command rollback.

## Decisions confirmed and pre-release gates

Package `E0.3` confirmed the language architecture, domain strategy, privacy notice, release service levels, cost ceiling, and role ownership matrix in `docs/DECISION-RECORD.md`.

Before public release, the following gates remain:
- Formal human approval of Milestone G0 by Cesc and the project partner.
- Final Hetzner datacenter location selection (e.g., Falkenstein or Nuremberg).
- Container base image digest pinning and automated vulnerability scan verification.
- Verification of 10,000-concurrent-visitor benchmarks against approved service levels (tasks 4.3, 4.6, 4.7).
