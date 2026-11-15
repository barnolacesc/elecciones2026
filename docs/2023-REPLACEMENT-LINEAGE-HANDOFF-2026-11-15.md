# 2023 source-version replacement lineage handoff — 2026-11-15

Roadmap package: **P0.11, proposal-only** in `2023-corpus-completion`.
This packet addresses version-lineage integrity, not whether a particular
programme was official, available before 23J, reusable, or editorially approved.

## Reconciled baseline

`origin/main` is `d13ba683` at this check. The source register has four
`es-gen-2023` pilot rows, all `published-unverified`, all with
`rights_review.status = not_reviewed`, and none with a replacement-history
entry. They are not a complete candidature/document denominator. The current
`source_register.load_register_from_dict` checks that a `replaced` row has a
nonempty history and checks each history entry's field shape. It does not
resolve `superseded_by` against a source ID, check the election or document
scope of a target, reject cycles, or establish that a prior version's bytes
were actually the same document. These are validation boundaries, not evidence
that a 2023 replacement record is currently wrong.

Draft PR [#101](https://github.com/c2ventures/elecciones2026/pull/101) is still
open, conflicting and has no GitHub review. A merge-tree simulation against
this main reports six conflict paths (review README and handoff, MVP tasks,
generator, and two pilot tests). Its October CI success does not test the
combined tree. The latest main [CI run](https://github.com/c2ventures/elecciones2026/actions/runs/43325747158)
passed on `d13ba683`; it does not approve a source or resolve PR #101. No
private PDF, publisher page, rights evidence or editorial record was inspected.

## Proposed review boundary

A future private inventory should distinguish a *version identity* (election,
reviewed document scope, publisher/candidature applicability, source ID and
exact hash when bytes exist) from a *transition event* (prior version, successor,
reason, observed date and evidence). A first registered version may refer to
an unarchived earlier lead; that is an unresolved predecessor, not a fabricated
verified source. An event only establishes a replacement after a human source
review accepts the exact versions and scope. Same URL, later filename, newer
retrieval, or equal hash alone cannot do so. A successor may replace one
territorial annex without replacing the whole general programme.

The proposed reconciler should reject missing or ambiguous target IDs,
cross-election edges, incompatible document scopes, self-edges, cycles and two
incompatible successors claimed effective for the same predecessor/scope.
Where legacy history cannot identify an exact predecessor, retain it as an
unresolved lead and withhold replacement-derived coverage conclusions. Do not
silently convert old event-log fields into graph edges. A reviewed successor
invalidates only dependent source locators, statements, comparisons and search
coverage within its accepted scope; the old version and decisions remain for
audit, and rights/editorial approval never transfers automatically.

Fictional checks for a later implementation: a valid two-version chain; an
unresolved pre-registration predecessor; a target in another election; a
self-edge and a two-edge cycle; simultaneous incompatible successors; and a
territorial annex replacement that leaves the general document in scope.

## Decisions and limits

The owner/source reviewers must decide document identity and scope, whether
parallel language editions count as versions or distinct documents, effective
time and correction policy, predecessor evidence for legacy rows, and reviewer
segregation. Reconcile these decisions with P0.4 source authenticity, P0.9
temporal provenance, P1.4 applicability and PR #101 before any schema or
validator implementation. This draft grants no rights, source status,
political-content approval, public release or change to the source register.
