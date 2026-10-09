# Design

## Context

This is an empty repository and a draft specification, not a running service. Programme files and the final candidate list are not yet available. See `proposal.md` for motivation and `specs/` for observable requirements. The public target is a modest 2-vCPU/8-GB host; document processing must not run on that host.

## Goals / Non-Goals

**Goals:** deterministic, inspectable publication from reviewed records; verifiable source lineage; inexpensive read-only serving; explicit coverage and correction history; secure handling of untrusted source documents.

**Non-Goals:** automatic political interpretation or release, user accounts, analytics, browser-side collection, a database or API in production, election predictions.

## Decisions

1. **Build a static site with Python 3.14 tooling.** A CLI validates editorial records and renders versioned JSON/HTML assets; a static web server serves the artifact. This avoids application execution and secrets on the public host. A FastAPI service is deferred until an actual interactive/server-side need appears. Alternative: FastAPI from day one; rejected for unnecessary attack surface and operations.
   Public copy and navigation use Spanish (`es-ES`) in the MVP; text organization should permit later reviewed Catalan and optional English translations.
   The static service runs in Docker for both local preview and production. Python build/extraction and public serving use separate containers/stages; the serving image has no editorial data, PDF parser or credentials. Pin and scan the base by digest for a production release. Alternative: install dependencies directly on the VM; rejected for weaker reproducibility.
   The frontend is designed from a 360–430 CSS-px baseline, with stacked party cards and a concise difference summary; wider layouts are progressive enhancement. Alternative: desktop-first comparison table; rejected because it forces zoom/horizontal scrolling on phones.
2. **Keep input and publication separate.** Programme metadata and editorial positions are versioned text records; original PDFs are referenced by URL and hash, not shipped by default. Extraction, including OCR or AI assistance, happens offline in an isolated environment with resource limits. Only approved records enter a build. Alternative: scrape/process PDFs on the web host; rejected as unsafe and non-reproducible.
3. **Model provenance as a required chain.** Each published claim has a stable ID, programme/version, page or section, URL, extraction method, review state and correction history. Validation rejects absent references or unreviewed claims. A missing statement is a distinct state, not a negative position. Alternative: free-form summaries; rejected because they cannot be audited.
4. **Treat similarity as editorially reviewed data.** Comparison relationships reference claim IDs and describe the precise shared proposal and qualifications. The UI does not infer equivalence from text embeddings or vague keywords. Alternative: live LLM clustering; rejected for bias, instability and cost.
5. **Separate code review from editorial approval.** CI checks schema, deterministic build, tests, accessibility baseline and dependency/secret scans. Human reviewers verify substantive political statements and rights to publish short extracts. Protected deployment consumes a reviewed immutable artifact. Untrusted PRs receive read-only tokens and no deploy secrets. Alternative: auto-publish merged extraction output; rejected.
6. **Design for correction.** Stable IDs, source-version history and dated corrections let a corrected statement invalidate derived comparisons. Publish a clear update timestamp and correction log. Roll back to a prior static artifact if a release is defective; for factual errors, issue a corrected release rather than silently rewriting history.
7. **Use edge caching and measured abuse control.** Cloudflare Free serves as DNS and proxy for the Hetzner static origin. Cache fingerprinted assets and revalidate mutable HTML. Use targeted rate or challenge rules only after testing plan limits and reader impact. Verify the origin cannot be bypassed where feasible. Alternative: universal CAPTCHA; rejected because it blocks legitimate readers and crawlers. A 10,000-concurrent-visitor scenario is a test target, not a capacity guarantee.
8. **Build discoverable pages from approved records.** Render Spanish topic, party, method, and source pages to HTML at build time. Add accurate title, canonical, sitemap, and crawler policy. Do not hide all claims behind client-side JavaScript. Alternative: keyword stuffing or `agents.txt` prompts; rejected because they do not establish trust or guarantee AI-search ranking.
9. **Share stable, neutral URLs.** Give home, topic, and two-party comparison views one Share control. Use `navigator.share` on supported HTTPS devices and copy-link fallback elsewhere. Restore allowlisted selection IDs from a URL; never encode personal or political-preference answers. Give each topic HTML page accurate Open Graph metadata and a locally built neutral preview image. A comparison query can have the topic's canonical URL until separate reviewed pair pages are justified. Alternative: a button for every social network; rejected because direct arbitrary-link posting is not uniformly supported and clutters mobile UI.

## Risks / Trade-offs

- [Static build becomes stale] → timestamp each build, schedule editorial freshness checks, and trigger rebuilds for corrected sources.
- [Selective coverage appears partisan] → publish inclusion rules, all known official candidacies and document availability, including missing/partial states.
- [Extracted text loses context] → require page/section review against original and preserve qualifications.
- [Rights to reproduce excerpts are unclear] → link originals; block quotes until reviewed.
- [PDF/OCR or CI supply chain is compromised] → isolated processing, limits, pinned/audited dependencies before implementation, least-privilege CI.
- [2-vCPU host proves insufficient] → load-test a representative artifact and record latency/memory before release; static serving can be moved independently.
- [Edge cache miss or flood reaches origin] → test cold cache and bursts, monitor cache-hit ratio/origin load, and keep a capacity response plan.
- [Crawler indexing or AI citation fails] → expose useful HTML, source links, update dates, sitemap and canonical URLs; measure discovery without ranking promises.

## Migration Plan

1. Approve editorial methodology and record schema; obtain two lawful pilot programmes.
2. Implement validator, reviewed pilot data, deterministic renderer and automated checks behind the draft OpenSpec change.
3. Preview a non-production artifact; verify provenance, accessibility, security and load profile.
4. Publish an immutable static release behind HTTPS. Keep the preceding artifact for one-step rollback and make editorial corrections via new versioned release.

## Decisions Resolved and Remaining Questions

- **Resolved by E0.3 (ADR-0001):**
  - UI Language: Spanish (`es-ES`) for public MVP, with decoupled strings for future Catalan (`ca-ES`).
  - Domain: `elecciones2026.es` canonical apex, with `elecciones2026.org` and `programaselectorales.es` defensive redirects.
  - Contacts & Privacy: `privacidad@elecciones2026.es` and `seguridad@elecciones2026.es` defined with full public notice text.
  - Release targets: Explicit p95, error rate, edge cache, and €50/mo cost ceiling codified.
  - Named owners: Assigned in `docs/DECISION-RECORD.md`.
- **Remaining Open Questions:**
  - Exact Hetzner datacenter location (e.g. Falkenstein vs Nuremberg).
  - Human Gate G0 signoff by Cesc and the project partner.
