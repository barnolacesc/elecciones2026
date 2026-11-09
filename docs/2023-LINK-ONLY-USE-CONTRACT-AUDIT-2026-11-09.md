# 2023 source-use vocabulary conflict — 2026-11-09

Roadmap package: **P0.17**, proposal-only source-use contract reconciliation
under `2023-corpus-completion`. This is not a legal rights decision, a change
to a source record, or permission to publish a summary.

## Reconciled evidence

- `origin/main` `488b6f5` contains the technical gate integrated by merged
  PR #166. Draft PR #101 remains open, conflicting and without GitHub reviews;
  PR #219 separately owns its supersession/disposition. Its 2026-10-12 green
  checks do not test the current tree or certify editorial decisions.
- The four `es-gen-2023` pilot sources (PP, ERC, PNV, Sumar) are all
  `published-unverified`, `rights_review.status=not_reviewed`, with unknown
  publication dates. Six 2023 statements are `under_review`, two are `draft`,
  and six relationships are `invalidated`. These are repository counts, not
  complete 2023 coverage or a publishable comparison.
- `src/elecciones2026/editorial.py` includes `link_only` in
  `PERMITTED_SUMMARY_RIGHTS`. The strict 2023 validator in `generator.py`
  therefore accepts a quote-free summary when its other gates pass, and
  `tests/test_pilot_editorial_audit.py` tests that behavior. The public status
  label is “Solo resúmenes y enlaces; sin citas”.
- By contrast, the draft P0 provenance requirement **Current rights decision
  and withdrawal propagation** says an outbound-link decision SHALL NOT
  authorize paraphrase. `docs/2023-SOURCE-USE-DECISION-QUEUE-2026-10-23.md`
  likewise requests separate link, paraphrase, quote and redistribution
  decisions. The PR #101 reuse handoff proposes neutral summaries plus links
  under `link_only`, but explicitly says that human source-specific decisions
  remain pending. This is a contract/vocabulary mismatch, not evidence that
  any right has been granted or a public claim has escaped the gate.

## Decision for the rights owner and editorial owners

Choose and record one version-bound, use-specific contract before a real 2023
source can move out of `not_reviewed`:

1. Keep `link_only` literal: it permits an outbound link only. Model neutral
   paraphrase as a separate explicit permission/decision, with its own scope
   and private evidence reference; rename the public label accordingly.
2. Explicitly redefine a combined status (prefer a name that says both uses)
   for *summary plus link*, subject to a human decision for those exact uses.
   Keep link-only distinct. Migrate schemas, validator, test fixtures and
   Spanish labels together, without converting existing decisions implicitly.

The rights owner must decide what lawful reuse is permitted for each exact
source version; the editorial owners must review the summary and its source
locator independently. Unknown publication dates, source authenticity,
coverage, statement reviews and relationship reviews remain separate gates.
No CI result can make these decisions.

## Proposed fail-closed acceptance

- A fictional source approved for **link only** may display the outbound link,
  but cannot publish a paraphrase, quotation or PDF copy.
- A separate, exact-version human decision for **summary plus link** may make a
  quote-free summary *eligible* for the other source/editorial gates; it never
  permits quotation or PDF redistribution.
- A narrower or withdrawn use decision invalidates affected summaries and
  comparisons, while retaining prior decisions in the private audit trail.
- The validator, source register/programme status, public label and tests must
  express the same approved use scope. A status name or free-text note cannot
  silently widen permission.

The current four pending source records stay unchanged. This audit did not
open private PDFs or decision evidence, retest publisher pages, resolve PR
#101, or run a public release. PRs #221–#222 address acquisition and discovery
evidence, not this use-vocabulary conflict. Current main CI is red; local
structure checks are not hosted CI or human review.
