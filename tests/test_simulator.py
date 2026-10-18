"""Simulator profile validation and static build tests (Epic E5).

All test fixtures use synthetic or official legal citations.
"""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from elecciones2026.generator import build_site, BuildValidationError, load_and_validate_site_data
from elecciones2026.simulator import prepare_simulator, SimulatorValidationError, safe_url, dual_review

ROOT = Path(__file__).resolve().parent.parent


class SimulatorBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = load_and_validate_site_data(ROOT)
        cls.raw_rules = json.loads((ROOT / "content/simulator/rules.json").read_text(encoding="utf-8"))
        cls.raw_mock = json.loads((ROOT / "content/simulator/mock.json").read_text(encoding="utf-8"))

    def prepare(self, raw, mock=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "simulator.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            return prepare_simulator(path, self.ctx, mock=mock)

    def test_mock_profile_validates_and_isolates(self):
        bundle = self.prepare(self.raw_mock, mock=True)
        self.assertEqual(bundle["election_id"], "simulator-fixture")
        self.assertEqual(bundle["mode"], "mock")
        self.assertEqual(bundle["total_seats"], 350)
        self.assertEqual(bundle["majority_threshold"], 176)
        self.assertTrue(bundle["available"])
        self.assertGreaterEqual(len(bundle["citations"]), 2)
        self.assertGreaterEqual(len(bundle["sample_groups"]), 1)

    def test_mock_profile_cannot_enter_reviewed_mode(self):
        with self.assertRaisesRegex(SimulatorValidationError, "Reviewed simulator profile must match target election ID"):
            self.prepare(self.raw_mock, mock=False)

    def test_reviewed_rules_profile_validates(self):
        bundle = self.prepare(self.raw_rules, mock=False)
        self.assertEqual(bundle["election_id"], self.ctx.election_id)
        self.assertEqual(bundle["mode"], "reviewed")
        self.assertEqual(bundle["total_seats"], 350)
        self.assertEqual(bundle["majority_threshold"], 176)
        self.assertTrue(bundle["available"])

    def test_bad_seats_or_threshold_fail(self):
        for bad_seats in (300, 351, 400, "350"):
            raw = deepcopy(self.raw_mock)
            raw["total_seats"] = bad_seats
            with self.subTest(seats=bad_seats), self.assertRaises(SimulatorValidationError):
                self.prepare(raw, mock=True)

        for bad_threshold in (175, 177, 200, "176"):
            raw = deepcopy(self.raw_mock)
            raw["majority_threshold"] = bad_threshold
            with self.subTest(threshold=bad_threshold), self.assertRaises(SimulatorValidationError):
                self.prepare(raw, mock=True)

    def test_bad_citations_fail(self):
        raw = deepcopy(self.raw_mock)
        raw["citations"] = []
        with self.assertRaises(SimulatorValidationError):
            self.prepare(raw, mock=True)

        raw = deepcopy(self.raw_mock)
        raw["citations"] = [{"source_id": "test", "title": "Test", "article": "1", "url": "http://insecure.test", "summary": "X"}]
        with self.assertRaises(SimulatorValidationError):
            self.prepare(raw, mock=True)

    def test_safe_url_requires_https(self):
        with self.assertRaises(SimulatorValidationError):
            safe_url("http://insecure.test")
        with self.assertRaises(SimulatorValidationError):
            safe_url("javascript:alert(1)")
        self.assertEqual(safe_url("https://www.boe.es/test"), "https://www.boe.es/test")

    def test_dual_review_validation(self):
        for bad in ({"review_status": "draft"},
                    {"review_status": "approved", "reviews": []},
                    {"review_status": "approved", "reviews": [{"reviewer_id": "rev-one", "review_date": "2026-10-12", "verdict": "approved", "review_notes": "ok", "reviewer_kind": "human", "evidence_ref": "https://example.test"}]}):
            with self.assertRaises(SimulatorValidationError):
                dual_review(bad)

    def test_default_build_unavailable_has_static_legal_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "site"
            build_site(ROOT, out, simulator_mode="unavailable")
            page = (out / "simulador/index.html").read_text(encoding="utf-8")
            self.assertIn("Herramienta no disponible en esta versión", page)
            self.assertIn("350 Diputados", page)
            self.assertIn("176 escaños", page)
            self.assertIn("BOE-A-1978-31229", page)
            self.assertFalse(list(out.glob("simulator-data.*.js")))
            self.assertFalse(list(out.glob("simulator-engine.*.js")))
            self.assertFalse(list(out.glob("simulator-ui.*.js")))
            self.assertNotIn("/simulador/", (out / "sitemap.xml").read_text(encoding="utf-8"))

    def test_mock_build_is_deterministic_and_noindex(self):
        with tempfile.TemporaryDirectory() as directory:
            out1 = Path(directory) / "one"
            out2 = Path(directory) / "two"
            res1 = build_site(ROOT, out1, simulator_mode="mock")
            res2 = build_site(ROOT, out2, simulator_mode="mock")
            self.assertEqual(res1.file_hashes, res2.file_hashes)

            page = (out1 / "simulador/index.html").read_text(encoding="utf-8")
            self.assertIn("noindex, nofollow", page)
            self.assertIn("Demostración técnica previa", page)
            self.assertIn("id=\"simulator-app\"", page)
            self.assertIn("id=\"simulator-hemicycle-chart\"", page)
            self.assertNotIn("/simulador/", (out1 / "sitemap.xml").read_text(encoding="utf-8"))
            self.assertEqual(len(list(out1.glob("simulator-data.*.js"))), 1)
            self.assertEqual(len(list(out1.glob("simulator-engine.*.js"))), 1)
            self.assertEqual(len(list(out1.glob("simulator-ui.*.js"))), 1)

    def test_reviewed_build_includes_sitemap(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "site"
            build_site(ROOT, out, simulator_mode="reviewed", simulator_file=ROOT / "content/simulator/rules.json")
            page = (out / "simulador/index.html").read_text(encoding="utf-8")
            self.assertNotIn("noindex, nofollow", page)
            self.assertIn("/simulador/", (out / "sitemap.xml").read_text(encoding="utf-8"))
            self.assertEqual(len(list(out.glob("simulator-data.*.js"))), 1)

    def test_invalid_simulator_profile_aborts_without_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid_file = Path(directory) / "corrupt.json"
            invalid_file.write_text("{}", encoding="utf-8")
            out = Path(directory) / "site"
            with self.assertRaises(BuildValidationError):
                build_site(ROOT, out, simulator_mode="mock", simulator_file=invalid_file)
            self.assertFalse(out.exists())

    def test_default_rebuild_withdraws_stale_simulator_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "site"
            build_site(ROOT, out, simulator_mode="mock")
            self.assertTrue(list(out.glob("simulator-data.*.js")))
            build_site(ROOT, out, simulator_mode="unavailable")
            self.assertFalse(list(out.glob("simulator-data.*.js")))
            self.assertFalse(list(out.glob("simulator-engine.*.js")))
            self.assertIn("no disponible en esta versión", (out / "simulador/index.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
