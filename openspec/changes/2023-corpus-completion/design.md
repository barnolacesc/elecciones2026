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

## P0.4 draft — publisher-bound source identity

Status: proposal-only. This narrows the P0 authenticity handoff for each
document version; it does not verify any current publisher page, grant reuse
rights, approve a candidature or implement a fetcher. It is separate from
rights withdrawal (draft PR #149) and multi-document applicability (draft PR
#150).

### Evidence unit and review boundary

For each candidate source version, propose a private evidence unit keyed by
`election_id`, source ID, document role and SHA-256. It records the claimed
publisher, official landing-page URL and captured reference, observed link or
discovery path to the document, every redirect and final URL, access timestamp,
content hash, and private capture reference. If a page links to an archive or
third-party host, record the chain rather than replacing the publisher URL
with the destination. An inaccessible page, changed redirect or unavailable
capture leaves the identity question pending; it is not a reason to fill an
unknown publication date from a path or filename.

A human source-authenticity reviewer decides whether the evidence binds the
claimed publisher to those exact bytes. Hash verification proves only byte
identity. Rights reviewers decide permitted use independently for the exact
version; editorial reviewers decide claims and locators independently. A
mirror may be an alternate location for an approved version only after its
chain and hash are reviewed. An equal hash alone does not establish publisher
authority, and two locations do not increase document coverage. Different
hashes at one URL remain separate version candidates, with old evidence kept.

### Proposed reconciliation and fictional cases

The future report lists each version's identity state (`pending`, `reviewed`,
or `invalidated`), observed URL chain, exact hash and decision reference. It
lists alternate locations separately from document/version counts. A changed
landing link, redirect, final hash or publisher claim invalidates the affected
identity decision and dependent locator check; rights and statement reviews
are not silently copied to new bytes. The public build receives no captures,
source bytes, redirect logs or private decision evidence.

Fictional acceptance cases: (1) official page but no captured link to the PDF;
(2) official page redirecting to a third-party mirror with matching bytes;
(3) two URLs with equal hashes but no reviewer equivalence decision; (4) a
stable URL returning new bytes; (5) a deleted landing page with retained,
dated private evidence. All remain pending or versioned as appropriate; none
authorizes a quote or political claim.

The owner must choose the acceptable evidence capture, freshness/recheck rule,
reviewer, and handling of inaccessible historic publisher pages. Review this
contract with the P0 inclusion and document-scope decisions, and reconcile its
eventual schema with PR #101 before implementation.

## P1.4 draft — correction dependency closure

Status: proposal-only. This specifies how a future 2023 correction should
invalidate derived decisions; it does not change current records, approve a
correction, or authorize implementation. It depends on approved P0 source,
rights and taxonomy contracts and the P1 statement/relationship method.

### Proposed review transaction

1. Identify the immutable election, source/version, statement or relationship
   revision being corrected and retain the prior state and reason. A correction
   to source authenticity, rights or document scope remains a distinct human
   decision; a content reviewer cannot silently confer those approvals.
2. Compute the transitive dependent set before public projection: exact source
   locators; initiative candidates; topic searches and absence findings;
   statement summaries; paired relationships; comparison-set ledgers; and
   quiz items that cite affected statements. Record each affected ID/revision,
   disposition and reviewer queue. A rights withdrawal also suspends affected
   public uses according to the approved rights policy.
3. Withhold affected public claims and derived labels until their respective
   human reviewers recheck the new exact versions. Keep unrelated, already
   approved measures available when the approved presentation method allows
   a clearly limited view. Do not convert withheld content into `not stated`.
4. Produce a deterministic private impact report and a public correction
   summary containing only approved, non-sensitive metadata. The old version
   stays traceable privately. The static build and browser publish set must
   agree; omission of a correction or an invalidated dependency must not
   revive a claim on the next rebuild.

The existing correction schema lists `invalidated_relationship_ids`, and the
generator loads correction records, but a complete dependency-closure contract
for 2023 topic coverage, comparison sets and quiz citations is not specified.
This draft does not assert that any current public 2023 claim is affected.

