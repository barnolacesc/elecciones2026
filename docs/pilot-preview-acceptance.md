# Private 2023 preview acceptance

Roadmap package: E1.4. Release issue: [#44](https://github.com/c2ventures/elecciones2026/issues/44).

## Current boundary

The repository can build a private, pending `es-gen-2023` artifact. It contains
zero approved statements and relationships. A review gap does not mean that a
party has no proposals or opposes a measure. The quiz is unavailable by default.
This artifact does not complete the reviewed three-topic preview or G2 for 2026.

The checks below verify the technical boundary. They do not grant source rights,
authenticate a human review, certify accessibility, or authorize hosted delivery.
The actual host must retain authentication, `noindex` and cache restrictions.
The local test server provides a restrictive application CSP; it does not model
Cloudflare, Basic authentication, TLS, capacity, or origin protection.

## Repeatable technical checks

Run from the repository root with Python, Node and Chromium installed:

```sh
PYTHONPATH=src ELECTIONS_TEST_PILOT_BROWSER=1 python -m unittest discover -s tests -p test_pilot_preview_acceptance.py -v
PYTHONPATH=src python -m unittest discover -s tests -p test_browser_publish_set.py -v
PYTHONPATH=src python -m unittest discover -s tests -p test_pilot_2023_rehearsal.py -v
PYTHONPATH=src python -m unittest discover -s tests -p test_pilot_editorial_audit.py -v
```

The first suite builds a temporary artifact and serves it on an assigned
loopback port. It closes its browser and server and removes its own output.
Ordinary unit runs skip its three browser tests unless the opt-in variable is
set. The mobile CI job enables them with its existing Chromium installation.

| Contract | Permanent evidence |
|---|---|
| All generated HTML routes retain 2023 election, private banner, pending rights notice, matching canonical/social URL, and no withdrawn quotes | `PilotArtifactTests` |
| Housing, education and health remain pending at 360, 390 and 430 CSS px; controls have labels and sufficient height; no clipped content | `PilotBrowserTests.test_pending_topics_keyboard_share_and_mobile_layout` |
| Keyboard skip link, submission and sharing work; duplicate parties report an error and recover | Same browser test |
| Shared URLs restore the selected topic and contain only election/topic/party IDs | Same browser test; existing Node sharing contracts |
| Comparisons send no requests outside the local origin and make only GET requests; no cookies or comparison profile are retained | Same browser test; only the existing visual accent preference is allowed in local storage |
| Home, method, sources, corrections, quiz, party and three topic routes remain readable without JavaScript; original-source links use HTTPS and `noopener` | `PilotBrowserTests.test_static_pilot_routes_remain_readable_without_script` |
| Missing data bundle and foreign-election URL cannot expose fictional claims | `PilotBrowserTests.test_missing_bundle_and_foreign_selection_fail_closed` |
| Synthetic approved positions, relationships, qualifications and exact citations match static/browser output; hostile strings remain inert | Existing `BrowserPublishSetTests`; clearly fictional 2026 records only |
| Drafts, cross-election records, unsafe source URLs and invalidated comparisons cannot publish; failed builds preserve the old artifact | Existing `BrowserPublishSetTests` and pilot/editorial suites |

These browser checks observe Chromium on local HTTP. Native share uses a test
stub; the real device share sheet and copy fallback still require device review.
No private PDF is fetched, and no real review or content record is modified.

## Owner checklist before a reviewed preview

Keep [#42](https://github.com/c2ventures/elecciones2026/issues/42),
[#70](https://github.com/c2ventures/elecciones2026/issues/70) and #44 open until
their respective evidence exists. Use retained records, not issue closure or CI
success, as proof of a review.

1. The owners select two parties and identify two distinct human reviewers.
   Retain each reviewer's approval, scope, date and evidence reference. Confirm
   that the secondary reviewer did not draft the statement.
2. Review the original private source pages against the registered hash/version.
   Confirm physical and printed page labels, publication date, exact summary,
   qualifications and lawful quotation rights. Review each relationship
   separately. Keep pending or unavailable evidence explicit.
3. Build the selected three-topic corpus after those approvals. Repeat the
   technical checks and inspect every source-linked position both with and
   without JavaScript. Current synthetic tests do not approve that corpus.
4. A human Spanish-copy reviewer checks the purpose, election/year labels,
   source status, gaps, neutral comparison language, share text, errors and
   correction contact. Confirm the contact exists and is monitored. Record
   each correction and the version reviewed.
5. A human accessibility reviewer tests keyboard-only navigation and a screen
   reader on a real phone and desktop. Record device, OS, browser, reader and
   date. Check heading/landmark order, labels, status announcements, visible
   focus, source-link names and new-window notice. Test zoom/text enlargement,
   contrast and a narrow viewport. Check both source dialogs and focus return
   when approved content makes those controls available.
6. A device reviewer tests touch selection, native share, cancellation and copy
   fallback on the supported phones. Open the resulting URL in a fresh session.
   Confirm that source links open the intended page and no personal answer or
   tracking token enters the URL. Record failures and fixes.
7. The owners record a dated decision for the exact artifact: pending withdrawal
   preview or reviewed historical pilot, authorized audience, immutable image
   digest, CI evidence, source/review versions and unresolved limits. Use
   [#71](https://github.com/c2ventures/elecciones2026/issues/71) for protected
   delivery and verification. Keep public release and G2 for 2026 separate.

For each manual check, retain the reviewer identity, date, artifact digest,
test environment, result and linked corrections. This is an evidence checklist;
it is not a completed review record.
