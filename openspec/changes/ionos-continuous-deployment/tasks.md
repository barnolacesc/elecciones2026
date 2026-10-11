# Tasks: E3.3 IONOS continuous deployment

Status: planning complete; restricted-access implementation in progress; live activation not started. These tasks extend E3.3 and do not complete the existing MVP tasks 4.4/4.6 or the E3.4 capacity gate.

## 1. Confirm host and release prerequisites

- [ ] 1.1 Record read-only Ubuntu VPS preflight for owner-supplied `195.20.230.75`: SSH port, version, architecture, disk, listeners, proxy, firewall and memory headroom; verify the inventory through a trusted operator connection and console recovery.
- [ ] 1.2 Record owner-confirmed finance-service retirement and backup/restore evidence for retained data; verify the selected loopback port is free before activation without deleting finance data.
- [ ] 1.3 Record the owner-selected GitHub-hosted runner and public key-only SSH path with connection rate limiting; verify hosted-runner reachability, denial of unauthorized keys and passwords, and preserved deployer restrictions.
- [ ] 1.4 Record unavailable required reviewers on the private repository plan, the owner-selected manual dispatch gate, main-only environment rules and protected secrets; demonstrate that missing operator approval blocks release.
- [ ] 1.5 Reconcile IONOS, 1-vCPU/1-GB and domain references in both roadmaps, ADR-0001, architecture/security/operations documentation and OpenSpec context; review consistency and retain original release targets until explicitly revised by owners.

## 2. Publish an immutable release candidate

- [ ] 2.1 Extend the existing CI dependency graph so trusted-main image publication requires validation, mobile accessibility, Docker parity and credential isolation; add workflow contract checks for failed jobs, wrong refs/repos, and fork events.
- [ ] 2.2 Build once for the inspected CPU architecture, run serving/release checks against that image, scan it, and push it to private GHCR using job-scoped package permissions; verify the tested, scanned and published artifact share one digest and retain scan/revision/build evidence.
- [ ] 2.3 Pin new actions by reviewed full SHA, set non-canceling deployment concurrency and least-privilege permissions, and document package access; verify PR jobs cannot publish images or access deployment secrets.
- [x] 2.4 Configure the approved IDNA canonical domain in generation, metadata and proxy inputs; add checks covering HTTPS canonical URLs, sitemap, social previews and absence of the obsolete canonical domain.

## 3. Prepare restricted host operations

- [x] 3.1 Implement the root-owned forced-command deployment wrapper with fixed Compose/state configuration, approved image-repository allowlist, digest validation and narrow sudo; test rejection of shell syntax, extra arguments, alternate repositories, environment overrides, and unauthorized commands.
- [ ] 3.2 Document and provision the restricted SSH account, VPS public key, GitHub `production` secret `VPS_SSH_KEY`, environment secrets `VPS_HOST=195.20.230.75`, `VPS_USER`, and `VPS_KNOWN_HOSTS`, with the owner-approved existing deployment key and a documented rotation path, independently verified known_hosts, and root-only private-registry authentication; verify key rotation, host-key mismatch rejection, and disabled forwarding/PTY without exposing credentials. Verify secrets are passed through environment variables, connection inputs are validated, and temporary key files are removed on success and failure.
- [ ] 3.3 Adapt the existing loopback Compose/proxy setup to preflight results, preserving non-root/read-only execution and bounded resources; verify Compose configuration, TLS/proxy syntax, container health, free ports and lack of public container listeners.
- [ ] 3.4 Document owner-controlled finance retirement, Cloudflare TLS/origin restrictions, cache handling and authenticated private staging; verify private pilot content is unavailable on the public domain and requires authentication in staging.

## 4. Deliver and recover

- [ ] 4.1 Replace the placeholder production gate with protected delivery of the reviewed candidate digest through strict SSH and the restricted wrapper; test no mutation for missing credentials, wrong host key, failed checks or absent approval.
- [ ] 4.2 Add artifact-linked publication checks and approval evidence for content classification, source rights, exact citations and human editorial review; verify private fixtures, missing citations and conflicting source versions cannot activate the public route.
- [ ] 4.3 Add external HTTPS/content/header verification and scoped Cloudflare cache purge after origin activation; test failed external probes and purge failures report failed deployment and document protected operator recovery.
- [ ] 4.4 Expose protected rollback using the retained approved digest and existing controller; rehearse successful A-to-B-to-A, unhealthy B, failed first release, registry-unavailable recovery, release lock contention, and factual-correction restrictions.
- [ ] 4.5 Document and test independent external monitoring, approved alerts and fresh-host restoration from retained image/state/configuration; record alert receipt and recovery evidence without visitor request logs.

## 5. Complete live release evidence

