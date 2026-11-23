"""Unit and integration tests for the 2026 exploratory questionnaire (E4.2 / E4.3)."""
from copy import deepcopy
from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from elecciones2026.generator import build_site, load_and_validate_site_data, BuildValidationError
from elecciones2026.mobile_accessibility import QuietHandler
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

    def test_topbar_menu_includes_cuestionario_link(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out = Path(tmp_dir)
            build_site(
                ROOT,
                out,
                election_id="es-gen-2026",
                records_dir=ROOT / "content/elections/es-gen-2026",
                quiz_mode="exploratory",
            )
            index_html = (out / "index.html").read_text(encoding="utf-8")
            nav_section = index_html.split('<nav class="nav-links"', 1)[1].split('</nav>', 1)[0]
            top_links = nav_section.split('<details class="site-menu">', 1)[0]
            self.assertIn('href="./cuestionario/"', top_links)
            self.assertIn(">Cuestionario<", top_links)

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


@unittest.skipUnless(os.environ.get("ELECTIONS_TEST_EXPLORATORY_BROWSER") == "1",
                     "Opt-in Chromium exploratory questionnaire test")
class ExploratoryQuizBrowserTests(unittest.TestCase):
    def test_answer_layout_focus_and_sources(self):
        from playwright.sync_api import sync_playwright

        with tempfile.TemporaryDirectory() as output, sync_playwright() as playwright:
            build_site(
                ROOT, Path(output), election_id="es-gen-2026", quiz_mode="exploratory",
                records_dir=ROOT / "content/elections/es-gen-2026",
            )
            handler = partial(QuietHandler, directory=output)
            with ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
                thread = Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    with playwright.chromium.launch() as browser:
                        for width in (320, 360, 390, 430, 1024):
                            with self.subTest(width=width):
                                page = browser.new_page(viewport={"width": width, "height": 800})
                                try:
                                    self.check_questionnaire(page, server.server_port, width)
                                finally:
                                    page.close()
                finally:
                    server.shutdown()
                    thread.join()

    def check_questionnaire(self, page, port, width):
        from playwright.sync_api import expect

        page.goto(f"http://127.0.0.1:{port}/cuestionario/")
        labels = page.locator(".exploratory-answer")
        expect(labels).to_have_count(144)
        self.assertEqual(page.evaluate("document.activeElement.tagName"), "BODY")
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), width)
        self.assertTrue(labels.evaluate_all("""(rows) => rows.every(row => {
            const {left, right, width, height} = row.getBoundingClientRect();
            return left >= 0 && right <= innerWidth && width >= 44 && height >= 44;
        })"""))
        first, second, third = (labels.nth(index) for index in range(3))
        self.assertEqual(first.bounding_box()["y"] == second.bounding_box()["y"], width == 1024)
        self.assertGreater(third.bounding_box()["y"], first.bounding_box()["y"])
        radio = first.get_by_role("radio")
        self.assertLess(radio.bounding_box()["width"], 24)
        radio.focus()
        expect(first).to_have_css("outline-style", "solid")
        expect(radio).to_have_css("outline-style", "none")
        page.keyboard.press("ArrowRight")
        expect(second.get_by_role("radio")).to_be_checked()

        source = page.locator(".exploratory-references summary").first
        self.assertGreaterEqual(source.bounding_box()["height"], 44)
        source.focus()
        page.keyboard.press("Enter")
        expect(source.locator("..").get_by_role("link").first).to_be_visible()
        page.locator("#finish").click()
        expect(page.locator("#results-heading")).to_be_focused()
        expect(page.locator(".result-user-answer").first).to_contain_text("Más bien a favor")
        page.locator("#edit").click()
        expect(radio).to_be_focused()
        expect(second.get_by_role("radio")).to_be_checked()


if __name__ == "__main__":
    unittest.main()
