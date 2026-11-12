# Private corpus draft preparation — 2026-11-12

Roadmap package: E1.4-2026. Run: `20261111T213914Z`.

The owner requested Antigravity workers through `agy` with
`--dangerously-skip-permissions`. The coordinator limited execution to three
concurrent workers and assigned each a private output directory. Repository
files and original documents were read-only in their task instructions. These
were instruction boundaries, not a claim that permission bypass enforces a
filesystem sandbox. Workers had no authorization to publish, grant editorial
approval, change rights, merge or deploy.

| Registered source | Physical pages | Draft measures |
|---|---:|---:|
| BNG | 91 | 513 |
| Coalición Canaria | 23 | 100 |
| ERC | 48 | 228 |
| Frente Obrero | 64 | 150 |
| Partido Humanista | 31 | 58 |
| EAJ-PNV | 43 | 225 |
| PP | 64 | 244 |
| SALF | 40 | 126 |
| Total | 404 | 1,644 |

Counts describe private inventory units. They do not confirm the documents'
election edition, political accuracy, reuse permission or human approval.

## Verification and private deliverables

All eight canonical inventories pass structural coordinator validation:
source/election/version binding, exact page evidence, page hashes, unique IDs,
complete physical-page ledgers and bidirectional page-to-point references.
There are no unaccounted substantive pages. Seven empty-text pages were
visually checked as blank, cover or decorative material. Machine checks cannot
prove that every political qualification or substantive point was understood.

The private source archive contains the dispatch logs, correction history,
canonical manifest, source-integrity audit, eight editorial Markdown packets,
and a blank human decision template. None contains an inferred human approval.
Originals and draft political content remain outside Git and serving artifacts.
The initial intake report records earlier blockers; the OpenSpec task record
records their exact-hash private resolution without changing shared PDF gates.

A private taxonomy extension proposes 12 topics and 64 subtopics and resolves
99 classification gaps. All 1,644 draft points have a proposed classification.
The current runtime remains on 8 topics and 40 subtopics. Existing assignments
need editorial harmonization if the proposal is accepted. Topic membership does
not establish agreement or disagreement between parties.

## Remaining publication prerequisites

Task 2.3 remains open: verify source identity/edition, decide lawful reuse,
resolve missing publication dates, obtain two independent human reviews for
each statement and relationship, then import approved production records and
verify the strict build. ERC and Frente Obrero have specific edition concerns.
No publication, merge or deployment is authorized by this machine preparation.
Technical test results and pre-existing suite failures are in the OpenSpec task
record. No qualified ASD-STE100 compliance claim is made.

## Current revision and technical preparation

The publisher-linked BNG revision acquired on 2026-11-12 has SHA-256
`1ab47bae90bd6de4be2cd42e1999c635757359ef9789a6c402ba7d64d9530432`.
It still has 91 pages; extracted text changes only on the contents page. All
513 draft measures retain exact cited evidence. Current private records are in
`publication-preparation/current-corpus-v2`; earlier artifacts remain intact.
Source-prefixed BNG v2 IDs retain explicit prior-point lineage. No new date,
source rights or human approvals were granted. The source register retains the
previous version as replaced history.

The offline converter produces 1,644 draft statement records with private
sidecar evidence and review fingerprints. A coordinator check finds no schema
errors against the private proposed 12/64 taxonomy. The production build rejects
those drafts. Election-specific taxonomy support is implemented, but the
proposal has not been accepted or installed as production content.

Frente Obrero's 2026 election-specific identity remains unconfirmed; the inspected
political programme and changed publisher links require a source decision before
its 150 draft measures can be considered for this election.

The CI candidate and authenticated staging validator now support the 2026 strict
record input and preserve historical recovery. This is not a public delivery
path. External DNS resolves, but apex/www return 521. Read-only host inspection
finds only the authenticated preview server block. No live configuration changed.
Full local suite: 534 tests pass, 17 skipped; 76 local Chromium mobile checks
passed before these later schema/source-metadata changes. No hosted CI success,
public release or human editorial approval is claimed by those local results.
