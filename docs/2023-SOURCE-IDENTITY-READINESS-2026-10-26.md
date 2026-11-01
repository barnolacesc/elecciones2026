# 2023 source-identity readiness — 2026-10-26

Roadmap package: **P0.4**, proposal-only source-authenticity handoff under
`2023-corpus-completion`. This audit does not verify any publisher site, PDF,
rights grant, political claim, candidature denominator or release decision.

## Reconciled baseline

- `origin/main` was `8e2fab4` at inspection. PR #113 is merged, so
  `docs/PRODUCT-ROADMAP-2023-2026.md` is on main. The 2023-first P0/P1 gates
  still precede 2026 refresh, polls and coalition work.
- `content/sources/register.json` has four `es-gen-2023` pilot rows: PP, ERC,
  PNV and Sumar. Each is `published-unverified`, has a SHA-256 and retrieval
  date, `publication_date: null`, and `rights_review.status: not_reviewed`.
  These rows are not an approved candidature manifest or complete programme
  inventory. The register stores an official and a direct URL but no captured
  landing-to-byte link, redirect chain, private capture reference or distinct
  human authenticity decision. Its local hash alone cannot fill those gaps.
- PR #101 remains open, unreviewed and conflicting. `git merge-tree
  --write-tree origin/main origin/pr-101` returned nine content conflicts:
  six PP/ERC statement examples, the pilot-review README, MVP tasks and
  `generator.py`. Its earlier successful checks do not test a resolved merge or
  establish rights/editorial approval. This P0.4 package changes none of its
  files or proposed statements.
- The latest main CI run at inspection, [40179863768](https://github.com/c2ventures/elecciones2026/actions/runs/40179863768),
  failed in the fork-PR/deploy-credential protection job; three other jobs
  passed and release was skipped. GitHub annotated the failed job as **not
  started** because of account payment or spending-limit status; it is not a
  demonstrated test regression. The preceding main run was successful.

## Specific gap and handoff

The existing P0 draft distinguishes byte integrity, authenticity and rights,
but does not yet specify how to bind a claimed publisher's landing page to the
exact document bytes across redirects, mirrors or changing URLs. A direct
URL, filename, HTTP success or identical hash is insufficient to infer that
the publisher authorized that exact document, or that two URLs represent one
reviewed version. A changed hash at a stable URL must not overwrite the old
evidence. This is a source-identity problem, not a rights-withdrawal decision
(draft PR #149), multi-document relevance decision (draft PR #150), or
relationship-integrity decision (draft PR #151).

The attached OpenSpec draft proposes the private evidence chain, fail-closed
states and fictional cases. The owner must choose the capture/recheck protocol,
authenticity reviewer and mirror-equivalence rule before an implementation
schema or real source decision. Rights and editorial review stay independent.
No publisher URL or private PDF was opened for this audit; current remote
availability and byte identity were not retested. No source record or public
artifact changed.

Evidence: local `origin/main` register and schema; OpenSpec P0/P1 drafts;
GitHub PR #101/#113 and current open-PR/issue/CI metadata; local `git
merge-tree` against fetched PR #101 head. A green future CI run cannot supply
the missing human source, rights or political-content decisions.

PR #155 CI run [40293266028](https://github.com/c2ventures/elecciones2026/actions/runs/40293266028)
also did not start its test and rendered-mobile jobs for the same GitHub
billing/spending-limit reason; downstream jobs were skipped. Local structural
validation and `git diff --check` passed, but hosted CI remains unverified.
