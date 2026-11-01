# Decision Record: Language, Domain, Privacy Notice, Service Levels, and Cost Ceiling

- **Record ID:** ADR-0001 (Roadmap Package `E0.3`)
- **Date:** 2026-10-09
- **Status:** Proposed — Awaiting Human Gate G0 Approval (Cesc and Project Partner)
- **Applicable OpenSpec Change:** `mvp-programme-comparison`
- **Related Issues:** Issue #2 ([E0.3])
- **Related OpenSpec Tasks:** 4.3, 4.6, 4.7
- **Dependencies:** None

## E3.3 verified setup update — 2026-10-12

The owner selected the existing IONOS Ubuntu VPS (1 vCPU, 1 GB RAM) and registered
`eleccionesespaña2026.es` at DonDominio. Use
`https://xn--eleccionesespaa2026-83b.es` as canonical base and
`preview.xn--eleccionesespaa2026-83b.es` for authenticated staging. Cloudflare
delegation and proxied preview DNS are active. The owner configured Origin CA
TLS, Full (strict), global AOP and HTTP Basic authentication. [Delivery run
38182379207](https://github.com/c2ventures/elecciones2026/actions/runs/38182379207)
passed manual authorization, restricted SSH, origin health, unauthenticated
rejection and exact authenticated home-content verification. The owner selected
manual dispatch because required environment reviewers are unavailable on the
private repository plan; it is self-approval, not independent review. See the
[dated setup record](../ops/SERVER-MIGRATION.md). DNSSEC, public routing, full origin
probes, monitoring, live rollback/restore and actual-host capacity remain open.
These facts supersede the provider/domain assumptions below. The older Hetzner sizing, throughput and
price/traffic estimates remain historical proposals, not evidence for IONOS.
Existing service targets, cost ceiling and G0/G4 gates are unchanged. Contact
mailboxes remain provisional and need separate owner verification.

---

## 1. Context and Problem Statement

The Elections 2026 project provides an auditable, non-partisan comparison of party programmes for the Spanish general election on 29 November 2026.

Before implementation and deployment proceed, the project requires explicit, binding policy decisions on:
1. Interface, repository, and translation languages.
2. Domain name, canonical URLs, and DNS architecture.
3. Privacy notice, data minimization, and regulatory compliance under GDPR and Spanish LOPDGDD.
4. Release service level objectives (SLOs), error budgets, latency, edge cache targets, and concurrency limits.
5. Monthly cost ceiling and financial governance.
6. Named owners and operational responsibilities.

This decision record establishes these operational and editorial contracts.

---

## 2. Decision Summary

| Area | Decision | Reference / Target |
|---|---|---|
| **Repository Language** | English (Controlled Technical English) | ASD-STE100 principles; all code, PRs, docs, and comments |
| **Public Interface Language** | Spanish (`es-ES`) | Build generates `<html lang="es">`; external copy in Spanish |
| **Localization Sequence** | Spanish MVP → Reviewed Catalan (Phase 5 / G8) → English (optional, demand-gated) | No unreviewed machine translation in public output |
| **Primary Domain** | `eleccionesespaña2026.es`, registered at DonDominio | ASCII canonical base: `https://xn--eleccionesespaa2026-83b.es`; DNSSEC unverified |
| **Defensive Domains** | `elecciones2026.org`, `programaselectorales.es` (placeholder targets) | Permanent 301 redirects to canonical domain once acquired |
| **Preview / Staging Domain** | `preview.xn--eleccionesespaa2026-83b.es` | Active proxied private preview; Basic authentication, no-store/noindex |
| **Privacy Architecture** | Zero personal data collection; zero tracking cookies; no cookie banner required | Complies with GDPR Art. 5, 6, 9 and LSSI-CE Art. 22.2 |
| **Technical Log Retention** | Ephemeral edge/origin logs retained <= 14 days solely for network security and DoS defense | IP anonymization; no behavioral profiling |
| **Edge Cache-Hit Target** | >= 95% steady-state; >= 85% cold-cache phase; >= 99% for fingerprinted assets | Cloudflare CDN proxy in front of active IONOS origin; public cache evidence pending |
| **p95 Latency Target** | < 150 ms edge cache hit; < 250 ms origin response; < 500 ms mobile page delivery | Evaluated on 360–430 CSS px mobile baseline |
| **Error Rate Budget** | HTTP 5xx < 0.05% steady-state; < 0.5% during 10,000-visitor burst scenario | 99.5% normal monthly availability; 99.9% election week |
| **Concurrency Scenario** | 10,000 concurrent active readers (~1,000–2,000 req/s edge; <= 200 req/s origin) | Acceptance target; not verified on active IONOS 1-vCPU / 1-GB host |
| **Cost Ceiling** | €50.00 / month hard maximum; ~€9.00–€15.00 / month expected baseline | Alerts at €25.00 (50%) and €40.00 (80%); no uncapped billing |
| **Operational Owner** | Cesc (`cesc`) / Infrastructure Lead | Responsible for IONOS, Cloudflare, TLS, DNS, monitoring |
| **Editorial Owner** | Cesc and Project Partner | Responsible for inclusion rules, claims, and corrections |
| **Release Gatekeeper** | Release Engineering Lead | Responsible for CI scans, image digests, and rollback |

---

## 3. Decision 1: Language and Translation Governance

### 3.1 Repository and Internal Work Language
- All code identifiers, comments, commit subjects, pull requests, technical documentation, and OpenSpec artifacts MUST use English.
- Technical documentation MUST follow ASD-STE100 principles: short sentences, direct active verbs, defined terms, consistent names, and explicit conditions.
- Any formal claim of ASD-STE100 compliance requires a qualified human reviewer with the current controlled dictionary and specification.

### 3.2 Public Interface Language
- The public MVP user interface, summaries, navigation, metadata, and methodology MUST use Spanish (`es-ES`).
- The static HTML build MUST declare `<html lang="es">`.
- Public copy MUST NOT contain untranslated English or unintended regional variants.

### 3.3 Text Decoupling and Architecture
- Public UI strings and editorial labels MUST be stored in versioned translation dictionaries or schema-governed records separate from Python rendering logic and HTML templates.
- Code logic MUST reference text keys, preventing code refactoring when adding translations.

### 3.4 Localization Roadmap and Quality Gate
- Spanish is the authoritative source language for all published political claims and comparisons.
- Catalan (`ca-ES`) localization is scheduled for Phase 5 / Epic E7 (`reviewed-localization`) under Gate G8.
- English public interface text is optional and deferred until validated public demand and dedicated editorial capacity exist.
- Automated or machine-translated political statements MUST NOT be published without human editorial review and approval against the original party document.

---

## 4. Decision 2: Domain, Branding, and DNS Architecture

### 4.1 Domain Selection
- **Registered Primary Domain:** `eleccionesespaña2026.es`, bought at DonDominio. Cloudflare delegation is active.
- **Primary Canonical Base:** `https://xn--eleccionesespaa2026-83b.es`. Public routing remains gated by G4.
- **Defensive / Secondary Domains:** `elecciones2026.org` and `programaselectorales.es` remain proposals. Acquisition and redirects are not verified.
- **Staging / Preview Domain:** `preview.xn--eleccionesespaa2026-83b.es` is active with origin Basic authentication and no-store/noindex.
- **Historical placeholders:** `elecciones2026.es` and `preview.elecciones2026.es` were the original primary and preview targets. They are superseded by the registered domain; retained contact addresses still need separate mailbox verification.

### 4.2 Canonical Routing and Redirects
The redirects below are public-release requirements; they are not verified active.

- Canonical base URL: `https://xn--eleccionesespaa2026-83b.es/`.
- All alternate endpoints MUST return an immediate HTTP 301 permanent redirect to the canonical HTTPS apex URL:
  - `http://xn--eleccionesespaa2026-83b.es/*` → `https://xn--eleccionesespaa2026-83b.es/*`
  - `http://www.xn--eleccionesespaa2026-83b.es/*` → `https://xn--eleccionesespaa2026-83b.es/*`
  - `https://www.xn--eleccionesespaa2026-83b.es/*` → `https://xn--eleccionesespaa2026-83b.es/*`
  - All defensive domain requests → `https://xn--eleccionesespaa2026-83b.es/*`
- HTTP Strict Transport Security (HSTS) MUST be enabled once DNS and TLS stabilization is verified: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.

### 4.3 Staging and Preview Environment Protection
- `preview.xn--eleccionesespaa2026-83b.es` MUST require authentication (via Cloudflare Access or HTTP Basic Auth) to prevent public disclosure of unreviewed draft data.
- The preview environment MUST emit HTTP header `X-Robots-Tag: noindex, nofollow, noarchive` and a restrictive `robots.txt` disallowing all crawling.

### 4.4 DNS and Proxy Configuration
- DNS management and edge caching MUST be handled via Cloudflare.
- DNSSEC MUST be enabled at the domain registrar and configured within Cloudflare. Verification remains open.
- The origin IP address on IONOS MUST remain masked behind the Cloudflare proxy. Direct access to port 80/443 on the IONOS origin from non-Cloudflare IP ranges SHOULD be blocked via firewall rules.

---

## 5. Decision 3: Privacy Notice and Data Minimization Policy

### 5.1 Regulatory Context and Principles
- The project operates under Regulation (EU) 2016/679 (General Data Protection Regulation - GDPR) and Spanish Organic Law 3/2018 (LOPDGDD).
- Political opinions constitute Special Category Data under Article 9 GDPR. The system is intentionally architected to ensure the project NEVER receives, processes, or stores user political opinions or voting preferences.

### 5.2 Data Minimization Architecture
1. **No User Accounts:** The MVP has no user registration, login, profiles, or sessions.
2. **No Tracking Cookies:** The site sets zero tracking cookies, zero analytics cookies, and zero advertising beacons.
3. **No Cookie Banner Required:** Under Article 22.2 of the Spanish Law 34/2002 (LSSI-CE) and AEPD guidelines, because no non-essential cookies, trackers, local storage identifiers, or device fingerprinters are used, no cookie consent banner is legally required or displayed.
4. **Client-Side Comparison:** Comparison selections (topic and parties) exist solely in browser DOM memory. When shared, parameters exist in the URL query string or hash (e.g., `/temas/vivienda/?partidos=psoe,pp`) solely to allow the recipient's browser to restore the view. No comparison query is written to an origin database.
5. **No Third-Party CDNs or External Fonts:** All assets, stylesheets, scripts, and fonts MUST be self-hosted within the static artifact. No requests are made to Google Fonts, external Tailwind CDNs, or third-party telemetry endpoints.

### 5.3 Technical Access Logs
- Cloudflare edge and IONOS origin process standard HTTP connection metadata (client IP, request method, URI path, HTTP status, User-Agent, and timestamp) strictly under Article 6.1(f) GDPR (legitimate interest for network security, abuse defense, and availability monitoring).
- Server logs MUST be rotated and permanently deleted within a maximum retention window of 14 days.
- Client IP addresses in diagnostic logs SHOULD be truncated or anonymized. Technical logs MUST NOT be linked to user identity or behavioral profiles.

### 5.4 Privacy Boundary for Future Features
- **Alignment Quiz (Epic E4):** Scoring algorithms MUST execute entirely client-side in browser memory. Answers and proximity scores MUST NOT be transmitted to any project server or saved in persistent server databases.
- **Source Feedback Reporting (Epic E8):** Discrepancy reporting is an optional post-MVP capability. Before implementation, it requires a separate threat model, data retention policy, and Data Protection Impact Assessment (DPIA).

### 5.5 Official Public Privacy Notice (Spanish Text)
The public site MUST display or link to the following plain-language privacy notice:

```markdown
### Aviso de Privacidad y Protección de Datos

**Responsable del tratamiento:** C2 Ventures  
**Contacto de privacidad y derechos:** privacidad@elecciones2026.es  
**Finalidad del sitio:** Servicio cívico informativo e independiente para la consulta y comparación neutral de los programas electorales oficiales para las Elecciones Generales de España del 29 de noviembre de 2026.

1. **Sin recogida de datos personales:**  
   Este sitio web no requiere registro ni creación de cuenta. No recopilamos su nombre, correo electrónico, dirección IP identificable ni sus preferencias políticas o intención de voto.

2. **Sin cookies ni rastreadores:**  
   No utilizamos cookies de seguimiento, herramientas de analítica de terceros, píxeles publicitarios ni tecnologías de huella digital («fingerprinting»). Al no instalar cookies no necesarias para el funcionamiento técnico básico, no mostramos banners de consentimiento de cookies.

3. **Comparador en su navegador:**  
   Las selecciones de temas y partidos que realice en el comparador se ejecutan y mantienen exclusivamente en la memoria de su navegador. Si utiliza la opción de compartir enlace, los parámetros de selección se reflejan en la dirección web para que el destinatario pueda visualizar la misma comparativa, sin almacenarse en ninguna base de datos del proyecto.

4. **Registros técnicos de red:**  
   Para garantizar la seguridad de la infraestructura, prevenir ataques de denegación de servicio (DDoS) y asegurar la disponibilidad del servicio (base legal: interés legítimo, art. 6.1.f RGPD), los servidores de red gestionados a través de Cloudflare y el centro de datos alojado en la Unión Europea registran temporalmente datos técnicos de conexión (dirección IP técnica, fecha, hora y recurso solicitado). Estos registros se eliminan o anonimizan de forma automática en un plazo máximo de 14 días y nunca se utilizan para elaborar perfiles.

5. **Ejercicio de derechos:**  
   De acuerdo con el Reglamento General de Protección de Datos (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD), puede solicitar información sobre el tratamiento técnico o ejercer sus derechos de acceso, rectificación, supresión y limitación escribiendo a privacidad@elecciones2026.es. Asimismo, tiene derecho a presentar una reclamación ante la Agencia Española de Protección de Datos (AEPD, www.aepd.es) si considera vulnerados sus derechos.
```

---

## 6. Decision 4: Release Service Levels, SLOs, SLIs, and Error Budgets

To satisfy the acceptance criteria for roadmap package `E0.3` and provide verifiable benchmarks for tasks 4.3, 4.6, and 4.7, the project establishes the following binding targets:

### 6.1 Service Level Objectives (SLOs) Table

| Service Level Indicator (SLI) | Steady-State Target | Peak / Burst Scenario Target (10,000 Visitors) | Measurement Method | Alert Threshold |
|---|---|---|---|---|
| **Monthly Availability** | **>= 99.5%** uptime (~3.6h error budget/mo) | **>= 99.9%** uptime during election week (2026-11-23 to 2026-11-30) | Synthetic HTTPS polling every 60s from external European probes | Downtime > 3 consecutive checks (3 min) |
| **Edge Latency (p95)** | **< 150 ms** | **< 200 ms** | Cloudflare Analytics / synthetic client probes across Spain | p95 > 250 ms over 5 min |
| **Origin Latency (p95)** | **< 250 ms** | **< 400 ms** (during cold cache burst) | Origin HTTP access logs and container metrics | p95 > 500 ms over 5 min |
| **Mobile Delivery (p95)** | **< 500 ms** | **< 750 ms** | Synthetic mobile profile (fast 4G, 360–430 CSS px) | p95 > 1,000 ms |
| **Static Asset Edge Hit Ratio** | **>= 99.0%** | **>= 98.0%** | Cloudflare cache analytics for fingerprinted `.css`, `.js`, `.svg` | Hit ratio < 97.0% |
| **HTML Document Edge Hit Ratio** | **>= 90.0%** | **>= 85.0%** | Cloudflare cache analytics for HTML paths (`/`, `/temas/*`, `/fuentes/`) | Hit ratio < 80.0% |
| **Aggregate Edge Hit Ratio** | **>= 95.0%** | **>= 85.0%** (cold-cache recovery phase) | Total edge requests cached vs origin requests | Hit ratio < 85.0% steady-state |
| **HTTP 5xx Error Rate** | **< 0.05%** | **< 0.50%** | HTTP status codes 500, 502, 503, 504 over total requests | 5xx rate > 0.1% over 5 min |
| **HTTP 4xx Error Rate** | **< 0.50%** (excl. crawlers) | **< 1.00%** | Total 4xx responses over total valid page requests | 4xx rate > 2.0% |
| **Origin CPU Utilization** | **< 30%** average | **< 70%** burst peak | Active IONOS host / Docker stats | CPU > 80% over 5 min |
| **Origin Memory Usage** | **< 150 MB** | **< 300 MB** | Static serving container memory consumption | RAM > 500 MB |

### 6.2 Cache Header Policy
- **Immutable Static Assets** (`/static/*`, fingerprinted CSS, JS, images, icons):
  - Header: `Cache-Control: public, max-age=31536000, immutable`
  - Edge Cache TTL: 365 days.
- **Stable-name CSS and JS** (current generated styles/scripts, including `/tokens/`):
  - Header: `Cache-Control: public, no-cache` until filenames are content-addressed.
  - Revalidate on reuse; immutable caching is reserved for URLs that change with content.
- **Mutable HTML Pages** (`/`, `/temas/*`, `/metodo/`, `/fuentes/`, `/correcciones/`):
  - Header: `Cache-Control: public, max-age=300, stale-while-revalidate=86400`
  - Edge Cache TTL: 300 seconds (5 minutes). Allows rapid propagation of corrections while absorbing traffic surges.
- **Security & Crawler Files** (`robots.txt`, `sitemap.xml`, `security.txt`):
  - Header: `Cache-Control: public, max-age=3600, stale-while-revalidate=86400`

### 6.3 Recovery and Rollback Targets (RTO / RPO)
- **Recovery Time Objective (RTO):** **< 5 minutes** to restore the previous immutable Docker artifact or redeploy the preceding verified static build.
- **Recovery Point Objective (RPO):** **0 data loss**. All site content and configurations are deterministically compiled from Git-versioned records; no runtime transactional database exists.

---

## 7. Decision 5: Capacity Target and 10,000-Concurrent-Visitor Modeling

Task 4.7 requires running a representative 10,000-concurrent-visitor scenario with cold-cache and burst phases. This model translates visitor concurrency into planned infrastructure demands.
The active IONOS host has 1 vCPU / 1 GB RAM. The older 2-vCPU / 8-GB sizing
below is a historical planning baseline; it is not measured capacity. Hetzner
is a future migration option, not an active replacement. Retain the <= 200 req/s
origin acceptance target until owners resolve the cold-cache estimate conflict.
Actual-host tests and owner review remain required:

### 7.1 Concurrency and Traffic Modeling
- **Visitor Population:** 10,000 active concurrent readers exploring comparisons and reviewing sources during high campaign interest.
- **User Behavior Model:** An average active reader performs 1 page or topic view every 5 to 10 seconds.
- **Gross Request Rate at Edge:** 1,000 to 2,000 HTTP requests per second (req/s) delivered to Cloudflare.
- **Origin Demand Under Steady-State Cache (Hit Ratio >= 95%):**
  - Origin receives **50 to 100 requests per second**.
  - Historical unverified estimate: a Hetzner 2-vCPU / 8-GB VM could handle 1,000+ req/s with under 15% CPU load while serving static files from memory.
- **Origin Demand Under Cold-Cache / Burst Phase (Hit Ratio 85%):**
  - Origin receives **150 to 300 requests per second**.
  - Historical unverified estimate: the 2-vCPU / 8-GB origin could absorb 300 req/s with CPU under 50% and memory under 200 MB. These values are not acceptance evidence.
- **Cold-Cache Protection Safeguards:**
  - Cloudflare Tiered Caching enabled to concentrate origin revalidations.
  - Origin connection limits and keep-alive connection reuse configured between Cloudflare and the origin.

---

## 8. Decision 6: Cost Ceiling and Financial Governance

### 8.1 Monthly Budget and Cost Breakdown

This retained cost model uses the earlier Hetzner plan. It is not the active
IONOS bill or a verified traffic allowance. Actual IONOS charges and limits need
owner evidence. The monetary targets and ceiling below are unchanged.

| Component | Provider / Tier | Expected Monthly Cost | Hard Monthly Ceiling |
|---|---|---|---|
| **Origin Compute & Host** | Hetzner Cloud (CX22 / CPX21: 2 vCPU, 4–8 GB RAM, 40–80 GB NVMe, 20 TB traffic) | €5.00 – €10.00 | €20.00 |
| **Edge, CDN, DNS, and DDoS** | Cloudflare Free Tier | €0.00 | €20.00 (fallback to Pro if advanced WAF needed) |
| **Domain Registration** | Primary (`.es`) + 2 Defensive (`.es`, `.org`) (amortized) | €2.50 | €5.00 |
| **Off-Host Backup & Storage** | Hetzner Storage Box / S3-compatible snapshot (100 GB) | €3.50 | €5.00 |
| **Total Project Budget** | — | **€11.00 – €16.00 / month** | **€50.00 / month** |

### 8.2 Financial Governance Rules
1. **Hard Ceiling:** Total monthly operational spend MUST NOT exceed **€50.00 / month** under any circumstance.
2. **Alert Thresholds:**
   - Warning Alert: Triggered when projected monthly cost reaches **€25.00** (50% of ceiling).
   - Critical Alert: Triggered when projected monthly cost reaches **€40.00** (80% of ceiling).
3. **No Uncapped Metered Billing:** The project strictly forbids unmetered serverless functions, per-invocation APIs, or uncapped egress bandwidth providers that could result in unexpected cost spikes under traffic surges or denial-of-wallet attacks.
4. **Traffic Allocation:** The historical Hetzner plan assumed 20 TB of outbound traffic per month and projected below 50 GB of origin egress with >= 95% Cloudflare edge offload. This is not verified IONOS allowance or billing evidence.

---

## 9. Decision 7: Role and Ownership Matrix

To ensure clear operational accountability and satisfy acceptance criteria, the following owners are assigned:

| Role | Named Owner / Identifier | Responsibilities |
|---|---|---|
| **Infrastructure and Operational Owner** | Cesc (`cesc`) / Infrastructure Lead | IONOS server configuration, Cloudflare DNS/edge routing, TLS certificate management, uptime monitoring, latency tracking, cost ceiling enforcement, and capacity response. |
| **Editorial and Methodology Owner** | Cesc and Project Partner | Candidate inclusion rules, party naming, source acquisition, editorial statement review, correction policy, and human release gates G0 and G2. |
| **Security and Release Gatekeeper** | Release Engineering Lead | CI/CD pipeline integrity, container digest pinning, vulnerability scanning, secret prohibition, reproducible builds, and rollback execution. |
| **Privacy and Data Protection Representative** | C2 Ventures Legal / Privacy Contact (`privacidad@elecciones2026.es`) | Compliance with GDPR and LOPDGDD, maintenance of the public privacy notice, handling user rights inquiries, and liaison with AEPD. |

---

## 10. Consequences and Compliance Verification

### 10.1 Positive Consequences
- Engineering and operations have unambiguous, quantified release targets for load testing (tasks 4.3, 4.6, 4.7).
- Legal and privacy compliance are established before any public exposure or data processing occurs.
- Financial risk is strictly bounded to €50.00 / month without unbudgeted runaway costs.
- Future localization (Catalan, English) is decoupled and protected by explicit review gates.

### 10.2 Negative Consequences and Mitigations
- *Constraint:* Using Cloudflare Free restricts advanced customized WAF rate-limiting rules.  
  *Mitigation:* The static architecture has no dynamic API or database to exploit; static assets are inherently resilient, and budget allows upgrading to Cloudflare Pro (€20/mo) within the €50 ceiling if required during election week.
- *Constraint:* Human review requirement limits the velocity of candidate additions and translations.  
  *Mitigation:* Essential for neutrality and accuracy; automation drafts records while humans retain final approval authority.

### 10.3 Verification and Acceptance Evidence
- **Automated Validation:** Test suite in `tests/test_service_levels.py` and `tests/test_decision_record.py` verifies all targets, thresholds, owners, and notice elements programmatically.
- **OpenSpec Task Alignment:** Recorded in `openspec/changes/mvp-programme-comparison/tasks.md` under tasks 4.3, 4.6, and 4.7.
- **Human Gate Signoff:** Recorded upon final approval of Milestone G0 by Cesc and the project partner.

---

# Decision Record: Source Rights, Quotation Limits, Reviewer Roles, and Internal Correction Process

- **Record ID:** ADR-0002 (Roadmap Package `E0.2`)
- **Date:** 2026-10-09
- **Status:** Proposed — Awaiting Human Gate G0 Approval (Cesc and Project Partner)
- **Applicable OpenSpec Change:** `mvp-programme-comparison`
- **Related Issues:** Issue #4 ([E0.2])
- **Related OpenSpec Tasks:** 1.1, 1.2, 2.2
- **Dependencies:** Blocked by Issue #1 (`E0.1`) — Predecessor work merged in commit `6542704`

---

## 1. Context and Problem Statement

The platform extracts, synthesizes, and compares electoral proposals across competing political parties for the 29 November 2026 Spanish general election (`es-gen-2026`).

Because political parties retain intellectual property in their manifestos and public campaigns, reproducing and comparing political statements creates legal, editorial, and reputational challenges:
1. **Source Rights & Copyright:** Unregulated reproduction of full documents or extensive excerpts risks copyright infringement under the Spanish Intellectual Property Law (*Real Decreto Legislativo 1/1996* - TRLPI).
2. **Quotation Scope & Context:** Publishing out-of-context, unverified, or excessive quotations undermines neutrality and risks misleading voters.
3. **Reviewer Bias & Segregation:** Individual editors could introduce personal partisan bias or inadvertent errors if proposals are published without strict separation of duties and dual review.
4. **Error Correction & Invalidation:** Errors in source text or classification must be corrected swiftly without breaking historical audit trails or leaving invalid comparisons active on the public site.

This decision record defines the binding editorial and operational policies governing source rights, quotation limits, reviewer roles, and error correction.

---

## 2. Decision Summary

| Area | Decision | Reference / Target |
|---|---|---|
| **Governing Copyright Law** | Spanish Intellectual Property Law (TRLPI), Art. 32 (*derecho de cita*) | Civic analysis and critical comparison; Art. 13 for official acts |
| **PDF Hosting Policy** | Full PDF hosting or redistribution is strictly forbidden | Direct outbound HTTPS links to official party URLs only |
| **Source Rights Taxonomy** | 5 explicit states: `link_and_short_quote`, `public_domain`, `link_only`, `permission_denied`, `not_reviewed` | Stored in `content/sources/register.json`; only first two allow quotes |
| **Quotation Word Limit** | Maximum **40 words** per verbatim extract | Strict ceiling; quotes must be enclosed in quotation marks |
| **Quotation Char Limit** | Maximum **300 characters** per verbatim extract | Accommodates short sentences with precise statutory figures |
| **Mandatory Locators** | Non-empty `page`, `section`, or both required for every quotation | Vague citations rejected at build time |
| **Unsupported Quote Rule** | **No unsupported quote can pass review** | Build fails if source is unverified, missing, or lacks dual review |
| **Reviewer Segregation** | Four-Eyes Principle: 2 distinct human reviewers required per statement | Drafter cannot act as Reviewer 2 (`drafter != reviewed_by_2`) |
| **Editorial Roles** | `drafter`, `editorial_reviewer_1` (Fact/Citation), `editorial_reviewer_2` (Neutrality), `lead_editor` | Segregated checklists and conflict-of-interest declarations |
| **Correction Severities** | Critical (Sev-1: <= 4h/12h SLA), Major (Sev-2: <= 12h/24h SLA), Minor (Sev-3: <= 24h/48h SLA) | Standardized triage and resolution deadlines |
| **Invalidation Protocol** | Automatic invalidation of dependent comparison relationships | Invalidation propagated at build time; public errata log updated |
| **Editorial Signoff** | Cesc and Project Partner under Human Gate G0 / G2 | Agents cannot approve source rights or publish claims unilaterally |

---

## 3. Decision 1: Source Rights and Copyright Framework

### 3.1 Statutory Basis (TRLPI Article 32)
- Political programmes are protected literary and political works.
- Quotations on the platform are permitted exclusively under the statutory right of quotation (*derecho de cita*) set forth in Article 32.1 TRLPI:
  - Works must have already been lawfully disclosed (*obras ya divulgadas*).
  - Excerpts are included strictly for civic analysis, commentary, and critical comparison.
  - Excerpts must be strictly proportionate to the objective of informing voters.
  - The source author and title must be explicitly cited with exact locators.

### 3.2 Outbound Linking vs. Redistribution
- The platform **MUST NOT** store, re-host, or mirror complete third-party party programme PDFs.
- All statements and source references **MUST** provide direct outbound HTTPS links pointing to the party's official publication landing page or official direct PDF link.
- Links to official BOE publications (e.g. Royal Decrees and JEC proclamations) are public domain under Article 13 TRLPI.

### 3.3 Rights Review Regimes
Every document in `content/sources/register.json` must undergo rights review before quotation extraction:
1. `link_and_short_quote`: Permitted for verified electoral programmes. Verbatim quotes allowed within quantitative limits.
2. `public_domain`: Permitted for public-domain works or CC0 releases.
3. `link_only`: Verbatim quotations prohibited. Only neutral editorial summaries permitted.
4. `permission_denied`: The rights holder has explicitly forbidden use. No quotes permitted.
5. `not_reviewed`: Default state for unverified documents. Build rejects any quote extraction.

---

## 4. Decision 2: Verbatim Quotation Limits and Unsupported Quote Prohibition

### 4.1 Quantitative Limits
- **Maximum 40 words** per quotation.
- **Maximum 300 characters** per quotation.
- Quotations exceeding these thresholds must be paraphrased into neutral editorial summaries or shortened to the operative commitment.

### 4.2 Qualitative Boundaries
- Quotations must capture exclusively operative policy mechanisms (numerical goals, tax percentages, budget allocations, dates, statutory thresholds).
- Rhetorical slogans, partisan attacks, campaign mottos, and ideological preambles are strictly prohibited from quotation.
- Quotations must be wrapped in quotation marks (`«...»` or `"..."`).

### 4.3 Unsupported Quote Prohibition
- **No unsupported quote can pass review.**
- Automated validation (`elecciones2026.editorial` and CI) enforces this rule:
  - If a quote lacks a valid `source_id` in `content/sources/register.json`, validation fails.
  - If the referenced source has status other than `verified`, validation fails.
  - If the source rights status is not `link_and_short_quote` or `public_domain`, validation fails.
  - If page and section locators are both absent, validation fails.
  - If the statement lacks a completed `ReviewRecord` with two distinct reviewers, validation fails.

---

## 5. Decision 3: Reviewer Roles, Segregation of Duties, and Dual Review

### 5.1 Role Definitions
1. **Drafter / Extractor (`drafter`):** Extracts proposals from verified sources, drafts the neutral Spanish summary (`summary_es`), extracts operative quotes (<= 40 words), and records page/section locators.
2. **Editorial Reviewer 1 (`editorial_reviewer_1` - Factual & Citation Auditor):** Verifies quote accuracy against the source document PDF, confirms page/section locators, enforces quotation limits, and confirms source rights status.
3. **Editorial Reviewer 2 (`editorial_reviewer_2` - Neutrality & Balance Auditor):** Verifies objective tone without evaluative adjectives, validates topic/subtopic taxonomy alignment, confirms that missing proposals are marked `not_found` rather than opposition, and ensures qualification accuracy.
4. **Lead Editor (`lead_editor`):** Resolves reviewer disputes, approves correction records, and validates human gates G0 and G2.

### 5.2 Four-Eyes Principle and Segregation Rules
- **Four-Eyes Requirement:** Every published statement must be audited and approved by at least two distinct human reviewers (`reviewed_by_1 != reviewed_by_2`).
- **Segregation of Drafter:** A drafter cannot act as Reviewer 2 (`drafter != reviewed_by_2`).
- **Conflict of Interest:** Reviewers must disclose political party affiliations. Active party members or campaign participants are disqualified from reviewing materials for that party and its direct electoral opponents.

---

## 6. Decision 4: Internal Correction Workflow, Severity SLAs, and Invalidation Protocol

### 6.1 Severity Taxonomy and SLAs
- **Critical (Sev-1):** Inverted party positions, fabricated or misattributed quotes, or copyright violations.
  - Triage SLA: **<= 4 hours** (immediate removal/quarantine from public site).
  - Resolution SLA: **<= 12 hours**.
- **Major (Sev-2):** Substantive errors in proposal mechanisms, incorrect page locators, or primary topic misclassification.
  - Triage SLA: **<= 12 hours**.
  - Resolution SLA: **<= 24 hours**.
- **Minor (Sev-3):** Typographical errors in summary, grammatical corrections, or subtopic refinement.
  - Triage SLA: **<= 24 hours**.
  - Resolution SLA: **<= 48 hours**.

### 6.2 Immutable Correction Records
- Published statement IDs are immutable.
- Substantive edits create an auditable `CorrectionRecord` containing:
  `id`, `statement_id`, `election_id`, `date`, `correction_type`, `severity`, `prior_value`, `new_value`, `reason`, `reviewed_by`, and `approved_by`.

### 6.3 Invalidation Protocol for Dependent Comparisons
- Comparisons (`ComparisonRelationship`) link statements together.
- When any referenced statement is corrected or invalidated, all dependent comparisons are automatically marked `status: "invalidated"`.
- The build excludes invalidated comparisons from public presentation until two editorial reviewers re-audit the comparative relationship and sign off on a new version.

### 6.4 Public Errata Log
- All corrections are published chronologically at `/correcciones/` and summarized on the methodology page, detailing date, party, topic, prior text, and rationale.

---

## 7. Decision 5: Signoff Matrix and Human Release Gates

| Milestone / Gate | Description | Required Signoff |
|---|---|---|
| **Gate G0** | Project Contract & Editorial Policies (E0.1–E0.4) | Cesc and Project Partner |
| **Gate G1** | MVP Specification & Data Model (E1.1–E1.3) | Cesc and Engineering Lead |
| **Gate G2** | Two-Programme Pilot Approval (E1.4) | Cesc and Editorial Reviewers |
| **Gate G3** | Staging / MVP Preview Security & Accessibility | Release Engineering Lead |
| **Gate G4** | Public MVP Launch | Cesc, Project Partner, Infrastructure Lead |

---

## 8. Consequences and Compliance Verification

### 8.1 Positive Consequences
- Strict compliance with Spanish Intellectual Property Law (TRLPI Art. 32) protects the project from copyright claims.
- The 40-word / 300-character ceiling prevents excessive verbatim quoting while preserving exact documentary citations.
- The Four-Eyes principle guarantees neutrality, preventing single-editor bias.
- Automatic relationship invalidation guarantees that stale or corrected positions never persist in active comparisons.

### 8.2 Negative Consequences and Mitigations
- *Constraint:* Dual human review slows extraction velocity.  
  *Mitigation:* Essential for non-partisan credibility; assistive tooling drafts proposals while humans retain approval.
- *Constraint:* Prohibition of PDF hosting means users must rely on external party websites that may change or experience downtime.  
  *Mitigation:* Retain verified SHA-256 hashes and archival retrieval timestamps in the source register; display last-verified dates.

### 8.3 Verification and Acceptance Evidence
- **Automated Validation:** Test suite in `tests/test_editorial_policy.py` validates quotation limits, unsupported quote rejection, reviewer role segregation, correction records, and relationship invalidations.
- **OpenSpec Task Alignment:** Recorded in `openspec/changes/mvp-programme-comparison/tasks.md` under tasks 1.1, 1.2, and 2.2.
- **Human Gate Signoff:** Formally submitted for human gate G0 approval by Cesc and the project partner.
