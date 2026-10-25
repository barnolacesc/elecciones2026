# 2023 source-locator verification handoff — 2026-10-24

Roadmap package: **P1.1-L** (`2023-corpus-completion`, proposal-only).
Scope: exact-source locator evidence for the 2023 pilot and a future complete
corpus. This is a repository-record audit and draft acceptance contract, not a
PDF recheck, political interpretation, rights decision or implementation.

## Reconciled baseline

Checked `origin/main` at `77de048` and open PRs on 2026-10-24. The product
roadmap prioritizes source-verified 2023 comparison. The current source
register has four 2023 pilot rows (PP, ERC, PNV, Sumar); each is
`published-unverified`, has `rights_review.status=not_reviewed`, and has no
evidenced publication date. There is no approved complete 2023 candidature
manifest. The private pilot inventory has page-count and candidate page
metadata, but its `visual_review_status` never denotes completed human review.
The eight 2023 statement examples are six `under_review` and two `draft`.

| Check against repository records | Result | Meaning |
|---|---:|---|
| Statement `source_url` and `source_version` join a 2023 register row | 8/8 | Metadata join only; not source authenticity. |
| `source_page` parses as an in-range PDF page for that inventory source | 8/8 | Bounds check only; not proof of claim on page. |
| Page appears among that source/topic's candidate locator rows | 8/8 | Candidate discovery only; not full-topic search or approved citation. |
| Candidate rows marked `automated-visual-inspection-human-review-pending` | 6/8 | Automated indication explicitly leaves human page review pending. |
| Candidate rows marked `pending` | 2/8 | No visual inspection approval is recorded. |
| Registered source rights reviewed / publication date evidenced | 0/4 / 0/4 | Neither URL access nor hash grants reuse or establishes a date. |

The join is reproducible from `content/sources/register.json`,
`docs/pilot-review/2023/inventory.json`, and
`content/examples/statements/statement-2023-*.json`. It does not read or
redistribute PDFs or extracted political text. PR #101 remains draft with no
GitHub review; its six PP/ERC page rechecks, source-use decisions and date
evidence remain open. PR #126 separately audits its merge conflicts. This
package does not alter or resolve either PR.

Current `source_page` is a nullable free-form string in
`content/schemas/statement.schema.json`. `StatementRecord.validate` requires
a page **or** section for an explicit position but does not test a PDF page
against immutable source bytes or a human locator decision.
`render_source_citation` and the browser payload append `#page=<source_page>`
when a page exists. That fragment is a navigation hint, not evidence that a
reader's viewer opened the right page or that a printed page label equals the
PDF page index. Some pilot inventory rows distinguish the two labels; both
must remain identifiable.

## Draft requirement delta for editorial/OpenSpec review

Add to `2023-corpus-completion`'s `editorial-statements` capability after
reconciling concurrent proposal PRs:

> A publishable statement SHALL bind its source locator to the exact
> `election_id`, source ID, immutable source hash/version, PDF page index or
> stable section, and reviewed statement revision. A human locator check SHALL
> record which immutable source bytes and page/section were inspected, the
> reviewer and decision reference, and whether the cited measure and material
> qualifications are present there. A generated link fragment, topic-search
> candidate or bounds check SHALL NOT satisfy this decision. An unknown,
> mismatched, replaced or unreviewed locator SHALL fail closed for that claim.

This adds locator evidence; it does not replace independent source authenticity,
rights, neutral-summary, relationship or publication reviews. `link_only`
rights do not authorize a quote, and a visually correct page does not authorize
paraphrase or PDF redistribution. The final reviewer/quorum and evidence-store
rules remain owner/editorial decisions.

### Required scenarios before implementation

1. A valid PDF page index with no human page decision stays unpublished.
2. A printed label differs from the PDF page index: the internal evidence keeps
   both; public wording and the link identify the correct coordinate without
   claiming the fragment was browser-tested.
3. A source hash or document replacement changes: old locator decisions and
   dependent statements/relationships become stale, while old evidence remains
   in the correction trail.
4. A reviewed page contains an initiative but omits a qualification continued
   on the next page: the statement cannot pass until the cited scope covers the
   qualification.
5. A section-only web document uses a stable, human-checked section reference;
   a free-form label or an unrelated same-named section is insufficient.
6. A candidate locator belongs to another election, source version or topic:
   a syntactically valid page number cannot satisfy the join.

## Draft design and task handoff

- Private locator decisions should reference immutable source/archive IDs and
  statement revisions, with PDF page index and printed label stored separately.
  Keep source bytes, rendered pages and reviewer evidence outside Git and the
  static build. The build receives only the reviewed locator outcome and safe
  citation metadata.
- The future validator should check exact source/version/hash and locator
  decision joins, invalidate dependents on source/statement correction, and
  distinguish machine-checkable bounds from the human content check. The
  reader flow should test each approved outbound citation on representative
  mobile browsers and provide a readable page/section label if a PDF viewer
  ignores `#page`.
- First, owner/editorial reviewers must agree the locator-check protocol,
  private evidence-store policy, who may sign it, and how multi-page measures
  are represented. Then revise the OpenSpec spec/design/tasks and PR #101
  reconciliation plan. Only after review should a fictional-fixture validator
  and tests be implemented; real 2023 locator decisions stay human-owned.

**Exit remains open:** no page, source-rights or political-content approval was
created here. Complete P0 coverage and rights, PR #101 reconciliation, P1
statement/relationship reviews, and mobile citation checks remain separate
gates. Passing CI is engineering evidence, not human editorial review.
