# Test suite

This directory contains automated tests for the election comparison platform.

## Test modules

- `test_methodology_examples.py`: Validates the topic taxonomy, candidate inclusion and party naming standard, and programme status lifecycle fixtures (`official`, `partial`, `replaced`, `missing`) (package `E0.1`).
- `test_editorial_policy.py`: Validates editorial policy rules, quotation limits (<= 40 words, <= 300 chars), unsupported quote rejection, reviewer roles and four-eyes segregation, and internal correction workflow with relationship invalidation (package `E0.2`).
- `test_decision_record.py`: Validates policy contracts defined in ADR-0001 (package `E0.3`), including release service level targets (p95 latency, cache-hit ratios, error budgets, availability), domain architecture, privacy notice requirements, cost ceiling, role ownership, and documentation cross-references across `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, and `tasks.md`.
- `test_source_register.py`: Verifies source register integrity, mandatory provenance fields, status enums, SHA-256 hash formatting, replacement history, rights review structure, and Task 1.2 pilot programmes registration (package `E0.4`).

## Running tests

Run using Python standard library `unittest`:
```bash
PYTHONPATH="src" python3 -m unittest discover -s tests -v
```

Or using `pytest`:
```bash
PYTHONPATH="src" pytest -v
```
