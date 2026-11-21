# E3.3 origin and edge operations

Status: the owner has configured IONOS SSH/UFW, Cloudflare delegation, origin TLS
and authenticated preview nginx. Private staging delivery and external exact-content
verification passed in run 38182379207. Start
with the [server setup and migration runbook](SERVER-MIGRATION.md) for the current
verification record and repeatable Hetzner migration steps. Use
[IONOS delivery setup](IONOS-DELIVERY.md) for workflow and registry details.
OpenSpec tasks 4.4 and 4.6 remain open until their full live evidence exists.

The pending move to the owner's personal GitHub account keeps this IONOS setup.
Use the [repository transfer runbook](REPOSITORY-TRANSFER.md) before transferring.

## Release prerequisites

Cesc and the project partner must record G0 approval. The dated setup record
confirms active IONOS private staging, Cloudflare delegation and successful
manual delivery; remaining account and origin checks still need evidence.
G2/G3/G4 must approve content, accessibility/security,
image scan, and public launch. The repository's 2023 pilot is private rehearsal
content; it is not approved public 2026 content. Keep it behind authenticated
staging. Never apply the public cache rule to staging.

Use the owner-selected patched 1-vCPU/1-GB Ubuntu IONOS VM with Docker Compose v2, Python 3, curl, and
host nginx. Use key-only SSH, disable password authentication after verifying a second
operator session, and retain IONOS console recovery. Docker access is equivalent
to root; only the infrastructure owner runs release commands. No remote deploy
job or credentials are added to PR CI.

The earlier 2-vCPU/8-GB sizing is a planning reference. A later Hetzner migration
is an option, not the active host. Neither establishes capacity on IONOS.
The setup instructions below also apply to replacement hosts; the dated record
states what is already verified.

## Origin firewall and TLS

1. Apply the reviewed IONOS firewall BEFORE starting public listeners. Allow inbound
   TCP 22 through the owner-approved key-only, rate-limited public SSH policy,
   with an IP-specific operator allow rule; TCP 443 only from the current
   official Cloudflare IPv4 AND IPv6 ranges. Do not open 80 or 8080. Preserve
   outbound DNS, HTTPS, time sync, registry, and update access. Retrieve and review
   the ranges from https://www.cloudflare.com/ips-v4 and
   https://www.cloudflare.com/ips-v6; update after vendor changes. Record the
   effective rules and both address-family probes. Keep console access while
   changing SSH/firewall rules. Do not rely on UFW to filter Docker published ports.
2. The production Compose file binds port 8080 to `127.0.0.1` only. Install
   `staging-origin.conf` for the active private preview. Use `origin.conf` only
   after G4 public approval. Verify the approved ASCII hostname, and
   remove default host sites/listeners. Host nginx listens on 443 for IPv4/IPv6.
3. Create an origin server certificate for the approved hostname (Cloudflare
   Origin CA or a public CA). Store cert/key at `/etc/elecciones2026/tls/origin.pem`
   and `origin.key` outside Git, with the key readable only by root. Install the
   official Origin Pull CA as `origin-pull-ca.pem`. Server certificate and client
   trust CA have different purposes. Set Cloudflare SSL/TLS to **Full (strict)**.
4. Enable Authenticated Origin Pulls in the zone before enforcing client validation.
   The template requires mTLS. Validate with `nginx -t`, then reload. Global AOP
   authenticates the Cloudflare network, not a single account; use a zone-specific
   certificate if exclusive zone authentication is required. Default/unknown
   hosts close the connection. Never treat the Cloudflare CIDR allowlist alone as
   exclusive account authentication.
5. Keep host access logs disabled. Production Compose disables retained container
   logs because the preview image emits request URLs; inspect container health
   instead. Rotate host nginx error logs daily, keep at most 14 days,
   and restrict access. Set journal retention to <=14 days as well. Cloudflare
   log retention/data processing still requires the privacy owner's account review.
   Enable unattended security updates and certificate expiry alerts (30/14/7 days).
   HSTS stays commented until TLS and all covered domains are verified. Approve
   `includeSubDomains`/preload separately after checking every subdomain.

## Cloudflare configuration

The preview zone delegation and proxied A record are active. Public apex routing
is a later G4 action: use proxied A and (only if IPv6 works) AAAA records
for the apex. Enable DNSSEC after delegation. Configure edge redirects for HTTP,
www, and acquired defensive domains to the HTTPS apex, preserving path/query.
Do not point an unauthenticated preview hostname at private pilot content.

Create one Cache Rule matching only the public apex and GET/HEAD:

```text
(http.host eq "APPROVED_APEX" and http.request.method in {"GET" "HEAD"})
```

Set cache eligibility to **Eligible for cache**, Edge TTL to **Use cache-control
header if present**, Browser TTL to **Respect existing headers**. Keep the default
query-string cache key; do not drop comparison parameters. Do not override origin
no-store/private directives. Do not cache staging, authentication, or future API
paths; narrow this expression when the product gains such routes.

The host proxy replaces the existing image's overly long mutable asset TTL:
mutable HTML/CSS/JS/JSON use 300 seconds; files with a >=12-hex fingerprint before
the extension use 31536000 seconds and immutable; crawler files use 3600 seconds.
The existing artifact has mutable `app.js` and `styles.css`; those must revalidate.
Origin CSP, nosniff, frame, referrer, and permissions headers pass through the proxy.

Vendor review (2026-10-10): Free has 10 Cache Rules, one rate limiting rule, and
Authenticated Origin Pulls. Origin Cache Control is enabled by default. Recheck
these capabilities before activation. Do not assume paid analytics/alerts or
advanced rate matching. Start with no blanket challenge. If measured abuse
justifies the one rate rule, approve a narrow path/threshold, test shared-IP readers,
crawlers and keyboard access, and record false positives before enabling it.

