# Proposal: IONOS continuous deployment

## Why

CI already validates the site and rehearses releases, but its production gate does not deploy an artifact. The owner wants to repurpose an existing Ubuntu IONOS VPS with 1 vCPU and 1 GB RAM; the finance development service will no longer run there.

## What Changes

- Extend package E3.3 with a reviewed GitHub Actions delivery path: test, scan, publish a private immutable Docker image, obtain production approval, and deploy the exact tested digest over restricted SSH.
- Adapt origin operations for the smaller IONOS host and Cloudflare domain `eleccionesespaña2026.es`, with an owner-controlled finance-service retirement and measured resource limits.
- Define credentials, runner connectivity, release evidence, health checks, rollback, and owner setup. Keep private pilot content behind authenticated staging until public-release gates pass.

## Capabilities

### New Capabilities

- `continuous-deployment`: Deliver approved immutable static images to a VPS with isolated credentials, explicit publication authorization, health verification, and recovery.

### Modified Capabilities

None. Main specs are not yet populated. This capability complements the in-flight MVP `static-publication` specification; it does not replace its editorial or release requirements.

## Impact

Bounded package: **E3.3**, dependent on E3.2 and E0.3. This PR contains planning artifacts only. Subsequent implementation will affect `.github/workflows/ci.yml`, `ops/`, release tests, and the hosting references in both roadmaps, ADR-0001, architecture/security documentation, and OpenSpec context. Reconcile those Hetzner references before activation; this proposal records IONOS as the requested replacement, not a completed infrastructure migration.

The MVP remains a Spanish static site without accounts, analytics, visitor storage, or public APIs. No automatic political review, source ingestion, finance-service removal, DNS change, or deployment is included in this planning PR. The new domain also replaces the canonical domain in ADR-0001; revise generated canonical, sitemap, and social-preview configuration before activation.

Risks: a green build does not establish editorial publication approval; service retirement can lose finance data; the 1-GB host can exhaust resources; private registry contents and logs can disclose pilot material; infrastructure changes can block accessible HTTPS access. Mitigate through protected release approval, verified owner backups, a restricted root-owned deployment controller, private artifacts and staging, and external/accessibility checks. Live capacity and rollback evidence remain required.
