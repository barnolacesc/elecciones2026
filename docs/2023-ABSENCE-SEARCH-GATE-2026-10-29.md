# 2023 absence-search publication gate — review packet

Roadmap package: **P1.8**, `2023-corpus-completion` (proposal only).
Election scope: `es-gen-2023`. This packet proposes a narrow acceptance gate
for a reader-facing “not stated” conclusion. It does not approve a search,
political position, rights use, implementation or publication.

## Reconciled evidence (2026-10-29)

- `origin/main` was `8e2fab4`. `content/sources/register.json` contained four
  2023 pilot rows (PP, ERC, PNV and Sumar), each `published-unverified`, rights
  `not_reviewed`, and with no evidenced publication date. The eight 2023
  example statements contained zero `not_found` and zero approved records.
  These counts do not establish a 2023 candidature or topic denominator.
- Draft PR #101 remained open, unreviewed and conflicting (`dirty`) at
  `f8506a1`; draft PR #166 proposes a superseding integration. Neither
  supplies a reviewed 2023 absence search. PRs #163 and #165 address coverage
  projection and document discovery, respectively; this packet addresses the
  distinct decision to publish a *negative topic-search conclusion*.
- The draft 2023 editorial spec already requires relevant document versions,
  searched scope, method, reviewer and unresolved exclusions before
  `not_found`. However, `StatementRecord` and `statement.schema.json` contain
  no search-dossier reference. The current `not_found` validation checks
  wording and absence of quote/page coordinates, not whether the relevant
  source set was actually searched. The fictional 2026
  `statement-housing-not-found.json` has no search-evidence field and
  `StatementRecord.validate(target_election_id="es-gen-2026")` returns no
  errors. This is a **contract gap**, not evidence of a false live 2023 claim.
- At the inspected main commit, the five check runs included three successes,
  one skipped private publication and a failed fork-isolation check. PR #101's
  historical green checks test its old head, not an integrated candidate.
  No CI result or fixture review is human editorial approval.

## Proposed requirement for OpenSpec review

A public `es-gen-2023` `not_found` statement SHALL refer to an immutable,
human-approved absence-search dossier for its exact election, candidature,
policy question, taxonomy revision and relevant document versions. The dossier
SHALL record the approved source-set boundary, searched pages/sections and
methods, search date, reviewer decision, unresolved exclusions and a private
evidence reference. A search of only one document, an empty extraction queue,
or a review note saying “searched” SHALL NOT by itself satisfy the gate.

The dossier SHALL distinguish **no supported candidate found after approved
search** from **not searched**, **partial search**, **unlocated document**, and
**source/rights unresolved**. The reader-facing wording and whether any
negative conclusion may be displayed while rights remain pending need owner
and editorial review. No absence state implies opposition. A new relevant
annex, replacement, corrected OCR/source text or changed taxonomy/question
SHALL invalidate the conclusion until the search scope and decision are
reviewed again.

## Proposed design and tests (not implementation authorization)

Keep a private, versioned search dossier separate from the statement and
source register. It should reference the approved P0 candidature/document
manifest, record non-textual method and scope metadata in Git only if safe,
and keep source bytes, OCR output and review evidence in the private store.
The public build should receive only an approved conclusion and its honest
coverage limitation, never the dossier's extracted text. A validator should
join an exact dossier revision to each candidate public absence statement
and fail closed on stale, incomplete or disputed search evidence.

Acceptance cases for fictional fixtures:

1. Main programme searched, relevant annex unsearched: no `not_found`.
2. Extraction returns no candidates, but human search is pending: no
   `not_found`.
3. All approved relevant versions searched and independently reviewed:
   conclusion is eligible for a separate wording, rights and publication
   decision; the search alone does not publish it.
4. A replacement or taxonomy change occurs after approval: the former
   conclusion is invalidated, with the old dossier retained for audit.
5. A document cannot be located: report unresolved source coverage, not a
   negative position.

## Tasks and decisions still open

1. Owner/editorial reviewers define the search stopping rule, relevant-source
   scope, OCR/manual verification threshold, review quorum, and public wording.
2. After PRs #163/#165 and the PR #101/#166 integration path are reconciled,
   add this requirement and the accepted cases to the formal 2023 OpenSpec
   spec/design/tasks. Do not implement from this packet alone.
3. Only after that OpenSpec review, implement fictional dossier fixtures and
   fail-closed validation; then seek separate human review for real sources,
   rights, statements and release.

No source register, PDF, political answer, review mark, public route or runtime
behavior changes in this package.

## Local validation

- `PYTHONPATH=src python3 -m unittest discover -s tests -p
  'test_editorial_gates.py' -q`: 20 passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests -p
  'test_editorial_policy.py' -q`: 22 passed.
- Direct validation of the existing fictional 2026 `not_found` fixture returned
  `[]`; its JSON contains no search/scope evidence key. This only demonstrates
  the current technical contract gap.
- The 2023 pilot rehearsal suite could not import under the available Python
  3.11.2: `generator.py` uses an f-string form requiring the project's Python
  3.14 target. This is a local interpreter limitation, not a test pass.
