# Private preview candidate — 2026-10-12

Roadmap package: **E3.3**. Issue: [#71](https://github.com/c2ventures/elecciones2026/issues/71).

Status: the merged main candidate uses the wrong election for the intended
2023 preview. The corrected CI configuration is prepared in this branch. Successful main CI,
exact owner approval, manual dispatch and hosted verification are pending. This record does not authorize delivery.

## Build selection and content boundary

Inspected merged revision: `0a710c85b2328cb5eadfc635785effec19dd545c`.
Existing main CI: [38236234261](https://github.com/c2ventures/elecciones2026/actions/runs/38236234261).
It includes redesign PR #66, review withdrawal PR #79, validated browser data
PR #84, budget snapshot checks PR #83 and IONOS documentation PR #82.

At the inspected merged revision, the trusted-main Docker build uses the Dockerfile defaults: `es-gen-2026` and
`QUIZ_MODE=unavailable`. A local build of that revision contains **seven synthetic
statements and three synthetic relationships**. It is a private fixture preview.
It is not a claim-free 2023 pilot and does not establish real editorial approval.

A separate local `es-gen-2023` build contains **zero statements and zero
relationships**, with Spanish private-pilot and pending-review labels. The CI workflow at the inspected merged revision does not select this build
for its published candidate. The intended target is the empty 2023 pilot. Inspect a matching CI-built candidate
before owner approval; do not relabel or rebuild the existing image on the VPS.

Both local builds use the merged Swiss theme with the monochrome default. The
last recorded successful hosted delivery used an older revision, so the redesign
is merged but has no newer hosted delivery evidence.

## Last verified hosted artifact

[Delivery 38182379207](https://github.com/c2ventures/elecciones2026/actions/runs/38182379207)
used CI run `38154601720`, attempt `2`, revision
`08da126fb50ae0fc1c3e783829a9edb55e2172da`.

- Image: `ghcr.io/c2ventures/elecciones2026@sha256:3e1a312b46d94d3b56ec11135241651c3ae30e88c4c3e77dac7efb4d642f2905`.
- Home SHA-256: `f4d6642a24ae9c1c5cb9afc994004ddf5dbe58ced40e7cfd865af07524e9d010`.
- That revision predates redesign PR #66 (`c344e30433b1d9d2ca77320e340e3a1f35f4a667`)
  and withdrawal PR #79. It is historical delivery evidence, not the current main
  artifact or confirmation of the current served content.

See [the setup record](SERVER-MIGRATION.md#current-setup-and-verification).
Do not restore an earlier image merely because its health check passes. Inspect
its political content and approval evidence first.

## Owner dispatch and hosted verification

After successful candidate inspection, obtain owner approval that identifies the
exact digest, revision, CI run/attempt, content boundary and authenticated preview
target. Store its reference in the dispatch; do not use this unsigned preparation
record as owner approval.

Use **Actions → Deliver approved staging candidate → Run workflow → main**.
Enter the corrected successful 2023 CI run ID, the retained owner approval
reference in `approval_record`, and `approve=true` only after approval. Do not
select run `38236234261` for the intended 2023 preview. The command below is a
prepared equivalent. Replace both references first; it was not executed.

```sh
gh workflow run deliver.yml --repo c2ventures/elecciones2026 --ref main \
  -f ci_run_id=APPROVED_2023_CI_RUN_ID \
  -f approval_record=OWNER_APPROVAL_REFERENCE \
  -f approve=true
```

Only release owner `barnolacesc` can dispatch/rerun delivery. Keep the target
`https://preview.xn--eleccionesespaa2026-83b.es/`; retain Basic authentication,
no-store, cache bypass, noindex and Disable RUM. Apex/www activation requires
separate public-release approval.

Retain the delivery run URL and result, exact revision/digest, verified home hash
and approved content selection. Confirm:

- Unauthenticated home returns 401 before and after activation.
- Authenticated home returns 200, matches the inspected candidate hash, and has
  required security and no-store headers. Do not log credentials or response text.
- The intended election label, source-review gaps, Swiss monochrome theme,
  comparison selections and unavailable quiz agree with the approved candidate.
- No withdrawn 2023 statement, relationship or fabricated review mark appears
  through HTML, browser selection, source links or share URLs.

The delivery workflow checks home authentication, exact home bytes and required
headers. Theme/election/route behavior and withdrawal coverage need separate
operator observations; a home hash alone does not establish these results.
If external verification fails after origin activation, inspect the delivery state
before recovery. Do not restore unsupported political content.

## Remaining evidence

No owner approval, workflow dispatch, SSH connection, server change, deployment,
public publication or live recovery check occurred during this preparation.
G0/G2/G4, real source rights and editorial reviews, monitoring/alerts, full origin
probes, retained-data restoration and actual-host capacity remain open.

## Local inspection evidence

At revision `0a710c85b2328cb5eadfc635785effec19dd545c`, both local builds used
`--build-date 2026-10-10`, approved ASCII canonical base and unavailable quiz.
They generated deterministic content locally; this is not an inspected Docker
image or registry digest.

| Election | Statements | Relationships | Home SHA-256 |
|---|---:|---:|---|
| `es-gen-2026` | 7 synthetic | 3 synthetic | `6ba3239ef2b51b619e2fc46b6afdd6b917df9fa392e25241c4130dae13ca844f` |
| `es-gen-2023` | 0 | 0 | `2615469859601fa902710fa849c0f194729a1b1e51282982f74ebb976de9591b` |

The 2023 browser payload and HTML share the validated publish set. All source
rights and human review gaps remain open. Synthetic data tests cannot supply
those approvals. The pending pilot remains behind private authentication.

Before dispatch, inspect the corrected CI artifact's `release.json` and `scan.json`:
confirm successful canonical main push, run attempt, revision, AMD64, exact digest,
image config ID, home hash, private classification, explicit `es-gen-2023`,
unavailable quiz and approved canonical base. Inspect the tested image contents
and retain scan/hash evidence without copying images or source text into Git.
Require the exact image's HIGH/CRITICAL vulnerability scan to pass.

## Corrected configuration in this branch

The serving-image CI build now sets `ELECTION_ID=es-gen-2023` and
`QUIZ_MODE=unavailable` explicitly. Reusable Dockerfile defaults stay unchanged.
The candidate record includes both values. Delivery validation requires that
election, unavailable quiz, the exact approved canonical base and the existing
private classification, digest, platform, revision and run/attempt binding.

Legacy records without these fields, including the earlier 2026 fixture record,
are rejected intentionally. Prepare a new matching candidate instead of editing
old provenance or bypassing validation. A failed validation stops before SSH.
The exact approved registry digest, release record, image scan and successful
main CI run remain pending until this change is merged and trusted-main CI passes.

Verification: the full Python suite passes with 431 tests, five skips and 223
subtests. Critical Ruff checks pass. Actionlint reports one existing ShellCheck
SC2034 warning for an unused `attempt` variable in the mobile retry step; no new
workflow syntax errors are reported. Local Markdown links resolve and the prepared
dispatch example passes `bash -n` without execution.

A local AMD64 Docker build with the corrected arguments passes and generates
zero statements/relationships. Its home hash is
`2615469859601fa902710fa849c0f194729a1b1e51282982f74ebb976de9591b`, matching
the local Python 2023 build. Image inspection confirms UID 101, the 2023 election
label, Swiss theme and monochrome default. This local image was neither scanned
for a release decision nor published; its local manifest is not an approved
registry digest. No existing preview container was changed.
