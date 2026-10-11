# Elections 2026 — Roadmap draft 0.2

## 1. Purpose and rules

The site will help people compare party programmes for the Spanish general election on 29 November 2026. It will not recommend a vote or predict party conduct. The election date is in [BOE-A-2026-20742](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742). Official changes take priority.

Cesc and the team will provide programme files later. This draft does not assume that the files, the final candidate list, or publication rights are available. The site must show source gaps. “Not found” must not mean “opposed.” Do not republish full PDF files or long extracts without a rights review.

The public MVP uses Spanish (`es-ES`). The repository uses English for documentation, OpenSpec, code, and comments. Apply [the writing standard](docs/WRITING-STANDARD.md). A later phase can add reviewed Catalan translation. Add English only if there is a clear need.

## 2. MVP — Programme comparison

### User flow

1. Show purpose, election date, source coverage, update date, and an entry point to comparison.
2. Let a visitor select one topic and exactly two parties in the initial MVP.
3. Show a short reviewed summary of specific agreements and differences. Show each party statement in equal space.
4. Link each statement to the original programme, version, page or section, and review date. Show conditions and qualifications.
5. Link to the original programmes and a concise source coverage/method page with a correction policy. Do not imply that a web report form already works.
6. Show absent, partial, or replaced documents explicitly. Do not invent positions.

Initial topics: housing; education; health and social services; economy, work, and tax; immigration; foreign policy and the EU; climate and energy; institutions and rights. Approve and version the taxonomy before content work.

### Mobile-first UX

Design for 360–430 CSS px first. Use a one-column comparison, a concise summary before detail, no forced horizontal scroll, legible text, and touch targets at least 44 CSS px high. Keep source links close to statements. Test the full flow with touch and keyboard at 360, 390, and 430 px. A wider desktop layout is a later enhancement, not the baseline. Measure loading on a simulated mobile network.

The first Stitch review favors a comparison **grouped by measure**, with both party positions in each section. The tab variant hides one party at a time and is not the default. Treat the exported screens as visual references only. See [Stitch review](docs/STITCH-REVIEW.md).

The MVP needs only four destinations: home, selection, comparison, and concise sources/method. A separate proposal-detail page, full coverage matrix, profile icon, tab mode, advanced filters, PDF download controls, and a report form are not launch requirements. The source link can open the original programme at its documented location. Add deeper views only after testing.

Make the home, topic, and two-party comparison views easy to share. Use a stable URL, one neutral Share control per view, the phone's native share sheet when available, and a copy-link fallback. Prepare accurate social preview metadata. Do not add vote-change answers or tracking data to shared URLs. See [sharing plan](docs/SHARING.md).

Do not show a report control that appears to submit data when no service exists. The method page can say “La función para avisar de errores estará disponible más adelante.” A [separate OpenSpec proposal](openspec/changes/source-feedback-reporting/proposal.md) defines the later database-backed feature. It does not block the quiz.

### Editorial data and review

A programme record needs party/candidacy ID, official URL, publisher, dates, language, version, SHA-256 hash, rights status, and coverage state. A statement needs a stable ID, topic, neutral text, qualification, exact source location, and review state. A relationship between statements needs specific grounds and human review. Keep dated corrections and old source versions.

Treat PDF, OCR, and web source text as untrusted input. Extract offline with file, time, and resource limits. Extraction can propose data; it cannot publish it. Human reviewers must verify substantive statements and comparison links. A build must reject unreviewed statements, missing references, and unapproved quotes.

### MVP acceptance

- A visitor can compare two pilot programmes across topics on a 390-px phone without zoom or horizontal scroll.
- Each published statement can be traced to an exact source and version.
- Missing data stays visible and never becomes a negative party position.
- A corrected statement updates dependent comparisons and keeps a correction record.
- The build is reproducible from approved records and needs no network or secrets at runtime.
- Editorial, accessibility, security, and representative load checks pass before release.

The MVP excludes polls, seat forecasts, accounts, comments, a quiz, live AI summaries, a public API, and user tracking.

## 3. Future phases and OpenSpec changes

The ordered delivery plan, milestones, and agent work packages are in [the OpenSpec delivery roadmap](openspec/ROADMAP.md). The project roadmap is not a single OpenSpec artifact. Each phase has its own change. The MVP has proposal, specs, design, and tasks. Later changes have proposals only until their prerequisites and editorial decisions are ready.

### Phase 2 — Programme alignment quiz

Use short reviewed programme statements with balanced party/topic coverage. Keep answers in the browser by default. Explain weights, skipped answers, uncertainty, and bias. Label the result as proximity to the answered questions, not a vote recommendation. See [`programme-alignment-quiz`](openspec/changes/programme-alignment-quiz/proposal.md).

### Phase 3 — Seat and coalition simulator

Accept manual seat counts. Validate chamber totals and applicable parliamentary rules against official sources. Show an accessible hemicycle and a text table. Show arithmetic majorities, not political probability. A vote-to-seat model needs a separate specification, data model, and validation. See [`seat-coalition-simulator`](openspec/changes/seat-coalition-simulator/proposal.md).

### Phase 4 — CIS data observatory

