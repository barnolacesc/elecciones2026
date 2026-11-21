# Design

## Context

See [proposal.md](proposal.md) for motivation and package E3.3 scope. Existing CI validates content, browser behavior, deterministic builds, Docker parity, and local release/load rehearsals. Its production job only prints gate messages and does not depend on the mobile-accessibility job. `ops/release.py` already switches digest-pinned images, checks health, serializes operations, and restores the prior image on failure. `ops/compose.yaml` binds to loopback and limits the serving container to 256 MB.

Owner-confirmed target: Ubuntu IONOS VPS at `195.20.230.75`, 1 vCPU, 1 GB RAM, finance service to be retired, Cloudflare routing, domain `eleccionesespaña2026.es`. ASCII DNS form: `xn--eleccionesespaa2026-83b.es`. Ubuntu version, CPU architecture, disk capacity, current proxy, and actual DNS configuration still need a read-only preflight. The repo assumes Hetzner, a 2-vCPU/8-GB benchmark, and `elecciones2026.es`; the Docker build uses Python 3.12 despite the Python 3.14 roadmap. Record the runtime mismatch without combining a Python migration into this package.

## Goals / Non-Goals

**Goals:** turn passing CI into an explicitly approved, recoverable deployment; build away from the small host; provide a precise owner setup checklist.

**Non-Goals:** automatic editorial approval, zero-downtime guarantees, a permanent CI runner on the VPS, automatic removal of finance data, or a capacity promise from existing rehearsals.

## Decisions

### Personal repository transition — 2026-11-20

The owner selected `barnolacesc/elecciones2026` as the future repository and
retained IONOS. During transition, CI accepts only that path and the existing
`c2ventures/elecciones2026`, on trusted main pushes. The publishing namespace
follows the active repository, and package visibility checks use the matching
GitHub user or organization API. Delivery binds CI metadata and image digests
to the active allowlisted `GITHUB_REPOSITORY`; one location cannot supply a
candidate for the other. Private images and manual approval remain required.

The root-owned VPS wrapper permits both exact image namespaces so retained
legacy images remain available for rollback. The operator must install the
reviewed wrapper and verify new private-registry access before new-owner
delivery. Keep the legacy namespace until retained rollback images no longer
need it. Follow `ops/REPOSITORY-TRANSFER.md` for the ordered account, host and
post-transfer checks. This PR does not execute them.

The generated Spanish footer credits development to `barnolacesc` through a
plain GitHub link. The README identifies the maintainer and pending transfer.
Existing source attributions, political reviews and copyright notices retain
their recorded identity. No home-cluster deployment or domain change is included.

### 1. Extend the existing trusted workflow

Keep PR jobs read-only. Add trusted-main image publication to existing CI with validation, mobile accessibility, Docker parity and isolation dependencies. A separate manually dispatched delivery workflow validates the successful canonical main CI run and its artifact before receiving production secrets. Never use `pull_request_target` or execute untrusted artifacts with release credentials. The delivery record must match the selected main run, revision and run attempt; mutable tags cannot select a release.

Build once for the inspected host architecture, test that exact image, scan it with an approved policy, and publish it to private GHCR. Deploy its registry digest; commit tags are labels only. Do not rebuild after tests. Pin new actions by reviewed full commit SHA. Publishing uses job-scoped `packages: write` and the ephemeral `GITHUB_TOKEN`; deployment uses `contents: read` only. Retain revision, digest, scan, build inputs, and approval references in release evidence. The existing pipeline's audit and rehearsal success are not production content approval.

Use protected `production` environment secrets and main-only deployment rules. Required reviewers are unavailable on this private repository plan. The owner selected explicit manual dispatch as an operator self-approval gate; restrict dispatch/rerun to the release owner and require an approval record and affirmative checkbox. This does not provide independent review. Verify these protections are available for this repository's visibility and GitHub plan before implementation activation. If unavailable, keep deployment disabled until an equivalent enforceable gate is agreed. Use workflow concurrency with no cancellation of active production switches, plus the existing host lock. Normal main pushes can produce candidates; they must wait for approval to activate.

### 2. Ship images, not a repository checkout

