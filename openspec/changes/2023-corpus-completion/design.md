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

## P1.2 draft — comparison-set integrity

This proposal-only method refinement concerns selection and presentation of
already reviewed measures. It does not revise P0 candidature/source evidence,
approve a political relationship, or implement a renderer. The existing
comparison payload groups by measure and currently stores one position per
party in each measure; a relationship record names specific statement IDs.
Those structures alone do not prove that every eligible statement is shown or
that a selected relation represents a party's complete topic position.

For each election/topic/two-candidature view, propose a deterministic set
ledger: eligible approved statement IDs and versions; included measure IDs;
relationship IDs and exact operands; unmatched statement IDs; excluded IDs
with a reviewed reason; source/topic coverage revision; and a completeness
state. The ledger is a private build input/audit output until its schema and
public projection are reviewed. It must not contain source PDF text, private
review evidence or personal political answers. An approved relation describes
only its paired measures. It cannot erase unmatched measures or promote a
partial set into a party-wide agreement summary.

Before implementation, editorial owners must decide the policy-question
granularity, whether one-to-many matches are permitted, when an exclusion is
editorially acceptable, the reviewer for the ledger, and Spanish wording for
partial coverage. If the current one-position-per-party display cannot show
all included measures without loss, the build must fail closed or present an
explicitly limited view under a reviewed rule; arbitrary first/last selection
is not a valid resolution. Use fictional asymmetric fixtures (2:1 measures,
only one reviewed pair), a 2:2 case with one unmatched measure on each side,
and a pending-annex case to check set accounting and bounded copy. Passing
fixture checks cannot approve real completeness or political meaning.

## P0.2 draft — inventory reconciliation handoff

Status: proposal-only, for owner and OpenSpec review. This is a bounded data
contract for the *future* P0 inventory reconciler, not an inclusion decision or
permission to alter source records. It follows P0.1 and does not change the
P1.1 proposal method above.

### Input records and keys

| Record | Required identity and evidence | Pending state |
|---|---|---|
| Inclusion rule | `es-gen-2023`, immutable rule revision, eligibility criterion, authoritative enumeration evidence reference, territorial and coalition treatment, exception policy, human decision reference | Draft/unapproved rules cannot establish a denominator. |
| Candidature manifest row | Rule revision, stable candidature ID, exact ballot/list name, constituencies or scope, official enumeration evidence, inclusion decision and decision reference | Candidate rows remain candidates until reconciled under the approved rule. A party ID is not automatically a candidature ID. |
| Document discovery row | Candidature ID, document role (`general`, `territorial_annex`, `coalition`, `replacement`, or other reviewed role), publisher, official landing and direct URLs when found, language, source ID/version/hash when bytes exist, dated retrieval evidence, publication-date evidence or unknown, private archive reference, replacement link, discovery status | An unlocated document records search attempts and `not_located`; it does not assert that no document existed. A PDF path or local hash is not publication-date evidence. |
| Version-bound review decision | Exact source ID and hash/version, decision kind (`authenticity`, `rights`, or `editorial`), scope of permitted use, human decider, date, private evidence reference | Each kind stays independent and pending by default; a source URL or review of summary wording cannot authorize quotes or PDF redistribution. |

The record names describe a proposed interface, **not** new approved schema
fields. Keep private source bytes, extraction text, page renders and decision
evidence out of Git and the static build. A public projection may contain only
approved metadata and reviewed claims. Unknown values remain explicit; do not
coerce them to a date, a negative search result or an approval.

### Reconciliation output and invalidation

The reconciler should produce a versioned, reproducible snapshot with input
revisions, rule decision reference, enumeration source, included candidature
count, candidature-to-document joins, unresolved document searches, and
separate source-authenticity, rights and topic-search states. Its rows must
distinguish `not_located`, `located_unverified`, `verified`, `partial`, and
`replaced` without equating any of them to topic-level `not stated`.

Only an approved, fully reconciled candidature manifest can supply the
**candidature** denominator. Count documents separately because one
candidature can have multiple relevant documents. Report `covered / included`
only with the exact rule revision and coverage definition; while either is
unapproved, output raw pilot counts and `denominator_unresolved`, never a
percentage or an “all programmes” label. A document's verified bytes do not
make its topic search complete. No empty extraction result produces a negative
policy claim.

Changing the rule or official enumeration invalidates the candidature
denominator and dependent coverage totals. Adding an annex or replacement
invalidates affected document/topic coverage. A source hash/version change
also sends exact page anchors and dependent statements/relationships to
re-review; it never mutates the prior source version in place. Rights and
editorial decisions must be rebound to the exact new version by their human
owners. A deterministic report should list invalidated dependencies rather
than silently carrying forward earlier approvals.

### Fictional acceptance cases before implementation

1. An included fictional candidature with no located programme remains in the
   denominator with an unresolved search, not a `not stated` position.
2. A fictional coalition has a joint programme and a territorial annex; both
   document rows join to one candidature without merging their rights states.
3. A document has verified bytes but an unknown publication date and pending
   rights; integrity is reported, publication/quotation permission is not.
4. A replacement changes the hash; the old row and its evidence remain, while
   page anchors, topic searches and related claims are flagged for review.
5. An unapproved rule, or a manifest row without authoritative inclusion
   evidence, yields `denominator_unresolved` and no coverage percentage.
6. A topic extraction yields no candidates but its annex was not searched; the
   topic remains unknown, not `not_found` or opposed.

### Evidence and decisions still needed

On `origin/main` at `9542582` (2026-10-21), the register has four 2023 pilot
source rows (PP, ERC, PNV, Sumar), each `published-unverified`, rights
`not_reviewed`, and publication date unknown. There is no approved 2023
inclusion rule or candidature manifest. Draft PR #101 changes source/editorial
gates and is conflicting with current main; this design neither edits its
files nor treats its green CI as human review. The prior readiness audit maps
current schema gaps, including the register timestamp mismatch. This package
specifies the next handoff only; it does not repeat that audit or implement it.

Before P0.2 implementation, owners must choose the official enumeration
source and eligibility rule, territorial/coalition treatment, source and rights
decision owners, private evidence-store policy, and the reviewed meaning of
`verified` coverage. Reconcile the eventual field design with PR #101 and
obtain OpenSpec/editorial review. Do not populate real candidate/rights rows
from this draft alone.
