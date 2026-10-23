# E2.5 — private 2023 two-party selection recovery

Date: 2026-10-23. Baseline: `origin/main` at `fe5e05e`. Scope: the private,
provisional 2023 comparator only. No editorial record, source, review status,
quiz answer, public release or 2026 route is changed.

## Reproduced defect and change

The private comparator selects PP and ERC by default, renders immediately, and
writes `topic`, `partyA`, and `partyB` into its address. Before this change,
selecting the same candidature in both controls removed the comparison and
showed an error, but returned before updating the address. A copied or reloaded
address therefore restored the previous valid pair while the visible controls
showed an invalid one. The error was a live alert but was not programmatically
associated with either select.

Now the invalid state clears the comparison query and fragment, and marks both
selects invalid with `aria-describedby="pilot-error"`. Choosing distinct
candidatures again clears those attributes and restores a valid comparison URL.
The test uses the shipped `site/pilot-2023.js` with a synthetic, position-free
2023 fixture. It checks the valid → duplicate → corrected transitions without
asserting any political position or exporting political answers.

## Verification and remaining gate

- `node --check site/pilot-2023.js`: pass.
- `node --test tests/pilot_selection_behavior.cjs`: 1/1 pass.
- CI runs that focused test in the main validation job.
- A broad local `node --test tests/*.cjs` invocation is not a supported suite:
  four optional browser files require absent Playwright, and the comparison
  publish harness requires an output-path argument. Its applicable sharing,
  quiz-engine, simulator, load and new selector cases passed; this broad command
  does not establish a green project test run.
- No physical iOS/Android or screen-reader observation was made. At 360, 390,
  and 430 CSS px, the remaining E2.5 task is to observe duplicate selection,
  error announcement/association, recovery, and whether the result remains
  reachable without a dead CTA or horizontal scroll. Passing CI cannot close
  human usability or editorial review.

This is a private link-state and error-association repair, not a claim that the
2023 corpus, source rights, quiz, or preview release gates are complete.
