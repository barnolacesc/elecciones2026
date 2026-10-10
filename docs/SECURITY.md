# Security and privacy plan

## Security goals

1. Protect the integrity of political information. Publish no unsupported or unreviewed claim. Record corrections.
2. Keep the dependency and CI chain small. Pin supported release dependencies and actions. Scan them before release. Give untrusted pull requests read-only access and no deployment secret.
3. Process source files offline with size, time, CPU, memory, and URL limits. Escape source text before HTML output. Do not let a source document command the build.
4. Serve static assets from a non-privileged, read-only Docker container. Put Cloudflare in front of a limited Hetzner origin. Use TLS, safe headers, host updates, monitoring, and rollback.
5. Collect no account data, cookie profile, quiz answer, or behavioral analytics in the MVP. Review privacy effects before later changes.
6. Enforce strict data minimization under GDPR (Regulation 2016/679) and Spanish LOPDGDD (Ley Orgánica 3/2018).

## Privacy architecture and public notice

The public MVP operates on a zero-personal-data, static-serving model:
- **No User Accounts or Telemetry:** No user registration, profiles, or tracking exist. No external analytics, tracking pixels, or third-party font/CDN requests are permitted.
- **No Cookie Banner Required:** Because no non-essential cookies, trackers, or local storage identifiers are used, no cookie consent banner is legally required under Article 22.2 of the Spanish LSSI-CE and AEPD guidelines.
- **In-Memory Comparison:** Topic and party selections exist solely in browser DOM memory. Shareable links encode selections in the URL query string solely to allow recipients to reproduce the view; selections are never stored on an origin database.
- **Ephemeral Technical Logs:** Cloudflare edge and Hetzner origin record standard HTTP connection metadata solely for infrastructure defense, DoS prevention, and operational monitoring (GDPR Art. 6.1(f) legitimate interest). Technical logs are automatically purged within a maximum retention window of 14 days, with IP addresses anonymized.
- **Future Feature Isolation:** The Phase 2 Quiz (Epic E4) evaluates answers strictly client-side in browser memory to protect Article 9 GDPR special category data (political opinions). Optional discrepancy reporting (Epic E8) requires a dedicated Data Protection Impact Assessment (DPIA) before any implementation.
- **Official Privacy Notice:** The binding Spanish public privacy notice text is documented in `docs/DECISION-RECORD.md` Section 5.5.

## Threat checks

| Threat | Control and release evidence |
|---|---|
| False or changed programme | Official source, URL, hash, version, independent review |
| Partisan or misleading summary | Editorial method, qualifications, equal presentation, correction review |
| XSS or injection | Typed records, output escaping, restrictive CSP, hostile-input tests |
| CI or dependency compromise | Least privilege, pinned versions/actions, scan reports, protected release |
| Malicious PDF or URL | Isolated extraction, resource limits, SSRF guard, failure tests |
| Traffic flood / denial-of-wallet | Edge cache (>=95% steady), targeted rate rules, burst tests, €50/mo hard cost ceiling |
| Direct origin attack | Restrict origin access to Cloudflare IPs, firewall, minimal exposed ports |
| Data loss / defacement | Versioned Git records, RPO=0, RTO<5 min rollback to previous Docker image |

## Security and privacy contacts

- **Security reports:** `seguridad@elecciones2026.es` (provisional placeholder email pending domain purchase; report via repository maintainers in interim)
- **Privacy inquiries and rights:** `privacidad@elecciones2026.es` (Data Controller: C2 Ventures; provisional placeholder pending domain purchase)
- **Vulnerability disclosure policy:** Coordinate disclosure with 48-hour initial response. Good-faith security research testing against staging (`preview.elecciones2026.es` placeholder or authenticated preview environments) without disrupting service is welcomed under standard safe harbor principles.

## Publication gates

Verify current advisories at implementation and release time. Do not promise zero vulnerabilities. Record residual risk and remediation dates. Before making the repo public, inspect its full history for secrets, licenses, and source PDFs. Pin the production container base by digest and scan it. The current preview Dockerfile is not an approved production image.

Owners for security and operational controls:
- **Infrastructure and Operational Owner:** Cesc (`cesc`) / Infrastructure Lead.
- **Security and Release Gatekeeper:** Release Engineering Lead.
- **Privacy Representative:** C2 Ventures Legal / Privacy Contact.
- Full details, SLO targets, and error budgets are codified in `docs/DECISION-RECORD.md`.

## E3.3 operations preparation

Reviewable origin configuration, immutable release switching, monitoring setup,
and live verification requirements are in [the operations runbook](../ops/README.md).
No infrastructure was provisioned or public content deployed by this package.
OpenSpec tasks 4.4 and 4.6 remain open until their live release evidence is reviewed.
