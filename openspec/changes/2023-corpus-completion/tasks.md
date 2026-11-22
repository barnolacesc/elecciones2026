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

## P1.5 — Relationship decision collision gate (2026-10-25 draft)

- [x] Reconcile `origin/main` `8e2fab4`, draft/conflicting PR #101 and open
  PRs #149/#150; inspect the per-record validation and ID-ordered emission
  path. Draft one requirement, four fictional scenarios and the private ledger
  design. No corpus, editorial, rights or public record changed.
- [ ] Editorial/OpenSpec review: decide policy-question identity, legitimate
  pair reuse, collision arbitrator and correction/supersession evidence. This
  draft is not approval of any relationship or implementation.
- [ ] After P0/P1 review, specify the concrete ledger schema, cross-record
  validator and acceptance tests for static/browser parity using fictional
  fixtures. Block affected publication on unresolved duplicate decisions.
- [ ] Reconcile any real relationship candidates only through the independent
  human review gate; do not promote the four-source pilot from this draft.

Draft validation (2026-10-25): `git diff --check` passed. A local structure
check found one P1.5 requirement, four paired WHEN/THEN fictional scenarios,
the design section and open review tasks. OpenSpec CLI was unavailable in
this checkout. These checks validate draft structure, not editorial meaning.

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

## P1.3 — Topic-search evidence and absence gate draft (2026-10-24)

- [x] Draft the version-bound search-ledger and fail-closed absence requirement,
  six fictional cases and proposed states in this change's `design.md` and
  `specs/editorial-statements/spec.md`. Reconciled against `origin/main`
  `77de048`, the four pilot source rows and draft/conflicting PR #101. No real
  search, rights decision, editorial record or public artifact changed.
- [ ] Owner/editorial review: approve the relevant-document and search-stopping
  protocol, negative-finding reviewer quorum, non-searchable source handling,
  translation treatment and reader-facing Spanish wording. This draft is not
  an editorial decision.
- [ ] After P0 inventory/taxonomy review and PR #101 reconciliation, align the
  concrete schema and validator tasks with the approved protocol. Use only
  fictional fixtures for implementation until source rights and editorial
  gates are satisfied; test invalidation and private/public projection.

P1.3 validation is a documentation/requirement structure check and
`git diff --check`; neither can approve a negative political claim.

## P0.5 — Rights withdrawal and use-scope change draft (2026-10-25)

- [x] Reconcile current rights fields, four 2023 source states, PR #101 and
  generator/quiz use gates; draft the decision-revision, dependency and served-
  artifact handoff in `design.md` and `specs/programme-provenance/spec.md`.
  No real decision, source record, code or public artifact changes.
- [ ] Human source-rights owner reviews event authenticity, use vocabulary,
  effective time, challenged-use policy, decision-store access and release
  response. A challenge does not let an agent adjudicate a legal permission.
- [ ] After P0 review and PR #101 reconciliation, specify concrete records and
  validators; test restrictive and renewed decisions with fictional fixtures,
  including unchanged hashes and already served artifacts. Keep real 2023
  activation behind source, editorial and release gates.

Validation for this draft: requirement/scenario structure and `git diff
--check`. CI may check engineering structure but is not human rights review.

## P1.4 — Multi-document applicability and conflict gate (2026-10-25 draft)

- [x] Reconcile `origin/main` `8e2fab4`, the four general-scope 2023 pilot
  source rows, open draft/conflicting PR #101 and open rights-withdrawal PR
  #149. Draft the distinct document-scope/conflict requirement and design in
  this change. No annex absence, source precedence, political position or
  editorial decision is inferred from the pilot.
- [ ] Owner/editorial review: approve document precedence and replacement
  evidence rules, territorial scope, coalition attribution, material-conflict
  threshold, adjudication roles and bounded reader-facing wording.
- [ ] After P0 inventory and P1 method review, specify the private ledger
  schema and validators. Test the six fictional cases in `design.md`, including
  static/browser projection and invalidation, before any real record is used.
- [ ] Reconcile with P1.2 comparison-set accounting and PR #101's source-use
  gate. Keep conflicting or unapproved candidates out of published relations;
  human content approval and release remain separate.

Validation for this draft: `git diff --check` and a structure check of the
requirement, five scenarios and pending review tasks. No source, rights,
statement, comparison or public output changes; CI is engineering evidence,
not human review.
PR #150 run `40185225258` did not execute the test or mobile jobs: GitHub
reported an account payment/spending-limit block before any job steps began.
Re-run CI after billing is restored; local checks do not replace it.

## P0.4 — Publisher-bound source identity draft (2026-10-26)

