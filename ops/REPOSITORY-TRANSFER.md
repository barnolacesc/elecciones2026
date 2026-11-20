# E3.3 personal repository transfer

Status: preparation only. The repository is still private at
`c2ventures/elecciones2026`. The planned destination is
`barnolacesc/elecciones2026`. Keep IONOS, Cloudflare, the domain, staging
authentication and manual release approval. This procedure does not authorize
a public release or a home-cluster deployment.

## Before transfer

1. Review and merge the transition PR through the normal merge gate. Run its
   required CI checks. It supports both exact repository locations; fork and
   non-main events cannot publish candidates. Image publication uses the active
   repository's namespace, so it continues using C2 Ventures before transfer.
2. Record the current and previous approved image digests from the protected
   release state. Keep those images and legacy pull access available. Do not
   delete packages or replace retained release state.
3. Have the operator install this PR's reviewed `ops/restricted_release.py`
   under root-owned `/opt/elecciones2026/`, following
   [restricted tooling installation](RESTRICTED-DEPLOYMENT.md). Verify file
   ownership/permissions and the restricted `check` request. This is required:
   changing the repository does not update the installed host wrapper. The new
   wrapper allows both exact GHCR namespaces, including mixed current/previous
   rollback state, without accepting arbitrary repositories or mutable tags.
4. Confirm the destination account has no conflicting `elecciones2026`
   repository or fork. Verify its Actions allowance and support for the existing
   private-repository branch/environment protections. If equivalent protections
   are unavailable, keep delivery disabled until an enforceable gate is agreed.
5. Inventory secret **names**, variables, environments, branch rules, Actions
   permissions, GitHub App installations and scheduled integrations. Check which
   credentials come from organization secrets; those need an explicit replacement
   after the transfer. Do not export secret values into Git, logs or a PR.
6. Set `DEPLOYMENT_READY=false` to block manual delivery while the account,
   registry and access checks below are incomplete. Repository transfer does not
   require stopping the running site.

## Transfer and restore CI publication

1. An administrator transfers the existing repository in GitHub Settings →
   General → Danger Zone → Transfer ownership, with new owner `barnolacesc`.
   Keep the name and private visibility. Accept any confirmation GitHub requests.
   This operation preserves Git history; do not copy to a fresh repository or
   rewrite commit authors. Do not recreate the old path, which removes redirects.
2. Update every working clone, worktree tool and scheduled task that stores the
   old remote. In the shared clone, the intended remote is:

   ```sh
   git remote set-url origin git@github.com:barnolacesc/elecciones2026.git
   ```

3. Verify Actions is enabled and inspect repository/environment secrets,
   `DEPLOYMENT_READY`, `VPS_SSH_PORT`, main-only protections, operator approval
   and connected apps. Preserve `DEPLOYMENT_READY=false` until the new path is
   ready. Reprovision missing organization-supplied credentials through their
   protected settings. Do not assume an organization policy transfers.
4. Produce a fresh successful **main push** CI run at the new location using a
   reviewed follow-up commit. Rerunning an old run can retain the old workflow or
   provenance and is not evidence for new-owner publication. Verify required
   validation, mobile, Docker and vulnerability checks, then the private image at
   `ghcr.io/barnolacesc/elecciones2026` and its `release-candidate` record.
   Keep its commit, run/attempt, digest, election mode and home hash together.
5. Check the new GHCR package remains private, is linked to the transferred
   repository and grants its Actions workflow write access. The pipeline uses
   the personal-account package API after transfer. Existing organization
   packages are separate resources; do not assume they moved with the repository.

## Verify IONOS delivery and recovery

1. Provision least-privilege private-package read access for the operator-managed
   root Docker login. Follow [registry setup](IONOS-DELIVERY.md#2-registry-access-separate-publish-and-pull-identities).
   Verify the host can pull the exact new approved digest and retained legacy
   rollback images. Do not reuse the workflow's short-lived token as a host login.
2. Confirm the reviewed wrapper is installed and its restricted `check` succeeds.
   Review readiness prerequisites, restore `DEPLOYMENT_READY=true` only when
   satisfied, then manually dispatch delivery for the new main CI run with an
   explicit approval record. The downloader and evidence checks use the active
   repository; old-namespace candidates are rejected for new-owner delivery.
3. Confirm unauthenticated staging returns 401, authenticated HTTPS has the exact
   candidate home hash and required security/no-store headers, and the operator
   can recover the prior approved digest under the existing recovery policy.
   Retain IONOS state, legacy images and their read access through this check.
4. Record live evidence in the OpenSpec task record. Remove the legacy repository
   and image allowlists in a separate cleanup after rollback retention no longer
   needs them. Preserve dated audit links and original source/copyright attribution.

## Visibility and references

The footer links to the developer's GitHub profile, and the README identifies
the maintainer. That credit is separate from editorial review, programme authorship
and copyright ownership. Moving the private repository does not make it public.
Any change of repository visibility requires its own source and release review.

GitHub documents [repository transfer behavior](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository)
and [package permissions](https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages).
