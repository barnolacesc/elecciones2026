# E4.3 quiz accessibility review record

Scope: `/cuestionario/`, shared header/footer, and every quiz state. Current content
is an explicitly labelled fictional fixture. Public WCAG conformance is **pending**.
No human, device, native-zoom, or screen-reader pass is recorded in this document.

Use the [WCAG 2.2 Recommendation](https://www.w3.org/TR/WCAG22/) and its linked
criterion guidance as the normative reference. Level AA requires the applicable A
and AA criteria for full pages and the complete process. Automated observations
are evidence for particular checks, not a conformance verdict.

## Automated checks

`tests/quiz_browser.cjs` covers portrait/landscape, 200-percent root text size,
spacing, 320px reflow, targets, expanded explanations, and focus visibility.
`tests/quiz_accessibility.cjs` adds actual Tab/Enter/Space/arrow-key operation through
entry, questions, insufficient results, optional review, results, weights, and reset.
It checks native answer-group names, unchanged navigation on answer selection,
heading focus, weight focus restoration, and polite update status.

Local run on 2026-10-12: 35 checks passed on the rebuilt Docker mock preview.
Complete layout/flow regressions and all five privacy cases also passed. Native
type-ahead verifies keyboard selection of the doubled weight; headless macOS popup
keys did not reliably commit a selection and are not recorded as a manual pass.
Remote CI has not run here.

Rendered opaque text pairs are compared without rounding their contrast ratios.
Native control drawing, transparent/complex backgrounds, images, and focus-outline
contrast are left for visual review. The output explicitly lists unmeasured pairs.
The runner retains counts, ratios, state names, and checks in
`build/quiz-accessibility.json`; it records no participant answers or identifiers.

The first run found footer text at 4.4935:1 against white, below the required 4.5:1
for its small text. The quiz stylesheet now uses the darker secondary text token
for that shared footer. Source headings now follow their nesting: h2 on a question,
h5 beneath a result's h4 item, instead of always emitting h3.

## Criterion inventory

All 55 current A/AA criteria are listed below. “Partial” means repository or mock
automation provides some evidence; the remaining checks still require review.
“Candidate N/A” is a proposed reason, not a reviewer decision. Mark an item passed
only after checking the applicable complete page and process. Preserve the criterion
ID, reviewer decision, evidence, date, finding, fix, and retest in the final record.

| Criterion | Level | Current evidence and remaining review |
|---|---|---|
| 1.1.1 | A | Partial: percentages are text; inspect all page images and controls. |
| 1.2.1 | A | Candidate N/A: no audio-only or video-only material. |
| 1.2.2 | A | Candidate N/A: no recorded audiovisual material. |
| 1.2.3 | A | Candidate N/A: no recorded video requiring an alternative. |
| 1.2.4 | AA | Candidate N/A: no live audiovisual material. |
| 1.2.5 | AA | Candidate N/A: no recorded video. |
| 1.3.1 | A | Partial: native groups, labels and nested headings; review accessibility tree and reading. |
| 1.3.2 | A | Partial: single-column DOM; check screen-reader sequence with disclosures open. |
| 1.3.3 | A | Partial: text labels; review instructions for dependence on shape or position. |
| 1.3.4 | AA | Partial: landscape regression; check physical orientation changes. |
| 1.3.5 | AA | Candidate N/A: no personal-information fields. |
| 1.4.1 | A | Partial: scores and selected answers have native/text signals; review visually. |
| 1.4.2 | A | Candidate N/A: no automatic audio. |
| 1.4.3 | AA | Partial: measured opaque text pairs; inspect remaining pairs and all states. |
| 1.4.4 | AA | Partial: doubled root text size; check browser text enlargement. |
| 1.4.5 | AA | Partial: quiz text is HTML; inspect shared page images. |
| 1.4.10 | AA | Partial: 320px reflow; native 400-percent zoom remains untested. |
| 1.4.11 | AA | Pending: inspect radio/select/disclosure boundaries and focus contrast. |
| 1.4.12 | AA | Partial: spacing overrides; repeat with reviewed citation metadata. |
| 1.4.13 | AA | Candidate N/A: no author-added hover/focus popovers; verify shared chrome. |
| 2.1.1 | A | Partial: keyboard flow; repeat in Safari/Firefox and source links. |
| 2.1.2 | A | Partial: Tab traversal; verify reverse traversal and screen-reader modes. |
| 2.1.4 | A | Candidate N/A: no author-added single-character shortcuts. |
| 2.2.1 | A | Candidate N/A: no answer timer; reset happens on explicit exit/reload. |
| 2.2.2 | A | Candidate N/A: no automatic moving or updating content. |
| 2.3.1 | A | Candidate N/A: no flashing material. |
| 2.4.1 | A | Partial: skip link first and reaches main; verify screen-reader landmarks. |
| 2.4.2 | A | Partial: Spanish document title; review state announcements. |
| 2.4.3 | A | Partial: heading and weight focus; review edit/reset/error transitions. |
| 2.4.4 | A | Partial: source context and new-window wording; review real links. |
| 2.4.5 | AA | Pending: verify navigation and method links across final published pages. |
| 2.4.6 | AA | Partial: native labels and heading hierarchy; review Spanish meaning. |
| 2.4.7 | AA | Partial: rendered focus outlines; repeat in each supported browser. |
| 2.4.11 | AA | Partial: settled focus rectangles; inspect at zoom and with browser overlays. |
| 2.5.1 | A | Candidate N/A: no multipoint or path gestures. |
| 2.5.2 | A | Partial: native click activation; test pointer-down/move-away cancellation. |
| 2.5.3 | A | Partial: answer names match visible labels; inspect all controls. |
| 2.5.4 | A | Candidate N/A: no device-motion input. |
| 2.5.7 | AA | Candidate N/A: no dragging operation. |
| 2.5.8 | AA | Partial: quiz targets at least 44px; inspect full page and real citations. |
| 3.1.1 | A | Partial: Spanish document language; verify screen-reader pronunciation. |
| 3.1.2 | AA | Pending: inspect approved source names and multilingual excerpts. |
| 3.2.1 | A | Partial: focusing controls does not advance; verify complete process. |
| 3.2.2 | A | Partial: answer changes stay on item; weights update with explicit selection. |
| 3.2.3 | AA | Partial: shared navigation; review all published pages. |
| 3.2.4 | AA | Partial: consistent controls; review source/reset/edit wording. |
| 3.2.6 | A | Partial: method remains outside changing state; review any other help. |
| 3.3.1 | A | Partial: insufficient answers and invalid-bundle text; verify announcement. |
| 3.3.2 | A | Partial: labelled choices and skip explanation; review real qualifiers. |
| 3.3.3 | AA | Partial: insufficient-answer recovery; verify instructions with a reader. |
| 3.3.4 | AA | Candidate N/A: no submission, transaction, or stored user-data change. |
| 3.3.7 | A | Partial: prior answers remain when editing; verify no redundant entry. |
| 3.3.8 | AA | Candidate N/A: no authentication. |
| 4.1.2 | A | Partial: native role/name/selection; inspect expanded state and live controls. |
| 4.1.3 | AA | Partial: persistent polite status; hear copy/reset/weight announcements. |

## Native zoom and screen-reader review

Use assigned fictional answers, never personal political preferences. Start with
an empty mock session. Record only the environment, task outcome and accessibility
finding; do not retain answers, clipboard payloads, recordings or participant IDs.

For desktop zoom, start with a 1280-by-1024 CSS-pixel content viewport at 100 percent.
Set the browser's own zoom control to 400 percent, record its actual displayed
setting and resulting `innerWidth`, and check all states below. A 320px viewport,
CSS transform, pinch zoom or increased device pixel ratio does not establish this
native browser-zoom test. Also test 200-percent text enlargement, spacing, both
phone orientations, forced colors and reduced motion.

| Task | Expected observable behavior | Actual result |
|---|---|---|
| Enter and inspect method | Main landmark, heading, privacy text, method and start are reachable in order. | Not run |
| Start and choose with arrows | Question and progress are understandable; group/labels/selection are announced; no automatic advance. | Not run |
| Skip and finish early | Skip remains distinct from neutral; insufficient-result explanation and recovery are available. | Not run |
| Open optional review and edit | Item controls have distinct names; editing restores the current selection; new heading is announced. | Not run |
| Assign the first response on eight items | Results appear as text for two fictional examples; the source-gap example has no percentage. | Not run |
| Expand contributions and sources | Nested headings and disclosure states are meaningful; all information remains reachable. | Not run |
| Change and reset topic weights | Selected value/focus survive update; concise status is heard without reading every result. | Not run |
| Reset, reload and exit/back | Empty session and reset status are clear; no old answer remains. | Not run |
| Corrupt and unavailable variants | Readable fallback/method access; no dead controls or partial score. | Not run |
| Inspect approved sources privately | Exact source location and new-window behavior are understandable; long metadata reflows. | Not run: no approved real set |

Run the complete process with VoiceOver/Safari on macOS and NVDA/Firefox on Windows.
Record browser/OS/reader versions, zoom setting, state, criterion IDs, outcome,
finding and retest. Test both forward and reverse keyboard movement, native radio
keys, disclosure activation, and focus after every transition. Browser-generated
accessibility snapshots do not replace listening and operating with these readers.

## Release boundary

Tasks 3.3 and 3.4 remain open until the outstanding native/manual and real-source
checks pass. The conformance review must also cover full pages, the complete
process, supported technology combinations and non-interference. Accessibility
review alone does not approve editorial content, provider privacy, performance,
or deployment. The separate G5 evidence and human release decision still apply.
