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

## P1.5 draft — relationship decision collision gate

Status: proposal-only, for editorial and OpenSpec review. This refines the
P1.2 comparison-set ledger without implementing it or approving any real
2023 relationship. It does not change P0 source rights or P1.4 document
applicability decisions.

The current builder validates each relationship separately and then emits one
measure group per active relationship ID. It does not reconcile two different
active IDs that name the same statement pair. Consequently, two contradictory
or duplicate reviewed-looking cards could coexist for one exact pair. The
current four-source pilot has no active reviewed relationship; this is a
future publication boundary, not a claim that a live contradiction exists.

Propose a private decision ledger keyed by election, exact unordered pair of
statement *versions*, and an editorially approved policy-question identity.
It records each candidate relationship ID, type, caveats, review disposition,
supersession/correction link and effective-state decision. Before publication,
the build checks the full candidate set, including competing IDs; it never
picks the first, last or newest record. A collision leaves the affected pair
unpublished pending independent human arbitration. An invalidated predecessor
stays in audit history, while a separately approved successor may be effective.
Distinct statement pairs are valid even if they share one operand. The
comparison-set ledger must count each effective pair and retain unmatched
statements; collision handling cannot conceal P1.2 coverage gaps.

Fictional acceptance fixtures should cover opposite classifications for one
pair, duplicate same-type decisions with different caveats, an invalidated
predecessor and approved successor, and one statement in two distinct pairs.
Verify the static fallback and browser payload reject or omit the same
unresolved pair. No fixture establishes the right political interpretation.

Editorial owners must decide the policy-question identity and granularity,
who may arbitrate a collision, whether genuinely distinct questions can reuse
one exact pair, and the private correction trail. Only after that review may a
concrete schema and validator task be marked implementation-ready.

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

## P0.3 draft — official enumeration evidence

The [2026-10-22 evidence handoff](../../../docs/2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md)
identifies the BOE's 2023 proclaimed-candidature notice and its two linked
corrections as a candidate primary input. One correction changes a Teruel
Congress entry from `No proclamada` to a candidate list; another changes a
Baleares coalition ballot name. The proposed manifest therefore retains
constituency, chamber, original status/name, every applied correction and
evidence locator as separate, reviewable facts. Corrections are not destructive
overwrites. A presented-candidature list is only a cross-check.

This does not approve the inclusion rule, establish a final denominator or
certify that no other official changes exist. Owner and peer review must set
the rule, finality/search protocol and coalition identity mapping before any
real manifest is treated as complete. No programme or rights state changes.

## P1.3 draft — topic-search evidence and absence gate

Status: proposal-only. This narrows the P1.1 topic-search requirement; it does
not approve a search protocol, a `not_found` record, or implementation. P0's
approved candidature manifest, relevant document set, rights decisions and
2023 taxonomy applicability are prerequisites. P1.2's comparison-set question
is separate: even an approved topic search cannot prove that a displayed
measure set is exhaustive.

### Search unit and private evidence ledger

The review unit is `(election_id, candidature_id, topic_id, taxonomy_revision,
source_set_revision)`. The source set enumerates every document version deemed
relevant to that candidature and topic, including annexes and replacements, or
records a human-reviewed reason for exclusion. Each source entry records its
immutable ID/hash, searched page or section ranges, method, search date,
reviewer, unresolved ranges, candidate IDs and evidence reference. A tool's
empty result is evidence about that tool run only; it is not a negative policy
finding. Private search notes and source text do not enter Git or the public
static artifact.

### Proposed state and publication boundary

| State | Meaning | Permitted public conclusion |
|---|---|---|
| `scope_pending` | Inclusion, taxonomy or relevant source set is unresolved. | Coverage unresolved; no topic absence. |
| `search_pending` | Source set is fixed but one or more required ranges are unsearched. | Partial coverage; no topic absence. |
| `review_pending` | Search ran, but scope, candidates or negative finding await human review. | Review pending; no topic absence. |
| `reviewed_with_candidates` | All required source ranges and candidate dispositions were reviewed. | Only independently approved statements may appear; not a completeness claim by itself. |
| `reviewed_no_supported_candidate` | All required source ranges were reviewed and no candidate supports a proposal under the approved protocol. | A carefully scoped absence label may be considered after separate editorial approval; never opposition. |
| `invalidated` | Rule, taxonomy, source set/version or review evidence changed. | Fall back to unresolved until re-review. |

This is a proposed internal state vocabulary, not an approved schema change.
The projection must retain the source-set and taxonomy revisions behind any
absence label. It must not generalize a document/topic finding to the party's
entire election platform or to a different election. A source link or rights
decision does not certify that a topic search was complete. Pending rights
continue to block claim publication independently of search state.

### Dependency and fictional acceptance cases

1. A programme was searched but a relevant territorial annex is unsearched:
   `search_pending`, never `not_found`.
2. An extractor returns zero hits over every PDF page, but no human has checked
   scope and method: `review_pending`, never a reviewed absence.
3. Two search methods disagree or a reviewer finds an ambiguous aim: retain
   the candidate and unresolved decision; do not force a negative conclusion.
4. A reviewer excludes an annex with a recorded scope reason; the exclusion
   remains visible in the private ledger and requires the approved protocol.
5. A source replacement, changed taxonomy revision or new relevant annex
   invalidates the prior negative finding and its reader-facing label.
6. A reviewed search yields proposals for one subtopic but not another:
   do not imply all measures or the whole topic were exhaustively compared.

### Decisions for owner/editorial review

