# E3.3 IONOS delivery setup

Status: the owner has completed registry login, Cloudflare delegation, origin TLS,
authenticated preview nginx and SSH/UFW setup. Private staging activation and
hosted external verification passed in delivery run 38182379207.
The [server migration runbook](SERVER-MIGRATION.md) records the verified setup,
remaining limits and a future Hetzner migration option. The owner set
`DEPLOYMENT_READY=true` before the successful private delivery. Each later delivery
still requires the owner-selected manual dispatch and artifact-linked approval.
Set the variable false during preparation or migration; it is an activation
prerequisite, not public-release approval.
The target is Ubuntu 22.04 AMD64, 1 vCPU and 1 GB RAM, at `195.20.230.75`.
The owner retired the finance service and rebooted the host. Preserve unrelated
volumes. Retained-data backup, full external firewall probes, monitoring and capacity evidence remain
open in the OpenSpec task record.

The earlier 2-vCPU/8-GB host sizing remains a planning baseline. It does not
establish capacity on the active IONOS host. Service and cost targets remain
unchanged. The sections below are repeatable setup instructions; they do not
mean the verified preview setup is still pending.

## Current-election candidate preparation (E1.4-2026)

CI now builds `es-gen-2026` with the strict production record directory and
`pilot_mode=approved-records-only`. Candidate classification remains
`private-staging`; an empty reviewed corpus means a pending private preview.
The validator retains `es-gen-2023` / `source-linked-provisional` compatibility
for reviewed operator-selected recovery. Mixed election/mode pairs and public
classification are rejected. None of these technical changes grants source,
reuse, editorial or public release approval.

On 2026-11-12 apex and www resolve through Cloudflare but respond 521. The
private preview responds 401. Read-only host inspection confirms valid Nginx
syntax and a preview-only authenticated server block. Public activation must
use the G4-approved current-election artifact; exposing the existing historical
container is not an authorized substitute.

## 1. DNS delegation: keep DonDominio as registrar