- [ ] 5.1 Run editorial/security/accessibility review and inspect HTTPS domain, DNS/proxy, cache, origin restrictions and staging access; retain human signoffs and external observations before public activation.
- [ ] 5.2 Coordinate the existing E3.4 off-host steady/cold-cache/burst scenarios against the actual 1-vCPU/1-GB target; record resource headroom, p95/errors/cache/bandwidth/cost and block launch if approved targets fail.
- [ ] 5.3 Rehearse origin plus edge rollback and fresh-host restore, confirm recovery meets the approved target, and record the public G4 decision; leave MVP tasks 4.4/4.6 and load task 4.7 open until their own evidence is complete.

## Planning verification

The finance deployment and test workflows at main revision `5c705d7f2be8cce74bc5b2434c078341d1b690c2` were reviewed read-only; secret values and live host settings were not inspected. The design records retained conventions and concrete security improvements.

Proposal, design, behavioral spec and task list were prepared from the existing workflow, Docker runtime, release controller and roadmap. Owner inputs specify Ubuntu, 1 vCPU, 1 GB RAM, Cloudflare, the new domain, and retirement of finance hosting. The agent has not connected to the VPS, created deployment credentials, run live load tests or deployed the site. Owner-provided terminal output confirms finance shutdown, VPS reboot and Docker-group removal; backup and firewall evidence remain pending.

Original planning-only checks: `openspec validate ionos-continuous-deployment --strict` passed; `openspec status --change ionos-continuous-deployment` reports all four planning artifacts complete. CLI was run through the existing cached OpenSpec executable because it is not on PATH. Staged `git diff --check` passed. No runtime tests were run during the original documentation-only planning phase. See the implementation evidence below for subsequent checks and task completion.

## Workflow follow-up

- Archive only after implementation, independent review and applicable release evidence are complete. This plan does not authorize merge, publication or infrastructure destruction.

## Restricted-access implementation evidence

Task 3.1 complete: root-owned request validator and isolated launchers, fixed Compose/state paths, GHCR repository/digest allowlist, narrow NOSETENV sudo policy, and account-wide SSH restriction with root-managed authorized keys. Eight boundary tests cover invalid requests, inherited settings, ownership/write permissions, symlinks, state references, and shell argument preservation. Existing seven release/recovery tests pass. Full Python unittest suite: 312 tests pass, 2 skips. Focused Ruff E9/F63/F7/F82 checks, compile validation, shell syntax, strict OpenSpec validation and diff whitespace checks pass.

Disposable Ubuntu 22.04 AMD64 rehearsal passes using real OpenSSH and sudo: restricted SSH check succeeds; arbitrary requests, other image repositories, edits to installation/state/key files and an old home authorized key are rejected. CI now repeats that off-host rehearsal on a digest-pinned Ubuntu test image. This does not test live Docker activation, VPS provisioning, production firewall or GitHub release approval. Task 3.2 remains unchecked until the owner installs the new public key/policy, provisions secrets and registry pull access, and verifies live access. The initial environment lacked protection rules. A later read-only API check confirmed the owner-configured main-only branch policy; required reviewers remain unavailable and application activation remains manual.

## Delivery preparation evidence — 2026-10-11

Owner confirmed the domain was bought at DonDominio; Cloudflare delegation is
pending. Registry helper, trusted-main private image publication, manual staging
delivery and both staging/public nginx templates are prepared. The owner selected
manual dispatch because required reviewers are unavailable on the repository plan.
The existing deploy key was retained by explicit owner decision. Live restricted
SSH check passed and arbitrary `id` was denied; no application was activated.
Main-only production environment branch policy was verified through GitHub API.

Local validation: 321 unittest tests passed (2 skips), focused Ruff and actionlint
passed; AMD64 Docker build passed; both domain TLS proxy templates passed nginx -t with disposable test certificates. Trivy 0.75.0 scan of the saved serving image
found no HIGH/CRITICAL vulnerabilities. Docker Desktop direct scan failed on a
missing snapshot; scanning the saved exact image succeeded. DNS, certificates,
registry login, approved runner/firewall path, live delivery and public gates
remain unverified. Tasks stay open where their full live evidence is absent.

## Hosted-runner network decision and owner evidence — 2026-10-11

The owner rejected self-hosted Actions and chose public SSH with keys only and
rate limiting. Both delivery jobs now use ubuntu-latest directly; the runner-label
variable and its authorization prerequisite are removed. Owner terminal output
confirms effective publickey-only SSH, password/interactive disabled, root key-only,
MaxAuthTries 3 and MaxStartups 10:30:30; SSH reload and a new operator login passed.
UFW is active with public SSH LIMIT for IPv4/IPv6, an operator IP-specific ALLOW,
Cloudflare-only HTTPS and the obsolete port 5001 rule removed. Nginx listens on 443
with no port 80. External preview rejects unauthenticated access (401, no-store,
noindex); authenticated access yields 502 because no application is running yet.
Hosted-runner access, a private-image pull and end-to-end activation remain open.