### Fictional acceptance cases and pending decisions

- Changing a fictional source hash with unchanged prose still withholds old
  page locators and every dependent approval until exact-version review.
- Retracting one of two paired fictional statements withholds its relationship
  and set-wide conclusion, without fabricating a negative position for that
  candidature or suppressing an unrelated reviewed measure.
- Reclassifying a measure across topics invalidates both old and new topic
  accounting, any scoped absence and quiz item selection that used the old
  assignment. A label-only taxonomy edit is classified by reviewers, not by
  an automatic string comparison.
- A corrected statement cited by a provisional quiz item cannot inherit its
  old item approval. No answer values enter the impact report or URLs.
- A correction affecting `es-gen-2023` cannot invalidate or revive records in
  `es-gen-2026`; a missing dependency ID fails the private reconciliation.

Editorial owners must settle correction severity and public notice wording,
reviewer segregation, whether a rights withdrawal removes links as well as
summaries, and how an incomplete comparison is displayed. The approved schema,
transaction boundary and tests follow those decisions, not this draft alone.

## P1.6 draft — initiative identity and duplicate lineage

Status: proposal-only. This refines P1.1's one-actionable-measure rule without
changing source records or approving 2023 content. It precedes the P1.2
comparison-set projection. P1.4 document applicability decides which source
versions govern a candidature; P1.5 relationship collision concerns paired
statements. Neither decides whether two extracted passages represent one
initiative.

### Proposed private ledger

Use three separate units: `(source ID, immutable hash, locator, extraction
event)` for an occurrence; a versioned candidate for an interpreted actionable
measure; and a reviewer-assigned initiative identity. Keep a many-to-many
occurrence-to-candidate link: one sentence can contain two instruments and one
initiative can recur across documents. The decision ledger records `split`,
`same initiative`, `distinct`, `qualification`, or `unresolved`, the compared
candidate versions, all source locators, reviewer/evidence references and the
reason. These are proposed states, not approved schema values. A machine may
suggest a match but cannot finalize identity or suppress an occurrence.

Count reviewed initiative identities only after every source occurrence in
the relevant document set has an explicit disposition. Keep raw occurrence
and candidate counts separately, with their denominator and review state.
Never turn an unresolved duplicate into a second public claim or silently
discard it to improve a coverage percentage. A changed source, candidate
granularity or identity decision creates a new ledger revision and sends
affected statements, topic counts, comparison sets and quiz dependencies to
review. Preserve the earlier decision and its citations. Rights and statement
approval remain independent; no private source text or approval evidence is
copied to the static artifact.

### Review boundaries and acceptance cases

Use the five fictional scenarios in the editorial-statements delta. Test
repeated runs, one-to-many splits, cross-document repetition, materially
different conditions and revision of an approved grouping. A fixture should
also check that a pending annex under P1.4 prevents a final initiative count
and that a grouped initiative can retain two source locators without treating
either as quotation permission. The public projection may show a summary only
after the exact final statement and its source-use decision pass their separate
gates.

The owners must decide identity granularity, reviewer quorum/segregation,
whether equivalent measures in different territorial scopes may share an
identity, how multiple citations appear to readers, and the meaning of a
reported initiative count. Reconcile these decisions with P0 source scope,
P1.4 applicability, P1.2 set accounting and PR #101 before implementation.
No agent or passing test can make these editorial decisions.

## P1 quantitative-comparability draft — value and basis ledger

Status: proposal-only. This narrows P1.1's amount and relationship method; it
does not approve a number, calculation, political relationship or renderer.
The [dated baseline audit](../../../docs/2023-QUANTITATIVE-COMPARABILITY-AUDIT-2026-10-28.md)
records the current schema boundary. P0 source/rights decisions, 2023 taxonomy
approval, candidate interpretation and separate relationship review remain
prerequisites.

