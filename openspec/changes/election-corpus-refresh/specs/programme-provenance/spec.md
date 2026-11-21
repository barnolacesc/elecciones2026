# Spec Delta

## Purpose

Preserve election-specific programme provenance while new source versions and
reviewed statements enter the comparator incrementally.

## ADDED Requirements

### Requirement: Separate production records
Production builds SHALL load only the selected election's production records.
They MUST NOT fall back to fictional examples or historical statements.

#### Scenario: Empty approved corpus
- **WHEN** no approved production statements exist
- **THEN** the comparator shows pending coverage without fictional proposals

### Requirement: Verify real political records
Every production statement MUST resolve to one verified election-scoped source
and a matching programme hash/version. Applicable reuse approval, publication
dates and exact locators MUST pass the existing gates. A 2026 programme
summary without a verbatim quotation requires one named human approval bound
to the approved content and provenance. Automated checks may support that
review. Verbatim quotations and comparison relationships require two human
approvals.

#### Scenario: Unverified source
- **WHEN** a production claim references a source without reuse approval
- **THEN** the build fails before replacing the prior output

#### Scenario: Cross-election record
- **WHEN** a production record belongs to a different election
- **THEN** the build rejects the record

### Requirement: Retain private intake boundaries
Originals and complete extracted text MUST remain outside Git and public
artifacts. Extraction MUST preserve physical page anchors and MUST NOT grant
editorial review or imply complete topic coverage.

#### Scenario: Unsafe or oversized input
- **WHEN** a document violates the existing processor limits
- **THEN** intake records the blocker without weakening those limits

### Requirement: Bound private processing exceptions
A private processing exception MUST bind to one exact document hash and a
recorded coordinator technical review. Shared safety checks MUST remain
unchanged. The route MUST retain isolated parsing, resource/output limits and
verification artifacts, and MUST NOT grant publication or human review.

#### Scenario: Changed document bytes
- **WHEN** bytes differ from an exception's recorded hash
- **THEN** the exception route rejects the input before parsing

### Requirement: Validate election-specific taxonomy membership
Production records MAY select a stable, versioned election-specific taxonomy.
The generator MUST reject draft versions, election mismatches and unknown topic
or subtopic membership. An extension MUST retain all core topic IDs. Supporting
an extension MUST NOT grant editorial approval or publish private draft mappings.

#### Scenario: Extended taxonomy without content approval
- **WHEN** an extension contains a valid additional topic but its statements lack human approval
- **THEN** the build still rejects those statements

#### Scenario: Cross-topic subtopic
- **WHEN** a statement references a subtopic outside its selected topic
- **THEN** validation rejects the record
