# Tasks: E3.3 IONOS continuous deployment

Status: planning complete; implementation and live activation not started. These tasks extend E3.3 and do not complete the existing MVP tasks 4.4/4.6 or the E3.4 capacity gate.

## 1. Confirm host and release prerequisites

- [ ] 1.1 Record read-only Ubuntu VPS preflight for owner-supplied `195.20.230.75`: SSH port, version, architecture, disk, listeners, proxy, firewall and memory headroom; verify the inventory through a trusted operator connection and console recovery.
- [ ] 1.2 Record owner-confirmed finance-service retirement and backup/restore evidence for retained data; verify the selected loopback port is free before activation without deleting finance data.
- [ ] 1.3 Select the isolated fixed-egress runner or approved authenticated private connection path; verify SSH reachability from that path and denial from an unapproved source.
- [ ] 1.4 Verify repository-plan support for required production reviewers, main-only deployment and protected secrets; record the configured gate and demonstrate that missing approval blocks release.
- [ ] 1.5 Reconcile IONOS, 1-vCPU/1-GB and domain references in both roadmaps, ADR-0001, architecture/security/operations documentation and OpenSpec context; review consistency and retain original release targets until explicitly revised by owners.

## 2. Publish an immutable release candidate

- [ ] 2.1 Extend the existing CI dependency graph so trusted-main image publication requires validation, mobile accessibility, Docker parity and credential isolation; add workflow contract checks for failed jobs, wrong refs/repos, and fork events.
- [ ] 2.2 Build once for the inspected CPU architecture, run serving/release checks against that image, scan it, and push it to private GHCR using job-scoped package permissions; verify the tested, scanned and published artifact share one digest and retain scan/revision/build evidence.
- [ ] 2.3 Pin new actions by reviewed full SHA, set non-canceling deployment concurrency and least-privilege permissions, and document package access; verify PR jobs cannot publish images or access deployment secrets.
- [ ] 2.4 Configure the approved IDNA canonical domain in generation, metadata and proxy inputs; add checks covering HTTPS canonical URLs, sitemap, social previews and absence of the obsolete canonical domain.

## 3. Prepare restricted host operations

- [ ] 3.1 Implement the root-owned forced-command deployment wrapper with fixed Compose/state configuration, approved image-repository allowlist, digest validation and narrow sudo; test rejection of shell syntax, extra arguments, alternate repositories, environment overrides, and unauthorized commands.
- [ ] 3.2 Document and provision the restricted SSH account, VPS public key, GitHub `production` secret `VPS_SSH_KEY`, environment secrets `VPS_HOST=195.20.230.75`, `VPS_USER`, and `VPS_KNOWN_HOSTS`, with a new election-site key pair, independently verified known_hosts, and root-only private-registry authentication; verify key rotation, host-key mismatch rejection, and disabled forwarding/PTY without exposing credentials. Verify secrets are passed through environment variables, connection inputs are validated, and temporary key files are removed on success and failure.
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

Proposal, design, behavioral spec and task list were prepared from the existing workflow, Docker runtime, release controller and roadmap. Owner inputs specify Ubuntu, 1 vCPU, 1 GB RAM, Cloudflare, the new domain, and retirement of finance hosting. No server connection, credential creation, runtime change, live load test or deployment was performed.

Planning checks: `openspec validate ionos-continuous-deployment --strict` passed; `openspec status --change ionos-continuous-deployment` reports all four planning artifacts complete. CLI was run through the existing cached OpenSpec executable because it is not on PATH. Staged `git diff --check` passed. Runtime tests were not run for this documentation-only change; all implementation tasks remain unchecked.

## Workflow follow-up

- Archive only after implementation, independent review and applicable release evidence are complete. This plan does not authorize merge, publication or infrastructure destruction.
