# Proposal: Seat and coalition simulator

Roadmap package: **E5.1**. Issue: #75. Status: planning for human review; no implementation or G6 release approval.

## Why

Readers can explore manually entered seat distributions and selected coalition sums without party programmes. The tool must distinguish an arithmetic scenario from an election result, forecast, voting intention, or political pact.

## What Changes

- Define one Congress profile with 350 seats, validated manual entries, a visible unassigned remainder, and an accessible hemicycle and text table.
- Sum user-selected groups against the 176-seat absolute-majority threshold. Explain the scope of that threshold and preserve the distinction from second-ballot investiture rules.
- Specify a Spanish static route, memory-only scenario state, source-linked rule explanations, and bounded implementation packages with human release gates.

Initial scope: `/simulador/`; Congress only; arbitrary user-labelled groups with stable local IDs; empty initial seat counts; no official candidacy, result, or pact is inferred. A later verified candidacy preset is a separate reviewed content addition. Scenario sharing is deferred until an approved privacy and URL contract exists.

Exclusions: vote-to-seat conversion, forecasts, pact probability, ideological ordering, stored scenarios, accounts, APIs, automatic coalition enumeration, Senate/regional chambers, second-ballot vote simulation, and personalized sharing in the first version.

## Capabilities

### New Capabilities

- `seat-scenario`: Validate manual groups and seat totals; provide accessible Spanish input, hemicycle, table, and static fallback.
- `coalition-arithmetic`: Sum selected groups, explain the sourced absolute-majority rule, and retain a memory-only privacy boundary.

### Modified Capabilities

None. `static-publication` belongs to the unarchived MVP change, not the main spec inventory. Integrate the new route while preserving existing publication contracts.

## Impact

The current Python generator supplies static routes and content-addressed local scripts; the quiz supplies an existing browser-only arithmetic pattern. This change needs a small pure seat engine, a separate Spanish UI, and optional static-generator integration. No programme parser or live source request enters the public runtime.

The user authorized E5.1 planning before the quiz's real content is ready. This changes planning order only. G4 remains the roadmap prerequisite for release progression; human E5.1 acceptance and a new implementation request are required before coding. Private fixture implementation before G4 needs explicit authorization. G6 also needs correctness, Spanish editorial, privacy, accessibility, build, and recovery evidence.

Risks: user-entered labels look official; selected seats are mistaken for promised votes; incomplete allocations look like results; color implies ideology; shared URLs expose personal choices. The specifications require visible scenario labels, no political inference, a remainder, neutral presentation, memory-only state, and a separate sharing decision.
