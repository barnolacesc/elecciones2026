# Test suite

This directory contains automated tests for the election comparison platform.

## Test modules

- `test_methodology_examples.py`: Validates the topic taxonomy, candidate inclusion and party naming standard, and programme status lifecycle fixtures (`official`, `partial`, `replaced`, `missing`).

## Running tests

Run using Python standard library `unittest`:
```bash
PYTHONPATH="src" python3 -m unittest discover -s tests -v
```

Or using `pytest`:
```bash
PYTHONPATH="src" pytest -v
```