Current verified preview setup also requires the hostname-specific Disable RUM
Configuration Rule described in [the migration guide](SERVER-MIGRATION.md#8-registry-and-github-delivery-settings).
It prevents Cloudflare analytics injection from changing the approved page bytes.

The owner bought `eleccionesespaña2026.es` at DonDominio. A registrar transfer is
not needed. Add the domain to Cloudflare using its normal full DNS setup; use
`xn--eleccionesespaa2026-83b.es` if a field requires the ASCII DNS form.
Select the Free plan and review the imported records. Preserve any existing mail
records. Cloudflare assigns two nameservers: copy those exact names to the domain's
nameserver settings at DonDominio, replacing the old nameservers. If DNSSEC is
already enabled, disable the old registrar DS before changing delegation, then
re-enable DNSSEC with Cloudflare's new DS after activation. Wait for the zone to
report Active. Do not invent or use another zone's nameservers.

First prepare authenticated staging at
`preview.xn--eleccionesespaa2026-83b.es`. Add a proxied A record named `preview`
with value `195.20.230.75`. Add no AAAA record until working IPv6 and its firewall
rules are verified. Do not route the apex or www to fixture/private pilot output.
The public apex A record, www redirect and public cache rule are G4 actions.

## 2. Registry access: separate publish and pull identities

CI's `publish-candidate` job uses its temporary `GITHUB_TOKEN` with `packages: write`.
No additional GitHub secret or repository deploy key is required to publish.
The package must be private; publication refuses an existing public package.
Review package settings after the first trusted-main publication and verify that
private access is inherited from this private repository. Never change visibility
while it contains private rehearsal content.

For the VPS, create an expiring **classic** GitHub personal access token with only
`read:packages`, using an account that can read this package. Authorize organization
SSO if required. A classic token can read other packages accessible to that account;
use a dedicated account with minimal access when that boundary is required.
Fine-grained PATs are not supported for this registry login. Store the credential
in the owner's secret manager; never put it in chat, Git or command arguments.

After reviewing and copying the helper to the VPS, run from the root console:

```sh
sh ops/registry-login GITHUB_USERNAME
```

Enter the token at Docker's hidden password prompt. The helper stores credentials
in `/root/.docker/config.json` with directory mode 700 and file mode 600. Docker
stores encoded credentials, not encrypted credentials; restrict root access and
prefer an approved credential helper if available. Set an expiry/rotation reminder.
The restricted release wrapper already selects `/root/.docker` explicitly.
Once CI publishes a candidate, verify access without starting a container:

```sh
DOCKER_CONFIG=/root/.docker docker pull ghcr.io/c2ventures/elecciones2026@sha256:APPROVED_DIGEST
```

## 3. TLS and authenticated staging

Install host nginx and `apache2-utils` through the Ubuntu package manager. Create
`/etc/elecciones2026/tls` root-owned with mode 700. In the active Cloudflare zone,
create an Origin CA certificate covering both the ASCII apex and
`*.xn--eleccionesespaa2026-83b.es`. Save certificate as `origin.pem` and its private
key as `origin.key` in that directory, with root ownership and key mode 600.
These files belong in the owner's secret manager and VPS, never the repository.
Download and verify the official Cloudflare Authenticated Origin Pull CA as
`origin-pull-ca.pem`; it is distinct from the server certificate.

Set Cloudflare to **Full (strict)** and enable **Authenticated Origin Pulls**.
Enable the edge redirect to HTTPS. For staging, add an explicit Cache Rule that
bypasses cache for `preview.xn--eleccionesespaa2026-83b.es`; apply no public cache
rule to it. Disable content-transform features so external content hashes remain
stable. Preserve the generated security headers.

Create a separate staging password (do not reuse an SSH or registry credential):

```sh
htpasswd -cB /etc/elecciones2026/staging.htpasswd STAGING_USERNAME
chown root:www-data /etc/elecciones2026/staging.htpasswd
chmod 640 /etc/elecciones2026/staging.htpasswd
```

Install **only** `ops/staging-origin.conf` in nginx's enabled HTTP configuration
for the first private release. Remove default HTTP sites/listeners after reviewing
unrelated configurations. The staging template requires Basic authentication at
the origin as well as AOP, sends `private, no-store`, and disables indexing.
It does not route the apex. `ops/origin.conf` is the public alternative for a later
G4-approved artifact; do not enable both copies of their default server.
Test with `nginx -t` before reload. Nginx's worker needs read access to the password
file; only root must have write access.

Apply the reviewed IONOS firewall before enabling the proxy: key-only SSH with UFW `limit 22/tcp` for hosted runners plus the approved
operator IP allow rule; 443 only from official
Cloudflare IPv4 and IPv6 ranges; no public 80 or 8080. Preserve console recovery.
Global AOP authenticates Cloudflare's network, not an exclusive Cloudflare account.
Staging's origin password is an additional independent content boundary.

## 4. GitHub settings and manual approval

Keep existing production secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`,
`VPS_KNOWN_HOSTS`. Keep production variable `VPS_SSH_PORT=22`.
Add production secret `STAGING_BASIC_AUTH` with the value
`STAGING_USERNAME:STAGING_PASSWORD`, matching the origin password file.

All workflow jobs use standard GitHub-hosted `ubuntu-latest` runners. The owner
selected public SSH with key-only authentication, strict verified host keys, the
restricted deployment account and UFW connection rate limiting. No self-hosted
runner or VPN is required. Keep builds and tests off the small VPS. This choice
exposes the SSH service to Internet connection attempts; patch OpenSSH and keep
unauthenticated connection limits. Rate limiting reduces bursts, not distributed
attacks or vulnerabilities. The IP-specific operator allow rule intentionally
bypasses the general rate limit for the approved operator address.

For a new setup, set repository variable `DEPLOYMENT_READY=true` only after registry pull, TLS,
DNS, authenticated staging, firewall and hosted-runner connectivity are verified.
Until then dispatch fails in authorization without exposing production secrets.

The private repository's plan does not provide required environment reviewers.
The owner selected manual workflow dispatch as the operator approval gate, with
main-only environment deployment rules. This is operator self-approval, not
independent review. `deliver.yml` restricts both dispatch and rerun actors to
`barnolacesc`; review this allowlist when the release owner changes.

After merging through repository review and successful main CI, choose
**Actions → Deliver approved staging candidate → Run workflow → main**. Enter the
successful CI run ID, a restricted approval-record reference, and explicitly
check the candidate approval box. Review scan/content evidence first. Automatic
main pushes publish candidates; they never activate a container.

CI builds once for AMD64, tests and scans that image, saves it between jobs,
and publishes it privately. The candidate record binds image digest/config ID,
Git revision, run ID/attempt, home content hash and private-staging classification.
Manual delivery verifies the successful canonical main CI run and its immutable
artifact, confirms staging rejects unauthenticated requests, then requests
`check` and `deploy REPOSITORY@sha256:DIGEST` through restricted SSH. The VPS pulls
and starts that image with Compose. Routine updates use neither SCP nor Git pull.
Strict host authentication is mandatory; temporary SSH credential files are removed
on success or failure. External HTTPS verifies authentication, content hash and
security/cache headers. An external failure reports failed delivery; the origin
may already have switched. Inspect its state before operator recovery.

## 5. Recovery and public activation

Use the existing restricted `rollback` request only after reviewing the previous
approved digest and confirming it does not restore known incorrect political
content. Origin health failure already recovers the preceding image automatically.
For an external failure, a manual dispatch of a reviewed earlier candidate can
restore its exact digest and repeat external verification. Authenticated staging
uses no-store and cache bypass; a public release needs the separately approved
zone-scoped cache purge, editorial/public classification checks and public probe.
The current workflow deliberately accepts private-staging records only. It cannot
publish fixtures through the apex. Those public gates and live recovery/capacity
checks remain open in OpenSpec; no green CI result substitutes for G2/G4 approval.

References: [Cloudflare full DNS setup](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/),
[GHCR authentication](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry),
[Origin CA](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/),
[Authenticated Origin Pulls](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/).

## Historical owner-provided live setup evidence — 2026-10-11

This pre-activation record is retained for history. The later [2026-10-12 setup
record](SERVER-MIGRATION.md#current-setup-and-verification) supersedes its pending
application and image-pull status: private delivery and exact external content
verification passed in run 38182379207.

Cloudflare delegation is active. The owner installed matching Origin CA certificate
and key (expiry 2028-10-10), covering apex and wildcard, and the global Origin Pull
CA (expiry 2029-11-01). Global AOP and Full (strict) were enabled; preview DNS is
proxied. Nginx syntax passed and the host listens on 443 only for HTTPS, with no
port 80 or application listener yet. External unauthenticated preview returned
401 with no-store/noindex; authenticated request returned the expected 502 while
the application is absent. Exact served application content remains unverified.

The owner confirmed root key-only login, installed `ssh-key-only.conf` settings
as `/etc/ssh/sshd_config.d/00-elecciones-key-only.conf`, validated sshd, reloaded it
and successfully opened a new key-authenticated operator session. UFW is active:
default deny incoming; operator-specific SSH allow; public IPv4/IPv6 SSH limit;
443 allowed only from the reviewed Cloudflare ranges; old port 5001 rule removed.
The owner reported GHCR login succeeded and the staging secret was provisioned.
A successful login does not yet prove access to the published private image.
