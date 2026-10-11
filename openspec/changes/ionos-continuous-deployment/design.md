# Design

## Context

See [proposal.md](proposal.md) for motivation and package E3.3 scope. Existing CI validates content, browser behavior, deterministic builds, Docker parity, and local release/load rehearsals. Its production job only prints gate messages and does not depend on the mobile-accessibility job. `ops/release.py` already switches digest-pinned images, checks health, serializes operations, and restores the prior image on failure. `ops/compose.yaml` binds to loopback and limits the serving container to 256 MB.

Owner-confirmed target: Ubuntu IONOS VPS, 1 vCPU, 1 GB RAM, finance service to be retired, Cloudflare routing, domain `eleccionesespaña2026.es`. ASCII DNS form: `xn--eleccionesespaa2026-83b.es`. Ubuntu version, CPU architecture, disk capacity, current proxy, and actual DNS configuration still need a read-only preflight. The repo assumes Hetzner, a 2-vCPU/8-GB benchmark, and `elecciones2026.es`; the Docker build uses Python 3.12 despite the Python 3.14 roadmap. Record the runtime mismatch without combining a Python migration into this package.

## Goals / Non-Goals

**Goals:** turn passing CI into an explicitly approved, recoverable deployment; build away from the small host; provide a precise owner setup checklist.

**Non-Goals:** automatic editorial approval, zero-downtime guarantees, a permanent CI runner on the VPS, automatic removal of finance data, or a capacity promise from existing rehearsals.

## Decisions

### 1. Extend the existing trusted workflow

Keep PR jobs read-only. Add trusted-main image publication and production deployment jobs to the existing workflow so their dependencies include validation, mobile accessibility, Docker parity, and isolation checks. Never use `pull_request_target` or execute untrusted artifacts with release credentials. Prefer explicit dependencies to a second workflow that can race or deploy the wrong revision.

Build once for the inspected host architecture, test that exact image, scan it with an approved policy, and publish it to private GHCR. Deploy its registry digest; commit tags are labels only. Do not rebuild after tests. Pin new actions by reviewed full commit SHA. Publishing uses job-scoped `packages: write` and the ephemeral `GITHUB_TOKEN`; deployment uses `contents: read` only. Retain revision, digest, scan, build inputs, and approval references in release evidence. The existing pipeline's audit and rehearsal success are not production content approval.

Use protected `production` environment secrets, required human reviewers, main-only deployment rules, and prevention of self-approval where supported. Verify these protections are available for this repository's visibility and GitHub plan before implementation activation. If unavailable, keep deployment disabled until an equivalent enforceable gate is agreed. Use workflow concurrency with no cancellation of active production switches, plus the existing host lock. Normal main pushes can produce candidates; they must wait for approval to activate.

### 2. Ship images, not a repository checkout

The VPS pulls the approved image; it does not clone or build the repository. Install reviewed release tooling once under root-owned `/opt/elecciones2026/`. Subsequent tooling updates are separate reviewed operator actions. This avoids a GitHub repository deploy key and avoids allowing CI to upload arbitrary code that sudo would run.

Keep GHCR private while it contains rehearsal material. Give the host a separately stored, expiring classic PAT with `read:packages` and access to this package only, under an approved account and SSO authorization if required. Do not reuse CI's short-lived token as a persistent host credential. Use `docker login --password-stdin` during owner provisioning; keep the Docker credential file root-only or use a credential helper. Public images would avoid a pull token but could disclose private pilot content, so they are excluded at this stage.

### 3. Restrict SSH to the deployment operation

Create a dedicated `elecciones-deploy` identity and key pair. The public key goes in the VPS account's `authorized_keys`; the private key goes in the protected GitHub environment. This key authenticates to IONOS, while a GitHub repository deploy key authenticates to GitHub. They serve different endpoints.

Use a forced command with no PTY, agent forwarding, port forwarding, or arbitrary shell execution. A root-owned wrapper accepts only an allowlisted GHCR repository plus a full sha256 digest, or a protected rollback action. Reject malformed input, extra arguments, and shell syntax; never evaluate `SSH_ORIGINAL_COMMAND`. The SSH user cannot edit the controller, Compose file, wrapper, state, or registry credentials. Grant narrowly defined sudo access to that wrapper only; do not add the user to the Docker group, whose access is effectively root. Restrict environment inheritance, including Compose port/project settings. Root-owned configuration fixes the site paths and selected port.

Store a `known_hosts` entry verified through the IONOS console or an existing trusted operator connection. `ssh-keyscan` output from the same unverified network path is not sufficient trust. Use strict host-key checking and disable secret shell tracing.

Runner connectivity is an activation prerequisite: use an isolated runner with fixed egress that the firewall can allowlist for SSH. Do not install it on the production VPS. Standard GitHub-hosted runners have changing addresses; do not solve that by opening SSH globally. If fixed egress is unavailable, owner review must select an authenticated private network path before enabling delivery. Preserve console recovery and operator SSH access.

### 4. Prepare the dedicated small host conservatively

Inspect listeners, service units, Docker projects, firewall rules, and the current reverse proxy. The owner retires the finance service after verifying backups and recovery; this PR does not authorize deleting its data. Reuse an existing compatible proxy, or install host nginx only if preflight confirms no conflicting listener. Do not blindly apply `ops/origin.conf`: its default-server blocks and instructions to remove host sites assume a fresh host.

