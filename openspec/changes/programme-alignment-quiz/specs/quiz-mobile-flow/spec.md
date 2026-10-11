# Quiz mobile flow

## Purpose

Let visitors answer, skip, revise, and inspect programme alignment through an accessible Spanish phone flow.

## ADDED Requirements

### Requirement: Informed voluntary entry
The introduction SHALL state the purpose, 16-item length, eight-topic coverage, memory-only answers, loss on leaving or reloading, scoring limits, and absence of vote recommendations. It SHALL link to coverage and method before the start control. Participation SHALL require no account or preference disclosure beyond voluntary answers.

#### Scenario: Visitor starts
- **WHEN** a visitor opens `/cuestionario/`
- **THEN** they can read the privacy and scoring summary and inspect sources before selecting “Empezar”.
- **AND** no political answer or result is preselected.

### Requirement: Explicit accessible navigation
The flow SHALL provide introduction, question, optional answer-review, result, and method states. Questions SHALL show topic and item progress, response labels, source details, previous/next controls, and explicit skip. Selecting an answer SHALL NOT automatically advance. Visitors SHALL be able to revise any answer and clear the entire session. Finishing SHALL open results directly without a required review step.

#### Scenario: Back and revise
- **WHEN** a visitor returns to an answered item
- **THEN** its current selection is present in memory, editing replaces it, and the review page distinguishes answered, skipped, and not-yet-visited items.

#### Scenario: Finish with skips
- **WHEN** a visitor requests a result with unfinished items
- **THEN** the question state explains that unfinished items count as skipped, and the explicit result control opens results directly with those items skipped.
- **AND** insufficient answer coverage produces the existing insufficient-data explanation.

#### Scenario: Optional answer review
- **WHEN** a visitor chooses to review answers from a question or result
- **THEN** the review state provides an edit control for each item and an explicit control to see results.
- **AND** visitors who do not choose review can reach results without opening that state.

### Requirement: Full WCAG 2.2 AA acceptance
All quiz pages, states, and the complete process SHALL meet all applicable WCAG 2.2 Level A and AA success criteria and conformance requirements. G5 SHALL require a criterion-by-criterion audit with evidence, justified non-applicability, and no unresolved failure. Automated checks alone SHALL NOT establish conformance.

#### Scenario: Accessibility release review
- **WHEN** G5 is assessed
- **THEN** reviewers check the complete flow against the [W3C WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/), including full pages, complete processes, supported technology, and non-interference.
- **AND** a conformance claim is permitted only after the implementation audit passes.

### Requirement: Phone layout and target size
All interactive targets SHALL be at least 44 by 44 CSS px, including source links and disclosure controls. The one-column flow SHALL work at 360, 390, and 430 CSS px and reflow at 320 CSS px without horizontal scrolling. It SHALL support portrait and landscape, 200 percent text resize, 400 percent zoom, and user text spacing without lost content or controls.

#### Scenario: Magnified phone view
- **WHEN** a visitor magnifies text or uses a 320-CSS-px viewport
- **THEN** answers, sources, explanations, and navigation remain readable and operable, without clipped text or controls.

### Requirement: Perceivable operable controls
The flow SHALL provide semantic headings, labelled grouped answers, keyboard operation, visible unobscured focus, logical reading order, accessible status/error messages, and text alternatives for visual scores. Text and control contrast SHALL meet AA. Color SHALL NOT be the only signal. No timed answers, dragging, or motion SHALL be required.

#### Scenario: Assistive technology flow
- **WHEN** a visitor completes the quiz with keyboard or a screen reader
- **THEN** they can select, skip, revise, open citations, adjust weights, and inspect results without a trap or pointer-only action.
- **AND** state changes announce the new heading or concise status without reading every result repeatedly.

#### Scenario: Fixed footer
- **WHEN** navigation controls remain visible during scrolling
- **THEN** they do not obscure focused elements, source links, or magnified content.

### Requirement: Plain Spanish result explanation
Public UI SHALL use neutral `es-ES` with reviewed scoring and uncertainty explanations. Results SHALL identify alignment with the answered measures, answer coverage, set version, source limits, weights, and the meaning of skips. Details SHALL be reachable without reading a formula or interpreting a chart.

#### Scenario: Draft result text
- **WHEN** editors prepare UI text
- **THEN** drafts use phrases such as “Coincidencia con las medidas que has respondido”, “Omitir no significa estar en contra”, “Cada tema tiene el mismo peso al empezar”, and “Este resultado no recomienda a quién votar”.
- **AND** final wording receives human editorial review; these phrases are interface drafts, not approved political content.

### Requirement: Safe static fallback
If scripts are unavailable, a set is unavailable, or validation fails, the page SHALL explain the limitation in Spanish and retain access to source coverage and method. It SHALL NOT offer a nonfunctional answer submission or fabricated result.

#### Scenario: JavaScript disabled
- **WHEN** the page loads without script execution
- **THEN** the introduction, method, and source information remain readable, and a message explains that local scoring needs JavaScript.
