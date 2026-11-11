# 2023 language-variant coverage handoff — 2026-11-11

Roadmap package: **P0.18**, proposal-only document-inventory method under
`2023-corpus-completion`. This is a repository audit, not a verified translation,
source-rights decision, programme claim, or approved coverage count.

## Reconciled boundary

- Fetched `origin/main` is `488b6f5`. Draft PR #101 is open at `f8506a1`,
  conflicts with main and has no GitHub reviews. Its older passing checks do
  not test current main. PR #219 separately audits its technical supersession
  by merged PR #166; this package does not replay or resolve #101.
- The 2023 register has four pilot rows (PP, ERC, PNV, Sumar). Every row is
  `published-unverified`, has `not_reviewed` rights and a null publication
  date. The register/schema have a language field but no explicit relation
  between distinct-language document versions. These four rows are not an
  approved candidature denominator or a complete document inventory.
- Draft PR #210 records publisher-page leads for Spanish and Basque EAJ-PNV
  23J PDFs under one publisher document ID, with different URLs and reported
  lengths. This audit did **not** retrieve either PDF or recheck those pages;
  the shared page ID and HEAD metadata do not prove content equivalence,
  identity, date, replacement, rights or page alignment.
- Open PRs #221–#224 and #226–#228 address acquisition, use rights, discovery,
  policy-question identity and integration/CI boundaries. P0.18 addresses
  only how language variants enter document and coverage accounting; it does
  not change those PRs' records or decisions.

## Proposed handoff

Inventory each language file as its own exact document version. Record a
separate, reviewable relationship that says whether versions are translations,
partial adaptations, independent documents, or unresolved; preserve the
evidence, reviewer and revision. Do not infer equivalence from a shared site
ID, title, URL path or file size. Count a reviewed translation family once
for *document-role breadth* only if the owner approves that count; still
report each version and its search/rights state separately. A pending family
must not erase an unsearched version or create a `not stated` conclusion.

Page/section locators, source authenticity, permitted use and claim-language
checks remain version-specific. If a Spanish summary uses a non-Spanish
version, its language bridge requires its own human review. A change to either
file or the family decision invalidates affected coverage and derived claims
for re-review, without automatically invalidating unrelated versions.

The attached OpenSpec delta gives fictional acceptance cases and owner
decisions. No PDF, source row, statement, relationship, reviewer record,
public artifact or routing changed. CI and structural checks are engineering
evidence only, not human editorial or legal review.
