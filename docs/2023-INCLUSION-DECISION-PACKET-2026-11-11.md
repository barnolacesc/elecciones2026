# 2023 candidature inclusion: owner decision packet

Roadmap package: **P0.1**, `2023-corpus-completion` (proposal-only). This is a
review form, not an adopted policy, an enumerated manifest, a rights decision,
or permission to publish a political claim.

## Evidence boundary at 2026-11-11

Fetched `origin/main` is `488b6f5`. Its `es-gen-2023` source register has four
pilot rows (PP, ERC, PNV, Sumar): all `published-unverified`, all rights
`not_reviewed`, and all with `publication_date: null`. The four coverage
examples do not define a national denominator. Six of eight 2023 statement
examples are `under_review`; the other two are `draft`. All six 2023
relationship examples are `invalidated`. These are repository-record counts,
not findings about which other candidatures had programmes.

The [official-enumeration handoff](2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md)
identifies the 2023 proclamation notice, two linked corrections, and the
presented-versus-proclaimed distinction. It did not enumerate every Congress
constituency, check later changes, or certify a final list. The
[product roadmap](PRODUCT-ROADMAP-2023-2026.md) requires an owner-approved,
versioned inclusion rule before any complete-coverage claim. Neither the
four-party pilot nor draft PR #101 establishes that rule. PR #101 is still open
and conflicting; its technical gate was separately integrated by merged PR
#166, but its old checks are not a current rights or editorial review.

This packet reuses repository and GitHub metadata only. It did not inspect
private PDFs, publisher sites, election results, or reviewer evidence.

## Decisions to record before enumeration

For each item, the human owner should record a choice, rationale, decision
date, approver identity, evidence reference, and policy revision. **Blank is
unresolved; an automated run must not fill it.** The options are prompts, not
recommendations.

| ID | Decision needed | Options or boundary to resolve | Current decision |
|---|---|---|---|
| D1 | Election/chamber scope | Congress only, or Congress and Senate in separate inventories; never silently combine chambers. | Unresolved |
| D2 | Inclusion threshold | All finally proclaimed candidatures, a defined parliamentary-force subset, or another explicit rule. State how exceptional and territorial lists are treated. | Unresolved |
| D3 | Counting unit | Constituency-level ballot candidature versus a separately deduplicated national/coalition display group. State which is the denominator; keep the two identities distinct. | Unresolved |
| D4 | Coalition and shared-document mapping | Specify how ballot names, component parties, territorial variants, joint programmes, annexes, and replacements map to sources; do not inherit one candidature's review or rights from another. | Unresolved |
| D5 | Finality and corrections | Name the authoritative notice/result cross-check, cut-off/search protocol, correction order, reviewer quorum, and handling of later changes. | Unresolved |

**Decision record to complete:** policy revision `_____`; owner `_____`;
decision date `_____`; D1–D5 choices and rationale `_____`; primary evidence
references `_____`; independent checker `_____`; unresolved exceptions
`_____`. Source authenticity, reuse rights, topic taxonomy, statement review,
relationship review and release need separate decisions; this form cannot
substitute for any of them.

## Review handoff and acceptance

1. The owner and checker review the exact rule and evidence references. If any
   D1–D5 answer remains open, keep `denominator_unresolved`; do not calculate
   a coverage percentage or describe the four pilot rows as exhaustive.
2. Only after the rule is approved, enumerate the authoritative candidature
   rows with source section/page and apply each correction as an auditable
   amendment. The Teruel PACMA proclamation correction and Baleares Sumar Més
   ballot-name correction from the handoff are mandatory spot checks, not the
   whole manifest.
3. Independently peer-check the resulting manifest, then map each included
   candidature to relevant programme versions, annexes, replacements, or an
   evidenced unresolved search. A candidature row is not proof of a programme
   or reuse permission. Keep the original bytes and private evidence outside
   Git and the public build.
4. Reconcile the approved rule and manifest with the draft OpenSpec
   requirement/design/tasks before implementation. Test missing, partial,
   replaced, territorial, shared-document and correction cases using fictional
   fixtures. A passing test is engineering evidence, not human approval.

This packet changes no source, rights, statement, relationship, coverage,
public route, deployment or release state.