Local follow-up validation: nine delivery boundary tests, actionlint, focused Ruff,
strict OpenSpec validation and diff whitespace checks passed. No live deployment
or hosted-runner connectivity test was performed during this change.

The owner confirmed effective deployer publickey-only authentication, forced
command, disabled forwarding/TTY/user RC after the global SSH change. Application
activation remains pending. CI now explicitly includes ready_for_review so the
owner can trigger review checks on the draft head without granting deploy access.

## Repeatable setup documentation — 2026-10-11

E3.3: ops/SERVER-MIGRATION.md consolidates owner-confirmed VPS, retired-service,
restricted SSH/sudo, UFW, DNS, Origin CA/AOP, authenticated nginx, registry and
GitHub configuration. It records secret locations without secret values and gives
replacement-host preparation, Hetzner firewall, identity verification, DNS cutover,
recovery and retirement steps. Existing operations guides link to this record and
distinguish initial inventory from later owner checks. Application activation,
hosted-runner connectivity, monitoring and fresh-host restoration remain unverified;
task 4.5 stays open until its live rehearsal and alert evidence exist.

Documentation validation: local file links resolve; 28 shell examples pass bash -n
without execution; strict OpenSpec validation and git diff --check pass. No server
configuration or DNS was changed by this documentation update.

## Main-branch conflict resolution — 2026-10-11

E3.3: integrated main revision 4306ac9. The Dockerfile conflict retains main's
election selector and 2026-10-10 build date together with the approved canonical
base. Other main changes merged without manual edits. Validation: 324 unittest
tests ran successfully (2 skips), 12 Node tests passed, AMD64 Docker build and
generator determinism passed; actionlint, focused Ruff, strict OpenSpec validation
and staged whitespace checks passed. Hosted CI must run on the updated PR head.
No application activation or merge into main was performed.

## Rendered CI follow-up — 2026-10-11

E3.3 integration: hosted run 38153746784 passed validation, Docker parity/scan
and credential isolation, but the mobile job failed the 360px stacked-card check.
Separate Playwright rectangle reads can observe different scroll positions while
the page smooth-scrolls. The check now collects both rectangles in one browser
task and records them as failure details; positive dimensions and stacking remain
required. A controlled Chromium regression reproduced the false failure between
separate reads and confirmed atomic reads accept stacked cards while rejecting
side-by-side cards. The complete rendered mobile audit passed 60/60 locally;
focused Ruff and diff whitespace checks passed. Hosted confirmation remains pending
on the next PR head. No product layout or deployment policy changed.

## First live delivery preflight — 2026-10-11

E3.3: owner confirmed the exact private candidate pulls on the VPS and the local
deployer check passes. Owner authorized DEPLOYMENT_READY=true and manual staging
dispatch for CI run 38154601720, attempt 2. Delivery run 38164607568 accepted the
approval and candidate download, then failed without any SSH output. The external
Python preflight was reproduced locally: default Python user agent received 403,
while curl and the explicit elecciones2026-deployment/1 client received the expected
401. The edge probe now identifies its client explicitly; authentication, redirect,
content/header checks and fail-closed behavior remain required. The live SSH path
and application activation remain unverified until a successful retry.

Follow-up verification: all 10 delivery boundary tests, focused Ruff, strict
OpenSpec validation and diff whitespace checks pass. The updated live
unauthenticated edge probe returns the required 401 without any SSH or mutation.

## Repeated staging delivery — 2026-10-11

E3.3: delivery run 38166342922 passed SSH and activated a healthy origin, but its
external verification failed. Owner probes then confirmed authenticated HTTP 200,
required security/no-store headers and the exact candidate home hash. After the
owner updated STAGING_BASIC_AUTH, retry 38167428810 passed SSH but the controller
rejected the already-current image before testing the updated credential. Same-image
deployment retries now check container and loopback health without registry access
or release-state changes, preserving the previous rollback image; failed health
and redundant rollback still fail. Root-owned host tooling requires an operator
update after review. Hosted credential verification remains pending.

Local verification: 10 origin controller tests and 10 delivery boundary tests pass,
including healthy/unhealthy repeated-image requests, retained-state preservation
and redundant rollback rejection. Focused Ruff, strict OpenSpec validation and
whitespace checks pass. The Docker rehearsal now repeats image A after rollback
and verifies its content and unchanged state; hosted execution remains pending.
