# Budget topic mapping

## Purpose

Connect reviewed official budget rows to the existing comparison taxonomy while preserving classification limits and visible gaps.

## ADDED Requirements

### Requirement: Eight-topic coverage contract
The mapping SHALL pin the approved taxonomy version and contain coverage records for all eight core topic IDs. Each record SHALL identify reviewed source rows or an explicit gap, with a Spanish scope note. A taxonomy change SHALL require mapping review before publication.

#### Scenario: Taxonomy coverage
- **WHEN** a mapping is validated against `content/taxonomy.json`
- **THEN** housing, education, health-social-services, economy-work-tax, immigration, foreign-policy-eu, climate-energy, and institutions-rights each have a coverage record.

#### Scenario: Taxonomy changes
- **WHEN** the selected taxonomy hash differs from the pinned mapping input
- **THEN** the build rejects that mapping until it is versioned and reviewed again.

### Requirement: Traceable mapping decisions
Each mapping SHALL reference a dataset version, official policy code, optional section or validated programme code, source locator, rationale, coverage state, and human review. Labels alone SHALL NOT be join keys. A relevant broad policy SHALL retain its official label and SHALL NOT be renamed as an exact topic allocation.

#### Scenario: Mixed industry and energy policy
- **WHEN** a broad policy is relevant to climate-energy and economy-work-tax
- **THEN** each topic can link to the same official row with a partial-coverage note, without assigning any inferred fraction to either topic.

### Requirement: No imputed topic totals
The system SHALL NOT split official rows using estimated weights, party claims, demographic proxies, or residual allocation. Exact sums SHALL use distinct, disjoint reviewed official rows on the same measurement basis. Related broad rows SHALL remain separate context; repeated references across topics SHALL NOT form an additive eight-topic total.

#### Scenario: Immigration is not isolated
- **WHEN** only a mixed inclusion, social-security, and migration row is available
- **THEN** the topic shows the broad official row as related context or a gap and never displays that amount as immigration spending.

#### Scenario: Overlapping references
- **WHEN** two mappings reference the same policy or a policy and one of its cells
- **THEN** aggregation rejects overlapping inputs rather than counting them twice.

### Requirement: Gaps do not become zero
Coverage SHALL distinguish `mapped`, `partial`, `not_available`, and `not_comparable`. Missing or ambiguous amounts SHALL have no numeric topic value. Only an explicit, reviewed source zero SHALL display as zero; missing context SHALL NOT imply absent spending or a party position.

#### Scenario: No separable climate figure
- **WHEN** no reviewed official row isolates the requested climate measure
- **THEN** the view explains the scope gap in Spanish and displays no estimated figure or zero for that measure.
