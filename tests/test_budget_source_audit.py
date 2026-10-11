"""Synthetic source-reconciliation tests for E10.1; no real downloads."""
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from html import escape

SPEC = importlib.util.spec_from_file_location(
    "budget_source_audit", Path(__file__).resolve().parents[1] / "tools/budget-audit/audit.py"
)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def sources(mutator=None):
    rows = [
        ["", "PRESUPUESTOS GENERALES DEL ESTADO", ""],
        ["", "Synthetic sector", ""],
        ["", "Capítulos 1 a 8 consolidado", ""],
        ["", "EJERCICIO PRESUPUESTARIO 2023", ""],
        ["", ""], ["", "(Miles de euros)", ""], ["", ""],
        ["Clasif. por programas", "Explicación", "Secc. 01", "Secc. 60", "Total", ""],
        ["11", " Synthetic policy A", "0,01", "", "0,01", ""],
        ["12", " Synthetic policy B", "0,02", "0,00", "0,02", ""],
        ["", "TOTAL", "0,03", "0,00", "0,03", ""], ["", "", ""],
    ]
    if mutator:
        mutator(rows)
    buf = io.StringIO()
    csv.writer(buf, delimiter=";").writerows(rows)
    prefix = [rows[i][1] for i in (0, 1, 2, 5)] + ["2023"]
    flat = prefix + [v.strip() for r in rows[7:11] for v in r[:-1]]
    html = "".join(f"<span>{escape(v)}</span>" for v in flat)
    return buf.getvalue().encode("cp1252"), html.encode("cp1252")


class BudgetSourceAuditTests(unittest.TestCase):
    def test_exact_decimal_reconciliation_retains_blanks(self):
        report = audit.reconcile(*sources())
        self.assertEqual(report["denominator_amount_thousand_eur"], "0.03")
        self.assertEqual(report["blank_cell_count"], 1)
        self.assertEqual(report["explicit_zero_cell_count"], 1)
        self.assertEqual(report["explicit_numeric_cell_count"], 3)
        self.assertFalse(report["publication_approved"])
        self.assertEqual(report["blank_convention"], "unavailable_pending_human_review")

    def test_source_disagreement_is_rejected(self):
        raw_csv, raw_html = sources()
        with self.assertRaisesRegex(ValueError, "matrix differ"):
            audit.reconcile(raw_csv, raw_html.replace(b"0,01", b"0,02", 1))

    def test_bad_grand_total_in_both_sources_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "margin totals"):
            audit.reconcile(*sources(lambda rows: rows[10].__setitem__(-2, "0,04")))

    def test_bad_policy_margin_is_rejected(self):
        def mutate(rows):
            rows[8][2] = "0,02"
        with self.assertRaisesRegex(ValueError, "Policy margin mismatch"):
            audit.reconcile(*sources(mutate))

    def test_bad_section_margin_preserving_grand_sum_is_rejected(self):
        def mutate(rows):
            rows[10][2:4] = ["0,02", "0,01"]
        with self.assertRaisesRegex(ValueError, "Section margin mismatch"):
            audit.reconcile(*sources(mutate))

    def test_duplicate_policy_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate policy"):
            audit.reconcile(*sources(lambda rows: rows[9].__setitem__(0, "11")))

    def test_duplicate_section_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate section"):
            audit.reconcile(*sources(lambda rows: rows[7].__setitem__(3, "Secc. 01")))

    def test_wrong_year_or_units_is_rejected(self):
        for index, text in [(3, "EJERCICIO PRESUPUESTARIO 2026"), (5, "(Millones de euros)")]:
            with self.subTest(index=index), self.assertRaises(ValueError):
                audit.reconcile(*sources(lambda rows: rows[index].__setitem__(1, text)))

    def test_invalid_numbers_are_rejected(self):
        for value in ["-1,00", "nan", "1.23,00", "0.01", "1,0", "=1+2"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit.number(value)

    def test_changed_bytes_and_symlinks_are_rejected(self):
        raw = b"synthetic pinned bytes"
        digest = hashlib.sha256(raw).hexdigest()
        record = {"sha256": digest, "file": "source.csv", "byte_count": len(raw)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / digest
            folder.mkdir()
            source = folder / "source.csv"
            source.write_bytes(raw)
            self.assertEqual(audit.read_pinned(root, record), raw)
            source.write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                audit.read_pinned(root, record)
            source.unlink()
            original = root / "original.csv"
            original.write_bytes(raw)
            source.symlink_to(original)
            with self.assertRaisesRegex(ValueError, "unsafe"):
                audit.read_pinned(root, record)

    def test_offline_report_is_deterministic(self):
        raw_csv, raw_html = sources()
        self.assertEqual(audit.reconcile(raw_csv, raw_html), audit.reconcile(raw_csv, raw_html))


if __name__ == "__main__":
    unittest.main()