For each candidate quantity, propose a private ledger keyed to exact election,
source ID/version/hash, page or section, candidate and statement versions. It
distinguishes the cited value from any derived value and records unit, period,
population/denominator, geography, conditions, value role, evidence reference,
review state and unresolved fields. The source wording and private evidence
remain outside Git and the static build. A transformation additionally records
input IDs, formula, assumptions and rounding; no missing value is filled from
general knowledge or a different party's document.

For a numeric comparison, reviewers first decide whether the policy question,
value role and all material bases match. If they do not, the measures may still
appear individually with their qualifications, but the comparison cannot rank
their magnitudes. A reviewed conversion can support a bounded difference only
when its inputs, method and resulting claim receive independent relationship
approval. Changing a source value, qualifier or conversion invalidates the
derived claim and dependent relationship, not the historical record. No
calculation can grant source reuse rights or editorial approval by itself.

Fictional acceptance cases: future target versus current baseline; annual
amount versus multi-year total; percentage versus percentage-point change;
missing denominator; and compatible same-basis values with an approved,
auditable conversion. The owner/editorial review must decide which conversions
are allowed, materiality and rounding rules, who checks calculations, and
Spanish wording for incomparable figures. Only after that review should a
concrete schema, validator and public presentation be specified and built.

## P1.7 draft — source-language bridge

Status: proposal-only. This package formalizes the repository-visible gap in
`docs/2023-TRANSLATION-TRACEABILITY-AUDIT-2026-10-24.md`; it does not inspect
source PDFs, certify a translation, change the six PP/ERC candidate records or
resolve draft PR #101. P0 source identity and rights, P1 statement review and
P1 relationship review remain independent gates.

The proposed private bridge joins an exact source ID/version/hash and physical
page/section to a statement ID/revision. It records source and output language,
the material terms checked (including qualifications, jurisdiction, amounts
and timing where stated), human disposition, decision date and private evidence
reference. The bridge stores no source text in Git. The public projection may
contain only the approved Spanish summary and lawful source locator, never
translation notes or a new claim that the source is Spanish.

An existing independent review can satisfy the language check only if its
authentic evidence explicitly covers that exact mapping and the editorial
owners accept that evidence standard. This design does not impose a third
reviewer or retroactively mark the pilot reviewed. A changed source version,
locator or statement wording invalidates the bridge and its dependent public
projection. If a material translation correction changes meaning, the
statement's relationships and quiz mappings also enter re-review; coverage
cannot silently retain the old summary. A Spanish-source record follows the
ordinary review route without a manufactured translation approval.

Before implementation, editorial owners must decide the evidence format,
responsible reviewer competence, whether the existing dual-human review can
carry this check, and whether any exact private pilot review already contains
it. Reconcile the decision with PR #101/#166; test only fictional multilingual
fixtures until source rights and editorial gates pass. CI can test references
and invalidation but cannot decide translation quality or source rights.

## P0.9 draft — temporal provenance of source versions

Status: proposal-only. This refines P0 document discovery and the source gate
for the later P1 corpus. It neither dates a real programme nor changes rights,
coverage, editorial records or public output. The dated baseline is in
`docs/2023-TEMPORAL-PROVENANCE-AUDIT-2026-10-29.md`.

### Proposed evidence record

For each source version, keep distinct event types: publisher's claimed
publication, observed publisher page or link, bytes retrieved, bytes archived,
and human review. Record the event date with precision and timezone when
known, evidence type, evidence locator/private snapshot reference, observer,
and the exact source ID/hash or an explicit `version_unresolved` link. Do not
collapse a page date or archive capture into the PDF publication date. A
current PDF at an unchanged URL may not be the PDF that an older page linked.

The proposed chronology decision points to the accepted evidence records,
version/hash, deciding human and decision date. It can conclude an evidenced
date, a bounded interval, or `unknown`; an interval must not be presented as
an exact day. Evidence sufficient for *a programme existed* may still be
insufficient for *this exact version existed* at that time. The owner must
decide whether a source with unknown exact publication date can support a
private historical comparator and what reader-facing uncertainty it requires.
Rights permission and statement review cannot answer that chronology question.

