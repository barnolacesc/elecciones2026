# 2023 reviewer eligibility handoff — 2026-11-12

Roadmap package: **P1 reviewer eligibility**, `2023-corpus-completion`
(proposal-only). This is a repository-method audit, not a finding about any
person, political content, source right, or existing approval.

## Reconciled boundary

- Fetched `origin/main` is `488b6f5`. The 2023 pilot register has four rows
  (PP, ERC, PNV, Sumar); each is `published-unverified` with rights
  `not_reviewed`. This is neither a complete 2023 inventory nor an approved
  candidature denominator.
- PR #101 remains open, conflicting with main and without GitHub reviews. Its
  old green checks do not validate its integration. Merged PR #166 and open
  PR #233 separately address integration and CI evidence; this package does
  not edit pilot statements, source records, validation code or public output.
- The proposed 2026 `docs/CONTENT-METHODOLOGY.md` and
  `docs/DECISION-RECORD.md` describe dual review, drafter segregation and
  political-affiliation recusal, but are not an approved 2023 policy. The
  statement and relationship schemas record reviewer IDs, verdicts and
  evidence references; they do not bind an eligibility/recusal decision to
  an exact 2023 review assignment. A pair of distinct IDs proves neither
  assignment eligibility nor a conflict-free relationship review.

## Proposed decision boundary

Before counting a human verdict toward a 2023 statement, absence finding or
relationship quorum, a private, owner-governed eligibility decision should
cover the reviewer, role, exact record revision, election, candidature(s),
territorial scope, decision time and policy revision. A cross-party relation
must check both operands. A reviewer should be able to recuse without an
explanatory political disclosure entering Git, a public artifact or ordinary
CI logs. The private ledger can hold sensitive declarations; the publish gate
needs only a non-sensitive eligibility reference and effective disposition.

Pending, expired, withdrawn or disputed eligibility cannot count as an
approval. A later recusal or corrected assignment must trigger a dependency
report for affected statements, absence findings, relationships and quiz items,
without converting a missing position into disagreement or automatically
invalidating unrelated reviewers' decisions. Reviewers and CI cannot approve
their own eligibility. This is a proposed fail-closed contract, not a claim
that any existing reviewer is conflicted.

Owners must decide the 2023 policy, eligible roles, scope of competitor
recusal, attestation cadence, adjudicator, private retention/access, quorum
after recusal and limited public correction wording. Only then should a
concrete schema, validator and fictional tests be implemented. CI can verify
references and propagation; it cannot assess an undisclosed conflict or
substitute for human editorial review.

Evidence inspected: current main roadmaps and `2023-corpus-completion` draft;
the two proposed 2026 policy documents; statement/relationship review schemas;
four-row source register; PR #101/#166/#233 metadata. No private personnel
records, source PDFs, political answers or real review evidence were accessed.