Approve the 2023 document/topic relevance and search-stopping protocol,
acceptable evidence for ranges that are non-searchable, reviewer quorum for
negative findings, treatment of translated sources, and exact Spanish wording
for a scoped absence. These cannot be supplied by CI or an agent. After review,
the implementation task can define a concrete schema and validators against
the agreed protocol; until then this draft is a fail-closed handoff only.

## P0.5 draft — rights withdrawal and use-scope changes

Status: proposal-only. This package addresses a decision changing **without**
any PDF byte or source-version change. It does not determine legal rights,
alter the four pilot source records, repair PR #101, or authorize publication.

### Reconciled gap (2026-10-25)

At `origin/main` `8e2fab4`, the four registered 2023 pilot sources remain
`published-unverified`, rights `not_reviewed`, publication date unknown. The
current `RightsReview` contains one status, reviewer, date and notes, without a
decision revision, use-specific evidence pointer or withdrawal history. Current
generator and quiz checks inspect rights status for quotation but cannot
identify a later withdrawal of an unchanged version. Draft PR #101 proposes
version-bound `link_only` summaries and remains conflicting, unreviewed and
unmerged. This delta is for the future reviewed 2023 contract and does not
change PR #101's files or assert that any current record was approved.

### Proposed decision and dependency contract

The private rights ledger should append immutable events keyed by election,
source ID, exact version/hash, use type, decision revision and private evidence
reference. Event types for review are grant, narrow, withdraw, expire, challenge
and resolve. The effective decision is the latest **human-authorized** state
for the exact use and version; an unresolved credible challenge should fail
closed for the affected use pending owner adjudication. Preserve event time
and effective time separately. The reviewer must decide how expiry and
challenges are authenticated; an agent or CI cannot create a real decision.

The dependency report should join a decision revision to each approved
statement, quote, relationship, quiz item and built artifact using that source.
On a restrictive event, invalidate only affected uses while preserving their
prior decisions and separate editorial reviews. A narrower quote permission
does not automatically remove a permitted outbound link, and a link decision
does not allow a paraphrase. The next deterministic build should fail closed or
omit the affected projection under an explicitly reviewed rule. If an earlier
artifact is already served, report its ID and correction/release action to the
owner; rebuilding in CI is not deployment or proof that readers no longer see
it. Private evidence and source bytes stay outside Git and public artifacts.

### Fictional cases and review questions

1. Same source hash, quote grant narrowed to link-only: quote is withheld;
   approved link survives only if it has its own current use decision.
2. A challenge is recorded but unresolved: affected paraphrase, comparison
   and quiz citation are withheld, not silently grandfathered.
3. A use grant expires between two builds: the later build cannot reuse it;
   the earlier served artifact appears in a release-remediation report.
4. A decision is re-granted after review: prior statement and relationship
   approvals are not automatically renewed; exact dependencies are rechecked.

Before implementation, human owners must decide the authoritative decision
store, challenged-use authentication, effective-time policy, use vocabulary,
review quorum and release-response owner. Reconcile any approved schema with
PR #101 and the P0 source-use queue. Fictional tests can check propagation,
but cannot establish a real right or complete a served-site withdrawal.

## P1.4 draft — multi-document proposal applicability and conflict gate

Status: proposal-only. P0.1 inventories general, territorial, coalition and
replacement documents separately, but a source-to-candidature join does not
decide which document governs a proposal or whether two records conflict.
The 2023 pilot register contains only four general-scope source rows; it is
not evidence that annexes are absent. Draft PR #101 concerns six PP/ERC
summaries and source-use gates, not a reviewed document-precedence policy.

### Proposed private decision ledger

For each candidate initiative, retain the exact source version, document
role, publisher, candidature/constituency scope, applicability claim and
evidence locator. Compare potentially overlapping initiatives from the same
candidature by their policy question, action, beneficiary, jurisdiction,
conditions, amount and timing. Record one of `distinct_scope`, `compatible`,
`potential_conflict`, or `superseded` as a *draft classification*, with linked
candidate IDs, source versions, grounds and reviewer disposition. These are
proposed review states, not approved schema fields or political findings.

No rule should silently prefer a general programme, annex, coalition text,
newer URL or apparent publication date. A replacement requires an evidenced
version chain; a territorial annex may narrow geography without replacing the
general text; coalition and member-party documents may have different
speakers. The editorial owner must decide the authoritative document-scope
and precedence policy after the P0 candidature/document manifest is reviewed.
Unknown scope, publisher identity, date or replacement relationship stays
unresolved. Private PDF text and adjudication evidence never enter Git or the
public artifact.

### Projection and acceptance boundary

A public statement must identify its own applicable source/scope. If a
materially overlapping initiative has unresolved applicability or conflicting
terms, the system must not emit an unqualified synthesized party position or
use that initiative in an agreement/divergence relation. Independently
approved, non-conflicting statements may remain eligible under the reviewed
policy, with a bounded scope limitation; a blanket ban on the whole party is
not implied. The P1.2 comparison-set ledger must retain excluded/conflicted
IDs so selection cannot silently erase them. A source replacement or scope
decision change invalidates affected statement and relationship approvals.

Fictional acceptance cases: (1) a general document and territorial annex
state different eligibility in one constituency; (2) two documents cover
different constituencies and are not falsely merged; (3) a later URL has no
evidenced replacement chain; (4) a coalition document and member-party text
have unapproved speaker mapping; (5) an approved non-conflicting statement
survives while a conflicting one is withheld; (6) a corrected scope decision
invalidates a previously approved relationship. Tests must exercise the
private ledger and static/browser publication projection, not real positions.

Owner/editorial review must decide document precedence, coalition attribution,
territorial display scope, conflict materiality and adjudication roles before
implementation. This draft grants none of those decisions and changes no
source, rights, review or public record.

