# 2023 document-discovery evidence handoff — 2026-10-27

Roadmap package: **P0.4, proposal-only** under
[`2023-corpus-completion`](../openspec/changes/2023-corpus-completion/proposal.md).
This is a bounded review packet for the discovery-attempt and `not_located`
contract. It is not an approved search protocol, a completed inventory, a
rights decision, or permission to implement or publish a coverage claim.

## Reconciled baseline

At `origin/main` `8e2fab4`, `content/sources/register.json` has four
`es-gen-2023` pilot source rows: PP, ERC, PNV and Sumar. Each is scoped
`general`, has status `published-unverified`, an unknown publication date, and
`rights_review.status = not_reviewed`. These rows are neither an approved
candidature denominator nor evidence that other programmes or annexes were
absent. The [P0 design](../openspec/changes/2023-corpus-completion/design.md)
already calls for retained search attempts when a document is unlocated, but
does not yet define the attempt record, search boundary or reviewer disposition.
The [official-enumeration handoff](2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md)
has not established an approved 2023 candidature manifest.

Draft PR [#101](https://github.com/c2ventures/elecciones2026/pull/101)
remains open, conflicting and without a GitHub review at this check. Its old
green checks test that branch, not a reconciled merge with current main. Its
PP/ERC summary and schema edits are outside this package. Main's [latest CI
run](https://github.com/c2ventures/elecciones2026/actions/runs/40179863768)
at `8e2fab4` has a failing fork-isolation/deploy-credential job; the other
three test, browser and image jobs passed. This packet does not infer a cause
or waive either gate. Open PRs #149, #150, #151, #155, #157, #158, #163 and
#164 already cover rights withdrawal, source identity, document applicability,
correction, comparison, coverage projection and pilot-rights documentation.
This packet does not edit their files or decide their questions. It does not
recheck remote publisher pages or private source files.

## Proposed discovery unit and evidence, for review

One private discovery ledger entry should be keyed by election ID, approved
inclusion-rule revision, candidature ID, expected document role and territorial
scope. The role is a *search target*, not an assertion that a document exists.
Coalition and member-party targets need distinct keys until the owner approves
their mapping. Each attempt should retain:

- search date, investigator, exact search surface or official publisher route,
  query or navigation path, language and territorial scope;
- an evidence reference to a dated private capture or official index, plus
  the result (`candidate_found`, `no_result`, `inaccessible`, or `ambiguous`);
- candidate URL/identity when found, without treating a search hit as an
  authentic programme, a lawful reuse decision or a verified publication date;
- unresolved leads, redirects, inaccessible pages and a reason for the next
  search or the proposed stopping point.

Keep captures, source bytes, extracted text and access credentials in the
owner-approved private store, not this repository or the static build. A
stable, non-sensitive reference is enough for a later reviewed inventory row.
The ledger must distinguish a publisher's explicit statement that no document
was issued from a tool returning no hits; neither automatically establishes a
party's policy position.

## Proposed state transition and invalidation

`search_pending` is the default for an included candidature/document role.
`candidate_found` means a possible document awaits the independent source
identity, version and rights gates. `search_exhausted_pending_review` means
the investigator followed the owner-approved surfaces and stopping rule but
has not obtained a reviewer decision. Only a named human reviewer may record
`not_located_as_of(date, protocol_revision)` after examining attempts and
unresolved leads. The label means the approved search did not locate a
qualifying document by that date; it does **not** mean no programme existed.
An inaccessible official source or unresolved coalition/territorial mapping
must remain unresolved, not become `not_located`.

Changing the inclusion rule, search protocol, relevant publisher route or
official index, or finding a new source must invalidate the affected
disposition and downstream coverage projection. A later source does not erase
the earlier attempt history. Neither `not_located` nor an empty source row
licenses `not stated`, opposition or topic-completeness wording; those need
the separate P1 topic-search and editorial gates.

## Fictional acceptance cases for a reviewed future spec

1. A qualifying constituency candidature has no registered PDF. It remains in
   the denominator with `search_pending`, not omitted from coverage counts.
2. An official search index returns zero results but a territorial publisher
   route is unsearched. The state remains pending; no absence label appears.
3. A coalition landing page names a member party but gives no programme link.
   Mapping and document discovery remain ambiguous, not silently joined.
4. A candidate URL redirects to a revised PDF. Both versions and their dated
   observations remain traceable; the new bytes require identity and rights
   review independent of the old version.
5. A reviewed, dated `not_located` disposition is followed by a newly found
   annex or a changed search protocol. The old disposition remains auditable
   but cannot support current coverage or a public absence statement.
6. A source is found but cannot be fetched. Discovery can report a candidate;
   hash, publication date, rights and proposal coverage remain unknown.

## Review and implementation boundary

The owner/editorial team must approve the eligible-candidature and
document-role rules, official search surfaces, repeat-search cadence,
stopping rule, coalition/territorial mapping, private evidence retention,
reviewer role and exact reader-facing wording. After that, revise the
OpenSpec provenance requirement, design and tasks and reconcile with open
P0 PRs and #101 before implementation. Use fictional fixtures first. This
packet changes no register, schema, source status, political content, public
artifact, routing or deployment; CI can verify a future ledger's mechanics,
not certify the completeness of a real-world search.
