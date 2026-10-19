# Follow-through method

## Purpose

Define the methodological rules governing the evaluation of prior electoral commitments, the assignment of non-evaluative follow-through states, the prohibition of accusatory terminology or arbitrary aggregate scores, and the standards for neutral Spanish presentation.

## ADDED Requirements

### Requirement: Exhaustive non-evaluative status taxonomy
Every verified commitment record SHALL be classified into exactly one of eight mutually exclusive, auditable status values:
1. `enacted_as_pledged` (*Cumplida según programa*): Policy instrument enacted via BOE with parameters matching the manifesto commitment.
2. `partially_enacted` (*Parcialmente cumplida*): Relevant legislation enacted, but with restricted scope, lower statutory thresholds, or extended deadlines.
3. `contrary_action_taken` (*Acción contraria documentada*): The party enacted an executive decree or voted in the Cortes in direct opposition to their explicit campaign pledge.
4. `coalition_compromise` (*Modificada por pacto*): The commitment was formally superseded or altered in a signed, publicly published coalition agreement.
5. `blocked_by_parliament` (*Iniciada pero rechazada*): The party submitted the relevant bill or decree, but it was rejected by the parliamentary majority or lapsed upon early election call.
6. `no_initiative_registered` (*Sin iniciativa registrada*): The party possessed executive or legislative initiative but registered no bill, amendment, or decree on the pledged topic.
7. `outside_state_competence` (*Competencia no estatal*): The policy requires regional (CCAA) or municipal jurisdiction under Articles 148 and 149 of the Spanish Constitution.
8. `unassessable` (*Evidencia no concluyente*): Imprecise wording or conflicting official data prevents an objective determination.

#### Scenario: Contradictory voting action
- **WHEN** a party pledged in 2023 to oppose an initiative, but the official BOCG roll-call voting record shows the parliamentary group voted YES
- **THEN** the status is assigned `contrary_action_taken` with direct citation to the BOCG journal date and roll-call session number.

#### Scenario: Inconclusive data
- **WHEN** official data is missing or incomplete regarding the execution of a pledge
- **THEN** the status SHALL be set to `unassessable` rather than presumed unfulfilled.

### Requirement: Absolute prohibition of accusatory labels
The system, data schemas, public interface, and documentation SHALL strictly prohibit subjective, accusatory, or moralizing terminology, including but not limited to: "mentira", "mentiroso", "engaño", "traición", "falsedad", "hypocrisy", or "lie". All public text SHALL describe verified institutional actions and statutory citations using neutral, descriptive phrasing.

#### Scenario: Accusatory string check
- **WHEN** an editorial summary or UI label contains the word "mentira" or "engaño"
- **THEN** automated validation rejects the record with a neutrality violation error.

### Requirement: Prohibition of arbitrary aggregate scores and percentages
The platform SHALL NOT compute or display party-level "honesty percentages", "fulfillment ratios", or aggregate rankings unless based on an independently audited, complete census of all operative commitments in that manifesto. Hand-picked or non-exhaustive subsets SHALL NOT be converted into percentages, as selective denominators create severe cherry-picking bias.

#### Scenario: Percentage calculation blocked on sample
- **WHEN** an editorial subset of 10 or 20 commitments is registered for a party
- **THEN** the system displays individual measure-level precedent cards and explicitly prohibits displaying an aggregate percentage score.

### Requirement: Neutral Spanish copy and mobile disclosure standard
Spanish text SHALL use factual, non-evaluative verbs (e.g. "Aprobado mediante Real Decreto...", "Votó a favor en el Congreso según sesión...", "No se registró proposición de ley"). In the mobile comparison view (360–430 CSS px), prior commitments SHALL be rendered as collapsed expandable disclosure cards underneath the corresponding 2026 proposal, ensuring that 2026 proposals remain the primary view while offering verified historical context upon reader interaction.

#### Scenario: Responsive mobile disclosure
- **WHEN** a reader views a 2026 proposal with a linked historical precedent on a 390 px mobile viewport
- **THEN** the card renders collapsed with a clear touch target (>= 44 px) labelled "Antecedente en la legislatura previa", expanding to show the 2023 text, institutional role, status, and BOE/BOCG link upon user tap.
