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

The Spanish MVP is a static site. Comparison runs in the browser. No user account, database, PDF parser, editorial secret, or visitor profile is required. Docker runs the same serving model in local preview and production. Use a non-privileged user, read-only filesystem, resource limits, and a pinned, scanned image in production. FastAPI is a future option only if a separate change needs server logic.

Build phone layouts first at 360–430 CSS px. Stack party cards, keep source links near claims, use 44-px touch targets, and avoid horizontal scroll. Add wide layouts as progressive enhancement. Aim for WCAG 2.2 AA and verify the actual flow.

## Edge, host, and scale

Cloudflare Free will manage DNS and proxy traffic. Cache fingerprinted assets for a long time. Revalidate HTML and correction pages quickly. Check actual plan features before setting WAF or rate limits. Use targeted challenges only for abusive patterns. A challenge for all readers would harm access and discovery.

The target origin is a Hetzner VM near 2 vCPU and 8 GB RAM. A static cache can absorb many readers, but 10,000 concurrent visitors is not the same as 10,000 origin requests per second. Benchmark cache-hit ratio, p95 latency, errors, memory, bandwidth, and cost. Test bursts, cold cache, and origin loss. Scale or change hosting if the measured service level fails.

Protect origin access where feasible. Expose only required ports. Use HTTPS, restrictive headers, updates, health checks, logs without personal data, and a retained prior artifact. Keep source records and build inputs in a separate backup. Test restoration before launch.

## Decisions deferred

Confirm domain, Cloudflare plan features, VM region, exact server image/digest, release automation, source file format, source rights, and measurable load target before public release.
