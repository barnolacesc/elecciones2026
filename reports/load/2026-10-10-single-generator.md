# E3.4 local load rehearsal

Date: 2026-10-10T12:10:55.968038+00:00. Revision: `cf44b59adb5fc1fbd8354648d4dbb96b1606a7ef`.

Superseded diagnostic run: origin observations include Docker health probes; use the final report for workload-only origin/cost evaluation. The burst drop count remains evidence of generator saturation.

This is a Docker cache-fixture observation. It does not establish Hetzner/Cloudflare capacity.

| Scenario | Readers | Offered req/s | Completed req/s | p95 ms (scheduled) | 5xx | Cache HIT | Origin peak req/s | Origin CPU peak % | Origin body MB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| steady | 10000 | 2025.3 | 2025.3 | 4.3 | 0.000% | 99.99% | 18 | 0.6 | 0.12 |
| cold-cache | 10000 | 2025.3 | 2025.3 | 4.5 | 0.000% | 99.98% | 19 | 0.4 | 0.14 |
| burst | 10000 | 2292.6 | 2226.5 | 41.2 | 0.000% | 100.00% | 1 | 0.0 | 0.02 |

## Evaluation

- steady: Local measured checks pass.
- cold-cache: Local measured checks pass.
- burst: dropped_requests require investigation.

Cost: projection_only; projected origin body egress 4.96 GB/month, projected monthly EUR 16. Inputs are proposed assumptions, not invoices.

## Limits and next action

- Local nginx caching is a fixture, not Cloudflare. No public DNS/TLS, geography, WAF, or live Hetzner evidence.
- The origin has a two-core quota; Docker shares a host with the generator and edge. It is not a dedicated 2-vCPU/8-GB VM.
- HTTP workload samples page navigation and 10% resource reloads; it does not execute JavaScript, fetch original programmes, or measure mobile rendering.
- CPU is sampled container CPU divided by its two-core quota; whole-VM CPU, sub-sample peaks, monthly availability, and billing are unverified.
- ADR-0001 is proposed pending G0 approval. Task 4.7 uses a stricter 200 origin req/s limit than ADR cold-cache estimates.
- Any dropped requests or large scheduling delays invalidate capacity claims; distribute generators before a live rerun.
- If origin targets fail, inspect cache-key cardinality/revalidation, then propose an owner-approved capacity increase within EUR 50/month and rerun.
