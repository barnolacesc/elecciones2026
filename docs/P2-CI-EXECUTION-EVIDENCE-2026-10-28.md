# E2.5 — CI execution evidence boundary

Date: 2026-10-28. Base: `origin/main` at `8e2fab495d943ac4e7b448b029b659d3ebf04c96`.
Scope: the mobile comparator and sharing acceptance evidence for the private 2023
pilot. This is an audit, not an implementation, editorial review, accessibility
sign-off, or release decision. No political content or visitor answer is included.

## Observed failure boundary

The latest inspected open PRs include mobile comparison work (#177), delivery
work (#176), and corpus documentation (#175 and #174). Their CI runs are all
`completed/failure`. For each run, both the validation job and the rendered
mobile/keyboard job report failure with an empty `runner_name` and **zero
recorded steps**. The Docker parity and fork-isolation jobs were skipped. These
API records do not show a failing test, a failed assertion, or a runner log.

| PR | Head | CI run | Validation / rendered-mobile observation |
|---|---|---|---|
| [#177](https://github.com/c2ventures/elecciones2026/pull/177) | `697e002fce9b` | [40707059217](https://github.com/c2ventures/elecciones2026/actions/runs/40707059217) | Both failed before any recorded step |
| [#176](https://github.com/c2ventures/elecciones2026/pull/176) | `8293f19b1a80` | [40697848854](https://github.com/c2ventures/elecciones2026/actions/runs/40697848854) | Both failed before any recorded step |
| [#175](https://github.com/c2ventures/elecciones2026/pull/175) | `4a1b6536d9b3` | [40680872587](https://github.com/c2ventures/elecciones2026/actions/runs/40680872587) | Both failed before any recorded step |
| [#174](https://github.com/c2ventures/elecciones2026/pull/174) | `896605612ca4` | [40673217601](https://github.com/c2ventures/elecciones2026/actions/runs/40673217601) | Both failed before any recorded step |

The common zero-step pattern is consistent with a CI execution or scheduling
failure, but the available job data does **not** establish its cause. It must
not be labelled a passed test, a code regression, or proof that the mobile
artifact was rendered. Do not bypass the required checks on that basis.

## Bounded local evidence

On a fresh worktree at this base, `node --test tests/share_behavior.cjs
tests/pilot_selection_behavior.cjs` passed 14/14 contracts. These cover URL
allowlisting, election isolation, comparison selection, invalid-state clearing,
share/copy fallback, and provisional pilot selection. This is simulated DOM
behavior, not generated-artifact, physical-phone, or screen-reader evidence.
The current runner has no Python 3.14 or Docker executable, so those lanes were
not reproduced locally. No real-device observations were performed.

## Required recovery evidence

1. Inspect GitHub Actions availability, repository/organization billing and
   runner settings, and the run pages for a platform diagnostic. Record the
   observed reason rather than inferring it from zero steps.
2. Rerun the unchanged PR heads only after execution is available. Require
   actual step output and conclusions for validation, rendered mobile/keyboard,
   Docker parity, and fork isolation. A rerun of a later commit does not prove
   an earlier head.
3. For E2.5, retain generated private 2023 artifact observations at 360, 390,
   and 430 CSS px for shared-link entry, topic/party change, source inspection,
   empty state, share fallback, focus, touch targets, and overflow. The existing
   automated browser job is necessary but does not replace physical iOS/Android,
   screen-reader, and task-success review.
4. Keep OpenSpec task 3.5 and the P2 exit gate open until those human and
   artifact observations exist. Passing CI cannot approve editorial records,
   source rights, public routing, or release.

The audit uses the GitHub REST pull, workflow-run, and job records for the exact
heads above, plus the repository's `AGENTS.md`, product roadmap, and
`mvp-programme-comparison` task/spec files. It changes no runtime behavior or
source register.
