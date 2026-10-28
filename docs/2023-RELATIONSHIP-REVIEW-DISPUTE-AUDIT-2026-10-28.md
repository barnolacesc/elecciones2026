# 2023 relationship-review dispute gate audit — 2026-10-28

Roadmap package: **P1.1, review-dispute handoff**. OpenSpec change:
`2023-corpus-completion`. This is an evidence-backed, proposal-only audit,
not a policy decision, implementation task completion, or publication approval.
Snapshot: `origin/main` `8e2fab4`. No private source, party claim, reviewer
identity, rights decision, or political answer was inspected or changed.

## Baseline and observed gap

- The 2023-first roadmap places traceable proposal and comparison review in P1.
  The draft [comparison delta](../openspec/changes/2023-corpus-completion/specs/programme-comparison/spec.md)
  requires approval of the exact statement pair and grounds, while leaving
  relationship-review quorum and segregation to an editorial decision.
- The existing [editorial method](CONTENT-METHODOLOGY.md) assigns statement
  disputes to a lead editor and requires two distinct human statement
  reviewers. It does not resolve the P1 relationship-specific case of a later
  dissenting verdict against an earlier pair of approvals, or define how that
  verdict binds a particular relation revision and operand versions.
- `content/schemas/relationship.schema.json` permits `approved`, `rejected`,
  and `needs_changes` review verdicts. `RelationshipRecord.validate` in
  `src/elecciones2026/schemas.py` checks for at least two distinct approved
  reviewer IDs when `review_status` is `approved`; it does not reject a mixed
  verdict set or require a resolution record. The relationship schema has
  statement IDs but no statement-version or relation-revision binding in each
  review entry. This is a technical gap, not evidence of a real disputed record.
- The current 2023 pilot pack says relationships are separately reviewed and
  adds none. Open draft PR #101 is conflicting with current main and has no
  GitHub reviews; PR #166 is a separate mergeable integration candidate with
  failed checks that did not start test steps. Neither PR supplies this missing
  editorial decision. Main CI at `8e2fab4` has a failed fork-isolation job;
  passing jobs are not editorial review.

## Reproduction with fictional data

On this snapshot, `PYTHONPATH=src python3` constructed an `es-gen-2023`
`RelationshipRecord` with two distinct human `approved` reviews followed by a
third human `rejected` review. Each review had a nonempty evidence reference;
the relation had `review_status=approved`, `status=active`, and fictional IDs.
Calling `validate(target_election_id='es-gen-2023', for_build=True)` with no
statement mapping returned `[]`. This isolates the verdict gate: it does not
demonstrate that a complete static build would accept those fictional
statements, nor that any real relationship has such reviews.

## Proposed review contract for owner decision

1. **Separate dissent from approval counts.** A `rejected` or `needs_changes`
   verdict for the current exact relation revision should leave the relation
   non-publishable until a recorded human resolution and renewed review. Two
   earlier approvals must not silently outvote an unresolved objection.
2. **Bind each verdict to immutable inputs.** The future review packet should
   identify the election, relation revision, both statement IDs and versions,
   policy question, relationship type, grounds, qualifications, and evidence
   reference. Editing any operand or material ground should create a new
   review target; old verdicts remain in history but do not approve the new
   target. No private review evidence belongs in Git or the public build.
3. **Record resolution without self-approval.** The editorial owner should
   decide who may resolve a dispute, whether the resolver can also be one of
   the required relation reviewers, the number of fresh approvals, and how
   conflicts of interest are handled. The existing statement lead-editor rule
   is a reference, not an automatic relationship policy.
4. **Keep display states honest.** Until a relation has current approval,
   separately approved statements may appear only if their own source, rights,
   and publication gates pass. The comparator must not present agreement,
   divergence, or partial overlap from a disputed relation. A missing relation
   is not opposition or a reviewed absence conclusion.

## Acceptance cases for a later reviewed spec/design/tasks update

| Fictional case | Required outcome to specify and test |
|---|---|
| Two approvals, then one current rejection | Relation withheld pending recorded resolution; approvals retained as history. |
| Two approvals, then `needs_changes` | Relation withheld; changed revision needs review of the changed exact pair and grounds. |
| Objection refers only to an older revision | Old revision remains auditable; no verdict is silently transferred to a newer revision. |
| One statement version changes after approval | Relation invalidated; new exact operand pair needs independent approval. |
| Two statements approved but relation disputed | Individual statements may pass their separate gates; no comparative claim passes. |

Before implementation, reconcile this contract with the existing MVP schema and
the pending PR #101/#166 integration path. The owner/editorial team must decide
the quorum, conflict-resolution authority, immutable review packet, and private
evidence-retention rules. Then update the `2023-corpus-completion` comparison
spec, design, and tasks and review them before code or real records change.
This audit does not check any OpenSpec completion box or grant G0/G2/G4.
