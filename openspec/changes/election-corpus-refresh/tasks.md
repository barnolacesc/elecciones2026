# Tasks — E1.4-2026

## 1. Election-scoped technical preparation

- [x] 1.1 Add explicit production record loading and real-source gates; verify empty, cross-election, fixture and unverified-source cases in generator tests; document incremental record layout.
- [x] 1.2 Default container preview to the 2026 production corpus; remove the historical programme inventory from that view and verify HTML/browser-payload election isolation and deterministic hashes.
- [x] 1.3 Prepare the existing authenticated staging candidate pipeline for the 2026 approved-record input; bind candidate election/mode consistently, retain historical rollback compatibility and reject public classification. This technical path does not grant editorial or public release approval.

- [x] 1.4 Support a versioned election-specific taxonomy in production record directories, validate topic/subtopic membership and reject draft/cross-election definitions. Keep the private 12-topic proposal out of the production input until editorial acceptance.

## 2. Private source intake and editorial completion

- [x] 2.1 Reconcile the eight local originals with registered hashes, run permitted isolated extraction and record per-document results and unresolved blockers without committing full text.
- [x] 2.2 Read every eligible programme completely; enumerate every substantive point with page/section, qualifications and taxonomy mapping in private review records. Verify page coverage and account explicitly for unmapped and unreadable content.
- [ ] 2.3 Obtain source identity/reuse decisions and two independent human reviews of every publishable statement and relationship; import approved records and verify the strict production build. Do not grant review marks automatically.

## Evidence

2026-11-11: Seven production migration tests pass, including disk-based incremental
loading, human approval/content-hash checks, fixture and cross-election rejection,
atomic failure, empty coverage, and two-build hash equality. Generator tests (13)
and generated source/method page tests (11) also pass.

The Docker builder and runtime build succeed; all 12 Docker configuration and
live container tests pass. The hardened local runtime on
`http://localhost:47486/` returns HTTP 200; `nginx -t` passes. The runtime check
identified and fixed an unquoted regex quantifier in the existing Nginx config.

Full suite: 521 tests, 17 skipped, two pre-existing failures, both reproduced on
base commit `35fc31c`: `test_delivery` expects a delegated authorization that
expired on 2026-10-31; `test_provisional_2023` expects obsolete source-link text.
These unrelated historical release tests were not weakened. Browser interaction
was not verified; HTML and the browser data projection were checked.

All eight original hashes match. Six private extractions verify (341 physical
pages). [Intake evidence](../../../docs/2026-CORPUS-INTAKE-2026-11-11.md) records
the Coalición Canaria size blocker and SALF active-content blocker. Full point
enumeration, empty-page visual checks, source identity/reuse decisions and human
reviews remain pending. No claim, merge, deployment or release was approved.

## Delegated private review (owner request, 2026-11-11)

The owner explicitly requested Antigravity workers through `agy` with
`--dangerously-skip-permissions`. Eight private assignments were prepared:
six complete programme inventories and two bounded extraction investigations.
The coordinator runs at most three workers at once, with one source and one
private output directory per worker. Shared Git files and original archive
objects are read-only to workers. No worker can publish, commit, change rights,
grant human approval, or weaken shared PDF processing controls.

Private dispatch run: `20261111T213914Z`, under the source archive's
`programme-review-runs/` directory. Structural coordinator checks cover source
identity, all physical page rows, unique point IDs, taxonomy assignments,
exact evidence substrings and page hashes. A second machine review is distinct
from the required human editorial review. Task 2.2 remains open until actual
coverage and unresolved extraction limits have been reconciled.

Coordinator remediation: all eight originals now have private page text
(404 physical pages). Coalición Canaria's exact-hash private route passed the
active-content scan with a 75 MiB input limit, bounded 160 MiB scratch space
and the same pinned networkless image. SALF's two raw scan hits were confirmed
inside one compressed raster image payload; an exact-hash private worker also
required empty `pdfinfo -js` output and zero embedded files before extraction.
The shared scanner and default limits remain unchanged. Scripts and manifests
are private run artifacts, not public inputs or source-rights approvals.

Seven previously empty-text pages were rendered in the isolated image and
inspected as blank/cover/decorative material. This automated visual check is
recorded privately with image hashes and does not grant human review. Draft
inventories and correction passes are still in progress; partial counts are
not evidence of completed point coverage.

