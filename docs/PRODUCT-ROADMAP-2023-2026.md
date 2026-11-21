# 2023-first product delivery roadmap

**Owner direction:** Cesc, 2026-10-19. **Election scope:** Spanish general
election 2023 (`es-gen-2023`) first; 2026 is a separate future corpus. This is
the product sequence, not permission to publish unreviewed political content.
Read `AGENTS.md`, `ROADMAP.md`, `openspec/ROADMAP.md`, and the applicable change
before implementing a package.

## Current baseline and boundaries

The repository has a static comparison pipeline, a limited four-party 2023
pilot, a provisional/fictional quiz foundation, a 2023 budget preview and a
manual seat simulator. These are **not** proof that all 2023 programmes, all
topics, the real quiz, or public release are complete. The private preview is
not the public release. Previous unsupported review records were withdrawn;
some exact-content owner-reported records exist, but rights, coverage and
relationship decisions still need their own evidence. Reconcile the current
main branch, open issues/PRs, and source registers at the start of each cycle.

## Success definition

A phone visitor arriving from a shared link can see that they are viewing the
2023 election, select a topic and parties, compare specific proposals and
qualifications, open the exact source, and understand when evidence is missing.
They can optionally complete a short, transparent, source-linked questionnaire
without surrendering answers to a server. The same ingestion and review
pipeline can process 2026 documents under a separate election ID once those
sources exist. Polls and coalition tools extend this experience later.

## Ordered milestones

### P0 — Coverage and editorial contract

- Freeze a versioned rule for which **2023 general-election candidacies** are in
  scope; enumerate each eligible party and every relevant programme/document.
  “All” means every entry under this declared rule, not an unverified claim
  that every party published a complete PDF. Record missing, partial, replaced,
  regional and coalition documents explicitly.
- For each document: publisher, official URL, publication/retrieval evidence,
  election ID, language, version, hash, rights decision and private archive
  location. Keep original PDFs/extracted text out of the public repo/build.
- Approve and version topic taxonomy and reviewer/correction roles. No agent
  can self-approve source rights, political interpretation or publication.

**Exit:** complete coverage register against the declared party list; unresolved
sources and rights visible; human owner signs inclusion and editorial policy.

### P1 — Traceable 2023 proposal corpus and comparison

- Extract candidate initiatives from every in-scope programme into a review
  queue. Tag topic/subtopic, actor, action, conditions, beneficiary, amount/time
  when stated, and exact PDF page/section. Preserve source and taxonomy versions.
- Human review separates extraction, neutral summary and comparison relation.
  Compare measures only when they address the same policy question; show
  agreement, difference, qualification and `not stated` separately. Never infer
  opposition from silence or turn a source link into quote permission.
- Build topic/party coverage accounting, correction propagation and deterministic
  validation. Each displayed claim and cross-party relationship must have
  distinct approval evidence and a source trail. Start with breadth across all
  topics, then deepen individual topics; do not silently mark thin coverage as
  exhaustive.

**Exit:** every in-scope source has an explicit coverage state; every displayed
  2023 claim and comparison is reviewed and reproducible. Coverage counts and
  limitations are visible to readers. Rights/publication gate remains separate.

### P2 — Mobile-first comparison experience

- Design from 360/390/430 CSS px: one-column measure-first comparison, clear
  heading/type/color hierarchy, readable source links, 44 px touch targets,
  no horizontal scrolling, loading/empty/error states, and prominent next CTA.
- Test a social-link entry into a deep comparison, topic/party changes, source
  inspection and sharing on real mobile browsers, keyboard and screen readers.
  Validate comprehension with task-based users rather than visual taste alone.
- Keep Spanish public copy neutral. Links must not encode political answers.

**Exit:** observed mobile task success and accessibility issues recorded/fixed;
  no misleading coverage, dead CTA or unlabeled election context. Desktop is
  supported but not the design baseline.

