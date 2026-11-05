# 2023 relationship-review dissent handoff — 2026-11-05

Roadmap package: **P1.1**, `2023-corpus-completion` (proposal-only). This is a
technical/editorial method draft, not approval of a political comparison,
reviewer verdict, rights use or publication.

## Reconciled baseline

- `origin/main` was `488b6f5`. PR #101 (`f8506a1`) remained draft, open and
  conflicting with main, with zero GitHub reviews. Its passing checks were
  recorded on 2026-10-12, not on a rebased current-main integration.
- The main source register contains four `es-gen-2023` pilot rows (PP, ERC,
  PNV and Sumar), each `published-unverified` with rights `not_reviewed`.
  This is not an approved candidature or document-coverage denominator.
- `RelationshipRecord.validate` in `src/elecciones2026/schemas.py` counts
  distinct `approved` reviewers when `review_status` is `approved`. It does
  not reject a mixed current verdict set or require a dispute-resolution
  record. The relationship schema's review entry has reviewer/date/verdict/
  notes but no exact operand-version or relationship-revision binding. This
  is a prospective gate gap, not evidence of an actual disputed relation.
- The earlier [dispute audit](2023-RELATIONSHIP-REVIEW-DISPUTE-AUDIT-2026-10-28.md)
  isolated the mixed-verdict behavior with fictional data. The P1.5 collision
  draft covers *multiple relationship records for one pair*; it does not
  resolve dissent *within one relationship revision*.
- Main CI run [41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
  failed on 2026-11-01, including delivery/provisional tests and Docker
  readiness errors. Passing CI would remain engineering evidence, not human
  editorial review.

## Proposed decision boundary

Bind each relationship verdict to an immutable private packet containing the
exact statement versions, policy question, type, grounds and caveats. An
unresolved current rejection or `needs_changes` blocks comparative publication
even if two earlier approvals exist. A changed packet needs fresh review;
historical verdicts remain auditable but cannot approve the new packet.
Separately approved statements may appear only under their own source, rights
and editorial gates. Neither withholding nor missing relation evidence means
opposition or `not stated`.

The corresponding draft requirement, design and tasks specify fictional
acceptance cases. Owner/editorial review must decide resolution authority,
reviewer segregation, quorum, conflicts and private evidence retention before
implementation. This PR changes no real source, right, review mark, political
record, renderer, routing or public artifact.
