# 2023 private acquisition expansion gate — 2026-11-09

Roadmap package: **P0.15**, `2023-corpus-completion` (proposal-only).
This is a source-access and coverage handoff, not a request to expand the
fetch allowlist now. It changes no source record, PDF, rights decision,
political claim, public artifact or release state.

## Reconciled baseline

- `origin/main` at `488b6f5` has four `es-gen-2023` source rows: PP, ERC,
  PNV and Sumar. Each is `published-unverified`, has
  `rights_review.status = not_reviewed`, and has no evidenced publication date.
  The rows are a rehearsal inventory, not an approved 2023 candidature or
  programme denominator.
- `content/sources/download-policy.json` permits exactly four acquisition
  hosts: `www.pp.es`, `static.esquerra.cat`, `movimientosumar.es` and
  `www.eaj-pnv.eus`. The [private archive procedure](PRIVATE-SOURCE-ARCHIVE.md)
  requires a registered source ID and SHA-256, explicit review of additions
  and redirects, and private storage outside Git. A permitted acquisition
  host grants neither source authenticity nor reuse rights.
- [PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains
  draft, conflicting and without GitHub reviews. Its old green checks are
  technical evidence only. [PR #219](https://github.com/c2ventures/elecciones2026/pull/219)
  separately audits its disposition; this package does not edit or resolve it.
  At inspection, the latest `main` CI run for `488b6f5` had failed, so this
  audit makes no claim of a green baseline.

## Two discovered hosts outside the acquisition policy

The existing [BNG discovery handoff](2023-BNG-SOURCE-DISCOVERY-2026-10-30.md)
and [EH Bildu discovery handoff](2023-EH-BILDU-SOURCE-DISCOVERY-2026-10-31.md)
identify candidate 23J documents. On 2026-11-09, a metadata-only HEAD request
to each linked publisher-hosted URL returned HTTP 200 and `application/pdf`
without an observed redirect:

| Candidate URL | Host | Current acquisition policy |
|---|---|---|
| [BNG 23J programme](https://www.bng.gal/media/bnggaliza/files/2023/07/05/23_bng_xerais_programa.pdf) | `www.bng.gal` | Not allowed |
| [EH Bildu 23J commitment document](https://ehbildu.eus/dokumentuak/23J-COMPROMISO-DE-EUSKAL-HERRIA-BILDU.pdf) | `ehbildu.eus` | Not allowed |

This is a **policy/registration gap**, not evidence that acquisition should
proceed. A HEAD response does not bind a publisher landing page to immutable
bytes, establish a 2023 publication date, identify a complete programme,
prove candidature applicability, or grant quotation, paraphrase or PDF
redistribution rights. No PDF was downloaded or hashed in this run. A direct
URL must not be added to the four-source `acquire` loop by bypassing the
allowlist or fabricating a registered checksum.

## Proposed P0 review sequence

1. The owner decides the approved 2023 candidature/territorial rule and each
   candidate document's role. For BNG, the already discovered decálogo and
   adapted summary require separate role and version decisions; for EH Bildu,
   the commitment document's completeness and Congress/Senate applicability
   remain unresolved. Do not treat the two URLs as the full party inventory.
2. A source owner retains publisher landing-to-document and redirect evidence,
   then privately retrieves and hashes each **exact** candidate version under
   an approved access/retention procedure. Unknown chronology stays unknown.
   A changed URL response creates a new candidate version, not a silent hash
   update.
3. Only after the source is registered with its reviewed scope and immutable
   hash should an operator propose the minimal host-policy expansion. Test that
   permitted hosts are exact, redirects to unapproved hosts are rejected, and
   missing/mismatched hashes fail closed. Keep PDF bytes and extraction out of
   Git, CI artifacts and the public build.
4. Human owners decide authenticity and each proposed reuse right independently
   of acquisition. P1 topic search, summaries, relationships and publication
   retain their own review gates. Passing an acquisition test or CI cannot
   approve any of these decisions.

The OpenSpec P0 tasks remain proposal-only and unchecked for these decisions.
This handoff deliberately avoids editing shared OpenSpec files that are being
changed by other open corpus PRs. After those reviews reconcile, a bounded
spec/design/task revision can define the implementation acceptance tests.

## Validation and limits

Local JSON assertions found four 2023 pilot rows, four pending rights states,
and exactly the four configured hosts. URL parsing confirmed that the two
candidate hosts are absent. HEAD checked response status, MIME type and final
URL only; it did not inspect or archive PDF bytes. `git diff --check` validates
formatting, not source identity, rights or editorial interpretation.
