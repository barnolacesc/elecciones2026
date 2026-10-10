# E3.4 observed local load evidence

These reports observe the generated static image on Docker Desktop, not an approved
Hetzner/Cloudflare release. Every run schedules 10,000 readers in steady (60 s),
cold-cache (60 s), and burst (30 s) phases. The fixture has only 19 cache keys and
fits inside the HTML TTL; it cannot demonstrate worldwide edge offload, query-key
cardinality, expiry-cycle traffic, mobile delivery, or production capacity.

| Record | Generator capacity | Burst dropped requests | Use |
|---|---|---:|---|
| [Single generator](2026-10-10-single-generator.md) | 1 × 512 in-flight requests | 1,983 | Superseded diagnostic; origin counts include health probes. |
| [Four workers, initial limit](2026-10-10-four-workers-512.md) | 4 × 512 | 129 | Shows remaining generator saturation; workload-only origin observations. |
| [Final rehearsal](2026-10-10-final.md) | 4 × 1,024 | 0 | Final measurements; all offered work completed without network/HTTP errors. |

The final run completed 314,471 HTTP requests. Four workers partition the population,
not multiply it. Splitting workers changes deterministic shard seeds; the two
four-worker runs share the same offered workload and differ in request capacity.
The one-worker baseline uses the same model but a different seeded schedule.

The JSON counterparts retain each plan, image ID, revision, metric breakdown,
per-check results, and explicit limits. The later runs also fingerprint the harness
sources. The revision identifies the serving artifact's source/base commit; the
harness was still in the working branch during observation; the final fingerprints
match the harness snapshot committed in `5fbc02c`. A later CI readiness fix checks
HTTP proxy/origin readiness without warming workload URLs; it does not change the
reader model or measurement definitions. Hardware timings vary;
reports are evidence, not deterministic golden-test fixtures.

Warm-cache steady/burst phases send zero workload requests to the origin, so their
origin p95 is unmeasured. The cold phase logs 19 origin requests. Nginx reports
origin timings in milliseconds; a recorded 0 ms means below its timestamp resolution,
not zero physical processing time. Warmup and Docker health probes are excluded
from the final origin observations. Origin CPU is sampled container CPU normalized
against its two-core quota, not whole-VM CPU.

Cost projections use proposed ADR-0001 fixed costs and illustrative monthly phase
hours. Zero warm-phase origin bytes in a short test do not predict traffic over
multiple TTL expirations. The projected EUR 16/month and traffic figures cannot
approve billing or establish the EUR 50/month ceiling. Supply current price/egress
allowances, longer live observations, and an owner-approved monthly workload.

Reproduce with [the runbook](../../ops/load/README.md). CI retains a shorter local
rehearsal separately; no public deployment or capacity change is authorized by
these observations. OpenSpec task 4.7 remains pending live evidence and approval.
