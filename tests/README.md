# Test suite

This directory contains automated tests for the election comparison platform.

## Test modules

- `test_methodology_examples.py`: Validates the topic taxonomy, candidate inclusion and party naming standard, and programme status lifecycle fixtures (`official`, `partial`, `replaced`, `missing`) (package `E0.1`).
- `test_editorial_policy.py`: Validates editorial policy rules, quotation limits (<= 40 words, <= 300 chars), unsupported quote rejection, reviewer roles and four-eyes segregation, and internal correction workflow with relationship invalidation (package `E0.2`).
- `test_decision_record.py`: Validates policy contracts defined in ADR-0001 (package `E0.3`), including release service level targets (p95 latency, cache-hit ratios, error budgets, availability), domain architecture, privacy notice requirements, cost ceiling, role ownership, and documentation cross-references across `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, and `tasks.md`.
- `test_source_register.py`: Verifies source register integrity, mandatory provenance fields, status enums, SHA-256 hash formatting, replacement history, rights review structure, and Task 1.2 pilot programmes registration (package `E0.4`).
- `test_schemas.py`: Validates JSON Schemas (Draft 2020-12) for programmes, statements, relationships, coverage, and corrections against positive and negative fixtures (package `E1.1`).
- `test_importer.py`: Validates isolated offline source import boundaries: PDF/URL size ceilings, streamed limits, `%PDF-` magic bytes, polyglot rejection, active content inspection (`/JavaScript`, `/Launch`, `/EmbeddedFiles`, `/SubmitForm`), zero source code execution, SSRF network boundaries, redirect safety, timeouts, and constant-time SHA-256 hash checks (package `E1.2`).
- `test_component_plan.py` & `test_design_tokens.py`: Validates accessible component specifications, CSS variables, and design tokens (package `E2.1`).

## Running tests

Run using Python standard library `unittest`:
```bash
PYTHONPATH="src" python3 -m unittest discover -s tests -v
```

Or using `pytest`:
```bash
PYTHONPATH="src" pytest -v
```

## E2.6 sharing checks

Run JavaScript syntax and behavior checks with Node 22 or later:

```bash
node --check site/app.js
node --check site/sharing.js
node --test tests/share_behavior.cjs
```

The runtime harness executes the shipped scripts with simulated DOM and browser APIs.
It covers allowlisted selection restoration, malformed/duplicate IDs, URL privacy,
2023 election isolation, native sharing, cancellation, clipboard rejection, and
manual copying. `test_sharing.py` checks generated home/topic controls, canonical
links, election labels, and asset inclusion for both election builds. CI runs both
suites; simulated APIs do not establish real-device behavior.

Before completing task 3.8, test an authorized private HTTPS preview on iOS Safari
and Android Chrome. Record device/OS/browser versions, preview commit, and date:

1. Share home and a topic; confirm one Share control, neutral text, and correct URL.
2. Select two distinct parties and a topic, share, and open the copied link in a
   fresh tab. Confirm all three selections and source context restore.
3. Cancel native sharing, then use the visible Copy link control. Deny clipboard
   access and confirm the readonly link can be selected and copied manually.
4. Check keyboard focus, status announcements, 44-px touch targets, and horizontal
   overflow at 360, 390, and 430 CSS px. Check source context with JavaScript off.
5. Append an unknown ID, a repeated selection parameter, a vote-answer parameter,
   and a fragment. Confirm invalid pairs do not restore and outgoing links contain
   only validated comparison IDs and the optional allowlisted election ID.

Stable routes are `/`, `/temas/{topic-id}/`, and
`/?topic={topic-id}&partyA={party-id}&partyB={party-id}`. Private 2023 comparisons
also carry `election=es-gen-2023`; the legacy `election=2023` input normalizes to
that value. URLs use the current preview origin rather than the placeholder public
domain. Open Graph previews and public-domain checks belong to E3.1a.
## Rendered mobile checks (E2.5)

The browser audit is separate from the standard-library unit suite. Install the
development-only browser tooling and run it against a temporary generated site:

```sh
python -m pip install playwright==1.63.0
python -m playwright install chromium
PYTHONPATH=src python -m elecciones2026.mobile_accessibility --output build/mobile-accessibility.json
```

Linux CI uses `python -m playwright install --with-deps chromium`. The report
contains individual automated outcomes, rendered layout observations, three
cold navigation samples at 1.6 Mbps download and 150 ms emulated latency, and
explicit review limits. Timing is observed in the browser; it excludes production
DNS, TLS, caching and origin latency. No production performance budget or TTI is
inferred. Browser emulation and accessible names do not replace participant,
VoiceOver/TalkBack, or physical device testing. Follow the pending review in
OpenSpec task 3.5 before declaring E2.5 complete.
