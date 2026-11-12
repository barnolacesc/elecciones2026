# 2023 cross-topic initiative placement — P1 review handoff

Status: evidence-backed draft for `2023-corpus-completion` review only. This
is not a taxonomy decision, political interpretation, implementation task or
publication approval. Baseline: `origin/main` `488b6f5` on 2026-11-12.

## Observed contract

- `content/sources/register.json` contains four `es-gen-2023` pilot source
  rows. It is not an approved complete candidature or document denominator.
- `content/taxonomy.json` is version `1.0.0`, bound to `es-gen-2026`.
  `content/schemas/statement.schema.json` requires one `topic_id` and one
  `subtopic_id` per statement. `StatementRecord` in
  `src/elecciones2026/editorial.py` validates that one topic/subtopic pair.
- `build_comparison_payload` in `src/elecciones2026/generator.py` places an
  unpaired statement only in `measures[stmt.topic_id]`; relationship validation
  requires both operand statements to match the relationship topic and
  subtopic. This is a single-topic display contract, not evidence that a
  source initiative can address only one policy area.
- The draft 2023 OpenSpec requires version-bound initiative identity, reviewed
  taxonomy applicability and full comparison-set accounting, but does not yet
  decide how one canonical initiative is placed in multiple topics or counted.
  No real 2023 multi-topic assignment was verified in this audit.
- Draft PR #101 is conflicting and its prior green checks do not validate the
  integrated main branch. Open PR #235 drafts reviewer eligibility in the
  same OpenSpec change. This handoff changes neither PR's files or decisions.

## Decision needed before P1 corpus implementation

The editorial owners should define a reviewable **initiative-to-topic placement**
rule for the approved 2023 taxonomy. The proposed contract is one canonical
initiative identity for each reviewed measure, with zero or more *separately
reviewed* topic placements. Each placement would record exact initiative and
source versions, taxonomy version, topic/subtopic, scope/reason, disposition,
review evidence and correction lineage. A secondary placement would aid
navigation, not create a second political claim or an independent approval.
This is a proposal for review, not an accepted data model.

Owners must decide whether a primary topic is mandatory, when a secondary
placement is justified, whether cross-topic relationships are ever allowed,
who reviews placement changes, and how the reader sees a measure spanning
several topics. Keep taxonomy approval, source rights, statement approval,
relationship approval and release approval separate.

## Counting and fail-closed acceptance candidates

1. Count distinct canonical initiatives separately from topic placements. A
   topic page may count its reviewed placements, but summing topic counts must
   not be labelled a unique-initiative total. Disclose the counting unit.
2. A draft or disputed placement must not create reviewed topic coverage,
   `not stated`, an agreement or a second approved statement. Missing tags
   do not prove a topic was searched or absent.
3. Changing the taxonomy version, initiative version, source scope or a
   placement must identify dependent topic pages, comparison-set accounting,
   relationships and quiz citations for re-review before a new release.
4. Never copy one human review mark onto a second topic placement or grant
   quotation/reuse rights through classification. Keep source bytes and
   review evidence private.

Fictional review cases (no party positions implied):

- One fictional initiative is relevant to two topics. It appears as one unique
  initiative with two reviewed placements; a global count does not become two.
- A reviewer disputes the second placement. The first reviewed placement may
  retain its own status; the disputed topic cannot claim reviewed coverage.
- A taxonomy revision moves a subtopic. Prior placement and count snapshots
  remain auditable, while affected pages and comparisons await re-review.
- Two source occurrences paraphrase the same measure. Placement cannot merge
  them merely because their topic tags match; initiative identity has its own
  review gate.
- A topic has no approved placements. Its state remains unresolved until the
  source and topic-search scope have been reviewed; it is not `not stated`.

## Next review package

After owners approve the placement/counting rule and the 2023 taxonomy, add a
coordinated requirement delta, design and tasks to `2023-corpus-completion`.
Reconcile concurrent OpenSpec PRs before editing those shared files. Test
fictional multi-topic, disputed, deduplicated and taxonomy-revision cases in
both private accounting and static/browser projections. No corpus or renderer
change is authorized by this handoff.

Audit checks: compare the paths above on `origin/main`; `git diff --check` and
repository-local assertions. Hosted CI may be blocked before test steps and
cannot substitute for the missing human decisions.
