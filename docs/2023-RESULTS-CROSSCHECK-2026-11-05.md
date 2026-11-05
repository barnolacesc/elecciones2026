# 2023 Congress results cross-check for candidature inventory

Roadmap package: **P0.3** (`2023-corpus-completion`, proposal-only).
Election: `es-gen-2023`. Checked on 2026-11-05 against `origin/main`
`488b6f5`, the BOE records below, open PRs #101 and #200–#204, and current
CI. This is a narrow official-record audit, not a complete row-by-row manifest,
an approved inclusion rule, a programme verification, or a political claim.

## Evidence and distinct purposes

| Official record | Observed use | Boundary |
|---|---|---|
| [BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066) and its [4 July](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15548) and [7 July](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15828) corrections | Constituent evidence for *proclaimed* candidatures by chamber and constituency, as already described in the [enumeration handoff](2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md). | It still needs a full corrected-row and later-change review before a denominator is approved. |
| [BOE-A-2023-18907](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907), published 1 September | JEC publication of Congress and Senate results from general-count and elected-candidate records. Congress table II lists formations with seats; table III lists those without seats. | A result or seat count is not a programme record, a source-use decision, or a substitute for the corrected proclamation ledger. |
| [BOE-A-2023-19537](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-19537), published 16 September | Erratum to `18907`; the text corrects a vote figure for a non-elected **Senate** candidate in Madrid. | This cited erratum does not by itself change a Congress candidature row. Search and review other applicable changes before claiming a final results revision. |

The Congress results table II in `18907` presents **PSOE** and
**PSC-PSOE (PSC)** as separately labelled columns. That is an observed source
label distinction, not a decision that they are separate product actors or
that either can inherit the other's programme. The repository's ten-name
product target and four registered 2023 pilot documents therefore cannot be
joined to official rows by a simple party-name or acronym match. No seat or
vote total is imported by this audit.

## Proposed reconciliation gate

1. Version the owner-approved 2023 eligibility rule and corrected Congress
   proclamation ledger first. Preserve chamber, constituency, exact ballot
   label, status and notice/correction locators. The owner has not approved
   that rule or a complete ledger.
2. Independently transcribe the corresponding *Congress* formation labels and
   constituency evidence from `18907`, with its applicable corrections.
   Record each mapping from result row to proclamation row and from those rows
   to a product actor as a separately reviewed decision. Preserve unmatched
   or ambiguous labels; do not guess coalition or member-party identity.
3. Report row counts separately from distinct reviewed actors and documents.
   A mismatch is a reconciliation item, not proof of a missing programme or a
   `not stated` policy position. Do not publish a completeness percentage while
   the rule, row review or mapping is pending.
4. Join programme and territorial-annex applicability only after that actor
   mapping is reviewed. Publisher-to-bytes identity, publication chronology,
   use rights, topic search and editorial approval remain independent gates.
   Original PDFs and private review evidence stay outside Git and the build.

The proposal-only [provenance requirement delta](../openspec/changes/2023-corpus-completion/specs/programme-provenance/spec.md)
now states this cross-check and three fictional acceptance cases. It does not
implement a reconciler, alter `content/sources/register.json`, or approve any
actor, source, right, statement or relationship. Open PR #200 covers a separate
Coalición por Canarias discovery lead; PR #201 already reconciles PR #101's
superseded code integration; #202 covers register-versus-discovery readiness;
#203 covers locators; #204 covers source-index link behavior. This package
changes none of their files.

**Open decision:** the owner/editorial reviewers must select the 2023 scope,
finality-search protocol and identity mapping before the results cross-check
can establish any denominator. Main CI and the recent open-PR runs are failing;
passing tests on this documentation delta would still not be human review.