- [x] Reconcile current main, the four 2023 pilot register rows and PR #101;
  record the limited evidence in
  `docs/2023-SOURCE-IDENTITY-READINESS-2026-10-26.md`. This does not recheck
  publisher websites or private PDFs.
- [x] Draft the exact-byte authenticity requirement, review boundary and
  fictional redirect/mirror/version cases in the provenance spec and design.
- [ ] Owner/source-authenticity review: choose the evidence capture and
  recheck protocol, reviewer, historic-page handling and mirror-equivalence
  rule. Keep this separate from rights and editorial decisions.
- [ ] After P0 review and PR #101 reconciliation, specify the private record
  schema and validators; test only fictional cases before any real version is
  marked authentic. Reconcile with P0 document scope and withdrawal rules.

Validation: `git diff --check` and a local requirement/design/task structure
check. No source, rights, content or public output was changed. CI is technical
evidence, not a human authenticity or editorial review. PR #155 run
`40293266028` could not start test jobs because GitHub reported an account
payment or spending-limit block; hosted CI is therefore unverified, not a
passing or failing test result.

## P1.4 — Correction dependency closure draft (2026-10-26)

- [x] Reconcile the current correction schema, loader and review gate with the
  P1 coverage/comparison/quiz dependency needs. Evidence:
  `docs/2023-CORRECTION-DEPENDENCY-AUDIT-2026-10-26.md`.
- [x] Draft the version-bound impact, withholding and projection-consistency
  requirement, design and fictional scenarios in this change. Proposal only;
  no source, editorial, quiz or public record changed.
- [ ] Owner/editorial review: decide correction severity, reviewer segregation,
  rights-withdrawal handling, partial-comparison wording and public notice.
- [ ] After P0/P1 contracts and PR #101 are reconciled, specify the concrete
  dependency graph, schema migration and transaction boundary. Test source
  replacement, retraction, reclassification, missing IDs, cross-election
  isolation and static/browser parity with fictional fixtures before any real
  2023 activation.

Validation (2026-10-26): requirement/scenario structure and `git diff --check`
passed; `PYTHONPATH=src python3 -m unittest tests.test_editorial_gates
tests.test_schemas -q` passed 47 existing tests on Python 3.11. Project
Python 3.14 and pytest were unavailable locally. Existing implementation
tests cannot approve this draft or a political correction.
PR #157 CI run `40308249819` failed before both test and mobile jobs reported
any steps; `gh run view --log-failed` returned no job log. This is not a test
result or an editorial decision. The CI execution blocker remains unresolved.

## P1.6 — Initiative identity and duplicate lineage draft (2026-10-26)

- [x] Audit the current statement/source boundary and draft a private
  occurrence-to-candidate-to-initiative requirement, design and five fictional
  scenarios. This is a proposal only; no real initiative, right or approval is
  added. See `docs/2023-INITIATIVE-LINEAGE-AUDIT-2026-10-26.md`.
- [ ] Owners review initiative granularity, reviewer quorum/segregation,
  territorial identity treatment, multi-citation presentation and count
  definitions. Reconcile the approved decisions with P0 source scope, P1.4
  document applicability, P1.2 set accounting and PR #101.
- [ ] After those reviews, define a private ledger schema and validator with
  fictional split/duplicate/revision fixtures. Prove repeated extraction does
  not inflate counts, distinct conditions do not auto-merge, and regrouping
  invalidates dependent statements, comparisons, coverage and quiz items.
- [ ] Review any proposed public projection and exact-content source-use
  decisions separately. Do not treat this draft or CI as editorial approval.

Validation (2026-10-26): `git diff --check`, a five-scenario structure check,
and 51 passing existing tests (`PYTHONPATH=src python3 -m unittest
tests.test_editorial_gates tests.test_editorial_policy
tests.test_source_register`). No source PDF, political claim, rights record,
schema, code or public artifact changed. The local interpreter is Python 3.11,
not the project 3.14 runtime. PR #158 CI jobs did not start test steps:
GitHub annotated an account payment/spending-limit block. CI remains unverified
and is not editorial approval.

## P0.5 — Coverage projection handoff (2026-10-27 draft)

- [x] Reconcile the four-row 2023 pilot, example review states, unresolved
  2023 denominator/taxonomy and overlapping open PRs; draft stage-separated
  coverage requirements, design and fictional cases. Evidence:
  `docs/2023-COVERAGE-PROJECTION-HANDOFF-2026-10-27.md`. No source, rights,
  editorial, public output or deployment record changed.
- [ ] Owner/editorial review: approve the coverage units, denominators,
  stage definitions, public unknown/partial wording and snapshot invalidation
  rules. This draft grants no such decision.