**Current evidence boundary (2026-10-26):** the [E2.5 private 2023 mobile
audit](2023-MOBILE-ACCEPTANCE-AUDIT-2026-10-26.md) records passing local
artifact/Node contracts and the still-missing rendered, device, participant
and source-review evidence. P2 exit is not met by those technical checks.

**Source-index evidence (2026-11-05):** [PR #204](https://github.com/c2ventures/elecciones2026/pull/204)
repairs the private 2023 source links' missing new-tab notice. Ten local pilot
tests pass on Python 3.11. This is a link-label repair, not source, editorial,
device or screen-reader acceptance; P2 exit remains open.

### P3 — Usable, defensible questionnaire

- Replace provisional/mock items with a balanced set drawn only from reviewed
  2023 proposals. Specify sampling, topic/party coverage, wording, scoring,
  skips, ties and uncertainty; audit ideological and coverage bias.
- Show a short progress path, clear actions and results that explain *why* each
  match appears, with proposal citations. Result means alignment with answered
  items, never a voting recommendation or scientific prediction.
- Keep answers in browser memory by default; verify no answer-bearing analytics,
  network calls or share URLs. Test comprehension, accessibility and mobile flow.

**Exit:** human editorial approval of item set/method; measured usability;
  privacy/fairness checks; explicit G5 release decision. Passing code tests
  alone does not establish validity.

### P4 — 2026 refresh and budget reuse

- Reuse versioned taxonomy, extraction, review and static-build contracts for
  `es-gen-2026`; never relabel 2023 claims as 2026 or compare across elections
  without a separately specified historical view. Newly published programmes
  require fresh source, rights, hash, page, claim and relationship reviews.
- Audit which 2023 budget context remains comparable. Label fiscal year,
  approved versus extended budget, executed figures, denominator and source;
  never silently carry 2023 amounts into a 2026 view.

**Exit:** a new election can be ingested without rewriting the product, while
  unreviewed 2026 content stays absent or clearly unavailable.

### P5 — Polls and surveys (after core comparison/quiz)

- Register original study and reputable pollster/media sources, fieldwork dates,
  sample, population, mode, question/estimation method, sponsor and publication
  date. Include CIS and identify it accurately as a public institution attached
  to the Spanish government; do not privilege or dismiss its results on that
  basis alone. Distinguish direct responses, vote estimates and seat forecasts.
- Compare only methodologically comparable series; display uncertainty and
  source-specific caveats, accessible chart plus table, and correction history.

**Exit:** reviewed method, source rights and trend interpretation; no composite
  forecast without a separate validated methodology.

### P6 — Pactometer and hemicycle (later iteration)

- Build on the existing manual seat simulator. Verify chamber size and voting
  thresholds from official rules for each election. Make coalition arithmetic,
  abstentions and assumptions explicit; hemicycle has accessible table equivalent.
- Keep user-entered scenarios distinct from poll-based seat projections and
  political likelihood. A projection engine would need a separate specification.

**Exit:** edge-case arithmetic tests and mobile/screen-reader validation; no
  implied prediction of which coalition will govern.

## Daily development contract

Two scheduled runs, morning and afternoon in `Europe/Madrid`, share this ordered
roadmap. Each run chooses one **bounded, non-overlapping** Ready package after
checking current main, open PRs, issues and OpenSpec dependencies. The first
run should reconcile the 2023 coverage register and editorial gaps; later runs
may work on independent mobile UX or fixture-only technical foundations while
human content reviews are pending. A run can report a genuine blocker rather
than fabricate progress.

Use a fresh branch, tests and a PR. Do not self-approve rights/reviews, invent
programme positions or poll findings, bypass CI, merge/deploy/publish political
content, switch the public site, or claim release from a private preview. Keep
review-gated work open for Cesc. Report one concrete change, tests, PR and
remaining gate; update this roadmap with evidence only, not optimistic status.
