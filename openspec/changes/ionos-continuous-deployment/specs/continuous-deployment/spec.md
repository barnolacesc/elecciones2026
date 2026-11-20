# Continuous deployment

## Purpose

Deliver reviewed static releases to the owner-managed VPS with immutable artifacts, protected authorization, verified HTTPS, and recoverable failures.

## ADDED Requirements

### Requirement: Trusted release authorization
The pipeline SHALL deploy only a tested revision from the canonical repository's main branch after all required CI checks and human release approval. Pull requests SHALL receive no deployment credentials or registry write permission.

#### Scenario: Untrusted contribution
- **WHEN** a pull request runs validation, including a fork pull request
- **THEN** it cannot publish a release image or access deployment secrets.

#### Scenario: Check or approval missing
- **WHEN** any required CI job fails or the production approval is absent
- **THEN** the deployed site remains unchanged.

#### Scenario: Personal repository transition
- **WHEN** the repository is at `c2ventures/elecciones2026` or `barnolacesc/elecciones2026`
- **THEN** trusted main CI publishes private candidates in the active owner's GHCR namespace and delivery accepts only matching CI provenance and image digests.
- **AND** a fork, another repository, or a candidate from the other namespace is rejected.

#### Scenario: Retained image after transfer
- **WHEN** an operator requests rollback to a retained approved legacy image
- **THEN** the reviewed VPS wrapper permits the two exact transition namespaces while continuing to reject mutable tags, foreign repositories and malformed requests.

### Requirement: Immutable verified artifact
The delivery system SHALL deploy the exact scanned and tested image by digest, retain its revision and approval evidence, and serialize releases. It SHALL NOT build application artifacts on the VPS.

#### Scenario: Successful release candidate
- **WHEN** a candidate passes the required checks and image scan
- **THEN** the published digest identifies the same image tested by serving and rollback checks.

#### Scenario: Competing releases
- **WHEN** two production releases are requested
- **THEN** only one can switch the running image at a time and an active switch is not canceled by the newer request.

### Requirement: Restricted deployment access
Deployment credentials SHALL authorize only the site release operation. Host authentication SHALL use a separately verified host key. Missing credentials or failed host authentication SHALL stop deployment before mutation.

#### Scenario: Host key mismatch
- **WHEN** the SSH endpoint presents a different host key
- **THEN** the pipeline refuses the connection and reports a failed deployment.

#### Scenario: Unauthorized command
- **WHEN** the deployment identity requests arbitrary commands, forwarding, or a different image repository
- **THEN** the server denies the request.

### Requirement: Owner-controlled host preparation
Activation SHALL require owner-confirmed retirement of the finance service and recoverable backups of any retained data. The static service SHALL use a non-privileged, resource-limited, read-only container behind HTTPS with no public container port.

#### Scenario: Retirement incomplete
- **WHEN** retained finance data has no verified backup or the old service still occupies the selected port
- **THEN** activation stops without deleting data or changing unrelated host services.

### Requirement: Editorial publication boundary
Public deployment SHALL require source traceability, rights and human editorial approval, and applicable launch gates. Private pilot and fictional fixture artifacts SHALL remain private and accessible only through authenticated staging.

#### Scenario: Missing or conflicting source evidence
- **WHEN** a release contains missing citations, conflicting source versions, or unreviewed substantive claims
- **THEN** publication fails without replacing the approved site.

#### Scenario: Private rehearsal content
- **WHEN** a validated artifact is still a private pilot or fixture build
- **THEN** it cannot be deployed to the unauthenticated public hostname.

### Requirement: Failure recovery
The system SHALL retain the preceding approved image and restore it after a failed origin health check. External HTTPS or cache verification failure SHALL report deployment failure and provide a protected recovery route. Known incorrect political content SHALL be repaired through a new approved release.

#### Scenario: Unhealthy candidate
- **WHEN** a new container fails readiness or loopback checks
- **THEN** the prior healthy image is restored and the release fails; a failed first release removes its candidate container.

#### Scenario: Edge failure
- **WHEN** the origin is healthy but the external TLS or content check fails
- **THEN** the release is reported as failed and operators can restore the previous approved digest and verify cache recovery.

### Requirement: Measured small-host operation
The release record SHALL contain measured CPU, memory, latency, errors, cache behavior, bandwidth, and recovery on the intended 1-vCPU/1-GB host. Local or larger-host results SHALL NOT establish production capacity.

#### Scenario: Capacity target fails
- **WHEN** the actual host or traffic generator fails an approved workload target
- **THEN** public launch remains blocked until owners approve and verify a capacity response.

### Requirement: Canonical domain consistency
Published canonical URLs, sitemap entries, and social metadata SHALL use the approved HTTPS domain consistently, including its ASCII-compatible DNS representation.

#### Scenario: Domain migration
- **WHEN** a release uses `eleccionesespaña2026.es`
- **THEN** TLS, proxy routing, canonical metadata, and crawler routes resolve consistently with `xn--eleccionesespaa2026-83b.es` and contain no obsolete canonical domain.
