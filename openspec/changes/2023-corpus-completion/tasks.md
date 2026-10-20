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

P0.2 readiness audit (2026-10-20):
`docs/2023-CORPUS-READINESS-AUDIT-2026-10-20.md` maps the merged draft
requirements to current register/schema/parser gaps and fictional acceptance
cases. It records four pilot sources with unresolved rights, the unapproved
2023 denominator, PR #101's independent conflict/review gate, and the main
mock-quiz browser CI failure. This is documentation evidence only; none of
the owner decisions or later P0/P1 implementation tasks above is complete.
