# 2023 corpus integration: CI evidence boundary — 2026-11-11

Roadmap package: **P0.2 integration evidence** (`2023-corpus-completion`,
proposal-only). This is a current-main audit, not a source or editorial decision,
an implementation task, or a release approval. It complements the source-PR
queue in [PR #224](https://github.com/c2ventures/elecciones2026/pull/224);
it does not re-rank or merge that queue.

## Reconciled baseline

- `origin/main` is `488b6f5` (roadmap draft 0.3). Its
  `content/sources/register.json` contains four `es-gen-2023` pilot rows: ERC,
  PNV, PP and Sumar. All four are `published-unverified`, have
  `rights_review.status: not_reviewed`, and have no publication date. These
  rows are not the approved candidature or document denominator. The ten-name
  product target in `ROADMAP.md` is a target, not a verified coverage count.
- PR [#101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  draft, conflicting with `main`, and has no recorded GitHub review decision.
  Its green October 12 checks ran on its old head, not on an integrated tree.
  The [current-main integration audit in PR #207](https://github.com/c2ventures/elecciones2026/pull/207)
  and [supersession audit in PR #219](https://github.com/c2ventures/elecciones2026/pull/219)
  own the conflict disposition. This note does not propose a second rewrite of
  the six PP/ERC records.
- The latest [main CI run](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
  for `488b6f5` failed. A passing check on an old PR head cannot be substituted
  for a green current-main or post-integration run.

## Distinct technical failures and existing owners

The main run reports two failed validation tests and nine Docker-parity setup
errors. Its rendered-mobile job also failed. These are technical blockers; none
supplies a human review of a programme, source use or comparison.

| Observed main failure | Existing non-overlapping repair | Verification still needed |
|---|---|---|
| `test_provisional_notice_and_source_links`: the source index has zero visible new-tab notices where the test requires four. | [PR #204](https://github.com/c2ventures/elecciones2026/pull/204) adds notices to the four registered-document links. | Re-run the source-index test and full CI on the eventual combined tree. |
| `test_real_workflow_authorization_rejects_missing_approval_and_wrong_actor`: the dated private-pilot delegation has expired. | [PR #214](https://github.com/c2ventures/elecciones2026/pull/214) changes the test to retain expiry rejection; it does not renew authorization. | Re-run the delivery test on the combined tree; do not make expired access valid just for CI. |
| Nine `TestLiveDockerContainerParity` cases error because the serving container does not become HTTP-ready. | [PR #225](https://github.com/c2ventures/elecciones2026/pull/225) diagnoses the unquoted Nginx regex and reports all nine parity cases passing on its head. | Re-run image readiness and full CI after integration; its full check is still red from other tests. |

The [November 10 PR #227](https://github.com/c2ventures/elecciones2026/pull/227)
[run](https://github.com/c2ventures/elecciones2026/actions/runs/42809034456)
still has a separate mock-quiz browser failure. That run is not a proof of
current-main status and this P0/P1 audit does not change the quiz. PR #227 also
changes pilot missing-position wording, not the three failures above.

## Reviewable integration gate

1. Resolve PR #101 against the current P0/P1 method and source-use decisions;
   use the existing #207/#219 disposition evidence. Do not merge duplicate
   branches or infer rights from the six reported content reviews.
2. Review each repair in its existing PR. On the resulting candidate tree,
   run the full validation, rendered-mobile and serving-image jobs. Record the
   exact SHA and any remaining failures; isolated passing cases are narrower
   evidence than a passing full run.
3. Reconcile the owner-approved 2023 inclusion rule, document scope, rights
   decisions and exact-source reviews independently of CI. No `not stated`
   conclusion or public comparison follows from four pilot links or green
   tests alone.

No PDFs, source text, political positions, rights decisions, approvals,
deployment configuration or public routing were changed by this audit.
