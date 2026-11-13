# P1.8 audit — embedded voices in 2023 programme passages

Status: proposal-only evidence for editorial/OpenSpec review. No real 2023
passage, political position, source right or publication decision is assessed.

## Reconciled boundary

- `origin/main` at `d13ba683` has a four-party 2023 pilot, not an approved
  complete 2023 corpus. PR #101 is open, conflicting and has no human review;
  its successful October CI cannot settle source rights or editorial meaning.
- `content/schemas/statement.schema.json` requires `party_id` and accepts
  `explicit_proposal` and `explicit_opposition`, but has no field for the
  speaking voice or whether a cited passage reports another actor's position.
  `src/elecciones2026/schemas.py` uses those same statement types. This is a
  *future extraction/review gap*, not evidence that any current pilot record
  misattributes a position.
- The P1.4 multi-document applicability draft maps document speakers to
  candidatures. It does not decide whether an individual passage is the
  issuer's own commitment, a reported third-party position, a quotation being
  rebutted, or an explicit endorsement. P1.8 concerns that passage-level
  distinction only; it does not change candidature inclusion or document scope.

## Proposed review unit

Before a private candidate becomes a party position, retain a version-bound
passage-voice disposition with the exact source locator, candidate ID,
document issuer, attributed speaker if stated, rhetorical role, evidence
reference and human reviewer. Suggested roles for review are `issuer_position`,
`reported_other_position`, `rebutted_other_position`, `explicit_endorsement`
and `unresolved`; these are draft vocabulary, not approved schema values or
automatic classifier labels. The private ledger may reference source text but
must not copy PDF wording into Git or the public build. An apparent quotation
mark, party name or source URL alone cannot prove endorsement or opposition.

A reported or rebutted third-party measure must not be attributed to the
programme issuer as its own proposal. An issuer's explicitly stated response
may be separately reviewed as its own candidate, with its own locator and
qualification. Where voice or endorsement is uncertain, withhold the affected
statement and relationships, preserving topic-search coverage as unresolved;
do not convert it to `not_found`. A change to passage, document version or
voice disposition invalidates dependent summaries, relationships and quiz
mapping for exact-version review.

## Fictional cases for a later implementation gate

1. A fictional programme reports a rival's proposed tax and rejects it: the
   reported tax is not the issuer's proposal; the issuer's rejection may enter
   a separate reviewed candidate if its object and scope are evidenced.
2. A fictional programme quotes a residents' association approving a measure
   without adopting it: the association's view cannot become the issuer's
   position; no party-wide agreement follows.
3. A fictional programme explicitly adopts an external group's measure: the
   adoption and the incorporated measure require separately locatable evidence
   and a human decision on what is actually endorsed.
4. A cropped OCR span drops “according to” before a third-party claim: the
   unverified range remains unresolved under P1.7; machine text cannot settle
   the speaker.
5. A corrected source version removes an endorsement sentence: prior voice,
   statement, relationship and quiz approvals are invalidated, not inherited.

Editorial owners must decide the role vocabulary, evidence granularity,
reviewer quorum, treatment of indirect speech and endorsement, and whether
the existing statement review can carry a traceable voice decision. This
proposal does not authorize schema or renderer implementation.
