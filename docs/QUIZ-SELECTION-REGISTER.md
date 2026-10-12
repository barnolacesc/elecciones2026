# Quiz source readiness and selection register

Roadmap package: **E4.1**. Preparation for [#73](https://github.com/c2ventures/elecciones2026/issues/73); no real question or party mapping is created.

## Repository snapshot

Snapshot date: 2026-10-12. Input: [source register](../content/sources/register.json) at revision `5051119d0cd54613a4258fcbe3a7990c362e4300`. This is a local register audit, not a fresh check of party websites. Registered missing status does not prove that a programme is absent online.

Source register SHA-256: `049d3aa2a77f11e5ee613be3d8cf282c41e1e03b22a9fdba1247eb410bcd008c`.

| Party ID | Source ID | Registered state | File hash | Rights review |
|---|---|---|---|---|
| psoe | src-2026-psoe-v0 | missing | Missing | not_reviewed |
| pp | src-2026-pp-v0 | missing | Missing | not_reviewed |
| vox | src-2026-vox-v0 | missing | Missing | not_reviewed |
| sumar | src-2026-sumar-v0 | missing | Missing | not_reviewed |
| erc | src-2026-erc-v0 | missing | Missing | not_reviewed |
| pnv | src-2026-pnv-v0 | missing | Missing | not_reviewed |
| ehbildu | src-2026-ehbildu-v0 | missing | Missing | not_reviewed |
| junts | src-2026-junts-v0 | missing | Missing | not_reviewed |
| bng | src-2026-bng-v0 | missing | Missing | not_reviewed |

None of these nine registered sources supplies a verified, rights-reviewed target-election programme for a scored quiz. The source register is not proof of a final candidate list. Use [#3](https://github.com/c2ventures/elecciones2026/issues/3) for source discovery and [#13](https://github.com/c2ventures/elecciones2026/issues/13) for the reviewed target-election corpus.

The four registered 2023 programmes have retained file hashes but remain `published-unverified` with rights `not_reviewed` in this snapshot. They cannot replace 2026 evidence. The PP/ERC comparison pilot is not an approved eight-topic quiz set.

## Topic readiness

| Topic | Required items | Selected reviewed quiz items | Next evidence needed |
|---|---|---|---|
| housing | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| education | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| health-social-services | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| economy-work-tax | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| immigration | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| foreign-policy-eu | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| climate-energy | 2 | 0 | Verified target-election sources, comparable measures, and dual review |
| institutions-rights | 2 | 0 | Verified target-election sources, comparable measures, and dual review |

Zero selected items means no approved quiz set exists; it does not assert that a party has no proposal. Do not turn topic slots into invented questions.

## Candidate entry template

Create an entry only after exact source evidence exists. Retain selected and rejected candidates with their reasons. A blank template is not a candidate or a review mark.

- Candidate ID and register version:
- Election ID and topic ID:
- One policy instrument, objective, competence, scope, and preserved conditions:
- Programme ID/version/hash and exact page or section for each party:
- Source statement IDs and rights evidence:
- Draft Spanish item and proposed response scale:
- Proposed support/reject mapping or explicit gap for each registered party, with source grounds:
- Selection or rejection decision and rationale; alternatives considered:
- Duplicate-measure, wording/polarity, complexity, and asymmetric-source findings:
- Actual first and second human reviewers, dates, verdicts, and retained evidence references:
- Conflict disclosures, disagreements, resolution, and independent bias findings:
- Corrections and dependent item/mapping invalidation:

No numeric mapping may follow from silence, a different policy instrument, a general party ideology, or unreviewed extraction. A party needs reviewed coverage for all 16 items; at least two eligible parties are needed.

## Handoff

The owner has accepted the proposed method in [the decision record](QUIZ-METHOD-REVIEW.md#owner-decision--2026-10-12). Next, obtain verified source records and lawful reuse evidence, assign the independent human review lane, then populate actual candidates. Review source availability again before drafting; this snapshot is not live discovery. G4, E1.4, source rights, real item/mapping reviews, and G5 remain separate prerequisites.

Verification: source and topic rows were derived from the recorded local JSON files. The register checksum binds this snapshot to those bytes. No political statements, citations, review marks, scoring values, or public artifacts were added.