### Fail-closed behavior and fictional checks

An altered hash at a stable URL creates a new version and queues chronology,
page anchors, statements and relationships for review. Historical evidence
for the older version is retained. The deterministic audit should report
unknown and contested dates without manufacturing a sortable date or hiding
the source; the eventual public projection needs reviewed wording for any
uncertainty it includes. Fictional checks cover a date-like filename, a later
retrieval, an undated PDF linked from a dated page, a stable-URL replacement,
and a rights-approved but chronologically unresolved version.

Before implementation, the owner/editorial team must approve acceptable
evidence classes, how a publisher's revision notices and external captures
are weighed, interval precision, reviewers, and the publication rule for
unknown dates. This draft makes no legal or historical determination.

## P0.10 draft — shared-document attribution gate

Status: proposal-only; owner and OpenSpec review required before schema or
inventory implementation. Repository audit:
[`docs/2023-SHARED-DOCUMENT-ATTRIBUTION-AUDIT-2026-10-29.md`](../../../docs/2023-SHARED-DOCUMENT-ATTRIBUTION-AUDIT-2026-10-29.md).

The proposed model separates a document-version identity (source ID, immutable
hash/version, publisher and archive reference) from a candidature-applicability
edge (election, approved manifest/rule revision, candidature, constituency,
document role and applicability scope). Each edge has evidence, reviewer,
decision state and revision. Several approved edges can refer to one source
version, but cannot borrow each other's scope, rights or editorial decisions.
The source/version still carries its independent authenticity and reuse-rights
gates; applicability does not grant publication or quotation permission.

The private reconciler should expose both counts: distinct source versions and
included candidatures with reviewed applicable documents. It should preserve
pending/disputed edges and avoid an apparent completeness percentage when the
inclusion denominator or required edges are unresolved. A changed manifest,
source version, edge decision or territorial scope invalidates only affected
candidature/topic dependencies, including negative-search findings and
relationships. The public projection cannot duplicate a coalition measure as
two independent party positions solely because two manifest rows share bytes.

Fictional acceptance cases: one source/two lists with only one approved edge;
coalition programme with an unapproved member-party edge; identical bytes at
different URLs with conflicting scopes; withdrawn edge invalidating one
candidature's coverage but preserving an unaffected edge. These are model
checks, not claims about actual 2023 documents.

Owner decisions: candidature granularity and coalition treatment; sufficient
publisher/ballot evidence for an edge; edge-review quorum; public shared-source
label and denominator wording. Reconcile with P0.2/P0.3, P1 document scope and
PR #101/#166 before implementation.

## P1.4 draft — qualification fidelity across summary and comparison

Status: proposal-only for editorial and OpenSpec review. This package narrows
the existing P1.1 requirement to preserve source-stated qualifications. It
does not approve a real summary, change source rights, edit the pilot records,
or implement publication logic. P0 source identity/rights, 2023 taxonomy and
P1 initiative-granularity decisions remain prerequisites.

### Evidence and review boundary

The current 2023 example statement shape has one `qualifications` field and
one `source_page`/`source_section` pair. That shape does not by itself show
which source span supports a condition that is elsewhere in the document, or
whether a shortened summary retained a material exception. The proposed
private review unit is a version-bound qualification ledger: measure ID and
source version/hash; each operative clause and material limit; its exact
page/section locator; the proposed summary location where it is represented;
and a human disposition (`retained`, `material_omission`, `not_applicable`, or
`unresolved`) with evidence reference. These labels are design candidates,
not approved schema values or automated political judgments. Source wording,
private review notes and PDFs remain outside Git and the public build.

Review the operative clause and qualifications against the full relevant
source range, not just a search snippet. A reviewer may approve concise copy
only after checking that the eligibility, geography, instrument, amount and
timing still mean the same thing. A second reviewer checks neutrality and
what a two-party comparison would imply. A relationship decision cites the
exact reviewed statement versions and cannot strip a qualification from one
side to create an apparent agreement or divergence. Missing source evidence,
review disagreement or a changed source version blocks the affected statement
and dependent relationship; it does not create a negative party position.

