# E4.3 quiz phone-flow gate audit — 2026-10-24

Roadmap package: **E4.3** (`programme-alignment-quiz`, tasks 3.3–3.5). This is an evidence and handoff record, not a completed accessibility, editorial, privacy, or release review. Scope is the *private fictional mock* quiz on `origin/main` at `fe5e05e` and its current test harness. No political answers, programme PDFs, or participant data were used.

## Collision and baseline check

At 2026-10-24 00:14 Europe/Madrid, `origin/main` was `fe5e05e`. Open PR #129 changes `site/quiz-ui.js`, `tests/quiz_browser.cjs`, and this change's `tasks.md`; it addresses result-set scope. Other open P2 PRs change the comparator, selection, sharing, and source-index surfaces. This audit changes only this new document. It does not infer that an open PR is reviewed or mergeable.

`docs/PRODUCT-ROADMAP-2023-2026.md` makes the source-verified 2023 comparator the first product gate. The quiz OpenSpec proposal and design remain drafts for human review. The mock technical implementation is permitted, but real quiz items, scored mappings, publication, and G5 acceptance are not established by that permission. Tasks 3.3–3.5 remain unchecked.

## What the current evidence does and does not establish

| Check | Evidence observed | Limit / required next evidence |
|---|---|---|
| 360/390/430-px question-to-result flow | `tests/quiz_browser.cjs` exercises start, 8 answers, skips, direct result, optional review/edit, weights, reset, source/method disclosures, target sizes, overflow, and no interaction requests at 320/360/390/430 CSS px. The latest checked PR #137 rendered-mobile CI job passed. | This is automated Chromium with fictional content, not a device or task-success observation. Repeat on actual phone Safari/Chrome and with approved source metadata before closing task 3.3. |
| Magnification and assistive operation | The browser runner includes landscape, doubled root text, spacing, 320-px reflow, and settled keyboard focus. `tests/quiz_accessibility.cjs` exercises keyboard/semantic/opaque-text contrast. `docs/QUIZ-ACCESSIBILITY.md` inventories the 55 A/AA criteria. | Native browser 400% zoom, VoiceOver/Safari, NVDA/Firefox, native-control/focus contrast, reverse navigation, and complete-process criterion decisions have no recorded pass. CSS text enlargement and a 320-px viewport are not native zoom evidence. Do not claim WCAG conformance. |
| Source inspection | The mock page provides disclosure and method controls; unavailable and corrupt-bundle fallbacks are covered in `tests/quiz_browser.cjs`. | Fictional fixtures cannot prove that a visitor reaches an exact official document, version, page/section, review date, and source gap with real long metadata. The approved real set is absent. Keep the citation task explicitly *not evaluated*. |
| Local-only answers | `tests/quiz_browser.cjs` and `tests/quiz_privacy.cjs` check no answer-triggered requests, empty storage/cookies/history, reload/second-tab isolation, and generic sharing under fictional inputs. The default generator mode is `unavailable`; mock is opt-in, and non-reviewed quiz pages are `noindex` (`generator.py`). | Browser tests do not establish edge/CDN, host, monitoring, or error-service no-retention. OpenSpec task 4.3 and the G5 operational privacy gate remain open. `noindex` is not access control. |
| Human comprehension | `docs/QUIZ-COMPREHENSION.md` provides fictional assigned-answer tasks and a blank aggregate-only record. | No participant attempt, approved acceptance rule, or retest is recorded. Task 3.5 cannot be checked from automated score assertions. |
| Current CI | PR #137: rendered mobile and validation jobs passed; Docker serving-image job failed, so overall CI failed. PR #129 likewise has passing rendered/validation jobs and a failed Docker job. | Passing component checks are not a full green gate or a human review. Do not attribute the Docker failure to quiz code without a separate scan diagnosis. |

## Bounded next acceptance pass (no publication)

1. After the source register, rights, item selection, mapping, and dual editorial reviews exist, build a **private** reviewed 2023 quiz; retain its set/method versions and approved source locators in a restricted test record. Never substitute the provisional or mock set for that evidence.
2. At each of 360, 390, and 430 CSS px, follow one shared-link entry through start, a numeric answer, skip, optional review/edit, result, source disclosure, and generic share. Record device/browser, viewport, control dimensions, overflow, focus, exact-source success, and any failed CTA. Repeat 320-px reflow, native 400% desktop browser zoom, landscape, 200% text enlargement, and text spacing.
3. Complete VoiceOver/Safari and NVDA/Firefox keyboard/reader paths, including errors and unavailable/no-script states. Resolve each applicable WCAG criterion finding and retest; keep non-applicability a reviewer decision, not an automated assumption.
4. Run the voluntary fictional-assignment comprehension protocol; retain only aggregate outcomes. Verify visitors distinguish neutral/skip/source gap and limits, and can explain an edited result. No personal political answers or session recordings.
5. Reconcile CDN/origin/monitoring privacy and G4/E1.4/E4.1/G5 human gates separately. The quiz remains unavailable by default; neither this audit nor passing CI authorizes enabling it.

## Reproduction and result

On this fresh worktree from `fe5e05e`:

- `node --check site/quiz-ui.js && node --check site/quiz-engine.js` — PASS.
- `node --test tests/quiz_behavior.cjs` — PASS, 11/11 numeric contract tests.
- Browser tests were **not rerun locally**: no private preview was listening on `127.0.0.1:48775`; this host has no `python3.14` or Docker executable, and no local Playwright installation was found. The rendered-mobile evidence above is the linked CI job, not a local claim.
- `git diff --check` — PASS before this document; rerun after the edit.

References: `openspec/changes/programme-alignment-quiz/specs/quiz-mobile-flow/spec.md`, `openspec/changes/programme-alignment-quiz/tasks.md`, `docs/QUIZ-ACCESSIBILITY.md`, `docs/QUIZ-COMPREHENSION.md`, `docs/QUIZ.md`, and [PR #137 CI](https://github.com/c2ventures/elecciones2026/actions/runs/40031660201). This record does not change task checkboxes because their acceptance evidence is incomplete and PR #129 is already editing that task file.
