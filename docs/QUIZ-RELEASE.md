# E4.4 quiz release review

Status: **private mock only; public release not approved**. This record assembles
existing evidence for tasks 4.6–4.7. It does not grant a release decision.

## Evidence and outstanding decisions

| Requirement | Evidence available | Still required before G5 |
|---|---|---|
| Method and Spanish copy | Proposal, design, four specifications; local mock feedback | Recorded method, selection-protocol and editorial copy decisions |
| Real question set | Offline provenance/rights/review validator and fictional balanced fixture | Approved target-election programmes, 16 reviewed items and mappings, exact citations, all-party selection register |
| Prerequisites | Local mock work explicitly authorized | Applicable G0 rights decisions, E1.4 and G4 evidence |
| Arithmetic | Local contracts for skips, ties, bounds, weights and invariance | Review acceptance of the method and fairness audit of real selection/exclusions |
| Browser privacy | Five fixture transport/share/source cases; memory-only regression | Delivery-provider, host, monitoring and error-system zero-tracking acceptance |
| Accessibility | 35 keyboard/semantic/text-contrast checks and layout matrix | Native zoom, VoiceOver/Safari, NVDA/Firefox, native-control contrast and full criterion audit |
| Comprehension | Assigned fictional exercises and empty aggregate record | Voluntary task outcomes, fixes and retests; real citation inspection |
| Performance | Local browser and steady/cold/burst observations | Approved targets; resolve cold-load and burst failures; representative provider/VM and reviewed-bundle measurements |
| Recovery | Local mock rollback/withdrawal rehearsal | Approved still-valid recovery set, production-controller/edge rehearsal and timed recovery |
| Publication | Static nonprivileged runtime and immutable release controller | Successful CI/scan, approved digest, owners, target, cache/privacy configuration and explicit G5 release decision |

Read [accessibility](QUIZ-ACCESSIBILITY.md), [privacy/data contract](QUIZ.md),
[performance](QUIZ-PERFORMANCE.md), and [comprehension](QUIZ-COMPREHENSION.md)
for exact observations and limits. Current task completion remains 9/22.

## Private recovery rehearsal

With the existing Docker mock image available:

```sh
python3.14 ops/quiz_smoke.py --mock-image quiz-preview:latest --output build/quiz-release.json
```

The runner inspects the immutable local mock image identity, rejects a non-mock
bundle, and uses a random owned container on a separate loopback port. It builds
a candidate with a nonpolitical HTML marker, switches A → B → A, and verifies
byte-identical restored quiz HTML. It checks complete script delivery, cache
headers, UID 101 and read-only serving. It then builds the default unavailable
artifact and verifies that scoring scripts disappear from both HTML and origin
paths, answer controls are absent, and method/sources/corrections remain available.

The script cleans up only its own containers and temporary image tags. It does
not touch the human preview, production Compose state, a registry, or public DNS.
The unavailable build uses the historical `es-gen-2023` rehearsal explicitly;
neither mock image represents approved real content. CI retains sanitized checks,
image identities, a restored-page hash and local rollback duration. No political
answers, participant data, source files or editorial approvals enter the report.

This checks artifact/recovery mechanics. It does not exercise a live registry,
the production controller, CDN invalidation or a still-valid approved real set.
The existing `ops/smoke.py` separately rehearses the generic release controller.

Local run on 2026-10-12: **19 checks passed**, with byte-identical mock rollback
in approximately **0.6 seconds**. All withdrawn scoring paths returned HTTP 404.
The owned fixture containers/tags were removed; the original preview was retained.
Remote CI and public recovery have not run here.

Verification after adding the rehearsal: the full Python suite passed (327 tests,
two existing skips), script compilation and whitespace checks passed, and strict
OpenSpec validation passed. The retained mock preview reports healthy. Negative
importer fixtures intentionally print blocked-URL/hash-mismatch messages; these
are expected checks, not suite failures.

## Deployment sequence after the release decision

1. Record the target election, approved question-set version, rights/correction
   status, owners and all G5 evidence. Resolve every substantive failure above.
2. Build the reviewed artifact twice from fixed approved inputs. Confirm identical
   hashes, no mock bundle, correct source coverage, and a static-only runtime.
3. Run CI and the security scan. Record the final Git revision, full immutable
   `repository@sha256:…` reference, build date and approval. Registry publication
   and production switching happen only through the existing authorized process.
4. Prepare a separately verified unavailable artifact for withdrawal. Validate
   that a functional recovery image still has valid sources, rights and reviews.
5. Follow [the operations guide](../ops/README.md#immutable-release-and-rollback)
   on the approved origin. Verify health and `/cuestionario/`, its complete bundle,
   source links, headers and absence of answer-dependent requests at origin/edge.
6. Invalidate mutable quiz HTML and any withdrawn assets through the reviewed edge
   procedure. Check fresh and stale-cache cases, then record the actual outcome,
   timing and approval reference without visitor-level observations.

No production target, registry digest, provider acceptance or human G5 approval is
recorded here. The local preview remains the concrete artifact for review.

## Functional regression versus invalid source recovery

A functional regression can restore a preceding image only after its content
validity is rechecked. Source, rights or correction defects require withdrawal:
serve the unavailable quiz with method/correction access, then prepare a corrected
set and obtain fresh review. Never restore the invalid set as a fallback.

The generic `ops/release.py` restores its current image after an unsuccessful
switch. Therefore it cannot alone guarantee safe source-defect withdrawal when
that current image is invalid. Before a live withdrawal, operators must verify an
approved delivery procedure that prevents the invalid quiz being served even if
the disabled-origin switch fails. Retain method/correction access during that
procedure. This provider/controller rehearsal remains outstanding.

Origin withdrawal does not purge edge or browser caches. Include immutable bundle
URLs as well as HTML in the reviewed withdrawal procedure. Previously loaded tabs
can retain their local static data until reset, reload or exit; no remote deletion
or tracking mechanism is present. Record these limits and verify stale behavior
before release; the local rehearsal does not establish end-to-end recovery time.
