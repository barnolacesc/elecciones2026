# E3.3 server setup and migration runbook

Use this guide to reproduce the election site's setup on a replacement Ubuntu
server, including a future Hetzner host. This documents configuration and operator
steps; it is not an automated provisioning script or permission to migrate now.
The current setup record is dated **2026-10-12**. Package: **E3.3**.

The planned transfer to `barnolacesc/elecciones2026` keeps IONOS. Follow the
[repository transfer runbook](REPOSITORY-TRANSFER.md) for pending account,
registry and wrapper steps; the dated evidence below does not verify that transfer.

Replace uppercase placeholders such as `NEW_VPS_IP`, `OPERATOR_PUBLIC_IP` and
`REVIEWED_CLOUDFLARE_CIDR` before running commands. Host commands assume an
operator root shell; SSH and external probes explicitly marked Mac run locally.

## Current setup and verification

| Component | Confirmed setup | Evidence or remaining limit |
|---|---|---|
| Host | IONOS, `195.20.230.75`, Ubuntu 22.04.5, AMD64, 1 vCPU, 856 MiB visible RAM | Owner terminal output; no swap; new-host capacity must be measured |
| Previous services | Finance service stopped/disabled; containers removed; Docker group removed from deployer | Unrelated PostgreSQL volume retained; finance backup/restore not verified |
| Updates | Host rebooted; latest owner login reports zero immediately applicable updates | ESM notices remain; no OS release upgrade performed |
| Registry | Root login to private GHCR with account `barnolacesc` | Owner confirmed exact private candidate pull after refreshing login |
| Registrar / DNS | Domain bought at DonDominio; nameservers delegated to Cloudflare | Owner confirmed active delegation; DNSSEC not verified |
| Domain | `eleccionesespaña2026.es` / `xn--eleccionesespaa2026-83b.es` | Canonical base uses the ASCII HTTPS form |
| Preview DNS | Proxied A record `preview` → `195.20.230.75` | External requests reach Cloudflare and the authenticated origin |
| Origin TLS | Matching Origin CA certificate and key; apex plus wildcard SANs | OpenSSL parse, public-key match and SAN checks passed; expires 2028-10-10 |
| Origin client authentication | Global Cloudflare Authenticated Origin Pulls (AOP), nginx client-certificate verification | AOP CA parsed; expires 2029-11-01; global AOP is not exclusive to this account |
| Cloudflare TLS mode | Full (strict), reported configured by owner | External HTTPS succeeds; dashboard/API mode not independently exported |
| Preview access | HTTP Basic username `preview`; bcrypt password file | No password value in this guide; unauthenticated GET returned 401, no-store/noindex |
| Nginx | TLS listener on IPv4/IPv6 443; default port-80 site disabled | Authenticated preview returns 200 with required security/no-store headers |
| SSH | Key-only root/operator access; restricted deployer forced command | New operator login and effective deployer settings verified |
| Firewall | Active UFW, deny incoming, allow outgoing, deny routed; IPv6 enabled | Public SSH LIMIT, operator-specific SSH ALLOW, Cloudflare-only 443; old 5001 rule removed |
| GitHub | Hosted runners, main-only production environment, DEPLOYMENT_READY=true | Delivery run 38285301273 passed approval, restricted SSH and external verification |
| Preview analytics | Configuration Rule matches preview hostname; Disable RUM enabled | Owner deployed rule; hosted page hash now matches the approved image |
| Application | Approved private candidate activated and healthy | Exact home hash verified from hosted runner; live rollback/restore and capacity remain unverified |

Always update this table after a real verification. A login, nginx syntax check or
401 response does not establish a healthy application or measured capacity.

