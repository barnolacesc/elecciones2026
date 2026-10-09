# Security and privacy plan

## Security goals

1. Protect the integrity of political information. Publish no unsupported or unreviewed claim. Record corrections.
2. Keep the dependency and CI chain small. Pin supported release dependencies and actions. Scan them before release. Give untrusted pull requests read-only access and no deployment secret.
3. Process source files offline with size, time, CPU, memory, and URL limits. Escape source text before HTML output. Do not let a source document command the build.
4. Serve static assets from a non-privileged, read-only Docker container. Put Cloudflare in front of a limited Hetzner origin. Use TLS, safe headers, host updates, monitoring, and rollback.
5. Collect no account data, cookie profile, quiz answer, or behavioral analytics in the MVP. Review privacy effects before later changes.

## Threat checks

| Threat | Control and release evidence |
|---|---|
| False or changed programme | Official source, URL, hash, version, independent review |
| Partisan or misleading summary | Editorial method, qualifications, equal presentation, correction review |
| XSS or injection | Typed records, output escaping, restrictive CSP, hostile-input tests |
| CI or dependency compromise | Least privilege, pinned versions/actions, scan reports, protected release |
| Malicious PDF or URL | Isolated extraction, resource limits, SSRF guard, failure tests |
| Traffic flood | Edge cache, targeted WAF/rate rules within plan limits, burst/load tests |
| Direct origin attack | Restrict origin access where feasible, firewall, minimal exposed ports |
| Data loss | Versioned records, off-host backup, restore and rollback test |

## Publication gates

Verify current advisories at implementation and release time. Do not promise zero vulnerabilities. Record residual risk and remediation dates. Before making the repo public, inspect its full history for secrets, licenses, and source PDFs. Pin the production container base by digest and scan it. The current preview Dockerfile is not an approved production image.

The public `SECURITY.md` disclosure policy and contact are not yet set. This planning file is not that policy. Do not place search keywords, crawler commands, or AI prompts in a privacy notice or security policy.
