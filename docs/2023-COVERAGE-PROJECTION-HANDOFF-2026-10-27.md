# 2023 coverage projection handoff — 2026-10-27

Roadmap package: **P0.5**, `2023-corpus-completion` (proposal-only). Baseline:
`origin/main` `8e2fab4`. This is a draft requirement, design and task handoff
for a future coverage snapshot. It does not approve a candidature rule,
source right, topic absence, political claim, comparison or release.

## Reconciled evidence and boundary

- The current register contains four `es-gen-2023` pilot source rows (PP, ERC,
  PNV, Sumar). All are `published-unverified`, have rights `not_reviewed`, and
  have `publication_date: null`. Four programme examples share the unverified
  state. Eight 2023 statement examples are six `under_review` and two `draft`;
  six relationship examples are `invalidated`. These are record counts, not
  a reviewed corpus or the number of eligible candidatures.
- `content/taxonomy.json` version `1.0.0` is scoped to `es-gen-2026`. No
  approved 2023 candidature manifest, document-set revision or 2023 taxonomy
  applicability decision exists in the repository. Current 2023 source cards
  show pilot records, not an audited completeness denominator.
- Draft PR #101 is still conflicting and unpublished. PRs #149, #150, #151,
  #155, #157 and #158 address rights withdrawal, document scope, relation
  collisions, source identity, correction dependencies and initiative lineage.
  This package does not edit their decision records or implement their gates.
  PR #156 separately audits #101 integration; this handoff does not resolve it.
- GitHub Actions run `40300408011` for PR #156 did not start its test/browser
  jobs because of the account payment or spending-limit block documented in
  that PR. A missing CI result is not a failed test or editorial review. The
  local evidence here is limited to Git data,
  register/example records and the current generator; no PDF, private review
  evidence or political source was inspected.

## Draft requirement for owner/OpenSpec review

A coverage projection for `es-gen-2023` **SHALL** identify the election ID,
snapshot date, approved inclusion-rule revision, authoritative manifest
revision, relevant document-set revision, taxonomy revision and independently
reviewed source/rights/topic/statement/relation stages. It **SHALL NOT**
describe source discovery, byte verification, lawful reuse, reviewed claims
and reviewed comparisons as one interchangeable “covered” count. Every count
must name its unit and denominator: candidatures, document versions,
candidature-topic search units, approved statements or approved relationship
operands. Unknown and invalidated units remain visible in the underlying
ledger and cannot be dropped from the denominator merely because they are
unavailable for publication.

Until the human-approved rule and reconciled manifest exist, the public
projection **SHALL** use a bounded pilot/unresolved-scope label. It may report
the number of registered pilot documents with that exact label, but **SHALL
NOT** show a percentage, “all parties/programmes”, or an implicit complete
party list. A topic with no candidate extraction is not `not stated` unless
the relevant document set, search scope and negative finding have separately
passed human review. A reviewed statement does not make a relationship or
the entire topic complete. A rights grant for a document does not authorize
quotations, PDF redistribution or claims outside its exact reviewed use.

### Fictional acceptance cases

1. Four pilot source rows and no approved manifest yield `scope_unresolved`;
   the public view cannot calculate `4 / all 2023 candidatures`.
2. One included fictional candidature has a general programme and an annex;
   candidature coverage counts it once, document coverage counts two versions,
   and pending annex rights/search remain separate.
3. An approved source link with pending paraphrase rights and a reviewed
   statement contributes to the source stage, not to publishable claims.
4. Two approved statements with no independently approved relationship may
   appear only under the separately approved single-party display rule; they
   cannot count as a reviewed cross-party comparison.
5. Replacing one source version preserves the old snapshot and marks affected
   locators, topic searches, claims and relationships invalidated in the new
   snapshot; stale approval counts cannot carry forward.
6. A search with zero extractor hits but an unsearched relevant annex remains
   partial; neither `not stated` nor disagreement is permitted.

## Draft design and work order

1. Start from the owner-approved P0 inclusion manifest and document-to-
   candidature join, not the current four-row register as a denominator.
   Record immutable input revisions, stage-specific decisions and unresolved
   rows in a private reconciliation snapshot. Do not copy PDF text, private
   evidence, reviewers' notes or political answers into Git or the build.
2. Derive a minimal public projection only from approved metadata. Keep
   election, as-of date, scope label, unit definitions, unknown/partial states
   and revision identifiers visible. Do not expose raw private decision
   evidence. An absent approved projection fails closed to the pilot label.
3. Recompute on inclusion-rule, source-set, taxonomy, rights or content
   revision. A diff report lists added, removed and invalidated units before
   any reader-facing count changes; a previous static artifact must not be
   treated as fresh evidence.
4. After the formal OpenSpec delta and owner decisions are reviewed, test the
   six fictional cases at both data and rendered-output boundaries, including
   a 360/390/430-px readable coverage explanation. Then connect real records
   only after source, rights, topic and editorial gates pass. No implementation
   or public-copy change belongs to this proposal-only handoff.

**Human decisions required:** the 2023 inclusion and coalition unit; the
authoritative manifest/finality protocol; what a “covered” candidature and
document mean; source/rights and negative-search reviewers; the public wording
for unknown, partial and invalidated states; and whether any coverage
percentage is appropriate after a denominator is approved. The P0.1/P0.2
inventory contract, P1.3 search gate and P1.2 comparison-set gate remain
independent prerequisites. Passing a fixture test cannot make these decisions.

Reproduction: inspect `content/sources/register.json`,
`content/examples/{programmes,statements,relationships}/*.json`,
`content/taxonomy.json`, `src/elecciones2026/generator.py` source-card
rendering, `openspec/changes/2023-corpus-completion/`, and GitHub PR/Actions
metadata as of this date. No source bytes or live political content changed.
