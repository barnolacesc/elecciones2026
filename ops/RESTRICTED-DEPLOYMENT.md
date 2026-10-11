# E3.3 restricted deployment setup

The site uses Docker Compose. The reused `deployer` account can request an image
switch through a root-owned wrapper; it cannot run arbitrary Docker commands.
This setup prepares access only. It does not publish the site, install a public
proxy, change the firewall, or approve any content. Production CI remains inactive
until the repository approval gate and runner connectivity are verified.

For the current SSH/UFW, TLS, Cloudflare and nginx verification record, and future
Hetzner migration, use the [server migration runbook](SERVER-MIGRATION.md).

## Initial host inventory (before proxy and firewall setup)

Owner-provided terminal output on 2026-10-11: Ubuntu 22.04.5 LTS, AMD64, one vCPU,
856 MiB visible RAM, no swap, about 3.6 GB free disk. After reboot, 418 MiB RAM
was available, Docker client/engine both reported 29.1.3, Compose reported 5.1.0,
and systemd had no failed units. SSH listens on port 22 for IPv4 and IPv6; DNS
and containerd listeners are loopback-only. No HTTP/TLS proxy was running.
The finance test service is disabled; there are no Docker containers. The owner
removed `deployer` from the Docker group. Subsequent owner output confirmed the
replacement sudo rule, key-only SSH, package updates, active UFW and TLS nginx;
these later checks are recorded in the migration runbook. Finance backup/restore
remains unverified. Preserve the unrelated PostgreSQL volume
`gestio-residus-backend_pg_data` until its owner approves disposal.

## Files and request contract

| File | Installed path / purpose |
|---|---|
| `restricted_release.py`, `release.py`, `compose.yaml` | Root-owned `/opt/elecciones2026/` |
| `elecciones-release` | `/usr/local/sbin/elecciones-release`: clears inherited settings before Python starts |
| `elecciones-ssh` | `/usr/local/libexec/elecciones-ssh`: passes one literal SSH request to sudo |
| `deployer.sudoers` | `/etc/sudoers.d/deployer`: permits only the release wrapper as root |
| `deployer-sshd.conf` | `/etc/ssh/sshd_config.d/00-elecciones-deployer.conf`: account-wide forced command and root-managed keys |

Allowed requests: `check`, `deploy ghcr.io/c2ventures/elecciones2026@sha256:`
followed by exactly 64 lowercase hexadecimal digits, and `rollback`. The wrapper
rejects other repositories, mutable tags, extra arguments, shell expressions,
unprotected/symlinked installation paths, and foreign retained image references.
State lives in `/var/lib/elecciones2026`; origin HTTP is fixed to loopback port
8080 and Compose project `elecciones2026-production`. A clean environment excludes
client-supplied Docker, Compose and Python settings. `check` does not contact
Docker or activate a container.

## 1. Prepare the files on your Mac

Use GitHub CLI authenticated to the private repository. Download the exact reviewed
commit from the PR, not a moving branch. Replace `REVIEWED_COMMIT` with its full SHA:

```sh
gh api repos/c2ventures/elecciones2026/tarball/REVIEWED_COMMIT \
  > /tmp/elecciones-deployment.tgz
scp /tmp/elecciones-deployment.tgz root@195.20.230.75:/root/
```

Generate the dedicated key as described in the design, if not already generated.
Send only its public half to the VPS:

```sh
scp ~/.ssh/elecciones2026_deploy.pub root@195.20.230.75:/root/
```

The full private key belongs in the GitHub `production` environment secret
`VPS_SSH_KEY`. Use `VPS_USER=deployer`, `VPS_HOST=195.20.230.75`, and independently
verified `VPS_KNOWN_HOSTS` secrets. Set variable `VPS_SSH_PORT=22`.

## 2. Install root-owned tooling on the VPS

Run these commands in the existing root session. Keep that session and IONOS
console access available. Use a fresh extraction directory. Stop if any command
fails or a destination is a symlink or an unexpected existing installation.

```sh
mkdir /root/elecciones-deployment-setup
tar -xzf /root/elecciones-deployment.tgz \
  --strip-components=1 -C /root/elecciones-deployment-setup
cd /root/elecciones-deployment-setup

install -d -o root -g root -m 755 /opt/elecciones2026 /usr/local/libexec
install -d -o root -g root -m 700 /var/lib/elecciones2026
install -o root -g root -m 644 ops/restricted_release.py ops/release.py \
  ops/compose.yaml /opt/elecciones2026/
install -o root -g root -m 755 ops/elecciones-release /usr/local/sbin/elecciones-release
install -o root -g root -m 755 ops/elecciones-ssh /usr/local/libexec/elecciones-ssh

visudo -cf ops/deployer.sudoers
```

