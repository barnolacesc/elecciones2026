# 2023 policy-question identity: P1.2/P1.5 review draft

Status: proposal-only audit, specification, design and task handoff for
`2023-corpus-completion`. This does not approve a comparison method, political
relationship, source right, implementation or release. Snapshot:
`origin/main` `488b6f5` on 2026-11-10.

## Reconciled boundary

- The 2023-first roadmap requires comparisons of specific, source-linked
  measures rather than topic-wide claims. The P1.2 design proposes accounting
  for every eligible statement; P1.5 proposes collision detection keyed partly
  by an **editorially approved policy-question identity**. Both explicitly
  leave that identity's granularity to owner/editorial review.
- `content/schemas/relationship.schema.json` currently requires a free-text
  `measure_label`, `topic_id`, `subtopic_id`, `statement_ids` and
  `relationship_type`; it has no policy-question identity or version field.
  This is a contract gap for the *future* P1 ledgers, not evidence of a bad
  published relationship. No current 2023 example relationship is active.
- The register contains four 2023 pilot sources (PP, ERC, PNV, Sumar), all
  `published-unverified` with rights `not_reviewed`; eight example statements
  are six `under_review` and two `draft`. Their source URL/version values
  match the corresponding register row, but this join does not verify pages,
  grant rights or make a 2023 inclusion denominator. PR #101 remains open and
  conflicting, and its 2026-10-12 CI predates current main. PR #219 separately
  audits its disposition; PR #224 separately maps the source PR queue. This
  draft does not edit their paths or settle their decisions.

## Draft requirement for OpenSpec review

For any proposed cross-party relation, the private review packet **SHALL**
identify one versioned policy question in the same election and taxonomy
revision as its exact statement versions. The question **SHALL** state the
decision being compared, the relevant instrument/outcome and population or
jurisdiction boundaries; a broad topic, slogan or display label **SHALL NOT**
serve as its identity. A human editor **SHALL** approve the question's scope
and the mapping of each operand to it, separately from approving the relation
type, grounds and caveats. No question ID or automated similarity score
constitutes political agreement.

The comparison-set ledger **SHALL** account for all eligible approved
statement versions that address that question, including unpaired measures
and reviewed exclusions. A change to the question definition, taxonomy,
source version or mapped statement **SHALL** invalidate dependent relations
and set-wide wording until reviewed again. Two proposed relations for the
same exact pair **SHALL NOT** evade the P1.5 collision gate merely by assigning
different question IDs; reviewers must resolve whether the questions are
materially distinct. Unknown question scope is a pending state, not a
negative party position or an exhaustive topic comparison.

### Fictional acceptance cases

1. Two fictional measures share a topic and aspiration but use different
   instruments. They are not auto-mapped to one question or called agreement.
2. Two fictional measures use one instrument but apply to different
   populations. Any shared question records both boundaries; the relation
   cannot hide the eligibility difference.
3. Two fictional A-side measures and one B-side measure answer one reviewed
   question. One reviewed pair does not consume or silently discard the extra
   A-side measure.
4. Two active fictional relation IDs use the same exact statement versions
   under differently named questions. Neither becomes effective until a human
   decides whether the questions are genuinely distinct and resolves the
   apparent collision.
5. A fictional question's scope is narrowed after relation review. The former
   relation and set-wide summary are withheld; old reviews remain history and
   cannot approve the new question version.

## Proposed design, not schema approval

Keep a private question registry keyed by election, question ID and immutable
revision. A question record would carry a neutral question text, taxonomy
revision, instrument/outcome and population/jurisdiction boundaries, author,
human decision reference and status. A separate mapping ledger would bind
question revision to exact statement versions with a reviewed inclusion,
exclusion or pending disposition. The relationship decision ledger would
reference both the approved question revision and exact operand versions.
The P1.2 set ledger would join these records and expose unresolved mappings
instead of manufacturing a complete view. Source text, PDF bytes and private
decision evidence stay outside Git and public artifacts; only approved,
bounded reader-facing wording may be projected.

Do not add these fields to the current public schema until P0 candidature,
document, rights and taxonomy boundaries are reviewed and the P1.2/P1.5
contracts are reconciled. A human decision is needed on question granularity,
one-to-many relations, when two questions over the same pair are distinct,
who reviews mappings, and Spanish wording for incomplete question coverage.

## Tasks and verification handoff

- [x] Audit the current schema, P1.2/P1.5 draft and 2023 pilot status at the
  stated main SHA; draft requirement, design and fictional cases here.
- [ ] Owner/editorial reviewers decide question granularity, mapping authority,
  collision arbitration, permissible exclusions and public limitation copy.
- [ ] Reconcile the decision with open OpenSpec PRs; then move the reviewed
  requirement, design and implementation tasks into
  `openspec/changes/2023-corpus-completion/` before changing code.
- [ ] Implement only after that review, using fictional fixtures to verify
  exact-version binding, asymmetric set accounting, collision handling,
  invalidation, and static/browser parity. Real 2023 claims need separate
  source, rights and editorial approvals.

Verification for this draft: parse the source register and example statements
locally, inspect the relationship schema and OpenSpec draft, and run
`git diff --check`. These checks establish only document and repository facts;
they do not validate a political interpretation or replace human review.
