# P0.5 draft: separate 2023 eligibility, document and display units

Status: proposal-only decision packet for `2023-corpus-completion` P0/P1 review.
Election: `es-gen-2023`. Baseline: `origin/main` `8e2fab4` and GitHub PR
metadata checked on 2026-10-28. This packet neither approves an inclusion rule
nor enumerates a complete candidature manifest, source inventory or position.

## Evidence and current blocker

- The [BOE proclamation notice](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066)
  publishes Congress and Senate candidatures by constituency. Its
  [4 July correction](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15548)
  changes a Baleares Congress coalition ballot name; its
  [7 July correction](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15828)
  changes a Teruel Congress entry from unproclaimed to a candidate list.
  These primary records were opened on 2026-10-28. The existing
  [enumeration handoff](2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md)
  has not checked every row, later official changes or finality.
- Main's source register contains four `es-gen-2023` pilot source rows (PP,
  ERC, PNV, Sumar), each `published-unverified`, rights `not_reviewed`, and
  publication date unknown. These are document records, not a frozen
  candidature denominator. Eight statement examples remain six
  `under_review` and two `draft`; six relationship examples are `invalidated`.
- Draft [PR #101](https://github.com/c2ventures/elecciones2026/pull/101)
  remains conflicting with main and has no GitHub review. Draft
  [PR #166](https://github.com/c2ventures/elecciones2026/pull/166) proposes a
  current-main replacement for its E1.4 gate; it also has no GitHub review.
  Neither branch supplies the P0 inclusion decision or source rights. The
  [PR #166's CI run](https://github.com/c2ventures/elecciones2026/actions/runs/40497081984)
  has test and browser jobs that never started: their check-run annotations
  report an account payment/spending-limit block. A failed check here is not
  an executed test result.

## Decision to make before any coverage percentage

The owner must choose and version the *eligibility unit* separately from the
*source-document unit* and the *reader-facing comparison unit*. The following
is a proposed review route, not a selected rule:

1. **Eligibility ledger:** consider one corrected, proclaimed Congress
   candidature per constituency as the auditable input row. Keep chamber,
   constituency, exact ballot name, original notice locator, each applicable
   correction and proclamation status. This avoids silently dropping a
   territorially limited list or treating a Senate entry as a Congress row.
   The owner must decide whether Congress-only is the product's scope and
   whether any exception is justified.
2. **Identity mapping:** map those rows to stable candidature identities only
   under a reviewed coalition/territorial rule. The same ballot label in
   several constituencies need not imply several independent programmes;
   conversely, an umbrella label need not prove one national document applies
   everywhere. Preserve the many-to-many row-to-identity mapping and its
   evidence rather than deduplicating names automatically.
3. **Document ledger:** discover each general programme, territorial annex,
   coalition document, replacement and unresolved search independently.
   Bind document applicability to the reviewed candidature identities and
   geography. Source authenticity, publication-date evidence, rights for
   each proposed use, and topic-search review remain separate decisions.
4. **Display projection:** only after the identity and document joins are
   approved, decide which candidature grouping a reader may select and what
   exact source scope its comparison represents. A display grouping must
   not change the eligibility denominator or imply a single party-wide
   position where territorial or coalition scope differs.

Two possible denominators must not be conflated: corrected proclamation rows
answer “which constituency-level candidatures met the eligibility rule?”;
reviewed candidature identities answer “which distinct comparison actors are
in scope?”. Document and topic coverage have their own denominators. Until the
owner fixes the rule, mappings and finality check, report raw pilot counts
and `denominator_unresolved`, not “all parties”, “all programmes” or a
percentage. A missing programme means discovery is unresolved, never that a
candidature opposed a measure.

## Draft requirement, design and task handoff

**Requirement delta for review:** A 2023 completeness claim SHALL identify
its approved eligibility rule revision, official proclamation/correction
revision, counting unit, candidature identity mapping revision, document
scope and review stage. A name-only deduplication or source-register party ID
SHALL NOT establish the denominator. A changed proclamation status, ballot
name or mapping SHALL invalidate dependent coverage totals while preserving
the earlier evidence. No source or topic absence is inferred from an
eligibility row.

**Design boundary:** keep the official row, reviewed actor mapping and
document applicability as separate versioned records. Produce a reconciliation
report with unresolved rows/mappings and no percentage when a prerequisite is
pending. Keep private PDF bytes and review evidence outside Git and the
public build. Fold the reviewed delta into `2023-corpus-completion` specs,
design and tasks before any schema, importer or public-coverage implementation;
do not implement from this packet alone.

**Fictional acceptance cases for the later reviewed contract:**

- A correction changes an unproclaimed Congress row to proclaimed; the old
  and new statuses remain traceable and counts are recalculated only after
  review.
- A corrected coalition ballot name preserves the original row and does not
  automatically merge its programme with another constituency's documents.
- Two constituency rows map to one reviewed actor but have different annexes;
  neither the row count nor document count is silently used as an actor count.
- A Senate-only row cannot enter a Congress-only denominator. An unresolved
  coalition mapping or unsearched official correction prevents completeness.
- One included actor has no located programme; it remains in eligibility
  accounting with unresolved discovery, not a `not stated` policy position.

**Owner/editorial decisions still open:** election/chamber scope, authoritative
finality-search protocol, correction reviewer, constituency-to-actor grouping,
coalition and territorial exceptions, document applicability, private evidence
store, source-rights owner, and the exact public coverage wording. After these
decisions, peer-check the full manifest and document joins. PR #101/#166's
E1.4 statement gate is independent; use neither CI nor this packet as human
approval, and do not merge both replacement branches.

Validation for this documentation-only packet: parsed the main register and
example records with Python 3, inspected the primary BOE notices and GitHub
PR metadata, and ran `git diff --check`. Project pytest was not run locally:
this host has Python 3.11 and no pytest, while the project requires Python
3.14. No private PDF, political wording, source record, approval, routing or
public build was changed.
