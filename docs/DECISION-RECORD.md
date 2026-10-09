# Decision Record: Language, Domain, Privacy Notice, Service Levels, and Cost Ceiling

- **Record ID:** ADR-0001 (Roadmap Package `E0.3`)
- **Date:** 2026-10-09
- **Status:** Proposed — Awaiting Human Gate G0 Approval (Cesc and Project Partner)
- **Applicable OpenSpec Change:** `mvp-programme-comparison`
- **Related Issues:** Issue #2 ([E0.3])
- **Related OpenSpec Tasks:** 4.3, 4.6, 4.7
- **Dependencies:** None

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
| **Primary Domain** | `elecciones2026.es` | Registered via accredited registrar; DNSSEC enabled |
| **Defensive Domains** | `elecciones2026.org`, `programaselectorales.es` | Permanent 301 redirects to canonical domain |
| **Preview / Staging Domain** | `preview.elecciones2026.es` | Gated by Cloudflare Access or HTTP authentication; `noindex` |
| **Privacy Architecture** | Zero personal data collection; zero tracking cookies; no cookie banner required | Complies with GDPR Art. 5, 6, 9 and LSSI-CE Art. 22.2 |
| **Technical Log Retention** | Ephemeral edge/origin logs retained <= 14 days solely for network security and DoS defense | IP anonymization; no behavioral profiling |
| **Edge Cache-Hit Target** | >= 95% steady-state; >= 85% cold-cache phase; >= 99% for fingerprinted assets | Cloudflare CDN proxy in front of Hetzner origin |
| **p95 Latency Target** | < 150 ms edge cache hit; < 250 ms origin response; < 500 ms mobile page delivery | Evaluated on 360–430 CSS px mobile baseline |
| **Error Rate Budget** | HTTP 5xx < 0.05% steady-state; < 0.5% during 10,000-visitor burst scenario | 99.5% normal monthly availability; 99.9% election week |
| **Concurrency Scenario** | 10,000 concurrent active readers (~1,000–2,000 req/s edge; <= 200 req/s origin) | Verified on Hetzner 2-vCPU / 8-GB RAM VM |
| **Cost Ceiling** | €50.00 / month hard maximum; ~€9.00–€15.00 / month expected baseline | Alerts at €25.00 (50%) and €40.00 (80%); no uncapped billing |
| **Operational Owner** | Cesc (`cesc`) / Infrastructure Lead | Responsible for Hetzner, Cloudflare, TLS, DNS, monitoring |
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
- **Primary Canonical Domain:** `elecciones2026.es`
- **Defensive / Secondary Domains:** `elecciones2026.org` and `programaselectorales.es`. These domains prevent phishing and brand confusion.
- **Staging / Preview Domain:** `preview.elecciones2026.es`.

### 4.2 Canonical Routing and Redirects
- Canonical base URL: `https://elecciones2026.es/`.
- All alternate endpoints MUST return an immediate HTTP 301 permanent redirect to the canonical HTTPS apex URL:
  - `http://elecciones2026.es/*` → `https://elecciones2026.es/*`
  - `http://www.elecciones2026.es/*` → `https://elecciones2026.es/*`
  - `https://www.elecciones2026.es/*` → `https://elecciones2026.es/*`
  - All defensive domain requests → `https://elecciones2026.es/*`
- HTTP Strict Transport Security (HSTS) MUST be enabled once DNS and TLS stabilization is verified: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.

### 4.3 Staging and Preview Environment Protection
- `preview.elecciones2026.es` MUST require authentication (via Cloudflare Access or HTTP Basic Auth) to prevent public disclosure of unreviewed draft data.
- The preview environment MUST emit HTTP header `X-Robots-Tag: noindex, nofollow, noarchive` and a restrictive `robots.txt` disallowing all crawling.

### 4.4 DNS and Proxy Configuration
- DNS management and edge caching MUST be handled via Cloudflare.
- DNSSEC MUST be enabled at the domain registrar and configured within Cloudflare.
- The origin IP address on Hetzner MUST remain masked behind the Cloudflare proxy. Direct access to port 80/443 on the Hetzner origin from non-Cloudflare IP ranges SHOULD be blocked via firewall rules.

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
- Cloudflare edge and Hetzner origin process standard HTTP connection metadata (client IP, request method, URI path, HTTP status, User-Agent, and timestamp) strictly under Article 6.1(f) GDPR (legitimate interest for network security, abuse defense, and availability monitoring).
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
| **Origin CPU Utilization** | **< 30%** average | **< 70%** burst peak | Hetzner VM host / Docker stats | CPU > 80% over 5 min |
| **Origin Memory Usage** | **< 150 MB** | **< 300 MB** | Static serving container memory consumption | RAM > 500 MB |

### 6.2 Cache Header Policy
- **Immutable Static Assets** (`/static/*`, fingerprinted CSS, JS, images, icons):
  - Header: `Cache-Control: public, max-age=31536000, immutable`
  - Edge Cache TTL: 365 days.
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

Task 4.7 requires running a representative 10,000-concurrent-visitor scenario with cold-cache and burst phases. This model translates visitor concurrency into concrete infrastructure demands:

### 7.1 Concurrency and Traffic Modeling
- **Visitor Population:** 10,000 active concurrent readers exploring comparisons and reviewing sources during high campaign interest.
- **User Behavior Model:** An average active reader performs 1 page or topic view every 5 to 10 seconds.
- **Gross Request Rate at Edge:** 1,000 to 2,000 HTTP requests per second (req/s) delivered to Cloudflare.
- **Origin Demand Under Steady-State Cache (Hit Ratio >= 95%):**
  - Origin receives **50 to 100 requests per second**.
  - Hetzner 2-vCPU / 8-GB VM serving static files from memory via a non-privileged web container (e.g., Caddy or Nginx) handles 1,000+ req/s with under 15% CPU load.
- **Origin Demand Under Cold-Cache / Burst Phase (Hit Ratio 85%):**
  - Origin receives **150 to 300 requests per second**.
  - The 2-vCPU / 8-GB VM origin can comfortably absorb 300 req/s with CPU usage under 50% and memory consumption under 200 MB.
- **Cold-Cache Protection Safeguards:**
  - Cloudflare Tiered Caching enabled to concentrate origin revalidations.
  - Origin connection limits and keep-alive connection reuse configured between Cloudflare and the origin.

---

## 8. Decision 6: Cost Ceiling and Financial Governance

### 8.1 Monthly Budget and Cost Breakdown

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
4. **Traffic Allocation:** Hetzner provides 20 TB of free outbound traffic per month. Combined with >= 95% Cloudflare edge offload, monthly origin egress is projected below 50 GB, well within the free allowance.

---

## 9. Decision 7: Role and Ownership Matrix

To ensure clear operational accountability and satisfy acceptance criteria, the following owners are assigned:

| Role | Named Owner / Identifier | Responsibilities |
|---|---|---|
| **Infrastructure and Operational Owner** | Cesc (`cesc`) / Infrastructure Lead | Hetzner server configuration, Cloudflare DNS/edge routing, TLS certificate management, uptime monitoring, latency tracking, cost ceiling enforcement, and capacity response. |
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
