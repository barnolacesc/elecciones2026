# 2023 source-to-Spanish translation traceability audit

Roadmap package: **P1.1-T**, a proposal-only editorial handoff under
`2023-corpus-completion`. Snapshot: `origin/main` at `fe5e05e` on 2026-10-24.
This is a repository-record audit, not a review of original PDFs, private
approval evidence, translation quality, source rights, or political meaning.

## Observed boundary

- The `es-gen-2023` source register has four pilot documents: three marked
  `es` and one ERC document marked `ca`. All four remain
  `published-unverified`, with rights `not_reviewed` and publication dates
  unknown. These four are not an approved 2023 candidature denominator.
- The eight 2023 statement examples include three ERC summaries in Spanish;
  six statements are `under_review` and two are `draft`. The ERC examples
  identify source version, PDF page, and Catalan section. Their record schema
  has no separate source-language, translation-review, or translation-evidence
  field. That is a **repository-visible traceability gap**, not proof that a
  private reviewer did or did not check the wording.
- `docs/pilot-review/2023/review-form.md` asks for language and Spanish
  translation checks and for reviewers to confirm that translation preserves
  meaning. The OpenSpec P1 draft binds candidates to source version/page and
  calls for neutral summaries, but does not yet specify how a multilingual
  source-to-Spanish decision is retained and invalidated independently.
- Draft PR #101 changes the six PP/ERC summaries and editorial gates, is
  conflicting with current main, and has no GitHub review decision. Its older
  green checks cannot establish translation or editorial approval. This audit
  does not edit its records, resolve its conflicts, or change publish state.

Inputs inspected: `content/sources/register.json`,
`content/examples/statements/statement-2023-*.json`,
`content/schemas/statement.schema.json`, `docs/pilot-review/2023/review-form.md`,
the `2023-corpus-completion` proposal/specs/design/tasks, and GitHub PR #101.
No source text or political position was copied into this audit.

## Proposed P1 requirement for editorial/OpenSpec review

A Spanish public summary derived from a non-Spanish source should retain an
auditable language bridge bound to the exact source version and locator, the
exact Spanish statement revision, and a human decision/evidence reference.
The decision should identify whether material qualifiers, jurisdiction,
amounts, timing, and terms of art survived translation. A source link alone,
two generic statement approvals, or CI should not silently stand in for an
explicitly evidenced language check. The owner must decide whether this is a
separate reviewer decision or an explicit part of the existing dual-human
review; this audit does not set a new quorum or claim any reviewer competence.

### Draft design and fail-closed cases

1. Keep original-language snippets and translation working notes only in the
   private review store. A public projection may contain the approved Spanish
   summary and exact outbound citation, not unreviewed source text.
2. Record source language, output language, source ID/hash/version and physical
   page/section, statement revision, review disposition, reviewer/date and
   private evidence reference. Do not infer language from party identity or
   auto-approve because a schema field is present.
3. If a Catalan-source summary has no retained language-check decision, leave
   it out of the publishable set even if source byte integrity passes. If a
   later reviewer corrects a material translation, version the statement and
   invalidate its dependent comparisons and quiz mappings for re-review.
4. If the source PDF hash or locator changes, recheck the language bridge and
   dependent claim. A Spanish-source record should follow normal statement
   review; this package should not require a fictitious translation approval.

Use fictional multilingual fixtures for these cases after the requirement,
design and tasks are reviewed. The acceptance test should inspect both the
static and browser publish sets and confirm that an unresolved language check
cannot become a public claim. No real ERC statement, source, right, review mark
or deployment should change in that implementation package.

## Decisions and next tasks

1. Editorial owners decide the language-check evidence standard, reviewer
   responsibility, and whether the current private review files already
   satisfy it for any exact statement revision. No approval is inferred here.
2. Reconcile the decision with PR #101 and the existing dual-review contract;
   then draft/review the corresponding OpenSpec spec, design and tasks before
   any schema or validator implementation. Keep this package separate from the
   open P0 inventory/rights, P1 comparison-set, taxonomy and P2 source-journey
   PRs.
3. Only after P0 source/rights gates and exact-content review, validate real
   multilingual summaries and downstream comparison/quiz dependencies. Public
   release remains a distinct owner decision.

Local audit validation: parsed the 2023 register and eight statement examples
with Python 3; inspected the statement schema and review worksheet. This
document changes no application code, public content or editorial state.
