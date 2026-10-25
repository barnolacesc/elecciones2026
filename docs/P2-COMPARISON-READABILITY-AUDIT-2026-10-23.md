# P2 / E2.3–E2.5 comparison readability audit — 2026-10-23

Baseline: `origin/main` at `fe5e05e8e006d7ab1f395eb1495af49368ee8703`. This is a code-and-test audit, not a device observation, editorial review, accessibility conformance claim, or release decision. No political record, source file, approval, or public copy changes in this package.

## Why this is an audit-only package

Open PRs already own the comparison implementation surfaces: #125 changes `site/app.js` and `site/styles.css` for result focus; #133 changes `src/elecciones2026/provisional2023.py` for the private home entry; #134 changes `site/pilot-2023.js` for stale-link selection; #135 changes `site/pilot-2023.css` for citation targets. #128 owns sharing behavior. This pass does not edit those files or the shared `mvp-programme-comparison/tasks.md` touched by #125/#128/#135. These PRs are unmerged at audit time; their proposed fixes are not baseline behavior.

## Observed contract and bounded findings

1. **Two different comparison paths need separate acceptance evidence.** The main comparator's `site/app.js` renders a measure heading, summary, two party cards, and a relationship callout (`renderMeasureGroupHtml`, lines 1091–1150); `site/styles.css` stacks `.measure-cards` into one column below 760 px (lines 453–457, 1314). The private provisional 2023 path in `src/elecciones2026/provisional2023.py` builds a measure heading and cards, but no reviewed relationship summary (lines 72–108). Its mobile `.cards` rule stacks below 500 px (`site/pilot-2023.css`, lines 617–624). Neither path's success proves the other's readability. Do not synthesize a comparison summary for provisional, unreviewed positions.
2. **Selection-to-results orientation is still an open integration point.** On baseline main, `site/app.js` scrolls `#measures-container` after form submit (lines 1299–1300), while the results heading in `site/index.html` is screen-reader-only (lines 161–164). Scrolling is not a measured keyboard or screen-reader announcement. #125 proposes focus handling; verify its merged behavior against the generated 2023 page, including empty and error states, before closing E2.5.
3. **Small secondary text is a readability test target, not a proven failure.** Main comparison summaries use `var(--font-size-sm)` (`site/styles.css`, `.measure-summary`); provisional locators use 0.85rem and qualifications 0.9rem (`site/pilot-2023.css`, `.locator` and `.qualification`). Source location and conditions are substantive context, so test at default text size and 200% zoom/reflow on 360/390/430 px. Do not enlarge only the headline while leaving provenance hard to read. #135 addresses citation touch targets, not all typography or comprehension.
4. **Existing automation does not establish human task success.** `tests/test_measure_comparison.py` checks DOM structure, citation attributes, CSS presence and synthetic fixture content. `tests/test_provisional_2023_browser.py` exercises 360/390/430 px and overflow in Chromium, but uses a provisional generated corpus. `openspec/changes/mvp-programme-comparison/tasks.md` task 3.5 remains unchecked and explicitly calls for physical-device, screen-reader and participant evidence. A source link opening and a zero-overflow assertion do not establish that a reader can find a qualification or interpret a missing record.
5. **The real-corpus boundary remains separate.** The MVP task record states the default 2023 artifact had zero published positions/relationships after unsupported approvals were withdrawn; #42/#70/#100 retain source, rights and authentic review work. Readability acceptance of reviewed political claims cannot be extrapolated from static fictional HTML in `site/index.html`, provisional claims, or a pending-content preview. Keep the 2023 election label and pending state visible in every tested route.

## Next independent acceptance run after the overlapping PRs settle

- Build the exact private 2023 artifact from a recorded commit and content hash. Record whether it has zero approved claims or an authentically reviewed corpus; do not use provisional material as approved content.
- At 360, 390 and 430 CSS px, open a neutral shared comparison URL; change topic and both parties; find the measure summary, each qualification, both source locators, the missing-content explanation and the next action. Record task completion, errors, recovery and time for each path without retaining political answers.
- Repeat keyboard-only and physical iOS Safari/VoiceOver and Android Chrome/TalkBack journeys. Inspect focus/announcement after submit, invalid selection and source return; check visible focus, 44 px actionable targets, 200% text zoom/reflow and absence of clipped content. Keep native share and copy fallback separate from comparison readability.
- For the pending-content artifact, verify that no statement or agreement is implied. For a future reviewed artifact, check that a relationship is shown only with its distinct human approval and exact source trail. Have human Spanish-copy/editorial reviewers assess comprehension; passing CI is engineering evidence only.

## CI boundary at audit time

Open PR #135's rendered mobile and test/validation jobs passed, but its Docker serving-image job failed during the high/critical Trivy scan in run 40029804751. This is not a green PR or a claim that comparison CSS caused the scanner failure. Resolve or triage that gate on its owning branch; this audit does not alter the container or scanner configuration.

## Local verification of this documentation-only package

`node --test tests/share_behavior.cjs tests/quiz_behavior.cjs`: 21/21 pass. `git diff --check`: pass. Python artifact/browser tests were not run locally because this host has Python 3.11.2, not the repository-required Python 3.14, and no Chromium executable or `uv` is installed. These limits are not substituted with a review claim.