- [ ] After P0 inventory and P1 search/comparison reviews, reconcile the
  approved contract with other open P0/P1 drafts; add the formal requirement
  delta, schema, design and fictional data/rendered tests before implementing
  a coverage projection. Do not infer completeness from the four pilot rows.

## P1 quantitative-comparability method draft (2026-10-28)

- [x] Audit current statement/relationship schemas and P1 method against
  numeric-basis and derived-value risks. Evidence:
  `docs/2023-QUANTITATIVE-COMPARABILITY-AUDIT-2026-10-28.md`.
- [x] Draft version-bound quantity and numeric-comparison requirements,
  private ledger design and fictional acceptance cases in this change. No
  corpus record, source right, comparison output or runtime code changed.
- [ ] Owner/editorial review: choose permitted conversions, materiality,
  calculation reviewer, rounding and reader-facing Spanish limitations.
- [ ] After P0/P1 review, reconcile with overlapping open OpenSpec PRs and
  specify a concrete private schema, validators and presentation. Test with
  fictional values before any real quantitative claim enters publication.

Validation: requirement/scenario structure and `git diff --check`; CI is
technical evidence only and cannot approve numerical political interpretation.

## P1.7 — Source-language bridge (2026-10-28 draft)

- [x] Reconcile current `origin/main` (`8e2fab4`), draft/conflicting PR #101,
  proposed replacement #166, the four pilot source rows, eight statement
  examples and the 2023 review worksheet. The existing dated translation
  audit identifies a repository-visible evidence gap, not missing private
  review proof. PR #173 addresses numeric comparability, not language review.
- [x] Draft a version-bound language-check requirement and private-to-public
  design with fictional fail-closed cases. No PDF, political answer, review
  mark, source right, application code or public artifact is changed.
- [ ] Editorial/OpenSpec review: decide evidence standard, reviewer
  responsibility/competence and whether the existing dual-human review can
  explicitly carry the language check; inspect any private exact-revision
  evidence without treating this draft as approval.
- [ ] After P0 source/rights and P1 method decisions, specify concrete record
  and validator tasks. Test fictional Catalan-to-Spanish pending/approved
  evidence, material correction, changed source/locator and Spanish-source
  bypass in both static and browser publish sets. Keep real activation behind
  human editorial and separate release gates.

Validation (2026-10-28): the local structure check found one requirement and
five WHEN/THEN scenarios; the four-source/eight-statement repository baseline
parsed and `git diff --check` passed. Focused Python unit tests could not run:
the host has Python 3.11, while `generator.py` requires the project's Python
3.14 syntax. Hosted CI and human translation review are separate. No
implementation task is marked complete by this draft.

## P0.9 — Source-version chronology gate (2026-10-29 draft)

- [x] Reconcile current main's four 2023 pilot source dates and rights, open
  PR #101 and its integration candidate, and the current CI execution state.
  Evidence: `docs/2023-TEMPORAL-PROVENANCE-AUDIT-2026-10-29.md`.
- [x] Draft a version-bound date-evidence requirement, design and fictional
  cases in this change. No real source date, right or approval was changed.
- [ ] Owner/editorial review: decide acceptable chronology evidence and
  precision, reviewers, and treatment of historically unresolved versions.
- [ ] After P0 inclusion/source review and OpenSpec approval, define a private
  evidence schema and fixture tests. Reconcile PR #101/#166 before changing
  its source fields or validators. Never infer dates from URLs or metadata.

Validation: `git diff --check` and a local structure/baseline check. CI is
engineering evidence only; it cannot approve dates, rights or political claims.

## P0.10 — Shared-document attribution draft (2026-10-29)

- [x] Audit the current singular source/programme identity fields and PR
  #101/#166 boundary; draft a version-bound candidature-applicability
  requirement, design and four fictional cases. Evidence:
  `docs/2023-SHARED-DOCUMENT-ATTRIBUTION-AUDIT-2026-10-29.md`.
- [ ] Owner/editorial review: approve the candidature/coalition unit, edge
  evidence and review quorum, and distinct-document versus candidature
  coverage wording. This draft approves no actual mapping or rights use.
- [ ] After P0.2/P0.3 and P1 document-scope reconciliation, specify the exact
  schema and validators using fictional fixtures. Require edge-specific
  invalidation and fail-closed public projection before real data entry.

Validation: repository audit and four fictional requirement scenarios;
`git diff --check`. No implementation, real source or political claim changed.
PR #182 CI run 40858569921 did not execute steps: GitHub annotated both test
jobs with an account payment/spending-limit block. Local structure checks
passed; they are not equivalent to CI or editorial review.

