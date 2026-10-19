# Proposal: Prior commitment follow-through

## Status

Exploratory proposal and methodology contract under Epic **E9** and Gate **G9**. No public release or automated scoring exists. Public publication is gated by human editorial approval and the go/no-go evaluation in package E9.3.

## Why

When reviewing electoral programmes for the 2026 general election, citizens frequently seek context on past performance: whether political formations followed through on their previous campaign commitments, altered their positions, or took contrary actions once in power. 

However, evaluating past commitments introduces severe risks of bias, political weaponization, and methodological failure:
1. Subjective terms like "mentira" (lie) impute psychological intent (*mens rea*) and destroy the platform's non-partisan credibility.
2. In a multi-party parliamentary system, governing formations hold executive power (decrees, budgets, administrative execution), whereas opposition formations hold only legislative voting power. Evaluating both by executive output introduces structural asymmetry.
3. Selective sampling of promises creates severe cherry-picking bias. Arbitrary aggregate percentages (e.g. "honesty scores") lack statistical validity without a fully audited census or pre-registered stratified sampling frame.
4. Relying on journalistic articles or political commentary imports third-party editorial bias into the primary platform data.

This proposal establishes a strict, evidence-based methodology that links prior 2023 commitments to verifiable primary sovereign records (*Boletín Oficial del Estado* and *Boletín Oficial de las Cortes Generales*), with objective non-evaluative states and institutional role transparency.

## What Changes

- Define a rigorous definition of a **testable commitment** (discrete, operative policy instruments with verifiable legislative or regulatory mechanisms; exclude broad slogans).
- Establish a **Sovereign Source Hierarchy**: restrict evidence to official gazettes (BOE, BOCG), official budget execution (IGAE), and verified statistical bodies (INE); prohibit journalistic opinion or unverified commentary as primary evidence.
- Introduce an explicit **Institutional Role Model** that distinguishes governing formations (evaluated on executive bills, decrees, and budget allocations) from opposition formations (evaluated on BOCG roll-call voting records on matching measures).
- Define an auditable **Taxonomy of Follow-Through States** (enacted as pledged, partially enacted, documented contrary action, coalition compromise, blocked by parliamentary vote, no initiative registered, outside state competence, unassessable). Prohibit the term "lie" and any aggregate percentage honesty score.
- Design a mobile-first, measure-level **Contextual Precedent Card** displayed inside the 2026 comparison view as an expandable disclosure, citing exact primary document identifiers, dates, and review signatures.
- Execute an offline 10-measure benchmark pilot dossier (5 governing, 5 opposition) to validate inter-reviewer agreement and establish the feasibility of the feature before modifying public generator code.

## Capabilities

### New Capabilities

- `commitment-evidence-register`: Schema and storage contract for historical commitments, primary legal citations (BOE, BOCG), institutional context, and dual-review audit trails.
- `follow-through-method`: Methodology rules governing commitment admissibility, institutional attribution (government vs. opposition), non-evaluative state assignment, and prohibition of aggregate scoring.

### Modified Capabilities

None. Main specs remain decoupled from exploratory tracks.

## Impact

This is package **E9.1** and **E9.2** under exploratory Gate **G9**. It does not block the MVP comparator, quiz, seat simulator, or CIS observatory. Implementation remains offline and editorial until Gate G9 approval.