Only after the sudoers syntax check succeeds, back up the old sudo file (if it
still exists), then replace the obsolete finance permission:

```sh
if test -f /etc/sudoers.d/deployer; then
  cp -a /etc/sudoers.d/deployer /root/deployer.sudoers.before-elections
fi
install -o root -g root -m 440 ops/deployer.sudoers /etc/sudoers.d/deployer
visudo -c
sudo -l -U deployer
/usr/local/sbin/elecciones-release check
```

The sudo listing must show only the release wrapper. The last command must print
`Restricted release access ready; no deployment performed.` Do not grant Docker
group membership or unrestricted sudo.

## 3. Install the key and account-wide SSH restriction

Confirm the uploaded file is the one-line, plain public key you generated:

```sh
ssh-keygen -lf /root/elecciones2026_deploy.pub
install -d -o root -g root -m 755 /etc/ssh/authorized_keys
install -o root -g root -m 644 /root/elecciones2026_deploy.pub \
  /etc/ssh/authorized_keys/deployer
install -o root -g root -m 644 ops/deployer-sshd.conf \
  /etc/ssh/sshd_config.d/00-elecciones-deployer.conf
/usr/sbin/sshd -t
/usr/sbin/sshd -T -C user=deployer,host=localhost,addr=127.0.0.1 \
  | grep -E '^(forcecommand|authorizedkeysfile|disableforwarding|permittty|permituserrc|passwordauthentication|kbdinteractiveauthentication) '
```

Do not reload SSH unless syntax is valid and the effective settings show the
expected wrapper, `/etc/ssh/authorized_keys/deployer`, forwarding/TTY/user-rc
disabled, and password/interactive authentication disabled. The existing account
must have an executable shell for SSH to run the wrapper. Existing unrestricted
keys in its home will no longer authorize new SSH logins; other operator accounts
are unaffected. Review any other configured SSH authentication routes during
preflight. Account restrictions do not revoke existing sessions: end old
`deployer` sessions before activating release access.

When the checks pass:

```sh
systemctl reload ssh
```

## 4. Verify from your Mac without deploying

Use the separately verified host-key file:

```sh
ssh -T -i ~/.ssh/elecciones2026_deploy \
  -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile=~/.ssh/elecciones2026_known_hosts \
  deployer@195.20.230.75 check
```

Expect the ready message. Repeat with `id` instead of `check`; expect rejection
with a nonzero exit status. The key cannot request a shell, SCP/SFTP, PTY or
forwarding. Root can still administer the machine. Do not test `deploy` or
`rollback` against private/unapproved content on a public route.

If these checks fail, use the retained root session to inspect permissions and
`journalctl -u ssh`. Remove the new SSH drop-in, validate `sshd -t`, then reload
to recover prior SSH settings if needed. Restore the backed-up sudo file only
after `visudo` validation. Do not troubleshoot by granting unrestricted sudo,
disabling host-key verification or restoring the Docker group.

## Remaining activation gates

Provision root-only GHCR pull authentication, verified GitHub-hosted runner access through key-only public SSH,
production approval rules and branch restrictions, authenticated staging, domain
and TLS configuration, external monitoring and publication evidence before any
live delivery. A later read-only API check confirmed the owner configured
main-only environment branch rules. Required reviewers are unavailable on this
private repository plan; the owner chose manual dispatch with explicit operator
approval. Automatic application activation remains disabled.

The account's ability to request a release does not establish that a digest is
editorially approved. Use the protected pipeline and retained approval evidence;
repair known incorrect content through a new approved artifact rather than
rolling back to an incorrect version.

See [OpenSSH forced commands](https://man.openbsd.org/sshd.8) and
[Ubuntu sudo policy](https://manpages.ubuntu.com/manpages/jammy/man5/sudoers.5.html).

## Delivery follow-up

The owner installed the restriction and retained the existing 1Password deploy key
by explicit choice. Live `check` succeeded and arbitrary `id` was denied. Next use
[IONOS delivery setup](IONOS-DELIVERY.md) for root-only private registry login,
DonDominio-to-Cloudflare delegation, TLS, authenticated staging and the manual
workflow. Public delivery remains behind G2/G4 and live evidence.