The VPS pulls the approved image; it does not clone or build the repository. Install reviewed release tooling once under root-owned `/opt/elecciones2026/`. Subsequent tooling updates are separate reviewed operator actions. This avoids a GitHub repository deploy key and avoids allowing CI to upload arbitrary code that sudo would run.

Keep GHCR private while it contains rehearsal material. Give the host a separately stored, expiring classic PAT with `read:packages` and minimal account/package access, under an approved account and SSO authorization if required. Do not reuse CI's short-lived token as a persistent host credential. Use `docker login --password-stdin` during owner provisioning; keep the Docker credential file root-only or use a credential helper. Public images would avoid a pull token but could disclose private pilot content, so they are excluded at this stage.

### 3. Restrict SSH to the deployment operation

Reuse the existing `deployer` identity with the owner-approved existing deploy key. The owner removed its Docker-group membership; replace its obsolete finance sudo rule with only the root-owned release wrapper. The public key goes in root-owned `/etc/ssh/authorized_keys/deployer`, selected by the account-specific SSH configuration; the private key goes in the protected GitHub environment. This key authenticates to IONOS, while a GitHub repository deploy key authenticates to GitHub. They serve different endpoints.

Use a forced command with no PTY, agent forwarding, port forwarding, or arbitrary shell execution. A root-owned wrapper accepts only an allowlisted GHCR repository plus a full sha256 digest, or a protected rollback action. Reject malformed input, extra arguments, and shell syntax; never evaluate `SSH_ORIGINAL_COMMAND`. The SSH user cannot edit the controller, Compose file, wrapper, state, or registry credentials. Grant narrowly defined sudo access to that wrapper only; do not add the user to the Docker group, whose access is effectively root. Restrict environment inheritance, including Compose port/project settings. Root-owned configuration fixes the site paths and selected port.

Store a `known_hosts` entry verified through the IONOS console or an existing trusted operator connection. `ssh-keyscan` output from the same unverified network path is not sufficient trust. Use strict host-key checking and disable secret shell tracing.

The owner explicitly selected standard GitHub-hosted runners and public SSH rather
than a self-hosted runner or VPN. Permit public SSH with key-only authentication,
strict verified host keys, UFW per-source connection rate limiting and OpenSSH
unauthenticated connection limits. Retain the restricted deployer forced command,
root-owned authorized keys and minimal sudo. The owner verified operator key access
before disabling passwords and widening the firewall. Rate limits reduce connection
bursts; they do not eliminate distributed abuse or OpenSSH vulnerability exposure.
Keep OpenSSH patched, preserve console recovery and verify hosted-runner access
before application activation. HTTPS remains restricted to Cloudflare ranges;
visitors connect to Cloudflare rather than directly to the origin.

### 4. Prepare the dedicated small host conservatively

Inspect listeners, service units, Docker projects, firewall rules, and the current reverse proxy. The owner retires the finance service after verifying backups and recovery; this PR does not authorize deleting its data. Reuse an existing compatible proxy, or install host nginx only if preflight confirms no conflicting listener. Do not blindly apply `ops/origin.conf`: its default-server blocks and instructions to remove host sites assume a fresh host.

Keep the static origin on an available loopback port, separate from public TLS. Retain the current non-root/read-only/capability-dropped container and 256-MB limit initially, then measure actual peak usage alongside Ubuntu, Docker, proxy, monitoring, and image pulls. No PDF extraction, build, or load generator runs on the VPS. Require sufficient disk for current, candidate, and retained prior images. Do not globally prune Docker artifacts during transition.

Keep Cloudflare DNS/proxy and Full (strict) TLS, with reviewed IPv4/IPv6 origin restrictions and Authenticated Origin Pulls where configured. Apply those restrictions to the site's actual interfaces/ports after checking recovery access. Verify the domain's IDNA form in DNS, certificates, server names, build configuration, canonical URLs, sitemap, and social previews. Mutable assets must revalidate as documented in the existing proxy. Private staging requires real authentication and no-store; robots exclusions alone do not make it private.

### 5. Verify origin and edge separately

Invoke the existing controller only through the restricted wrapper. Origin health failure restores the previous image; a first-release failure removes the candidate. After origin success, check approved external HTTPS home/topic/method routes, security/cache headers, and release identity. Purge mutable Cloudflare URLs after release and rollback with a zone-scoped purge token. A failed purge or external probe fails the deployment and requires protected operator recovery; do not automatically restore known incorrect editorial content.

