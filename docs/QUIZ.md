# Programme alignment quiz structure

Roadmap packages: E4.2 technical foundation and E4.3 phone flow. The user authorized private mock implementation before G4/E1.4. This authorization does not approve political content or public release.

## Try the mock quiz

From this worktree:

```sh
QUIZ_MODE=mock PORT=127.0.0.1:48775 docker compose up --build -d
```

Open `http://localhost:48775/cuestionario/`. The page labels every example as fictional. Its 16 generic test elements have no political claims, party documents, invented citations, or editorial review badges. Example A and B have complete numeric vectors. Example C has an explicit source gap and no score. The topic labels come from the existing taxonomy.

The flow supports start, previous/next, skip, optional answer review, editing, local topic weights, results, contribution/source details, reset, and generic sharing. Selecting an answer does not advance. “Ver resultado” opens results directly; unfinished items count as skipped. Visitors can choose “Revisar respuestas” before finishing or edit answers from results. Eight answers across four topics are required for an aggregate. Answers stay in page memory and disappear on reset, reload, exit, or back/forward-cache restoration. The demo is not indexed or listed in the sitemap.

Without `QUIZ_MODE=mock`, the default build shows an unavailable page and includes no mock scoring bundle. Rebuilding without mock mode removes older generated quiz bundles. The mock mode is for a private preview only; `noindex` is not an access control.

The browser regression checks portrait and landscape layouts, doubled root text size, text spacing, 320px reflow, expanded explanations, and keyboard focus. Reduced-motion mode uses immediate scrolling. These automated mock checks do not cover native 400-percent browser zoom, real citation layouts, screen readers, or the complete WCAG audit. See E4.3 tasks 3.3–3.5 for remaining acceptance work.

Result details show answer labels, fictional or sourced support/rejection, item agreement, and each topic's share of the total in Spanish. Score changes say whether the percentage rose, fell, or stayed the same. [QUIZ-COMPREHENSION.md](QUIZ-COMPREHENSION.md) provides assigned fictional exercises, facilitator checkpoints, and an empty aggregate record for voluntary human checks. No participant results or public copy approvals are recorded yet.

## Data contract for later real documents

The structure already accepts `--quiz-mode reviewed --quiz-file <authoring-file>`. The current repository has no approved real quiz file. Do not copy the mock file and change its mode flag: reviewed validation requires existing approved, election-matched statement and programme records, lawful sources, and genuine human review evidence.

Prepare those source records through the established editorial process first. Source extraction cannot approve content. Add a separate versioned quiz authoring file with these fields:

| Record | Fields |
|---|---|
| Set | `schema_version`, `method_version`, `taxonomy_version`, `version`, `mode: reviewed`, target `election_id`, `review_status`, `reviews`, `items`, `parties` |
| Item | unique kebab-case `id` and `measure_id`, `topic_id`, neutral Spanish `text`, `qualifications`, `selection_rationale`, `review_status`, `reviews` |
| Party | approved `id` and `name`, `positions` covering every item |
| Scored position | `item_id`, `status: support` or `reject`, matching `value: 1` or `-1`, approved `statement_id`, `review_status`, `reviews` |
| Gap | `item_id`, explicit `status`, `value: null`, neutral Spanish `reason` |

Gap statuses are `missing`, `partial`, `conflicting`, `unverified`, and `replaced`. All parties in the election's source register must appear. A party needs a valid position for all 16 items to receive an aggregate; at least two complete parties are needed. Each topic must contain two items. No gap is converted to opposition.

Reviews use the existing `ReviewRecord` contract: distinct human reviewers, approved verdicts, valid dates, and retained evidence references. They apply to the set, each item, each mapping, and underlying statements. Placeholders and automated reviews do not count. The build resolves programme ID, official URL/version/checksum, exact page/section, qualifications, rights status, and review date from existing records. It rejects unreviewed, fictional, replaced, cross-election, conflicting, or correction-stale numeric mappings. Reviewer details are not copied to the public bundle.

The frontend and engine are shared between modes. Replacing the mock data means preparing reviewed records and building the reviewed mode, not rewriting the quiz. G4/E1.4 and E4.1 review evidence are still required before real activation; G5 still requires independent fairness, full accessibility, user, infrastructure privacy, and release review.

## Verification

```sh
PYTHONPATH=src python3.14 -m unittest discover -s tests -p test_quiz.py -v
node --test tests/quiz_behavior.cjs
PYTHONPATH=src python3.14 -m unittest discover -s tests -q
```

With development Playwright installed and the private preview running:

