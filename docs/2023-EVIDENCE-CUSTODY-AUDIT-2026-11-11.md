# 2023 private evidence custody audit — 2026-11-11

Roadmap package: P0 source/rights evidence contract under
`2023-corpus-completion` (proposal-only). Baseline: `origin/main` `488b6f5`.
This audit concerns whether a reviewer can retrieve the private evidence behind
an eventual decision. It does not decide source authenticity, legal rights,
candidature inclusion, editorial validity or publication.

## Repository-observable boundary

- `content/sources/register.json` has four `es-gen-2023` source rows. All four
  are `published-unverified`, have a SHA-256 and retrieval date, and have
  `rights_review.status=not_reviewed`; none has `rights_review.evidence_ref`.
  These are pilot rows, not the approved 2023 candidature denominator.
- `content/sources/register.schema.json` permits an optional string
  `rights_review.evidence_ref`, described as a private reference. It does not
  define retrieval, version binding, access, retention or integrity recheck.
  The source row has a hash, but a matching source hash cannot prove that a
  rights-decision record is retrievable or applies to those exact bytes.
- The current P0 design calls for a private archive and leaves its retention
  and access policy to the owner. Repository visibility cannot establish
  whether an off-repository evidence store exists or is healthy.
- Draft/conflicting PR #101 has old successful checks from 2026-10-12; merged
  PR #166 integrated its technical gate. Open PR #219 covers PR #101
  supersession and #228 covers current integration CI. This package changes
  neither gate nor either PR's files/decision.

## Proposed acceptance boundary

A private, version-bound evidence ID should resolve for an authorized human
reviewer at the point a source authenticity, applicability or reuse decision
is considered for publication. Record the recheck result and date privately.
A missing, inaccessible or mismatched object keeps the dependent use pending;
it does not automatically revoke a human decision or conclude that permission
is absent. Public builds and CI logs must not include private locators, source
bytes, extracted text or correspondence. A source URL, checksum, or passing CI
is not a substitute for the underlying decision evidence.

The owner must decide the store, access roles, retention, recovery, redaction
and recheck responsibility before implementation. The four rows are not being
promoted and no private evidence was opened or assumed missing. This draft
adds a proposed requirement and fictional scenarios only; it does not modify
schema, source records, application code or public output.

## Reproduce the repository check

`python3` parsed the register at `488b6f5`: four 2023 rows, four pending
rights statuses, four non-null source hashes, zero non-null evidence references.
`git diff --check` and a requirement/scenario structure check validate this
proposal's format, not any human decision. Hosted CI and editorial review
remain separate gates.
