# Tasks

## 1. Editorial contract and pilot sources

- [x] 1.1 Agree the topic taxonomy, candidate inclusion and coverage policy; verify a reviewed methodology document and representative missing-source cases exist.
  - Evidence: Policy version 1.0.0 documented in `docs/CONTENT-METHODOLOGY.md`; taxonomy v1.0.0 in `content/taxonomy.json`; party naming fixtures in `content/examples/parties.json`; programme status examples in `content/examples/programmes/` covering official, partial, replaced, and missing states; 14 automated tests passing in `tests/test_methodology_examples.py` and CI workflow `.github/workflows/ci.yml`. Awaiting human gate G0 approval.

- [ ] 1.2 Register two lawful pilot programme versions with official URLs, dates, rights status and SHA-256; verify hashes against downloaded originals and document accessibility.
- [ ] 1.3 Define versioned programme, claim, relationship and correction schemas; verify example valid and invalid records against the schema validator.
- [ ] 1.4 Add an immutable election ID to sources, positions, and builds; verify 2023 pilot pages are labelled 2023 and a 2023 source cannot appear in a 2026 comparison.

## 2. Source and editorial validation

- [ ] 2.1 Implement offline import boundaries and size/type limits for source files; verify malformed or oversized input is rejected without executing embedded content.
- [ ] 2.2 Implement provenance and review-state validation; verify missing references, unknown programme versions, unreviewed claims and unlicensed quotes fail the build.
- [ ] 2.3 Enter pilot positions with stable IDs, qualifications and page/section citations; verify two human reviewers can follow each published assertion to its original context.
- [ ] 2.4 Implement versioned corrections and relationship invalidation; verify changing a source claim invalidates dependent comparison output.

## 3. Comparator and public artifact

- [ ] 3.1 Implement a deterministic Python 3.14 static build; verify identical reviewed input produces identical output without network access or runtime secrets.
- [ ] 3.2 Implement one-topic/two-party selection and claims grouped by measure; verify a phone user sees both party positions and source links before moving to the next measure, without tabs or horizontal scroll.
- [ ] 3.3 Show reviewed agreements, divergences, qualifications and missing/partial coverage; verify missing data is never rendered as opposition or agreement.
- [ ] 3.4 Publish a concise source coverage/method page, update timestamp and correction history; verify every visible claim exposes its provenance without a separate proposal-detail page.
- [ ] 3.5 Add keyboard/screen-reader and mobile-first checks at 360, 390 and 430 CSS px; verify no horizontal overflow, 44-px touch targets, readable comparison without zoom and source links reachable in one-column flow.
- [ ] 3.6 Use Spanish for every public UI/editorial string and structure strings for future reviewed translations; verify the released artifact declares `lang=es` and contains no accidental Catalan UI copy.
- [ ] 3.7 Render crawlable topic, party, methodology and source pages with canonical URLs, update dates, a sitemap and accurate `robots.txt`; verify a text-only fetch exposes approved claims and source references without JavaScript.
- [ ] 3.8 Add one neutral Share control to home, topic, and comparison views with native share and copy-link fallback; verify stable allowlisted URL state, no tracking/political-answer parameters, keyboard access, and iOS/Android behavior.
- [ ] 3.9 Generate approved neutral Open Graph metadata and a local preview image for shareable pages; verify public preview rendering and canonical behavior after a domain exists.

## 4. CI and secure release

- [ ] 4.1 Add least-privilege CI for formatting, tests, schema validation, deterministic build and secret/dependency scans; verify a fork PR cannot access deploy credentials.
- [ ] 4.2 Review actual pinned build dependencies and PDF-processing tools for supported versions/advisories; verify the dependency inventory and scan report are attached to release evidence.
- [ ] 4.3 Preview the immutable artifact, complete editorial/security review and benchmark on the intended 2-vCPU/8-GB class; verify recorded latency (origin p95 < 250 ms), memory (< 150 MB), and release checklist against targets in `docs/DECISION-RECORD.md`.
- [ ] 4.4 Deploy read-only static output over HTTPS with minimal host privileges, health monitoring and retained prior artifact; verify rollback restores the preceding version (RTO < 5 min).
- [ ] 4.5 Pin and scan the Docker serving image by digest and verify local Compose preview and production serve the same artifact with a non-privileged user, read-only filesystem and no build-only tools.
- [ ] 4.6 Configure Cloudflare DNS/proxy and tested cache rules for the Hetzner origin; verify edge cache behavior (ADR-0001 targets: >= 99% static assets, >= 90% HTML documents, >= 95% aggregate steady-state), direct-origin restrictions where feasible, and the current plan limits for targeted abuse rules.
- [ ] 4.7 Run a representative 10,000-concurrent-visitor scenario with cold-cache and burst phases; record p95 (edge < 150 ms, peak < 200 ms), error rate (5xx < 0.05% normal, < 0.5% burst), cache-hit ratio (>= 85% cold-cache recovery), origin load (<= 200 req/s, CPU < 70%), and cost (within €50.00/mo ceiling), and verify each approved release target in `docs/DECISION-RECORD.md` or document a capacity change.
- [ ] 4.8 Review repository documents and OpenSpec artifacts against the current ASD-STE100 controlled dictionary with a qualified reviewer; verify the review record before any strict-compliance claim.

## Workflow follow-up

- Archive this OpenSpec change only after implementation and review evidence is complete.
- Propose simulator, CIS observatory and quiz as separate OpenSpec changes.
