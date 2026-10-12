# E3.4 load tests

Scope: define and rehearse task 4.7. E0.3 and E3.3 predecessor code is merged in
PRs #23 and #37. Their live approval/provisioning gates remain pending. These
scripts do not acquire a domain, provision infrastructure, deploy, purge a live
zone, or submit political content. ADR-0001 service targets are proposed until G0.

## Workload

`plan.json` defines 10,000 active readers with seeded, independent 5–10-second
navigation schedules. Scheduling is independent of response completion: a slow
response cannot silently lower offered traffic. Only a bounded number of HTTP
requests can be in flight; excess offered work is counted as dropped. Connection
reuse is an HTTP transport choice, not a count of visitors. The default uses four
Node workers, each with up to 1,024 in-flight requests. They partition the same
10,000-reader population, synchronize the start, and combine raw latency samples
before computing percentiles. The aggregate in-flight peak is labelled as an upper
bound (sum of worker peaks), not an observed simultaneous connection count.

- **Steady:** warm the finite URL/resource set; distribute initial reader activity
  over ten seconds, then maintain the same reader population for 60 seconds.
- **Cold cache:** replace the local cache container and its tmpfs; verify readiness
  through a noncached readiness endpoint outside the workload URL set, then run the same 60-second reader workload. Include every miss
  from the start of measurement; do not omit the initial cold period.
- **Burst:** retain a warm cache, bring all 10,000 readers into activity within one
  second, then run for 30 seconds. This intentionally creates a sharper initial
  spike than the nominal 1,000–2,000 req/s steady model.

Pages cover home, eight topics, sources, method, corrections, and two allowlisted
comparison-query variants. Query strings remain distinct cache keys, as in the
E3.3 runbook. Ten percent of page visits reload a bundle of five local resources
(CSS, two scripts, tokens, and the preview PNG). Expected sustained edge demand is
about 2,000 req/s: roughly 1,390 page views/s plus resource reloads. The start ramp,
finite duration, and burst change the measured average. This is a declared HTTP
workload, not a JavaScript/browser/network/device simulation. It neither downloads
original party programmes nor creates a visitor profile. It does not cover every
possible comparison query; obtain human approval for a broader key-distribution
model before live acceptance.

## Run locally

Requires Docker, Node 22+, and Python 3.12+ for tooling (the site remains a Python
3.14 project). No third-party load package or runtime dependency is installed.

```sh
docker build -t elecciones2026:load .
python3 ops/load/run.py --image elecciones2026:load --output build/load
node --test tests/load_behavior.cjs
PYTHONPATH=src python3 -m unittest discover -s tests -p test_load_report.py -v
```

`--seconds 20` shortens all phases for CI. Each phase still schedules 10,000
readers, with the 5–10-second activity interval unchanged. CI uploads the reports
and fails if the workload or resource collection cannot run; target failures are
recorded in reports rather than mistaken for release approval. Review them before
any capacity claim. A short CI run is not the full release workload.

The origin runs the existing pinned static image with a two-core quota, 300 MB
memory ceiling, read-only filesystem, dropped capabilities, and tmpfs. The edge
runs the same image with a test-only cache configuration. Only the edge test port
is published, on loopback. A separate Docker network and random container names
avoid existing previews; cleanup removes owned containers/network. A hard-killed
runner can leave these resources; remove only the `e34-*` resources for that run.

`edge.conf` is a cache fixture with request coalescing, not a Cloudflare emulator.
It honors origin cache headers; it does not reproduce the E3.3 host TLS proxy,
Free-plan features, cache geography, expiry cycles, query cardinality, or WAF.
The short runs fit inside the 300-second HTML TTL. Repeat long enough to cover
several expirations before production acceptance. The client does not retry,
follow redirects, disable TLS verification, or discard HTTP error responses.

## Measurements and interpretation

### E4.4 quiz fixture

Build an explicit private mock image and select the quiz workload:

```sh
docker build --build-arg QUIZ_MODE=mock -t elecciones2026:quiz-load .
python3 ops/load/run.py --image elecciones2026:quiz-load --quiz --output build/quiz-load
```

The quiz workload requests only `/cuestionario/` and its generated local resources.
The same reader schedules, reload rate, and limits apply. An unavailable build is
rejected because it has no scoring bundle. This is HTTP delivery evidence; the
separate `tests/quiz_performance.cjs` runner measures browser readiness with fictional
data. Neither run executes scoring on the server.

