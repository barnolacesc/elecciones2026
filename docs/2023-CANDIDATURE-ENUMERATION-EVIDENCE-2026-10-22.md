# 2023 candidature enumeration: official-evidence handoff

Roadmap package: **P0.3**, `2023-corpus-completion`. Checked on 2026-10-22
against `origin/main` `fe5e05e`. This is a source audit and proposed inventory
procedure, not an approved inclusion rule or a completed candidature list. No
party site, programme PDF, private archive, reuse permission or editorial
decision was verified in this package.

## Primary records and their limits

| Record | What it establishes | Limit for this project |
|---|---|---|
| [BOE-A-2023-12663](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-12663) | The 23 July 2023 election call for both chambers. | It does not enumerate candidatures or programmes. |
| [BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066), 27 June | Provincial boards' proclaimed Congress and Senate candidature notices, grouped by constituency. Its analysis links later corrections. | A Congress denominator must be taken from the Congress sections, not Senate entries or a deduplicated national party-name list. The published text is not correction-free. |
| [BOE-A-2023-15548](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15548), 4 July | Corrects entries in the proclamation notice, including the Congress ballot name of Sumar Més in Baleares. | Exact names/coalition scope cannot be frozen from the 27 June text alone. |
| [BOE-A-2023-15828](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15828), 7 July | Replaces a `No proclamada` entry for PACMA in the Teruel Congress section with a candidate list; it also corrects the Senate entry. | Correction handling can change inclusion, not just spelling. Do not count this Congress candidature as unproclaimed from the base notice. |
| [BOE-A-2023-14733](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-14733), 21 June | Earlier *presented* candidatures. | Presented is not proclaimed; this is a cross-check for changes, not the approved denominator. |

The BOE analysis for `15066` lists `15548` and `15828` as subsequent
corrections at the time checked. This audit did **not** enumerate all Congress
sections, reconcile each correction to every affected row, check possible
later judicial changes, or compare the official results list. The base notice
and its linked corrections are an evidence **candidate**, not a certified
complete or final manifest.

## Proposed P0 reconciliation sequence

1. Have the owner approve the eligibility rule and unit: Congress versus both
   chambers; constituency-level candidature versus coalition/party grouping;
   territorial and exception treatment. Until then, show
   `denominator_unresolved` and no completeness percentage.
2. For each Congress constituency, transcribe a candidate row from `15066`
   with its notice section/page, exact ballot name, original proclamation
   status and evidence URL. Keep Senate entries separate. Do not merge shared
   names into one candidature or equate a candidature with a source-register
   `party_id`.
3. Apply `15548` and `15828` as versioned amendments, retaining the original
   value, changed field, corrected value, correction URL and human verification
   status. Search for additional official changes before freezing the manifest;
   record the search date and scope rather than assuming these two are final.
4. Peer-check the reconciled rows against the approved rule. Separately map
   each included candidature to candidate programme, annex, coalition and
   replacement documents, or a documented unresolved search. Programme
   discovery and reuse rights are independent of ballot-list verification.
5. Only an owner-approved rule and independently checked manifest establish
   the candidature denominator. Topic completeness and `not stated` still
   require their own source/search reviews; no political position follows
   from this enumeration.

## Specific acceptance cases for a later implementation

- Teruel PACMA Congress changes from the base notice's unproclaimed text to
  the corrected proclaimed entry without discarding the audit trail.
- Baleares Sumar Més retains the corrected exact Congress ballot name while
  its coalition-to-programme mapping stays unresolved until separately reviewed.
- A Senate-only correction cannot silently change a Congress denominator.
- An unapproved rule or unapplied correction prevents a complete-corpus label.

Human decisions still needed: the scope rule, accepted finality/search
protocol for official changes, stable candidature/coalition identity policy,
manifest reviewer, and the separate programme/source-rights owners. Neither
this audit nor CI supplies those decisions.