## Immutable release and rollback

Build and scan the reviewed artifact in CI. Push it to an approved registry and
record its full `repository@sha256:...` reference, Git revision, scan, content
signoffs, build date, and release owner. Keep the preceding image available both
locally and in the registry. Do not prune retained releases. The production file
uses the same serving image as local preview; no build runs on the VM.

Routine private delivery uses owner manual dispatch and restricted SSH; see
[the delivery guide](IONOS-DELIVERY.md#4-github-settings-and-manual-approval).
The following controller commands are for the infrastructure owner only, from the
root-owned reviewed tooling installation after the applicable gate. They are not
commands granted to the restricted deployer:

```sh
sudo python3 /opt/elecciones2026/release.py --image APPROVED_REPOSITORY@sha256:APPROVED_DIGEST
sudo python3 /opt/elecciones2026/release.py --rollback
```

The controller serializes switches, pulls before replacing the current container
(rollback uses the retained local image and pulls only if it is absent),
waits for health, checks loopback HTTP, and atomically records current/previous
images in `/var/lib/elecciones2026/release.json`. Failed switches restore the
current image; a failed first release removes its container. If recovery also
fails, it exits unsuccessfully; use console recovery. A switch can interrupt
requests briefly; this is not a zero-downtime deployment.

Repeating a deployment of the current digest verifies container and loopback health
without pulling or changing the current/previous release record. An unhealthy retry
still fails. Install the reviewed controller update as root before relying on this
behavior; routine image delivery does not replace host tooling.

After EVERY switch or rollback, verify the edge. Private staging uses no-store
and cache bypass. For a public release, purge mutable page/asset URLs
(including query variants), or use a reviewed zone purge when enumeration is
incomplete. Purge requires the operator's scoped token outside Git. Browser
copies can remain stale for the existing five-minute TTL. Measure end-to-end
recovery, including edge purge, against RTO <5 min; local origin timing alone
cannot establish production RTO. Never roll back a factual correction to known
incorrect content: make a new reviewed corrected release instead.

If the host is lost, provision the same firewall/TLS/Compose setup, pull the
retained approved digest, and restore the release record from the restricted
operations backup. Recreate certificate material from the approved secret store.
After a process/host crash during a switch, inspect the actual running digest and
health before reconciling the state record; the state file is not a crash journal.

## Monitoring and release evidence

Install `monitor.service` and `monitor.timer` as
`/etc/systemd/system/elecciones2026-monitor.{service,timer}`. Supply the owner-managed
`elecciones2026-alert.service` before enabling the timer; it must notify the
approved on-call route without visitor URLs/IPs. Enable with
`systemctl enable --now elecciones2026-monitor.timer`. Test an induced failure
and alert receipt. A loopback check detects origin faults, not DNS/TLS/edge faults.
Use an independent external probe of public HTTPS every minute, plus weekly
source-page smoke checks. Record uptime, p95, 5xx, container memory/CPU, certificate
expiry, disk, cache-hit ratio, and cost; alert on ADR-0001 budget exhaustion and
€25/€40 spend. Select and approve the probe/alert service before launch.

For each live release retain a restricted dated evidence record:

- Approved domain, firewall exports, DNS/proxy/DNSSEC, Full (strict), AOP, image
  digest and scan; edge GET/HEAD headers for home/topic/method/CSS/JS and a missing
  URL. Verify CSP/nosniff/frame/referrer/permissions plus valid TLS. Test an
  unrelated Host header and requests without the client certificate.
- From outside Cloudflare, direct origin IPv4/IPv6 probes to 443 and 8080 must fail.
  Confirm legitimate Cloudflare requests succeed. Use `curl --resolve` with the
  public hostname to avoid a misleading host-name-only rejection.
- Fetch identical public URLs twice without cache-busting; retain CF-Cache-Status,
  Age, status and Cache-Control; verify eventual HIT and expiry/revalidation.
  Measure aggregate ratios separately in E3.4; a pair of HITs is not a load test.
- Switch A -> B -> A, verify actual content markers at origin and edge, purge,
  restore on a fresh host, and time recovery. Induce an unhealthy release and
  verify the preceding artifact and alert route. Keep tasks 4.4/4.6 open until
  this live evidence is reviewed.

## Local verification

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -p test_operations.py -v
docker build -t elecciones2026:ci .
python3 ops/smoke.py --base-image elecciones2026:ci
```

The rehearsal creates a disposable local registry and A/B/unhealthy fixture images,
uses production Compose with a unique rehearsal project name and release switching, checks content restoration, times
rollback, and validates the host nginx TLS configuration with disposable test
certificates. It requires Linux Docker, openssl, and registry:2 network access; it selects
a free loopback port so other previews are untouched. Docker Desktop may not
route daemon requests to the disposable registry; use the Linux CI rehearsal. It removes its containers/images. It does not establish live
origin protection, TLS trust, Cloudflare behavior, monitoring delivery, or load.

References: [Hetzner firewall behavior](https://docs.hetzner.com/cloud/firewalls/faq/),
[Cloudflare IPs](https://developers.cloudflare.com/fundamentals/concepts/cloudflare-ip-addresses/),
[AOP](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/),
[Cache Rules limits](https://developers.cloudflare.com/cache/how-to/cache-rules/),
[origin cache control](https://developers.cloudflare.com/cache/concepts/cache-control/),
[WAF availability](https://developers.cloudflare.com/waf/).