Retain prior images and a restricted release-state backup; test registry-unavailable rollback, first-release failure, and a fresh-host restore. Measure end-to-end recovery including edge/cache checks against the existing <5-minute target. Install an independent external probe and approved alert route; avoid visitor URL/IP logging. The existing local load report and the CI burst saturation do not establish capacity on this 1-GB host. Repeat approved scenarios using off-host generators; revise capacity or approved targets based on measured results.

## Personal-finances deployment review

Reviewed `barnolacesc/personal-finances` main revision `5c705d7f2be8cce74bc5b2434c078341d1b690c2` through the GitHub API. Only repository workflow files were read; secret values, server configuration and authorized keys were not inspected.

| Observed finance behavior | Election-site decision |
|---|---|
| VPS workflow uses `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, SSH, and retried loopback HTTP checks | Preserve secret naming and SSH/HTTP checks; use a new restricted election deployer key |
| VPS workflow has `if: false` while the server is repurposed | Preserve the disabled finance workflow; owner confirms retirement before site activation |
| VPS workflow records live `ssh-keyscan` output as trust | Require an independently verified `VPS_KNOWN_HOSTS`; reject mismatches |
| Key/host secrets appear directly in shell source expressions | Pass secrets through environment variables, validate connection values, quote arguments, and securely remove temporary key files |
| VPS workflow fetches a moving branch and installs dependencies on the server | Test and scan a single CI-built image; deploy its immutable digest without a server Git checkout or build |
| Deployment is a standalone push workflow with no visible test dependency, environment approval, explicit token permissions, or concurrency | Make release depend on all required checks, protected approval, read-only deployment permissions, and serialized switches |
| HTTP checks run after restart without a retained-artifact recovery step | Keep origin and external probes; add automatic failed-origin recovery and protected rollback |
| Raspberry Pi production workflow uses password SSH and `StrictHostKeyChecking=no` | Use dedicated key authentication and strict verified server identity; do not copy password SSH |
| Finance PR tests run on a persistent self-hosted runner and reuse a virtual environment | Keep untrusted PR tests off the privileged delivery runner; any delivery runner must be isolated from PR execution and the VPS |

The finance workflows establish an operational reference, not evidence that the current VPS firewall, SSH permissions or GitHub protection rules are secure. Review these during preflight. No changes are made to the finance repository in this package.

## Owner setup checklist

| Item | Needed value or access | Where it belongs |
|---|---|---|
| VPS details | Host/IP, SSH port, Ubuntu version, architecture, disk space, console access | Restricted operations inventory; environment secrets for host/user and variable for port |
| Host preflight | Current proxy/listeners, firewall, retirement confirmation, verified finance backup | Owner-reviewed operations record |
| Domain | `eleccionesespaña2026.es` / `xn--eleccionesespaa2026-83b.es`, zone and DNS control | Build/proxy configuration; approved Cloudflare zone |
| Deploy identity | Dedicated username and public key | VPS restricted SSH account |
| `VPS_SSH_KEY` | Dedicated deployment private key; matching public key is installed on the VPS | GitHub `production` environment secret only |
| `VPS_KNOWN_HOSTS` | Independently verified host-key entry, including nonstandard port if used | GitHub `production` environment secret |
| `VPS_HOST` | `195.20.230.75` (bare IP, without `http://`) | GitHub `production` environment secret; matches finance workflow naming |
| `VPS_USER` | Reused `deployer` username with restricted release permissions | GitHub `production` environment secret; matches finance workflow naming |
| `VPS_SSH_PORT` | Verified SSH port | GitHub `production` environment variable |
| Runner path | GitHub-hosted runner to owner-approved public key-only SSH with connection limiting | CI/network owner configuration |
| Registry publishing | Actions package permissions | Workflow-scoped `GITHUB_TOKEN`; no extra publishing PAT |
| Registry pull | Account and expiring `read:packages` credential for private GHCR image | Root-only VPS registry credentials, not repository or chat |
| Cloudflare | Zone ID; token with only needed cache-purge rights for this zone | Environment variable and protected secret (`CLOUDFLARE_ZONE_ID`, `CLOUDFLARE_PURGE_TOKEN`) |
| Repository administration | Authority to configure environment reviewers, branch checks, secrets, and package access | GitHub owner/admin setup |
| Release approval | G0/G2/G3/G4 evidence, reviewed public corpus, accessibility/security/load evidence | Restricted release record and production approval |

