# Quiz privacy and fairness

## Purpose

Prevent collection or persistence of political preferences and make privacy and editorial fairness verifiable release conditions.

## ADDED Requirements

### Requirement: Strict zero visitor tracking
The quiz SHALL have no analytics, telemetry, tracking pixels, visitor identifiers, fingerprinting, session replay, personalized experiments, or behavioral events. It SHALL NOT load third-party scripts, fonts, images, embeds, or remote inference services. No account SHALL be required or offered for quiz participation.

#### Scenario: Normal interaction
- **WHEN** a visitor starts, answers, skips, edits, changes weights, or reads results
- **THEN** no visitor identifier or behavioral event is created or sent to any endpoint.
- **AND** all runtime resources are approved local static assets.

### Requirement: Memory-only political state
Answers, weights, progress, result values, and prior result changes SHALL remain in transient browser memory only. The quiz SHALL NOT write them to cookies, localStorage, sessionStorage, IndexedDB, caches, service workers, files, browser history state, or URLs. No persistent political profile SHALL be created.

#### Scenario: Reload or exit
- **WHEN** a visitor reloads, leaves the quiz, closes the page, or selects “Borrar respuestas”
- **THEN** the application discards all political state and a subsequent entry starts empty.
- **AND** restoration from browser back/forward cache clears the state before showing quiz content.

#### Scenario: Second tab
- **WHEN** the same quiz is opened in another tab
- **THEN** the second tab has no access to answers or results from the first tab.

### Requirement: Zero political data transfer
Political state SHALL NOT enter network requests, query strings, URL fragments, referrers, beacons, form submissions, console logs, error reports, access logs, or crash diagnostics. Static asset requests SHALL be independent of answers, weights, progress, and party scores. External citation navigation SHALL send no referrer or political payload.

#### Scenario: Answer trace
- **WHEN** a network and console trace is captured using fictional fixture answers
- **THEN** answering and scoring generate zero requests, and no answer or score is present in console output or URLs.

#### Scenario: Citation opened
- **WHEN** a visitor selects an official source link
- **THEN** the request contains only the reviewed public source URL and locator, uses a no-referrer policy, and does not expose answers or scores.
- **AND** the interface explains that the external source has its own privacy policy.

### Requirement: Neutral sharing only
Any quiz share or copy-link action SHALL provide only the canonical generic quiz URL and neutral public text. Answers, scores, party alignment, user weights, identifiers, and personalized result exports SHALL NOT be shared by the application.

#### Scenario: Share from results
- **WHEN** a visitor selects “Compartir el cuestionario”
- **THEN** the share payload is the same generic URL for every answer set, without query parameters or a result fragment.

### Requirement: Operational privacy gate
Before G5, operators SHALL verify browser, CDN/edge, origin, monitoring, and error configuration against zero tracking. Retained visitor-level logs, IP or user-agent histories, cookies, and request correlation SHALL be absent for quiz delivery. Aggregate availability metrics SHALL contain no visitor identifiers or political data. An incompatible provider setting SHALL block release.

#### Scenario: Existing log policy
- **WHEN** deployment permits retained technical connection logs under the existing security plan
- **THEN** G5 remains blocked until the quiz delivery policy and configuration are reconciled and reviewed; anonymization or a short retention period alone does not prove zero tracking.
- **AND** transient network processing required to serve a static response is distinguished from retained tracking data.

### Requirement: Non-directive fair results
The quiz SHALL present programme-measure alignment only, with alphabetical party order, equal card space, visible source gaps, and no endorsement, vote advice, ideological profile, or prediction of conduct. Human review SHALL verify the same evidence and scoring standards for every party before G5.

#### Scenario: Results audited
- **WHEN** reviewers inspect results under extreme and balanced fictional answer patterns
- **THEN** no party gets preferred order, visual prominence, hidden weight, or a different denominator, and excluded parties remain visibly explained.
- **AND** numerical similarity is not labelled electoral suitability or a recommendation.

### Requirement: Documented fairness and comprehension evidence
G5 SHALL require a recorded independent editorial bias review and voluntary usability checks of skips, coverage, weights, citations, uncertainty, and non-recommendation wording. Test evidence SHALL use fictional answers and record only nonpolitical aggregate task outcomes. Unresolved substantive fairness or comprehension failures SHALL block release.

#### Scenario: User review
- **WHEN** test participants inspect a result
- **THEN** the review records whether they can explain a score change, distinguish missing evidence from opposition, and recognize that the tool does not recommend a vote.
- **AND** participant political answers, identities linked to results, and recorded political profiles are not collected.
