# E3.3 IONOS delivery setup

Status: prepared for review. No live registry login, DNS change, TLS installation,
or application activation has been performed by these files. Delivery stays
blocked until repository variable `DEPLOYMENT_READY=true` is deliberately set.
The target is Ubuntu 22.04 AMD64, 1 vCPU and 1 GB RAM, at `195.20.230.75`.
The owner retired the finance service and rebooted the host. Preserve unrelated
volumes. Retained-data backup, firewall, monitoring and capacity evidence remain
open in the OpenSpec task record.

## 1. DNS delegation: keep DonDominio as registrar

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

Apply the reviewed IONOS firewall before enabling the proxy: SSH from approved
operators and the approved delivery connection path; 443 only from official
Cloudflare IPv4 and IPv6 ranges; no public 80 or 8080. Preserve console recovery.
Global AOP authenticates Cloudflare's network, not an exclusive Cloudflare account.
Staging's origin password is an additional independent content boundary.

## 4. GitHub settings and manual approval

Keep existing production secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`,
`VPS_KNOWN_HOSTS`. Keep production variable `VPS_SSH_PORT=22`.
Add production secret `STAGING_BASIC_AUTH` with the value
`STAGING_USERNAME:STAGING_PASSWORD`, matching the origin password file.

Repository variable `DEPLOY_RUNNER_LABELS` is a JSON array of runner labels for
the approved connection path. Do not select a persistent runner that executes
untrusted PRs or run a build runner on the small VPS. A hosted runner needs an
explicitly approved way to reach SSH; do not widen the firewall silently.
Set repository variable `DEPLOYMENT_READY=true` only after registry pull, TLS,
DNS, authenticated staging, firewall and runner connectivity are verified.
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
