# Manual seat scenario

## Purpose

Let readers enter hypothetical Congress seat distributions and inspect an accessible diagram and table without implying official results or forecasts.

## ADDED Requirements

### Requirement: Explicit manual Congress context
The simulator SHALL use a versioned Congress profile with 350 seats and sourced rule metadata. It SHALL label every distribution as user-entered, start with no assigned seats, and avoid official party, candidacy, result, or pact assertions. User labels SHALL not change rule eligibility.

#### Scenario: First visit
- **WHEN** a visitor opens the simulator
- **THEN** the Spanish introduction identifies a manual scenario, its chamber total, source links, and the absence of prediction; no real seat distribution or selected coalition is prefilled.

### Requirement: Bounded integer seat input
Each group SHALL have a unique stable ID, a trimmed nonempty plain-text label of at most 60 Unicode code points, and an integer seat count from 0 to 350. The scenario SHALL permit 1 to 30 groups. Invalid or blank counts SHALL remain explicit errors without silent rounding, clamping, or conversion to zero.

#### Scenario: Invalid count or label
- **WHEN** a count is blank, negative, fractional, nonnumeric, exponent notation, or above 350, or a label violates its limits
- **THEN** the field has an accessible Spanish error and no valid coalition result is shown until it is corrected.

#### Scenario: Hostile label
- **WHEN** a user enters markup in an otherwise valid label
- **THEN** it is displayed as literal text without executing markup or changing document structure.

### Requirement: Distribution total and unassigned remainder
For valid fields, the simulator SHALL show assigned seats and 350 minus assigned seats. A total below 350 SHALL be labelled incomplete and leave unassigned seats visible. A total above 350 SHALL invalidate arithmetic output. An incomplete valid scenario SHALL permit a selected sum but no conclusion about unassigned seats.

#### Scenario: Incomplete distribution
- **WHEN** the assigned total is 200
- **THEN** 150 seats remain visibly unassigned in the diagram and table; any selected sum is labelled as part of an incomplete scenario.

#### Scenario: Excess distribution
- **WHEN** otherwise valid groups sum to 351
- **THEN** a total error is shown and the diagram and coalition result do not retain a stale valid calculation.

### Requirement: Stable group editing
Visitors SHALL add, edit, and remove groups using explicit controls. Duplicate normalized labels SHALL be rejected to prevent ambiguous selection. Removing a group SHALL remove its coalition selection. Reordering SHALL not change totals or selected membership. Reset SHALL return to an empty allocation and clear selections.

#### Scenario: Selected group removed
- **WHEN** a selected group is removed
- **THEN** its seats leave the sum immediately and focus moves to an available editing control without an orphan selection.

### Requirement: Equivalent accessible views
The hemicycle and text table SHALL represent the same assigned and unassigned seat counts, with neutral stable group ordering. No ideological location or official party color SHALL be inferred. The table SHALL convey every numeric fact without color or the graphic. A diagram SHALL not be the only input or result control.

#### Scenario: Diagram unavailable
- **WHEN** a visitor uses a screen reader or cannot distinguish group colors
- **THEN** the labels, counts, total, and unassigned remainder remain available in an equivalent semantic table.

### Requirement: Spanish phone flow and fallback
The complete flow SHALL support keyboard and 320/360/390/430 CSS-px layouts without horizontal scrolling, with labelled controls, visible focus, 44-by-44-px targets, and accessible validation messages. Without JavaScript or a valid rule profile, the page SHALL retain source and method text without active calculation controls.

#### Scenario: Static fallback
- **WHEN** scripts are disabled or the rule profile is invalid
- **THEN** the page explains the limitation in Spanish and offers the chamber rules and method without a fabricated scenario result.
