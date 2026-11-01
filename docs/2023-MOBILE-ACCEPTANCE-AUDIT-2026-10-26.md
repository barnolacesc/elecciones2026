# E2.5: 2023 mobile acceptance evidence boundary (2026-10-26)

Status: technical audit for review, not a device, accessibility, editorial or
release approval. Baseline: `origin/main` at `8e2fab495d943ac4e7b448b029b659d3ebf04c96`.
Scope: the private, source-gated `es-gen-2023` comparator at 360, 390 and
430 CSS px. No source record, political answer, public artifact or routing
configuration was changed.

## Evidence observed on this baseline

- The generated pilot artifact test passes: every generated route retains the
  2023 election label, private/pending notice and matching canonical/social
  URL, and the artifact contains zero approved statements or relationships.
  This is an automated artifact observation, not source or rights review.
- `node --test tests/share_behavior.cjs` passes 13/13 simulated contracts for
  election isolation, neutral URL state, invalid-selection clearing, result
  focus, native-share/copy fallbacks and stale-link prevention. Simulated APIs
  do not establish iOS or Android share-sheet behavior.
- The opt-in 2023 Chromium suite did **not** run its four browser cases here.
  Python 3.14 initially lacked Playwright; after installation in a disposable
  `/tmp` virtual environment and installation of its Chromium binary, launch
  failed because the host lacks `libglib-2.0.so.0`. The one non-browser
  artifact test passed. The ordinary suite reports 5 tests, 4 browser skips.
- The latest `origin/main` CI run
  [40179863768](https://github.com/c2ventures/elecciones2026/actions/runs/40179863768)
  passed its test, rendered-mobile and Docker jobs, then failed the fork
  isolation job. The current open PR checks are not substitute evidence:
  [PR #160](https://github.com/c2ventures/elecciones2026/pull/160) fails before
  tests start; its check annotation says recent account payments failed or the
  spending limit needs increasing. No CI or review pass is inferred.

## Remaining E2.5 acceptance, to record against an exact artifact

Use assigned, fictional comparison choices; never retain a participant's
political preferences. Record artifact digest, date, device/OS/browser/reader,
task outcome, issue and retest reference for each row. A blank row is not a pass.

| Journey | Observable result | Evidence still required |
|---|---|---|
| Open a shared 2023 comparison URL at 360/390/430 px | Year and private scope are immediately clear; valid topic/pair restore; no horizontal clipping or zoom is needed | Real iOS Safari and Android Chrome touch observations; no participant run recorded |
| Change topic and pair, then submit | Both choices and result heading are announced in order; invalid identical pair is recoverable and stale content disappears | Keyboard plus VoiceOver/TalkBack observations on the exact artifact; PR #159 is separate and unmerged |
| Inspect each party position and source | Approved position, qualification, exact source/version and missing-state limit are understandable; both citations are reachable; source opens at the reviewed location | Blocked until reviewed content and rights exist; zero approved pilot claims on this baseline |
| Follow the empty-state next action | Coverage/method page opens, states the unresolved source and rights gates and offers a clear return path | Real-device task outcome and comprehension, not just DOM/link presence |
| Share, cancel, copy and reopen in a fresh session | Native and fallback paths use only allowlisted election/topic/party IDs; no answer, tracking token or stale selection survives | Physical share-sheet/clipboard tests on both platforms; current Node stubs are insufficient |
| Operate at enlarged text and with a reader | No clipped controls, hidden focus, lost status or ambiguous source link; process remains usable | Native zoom, screen-reader and manual accessibility review; no WCAG claim |

The full reviewed three-topic pilot and G5 quiz remain separate gates. Do not
mark OpenSpec task 3.5 complete from this audit, the earlier automated browser
checks or passing CI. Resolve the runner/billing blockers, then rerun the
rendered suite and retain device/participant evidence before acceptance.