### Fictional acceptance cases and decisions

1. The operative measure and eligibility limit appear on different pages:
   two locators are retained; an unqualified headline remains unpublished.
2. A general rule has a stated exception: the summary and relationship keep
   its effect, or the omission is unresolved and both stay unpublished.
3. An amount or deadline is absent from the reviewed source range: record
   unknown, never an unlimited promise or a zero value.
4. A new document version changes a condition: retain the old evidence and
   invalidate the statement, its comparison and any quiz item using it.

Editorial owners must decide the materiality test for limits, how to represent
multiple locators in public copy, reviewer disposition/quorum, and whether a
qualified measure needs a shorter headline plus visible detail on a phone.
Only after those decisions and reviewed specs/design/tasks may an engineer
define schema, validator and fictional-fixture implementation. CI cannot
approve a political interpretation or a rights decision.

## P1.7 draft — extraction-visibility handoff

Status: proposal-only. This refines P1.3's treatment of non-searchable source
ranges; it does not implement OCR, alter private PDFs or approve an absence
claim. The P0 source/version and relevant-document scope decisions, approved
2023 taxonomy and human search protocol remain prerequisites.

A future private per-range visibility ledger should join `(election_id,
candidature_id, source_id, source_sha256, physical_pdf_page_or_section_range,
extractor_identity, extraction_artifact_hash, topic_search_revision)` to the
P1.3 search ledger. It should record extraction outcome, whether the original
page was visually inspected, the inspection method and reviewer, legibility
limitations, unresolved text/reading-order regions, any alternate-processing
run and a private evidence reference. The proposed states are `uninspected`,
`extracted_unverified`, `visual_review_pending`, `visually_checked`, and
`unresolved`. These are draft semantics, not approved schema values. The
ledger must not copy full source text or page images into Git or the static
build.

The current E1.2 worker verifies page count and deterministic text hashes; it
cannot certify visual completeness. A blank `pages.json` entry can be a blank
page, an image-only page or extraction failure. Nonempty text can still omit a
column, table, footnote or qualification. Therefore P1.3 may reach a reviewed
negative finding only if every required range has a reviewed visibility path
under the owner-approved protocol. A reviewer can document manual inspection
of a range; automatic OCR, if later approved, is an aid and never substitutes
for source/rights, proposal or absence review. Tool or source-version changes
must invalidate dependent range observations and search conclusions.

Before implementation, owners must decide visual-sampling versus full-range
inspection, treatment of tables/footnotes and inaccessible pages, acceptable
alternate processing, reviewer quorum, private evidence retention and the
threshold for declaring a range searchable. Fictional acceptance cases are in
`specs/editorial-statements/spec.md`. No real 2023 page is classified here.

## P1.8 draft — comparison presentation order

Status: proposal-only. See the dated comparison-order audit. P1.2 defines
which reviewed measures belong to a pair/topic view; P1.8 governs only their
presentation sequence and party display order. It neither chooses a political
position nor changes source, rights, relationship, coverage or release gates.

The current builder emits relationship-backed groups by relationship ID before
unmatched statement groups by statement ID. This is deterministic, but the
identifiers and paired status are not reviewed importance scores. Propose an
explicit order-policy version in the private comparison-set ledger and a
stable presentation key for each included group, with a review reason where
editorial ordering is needed. A renderer consumes only the approved order and
bounded method label; it must not rank by relationship type or source count.
The static fallback and browser payload must use the same sequence. Preserve
all unmatched and limitation entries even when the visual order changes.

Before a schema or renderer change, the editorial owner must select the
default ordering rule, tie resolution, treatment of several measures answering
one policy question, party order, user-controlled sort semantics and Spanish
method wording. Fictional fixtures should cover identifier renaming, paired
versus unmatched entries, party reversal and incremental corpus additions.
Mobile comprehension review must check whether readers infer endorsement from
first position. Neither automated determinism nor this draft settles that
interpretation.
