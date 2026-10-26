# 2023 initiative-lineage readiness audit — 2026-10-26

Roadmap package: **P1.6**, `2023-corpus-completion` (proposal-only).
Repository baseline: `origin/main` `8e2fab4`. This audit reads repository
contracts and GitHub metadata, not private PDFs, publisher pages or review
evidence. It changes no political or source record.

## Observed boundary

| Evidence | Observation | Limit |
|---|---|---|
| `content/sources/register.json` | Four `es-gen-2023` pilot source rows: PP, ERC, PNV and Sumar. Each is `published-unverified`, with `not_reviewed` rights and null publication date. | These are not an approved candidature/document denominator or cleared sources. |
| `content/schemas/statement.schema.json` and `src/elecciones2026/schemas.py` | A statement has one `programme_id` and one source URL/version/page or section; no occurrence, extraction-event, candidate-lineage or reviewed initiative-identity field. | Current validation cannot by itself explain a split, repeated extraction or cross-document duplicate. This is a schema observation, not a claim that real records are duplicates. |
| `openspec/changes/2023-corpus-completion/specs/editorial-statements/spec.md` before this delta | P1.1 already requires one actionable measure per candidate and gives a composite-sentence split case. | It does not yet state how source occurrences, duplicate dispositions and approved identity revisions preserve lineage and counts. |
| Open PRs | Draft PR [#101](https://github.com/c2ventures/elecciones2026/pull/101) is conflicting and has no submitted GitHub review. [#150](https://github.com/c2ventures/elecciones2026/pull/150) addresses document applicability; [#151](https://github.com/c2ventures/elecciones2026/pull/151) addresses relationship collisions; [#157](https://github.com/c2ventures/elecciones2026/pull/157) addresses correction dependencies. | This package must not resolve #101, approve its six summaries or duplicate the other packages' decision scope. Its older green checks do not test a current integration candidate. |

## Bounded proposal

Define a *private* occurrence-to-candidate-to-initiative ledger in the OpenSpec
delta and design. A source occurrence always keeps its immutable version and
locator. A reviewer can split an occurrence into measures or group repeated
occurrences, with an explicit reason and version-bound decision. Raw hits,
candidate measures and reviewed initiatives have different counts; only the
last may support an initiative count, and only after the relevant document set
and dispositions pass review. Similar wording is a suggestion, never a merge
or approval. A material condition difference or pending annex stays unresolved.

This is not a new programme inventory, a real extraction, a rights opinion or
permission to change the public comparator. Public statements still require
exact source/use and human editorial gates. Source bytes, extraction text and
private review evidence remain out of Git and serving artifacts.

## Acceptance handoff

Fictional fixtures should cover repeated extraction of one passage, splitting
two instruments in one sentence, recurrence across a programme and annex,
similar wording with different conditions, and revision of an approved
grouping. Check that all exact locators survive, unresolved dispositions cannot
produce final initiative counts, and changed grouping invalidates downstream
statement/comparison/coverage/quiz dependencies. Owners must decide identity
granularity, territorial equivalence, reviewer quorum, count wording and
multi-citation presentation before schema or runtime implementation.

Local verification for this proposal: `git diff --check` plus a structure
check of the five WHEN/THEN cases and separate owner/implementation tasks.
Neither check is editorial review, rights clearance or release approval.
