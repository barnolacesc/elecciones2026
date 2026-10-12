# Quiz method review

Roadmap package: **E4.1**. GitHub issue: [#72](https://github.com/c2ventures/elecciones2026/issues/72).

Status: owner acceptance recorded on 2026-10-12; independent review and release prerequisites remain pending. The tables below retain the original proposed decisions for comparison with the dated record at the end. This packet summarizes the existing contract; the dated owner decision below records acceptance without changing the contract. The mock engine is implemented. Real question selection and release remain separate.

## Review inputs

Read the [proposal](../openspec/changes/programme-alignment-quiz/proposal.md), [design](../openspec/changes/programme-alignment-quiz/design.md), and all four specifications: [question set](../openspec/changes/programme-alignment-quiz/specs/quiz-question-set/spec.md), [scoring](../openspec/changes/programme-alignment-quiz/specs/quiz-scoring/spec.md), [mobile flow](../openspec/changes/programme-alignment-quiz/specs/quiz-mobile-flow/spec.md), and [privacy](../openspec/changes/programme-alignment-quiz/specs/quiz-privacy/spec.md). Record decisions against the exact Git revision reviewed. If this summary differs from those files, report the difference before accepting it.

The PP/ERC historical comparison covers housing, health, and education. Approval of those comparison statements does not approve quiz items, binary party mappings, eight-topic coverage, or a target-election question set. The current quiz contract requires 16 items across eight topics. Do not enlarge the historical pilot or convert it into a scored quiz without a separate reviewed decision.

## Method decisions — task 1.1

For each row, record **accept**, **revise**, or **reject**, with a reason. An unanswered row is pending.

| ID | Current proposal | Effect and review question | Decision |
|---|---|---|---|
| M1 | 16 fixed questions; two per core topic | Includes housing, education, health/social services, economy/work/tax, immigration, foreign policy/EU, climate/energy, and institutions/rights. Keep this length and balance? | Pending |
| M2 | One election and fixed question order | No adaptive selection or mixed-election evidence. Keep taxonomy order, then stable item IDs? | Pending |
| M3 | Score only parties with all 16 reviewed mappings; require at least two eligible parties | Show other parties and their gaps without scores. Strict coverage can prevent launch or exclude parties; review the exclusion pattern. Keep this rule? | Pending |
| M4 | Explicit support = +1; explicit rejection = -1 | Silence, ambiguity, or a different policy instrument is a gap. Preserve relevant conditions. Is binary mapping acceptable for each selected measure? | Pending |
| M5 | Five numeric visitor answers; separate skip | Values are -1, -0.5, 0, +0.5, +1. Neutral is an answer; unknown/skip is absent. Keep this scale? | Pending |
| M6 | At least eight numeric answers across four topics | Below the threshold, show counts and sources without percentages. This is a product limit, not statistical confidence. Keep it? | Pending |
| M7 | Equal topic weights initially; optional double weight | Average answered items within each topic, then weight answered topics. Apply identical weights to every party; unanswered topics do not enter the answered score. Keep this behavior? | Pending |
| M8 | Whole-number percentages; alphabetical party cards | Compare exact values before rounding. Identify exact ties and differences of at most one unrounded point. Explain equal rounded values. No preferred party or vote recommendation. Accept? | Pending |
| M9 | Full-set bounds for skipped answers | Use all eight topics, including unanswered topics. Bounds are possible calculations, not probabilities; their denominator differs from the answered score. Accept this explanation and presentation? | Pending |
| M10 | Remove one answered item at a time for sensitivity | Recalculate only where the minimum answer threshold still holds. Otherwise show sensitivity unavailable. Keep this method? | Pending |

The scoring specification contains the normative formulas. A nonpolitical arithmetic example: an answer of +1 and a mapped position of +1 give 100% item alignment; an answer of +1 against -1 gives 0%; a neutral answer gives 50% against either binary position. Skipping creates no item contribution. These examples do not establish a party position or validate the method scientifically.

## Selection and bias review — task 1.2

Approve the protocol before preparing a real set in [#73](https://github.com/c2ventures/elecciones2026/issues/73). Keep a versioned register of selected and rejected candidates. Each candidate needs its exact source version/hash/location, one policy instrument, scope, conditions, topic, selection reason, rejected alternatives, and mapping evidence for every party in the approved inclusion register.

Two distinct human reviewers must approve each item's wording and every party mapping. Retain disagreements and resolutions. A separate review lane must check repeated measures, leading wording, polarity, complexity, conditions, source asymmetry, and excluded-party patterns. Equal question counts alone do not prove fairness. Unresolved substantive findings block release.

| ID | Decision requested | Decision |
|---|---|---|
| B1 | Accept or revise the candidate register and identical evidence standard for all parties. | Pending |
| B2 | Identify the editorial owner and independent review lane; agree conflict handling. | Pending |
| B3 | Accept or revise the exclusion-bias audit and requirement to resolve substantive findings. | Pending |

No real political question or party mapping is proposed in this packet. Do not generate questions to fill missing topics.

## Spanish interface drafts — task 1.3

These phrases are drafts for editorial review. Approval here concerns interface wording, not programme content. Review against the rendered mock flow described in [QUIZ.md](QUIZ.md).

| Purpose | Draft Spanish text | Decision |
|---|---|---|
| Scope | Este cuestionario compara tus respuestas con medidas de los programas. No recomienda a quién votar. | Pending |
| Length | Son 16 preguntas sobre ocho temas. Puedes omitir preguntas y cambiar tus respuestas. | Pending |
| Privacy | Tus respuestas se mantienen solo en la memoria de esta página. Se pierden al salir o recargarla. | Pending |
| Response scale | Totalmente en desacuerdo / Más bien en desacuerdo / Ni de acuerdo ni en desacuerdo / Más bien de acuerdo / Totalmente de acuerdo | Pending |
| Skip | No lo sé / Omitir | Pending |
| Neutral versus skip | Una respuesta neutral cuenta en el cálculo. Omitir una pregunta no significa estar en contra. | Pending |
| Current score | Coincidencia con las medidas que has respondido | Pending |
| Minimum coverage | Responde al menos ocho preguntas de cuatro temas para ver los porcentajes. | Pending |
| Weights | Cada tema tiene el mismo peso al empezar. Puedes dar doble peso a un tema. Los temas sin respuestas no cuentan en el porcentaje actual. | Pending |
| Source gap | Faltan datos revisados para calcular el porcentaje de este partido. Esto no significa que esté en contra. | Pending |
| Bounds | Estos límites muestran posibles resultados si completas las preguntas omitidas. Incluyen todos los temas. No indican una probabilidad. | Pending |
| Sensitivity | Esta comprobación muestra cómo cambia el porcentaje al quitar una respuesta cada vez. Solo se calcula si quedan suficientes respuestas. | Pending |
| External source | El documento se abre en otra página. El sitio de origen tiene su propia política de privacidad. | Pending |

Apply the existing drafting rules: one measure per question, short sentences, explained technical terms, preserved source conditions, and no slogans, value judgements, double negatives, or leading questions.

Use [QUIZ-COMPREHENSION.md](QUIZ-COMPREHENSION.md) to agree a volunteer sample and an acceptance rule before sessions. The current proposed rule requires every volunteer who attempts each critical task to complete and explain it without help; a failure triggers revision and retesting. Reviewers must accept or revise that rule. Use assigned fictional answers and retain aggregate task outcomes only. Real citation inspection must be repeated with an approved real set. No participant session or comprehension acceptance is recorded here.

## Decision record

Complete this record after an actual review. Do not replace blank fields with assumed approvals. Retain identity and conflict information in the approved editorial evidence location; publish only permitted review metadata.

- Reviewed Git revision and method version: pending.
- Actual reviewer, role, review date, and evidence reference: pending.
- Decisions M1–M10 and reasons: pending.
- Decisions B1–B3 and reasons: pending.
- Spanish wording decisions and required corrections: pending.
- Volunteer sample and comprehension acceptance rule: pending.
- Unresolved findings and owner: pending.

An acceptance applies only to the identified revision and stated scope. A requested method change needs coherent specification and implementation updates before further acceptance. A content change needs fresh item and mapping review.

## Completion and release boundary

Tasks 1.1–1.3 remain open until authentic decisions and evidence are retained. Task 1.4 remains open until G4, E1.4, and applicable source rights evidence are verified for the target election. The [task record](../openspec/changes/programme-alignment-quiz/tasks.md) and [release packet](QUIZ-RELEASE.md) retain the other G5 requirements. Method acceptance does not approve real content, hosting privacy, accessibility, capacity, deployment, or public release.

Preparation verification: compared this packet with the proposal, design, and four specifications; checked local Markdown link targets and whitespace. No code or scoring contract changed. Human method, copy, fairness, source, and comprehension reviews have not occurred through this preparation.

## Owner decision — 2026-10-12

Reviewed packet revision: `5051119d0cd54613a4258fcbe3a7990c362e4300` (merged PR #88). Reviewer: Cesc, project owner, in the project conversation. Evidence: after the assistant listed the proposed 16 questions/eight topics, complete party coverage, eight-answer/four-topic minimum, selection protocol, and Spanish wording and requested decisions, the owner replied “yea continue”. This is acceptance of the proposed method and interface drafts for continued preparation; it is not independent editorial evidence for political records.

- M1–M10: accepted by the owner as the proposed method, including the scoring, weights, ties, bounds, and sensitivity defined by the linked specification.
- B1 and B3: selection register and bias-audit protocol accepted by the owner. Independent findings and reviewer assignments are not supplied by this acceptance.
- Spanish interface drafts: accepted by the owner for this revision. Actual participant comprehension and independent editorial review remain pending.
- B2: independent review lane, conflict disclosures, and dispute handling assignments remain pending. No reviewer identity is invented.
- Volunteer sample and comprehension acceptance rule: pending; the owner's reply did not select a sample or provide participant evidence.

This record does not complete tasks 1.1–1.4 or authorize #73 real content activation. See [the source readiness and selection register](QUIZ-SELECTION-REGISTER.md). A future source or method change requires review against its new revision.
