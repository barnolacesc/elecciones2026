# Sumar 23J publisher-link and byte-identity audit — 2026-11-06

Roadmap package: **P0.18** (`2023-corpus-completion`, proposal-only).
Election: `es-gen-2023`. This is a bounded source-discovery check, not a
rights, editorial, coverage or release decision.

## Reconciled baseline

`origin/main` at `488b6f5` has four 2023 pilot source rows. The Sumar row
`src-2023-sumar-v1` records the landing and PDF URLs below, SHA-256
`d5ccdac0d20f1b93a5f703f180d086041bd988835072dd5cb5d1378bf0195820`,
`publication_date: null`, `published-unverified` and rights `not_reviewed`.
There is no approved full 2023 candidature/document denominator. PR #101 is
still open and conflicting, while its integration gate was merged via PR #166;
neither supplies a Sumar rights or editorial decision. Open PRs #208–#210
cover other publisher leads, not this registered Sumar URL pair.

## Publisher evidence observed on 2026-11-06

| Observation | Evidence and limit |
|---|---|
| [Movimiento Sumar's 23J landing page](https://movimientosumar.es/programa-electoral-23j/) labels itself `Programa Electoral 23J` and has a `Descarga el programa (PDF)` link. | The publisher page is a selected web presentation. Its text must not be treated as a complete transcription of the linked programme or a reviewed proposal corpus. |
| The link resolves to the register's [direct PDF URL](https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf). | Web retrieval identified an accessible 182-page PDF. Runner HEAD returned HTTP 200, `application/pdf`, and `Content-Length: 2567339`. These checks do not establish the document's original publication date or whether annexes/replacements exist. |
| A bounded, streaming GET of the direct URL produced SHA-256 `d5ccdac0d20f1b93a5f703f180d086041bd988835072dd5cb5d1378bf0195820`, equal to the registered hash. | This verifies the bytes returned to this runner on this date against the recorded digest; no PDF was retained in Git or this worktree. It is not a human authenticity, completeness or rights review. |
| HEAD reported `Last-Modified: Thu, 21 Aug 2025 11:00:11 GMT`. | This is server metadata for the currently served object, **not** evidence that the 2023-election document was first published then. The `/2023/07/` path also does not prove an exact publication date. Leave `publication_date` unknown. |

## Review handoff and boundary

Under the proposed P0 inventory protocol, bind a private acquisition record to
the observed URL, retrieval time, digest and exact bytes; check the publisher's
document role, any annexes or superseding versions, and applicability to the
owner-approved candidature unit. A human source reviewer must decide
authenticity and completeness. A separate human rights owner must decide
permitted linking, paraphrase, quotation and redistribution for the exact
version. Only then can P1 page-level proposal extraction and independent
statement/relationship review proceed. The landing-page highlights cannot
substitute for a full-document topic search or justify `not stated`.

No source/register field, PDF, political claim, review mark, public output or
routing changed. The current Sumar row remains `published-unverified`, with
rights `not_reviewed` and unknown publication date. This audit is not evidence
of complete 2023 coverage or a passing release gate.