The origin normally disables request logs. The harness replaces that directive
only in the temporary configuration of its isolated fixture container. Its numeric
log includes timestamp, status, elapsed time, and response bytes only, restricted
to the harness marker. It retains no paths, addresses, answers, or identifiers.
The preview and production configuration remain unchanged. Never enable this
fixture override on a visitor-serving origin.

Reports contain the plan, image identity, revision, host observations, and per-phase:

- Offered, sent, completed, dropped, and failed requests; reader count, peak in-flight
  requests, per-second achieved traffic, and load-generator process RSS/max worker event-loop delay.
- Response p95 and p95 from intended schedule to response completion. The latter
  includes generator scheduling delay; request deadlines include connection/TLS
  time. Dropped work has no latency sample and remains a separate failing check.
- Cache statuses observed from `X-Load-Cache` locally or `CF-Cache-Status` on a live
  run. Only `HIT` counts as a fresh hit; unknown headers never become a success.
  Report aggregate, HTML, and resource ratios separately, including cold misses.
- Independent origin request count, one-second peak, response p95 (nginx records time at millisecond resolution), and response
  body bytes from numeric nginx test observations. Only the harness User-Agent is included; warmup and Docker health probes are
  excluded. No URLs/IPs are retained.
  A fully warm cache can send zero origin requests: origin p95 is then unmeasured.
- Sampled origin container CPU (Docker CPU percent divided by two allocated cores)
  and memory. This is not whole-VM CPU; sub-sample spikes can be missed.
- Client and origin response-body bandwidth. Body bytes are compressed when the
  server uses gzip; they exclude HTTP/TCP/TLS overhead and are a lower bound on
  billed/network traffic. Cost is a projection from explicit monthly scenario
  hours, included egress, and fixed costs. Proposed ADR inputs are not invoices.
  Unknown excess-traffic prices cannot produce a successful budget result.

`report.py` compares numeric evidence against ADR-0001 and task 4.7. It uses the
stricter <= 200 origin req/s limit despite ADR's 150–300 req/s cold-cache estimate.
Normal/burst latency, HTTP 4xx/5xx, resource/HTML/aggregate hit ratios, CPU, and
memory remain distinct checks. Network failures, drops, reader shortfalls, or p95
scheduling delay >100 ms invalidate a capacity claim. No monthly uptime, browser
mobile delivery, or production cost is inferred from this test.

## Live acceptance and capacity response

No approved public environment is configured in this repository. Before a live
run, the infrastructure owner must provide the approved target, test window,
load-generator hosts, G0/G3 and applicable G4 evidence, artifact digest, cache rules,
query distribution, current cost/egress allowances, and resource-observation access.
Keep staging authenticated; do not expose private pilot content to make a load test
work. Do not commit credentials, source files, or private endpoint evidence.

`client.cjs` also supports an explicitly configured `approved-live` HTTPS origin
and a non-secret `authorization_reference` in its input JSON. The caller supplies
`pages`, `assets`, and one `scenario` together with the plan fields. Run
`node ops/load/client.cjs INPUT.json OUTPUT.json` only in the approved test window.
It reads actual Cloudflare cache statuses. The local orchestrator never runs a
remote test. Collect independent nginx numeric request timings, host/container
CPU/memory, Cloudflare aggregate cache metrics, and bandwidth/billing observations
for each phase; use `origin_metrics` and `evaluate` in `report.py` to evaluate them.
Do not treat client cache misses as independently measured origin request counts.

The owner must perform and record an approved cold-cache purge immediately before
that phase, separate warmup from measurement, verify the workload completes without
generator loss, and retain platform/region, duration, revision, artifact, purge,
resources, billing, and per-check results. Run sustained phases long enough to
cover several HTML expirations and repeat from external Spain-region generators.
Reconcile stricter task limits with ADR-0001; obtain target/cost/workload approval.
Only then can task 4.7 be completed.

If the generator drops work, distribute the same seeded reader population across
multiple generators and preserve total offered traffic. Do not lower the reader
count or omit queued/dropped requests to obtain a pass. If origin metrics fail,
inspect cache eligibility, variant cardinality, expiry/coalescing, and connection
reuse. Propose a larger VM or separate static origin only after measuring the
bottleneck; provide a current cost estimate within EUR 50/month and rerun all
phases after owner approval. No capacity upgrade is executed by these scripts.

References: [Node HTTP agents](https://nodejs.org/docs/latest-v22.x/api/http.html#class-httpagent),
[nginx proxy caching and cache locks](https://nginx.org/en/docs/http/ngx_http_proxy_module.html),
[Cloudflare cache statuses](https://developers.cloudflare.com/cache/concepts/cache-responses/).
