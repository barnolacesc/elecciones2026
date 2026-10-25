# Tasks: 2023 corpus completion

Status: proposal-only. The checkboxes below are not implementation approval.
P0.1 is the bounded specification/audit package in this PR; later packages
require editorial review of this design and requirement delta.

## P0.1 — Inventory and rights contract

- [x] Reconcile `origin/main`, PR #101, current source/coverage records and
  draft the dated baseline audit. Evidence: `docs/2023-CORPUS-BASELINE-2026-10-19.md`.
- [x] Draft the inclusion, document, rights and coverage requirement delta and
  design. Evidence: this change's `design.md` and `specs/programme-provenance/spec.md`.
- [ ] Owner/editorial review: approve or revise 2023 inclusion rule, evidence
  standard, rights decision owner and private-store contract. No agent signoff.

## Later P0 work — not started

- [ ] Enumerate the eligible 2023 candidature manifest from authoritative
  evidence under the approved rule; peer-check coalition/territorial scope.
- [ ] Reconcile every relevant programme, annex and replacement; record
  unresolved searches, publication-date evidence, hashes and private archive
  references. Keep source bytes outside Git.
- [ ] Obtain per-source human authenticity and rights decisions; approve the
  taxonomy and reviewer/correction roles separately.
- [ ] Validate the inventory join and coverage accounting with missing,
  partial, replaced, unknown-date and coalition/territorial fixtures.

## Later P1 work — not started

- [ ] Review a separate proposal-level design/spec for initiative extraction,
  exact page evidence, independent statement and relationship approvals, and
  correction invalidation before implementing the full 2023 corpus.

## P1.1 — Proposal and comparison method (stacked on P0.1)

- [x] Draft the initiative, topic-search and relationship requirement deltas.
  Evidence: `specs/editorial-statements/spec.md` and
  `specs/programme-comparison/spec.md` in this change.
- [x] Draft the P1 evidence flow, fail-closed projection and fixture plan.
  Evidence: the P1.1 section of `design.md`; no source or claim changed.
- [ ] Owner/editorial review: resolve search stopping rules, proposal
  granularity, relationship approval roles and public coverage wording.
- [ ] Reconcile this P1 delta with P0.1 after PR #114 lands; complete the
  reviewed OpenSpec change before any 2023 corpus implementation.
- [ ] Implement and test the versioned private extraction/coverage queue and
  independent statement/relationship gates using fictional fixtures only.
- [ ] Populate real 2023 candidates and relationships only after P0 rights,
  exact-source and human editorial gates; keep public activation separate.

P1.1 validation (2026-10-19): a local structure check found four statement
requirements/seven scenarios and three comparison requirements/six scenarios;
it confirmed the draft status and dependency gates. `git diff --check` passed.
No implementation, source, editorial record or public output changed.
OpenSpec CLI and project Python 3.14/pytest are unavailable on this host.
The stacked PR has no automatic CI because `.github/workflows/ci.yml` targets
pull requests into `main` only; run CI after PR #114 lands and this PR is
retargeted. CI will remain engineering evidence, not human review.

## P1.2 — Comparison-set integrity (2026-10-23 draft)

- [x] Draft the set-accounting requirement and asymmetric fictional scenarios
  in `specs/programme-comparison/spec.md`; document the proposed ledger and
  one-position-per-party display limitation in `design.md`.
- [ ] Editorial owners review policy-question granularity, one-to-many
  treatment, permitted exclusions, ledger reviewer and bounded Spanish copy.
  This draft is not approval of a real relation or completeness claim.
- [ ] After P0 scope and P1 method review, specify the ledger schema and
  acceptance tests before implementing it. Test that every eligible approved
  statement is included or explicitly excluded, unmatched measures survive,
  and incomplete source/topic coverage cannot yield an exhaustive summary.
- [ ] Reconcile the approved method with the existing static/browser payload;
  keep real 2023 set activation behind source rights and statement/relationship
  review gates. No current pilot record is promoted by this task.

Validation (2026-10-23): a local structure check confirmed three P1.2
WHEN/THEN scenarios, the design section and unresolved editorial tasks;
`git diff --check` passed. This proposal changes no code or public data.
OpenSpec CLI and project Python 3.14 are unavailable locally; PR CI is the
engineering regression check, not editorial review.

P0.2 readiness audit (2026-10-20):
`docs/2023-CORPUS-READINESS-AUDIT-2026-10-20.md` maps the merged draft
requirements to current register/schema/parser gaps and fictional acceptance
cases. It records four pilot sources with unresolved rights, the unapproved
2023 denominator, PR #101's independent conflict/review gate, and the main
mock-quiz browser CI failure. This is documentation evidence only; none of
the owner decisions or later P0/P1 implementation tasks above is complete.

## P0.2 — Inventory reconciliation handoff draft (2026-10-21)

- [x] Draft a field-level input/output contract, independent review decisions,
  invalidation rules and fictional acceptance cases in `design.md`. Reconciled
  against `origin/main` `9542582`, the four 2023 pilot source rows and open
  draft PR #101; no source or editorial record changed.
- [ ] Owner/editorial review of the proposed record semantics, enumeration and
  inclusion policy, coalition/territorial treatment, rights ownership,
  evidence-store policy and coverage definitions. This draft is not approval.
- [ ] After review and PR #101 reconciliation, revise the applicable spec and
  task acceptance criteria for implementation. Then implement using fictional
  fixtures; enumerate real 2023 rows only under the approved rule.

Validation for this draft: `git diff --check` and a structure check of the six
fictional cases and pending gates. No corpus implementation or political claim
test applies to a design-only change; CI remains technical evidence only.

## P0.3 — Official enumeration evidence handoff (2026-10-22)

- [x] Identify the official 2023 proclaimed-candidature notice, its two linked
  corrections and the presented-list distinction; record the Teruel status and
  Baleares ballot-name cases in the dated evidence handoff. This is a source
  audit, not an enumerated or approved manifest.
- [x] Draft a correction-preserving design and requirement scenario without
  changing source, rights, editorial or public records.
- [ ] Owner sets and approves Congress/chamber and constituency/coalition
  inclusion units, finality/search protocol and reviewer. Peer-check every
  corrected row before any denominator or completeness claim.
- [ ] After approval, enumerate and reconcile the full manifest and separately
  discover programmes, annexes and rights decisions. PR #101's editorial gate
  and its merge conflict remain independent blockers.

Validation: official BOE pages and linked correction notices inspected on
2026-10-22; `git diff --check` and document-structure checks. No software or
political-content tests apply to this proposal-only source handoff.
