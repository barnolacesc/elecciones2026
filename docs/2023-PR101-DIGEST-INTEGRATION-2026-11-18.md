# PR #101 digest-validation integration handoff — 2026-11-18

Roadmap package: **E1.4 / P0 provenance integration evidence**. This note is
limited to the source-digest contract proposed by [PR #256](https://github.com/c2ventures/elecciones2026/pull/256)
when the owner eventually reconciles [draft PR #101](https://github.com/c2ventures/elecciones2026/pull/101).
It does not approve a source, right, statement, comparison, OpenSpec change or
release. It complements, rather than replaces, the separate [rights-grant
integration audit](https://github.com/c2ventures/elecciones2026/pull/250).

## Reconciled evidence

- `origin/main` is `d13ba683888de17714ad958a8034916168889cc3`.
  Its latest Actions run `43325747158` passed on that SHA. Main has four
  `es-gen-2023` pilot source rows (PP, ERC, PNV, Sumar); all four remain
  `published-unverified`, `not_reviewed` for rights, and without an evidenced
  publication date. Neither that CI run nor a recorded digest proves private
  byte authenticity or a publishable 2023 denominator.
- PR #101 is still draft at `f8506a10b6784edf597e9e315f4c000dc0d341af`,
  with no submitted GitHub reviews and a dirty merge state. Its successful
  head checks ran on its own old tree. `git merge-tree --write-tree origin/main
  origin/pr-101` reports six conflicts, none in `source_register.py`.
- PR #256 is open at `f92ff6478a` with no submitted GitHub reviews. It changes
  the existing E1.1 parser so **every supplied** SHA-256 digest must be exactly
  64 lowercase hexadecimal characters, even while the source is
  `published-unverified`. Its fictional regression cases reject a short
  digest, uppercase digest and non-string value, and accept a well-formed
  digest. The fix does not verify that the digest matches privately held bytes.
- `git merge-tree --write-tree origin/pr-256 origin/pr-101` still reports the
  six PR #101 conflicts, but automatically merges `source_register.py`.
  Automatic merging is not evidence that the resolved branch retains the
  intended behavior after the six manual conflict decisions.

## Required check on the eventual resolved head

Keep PR #256's present-digest validation **and** PR #101's source-rights
`evidence_ref` parsing. Test both contracts on the exact reconciled head:

1. With a fictional `published-unverified` source, reject malformed and
   non-string supplied digests; accept a syntactically valid digest without
   upgrading source identity, rights or editorial state.
2. With fictional grant metadata, keep the separate rights/reuse gate and
   quote-free `link_only` behavior; a valid digest cannot substitute for a
   source-use decision or a private-byte recheck.
3. Re-run the full CI suite on the resolved SHA, including the 2023 empty
   publish-set and source-register tests. Report any changed pilot rows or
   generated claims as a separate editorial/release decision, not a merge
   side effect.

This handoff changes no parser, schema, source record, PDF, political answer,
review mark, generated artifact or routing. PR #101 remains blocked on conflict
resolution and human evidence/review; passing CI is only technical evidence.
