# PR #101 and source-use grant integration gate — 2026-11-16

Roadmap package: **E1.4 / P0–P1 integration evidence**. This is a bounded
engineering handoff for the PR #101 owner, not an editorial review, source-rights
decision, OpenSpec approval, or publication request. It complements the
[record-root handoff PR #238](https://github.com/c2ventures/elecciones2026/pull/238); it does not
change that PR, PR #245, the source register, public content, or routing.

## Reconciled baseline

- `origin/main` is `d13ba683888de17714ad958a8034916168889cc3` (merged #237).
  Its latest check run and Actions run `43325747158` passed. Those checks do not
  exercise a resolved PR #101 or the unmerged #245 changes.
- Draft PR [#101](https://github.com/c2ventures/elecciones2026/pull/101)
  remains at `f8506a10b6784edf597e9e315f4c000dc0d341af`, with no GitHub
  reviews. Its head checks passed, but they predate the current main tree.
  `git merge-tree --write-tree origin/main origin/pr-101` reports six conflict
  paths: `docs/pilot-review/2023/README.md`,
  `docs/pilot-review/2023/reuse-handoff.md`,
  `openspec/changes/mvp-programme-comparison/tasks.md`,
  `src/elecciones2026/generator.py`, `tests/test_pilot_editorial_audit.py`,
  and `tests/test_pilot_preview_acceptance.py`. This is a simulated merge;
  no conflict was resolved here.
- Open PR [#245](https://github.com/c2ventures/elecciones2026/pull/245)
  is at `3cef0254cd0dff6d4399615d10cce01897fcbd34`, with no GitHub reviews.
  Its checks passed. It proposes that `link_only`, `link_and_short_quote`,
  and `public_domain` grants require a nonblank reviewer, review date, and
  private evidence reference in the register parser and schema. It changes no
  actual source decision. `git merge-tree --write-tree origin/pr-245
  origin/pr-101` reports seven conflict paths, including the shared
  `src/elecciones2026/source_register.py` and editorial test. The branches
  cannot be combined by assuming the green checks on either head compose.
- The current `es-gen-2023` register still has four pilot source rows. All four
  have `rights_review.status=not_reviewed`, `status=published-unverified`, and
  `publication_date=null`. PR #101 leaves those values unchanged. These are
  pilot rows, not an approved 2023 candidature or programme denominator.

## Exact integration boundary

PR #101's fictional `link_only` publish test supplies a named reviewer, a date,
and `evidence_ref`, then checks quote-free output and rejection of a missing
reference. PR #245 separately requires that metadata for **every** grant state
at register-load time. A resolved branch must preserve both layers: a malformed
or unattributed grant fails schema/parser validation; a syntactically valid
fictional grant still passes the separate programme/source match, exact-content
editorial review, quote-use, and publication gates. Metadata presence is not
proof that a real person decided a real right. No automated reconciliation may
upgrade the four `not_reviewed` pilot rows or fill unknown publication/review
dates.

The PR #101 owner should reconcile on its own branch against current main and
whatever disposition PR #245 receives, then test the **resolved head**:

1. Fictional grant states with missing/blank reviewer, date, or private
   evidence reference fail both register parser and JSON Schema validation;
   pending and denied states do not acquire a grant by default.
2. A fictional `link_only` source with matching programme rights and an exact,
   independently approved, quote-free statement can enter only the intended
   private build; adding a literal quotation fails. A changed hash, date,
   locator, statement fingerprint, or revoked right invalidates the dependent
   publication candidate rather than silently reusing the earlier decision.
3. The unmodified four 2023 pilot rows remain out of the publish set. The
   current 2026 production-record path, four-source pilot copy, empty-state
   rendering, and static/browser output must be tested together after conflict
   resolution. Rerun full CI on that exact head; CI is technical evidence only.

The human rights owner still needs a separate source/version/use decision for
PP and ERC, with authentic private evidence. The editorial owners still need
actual review dates and exact-content evidence, source-page/archive rechecks,
a defensible chronology decision, and the approved 2023 inclusion rule. A
passing combined build neither supplies these decisions nor authorizes a
public release.

## Evidence and limits

Inspected the current main and both PR heads via Git and GitHub API on
2026-11-16; simulated both merges with `git merge-tree --write-tree`; counted
2023 register rows from each committed `register.json`. No private PDFs,
reviewer dossiers, political answers, or rights evidence were opened. This
handoff introduces no political claim or approved source record.
