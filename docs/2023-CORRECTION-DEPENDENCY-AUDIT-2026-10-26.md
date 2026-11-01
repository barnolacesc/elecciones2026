# 2023 correction dependency handoff — 2026-10-26

Roadmap package: P1.4 (`2023-corpus-completion`). Proposal-only audit of the
private repository at `origin/main` `8e2fab4`. It does not approve a political
correction, source right, review record, OpenSpec implementation or release.

## Reconciled baseline

- The source register contains four `es-gen-2023` pilot rows (PP, ERC, PNV,
  Sumar), each `published-unverified` with rights `not_reviewed`. The eight
  2023 statement examples are six `under_review` and two `draft`; six 2023
  relationship examples are `invalidated`. There is no 2023 correction example
  in `content/examples/corrections/`. These are pilot-record counts, not a
  complete candidature denominator or a publishable corpus.
- Draft PR #101 (`f8506a1`) remains open and `CONFLICTING` with main. Its
  2026-10-12 green checks do not test a resolved branch and do not establish
  source rights or human review. PR #156 already audits that integration gate;
  this handoff neither resolves nor repeats its nine-file conflict analysis.
- Main's 2026-10-25 CI ran against `8e2fab4`: test, mobile and container jobs
  passed; the fork-isolation/deploy-protection job failed with no reported
  steps and release was skipped. Open documentation PR checks on 2026-10-26
  also fail before useful steps. This audit does not assign an unverified
  cause or treat CI as editorial approval.

## Observed contract boundary

`content/schemas/correction.schema.json` supports a target type and an explicit
list of invalidated relationship IDs. `schemas.py` validates correction shape
and offers direct relationship invalidation. `editorial.py` has a correction
application helper and a build gate, while `generator.py` loads corrections
for rendering. Inspection does not establish a 2023-wide transitive closure
over topic-search findings, comparison-set accounting and provisional quiz
citations, or an enforced parity check between static and browser publish sets.
The existing draft P1 requirements already call for dependent invalidation;
P1.4 makes the review transaction and acceptance boundary explicit.

## Review handoff

The proposed design and `programme-comparison` requirement cover exact-version
impact accounting, withholding, separate human re-review and fictional tests.
Before implementation, owners must settle correction severity, source-rights
withdrawal behavior, reviewer roles and reader-facing partial-coverage copy.
The approved P0 candidature/document scope, taxonomy and PR #101 integration
remain prerequisites. Do not infer a negative party position from a withheld
claim, or copy source bytes, reviewer evidence or quiz answers into Git.

Reproduction: inspect `content/sources/register.json`, the 2023 examples,
`content/schemas/correction.schema.json`, `src/elecciones2026/{schemas,editorial,generator}.py`,
GitHub PR #101 and main CI run `40179863768`. No private PDFs were opened.
