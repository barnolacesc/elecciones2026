# Coalition arithmetic

## Purpose

Calculate selected hypothetical seat sums against sourced Congress thresholds while preserving the distinction between seats, parliamentary votes, and political agreements.

## ADDED Requirements

### Requirement: Selected sum and absolute threshold
For valid seat entries whose total does not exceed 350, the simulator SHALL sum each selected group once. It SHALL show the sum, the 176-seat absolute-majority threshold, seats needed below it, and seats above it. An empty selection SHALL show no selected coalition rather than a successful result.

#### Scenario: Threshold boundary
- **WHEN** selected seats total 175, 176, or 177
- **THEN** the result respectively shows one seat needed, the threshold reached with zero surplus, or the threshold exceeded by one seat.

#### Scenario: Duplicate selection
- **WHEN** a selection action repeats for the same stable group ID
- **THEN** that group's seats are counted once; group identity and arithmetic do not depend on its label or position.

### Requirement: Rule-specific interpretation
The result SHALL describe an arithmetic absolute majority of a 350-seat Congress. It SHALL not claim that selected groups will cooperate or vote together. It SHALL explain that the second investiture ballot uses a simple-majority rule and that seat counts alone do not determine that vote. It SHALL not label a sub-176 sum as incapable of supporting investiture.

#### Scenario: Below absolute majority
- **WHEN** a selected set has 170 seats
- **THEN** the result states six seats are needed for the specified absolute threshold without saying that a government cannot be formed.

### Requirement: Exact sourced rule profile
The profile SHALL include a version, chamber, seat total, rule ID, exact source URLs and article locators, consultation date, and human review evidence for publication. Missing, conflicting, stale, or unapproved rule evidence SHALL block public activation. A private fixture SHALL identify its nonapproved status and remain nonindexable.

#### Scenario: Rule source changes
- **WHEN** retained evidence conflicts with a current chamber rule or a rule is corrected
- **THEN** public activation stops until the profile, dependent explanations, and human review are updated; no old rule is silently reused.

### Requirement: Memory-only scenario privacy
Seat entries, user labels, selected groups, and calculated sums SHALL stay in page memory. The simulator SHALL not store them in browser storage, URLs, cookies, logs, analytics, or requests. Reload, exit, reset, and back/forward-cache restoration SHALL clear them. Source navigation SHALL send no scenario or referrer.

#### Scenario: Complete interaction
- **WHEN** a visitor enters seats, selects groups, changes labels, or resets
- **THEN** the application sends no scenario requests or telemetry and creates no persistent political profile.

### Requirement: Sharing deferred
The first version SHALL omit personalized share, copy-scenario, and export controls. Any generic page link SHALL contain only the canonical simulator URL. Scenario encoding SHALL require a separate approved contract before introduction.

#### Scenario: Page link copied
- **WHEN** a visitor copies a provided page link
- **THEN** no labels, seats, selected groups, or result appear in its path, query, or fragment.

### Requirement: Neutral Spanish result and release review
Spanish result text SHALL label manual arithmetic and expose the applicable source and limits. G6 SHALL require human rule/copy review, arithmetic and privacy evidence, complete accessibility acceptance, reproducible builds, and approved recovery. Automated tests or planning-file existence SHALL not imply release approval.

#### Scenario: Review missing
- **WHEN** technical checks pass but required human or release evidence is absent
- **THEN** the feature remains a private nonindexable preview or unavailable, without a public release claim.
