# BNG 2023 general-election document discovery — 2026-10-30

Roadmap package: **P0.13** (`2023-corpus-completion`, proposal-only).
Checked against `origin/main` `8e2fab4`, the open PR/issue list, and the
publisher links below on 2026-10-30. This is a candidate-document handoff,
not an approved candidature, exhaustive inventory, source version, rights
finding, topic review, political claim or release. No PDF bytes or programme
text were added to Git.

## Reconciled baseline

- `content/sources/register.json` has four `es-gen-2023` pilot rows (PP, ERC,
  PNV and Sumar), all `published-unverified` with rights `not_reviewed`. It has
  no 2023 BNG row or approved 2023 candidature denominator. Those four rows
  cannot establish completeness.
- `src-2026-bng-v0` is a separate `es-gen-2026` missing-source placeholder.
  Its homepage URL cannot be reused as a 2023 source version or evidence of a
  2026 programme.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) is still
  open/conflicting; [PR #166](https://github.com/c2ventures/elecciones2026/pull/166)
  separately proposes its integration. Neither supplies BNG document identity,
  rights or editorial approval. Do not merge both duplicate gates.

## Publisher discovery evidence

The BNG [electoral-programme archive](https://www.bng.gal/estaticas/programas-eleitorais.html)
separates the 2023 **Xerais** entry from 2023 municipal and other elections.
Under Xerais it links three different files. The links and response metadata
were observed on 2026-10-30; page counts below are retrieval-tool metadata,
not private archive verification.

| Archive label and linked candidate | Observed response | Inventory question |
|---|---|---|
| [Programa electoral](https://www.bng.gal/media/bnggaliza/files/2023/07/05/23_bng_xerais_programa.pdf) | PDF, 68 pages in web retrieval; HTTP HEAD `200 application/pdf`. Its cover identifies the 2023 general election. | Candidate general programme; verify exact bytes, version, applicability and replacement history privately. |
| [Decálogo de compromisos](https://www.bng.gal/media/bnggaliza/files/2023/07/05/23_bng_xerais_decalogo.pdf) | PDF, 4 pages in web retrieval; HTTP HEAD `200 application/pdf`. | Decide whether this companion document is an independently in-scope source or a derivative summary; do not silently drop or double-count it. |
| [Formato adaptado](https://www.bng.gal/media/bnggaliza/files/2023/07/12/Programa%20BNG%20LF.pdf) | PDF, 16 pages in web retrieval; HTTP HEAD `200 application/pdf`. Its introduction identifies it as a *resumo* in easy-read format. | Record its relationship to the decálogo and full programme; do not treat an adapted summary as an identical source version or substitute it for a full-document topic search. |

The dated URL paths are **not** evidence of the exact bytes' publication dates.
HEAD responses do not establish a hash, stable page anchors, historical
availability, copyright terms, or rights to paraphrase, quote or redistribute.
The archive may not list every annex or replacement; no absence finding follows.

## Private P0 review handoff

1. Apply the future owner-approved 2023 inclusion rule and verify BNG list
   identity/territorial scope against authoritative election evidence. Decide
   document-to-candidature applicability without equating a party ID to a list.
2. Capture each applicable file through an authorized private path. Preserve
   dated landing/direct URL and redirect evidence, immutable bytes, SHA-256,
   language, version and archive reference. Search for annexes and revisions.
   Leave publication dates unknown unless independently evidenced.
3. Have the human source owner decide authenticity and the rights owner decide
   permitted use for **each exact file version**. The three documents may need
   different rights and coverage states. Keep bytes and decision evidence
   outside Git and the public build.
4. Reconcile their document roles and derivative relationship before adding
   reviewed `es-gen-2023` source/coverage rows. Only later P1 review can support
   exact proposals, topic-level `not stated`, comparison relations or display.

This package changes no register, OpenSpec readiness flag, source/statement/
relationship record, public output, routing or release gate. CI cannot replace
source, rights or editorial review.

## Validation record

The archive-to-three-URL links and PDF response types were checked through the
web retrieval tool and independent HEAD requests on 2026-10-30. Local
repository assertions confirm the four pilot rows and separate BNG 2026
placeholder. `git diff --check` passed. This documentation check does not
verify PDF bytes, publication dates, rights, content or topic coverage. Recent
GitHub CI jobs on other PRs have failed with zero executed steps, so no
passing GitHub test is inferred for this package.
