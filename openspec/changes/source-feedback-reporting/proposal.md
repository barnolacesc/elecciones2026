# Proposal: Source feedback reporting

## Why

Readers may find a wrong citation, missing source, or inaccurate summary. The project needs a structured way to record and review these reports. The static MVP has no server API or database, so a working submission form is not part of its launch scope.

## What Changes

- Add a report action tied to a statement or source ID only after a secure write service exists.
- Accept a short report type and free-text description. Do not require an email address, account, or attachment.
- Store the report and its target ID in a database with a receipt ID and review state. Do not send email from the submission path.
- Use a small FastAPI write API if the team approves the added operational cost. Validate type and length, escape display output, use parameterized database access, restrict origin/CORS, and rate-limit abusive submissions.
- Define data retention, backup, reviewer access, abuse handling, and a privacy notice before launch. Avoid storing request IPs or user-agent strings unless a documented abuse-control need requires them.
- Keep editorial correction decisions separate from report intake. A report must not change published political content automatically.

## Capabilities

### New Capabilities

- `source-report-intake`: Accept and validate a report for a published statement or document.
- `source-report-review`: Record review status and link any resulting correction to the public correction log.

### Modified Capabilities

- `static-publication`: Show a report entry point only when the service is active. Until then, a plain “Feature coming later” note may appear on the method page; no dead form or deceptive per-statement control.

## Impact

This is an **optional post-MVP track**. It does not block the quiz or seat simulator. It introduces a write API, persistent database, public text input, and new security/privacy operations. The future specs and design must compare the operational cost with a no-backend alternative before implementation. SQL injection prevention alone is insufficient: spam, denial of service, stored XSS, PII in free text, retention, and moderation also need controls.