Keep the static origin on an available loopback port, separate from public TLS. Retain the current non-root/read-only/capability-dropped container and 256-MB limit initially, then measure actual peak usage alongside Ubuntu, Docker, proxy, monitoring, and image pulls. No PDF extraction, build, or load generator runs on the VPS. Require sufficient disk for current, candidate, and retained prior images. Do not globally prune Docker artifacts during transition.

Keep Cloudflare DNS/proxy and Full (strict) TLS, with reviewed IPv4/IPv6 origin restrictions and Authenticated Origin Pulls where configured. Apply those restrictions to the site's actual interfaces/ports after checking recovery access. Verify the domain's IDNA form in DNS, certificates, server names, build configuration, canonical URLs, sitemap, and social previews. Mutable assets must revalidate as documented in the existing proxy. Private staging requires real authentication and no-store; robots exclusions alone do not make it private.

### 5. Verify origin and edge separately

Invoke the existing controller only through the restricted wrapper. Origin health failure restores the previous image; a first-release failure removes the candidate. After origin success, check approved external HTTPS home/topic/method routes, security/cache headers, and release identity. Purge mutable Cloudflare URLs after release and rollback with a zone-scoped purge token. A failed purge or external probe fails the deployment and requires protected operator recovery; do not automatically restore known incorrect editorial content.

Retain prior images and a restricted release-state backup; test registry-unavailable rollback, first-release failure, and a fresh-host restore. Measure end-to-end recovery including edge/cache checks against the existing <5-minute target. Install an independent external probe and approved alert route; avoid visitor URL/IP logging. The existing local load report and the CI burst saturation do not establish capacity on this 1-GB host. Repeat approved scenarios using off-host generators; revise capacity or approved targets based on measured results.

## Owner setup checklist

| Item | Needed value or access | Where it belongs |
|---|---|---|
| VPS details | Host/IP, SSH port, Ubuntu version, architecture, disk space, console access | Restricted operations inventory; non-secret workflow variables for host/port |
| Host preflight | Current proxy/listeners, firewall, retirement confirmation, verified finance backup | Owner-reviewed operations record |
| Domain | `eleccionesespaña2026.es` / `xn--eleccionesespaa2026-83b.es`, zone and DNS control | Build/proxy configuration; approved Cloudflare zone |
| Deploy identity | Dedicated username and public key | VPS restricted SSH account |
| `IONOS_SSH_PRIVATE_KEY` | Dedicated deployment private key | Protected GitHub environment secret only |
| `IONOS_SSH_KNOWN_HOSTS` | Independently verified host-key entry, including nonstandard port if used | Protected environment configuration |
| `IONOS_HOST`, `IONOS_SSH_PORT`, `IONOS_SSH_USER` | Verified connection values | Protected environment variables |
| Runner path | Isolated runner and fixed SSH egress allowlist, or approved authenticated private path | CI/network owner configuration |
| Registry publishing | Actions package permissions | Workflow-scoped `GITHUB_TOKEN`; no extra publishing PAT |
| Registry pull | Account and expiring `read:packages` credential for private GHCR image | Root-only VPS registry credentials, not repository or chat |
| Cloudflare | Zone ID; token with only needed cache-purge rights for this zone | Environment variable and protected secret (`CLOUDFLARE_ZONE_ID`, `CLOUDFLARE_PURGE_TOKEN`) |
| Repository administration | Authority to configure environment reviewers, branch checks, secrets, and package access | GitHub owner/admin setup |
| Release approval | G0/G2/G3/G4 evidence, reviewed public corpus, accessibility/security/load evidence | Restricted release record and production approval |

No private keys, passwords, tokens, finance backups, or visitor data belong in a commit or chat. No IONOS API token is needed for SSH-based image delivery; one would require a separate infrastructure automation decision.

## Risks / Trade-offs

- [1 GB is below the planned benchmark] → keep builds and load generation off-host; measure headroom, image pulls, OOM behavior, and actual Cloudflare delivery before release.
- [Finance retirement loses state] → owner-verified backups and recovery before stopping services; defer deletion to the owner.
- [Root release controller can be abused] → root-owned tooling, fixed configuration, restricted forced command, allowlisted image repository, and narrow sudo.
- [Successful build publishes private or unreviewed content] → private registry/authenticated staging and explicit artifact-linked editorial approval.
- [A container switch briefly interrupts service] → monitor the interruption and retain rollback; do not claim zero downtime.
- [Provider/domain documents disagree] → reconcile roadmaps, ADR, config context, operations and generated metadata before activation.

## Migration Plan

1. Review this E3.3 plan and supply connection/proxy/runner details. Complete the read-only preflight and verify finance recovery.
2. Reconcile hosting/domain documents and implement trusted delivery, restricted host tooling, and meaningful failure tests.
3. Provision private staging and rehearse approved artifact delivery, bad-key rejection, unhealthy-image recovery, and cache verification.
4. Retire the finance service through the owner gate. Confirm host headroom, certificates, DNS, alerts, and off-host load evidence.
5. After content and launch approval, activate the public route and protected delivery. Keep prior approved digest, state backup, and a console recovery path.

## Open Questions

- What are the VPS address, SSH port, Ubuntu version, architecture, disk capacity, and current proxy/listeners? These determine provisioning values, not the release contract.
- Which isolated runner provides the approved connection path, and who administers the repository and Cloudflare zone? Delivery stays disabled until these prerequisites are satisfied.
- Which notification route and external probe should receive release/availability failures?

## References

- [GitHub: Publishing Docker images](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- [GitHub: Container registry authentication and permissions](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub: Deploy keys authenticate access to a repository](https://docs.github.com/en/enterprise-cloud%40latest/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
- [GitHub: Deployment environments and required reviewers](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)