## P0.13 — BNG 2023 document discovery (2026-10-30)

- [x] Record the official archive's three distinct 2023 general-election
  document leads and their observed response metadata without importing PDFs
  or promoting them to verified source records. Evidence:
  `docs/2023-BNG-SOURCE-DISCOVERY-2026-10-30.md`.
- [ ] Owner/editorial review: decide 2023 candidature applicability, the three
  document roles and derivative relationship, exact-byte source identity,
  publication dates, rights and any annex/replacement scope. No topic absence
  or political-content approval follows from this discovery.

Validation: `python3` assertions passed for the four existing pilot rows, their
pending rights and the distinct 2026 BNG placeholder. Three publisher PDFs
returned `200 application/pdf` to HEAD; retrieval metadata reported 68, 4
and 16 pages. `git diff --check` passed. No private PDF, hash or publication
review was performed; GitHub CI remains separate engineering evidence.

## P1.4 — Qualification fidelity draft (2026-10-30)

- [x] Reconcile `origin/main` `8e2fab4`, four 2023 pilot source rows and the
  open PR #101 gate; draft source-bound qualification scenarios and a private
  review-ledger design. This changes no real source, claim, review, rights or
  public output. PR #101 remains draft, conflicting and without human reviews;
  PR #166 separately attempts its integration and has failing checks.
- [ ] Editorial owners review the materiality test, multi-locator presentation,
  reviewer quorum/disposition and phone-visible qualified-copy rule. No agent
  may resolve these by marking a real record approved.
- [ ] After P0/P1 review and PR #101 reconciliation, specify the concrete
  ledger schema and validator against fictional multi-page, exception,
  unknown-limit and replacement fixtures. Verify dependent comparison and
  quiz invalidation before any real 2023 activation.

Validation for this proposal: structure and whitespace checks only. CI is
technical evidence, not editorial or source-rights approval.

## P0.14 — EH Bildu 23J document discovery (2026-10-31)

- [x] Record the publisher-hosted 23J PDF lead and separate Senate coalition
  context without importing bytes, assigning a programme role or promoting a
  source record. Evidence: `docs/2023-EH-BILDU-SOURCE-DISCOVERY-2026-10-31.md`.
- [ ] Owner/editorial review: decide Congress/Senate candidature applicability,
  document role and completeness, exact-byte identity, date, rights, other
  documents and replacements under the approved inclusion rule. No topic
  absence or political-content approval follows from this discovery.

Validation: local repository assertions, publisher PDF HEAD and article check,
web retrieval metadata, and `git diff --check`. No source PDF, political
statement or public output was changed; CI cannot supply a human decision.

## P1.7 — Extraction-visibility handoff (2026-10-31 draft)

- [x] Audit the current E1.2 artifact boundary and P1.3 search-state gap;
  draft a private range-ledger design and five fictional requirement cases.
  Evidence: `docs/2023-EXTRACTION-VISIBILITY-AUDIT-2026-10-31.md`, this
  change's `design.md` and `specs/editorial-statements/spec.md`. No PDFs,
  claims, rights, source records, renderer or routing changed.
- [ ] Owner/editorial review: approve the visual-inspection protocol, range
  granularity, non-searchable/table handling, alternate processing and reviewer
  quorum. This draft is not a source-quality or negative-finding approval.
- [ ] After P0 and P1.3 review, reconcile a concrete private ledger schema,
  invalidation rules and tests against the approved protocol. Use fictional
  blank, image-only, omitted-column, tool-change and OCR cases before any real
  2023 search conclusion is considered.

Validation: `git diff --check` and local document-structure checks only. CI
and fixture tests cannot replace human inspection or editorial review.

## P1.8 — Pairwise inference boundary (2026-11-22 draft)

- [x] Reconcile current main's 2023 register and unpublished example records,
  draft PR #101, merged PR #166, and the pair-keyed generator; draft a
  no-transitive-inference requirement, design and fictional scenarios.
  Evidence: `docs/2023-PAIRWISE-INFERENCE-AUDIT-2026-11-22.md`.
- [ ] Editorial/OpenSpec review: settle policy-question identity, display
  wording for more than two parties, direct-pair reviewer quorum and
  correction dependencies. No real relationship approval is implied.
- [ ] After P0/P1 gates and review, define a private relationship-ledger
  schema and test the approved rule with fictional three-party fixtures in
  static and browser projections before any 2023 activation.

Validation for this draft: document-structure and whitespace checks passed.
Existing comparison regression tests could not run here: this workspace has
Python 3.11 only, while the generator uses Python 3.14 syntax; `pytest` is not
installed in the system interpreter. CI cannot supply source rights or
political interpretation.
