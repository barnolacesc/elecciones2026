# Budget data bundle

## Purpose

Provide reproducible, audited budget snapshots for static publication and evaluate optional offline delivery without affecting the core comparison flow.

## ADDED Requirements

### Requirement: Versioned audit bundle
A bundle SHALL contain schema and dataset versions, source hashes, normalized official values, measurement contract, topic mapping and taxonomy hash, Spanish notes, review references, corrections, and an integrity manifest with file sizes and SHA-256 hashes. Official values SHALL use exact decimal representations. It SHALL contain no personal answers, secrets, or unreviewed raw sources.

#### Scenario: Bundle inspection
- **WHEN** a reviewer selects a displayed figure from a bundle
- **THEN** its record resolves to the exact source version, locator, transformation version, denominator, and review evidence.

### Requirement: Deterministic offline generation
The same pinned inputs, tool version, configuration, and explicit build date SHALL produce identical bundle bytes without network access. Import SHALL enforce size and resource limits and reject schema drift, duplicate keys, invalid numeric syntax, unsafe paths, or altered hashes. Public serving SHALL perform no ingestion or external data fetch.

#### Scenario: Repeat generation
- **WHEN** the documented reproduction command runs twice with networking disabled
- **THEN** both manifests and all normalized outputs have identical hashes.

#### Scenario: Invalid input
- **WHEN** a source exceeds its limits, changes schema, or fails its checksum
- **THEN** generation stops before publishing output and records a diagnostic without executing source content.

### Requirement: Atomic versions and correction history
The public build SHALL bind HTML and context data to one approved bundle version. Corrections SHALL create a new immutable version, invalidate affected mappings and reviews, and retain the correction trail. Failed validation SHALL preserve the previous release. Rollback SHALL restore matching HTML and bundle versions together.

#### Scenario: Mixed versions
- **WHEN** a page references a mapping or measurement contract from another bundle
- **THEN** publication fails rather than serving inconsistent context.

#### Scenario: Correction rollback
- **WHEN** a release smoke check fails
- **THEN** the prior verified artifact can be restored with its matching bundle; a withdrawn unsafe version cannot be selected as an approved rollback.

### Requirement: Offline-distribution decision
Before adding public offline distribution, the team SHALL record a go/no-go evaluation of rights, bundle size, standalone usability, integrity, freshness, accessibility, security, bandwidth, and primary-site performance. A download SHALL be explicit, version-labelled, and separate from the initial comparison payload. No bulk prefetch or whole-site service worker SHALL be introduced by this change.

#### Scenario: Offline delivery rejected
- **WHEN** review or performance evidence does not support a public bundle
- **THEN** a no-go decision is recorded and the reviewed online static view remains independently deliverable.

#### Scenario: Offline candidate opened
- **WHEN** a reviewed candidate is opened without a network connection
- **THEN** figures, notes, and source/version details are readable, official outbound links are identified as requiring connectivity, and the snapshot does not claim to be current.

### Requirement: Primary-site performance protection
Core pages SHALL request no full budget bundle or download archive during initial navigation. Evaluation SHALL compare baseline and candidate transferred bytes, request count, mobile delivery, cache ratio, p95 latency, errors, origin load, and bandwidth cost. Release SHALL require agreed service targets and a scoped workload on the 2-vCPU/8-GB target; local rehearsal SHALL NOT count as live capacity proof.

#### Scenario: Core navigation
- **WHEN** a reader opens home or comparison without requesting a download
- **THEN** the network trace contains no bulk budget fetch or background prefetch; any context data is limited to the selected topic.

#### Scenario: Download burst
- **WHEN** the candidate workload includes explicit offline downloads
- **THEN** their cache, origin, and cost impact is reported separately and distribution is rejected if approved primary-site targets fail.
