"""Compatibility entry point for the offline E10.1 source audit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from elecciones2026.budget_source_audit import (  # noqa: E402,F401
    MAX_BYTES, NUMBER, SectionReader, SpanReader, check_records,
    main, matrix, number, read_pinned, reconcile,
)

if __name__ == "__main__":
    main()
