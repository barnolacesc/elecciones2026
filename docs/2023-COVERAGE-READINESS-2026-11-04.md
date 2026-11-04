# 2023 coverage readiness: register versus discovery leads

Roadmap package: **P0.2** (`2023-corpus-completion`, proposal-only).
Election: `es-gen-2023`. Checked against `origin/main` `488b6f5` on
2026-11-04. This is a repository-evidence reconciliation, not a fresh
publisher, private-PDF, rights or editorial review. The ten party names below
are the current product target in `ROADMAP.md`, **not** an approved 2023
candidature denominator. A party and a constituency candidature are not the
same inventory unit.

## Observed handoff state

| Product-target party | 2023 source register | Discovery handoff outside register |
|---|---|---|
| PP | Pilot row | None needed for this snapshot |
| PSOE | No row | [PSOE lead](2023-PSOE-SOURCE-DISCOVERY-2026-10-29.md) |
| VOX | No row | [VOX lead](2023-VOX-SOURCE-DISCOVERY-2026-10-30.md) |
| Sumar | Pilot row | None needed for this snapshot |
| ERC | Pilot row | None needed for this snapshot |
| Junts | No row | [Junts lead](2023-JUNTS-SOURCE-DISCOVERY-2026-10-31.md) |
| EH Bildu | No row | [EH Bildu lead](2023-EH-BILDU-SOURCE-DISCOVERY-2026-10-31.md) |
| EAJ-PNV | Pilot row (`pnv`) | None needed for this snapshot |
| BNG | No row | [BNG lead](2023-BNG-SOURCE-DISCOVERY-2026-10-30.md) |
| UPN | No row | [UPN lead](2023-UPN-SOURCE-DISCOVERY-2026-10-31.md) |

`content/sources/register.json` has four `es-gen-2023` rows: PP, ERC, PNV
and Sumar. All four are `published-unverified`, have
`rights_review.status = not_reviewed`, have a recorded SHA-256, and have no
evidenced `publication_date`. The six linked files are **candidate discovery
handoffs**, not six verified programme records or six negative coverage
findings. [PR #200](https://github.com/c2ventures/elecciones2026/pull/200)
adds a separate Coalición Canaria discovery handoff for review; it is not
merged, and the unresolved inclusion rule means this ten-name target cannot
exclude other eligible candidatures.

The four 2023 pilot coverage examples repeat source status; they are not a
per-candidature, per-document, eight-topic search matrix. Eight 2023 pilot
statement examples exist (six `under_review`, two `draft`); six 2023 pilot
relationship examples are `invalidated`. None of these counts is a full
programme inventory, a reviewed topic-absence finding or an approved
cross-party comparison. Do not divide them by ten or call any percentage
"coverage". The [official-enumeration handoff](2023-CANDIDATURE-ENUMERATION-EVIDENCE-2026-10-22.md)
has candidate BOE evidence but no approved/reconciled manifest.

## Reconciliation order and decision boundary

1. The owner approves the 2023 inclusion unit/rule and corrected official
   candidature manifest. Until then, report `denominator_unresolved`.
2. For each included candidature, review document applicability, general
   programme, coalition/territorial annexes and replacements. Convert each
   discovery lead into a versioned source row only after publisher-to-bytes
   evidence and scope are checked. An unlocated document is an unresolved
   search, not an absent political position.
3. Bind authenticity, chronology and each proposed source use to independent
   human decisions for the exact version. A URL/hash does not grant paraphrase,
   quotation or PDF redistribution rights. Keep originals and review evidence
   private.
4. Reconcile every relevant document and topic search before any `not stated`
   conclusion. P1 proposals and relations then need distinct exact-version
   editorial reviews and [comparison-set accounting](../openspec/changes/2023-corpus-completion/specs/programme-comparison/spec.md).

## Open PR and CI boundary

[PR #101](https://github.com/c2ventures/elecciones2026/pull/101) remains open
and conflicting. Its earlier passing checks do not review current main; its
code integration was merged separately in PR #166. [PR #201](https://github.com/c2ventures/elecciones2026/pull/201)
already reconciles that conflict and the rights-decision packet, so this
package does not edit either handoff or `tasks.md`. Main CI run
[41343879201](https://github.com/c2ventures/elecciones2026/actions/runs/41343879201)
failed; there is no current green release gate to cite.

Evidence: `content/sources/register.json`, `content/examples/coverage/`,
`content/examples/statements/`, `content/examples/relationships/`, the linked
discovery and enumeration handoffs, `ROADMAP.md`, and GitHub PR/CI metadata.
No inclusion, source-rights, claim, relationship, route or publication state
was changed here. P0/P1 owner and editorial decisions remain open.
