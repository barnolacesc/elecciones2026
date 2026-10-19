# Tasks: Prior commitment follow-through

Exploratory package: **E9.1–E9.4**. Release gate: **G9**. No code or public publication occurs without human Gate G9 approval.

## 1. E9.1 — Methodology and schema contract

- [ ] 1.1 Obtain human editorial approval of the 8-state follow-through taxonomy (`enacted_as_pledged`, `partially_enacted`, `contrary_action_taken`, `coalition_compromise`, `blocked_by_parliament`, `no_initiative_registered`, `outside_state_competence`, `unassessable`).
- [ ] 1.2 Define JSON schema `schemas/commitment.schema.json` with strict validation (mandating operative instruments, page/section locators, sovereign BOE/BOCG citations, and prohibiting words like "mentira" or "engaño").
- [ ] 1.3 Define the Institutional Role matrix distinguishing governing formations (executive enactments, decrees, PGE budgets) from opposition formations (BOCG roll-call voting records).
- [ ] 1.4 Establish the Four-Eyes dual review protocol (`drafter != reviewed_by_2`, conflict of interest disclosures, lead editor signoff).

## 2. E9.2 — 10-Measure benchmark pilot dossier

- [ ] 2.1 Sample 10 high-salience, testable commitments from 2023 general election programmes (5 governing [PSOE/Sumar], 5 opposition [PP/Vox]) across at least 5 taxonomy topics.
- [ ] 2.2 Trace each commitment to primary sovereign evidence: exact BOE gazette references, BOCG roll-call session numbers, or official IGAE budget figures.
- [ ] 2.3 Draft neutral Spanish summaries for each outcome adhering to ASD-STE100 technical principles and Spanish descriptive standards (factual verbs only, no evaluative adjectives).
- [ ] 2.4 Complete independent Four-Eyes dual review on the 10-measure dossier and document any reviewer disputes.

## 3. E9.3 — Inter-reviewer agreement audit and go/no-go decision

- [ ] 3.1 Calculate inter-reviewer coding agreement across the 10 pilot items (target >= 90% agreement on status assignment).
- [ ] 3.2 Audit selection balance to ensure neither government nor opposition is disproportionately disadvantaged by the sampling frame.
- [ ] 3.3 Verify strict absence of party-level "honesty percentages", "fulfillment ratios", or aggregate scoring.
- [ ] 3.4 Draft and publish the formal Gate G9 Feasibility and Go/No-Go Report for project owner signoff.

## 4. E9.4 — Generator integration and mobile UI (Contingent on G9 signoff)

- [ ] 4.1 Implement offline Python loader and validator in `src/elecciones2026/commitments.py` validating commitment JSON fixtures against `schemas/commitment.schema.json`.
- [ ] 4.2 Integrate the expandable mobile disclosure component (`<details>`) into `src/elecciones2026/generator.py` underneath matching 2026 comparison measures.
- [ ] 4.3 Verify mobile ergonomics (360/390/430 CSS px), minimum 44px touch targets, keyboard navigation, and screen reader announcements.
- [ ] 4.4 Add unit and regression tests in `tests/test_commitments.py` checking determinism, absence of accusatory strings, and fallback handling when evidence is missing.
