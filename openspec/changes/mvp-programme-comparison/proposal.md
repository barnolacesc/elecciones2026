# Proposal: MVP programme comparison

## Why

Citizens need a fast, auditable way to compare the 2026 Spanish general-election programmes by topic without reading every document end-to-end. A source-linked, neutral comparison can reduce search cost while preserving access to each original programme and making gaps explicit.

## What Changes

- Add an offline workflow to register original programmes with provenance, version, hash, rights status and coverage.
- Add human-reviewed, topic-tagged statements and explicit comparison relationships, with source page/section and correction history.
- Generate a lightweight public static site with party/topic selectors, side-by-side views, agreements, differences, source links, methodology and incomplete-data notices.
- Keep the MVP to four mobile-first destinations: home, a two-party/one-topic selector, comparison grouped by measure, and a concise sources/method page. Source links open the original document. A separate proposal-detail page, tabs, advanced filters, download controls, correction form, and account/profile UI are not required for launch.
- Do not render a working discrepancy-report form or a per-statement report button in the MVP. The method page may state plainly that in-site reporting is not available yet. A later change will specify a secure write API and database if approved.
- Publish Spanish, mobile-first, crawlable HTML pages for topics, parties, methodology and sources. Use accurate metadata and a sitemap. Do not promise search ranking.
- Serve a Dockerized static artifact through Cloudflare Free to a Hetzner origin. Measure edge cache and burst behavior before release.
- Add deterministic validation/build gates, accessibility and security checks; keep ingestion away from production.
- No accounts, personal-data storage, live LLM summaries, CIS trends, seat simulation or alignment quiz in this change.

## Capabilities

### New Capabilities

- `programme-provenance`: Track official documents, versions, coverage and rights; block unsupported claims.
- `editorial-statements`: Maintain reviewed, neutral, source-linked programme positions and corrections.
- `programme-comparison`: Present fair topic-based comparisons, agreements, differences and missing positions.
- `static-publication`: Build and serve a reproducible, accessible static artifact without a user-data backend.

### Modified Capabilities

None (new project).

## Impact

Python 3.14 offline tooling in `src/`, versioned content in `content/`, generated static assets in `site/`, tests and CI to be implemented after spec/design approval. Publication requires real programme files, an editorial reviewer, a rights decision and an independent security review.
