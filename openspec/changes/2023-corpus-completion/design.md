# Design: P0.1 2023 inventory and rights contract

Status: draft for owner/editorial review. This design does not authorize an
inventory rule, rights decision, political claim, implementation or release.

## Scope and boundary

This package specifies the P0 inventory handoff for `es-gen-2023`. It does not
extract initiatives, change source records, import PDFs, or alter the live
comparator. P1 proposal and relationship modelling will need a subsequent
reviewed design. The existing four-party pilot is input evidence, not the
denominator for a complete 2023 corpus.

## Decisions proposed for review

1. **Freeze the denominator before counting coverage.** An owner-approved,
   versioned inclusion-rule record names the election, objective eligibility
   test, authoritative election/candidacy evidence, territorial treatment,
   coalition treatment, exceptions and approvers. A separate candidature
   manifest enumerates each qualifying candidature, official ballot name,
   stable ID, constituencies and evidence. Agents can prepare candidates but
   cannot mark this rule or list approved. A list of parties in a source
   register is not, by itself, an inclusion rule.
2. **Inventory documents separately from candidatures.** A candidature may
   have a general programme, territorial annexes, coalition documents,
   revisions or no located programme. A document-discovery row records its
   role and scope, publisher, official landing/direct URL, dated access
   evidence, language, source version, checksum when bytes exist, private
   archive reference, publication-date evidence, replacement chain and
   verification state. Unknown dates stay null. Search attempts and unresolved
   candidates are retained; an unlocated document is not proof that none
   existed.
3. **Keep three independent gates.** Source authenticity/integrity, reuse
   rights and editorial approval are separate. A rights decision identifies
   the exact source/version, permitted use (link, paraphrase, short quote,
   redistribution), deciding human, date and private evidence reference.
   `not_reviewed` remains the default. A link or checksum cannot become quote
   permission; a content review cannot decide rights.
4. **Make coverage a reproducible join.** For each included candidature,
   account for relevant document rows and an explicit source-coverage state.
   Report counts against the frozen candidature manifest and document
   inventory, not against currently imported PDFs. A topic-level `not stated`
   conclusion is unavailable until the relevant source scope and search have
   been reviewed. Preserve unknown/incomplete states in private reports and
   eventual reader-facing limitations.

## Data flow

Owner-approved inclusion rule -> evidenced candidature manifest -> document
discovery and private source archive -> source/rights review -> coverage
reconciliation -> P1 extraction queue. The public static build receives only
approved metadata and reviewed content; original PDFs, extracted text, page
renders and private approval evidence stay out of Git and serving artifacts.

## Reconciliation and invalidation

The inventory report records the rule version, input revisions, election ID,
counts and unresolved rows. A changed inclusion rule or newly found document
invalidates prior coverage totals. A changed source hash/version or replacement
invalidates dependent page anchors and P1 statements/relationships for review;
it must not silently rewrite old versions. CI can check joins and fail-closed
states, but cannot resolve authenticity, rights or political interpretation.

## Open owner/editorial decisions

- Select and evidence the 2023 eligibility rule, including regional lists and
  coalition versus member-party granularity. Do not copy the 2026 candidate
  rule without an explicit 2023 decision.
- Name the owner of source authenticity, rights, taxonomy and coverage review,
  plus the private evidence store and retention/access policy.
- Decide whether unknown publication dates can be handled under a narrower
  private-only workflow; never fabricate a date to satisfy a schema.

## Alternatives rejected for this draft

- Treat the four registered PDFs as all 2023 programmes: no inclusion-rule
  evidence supports that denominator.
- Treat an official URL, local hash or successful CI as rights approval: these
  establish neither legal reuse nor human editorial acceptance.

## P1.1 draft — initiative and comparison method

This section is a separate, proposal-only P1 method package. It depends on the
P0 candidature/document manifest and rights decisions above; it does not
approve that manifest, any statement, any relationship, or implementation.

### Units and evidence flow

1. Preserve candidate extraction as a private queue keyed to election ID,
   candidature, document version/hash, PDF page or stable section, taxonomy
   version, and extraction run. Record the source's wording privately, but do
   not put PDF text, page renders, or unreviewed quotes in Git or a public build.
   One candidate represents one actionable measure. Record actor, action,
   instrument, target/beneficiary, jurisdiction, conditions, amount and timing
   **when the document states them**; unknown fields remain unknown. Broad aims
   and slogans remain candidates for classification, not automatically proposals.
2. Separate four decisions: source/rights acceptance (P0), candidate-to-proposal
   interpretation, neutral public summary, and cross-party relationship. Bind
   each approval to an immutable record version and evidence reference. Existing
   dual-human statement review remains mandatory; relationship reviewers must
   approve the exact paired statement versions and the stated grounds separately.
   A reviewed statement is not a reviewed relationship.
3. Make topic coverage an auditable matrix over the approved candidature list,
   relevant document versions, and taxonomy. Track search scope, pages/sections,
   search method, review state and unresolved exclusions. Distinguish unsearched,
   partly searched, searched with candidates, and searched with no supported
   candidate. `not_found`/`not stated` requires an approved relevant-source
   search; it is never inferred from an empty extraction queue. Counts label
   their denominator and review stage and are not called exhaustive while any
   required document or topic remains unresolved.
4. A relationship begins with a specific policy question and a pair of
   source-linked statements in the same election. Reviewers compare actor,
   action/instrument, beneficiary, geography/jurisdiction, conditions,
   magnitude, funding and timing where stated. They select agreement,
   divergence or partial overlap only with explicit grounds and caveats.
   A single-party measure is a display grouping, not evidence that another
   party disagrees. A missing or unsupported position cannot be an agreement
   or divergence operand.

### Publication projection and invalidation

The deterministic public projection contains only approved source metadata,
approved summaries, qualifications, exact outbound source locators, reviewed
relationships, and honest coverage limitations. It excludes candidate queue
text, private evidence and unapproved claims. It does not turn `link_only` into
quotation permission. A changed source version/hash, taxonomy classification,
statement content or review disposition invalidates dependent locators,
coverage conclusions and relationships until re-reviewed. Corrections retain
the superseded record and affected IDs; rebuilding cannot silently revive an
invalidated relation. Cross-election joins fail closed.

### Fixtures and review decisions before implementation

Use fictional fixtures for: a composite sentence split into two measures; a
cross-topic measure with a documented primary instrument; an absent amount
left unknown; a partial programme with unsearched annex; similar slogans but
different instruments; equal instrument with different eligibility; a searched
topic with no supported candidate; a source replacement; and a correction that
invalidates a relationship. Tests must check both static and browser publish
sets, including no false `not stated` or inferred disagreement.

Editorial owners still need to set the accepted search protocol and stopping
rule for each document/topic, the proposal-granularity arbitration process,
the relationship-review quorum/segregation rule, and reader-facing coverage
wording. These are review questions, not agent decisions. The existing 2026
methodology is a reference; its 2026 inclusion rule does not become a 2023 rule.
