# ERC 23J programme: version-chronology lead — 2026-11-07

Roadmap package: **P0.9** (`2023-corpus-completion`, proposal-only). This is a
publisher-page and repository-record audit for `src-2023-erc-v1`, not a review
of programme text, source rights, political positions or publication approval.
No PDF was downloaded or committed for this audit.

## Reconciled baseline

- `origin/main` at `488b6f5` still has four `es-gen-2023` pilot source rows.
  All four are `published-unverified`, have `publication_date: null` and
  `rights_review.status: not_reviewed`. This is neither an approved candidature
  denominator nor complete topic coverage.
- The ERC row names the [official programmes index](https://www.esquerra.cat/transparencia/programes-electorals/)
  and a [direct PDF URL](https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf).
  Its URL path contains `20230905`; that string does **not** establish when
  this exact PDF version was first published.
- Draft [PR #101](https://github.com/c2ventures/elecciones2026/pull/101)
  remains open and conflicting with main. Its old green checks do not test a
  reconciled head or satisfy source rights and editorial review. Draft
  [PR #207](https://github.com/c2ventures/elecciones2026/pull/207) handles
  its current integration conflict; this packet does not duplicate that work.

## Publisher-page observations

Checked 2026-11-07 without fetching PDF bytes:

1. [ERC's programme announcement](https://www.esquerra.cat/esquerra-republicana-erc-programa-electoral-referendum-amnistia-republica-catalana/)
   displays **5 July 2023** and **21 March 2024** next to the byline. It says
   a programme was made public for 23J and links to the party's campaign site,
   not to the registered PDF URL. The two displayed dates need interpretation;
   neither binds the registered hash to a pre-election publication date.
2. The [official programmes index](https://www.esquerra.cat/transparencia/programes-electorals/)
   is indexed with a `Corts espanyoles / 2023` entry and a displayed last
   update of 20 February 2024. A direct automated page fetch returned HTTP
   403, so this run could not inspect its current outbound link or revision
   history. An indexed entry is a discovery lead, not byte-version proof.
3. A HEAD request to the registered static PDF URL returned HTTP 200 with
   `application/pdf`. The campaign-site URL linked by the announcement returned
   HTTP 200 to HEAD, but its fetched HTML did not expose a PDF/programme link
   in `href` or `src` attributes. Availability today establishes neither
   historical availability of the registered bytes nor reuse permission.

## Review handoff

The source-authenticity reviewer should retain a dated publisher-page or
archive capture that links the relevant programme to an exact private
source version/hash; separately establish whether that version was available
before 23 July 2023, or record the date as unknown. Compare any campaign-site
version, transparency-index target and registered PDF privately before
claiming equivalence. The rights owner then decides permitted uses for that
exact version; statement and relationship reviewers decide content separately.
Do not change the ERC register date, rights state or PR #101's six candidates
from this lead. If the exact-version chronology remains unresolved, the
P0.9 publication rule needs an owner decision, not an inferred date.

The current-main CI is red on unrelated test/browser/container checks (latest
checked run [42211358887](https://github.com/c2ventures/elecciones2026/actions/runs/42211358887)); a new PR check cannot be treated as editorial review.