Successful private staging evidence: [delivery run 38285301273](https://github.com/c2ventures/elecciones2026/actions/runs/38285301273),
using successful main CI run `38281740524`, attempt `1`, revision
`01b77bcdcafb988bb5ea88e7d5df6afc34bcc430`:

- Image: `ghcr.io/c2ventures/elecciones2026@sha256:6a0ed41438faba6f81cce2a61d4cce7e4fb288b1fa395e03f32de708d30741ca`.
- Home SHA-256: `2615469859601fa902710fa849c0f194729a1b1e51282982f74ebb976de9591b`.
- Boundary: private `es-gen-2023` preview, merged redesign, zero published
  statements and relationships, and unavailable quiz. PP/ERC candidates remain unpublished.
- The owner approved this exact tested candidate in the project session on
  2026-10-12. Retained reference:
  `private-reviews:es-gen-2023/owner-preview-release-38281740524-1.json`.
- Protected delivery passed the origin deployment, pre/post unauthenticated 401,
  authenticated HTTP 200, exact home bytes and required security/no-store headers.
  A separate local curl request with the deployment user agent confirmed 401,
  Basic authentication, private/no-store and noindex/nofollow after delivery.
- Exact-image inspection and CI establish the election, redesign, zero-claim
  browser projection and unavailable quiz. Hosted browser/device checks remain
  in #44; public G4, monitoring, live rollback/restore and capacity remain open.

Delivery `38182379207` is historical evidence for the preceding image. It
predates the review withdrawal and redesign; do not restore it without a new
content and release review.

## Configuration and secret inventory

| Source or secret | Destination / use | Ownership and access |
|---|---|---|
| `restricted_release.py`, `release.py`, `compose.yaml` | `/opt/elecciones2026/` | root:root; directory 755, files 644 |
| `elecciones-release` | `/usr/local/sbin/elecciones-release` | root:root, 755 |
| `elecciones-ssh` | `/usr/local/libexec/elecciones-ssh` | root:root, 755 |
| `deployer.sudoers` | `/etc/sudoers.d/deployer` | root:root, 440 |
| `deployer-sshd.conf` | `/etc/ssh/sshd_config.d/00-elecciones-deployer.conf` | root:root, 644 |
| `ssh-key-only.conf` | `/etc/ssh/sshd_config.d/00-elecciones-key-only.conf` | root:root, 644 |
| Approved deployment public key | `/etc/ssh/authorized_keys/deployer` | root:root, 644; deployer cannot edit |
| `staging-origin.conf` | `/etc/nginx/sites-available/elecciones2026` plus enabled symlink | root-owned; install this for current private candidates |
| Origin certificate / key | `/etc/elecciones2026/tls/origin.pem`, `origin.key` | root:root; directory 700, files 600 |
| Official AOP CA | `/etc/elecciones2026/tls/origin-pull-ca.pem` | root-owned; contains no private key |
| Staging password hash | `/etc/elecciones2026/staging.htpasswd` | root:www-data, 640 |
| Root registry login | `/root/.docker/config.json` | directory 700, file 600; encoded credentials, not encryption |
| Release state | `/var/lib/elecciones2026/release.json` | root-only state directory 700; current and previous digests |
| `origin.conf` | Public alternative to staging nginx configuration | Requires approved public content and G4; never enable both default servers |

Existing 1Password items reported by the owner:

- `Elecciones Cloudflare Origin TLS`: certificate, private key, domain and expiry.
- `deploy test personal finances`: reused deployment SSH key, explicitly retained
  by the owner. Review other systems trusting it before a future rotation.
- The GHCR pull token and separate staging password were saved/provisioned by the
  owner. Record their actual item names in the private operations inventory.
- The operator key is separate from the deployer key. Do not assume it is in the
  same item or copy its private half into the VPS.

No secret values belong in Git, chat, shell arguments or CI logs. Store restricted
configuration/state backups outside the repository. Do not copy the old host's SSH
host private keys to the new host: verify and trust the replacement identity.

## 1. Plan a replacement without changing live traffic

Choose a supported Ubuntu AMD64 host. CI currently builds `linux/amd64`; choosing
ARM requires a separately reviewed build/platform change. Record the new IP,
operator address, console recovery, disk, RAM, architecture and intended DNS
records. Verify capacity on the new host rather than inheriting old estimates.

Keep the old origin and retained images available during cutover. Pause application
switches by setting repository variable `DEPLOYMENT_READY=false`; wait for active
and queued delivery jobs to finish or be resolved before copying release state.
Record the approved current/previous digests, corresponding CI runs, editorial
approval and exact tooling commit. Do not restore a known incorrect factual release.

Preserve unrelated service data through a reviewed backup. Do not repeat the
original global container prune on a replacement or shared server. No bulk service
removal is required on a fresh Hetzner instance.

## 2. Prepare Ubuntu and Docker

Keep a root/operator session and provider console available. Inspect first:

```sh
cat /etc/os-release
uname -m
free -h
df -h /
systemctl --failed
ss -lntp
```

Apply reviewed Ubuntu updates and reboot if required, then verify a new operator
login. Install Python 3, curl, CA certificates, OpenSSH, sudo, UFW, nginx and
apache2-utils. On a fresh supported Ubuntu host, install Docker Engine and Compose
using the [official Docker apt instructions](https://docs.docker.com/engine/install/ubuntu/).
Avoid mixing Ubuntu Docker packages and Docker's upstream packages; do not remove
an existing installation blindly. The old host's recorded version is inventory,
not a requirement to install that historical version on a new server.

```sh
apt-get update
apt-get install -y python3 curl ca-certificates openssh-server sudo ufw nginx apache2-utils
systemctl stop nginx
docker version
docker compose version
```

Nginx is stopped while TLS and firewall configuration are incomplete. Do not add
the deployer to the Docker group. Docker port publishing can bypass UFW; production
Compose must retain its explicit `127.0.0.1:8080:8080` binding.

## 3. Install the restricted deployment boundary

Create the `deployer` account with a home and executable shell if it does not
exist. Keep it out of Docker and general sudo groups. Existing accounts need an
actual membership/privilege review; an account name alone provides no boundary.

Download an exact reviewed repository commit on the operator's Mac, transfer its
archive using the operator account, and install the files using
[restricted deployment setup](RESTRICTED-DEPLOYMENT.md), sections 1–3. That guide's
`195.20.230.75` examples must be replaced with the new host IP. Routine releases
never upload a repository or executable wrapper through the deployer account.

Validate root ownership, sudo syntax and the forced-command policy. Test the
non-mutating `check` request; arbitrary `id` must fail. Retain any old sudo policy
as a restricted backup before replacement. A host tooling update is a reviewed
operator action, not a normal image delivery.

Install the reviewed controller that supports repeated-image health checks (the
owner installed this update from PR 61). An older controller rejects an already
current digest before external verification. The updated controller verifies health
without pulling or overwriting the previous release record; failed health still
fails delivery. Include this behavior when restoring host tooling on Hetzner.

## 4. Make SSH key-only before opening it to hosted runners

First prove a second operator connection works with key authentication from the Mac:

```sh
ssh -o PreferredAuthentications=publickey \
    -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no \
    root@NEW_VPS_IP
```

If too many agent keys are offered, use `IdentitiesOnly=yes` with the explicitly
selected operator key. Do not use the deployer key for administration.

Install the repository's key-only policy from the reviewed extraction directory:

```sh
install -o root -g root -m 644 ops/ssh-key-only.conf \
  /etc/ssh/sshd_config.d/00-elecciones-key-only.conf
sshd -t
sshd -T | grep -E '^(passwordauthentication|kbdinteractiveauthentication|authenticationmethods|permitrootlogin|maxauthtries|maxstartups) '
sshd -T -C user=deployer,host=github-runner,addr=203.0.113.10 |
  grep -E '^(authenticationmethods|passwordauthentication|forcecommand|disableforwarding|permittty|permituserrc) '
```

Expect publickey-only authentication, password/interactive disabled, root
`without-password`/`prohibit-password`, MaxAuthTries 3 and MaxStartups 10:30:30.
The deployer must retain `/usr/local/libexec/elecciones-ssh`, no forwarding, no
TTY and no user RC. The sample address tests effective configuration; it is not a
real hosted-runner connectivity probe. OpenSSH takes the first applicable setting;
if output differs, inspect Include/Match ordering before reloading.

Reload with `systemctl reload ssh` only after syntax and effective settings pass.
Test another operator key login while keeping the original session open. Public
SSH with key-only access and connection limiting is the owner's selected network
policy; no VPN or self-hosted Actions runner is required.

## 5. Reproduce the firewall

On a new host, use the operator's current public address, not the historical
`88.148.27.13`. An SSH session reports it as the first field of `$SSH_CONNECTION`.
Review existing rules with `ufw show added`; do not erase unrelated rules on a
shared host. Verify `IPV6=yes` in `/etc/default/ufw` when IPv6 is enabled.

```sh
ufw allow from OPERATOR_PUBLIC_IP to any port 22 proto tcp
ufw limit 22/tcp
```

Allow TCP 443 only from the current official [Cloudflare IPv4 list](https://www.cloudflare.com/ips-v4)
and [IPv6 list](https://www.cloudflare.com/ips-v6). Download and review both lists
before applying rules; for each validated CIDR:

```sh
ufw allow from REVIEWED_CLOUDFLARE_CIDR to any port 443 proto tcp
```

The original Python urllib download received HTTP 403. If downloads fail, fetch
and verify the official lists through another trusted operator connection and
transfer those reviewed CIDRs; never substitute `allow 443/tcp` or silently use an
empty list. Do not permanently hard-code the 2026 ranges as migration truth.

Remove obsolete service-port rules after ownership review (the old host had a
5001/tcp allow rule). Do not allow public 80 or 8080. Set deny incoming and allow
outgoing, review the complete rules, and confirm provider console access first:

```sh
ufw default deny incoming
ufw default allow outgoing
ufw show added
ufw enable
ufw status verbose
```

If the interactive prompt aborts, review the rules again and use `ufw --force enable`
only when ready. Keep the existing session and verify a second operator login.
The operator-specific ALLOW intentionally bypasses the public SSH LIMIT for that
source. Per-source rate limits do not eliminate distributed abuse or vulnerabilities.

For Hetzner, also attach a reviewed Cloud Firewall: permit public TCP 22 (host UFW
supplies connection limiting) and TCP 443 from Cloudflare IPv4/IPv6 CIDRs. Review
its outbound policy so updates, DNS, GHCR and time sync still work. Provider and
host rules must both permit the intended path. See
[Hetzner firewall behavior](https://docs.hetzner.com/cloud/firewalls/overview/).
Verify the effective provider rules and external probes; they were not configured
or verified on Hetzner during the IONOS preparation.

## 6. Restore certificates and authenticated staging

Keep DonDominio registration and existing Cloudflare nameservers when changing
servers; a provider migration does not require a registrar transfer. If setting up
the domain from scratch, follow [DNS delegation](IONOS-DELIVERY.md#1-dns-delegation-keep-dondominio-as-registrar).
Existing mail/DNSSEC records must be preserved and reviewed.

Create the TLS directory, restore the certificate/key from 1Password and preserve
real PEM line breaks. The private key is displayed only once when first generated
by Cloudflare; save it before closing that screen.

```sh
install -d -o root -g root -m 700 /etc/elecciones2026/tls
```

Use the operator's preferred editor to create `origin.pem` and `origin.key`.
Set root ownership and mode 600. Use separate BEGIN/END lines; the original
one-line paste made OpenSSL unable to parse the certificate.

```sh
chown root:root /etc/elecciones2026/tls/origin.pem /etc/elecciones2026/tls/origin.key
chmod 600 /etc/elecciones2026/tls/origin.pem /etc/elecciones2026/tls/origin.key
openssl x509 -in /etc/elecciones2026/tls/origin.pem -noout -subject -dates -ext subjectAltName
```

The certificate must be unexpired and cover the apex plus
`*.xn--eleccionesespaa2026-83b.es`. Validate the private key and matching public keys;
use Bash pipefail so a failed parser does not become a misleading empty-data hash:

```sh
(
  set -o pipefail
  openssl pkey -in /etc/elecciones2026/tls/origin.key -check -noout &&
  openssl x509 -in /etc/elecciones2026/tls/origin.pem -pubkey -noout |
    openssl pkey -pubin -outform DER | sha256sum
)
(
  set -o pipefail
  openssl pkey -in /etc/elecciones2026/tls/origin.key -pubout -outform DER | sha256sum
)
```

Both successful hashes must match. Reuse an unexpired certificate on the replacement
only if the same approved hostnames and key handling remain suitable; otherwise
issue a replacement Origin CA certificate and store its key. Do not replace AOP
trust with the server certificate: they perform different checks.

```sh
curl -fsSLo /etc/elecciones2026/tls/origin-pull-ca.pem \
  https://developers.cloudflare.com/ssl/static/authenticated_origin_pull_ca.pem
openssl x509 -in /etc/elecciones2026/tls/origin-pull-ca.pem -noout -subject -dates
```

In Cloudflare, select Full (strict) and enable **Global Authenticated Origin Pulls**.
Global uses Cloudflare's shared client certificate; it does not exclusively identify
this zone. Zone-level AOP uses custom certificate configuration and is not the
setting used here. Keep origin Basic authentication for private content.

Restore the password hash from a restricted backup or generate a new staging
password in 1Password and create the hash interactively:

```sh
htpasswd -cB /etc/elecciones2026/staging.htpasswd preview
chown root:www-data /etc/elecciones2026/staging.htpasswd
chmod 640 /etc/elecciones2026/staging.htpasswd
```

Use `-c` only for a new/replacement file: it overwrites the password file. If rotating
an existing user's password, omit `-c`. Update GitHub `STAGING_BASIC_AUTH` when the
password changes. Never put the password in command arguments.

## 7. Install the nginx route

From the reviewed extraction directory:

```sh
install -o root -g root -m 644 ops/staging-origin.conf \
  /etc/nginx/sites-available/elecciones2026
ln -s /etc/nginx/sites-available/elecciones2026 /etc/nginx/sites-enabled/elecciones2026
```

If the symlink already exists, inspect its target rather than blindly replacing it.
Disable the fresh Ubuntu default site after checking it is not serving another
application. On the original fresh nginx installation we used
`unlink /etc/nginx/sites-enabled/default`. Then run `nginx -t` before starting.

The original setup archive lacked `staging-origin.conf`, so the owner copied the
reviewed template into the installed nginx site manually. For a migration, obtain
an archive that contains the current configuration; a missing template is not a
reason to expose an unprotected default site.

```sh
nginx -t
systemctl start nginx
systemctl is-active nginx
ss -lntp
```

Expect host listeners on 22 and 443, and only loopback 8080 after an approved
container is activated. No public 80/8080. Private staging sends no-store/noindex,
requires Basic authentication and validates AOP. Do not simultaneously enable the
public and staging templates' default-server blocks.

## 8. Registry and GitHub delivery settings

Before external content verification, create a Configuration Rule in the election
zone: Rules → Configuration Rules → Create rule. Name it `Disable preview analytics`;
match **Hostname equals** `preview.xn--eleccionesespaa2026-83b.es`, or use:

```text
(http.host eq "preview.xn--eleccionesespaa2026-83b.es")
```

Add **Disable Real User Monitoring (RUM)** and enable that setting, then deploy
the rule. This preview-specific rule takes precedence over Web Analytics rules.
Do not change unrelated analytics sites. The owner deployed it after hosted run
38181492298 showed an injected analytics beacon: 25333 bytes instead of 24966,
with a different hash. Mac curl and Python probes returned the original bytes.
After the rule, hosted run 38182379207 verified the exact image content. An
EU-only exclusion is insufficient for consistent delivery from other regions.
See [Cloudflare Disable RUM](https://developers.cloudflare.com/rules/configuration-rules/settings/#disable-real-user-monitoring-rum).

Keep this zone rule when moving the origin to Hetzner. Reproduce it if moving to a
different Cloudflare zone. Do not weaken or normalize the page hash check to allow
injected scripts; approve any future analytics separately.

Create/restore an expiring classic PAT with only read:packages from an account
that can read the private package. Fine-grained tokens do not support this registry
login. Follow [registry setup](IONOS-DELIVERY.md#2-registry-access-separate-publish-and-pull-identities)
and use `sh ops/registry-login barnolacesc` from the root console. Enter the PAT
at the hidden prompt. Reauthenticate on the new host rather than copying the old
Docker credential file. Ensure root-only permissions. Test pulling the exact
approved digest; login alone is insufficient.

| GitHub location | Setting | Migration action |
|---|---|---|
| production environment secret | `VPS_HOST` | Replace with the new bare IP, without a URL scheme |
| production environment secret | `VPS_USER` | `deployer` |
| production environment secret | `VPS_SSH_KEY` | Retain only if its public key was installed; rotate through owner review |
| production environment secret | `VPS_KNOWN_HOSTS` | Replace with independently verified new-host entry |
| production environment secret | `STAGING_BASIC_AUTH` | `preview:PASSWORD`, matching the origin hash |
| production environment variable | `VPS_SSH_PORT` | `22`, unless an approved port change is implemented |
| repository variable | `DEPLOYMENT_READY` | Keep false while migrating; true only after prerequisites and connection verification |
| production environment branch rules | main only | Preserve; do not grant PR branches access |
| workflow authorization | actor and rerun actor `barnolacesc` | Review when the release owner changes |

Verify the new host key via provider console:

```sh
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

On the Mac, collect its candidate public entry with `ssh-keyscan -t ed25519 NEW_VPS_IP`
and compare its fingerprint to the independent console value before saving it as
`VPS_KNOWN_HOSTS`. Do not reuse the IONOS entry for a new host. Keep strict checking;
never resolve a mismatch by disabling it. The host identity, deployment SSH key and
TLS certificate are three distinct credentials.

Only the operator account transfers installation archives. For routine updates,
CI tests/scans an image once, pushes privately with its temporary GITHUB_TOKEN,
and manual delivery requests a digest-pinned pull/Compose switch through restricted
SSH. There is no server Git pull, application build or SCP delivery of each code change.

## 9. Verify before and after DNS cutover

Before changing Cloudflare records, verify the new host through the trusted operator
connection: restricted `check` succeeds, `id` fails, exact private image pulls,
loopback health works after owner-approved activation, and Compose publishes only
loopback 8080. Restore any retained release state only while no release is active,
with root-only ownership and reviewed digests. A state file does not start a container;
explicitly activate the approved current image on the new host and reconcile state
with what is actually running. Preserve both retained registry digests for rollback.

After review, change the proxied preview A record to the new IP. Keep the same
hostname and orange-cloud status. Remove/update obsolete AAAA records; add new IPv6
only after its routing, firewall and TLS path pass. Changing A/AAAA records does not
require replacing Cloudflare nameservers at DonDominio.

From an external Mac:

```sh
curl -sS -o /dev/null -D - https://preview.xn--eleccionesespaa2026-83b.es/
curl -sS -u preview -o /dev/null -D - https://preview.xn--eleccionesespaa2026-83b.es/
```

The first must return 401 and no-store/noindex. The second prompts privately and
must return 200 for an activated healthy candidate. In the original preparation,
502 was expected because the application was not running; it is **not** acceptable
migration completion. Verify exact image content hash and security headers through
the delivery workflow. Basic-auth success alone does not validate the artifact.

Verify direct origin 443/8080 are inaccessible from outside Cloudflare, including
IPv6 if used, and that legitimate proxied requests work. Keep staging cache bypass
explicit; no-store on an error response alone does not prove the full cache policy.
DNSSEC, Always Use HTTPS, transformations, the staging Cache Rule, logs/retention,
monitoring and alert receipt still need recorded account checks; do not treat them
as completed by the original setup conversation.

For a future already-public release, reproduce the approved public template,
publication classification, cache rule and scoped purge process under G4. Current
manual delivery supports authenticated private staging only; public pipeline work
remains pending. Do not expose fixture output through the apex during migration.

## 10. Cutover recovery and retirement

Do not decommission IONOS until the replacement is healthy, hosted-runner delivery,
external verification and rollback/restore have been rehearsed, and the owner
accepts resource and availability measurements. Record actual recovery duration;
the existing less-than-five-minute target is not demonstrated by this document.

If cutover fails, pause new releases and restore Cloudflare's prior A/AAAA records
and GitHub's verified old-host settings, provided the old origin still serves an
approved healthy digest. Recheck HTTPS and authentication externally. For public
content, perform its approved purge/verification too; never revert a factual
correction to known incorrect material. Console recovery remains available when
SSH fails. Revoke old credentials or retire the old host only after rollback is
no longer needed and its retained data has an approved backup.

Record a restricted migration report: old/new IPs and host fingerprints, tooling
commit, digests and CI runs, DNS change time, TLS expiries, firewall exports, SSH
proofs, unauthenticated/authenticated probes, resources, recovery timing and human
approval. Export account settings without exporting tokens or private keys.

## Maintenance after setup

Track certificate expiry (30/14/7-day reminders), GHCR PAT expiry, deployment and
operator key rotation, Ubuntu/OpenSSH/Docker updates, disk headroom, release image
retention and current Cloudflare ranges. Preserve operator access when their public
IP changes. Configure and test independent external monitoring and alert receipt;
the loopback monitor alone cannot detect DNS or Cloudflare TLS faults. Keep private
request logging disabled and approve retention of firewall/journal/error/edge logs.
A repeatable runbook supports restoration; a fresh-host rehearsal is still required.
