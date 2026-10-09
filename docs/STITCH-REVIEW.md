# Stitch design review — 2026-10-09

## Input

The user provided a ZIP with seven PNG screens, seven generated HTML files, and one design-system document. The ZIP was inspected as data. No generated script was run. The files remain outside the project repository in a local review folder.

## Decision

Use the **comparison grouped by measure** screen as the mobile MVP reference. It puts both party positions under the same measure. This structure supports direct comparison better than the tab view, which hides one party at a time. Keep tabs only as a possible secondary reading mode after usability tests.

Use the home, selection, source coverage, statement detail, and method screens as visual references. Keep the four-item bottom navigation only if testing shows that each item has a distinct MVP purpose. Remove the profile icon: the MVP has no user accounts.

## Changes required before implementation

1. Replace all fictional programme quotes, policy claims, party counts, page numbers, official record IDs, dates, review badges, file hashes, and download links with explicit placeholders. The current images look like verified political evidence, but they are generated examples.
2. Reduce density on the grouped comparison screen. Show a short neutral summary, then one measure at a time or compact measure sections. Expand source detail on demand. Keep both party positions and the source path in the same flow.
3. Distinguish direct quotation, neutral summary, reviewed inference, and missing mention. Do not label all summaries as literal transcription. Remove claims such as “100% verified” until editorial evidence supports them.
4. Remove generated runtime dependencies on Tailwind CDN, Google Fonts, and externally hosted images. Build audited local assets. Do not copy the generated HTML or JavaScript directly into production.
5. Test actual mobile interaction at 360, 390, and 430 CSS px: tap targets, scrolling, focus, screen reader, source links, layout overflow, and perceived load time. The PNG screens alone do not prove these behaviors.
6. Remove the working discrepancy-report form and per-statement report actions from the MVP. The static site has no write API or database. The method page can identify the feature as planned. Implement it only through the separate `source-feedback-reporting` change.

## Open design questions

- Do users prefer grouped measure cards with expandable detail, or a shorter summary-first path?
- Should the source coverage page show technical fields such as hashes to all readers, or place them in an advanced detail view?
- Is the permanent bottom navigation useful with only four MVP destinations, or does it take too much phone space?

The design is a reference, not an approved content source or production implementation.