Use the [official CIS study catalogue](https://www.cis.es/es/estudios/catalogo). Preserve field dates, sample, population, question wording, method, and version. Compare time series only when measures are comparable. Distinguish a poll result from an election result and a direct response from an estimate. Verify official data access and terms before automated import. See [`cis-data-observatory`](openspec/changes/cis-data-observatory/proposal.md).

### Phase 5 or later — Localization

Add reviewed Catalan copy after the Spanish MVP. Consider English only if demand justifies it. Do not auto-translate political statements into publication without human review. See [`reviewed-localization`](openspec/changes/reviewed-localization/proposal.md).

### Optional post-MVP track — Source feedback

A reader may later submit a short discrepancy report for a statement or source. This requires a write API, database, spam controls, retention policy, and editorial review queue. It is not a simple static-page feature and must not publish changes automatically. See [`source-feedback-reporting`](openspec/changes/source-feedback-reporting/proposal.md). It can be planned after the MVP without changing the quiz → simulator priority.

### Exploratory later track — Prior commitment follow-through

Investigate whether the site can show the documented status of selected, measurable commitments from earlier programmes. This is **not** a score of party honesty, a "lies" percentage, or an MVP feature. A public percentage would require a defensible denominator, a stable observation date, consistent inclusion rules, and comparable evidence for every party. Otherwise, show individual commitments with evidence and an explicit "cannot determine" state, or reject the feature. Do not infer fulfilment from a single economic indicator or attribute a coalition outcome to one party without context. See [`commitment-follow-through`](openspec/changes/commitment-follow-through/proposal.md).

### Optional post-MVP track — Official budget context

Start with the approved 2023 PGE official policy-by-section table. Show the size and share of spending policies and their administrative sections; do not label every section a ministry or invent programme-level amounts. Start with a mobile ranked-bar list and an accessible table; a treemap is optional. Label the year, scope, denominator, units, and source. Keep the 2023 approved budget, the 2026 extended budget, and IGAE execution figures distinct. This is public-finance context, not a measure of any party's performance. See [source research](docs/BUDGET-SOURCE-RESEARCH.md) and [`budget-context`](openspec/changes/budget-context/proposal.md).

## 4. Architecture and operations

Use Python 3.14 for an offline validator and static build. Use Docker for local preview and production. A small non-privileged container serves only static output; it does not process PDFs or store visitor data. Use FastAPI only after a separate need and OpenSpec change.

The owner selected an existing IONOS Ubuntu VPS with 1 vCPU and 1 GB RAM, with Cloudflare Free as DNS and proxy. The domain `eleccionesespaña2026.es` is registered at DonDominio; Cloudflare delegation is pending. The earlier 2-vCPU/8-GB planning baseline does not establish capacity on this smaller host. Cache versioned static assets at the edge. Give HTML a short or revalidated lifetime so corrections propagate. Verify the current Cloudflare plan limits before choosing WAF and rate rules. Protect the origin from direct access where feasible; restrict ports, enable TLS, use minimal privileges, apply updates, monitor availability, and keep a rollback artifact. Do not challenge every reader with a CAPTCHA. Use targeted mitigations if evidence shows abuse, and check accessibility and false positives.

Define a measurable load test before release: 10,000 concurrent *visitors* is a target scenario, not a promise that 10,000 requests per second can reach a 2-vCPU origin. Record cache-hit ratio, origin request rate, p95 latency, error rate, memory, and cost under normal and burst loads. Test origin-failure behavior and plan a capacity step-up if results fail. See [architecture](docs/ARCHITECTURE.md) and [security](docs/SECURITY.md).

## 5. Discoverability and AI search

Publish useful Spanish landing, topic, party, method, source, and correction pages as crawlable HTML with clear titles, headings, canonical URLs, internal links, a sitemap, and an accurate `robots.txt`. Use structured data only where it matches visible content and a supported schema. State author/editor, source, and update date. Make each factual claim easy to cite. Do not put keyword spam or manipulative instructions in `robots.txt`, privacy policy, or an `agents.txt` file. No file can guarantee a top AI-search result. Measure indexing and referrals, then improve real content. Follow [Google Search Central guidance for AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).

## 6. Milestones

| Milestone | Exit gate |
|---|---|
| M0 — Editorial agreement | Taxonomy, coverage, source rights, and reviewers agreed |
| M1 — OpenSpec MVP | Proposal, specs, design, and tasks approved |
| M2 — Pilot data | Two real programmes with reviewed, source-linked statements |
| M3 — Product pilot | Mobile comparator, tests, security review, and load results |
| M4 — Public release | Domain, Cloudflare/IONOS setup, rollback, monitoring, source coverage |
| M5 | Programme alignment quiz with local scoring, source links, and fairness/privacy review |
| M6 | Manual seat and coalition simulator with verified rules |
| M7 | CIS observatory with comparable official study data |
| M8 | Reviewed Catalan localization; English only after a demand decision |
| M9 (exploratory) | Go/no-go decision on evidence-based prior commitment follow-through; no score is presumed |
| M10 (optional) | Reviewed official budget breakdown with a defensible denominator and accessible mobile view |

Package dependencies and acceptance evidence are in [the delivery roadmap](openspec/ROADMAP.md).

## 7. Decisions needed before a public release

Choose the name and domain; candidate inclusion rule; source acquisition and rights; editorial owners and review process; correction policy; privacy notice; publication schedule; load-test workload and acceptable latency/error budget. The local draft does not require these decisions. Public content and release do.
