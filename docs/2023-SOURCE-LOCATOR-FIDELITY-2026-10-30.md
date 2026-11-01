# 2023 source-locator fidelity handoff — 2026-10-30

Roadmap package: **P1.2**, proposal-only within `2023-corpus-completion`.
Election: `es-gen-2023`. Baseline: `origin/main` at `8e2fab4`. This is a
repository-record audit and a proposed review contract, not a verification of
remote PDFs, approval of a citation, rights decision, or implementation gate.

## Reconciled boundary

- `content/sources/register.json` has four 2023 pilot sources (PP, ERC, PNV,
  Sumar). They remain `published-unverified`, with rights `not_reviewed` and
  unknown publication dates. This is not a complete candidature inventory.
- The eight 2023 statement examples have numeric `source_page` values and
  registered direct-PDF URLs. Six are `under_review` and two are `draft`; none
  is a published citation. Six section descriptions distinguish a printed
  page label from a different physical PDF page. The pilot review pack calls
  its page ranges search candidates, not accepted citations.
- `StatementRecord.validate()` requires a page **or** section for a proposal,
  but does not define whether `source_page` is a physical PDF page or a printed
  label. `render_source_citation()` and the browser projection append
  `#page=<source_page>` when the URL has no fragment. They do not verify that
  the URL currently serves the reviewed bytes, is a PDF, or honours that
  fragment. A locator can be structurally present without a verified reader
  journey to the exact source passage.
- PR #101 remains open, draft and conflicting, with no GitHub reviews. PR
  #166 proposes a separate integration candidate. Neither is a locator
  approval; do not merge both versions of the pilot gate. Recent CI jobs fail
  before runner steps start, so those runs do not establish integrated tests.

This packet does not repeat source identity (#155), document discovery (#165),
version chronology (#181), language bridge (#174), or mobile source navigation
(#131/#171). It addresses the narrower join from an **approved exact source
version and physical passage** to the **reader-facing link and locator label**.

## Proposed P1.2 requirement delta for editorial/OpenSpec review

1. A reviewed proposal locator binds the election, source ID, immutable
   version/hash, physical PDF page or stable source section, and any printed
   page label **as separate fields**. An extractor's page number is only a
   candidate until a human checks the original page and surrounding context.
   The review evidence records the exact statement revision and source
   passage; a valid-looking number is not citation approval.
2. The public citation uses a reviewed HTTPS landing or direct-document URL
   associated with that exact source version. A PDF fragment may be emitted
   only for a positive, verified physical PDF page and a compatible direct-PDF
   target. Printed labels and section-only locators remain readable text; they
   are not silently converted into PDF fragment numbers. A link landing at a
   document rather than the exact page must not be described as tested deep
   navigation.
3. A changed or unreachable remote target is a link-health finding, not proof
   that the source, proposal or programme ceased to exist. Preserve the
   checksum-bound private original and old citation history. Escalate a
   replacement, redirect to different bytes, or ambiguous section to source
   and editorial reviewers; do not rewrite an approved citation in place or
   link publicly to the private archive.
4. The static and browser projections must use the same approved locator and
   fallback wording. The publication gate fails closed when an exact source
   passage cannot be bound; source-link checks and UI tests are engineering
   evidence, not a substitute for rights or editorial review.

## Fictional acceptance cases for a later reviewed design and tests

| Fixture | Required result |
|---|---|
| PDF physical page 5 has printed label 3 | Citation says which number is which; `#page=5` only on a compatible direct-PDF URL. |
| Section-only source on an HTML landing page | Keep the reviewed section label; no invented `#page=` fragment or PDF-page claim. |
| Direct URL redirects to different bytes | Flag source-version recheck and withhold changed-target approval; retain old hash and review trail. |
| Same-version PDF link is temporarily unavailable | Show a truthful source-access limitation and retain provenance; do not infer a missing political position. |
| Replacement PDF moves the passage to another page | Preserve the earlier citation; invalidate dependent locator/statement/relation reviews until the new passage is checked. |
| Static HTML and browser disagree on page label or URL | Reject the projection rather than ship inconsistent citations. |

## Review and implementation handoff

- Editorial owners decide the locator review evidence, whether a landing-page
  fallback is acceptable for each source, and reader-facing wording when the
  direct link is unavailable. Source/rights owners separately confirm the
  exact version and permitted use. No agent can approve these decisions.
- Add reviewed P1.2 requirements, design and tasks to the
  `2023-corpus-completion` OpenSpec change after reconciling open PRs that edit
  its artifacts. Then implement with fictional fixtures and static/browser
  parity tests. Real 2023 citations still need human page and context review.
- No source record, PDF, extract, statement, relationship, rights state,
  public artifact, routing or deployment is changed by this packet.

Reproduce this audit from `content/sources/register.json`,
`content/examples/statements/*2023*`,
`docs/pilot-review/2023/README.md`, `src/elecciones2026/schemas.py`, and
`src/elecciones2026/generator.py`. It does not contact party websites or read
private source bytes.