2026-11-12 recovery: several Antigravity turns ended with provider network
errors and later HTTP 401 responses. A fresh connection probe succeeded.
Six failed conversations were resumed from private checkpoints, retaining
the three-worker limit and adding a 20-minute per-turn cap. No source or
political approval was inferred from a process exit status.

Coordinator checks rejected inconsistent page ledgers in ERC and Frente
Obrero. A separate PP editorial pass was requested because source paragraphs
had been copied into summary fields. These drafts are excluded from the
private neutral-summary packet until their corrections pass. Private source
extracts and earlier versions remain available for audit.

## Final private draft reconciliation (2026-11-12)

Task 2.2 machine preparation is complete. The canonical eight inventories contain
1,644 draft measures across all 404 physical pages: BNG 513, Coalición Canaria
100, ERC 228, Frente Obrero 150, Partido Humanista 58, EAJ-PNV 225, PP 244 and
SALF 126. Counts are inventory units, not approval or party-quality scores.
Coordinator validation passes for every canonical inventory: exact evidence
substrings, page hashes, unique IDs, election/source/version binding and
bidirectional page ledgers. No substantive page is left without a recorded point.
This structural evidence does not prove semantic completeness or human approval.

Correction passes reconciled the ERC/Frente Obrero ledgers, replaced the PP
summary draft, preserved its source qualifications, and incorporated the
Humanista peer-review findings. Earlier drafts remain private audit artifacts.
The canonical manifest freezes points and coverage hashes; the source-integrity
audit verifies unchanged originals. The private `editorial-packet/README.md`
links the eight neutral-summary packets and their original page references.

The current taxonomy leaves 99 draft topic/subtopic gaps. A separate private
proposal supplies all 99 mappings and an index of all 1,644 points using 12
topics and 64 subtopics. Existing IDs and Spanish labels are preserved. This
proposal has not changed the runtime taxonomy (8 topics / 40 subtopics).
Existing assignments still need editorial harmonization if the extension is
accepted; automated grouping does not establish agreement between parties.

Task 2.3 remains open. All eight source records remain unverified for publication;
source identity, edition, reuse and missing publication dates need decisions.
Every publishable statement and comparison relationship still requires two
independent human reviews. The blank private decision form records no invented
reviewers or approvals. No draft measures were added to production records,
committed, merged or deployed. The local preview therefore continues to show
pending reviewed proposals. [Completion evidence](../../../docs/2026-CORPUS-DRAFT-REVIEW-2026-11-12.md)
contains counts and boundaries only, not political source text.

## Workflow follow-up

- Obtain the applicable release gate before deployment, publication or merge.
- Retain the previous immutable serving artifact for rollback.

## Publication preparation requested on 2026-11-12

The owner requested continuation and publication today. This is operator intent;
it does not supply the missing source decisions or individual human reviews.
The coordinator continued technical preparation without marking task 2.3 done.

The two historical suite failures have been corrected: original-document links
now announce their new-tab behavior, and the delegation test checks both sides
of the 2026-10-31 expiry using a fixed clock. The live authorization deadline is
unchanged. Full standard-library suite: 521 tests pass, 17 skipped. The skipped
checks are not claimed as verified.

A separate automated Chromium pass against the local Docker preview on port
47486 passes 76/76 checks at 360, 390 and 430 px. It checks keyboard skip links,
selection of PP/ERC, seven routes, horizontal overflow, script errors and absence
of historical/fictional programme records. It verifies the pending-record state,
not the 1,644 private political drafts. Evidence remains under `.dockyard-state/`.

Three bounded Antigravity tasks recheck source identity, audit the actual release
path and prepare offline private draft conversion. Permission bypass is enabled
at the owner's request; worker limits are instructions, not an enforced sandbox.
No deployment, rights changes or human review marks are delegated.

Final coordinator evidence: 534 standard-library tests pass, 17 skipped. The
14 delivery tests cover current 2026 metadata, historical recovery, mismatched
modes and public classification rejection. Nine corpus-refresh tests include
extended taxonomy membership, draft/cross-election taxonomy rejection and
unchanged human approval requirements. Nine staging tests cover corrupt hashes,
missing metadata, exact page coordinates, classification tampering, permissions,
atomic failure and repository/output boundaries. The mock quiz CLI build also
succeeds with the 2026 production context; it remains an opt-in private fixture.

