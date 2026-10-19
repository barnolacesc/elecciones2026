# Commitment evidence register

## Purpose

Define the data structure, storage contracts, and validation rules for preserving source-linked prior commitments, official legal and parliamentary citations, institutional context, and editorial review records.

## ADDED Requirements

### Requirement: Discrete historical commitment record
Every commitment record SHALL reference a valid, registered prior electoral programme (e.g. `es-gen-2023`). It SHALL record the exact party or candidacy ID, the primary taxonomy topic, an operative summary of the pledge (<= 40 words), exact source locators (`page` and/or `section`), and the SHA-256 hash of the registered programme document. Slogans, general statements of intention, or untestable rhetoric SHALL be rejected during validation.

#### Scenario: Valid commitment registration
- **WHEN** a commitment record references an approved 2023 programme with exact page coordinates and an operative policy instrument
- **THEN** the record passes structural validation and is assigned a unique stable ID (e.g. `cmt-2023-psoe-housing-001`).

#### Scenario: Rejection of unspecific rhetoric
- **WHEN** an extracted record lacks an operative instrument (e.g. "We will defend family welfare" without specific statutory or fiscal tools)
- **THEN** validation fails with an error indicating that the commitment lacks a testable operational mechanism.

### Requirement: Mandatory sovereign primary evidence
Every evaluated commitment SHALL reference at least one sovereign primary document confirming the legislative or regulatory outcome. Sovereign sources SHALL be strictly restricted to:
1. *Boletín Oficial del Estado* (`boe`): Official laws, Royal Decree-laws, Royal Decrees, or ministerial orders.
2. *Boletín Oficial de las Cortes Generales* (`bocg_initiative` or `bocg_vote`): Official parliamentary initiatives or roll-call vote logs (*votaciones nominales*).
3. *Intervención General de la Administración del Estado* (`igae`): Official budgetary execution and audit records.
4. *Instituto Nacional de Estadística* (`ine`): Official statistical records for quantitative targets.

Secondary sources, including newspaper reports, media analyses, party press releases, and editorial op-eds, SHALL be strictly prohibited as primary evidence.

#### Scenario: Sovereign source validation
- **WHEN** a commitment references a valid BOE identifier (e.g. `BOE-A-2024-2228`) with an official URL and publication date
- **THEN** the evidence item is validated and linked to the commitment record.

#### Scenario: Rejection of journalistic citations
- **WHEN** an evidence item provides a newspaper URL or media article as evidence of fulfillment or non-fulfillment
- **THEN** validation fails with a rule violation prohibiting secondary non-sovereign sources.

### Requirement: Institutional context attribution
Every commitment record SHALL declare the institutional role of the political formation throughout the observation period:
- `governing_sole`: Party held single-party executive government.
- `governing_senior`: Party led a coalition government holding the Prime Ministry (*Presidencia del Gobierno*).
- `governing_junior`: Party was a junior coalition member holding specific ministerial portfolios.
- `opposition`: Party held parliamentary representation without executive cabinet positions.

The evaluation criteria SHALL strictly correspond to the institutional role: executive enactments and decrees for governing parties; BOCG roll-call voting records on matching initiatives for opposition parties.

#### Scenario: Opposition evaluation role
- **WHEN** a commitment evaluates an opposition party
- **THEN** the record requires parliamentary voting evidence (`bocg_vote`) or bill initiatives (`bocg_initiative`), and SHALL not evaluate the party on unexercised executive power.

### Requirement: Four-Eyes editorial verification trail
Every published commitment record SHALL record independent approvals from at least two distinct human reviewers (`reviewed_by_1 != reviewed_by_2`) and a signoff from the lead editor. The record SHALL include the review timestamp, verification of source locators, neutrality audit of the factual summary, and confirmation of absence of evaluative or accusatory language.

#### Scenario: Missing second reviewer
- **WHEN** a commitment record is submitted with only one reviewer signature
- **THEN** the build marks the record as `pending_review` and excludes it from public view.