```sh
QUIZ_TEST_URL=http://127.0.0.1:48775 node tests/quiz_browser.cjs
QUIZ_TEST_URL=http://127.0.0.1:48775 QUIZ_PRIVACY_EVIDENCE=build/quiz-privacy.json node tests/quiz_privacy.cjs
QUIZ_TEST_URL=http://127.0.0.1:48775 node tests/quiz_accessibility.cjs
```

`PLAYWRIGHT_MODULE` can point to an existing Playwright module. `QUIZ_CHROMIUM` can select an existing test Chromium executable. The browser runner checks 320/360/390/430-px layout and targets, answer/review/edit/weights/reset, source/details access, no interaction requests, no console output, empty browser storage/cookies, tab isolation, cache-restore/reload, and no-script fallback. It does not establish WCAG conformance or edge/origin zero tracking. CI runs the Python and numeric tests plus the rendered browser checks.

The runner also intercepts a fixture bundle to test a corrupt-version error without publishing corrupt data. `QUIZ_UNAVAILABLE_URL` can point to a separate default build for the unavailable-state check. CI serves that build beneath its test server and verifies that it offers method/source links without loading the scoring bundle or showing dead answer controls.

Numeric tests cover exact ties, neutral versus skip, sparse answers, missing party positions, weight changes, topic denominators, bounds against 125 permitted completions, sensitivity, revisions, malformed data, party permutation, and polarity invariance. Browser state and network tests use only fictional data.

[QUIZ-ACCESSIBILITY.md](QUIZ-ACCESSIBILITY.md) records all A/AA criterion IDs,
partial automated evidence, proposed non-applicability, and the remaining native
zoom/screen-reader review. The accessibility runner uses actual keyboard navigation
and unrounded opaque-text contrast; its sanitized CI artifact is
`build/quiz-accessibility.json`. This does not establish full conformance.

`tests/quiz_privacy.cjs` compares static resources across assigned answer sets, checks zero requests during the complete interaction, and verifies generic native/copy/manual sharing. It intercepts nonpolitical transport metadata inside the test browser to exercise the actual source-link renderer and confirm no referrer or opener. That metadata explicitly has no editorial review or source rights; the offline validator would reject it. It is never built, published, or treated as a real citation. Set `QUIZ_PRIVACY_EVIDENCE=build/quiz-privacy.json` to retain sanitized counts and resource paths, without answers, scores, participant identifiers, or request headers. CI retains this artifact.

The shared Nginx origin disables access and request-error logs for all routes because quiz delivery uses shared assets. Docker integration checks verify successful and missing-file fixture requests do not enter container logs; they do not print raw logs. Edge/CDN, host logging, monitoring, and error-service privacy remain unverified and must pass the separate G5 review. Startup diagnostics and aggregate health checks are available; request-level debugging must use isolated fictional fixtures rather than enabling visitor logging.

No public deployment, merge, or content approval is performed by these commands. Release and rollback must follow the existing project gates, including withdrawal of invalidated content rather than restoring an unsafe old set.

[QUIZ-RELEASE.md](QUIZ-RELEASE.md) assembles the G5 evidence, outstanding decisions,
deployment sequence and functional/source-defect recovery distinction. Run
`python3.14 ops/quiz_smoke.py --mock-image quiz-preview:latest` for an isolated
fictional rollback/withdrawal rehearsal; this leaves the existing preview running.

## Local delivery rehearsal

With the private mock preview running, use the same browser-tooling environment as
the regression checks:

```sh
QUIZ_TEST_URL=http://127.0.0.1:48775 node tests/quiz_performance.cjs
python3.14 ops/load/run.py --image quiz-preview:latest --quiz --output build/quiz-load
```

The browser runner measures five cold and five warm visits at each of 360, 390,
and 430 CSS px, with 150-ms simulated latency, 1.6-Mbit/s download, 750-kbit/s
upload, and fourfold CPU slowdown. Readiness requires the complete bundle and the
start control; the runner then verifies that the question controls work. It writes
`build/quiz-performance.json`. CI retains these synthetic observations. A missed
500-ms proposed target is reported, not converted into service approval. Five
samples make the reported p95 the maximum sample, not a population estimate.

The HTTP harness runs isolated steady, cold-cache, and burst scenarios with 10,000
scheduled readers. See [the harness guide](../ops/load/README.md) for numeric-only
fixture logging, resource limits, and interpretation. Browser emulation and local
cache fixtures do not establish real mobile, CDN, dedicated-VM, billing, or approved
programme-bundle performance. See [the measured record](QUIZ-PERFORMANCE.md).
