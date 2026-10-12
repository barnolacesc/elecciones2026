# E4.4 local quiz delivery evidence

Date: 2026-10-12. Scope: private fictional quiz fixtures. G5 acceptance remains open.

## Browser readiness

`tests/quiz_performance.cjs` measured the current mock Docker preview on loopback.
Chromium used 150-ms simulated latency, 1.6-Mbit/s download, 750-kbit/s upload,
fourfold CPU slowdown, and five samples for each cache/viewport case. Readiness
requires the scoring bundle, engine, UI, and start control. Starting a question
also passed in every sample. The p95 below is the maximum of five samples.

| Width | Cold readiness p95 | Warm readiness p95 | Proposed <500-ms target |
|---|---:|---:|---|
| 360 CSS px | 633.3 ms | 41.9 ms | Cold missed; warm met |
| 390 CSS px | 595.2 ms | 31.0 ms | Cold missed; warm met |
| 430 CSS px | 609.8 ms | 28.4 ms | Cold missed; warm met |

The quiz page now preloads the existing imported design-token stylesheet alongside
the main stylesheet. Resource observations confirm that the tokens start with the
other head resources instead of waiting for a stylesheet import round trip. No
new remote request, tracking, or browser storage is added.

An earlier run measured cold p95 values of 862.3/740.3/745.1 ms and warm values of
32.6/33.3/28.4 ms at the same widths. It overlapped the load rehearsal; the current
browser measurement ran without that load. These are different shared-host
conditions, so the numerical difference cannot establish the optimization's effect.
The current first visits still miss the proposed target. Retained local observations
are `build/quiz-performance-before.json` and `build/quiz-performance.json`.

## HTTP load rehearsal

The initial full rehearsal used 10,000 scheduled readers, 60-second steady and
cold-cache phases, and a 30-second burst. Steady/cold scheduled response p95 was
5.0/3.2 ms with zero dropped requests or network errors. Burst p95 was 393.2 ms,
with 262 dropped requests and 211 network errors. No HTTP 5xx was observed. The
burst fails the measurement checks and does not support a capacity claim.

That image preceded the stylesheet preload. Its discovered head resource set did
not include the imported token stylesheet. A separate short current-image run
includes that stylesheet; it is a smoke rehearsal, not the full acceptance workload.
The initial report retains image identity
`sha256:6bcc8c4523e56f26664439dd06836a4d0deb557ce17884fd7cd01650bc035ea6`.
Full and current reports are retained locally in `build/quiz-load/` and
`build/quiz-load-current/`.

The current image is
`sha256:688d63983c476dc8d5e308fc96be50d8065b9c43277b7c34a51a08ef82886b92`.
Its short run requests the quiz page and seven local resources, including tokens.
All three phases last 20 seconds; browser regression processes also share the host.

| Current scenario | Scheduled response p95 | Dropped requests | Network errors |
|---|---:|---:|---:|
| Steady | 9.1 ms | 0 | 0 |
| Cold cache | 3.6 ms | 0 | 0 |
| Burst | 464.3 ms | 171 | 449 |

Measured steady/cold checks pass. Burst checks fail again; the short run is not
evidence that the first run's failure was resolved. Neither run measures scoring
latency, which remains local in the browser.

The origin has a two-core quota and 300-MB cap on a shared Docker host. It is not
the dedicated 2-vCPU/8-GB environment. The local Nginx edge is a cache fixture.
Only numeric fixture request observations are enabled in an isolated temporary
origin configuration. Visitor-serving origin logs remain disabled.

## Verification and limits

Python quiz build/provenance checks: 17 passed. Load-report/configuration contracts:
8 passed. Load-client contracts: 5 passed on an uncontended rerun; two short timing
cases initially failed during simultaneous load/browser CPU emulation. Complete
mock browser layout/flow checks and all five privacy cases passed after the preload.
Strict OpenSpec validation, JavaScript syntax, and whitespace checks passed.
CI now retains browser performance observations; remote CI has not run here.

Local HTTP excludes production DNS, TLS, CDN geography, and provider behavior.
Synthetic browser data does not establish real-device performance or the size of
approved programme bundles. Cost projections are assumptions, not billing evidence.
Service targets need approval, first-visit delivery needs improvement, and burst
measurement needs distributed generators before live acceptance. Task 4.5 remains
open. No application scoring API, database, source parser, or editorial credential
was added to the public runtime. No public deployment or release approval occurred.
