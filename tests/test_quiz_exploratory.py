"""Unit and integration tests for the 2026 exploratory questionnaire (E4.2 / E4.3)."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from elecciones2026.generator import build_site, load_and_validate_site_data, BuildValidationError
from elecciones2026.quiz_exploratory import (
    ExploratoryQuizError,
    validate_exploratory_bank,
    render_exploratory_quiz_content,
)

ROOT = Path(__file__).resolve().parent.parent


class ExploratoryQuizTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank_path = ROOT / "content/elections/es-gen-2026/quiz-bank.json"
        cls.raw_bank = json.loads(cls.bank_path.read_text(encoding="utf-8"))
        cls.ctx = load_and_validate_site_data(
            ROOT,
            election_id="es-gen-2026",
            records_dir=ROOT / "content/elections/es-gen-2026",
        )

    def test_2026_quiz_bank_validates_cleanly(self):
        bundle = validate_exploratory_bank(self.raw_bank, self.ctx)
        self.assertTrue(bundle["available"])
        self.assertEqual(bundle["mode"], "exploratory")
        self.assertEqual(bundle["total_items"], 96)
        self.assertEqual(len(bundle["topics"]), 12)
        for topic in bundle["topics"]:
            self.assertEqual(len(topic["items"]), 8)
            for item in topic["items"]:
                self.assertTrue(item["id"].startswith("quiz-29n-"))
                self.assertTrue(item["source"]["url"].startswith("https://"))
                if item.get("context"):
                    self.assertTrue(bool(item["context"]["text"]))
                    for ref in item["context"]["references"]:
                        self.assertTrue(ref["url"].startswith("https://"))

    def test_rejection_of_malformed_bank(self):
        for key in ("items", "taxonomy_version"):
            bad = deepcopy(self.raw_bank)
            bad[key] = "wrong"
            with self.subTest(missing_key=key), self.assertRaises(ExploratoryQuizError):
                validate_exploratory_bank(bad, self.ctx)

    def test_rejection_of_wrong_item_count_or_topic(self):
        bad = deepcopy(self.raw_bank)
        bad["items"].pop()
        with self.assertRaises(ExploratoryQuizError):
            validate_exploratory_bank(bad, self.ctx)

        bad2 = deepcopy(self.raw_bank)
        bad2["items"][0]["topic_id"] = "non-existent-topic"
        with self.assertRaises(ExploratoryQuizError):
            validate_exploratory_bank(bad2, self.ctx)

    def test_rejection_of_unsafe_url(self):
        bad = deepcopy(self.raw_bank)
        bad["items"][0]["source"]["url"] = "http://insecure.example.com"
        with self.assertRaises(ExploratoryQuizError):
            validate_exploratory_bank(bad, self.ctx)

    def test_build_site_with_exploratory_mode_generates_interactive_cuestionario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "dist"
            res = build_site(
                ROOT,
                out,
                election_id="es-gen-2026",
                records_dir=ROOT / "content/elections/es-gen-2026",
                quiz_mode="exploratory",
            )
            cuestionario_html = (out / "cuestionario/index.html").read_text(encoding="utf-8")
            self.assertIn("Cuestionario de propuestas", cuestionario_html)
            self.assertIn('id="exploratory-form"', cuestionario_html)
            self.assertIn('id="topics"', cuestionario_html)
            self.assertIn('id="results"', cuestionario_html)
            self.assertNotIn("aún no está disponible", cuestionario_html)
            self.assertIn("/cuestionario/", (out / "sitemap.xml").read_text())

            # Fingerprinted assets generated
            data_scripts = list(out.glob("quiz-exploratory-data.*.js"))
            self.assertEqual(len(data_scripts), 1)
            ui_scripts = list(out.glob("quiz-exploratory.*.js"))
            self.assertEqual(len(ui_scripts), 1)
            style_sheets = list(out.glob("quiz.*.css"))
            self.assertEqual(len(style_sheets), 1)

    def test_exploratory_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            out1 = Path(tmp1) / "dist"
            out2 = Path(tmp2) / "dist"
            build_site(
                ROOT,
                out1,
                election_id="es-gen-2026",
                records_dir=ROOT / "content/elections/es-gen-2026",
                quiz_mode="exploratory",
                build_date="2026-11-20",
            )
            build_site(
                ROOT,
                out2,
                election_id="es-gen-2026",
                records_dir=ROOT / "content/elections/es-gen-2026",
                quiz_mode="exploratory",
                build_date="2026-11-20",
            )
            files1 = {p.name: p.read_bytes() for p in out1.rglob("*") if p.is_file()}
            files2 = {p.name: p.read_bytes() for p in out2.rglob("*") if p.is_file()}
            self.assertEqual(set(files1), set(files2))
            for name in files1:
                self.assertEqual(files1[name], files2[name], f"Mismatch in {name}")

    def test_unavailable_quiz_mode_preserves_static_notice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "dist"
            build_site(
                ROOT,
                out,
                election_id="es-gen-2026",
                records_dir=ROOT / "content/elections/es-gen-2026",
                quiz_mode="unavailable",
            )
            cuestionario_html = (out / "cuestionario/index.html").read_text(encoding="utf-8")
            self.assertIn("aún no está disponible", cuestionario_html)
            self.assertFalse(list(out.glob("quiz-exploratory-data.*.js")))


if __name__ == "__main__":
    unittest.main()
