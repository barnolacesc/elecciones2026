# 2023 document discovery: access evidence is not an absence finding

Roadmap package: **P0.16** (`2023-corpus-completion`, proposal only).
Reconciled against `origin/main` `488b6f5` on 2026-11-09. This is a
repository/PR evidence audit, not a fresh publisher-site check, a source
registration, a rights decision, an approved 2023 inclusion rule, or a
political-content review.

## Observed boundary

- The 2023 register has four pilot rows (PP, ERC, PNV, Sumar), all
  `published-unverified`, with `rights_review.status=not_reviewed` and
  `publication_date=null`. It has no complete 2023 candidature/document
  denominator. `download-policy.json` allows private acquisition from only
  four hosts; that allowlist is not an absence or reuse decision.
- The current register's `missing`/`published-unverified` statuses describe
  source records, not the outcome of each discovery request. Its parser has
  no discovery-attempt evidence object. The draft P0.2 design asks for search
  attempts but does not yet specify how a 403, 404, timeout, stale index, or
  differing access paths affect a negative discovery conclusion.
- [PR #215](https://github.com/c2ventures/elecciones2026/pull/215)
  reports that two retrieval paths disagreed (403/404) for a candidate VOX
  23J URL. That PR explicitly did **not** verify exact bytes or establish
  permanent absence. [PR #221](https://github.com/c2ventures/elecciones2026/pull/221)
  handles the distinct private acquisition-allowlist expansion gate. Neither
  PR is an approved source or a reviewed negative finding.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  open/conflicting, has no GitHub reviews, and its successful checks predate
  current main. [PR #219](https://github.com/c2ventures/elecciones2026/pull/219)
  owns its disposition; this package does not change that branch or its
  six editorial candidates. Main CI [run 41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
  is failing; no current CI or human review is inferred from the old PR run.

## Proposed P0.16 handoff

Keep technical **attempt outcomes** separate from the human **document
discovery disposition**. A private, versioned attempt ledger should bind the
2023 election, candidate candidature/document role, attempted URL, UTC time,
request method/access path, redirect/final host, response or transport error,
content type, obtained-byte hash if any, and a private evidence reference.
It must not store credentials, full PDF text, or political answers in Git.
An unsuccessful HEAD request must not be represented as a successful or failed
GET of the same document; a search index entry must not be treated as current
publisher bytes.

The proposed disposition stays **unresolved** after an access block, timeout,
contradictory response, stale cache, or one missing URL. `Not located after
reviewed search` requires an approved candidature/document scope, a documented
search protocol and stopping rule, and human acceptance of the attempts and
alternate official paths. Even that disposition means *not located by this
search*, not *no programme existed* or *the party opposed the policy*.
New URLs, changed bytes, corrected candidature scope, or a changed search
protocol invalidate the affected disposition; they do not silently overwrite
old attempts. Exact-byte authenticity, chronology, rights and P1 topic absence
remain separate gates.

Before implementation, the source owner must decide acceptable access paths,
retry/alternate-path and archival-evidence rules, retention/redaction of
attempt metadata, reviewer quorum, the negative-discovery stopping rule, and
public wording. These decisions and a concrete schema need OpenSpec review.
No status in the current register is changed by this proposal.
