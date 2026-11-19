# Soria ¡YA! 23J source discovery — 2026-11-19

Roadmap package: **P0.1 source inventory** (`2023-corpus-completion`, proposal-only). This is a private, evidence-bounded discovery handoff, not an inclusion, rights, editorial, or release decision.

## Reconciled baseline

- `origin/main` at `d13ba683888de17714ad958a8034916168889cc3` has four `es-gen-2023` pilot source rows (PP, ERC, PNV, Sumar). Each has `published-unverified` status, `not_reviewed` rights and an unknown publication date. This is neither a complete candidature list nor a coverage denominator.
- PR #101 (`f8506a10b6784edf597e9e315f4c000dc0d341af`) remains open, conflicting and without GitHub reviews. A merge-tree check against this main reports six conflicted paths. Its October CI did not test a resolved current-main tree or provide human approval.
- No Soria ¡YA! source row or Soria ¡YA! discovery handoff was found in current main, and no open PR title/body identified this source on the audit date. This new lead does not alter the four-row register.

## Primary-source lead

| Evidence | Observed boundary |
|---|---|
| [BOE-A-2023-15066, Soria, Congress](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066) | Under `JUNTA ELECTORAL DE SORIA` → `CONGRESO DE LOS DIPUTADOS`, the proclaimed-candidature notice lists `SORIA ¡YA! (SY)`. This is a candidate enumeration input, not an owner-approved inclusion rule. Corrections and finality still require a separate check. |
| [Publisher presentation, dated 6 July 2023](https://soriaya.org/soria-ya-presenta-su-programa-electoral-hecho-en-soria/) | The party's own post identifies its 23J general-election programme and links to the complete programme page. The post date is evidence about this announcement, not proof of an immutable programme edition. |
| [Publisher programme page, displaying 10 July 2023](https://soriaya.org/programa-electoral-de-soria-ya-2023/) | The linked page identifies itself as a programme for the 23J 2023 general election. It is HTML, not an archived PDF with stable physical pages. It displays a relative last-update age, so its current bytes and the content present in July 2023 must not be conflated. |

These pages were inspected on 2026-11-19. No programme text, PDF, extracted text, screenshot or political position is copied into this repository by this handoff. No source hash, archived edition, exact section-level claim locator, or rights decision is asserted.

## Review and intake handoff

1. Apply the owner-approved 2023 Congress candidature rule and correction/finality protocol to the BOE entry. Decide whether a Soria-only candidature is included and how Congress versus Senate material is scoped; do not infer inclusion from this lead alone.
2. Preserve a private dated snapshot of the publisher HTML and its linked announcement, record the retrieved bytes/hash and source-version identity, and check for archived or revised editions. The page's displayed date must not silently become an immutable publication or review date.
3. Have the source-rights owner decide separately whether linking, paraphrase, short quotation or redistribution is permitted for that exact version. Until then, rights remain `not_reviewed`; the existence of a public page grants no reuse approval.
4. Only after inclusion, scope, source identity and rights review, decide the appropriate document row and topic-search plan. HTML headings/anchors need reviewed locators; PDF page-number assumptions do not apply. Keep coverage unresolved and do not generate a `not stated` position from an unsearched page.
5. Reconcile any future source/statement integration with PR #101's version-bound gate on a resolved head. Passing CI cannot supply the missing human decisions.

This is one candidate source lead, not a complete Soria ¡YA! inventory and not evidence of complete 2023 party or topic coverage.
