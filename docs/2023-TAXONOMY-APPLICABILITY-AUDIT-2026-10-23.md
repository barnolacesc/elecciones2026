# 2023 taxonomy applicability handoff — 2026-10-23

Roadmap package: **P0.4**, proposal-only within `2023-corpus-completion`. Baseline: `origin/main` at `fe5e05e`. This is an audit of repository metadata and review gates, not approval of a 2023 taxonomy, any classification, source right, claim, quiz item, or release.

## Reconciled evidence

- `content/taxonomy.json` has `taxonomy_version: 1.0.0`, eight core topics and `election_id: es-gen-2026`. `docs/CONTENT-METHODOLOGY.md` version 1.1.0 is explicitly scoped to `es-gen-2026` and remains a draft for human G0 approval. The current 2023-first roadmap instead requires a versioned, owner-approved topic taxonomy for the 2023 corpus.
- The eight 2023 statement examples span only housing, education and health/social services. They carry `election_id` and topic/subtopic IDs, but `content/schemas/statement.schema.json` has no taxonomy-version field. These counts show fixture breadth only; they do not show exhaustive programme search or topic coverage.
- `Taxonomy.validate()` checks the eight IDs and labels but does not check election applicability. `StatementRecord.validate()` checks membership of topic/subtopic IDs, not whether a 2026-scoped taxonomy is approved for a 2023 statement. The generator also checks core topic membership. A successful structural validation therefore cannot be read as 2023 editorial taxonomy approval.
- `content/quiz/2023-provisional.json` has its own eight topic labels and a `historical-provisional-private` status. It is not a reviewed taxonomy or quiz set; do not use its labels to settle the comparator's classification policy.
- Open PRs #124 (official candidature enumeration), #126 (PR #101 reconciliation), #127 (comparison-set integrity), #130 (source-use rights) and #131 (source journey) cover other gates. PR #101 remains draft/conflicting and its green historical checks are not editorial review. None is a 2023 taxonomy applicability decision.

## Review decision, not an agent default

The owner/editorial reviewers need to decide whether to **adopt the eight-topic structure for 2023 unchanged**, revise its boundaries/subtopics, or version a distinct 2023 taxonomy. Record the chosen election scope, exact taxonomy revision/hash, date, reviewers, rationale and effective corpus revision in private review evidence. The decision must distinguish topic vocabulary reuse from approval of any programme classification. If the choice changes topic or subtopic meaning, preserve a mapping/reclassification trail rather than silently changing existing IDs or historical statements.

## Proposed acceptance cases for a later reviewed design/tasks package

1. A fictional 2023 statement with a valid topic ID but no approved 2023 taxonomy applicability record cannot be presented as fully classified/reviewed 2023 coverage. A matching 2026 taxonomy version string alone is insufficient.
2. A cross-cutting fictional measure records one primary topic plus a reviewer rationale; optional secondary discovery tags do not create duplicate proposal counts or unsupported comparisons.
3. A new taxonomy revision preserves the old classification and affected statement, relationship, coverage, quiz and budget-mapping dependencies; each is explicitly reviewed or withheld before rebuilding. A cosmetic label edit must not be treated as automatically equivalent to a changed category boundary.
4. Coverage counts identify the election, approved candidature denominator, taxonomy revision and search state per topic. An unsearched or partly searched document does not yield `not stated`, and an empty candidate queue does not establish absence.
5. A reviewed 2023 quiz, if later attempted, binds to the same approved 2023 taxonomy revision and its own reviewed item/method record. The provisional quiz cannot be promoted by copying topic names.

## Handoff and limits

Add the requirement delta in `openspec/changes/2023-corpus-completion/specs/editorial-statements/spec.md` to the P0/P1 review queue. Before implementation, reconcile this delta with PRs #124/#127 and the existing design/tasks, obtain an explicit taxonomy decision and review the migration/invalidation design and fictional tests. No source files, editorial records, schema, validator, public copy, quiz data or routing change in this package.

Reproduction from this baseline: inspect `content/taxonomy.json`, `docs/CONTENT-METHODOLOGY.md`, `content/schemas/statement.schema.json`, `src/elecciones2026/methodology.py`, `src/elecciones2026/editorial.py`, and the eight `es-gen-2023` statement examples. These observations do not inspect private PDFs or make source-rights findings.
