# EH Bildu 23J document discovery — 2026-10-31

Roadmap package: **P0.14**, `2023-corpus-completion` (proposal-only).
Checked against `origin/main` `8e2fab4`, the open PR/issue list, the source
register, and the publisher URLs below on 2026-10-31. This is a discovery
handoff, not an approved candidature, exhaustive inventory, verified source
version, rights finding, editorial decision, or release. No PDF bytes or
political positions were added to Git.

## Reconciled baseline

- `content/sources/register.json` has four `es-gen-2023` pilot rows (PP, ERC,
  PNV and Sumar), each `published-unverified` with rights `not_reviewed`. It has
  no EH Bildu 2023 source row or approved 2023 candidature denominator. Four
  pilot rows cannot establish complete coverage.
- `src-2026-ehbildu-v0` is a separate `es-gen-2026` missing-source placeholder.
  Its homepage URL is not a 2023 source version or proof of a 2026 programme.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  open and conflicting. [PR #166](https://github.com/c2ventures/elecciones2026/pull/166)
  separately proposes its integration. Neither establishes EH Bildu source
  identity, reuse rights, or editorial approval; do not merge duplicate gates.

## Publisher evidence and its limits

| Lead | Observed on 2026-10-31 | Unresolved question |
|---|---|---|
| [Publisher-hosted *Compromiso de Euskal Herria Bildu* PDF](https://ehbildu.eus/dokumentuak/23J-COMPROMISO-DE-EUSKAL-HERRIA-BILDU.pdf) | The publisher URL returned HTTP `200`, `application/pdf`, `Content-Length: 64872` to HEAD. Web retrieval identified a 16-page document with that cover title. | Determine whether this is the full general-election programme, a shorter commitment document, or one of several relevant documents; verify applicability, exact bytes, page locators, annexes and replacement history privately. |
| [Publisher article on the ERC–EH Bildu Senate coalition](https://ehbildu.eus/es/noticias/esquerra-republicana-y-eh-bildu-se-presentan-en-coalicion-a-las-elecciones-al-senado) | The publisher dates the article 2023-06-08 and identifies a joint Senate candidature for 23J. | Review Congress and Senate candidature/document scope separately under the owner-approved inclusion rule. The article does not establish that the PDF applies to the joint Senate list or that the PDF covers every relevant list. |

The PDF HEAD response reported `Last-Modified: Thu, 26 Feb 2026 09:55:43 GMT`.
That server timestamp is **not** evidence of the document's 2023 publication
date or historical byte identity. The URL's `23J` label and a current 200
response likewise do not establish the exact election version, a checksum,
rights to paraphrase, quote or redistribute, or a complete document search.
The publisher article is candidature-scope context, not an editorial source
for a comparison. No missing-document or `not stated` conclusion follows.

## Private P0 handoff

1. Apply an owner-approved 2023 inclusion rule and authoritative corrected
   candidature evidence. Resolve Congress versus Senate units and the joint
   Senate candidature before assigning any document to a candidature ID. Do
   not equate a party ID, a Senate coalition, and a Congress list.
2. Recheck the publisher document through an authorized private retrieval
   path. Preserve dated landing/direct URL and redirect evidence, immutable
   bytes, SHA-256, language, source version, archive reference and page mapping.
   Search for other applicable general programmes, annexes and replacements;
   retain unresolved searches. Keep publication date unknown without evidence.
3. Have the human source owner decide authenticity and the rights owner decide
   permitted uses for each exact source version. Linking, paraphrase, quotation
   and PDF redistribution require distinct decisions. Keep bytes and decision
   evidence outside Git and the public build.
4. Only after those gates, propose reviewed `es-gen-2023` source and coverage
   rows. P1 topic search, statements, comparison relationships and display
   require independent review. A successful technical test is not approval.

This package changes no source register, OpenSpec readiness status, political
content, routing, deployment or release gate.

## Validation record

Local Python assertions confirmed four pilot 2023 source IDs, four pending
rights states, no 2023 EH Bildu source row and a distinct missing 2026
placeholder. Publisher PDF HEAD returned `200 application/pdf`; web retrieval
reported 16 pages. The publisher Senate article was inspected. `git diff
--check` passed. No PDF bytes entered the repository or private archive and no hash was
verified here; source authenticity,
publication date, rights, completeness and political content remain unverified.
GitHub CI is a separate engineering gate; recent PR jobs show failures with no
executed steps, not passing tests or human review.
