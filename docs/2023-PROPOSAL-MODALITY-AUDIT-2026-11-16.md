# 2023 proposal-modality handoff — 2026-11-16

Roadmap package: **P1.1**, `2023-corpus-completion` (proposal-only).
Baseline: `origin/main` `d13ba683` after fetch on 2026-11-16. This audit
inspects repository contracts and GitHub metadata only. It does not inspect
private PDFs or establish that any real passage is a proposal.

## Observed boundary

- `content/sources/register.json` has four `es-gen-2023` pilot rows. All four
  are `published-unverified` with `not_reviewed` rights. This is not an
  approved 2023 candidature or document denominator.
- The P1.1 editorial spec requires an actionable measure and rejects a broad
  slogan as a concrete proposal. It does not yet require a reviewer to
  distinguish a *future commitment* from a description of past action, an
  existing policy or a diagnosis. Actionable wording
  alone does not settle whether the candidature proposes that action.
- The current statement schema has an `explicit_proposal` output type, but no
  version-bound classification decision distinguishing prospective commitment
  from retrospective or descriptive wording. No real record is reclassified
  by this audit.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  draft and conflicting, with zero submitted reviews. Its historical green
  checks cannot approve its six summaries or resolve this method question.
  Main's latest CI run for `d13ba683` succeeded; that is engineering evidence,
  not source-rights or editorial review.

## Bounded method question

The review queue should retain a version-bound *speech-act and time-orientation*
decision before a passage can become a proposal statement. The reviewer must
identify what the document actually commits to do, if anything, and distinguish
that from a past-action claim, a current-policy description, an aspiration or
diagnosis. A passage may mix these functions; its actionable future part needs
its own exact locator and review. Absence of a future commitment in one passage
is not a topic-level `not stated` finding.

This gate is separate from source authenticity, lawful reuse, initiative
identity, speaker attribution, exact-locator verification, neutral wording and
relationship approval. It does not infer truth of retrospective claims or
judge whether a current policy exists. Private source text and review evidence
stay outside Git and the public build.

## Decisions and acceptance handoff

Editorial owners must decide the allowed classification vocabulary, treatment
of reaffirmations/continuations, reviewer responsibility and whether a
non-proposal passage can appear in a separate, explicitly labelled context
view. Until then, no such passage is promoted as a 2023 proposal. Fictional
fixtures should cover a past-tense achievement, a status-quo description, an
aspiration without an instrument, a mixed retrospective/future passage, and an
explicit continuation commitment. A changed source version or classification
must invalidate dependent summary, comparison, coverage and quiz decisions.

No real source, rights, statement, relationship, build or routing change is
proposed in this PR. CI can validate a later implementation, not decide what a
party meant or clear publication.