The owner-requested source recheck found a new publisher-linked BNG revision.
The coordinator acquired and extracted it with the unchanged allowlisted,
bounded, networkless pipeline. Its hash is
`1ab47bae90bd6de4be2cd42e1999c635757359ef9789a6c402ba7d64d9530432`.
All 91 physical pages remain present; extracted page text differs only on page 2,
which was rendered and inspected as contents. No draft measure cites that page;
all 513 measures retain exact evidence/page hashes. Register v1 remains as
replaced history; production excludes replaced sources and selects BNG v2.
No publication date or rights approval was inferred from an upload timestamp.

The refreshed private corpus is in run `20261111T213914Z`, beneath
`publication-preparation/current-corpus-v2`. It preserves the preceding run and
BNG draft lineage. All eight originals were rehashed; all 404 page text hashes
and all canonical inventories pass coordinator checks. All 1,644 converted
statement drafts validate structurally against the proposed 12/64 taxonomy.
The strict production loader correctly rejects the full draft set. The staging
utility verifies the prior original-integrity audit; it does not itself claim
to have rehashed source bytes. Private evidence excerpts are separate sidecars.

Frente Obrero remains held for election-specific identity: the inspected document
is headed as a political programme without evidence establishing the 2026
edition. A live source link is also unavailable at the registered direct URL.
These findings do not establish its election date or authorize publication.
The refreshed private decision form retains blank source/reviewer decisions.

Read-only origin inspection confirms valid Nginx syntax and a preview-only
server block with authentication. No public apex/www server block is present.
Live apex/www responses are 521; private preview responds 401. Root SSH read
access succeeded; no origin, DNS or live container setting was changed. The
owner GitHub actor is available, so the expired historical bot delegation does
not block owner dispatch. Public activation, G4 evidence and actual political
approvals remain outstanding; do not deploy the existing historical image
through the public hostnames.

## Hosted integration follow-up

PR #237's first CI run (`43319062318`) passed the Python/Node data and security
validation job, but failed two integration checks. The Docker workflow still
expected immutable caching for stable CSS; it now checks CSS revalidation and
immutability of the actual fingerprinted comparison bundle. The quiz's synthetic
long-source fixture expected two links although three non-null positions exist;
the test now checks the actual fixture count and requires multiple parties.
That repaired check exposed fieldset/answer reflow at 320 px with 200% text; the
intrinsic minimum width and long-word wrapping were corrected without weakening
touch-target, clipping or contrast assertions.

Local browser rerun passes the complete mock flow and long-source metadata
regression, six privacy cases, and 67 keyboard/semantic/contrast checks. The
current local Docker preview was rebuilt with BNG v2, eight active source
objects, and build date 2026-11-12; 76/76 mobile checks pass again. CSS uses
no-cache; the current comparison bundle is immutable; robots uses 3600 seconds.
Production derives its default build date from the versioned source register,
which removes a stale fixed Docker date. These remain private/pending artifacts.

The extended-taxonomy test now renders the whole synthetic site and browser
payload, rather than checking only record loading. Full page locators remain
visible; PDF fragments open the first physical page instead of invalid range
fragments. No real political approval was used for this synthetic verification.

A final metadata audit removed inferred parliamentary inclusion and territorial
scope from source-only party entries: both are pending verification until a
reviewed party record provides them. Production pages identify project records
rather than claiming an official party registry, and omit unverified legal-name
structured metadata. This corrects metadata defaults, not political statements.
The mock performance observation still misses its 500 ms cold-delivery target
(about 1.1–1.2 seconds under emulated latency/CPU); warm cases meet it. Exit code
zero for the measurement script is not a performance release approval.

The second hosted run (`43320432318`) passed data/security and browser jobs but
found that fingerprinted quiz assets did not receive their expected immutable
cache headers. The existing comparison-only rule is retained; an earlier rule
now covers fingerprinted quiz/simulator JS and CSS while stable names still
revalidate. Local immutable-asset tests and all 19 owned-loopback rollback and
withdrawal checks pass (about 0.7 seconds for the measured rollback). This fixes
the runtime policy rather than relaxing the recovery assertion. No remote host
or public cache settings were changed.
