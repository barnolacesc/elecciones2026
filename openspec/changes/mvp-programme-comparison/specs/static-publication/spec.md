# Static publication

## Purpose
Publish a low-cost, secure and reproducible comparison without a visitor database or dynamic user-facing API in the MVP.

## ADDED Requirements

### Requirement: Deterministic reviewed-data build
The Python 3.14 pipeline SHALL generate the same static output from the same approved source records and configuration, and SHALL fail on unreviewed or invalid references.

#### Scenario: Repeat build
- **WHEN** an approved dataset is built twice in a fixed environment
- **THEN** the public artifacts are identical.

#### Scenario: Draft enters input
- **WHEN** an unreviewed statement enters the publish set
- **THEN** the build fails without a partially published site.

### Requirement: No visitor profile
The MVP SHALL require no account, cookie or collection of quiz answers/visitor preferences, and SHALL keep comparisons client-side.

#### Scenario: User compares parties
- **WHEN** a visitor uses the comparator
- **THEN** no personal profile is sent to or stored by the project.

### Requirement: Spanish-language MVP and container parity
The public MVP SHALL present its interface and reviewed editorial content in Spanish. Local preview and production SHALL use containerized static serving, while untrusted document extraction remains outside the public serving container.

#### Scenario: Local preview
- **WHEN** a contributor runs the documented Docker Compose command
- **THEN** the public static preview is accessible on localhost without a database or application server.

#### Scenario: Production artifact
- **WHEN** a reviewed release is deployed
- **THEN** a non-privileged container serves the same static artifact in Spanish behind HTTPS, with no PDF processor or editorial credentials inside it.

### Requirement: Secure accessible release
The release SHALL use HTTPS, safe output escaping, a restrictive CSP compatible with the frontend, accessible controls, immutable artifacts and a tested rollback route.

#### Scenario: Hostile source string
- **WHEN** a source field contains HTML or script text
- **THEN** it is rendered as inert text and cannot execute in the browser.

#### Scenario: Release regression
- **WHEN** smoke checks fail after deployment
- **THEN** operators can restore the previous verified artifact.

### Requirement: Mobile-first comparison
The MVP SHALL keep the full comparison and source-tracing flow usable at 360–430 CSS px without horizontal scrolling or zooming, with touch targets at least 44 CSS px high.

#### Scenario: Phone-sized viewport
- **WHEN** a visitor opens a comparison at 390 CSS px width
- **THEN** party positions, reviewed similarities/differences and their source references remain readable and reachable in a single-column flow.

### Requirement: Load-resilient static delivery
The public release SHALL use a cacheable static artifact through the configured edge proxy. It SHALL have measured burst and concurrent-visitor behavior before release. The release record SHALL state an error budget, p95 latency, cache-hit ratio, origin load, and a capacity response plan.

#### Scenario: Target visitor load
- **WHEN** a representative test models 10,000 concurrent visitors, including cold-cache and burst phases
- **THEN** the team can compare recorded metrics with the approved service targets and must not claim capacity if the targets fail.

### Requirement: Crawlable source-linked pages
The public site SHALL expose indexable Spanish HTML pages for topics, parties, methodology, and sources, subject to source rights and publication status. It SHALL provide accurate titles, canonical links, a sitemap, and a `robots.txt` policy.

#### Scenario: Published topic page
- **WHEN** a crawler fetches a published topic URL without running JavaScript
- **THEN** it can read the page topic, current source-linked statements, publication date, and canonical URL.

### Requirement: Neutral shareable pages
The MVP SHALL offer a Share control on home, topic, and comparison views. It SHALL share a stable URL with neutral Spanish text. It SHALL use the device share sheet when available and provide a copy-link fallback. A shared URL SHALL contain no visitor ID, quiz answer, vote intention, or tracking token.

#### Scenario: Supported phone browser
- **WHEN** a reader selects Share on a supported HTTPS phone browser
- **THEN** the native share sheet receives a valid page URL and neutral title/text.

#### Scenario: Share API unavailable
- **WHEN** the browser does not support native sharing
- **THEN** the reader can copy the same stable URL with an accessible control.

#### Scenario: Comparison link opened
- **WHEN** a reader opens a shared two-party/topic link
- **THEN** the site restores valid selections and shows the approved comparison and source context. Invalid IDs do not create a claim.
