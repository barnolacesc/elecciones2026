# 2023 source-use decision queue — 2026-10-23

Roadmap package: **P0.1-R**, a documentation-only rights and coverage handoff
under the proposal-only `2023-corpus-completion` change. Election:
`es-gen-2023`. This is a request for human decisions, not a rights opinion,
source verification, OpenSpec approval, or permission to publish.

## Reconciled input and scope

`origin/main` at `fe5e05e` has four 2023 pilot rows in
`content/sources/register.json`. Each row is `published-unverified`, has
`rights_review.status = not_reviewed`, and has no evidenced publication date
in the register. They are source rows, **not** an approved candidature list or
the denominator for 2023 coverage. PR #101 is a draft for six PP/ERC summaries;
it remains conflicting with current main and cannot establish the rights or
editorial gate through its passing CI. Open draft PRs #124, #126, and #127
cover candidature evidence, PR #101 conflict analysis, and comparison-set
accounting respectively; this packet changes none of their files or decisions.

| Registered source | Intended review unit | Pending decision |
|---|---|---|
| `src-2023-pp-v1` | Exact registered PDF version/hash; PP pilot | Source identity, proposed outbound-link and quote-free-summary use, date evidence |
| `src-2023-erc-v1` | Exact registered PDF version/hash; ERC pilot | Same; Spanish summary must also retain original-language qualification |
| `src-2023-pnv-v1` | Exact registered PDF version/hash; PNV pilot | Source identity and use scope before any future proposal publication |
| `src-2023-sumar-v1` | Exact registered PDF version/hash; Sumar pilot | Source identity and use scope before any future proposal publication |

The PP/ERC [reuse handoff](https://github.com/c2ventures/elecciones2026/blob/feat/issue-100/docs/pilot-review/2023/reuse-handoff.md) exists
only on draft PR #101, not on this base branch. It requests source-specific
human decisions and a private page recheck; it is not itself a decision. The
four-party [pilot inventory](pilot-review/2023/README.md) records earlier local
byte/extraction verification, which does not prove publisher authenticity,
publication date, rights, or complete topic search. This run did not open PDFs
or the private evidence store and did not retest remote publisher URLs.

## Decision packet for each exact version

The owner should resolve the following **independently for each document
version**, including any annex or replacement discovered under the eventual
approved inclusion rule. Keep the full decision and supporting material in an
owner-approved private store; the repository should retain only a non-sensitive
reference and the approved projection.

1. **Identity and availability:** record publisher evidence that binds the
   landing page to the exact document; compare the private original with the
   registered SHA-256; record retrieval evidence and an evidenced publication
   date *or* `unknown`. A directory name, PDF filename, local version label,
   or HTTP success is not proof of the publication date of those exact bytes.
2. **Proposed use:** decide separately whether the project may link to the
   official document, publish a neutral human-reviewed paraphrase, reproduce
   a short quote, or redistribute any PDF/extracted text. State conditions,
   attribution, version/hash, decision date, human decider and private evidence
   reference for each permitted use. A link or hash does not grant other uses.
3. **Editorial dependency:** keep source/rights acceptance distinct from the
   two human statement reviews and from relationship approval. A rights
   decision cannot certify proposal wording, coverage, or a comparison. A
   statement review cannot decide rights. No agent or CI run fills either role.
4. **Coverage dependency:** join the document to an approved candidature and
   its document role (general, annex, coalition or replacement) before any
   completeness count. Record unresolved search and topic-review states
   separately. `not_reviewed`, unlocated documents and unsearched sections
   cannot become `not stated`, opposition, or a coverage percentage.

The current register offers `not_reviewed`, `link_only`,
`link_and_short_quote`, `public_domain`, and `permission_denied`; these are
schema labels, not self-executing permissions. PR #101 proposes tighter
version-bound evidence and quote-free publication gates. Reconcile that
proposal with the reviewed P0 record contract before implementing new states
or changing existing rows. Until then, keep all four rights states unchanged.

## Proposed fail-closed acceptance cases for later reviewed specs

- A verified hash with pending rights remains an integrity observation only;
  no summary or quotation enters the public build.
- A human `link_only` decision for one source version never authorizes a quote,
  PDF mirror, different hash, annex, or another party's document.
- A source replacement retains its old decision for audit but sends the new
  version and dependent page locators, statements, topic searches and
  relationships back to their respective reviewers.
- A reviewed statement with pending source rights, or an approved source with
  unreviewed statement/relationship, cannot be represented as a fully reviewed
  comparison.
- A missing document remains an unresolved discovery/coverage row, not a
  negative political position. A changed inclusion rule invalidates coverage
  counts rather than silently changing their denominator.

## Owner/editorial handoff and limits

The next review needs a named source-authenticity owner, a named rights
decision owner, an approved private evidence-store/access and retention rule,
the 2023 candidature inclusion/coalition rule, and a policy for unknown exact
publication dates. The owners should decide whether the proposed use scope
is acceptable for each source; this document does not choose a legal basis or
mark a rights status. Once reviewed, update the applicable OpenSpec design,
spec and tasks, reconcile PR #101 on its own branch, then implement/test only
the approved contract. No corpus content, source record, public build, or
deployment changes in P0.1-R.
