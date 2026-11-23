"""E2.4: the private 2023 source index must not present 2026 inventory."""

import tempfile
import unittest
from pathlib import Path

from elecciones2026.generator import build_site
from elecciones2026.source_register import load_register


ROOT = Path(__file__).resolve().parents[1]


class PilotSourceIndexScopeTests(unittest.TestCase):
    def test_2023_pilot_lists_only_2023_sources(self):
        register = load_register(ROOT / "content/sources/register.json")
        sources_2023 = [source for source in register.sources if source.election_id == "es-gen-2023"]
        sources_2026 = [source for source in register.sources if source.election_id == "es-gen-2026"]
        self.assertTrue(sources_2023)
        self.assertTrue(sources_2026)

        with tempfile.TemporaryDirectory(prefix="pilot-source-scope-") as temporary:
            output = Path(temporary) / "site"
            result = build_site(ROOT, output, election_id="es-gen-2023", build_date="2026-11-23")
            html = (output / "fuentes/index.html").read_text(encoding="utf-8")

        self.assertEqual((result.statements_count, result.relationships_count), (0, 0))
        self.assertIn("Fuentes monitorizadas · Elecciones Generales 2023", html)
        self.assertNotIn("Fuentes monitorizadas · Elecciones Generales 2026", html)
        self.assertNotIn("Fuentes históricas de ensayo", html)
        for source in sources_2023:
            with self.subTest(source=source.id):
                self.assertIn(f'href="{source.official_url}"', html)
        current_urls = {source.official_url for source in sources_2023}
        for source in sources_2026:
            if source.official_url not in current_urls:
                with self.subTest(excluded_source=source.id):
                    self.assertNotIn(f'href="{source.official_url}"', html)


if __name__ == "__main__":
    unittest.main()