Configure `VPS_HOST=195.20.230.75`, `VPS_USER=deployer`, `VPS_SSH_KEY`, and `VPS_KNOWN_HOSTS` under repository **Settings → Environments → production → Environment secrets**. Reference them through the `secrets` context, for example `${{ secrets.VPS_HOST }}` and `${{ secrets.VPS_SSH_KEY }}`. Configure `VPS_SSH_PORT` under **Environment variables** and reference `${{ vars.VPS_SSH_PORT }}`. The public IP and username do not require secrecy, but storing them as secrets matches the owner's finance workflow and masks routine output.

Install only the matching public deployment key in root-owned `/etc/ssh/authorized_keys/deployer`; account-wide ForceCommand and forwarding/TTY restrictions prevent old home keys or mutable home configuration from bypassing this access policy. The owner explicitly chose the existing deployment key; rotate it separately when reviewing other systems that trust it. Never reuse a password. Matching secret names do not share values across repositories: provision each value explicitly in this repository's protected environment. The verified server host-key entry is separate from the deployment key pair. The owner reports production SSH secrets and port configured; API checks confirm main-only deployment rules. Registry pull and activation prerequisites remain pending.

Pass secrets to shell steps through step-level environment variables, not expression substitution inside shell source. Write key and host-trust files into a private temporary directory with `umask 077`, `printf`, and mode 600; disable tracing and clean up through a trap and an always-run fallback. Quote host/user/port values, validate their formats, use noninteractive SSH with `StrictHostKeyChecking=yes`, explicit `UserKnownHostsFile`, `IdentitiesOnly=yes`, and connection timeouts. Never print keys or return raw SSH output that could expose credentials.

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

- What are the SSH port, Ubuntu version, architecture, disk capacity, and current proxy/listeners for `195.20.230.75`? These determine provisioning values, not the release contract.
- Has the GitHub-hosted runner verified restricted key-only SSH access from outside the operator IP? Delivery stays disabled until these prerequisites are satisfied.
- Which notification route and external probe should receive release/availability failures?

## References

- [GitHub: Publishing Docker images](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images)
- [GitHub: Container registry authentication and permissions](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub: Deploy keys authenticate access to a repository](https://docs.github.com/en/enterprise-cloud%40latest/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
- [GitHub: Deployment environments and required reviewers](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)

- [GitHub: Configuration variables and the vars context](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables)
- [GitHub: Environment secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)

- [Reviewed finance VPS workflow](https://github.com/barnolacesc/personal-finances/blob/5c705d7f2be8cce74bc5b2434c078341d1b690c2/.github/workflows/deploy-test.yml)
- [Reviewed finance Raspberry Pi workflow](https://github.com/barnolacesc/personal-finances/blob/5c705d7f2be8cce74bc5b2434c078341d1b690c2/.github/workflows/deploy.yml)
- [Reviewed finance test workflow](https://github.com/barnolacesc/personal-finances/blob/5c705d7f2be8cce74bc5b2434c078341d1b690c2/.github/workflows/test.yml)

## Implementation progress

The restricted release wrapper, shell launchers, sudo policy, account-specific SSH policy and [installation runbook](../../../ops/RESTRICTED-DEPLOYMENT.md) implement task 3.1. Requests use fixed root-owned paths, a clean environment and the election GHCR repository allowlist. A `check` request verifies access without deployment. The runbook records the owner-provided Ubuntu preflight and uses the existing `deployer` account. Production environment approval rules, live provisioning and runner connectivity remain pending; no production delivery is activated.

## Registry, delivery and domain preparation

The domain is registered at DonDominio, not yet active in Cloudflare. Delegation
does not require registrar transfer. Current candidates are classified as private
staging; the origin enforces Basic authentication and no-store on the preview
hostname. The manual delivery workflow verifies unauthenticated rejection before
switching and exact home content after switching. Public classification, cache
purge and launch evidence remain later gated tasks, not automatic consequences
of successful staging delivery. See [setup](../../../ops/IONOS-DELIVERY.md).
