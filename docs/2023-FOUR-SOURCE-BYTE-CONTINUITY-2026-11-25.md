# Four-source 2023 pilot byte-continuity check — 2026-11-25

Roadmap package: **P0.4** (`2023-corpus-completion`, proposal-only). This is a
private, read-only source-access check for the four *registered pilot* URLs,
not a publisher-authenticity, historical-publication, source-rights, editorial,
coverage or release decision. No PDF bytes were saved or committed.

## Reconciled boundary

- Fetched `origin/main` at `d49454c` before the check. Its 2023 register still
  has four `published-unverified` pilot rows (PP, ERC, PNV and Sumar), each with
  `rights_review.status = not_reviewed` and `publication_date = null`. The eight
  2023 example statements remain six `under_review` and two `draft`; the six
  relationship examples remain `invalidated`. These are file counts, not an
  approved candidature denominator or publishable comparison corpus.
- Draft [PR #101](https://github.com/c2ventures/elecciones2026/pull/101)
  remains open at `f8506a1`, with zero GitHub review records and a dirty merge
  state. A simulated merge against `d49454c` reports seven conflicted paths.
  Its four successful test checks and skipped release check date from the old
  head, not a resolved candidate. Merged [PR #166](https://github.com/c2ventures/elecciones2026/pull/166)
  describes itself as the replacement; [PR #276](https://github.com/c2ventures/elecciones2026/pull/276)
  separately audits the post-import integration delta. This check does not
  resolve or duplicate those branches. Current-main checks on `d49454c` are
  successful, which still provides no human review of 2023 content.

## Observed live bytes

On 2026-11-25, the four `direct_url` values from the checked-in register each
returned `200 application/pdf` to a HEAD request. Separate GET requests
completed successfully; response bytes were streamed into SHA-256 and
discarded. None was opened for content review. The resulting hashes matched
the corresponding *existing register hashes* exactly:

| Source ID | GET bytes | SHA-256 observed and registered | Match |
|---|---:|---|---|
| `src-2023-pp-v1` | 8,214,497 | `c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108` | Yes |
| `src-2023-erc-v1` | 1,228,157 | `760db25e48422b74a9b0c3172cab16cf39d010345849e50b921ff8bf61be2854` | Yes |
| `src-2023-pnv-v1` | 3,602,932 | `46fec3a017cdc5c4e506fa5e228b97690071d5a03dfd3d8128392aa20f57d132` | Yes |
| `src-2023-sumar-v1` | 2,567,339 | `d5ccdac0d20f1b93a5f703f180d086041bd988835072dd5cb5d1378bf0195820` | Yes |

This establishes only that these URLs served matching bytes at this check
time. Neither HTTP success nor hash equality proves the publisher's link chain,
that these exact versions existed before the 2023 election, that page locators
are correct, or that summaries/quotes may be reused. HEAD metadata does not
date the document. No `status`, date, rights field or review mark is promoted.

## Reproduction and next gate

Read the four `es-gen-2023` rows from `content/sources/register.json`; for each
`direct_url`, run a bounded HEAD request and a bounded streaming GET, verify
the GET exit status, count bytes and compare its SHA-256 with the row's
`sha256`. Do not persist PDF or extracted text. The check used `curl -sSIL
--max-time 15` for HEAD and `curl -fsSL --max-time 30` for GET. A failed
request or changed hash must be reported as a new source-version candidate,
not silently corrected in the register.

The P0.4 authenticity reviewer still needs a retained publisher-entry/link or
redirect-chain evidence reference for each exact version. The owner must
separately decide 2023 inclusion/document scope, version-specific rights and
historical publication evidence; human editors must verify locators and claims.
PR #101 disposition and any resolved-head CI are independent integration
gates. This check completes none of those tasks.

Validation: parsed `origin/main` register and 2023 examples by election ID;
checked four HTTP responses, GET byte counts and exact hash equality; simulated
the PR #101 merge and checked its reviews/check metadata. `PYTHONPATH=src
python3 -m unittest tests.test_source_register tests.test_schemas -q` passed
36 tests with local Python 3.11; `git diff --cached --check` passed. These
tests do not verify political content or publisher authenticity. No private
evidence store or public output was accessed.
