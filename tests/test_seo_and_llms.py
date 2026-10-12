"""Tests for SEO, Schema.org JSON-LD structured data, snippet controls, and AI/LLM discoverability (E3.1b)."""
import json
from pathlib import Path
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET

from elecciones2026.generator import (
    DEFAULT_BUILD_DATE,
    DEFAULT_CANONICAL_BASE,
    build_site,
    render_llms_txt,
    render_llms_full_txt,
    safe_json_ld,
    build_structured_data,
    load_and_validate_site_data,
)

ROOT_DIR = Path(__file__).resolve().parent.parent


class TestSeoAndLlms(unittest.TestCase):
    """Test suite for SEO optimizations and LLM discoverability artifacts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="elecciones_seo_test_"))
        cls.build_res = build_site(
            root_dir=ROOT_DIR,
            output_dir=cls.temp_dir,
            build_date=DEFAULT_BUILD_DATE,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        import shutil
        if cls.temp_dir.exists():
            shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_llms_txt_conforms_to_spec_and_dynamic_base(self) -> None:
        """Verify llms.txt follows the llmstxt.org specification and uses dynamic canonical_base."""
        llms_file = self.temp_dir / "llms.txt"
        self.assertTrue(llms_file.is_file(), "Missing llms.txt in build output")
        content = llms_file.read_text(encoding="utf-8")

        # 1. H1 title and summary blockquote
        self.assertTrue(content.startswith("# Comparador de Programas Electorales · Elecciones Generales 2026"))
        self.assertIn("> Comparador neutral e independiente", content)
        self.assertIn("BOE-A-2026-20742", content)

        # 2. Key sections
        self.assertIn("## Principios y Metodología", content)
        self.assertIn("## Páginas Principales", content)
        self.assertIn("## Temas Electorales", content)
        self.assertIn("## Candidaturas Monitorizadas", content)
        self.assertIn("## Sintaxis de Consulta para LLMs y Comparativas", content)
        self.assertIn("## Formato Completo para LLMs", content)

        # 3. Dynamic URLs
        self.assertIn(f"{DEFAULT_CANONICAL_BASE}/llms-full.txt", content)
        self.assertIn(f"{DEFAULT_CANONICAL_BASE}/temas/housing/", content)
        self.assertIn(f"{DEFAULT_CANONICAL_BASE}/partidos/pp/", content)

        # 4. Test custom base URL interpolation (e.g. preview domain)
        ctx = load_and_validate_site_data(ROOT_DIR, canonical_base="https://custom.test")
        custom_txt = render_llms_txt(ctx)
        self.assertIn("https://custom.test/llms-full.txt", custom_txt)
        self.assertNotIn(DEFAULT_CANONICAL_BASE, custom_txt)

    def test_llms_full_txt_structure_and_neutrality(self) -> None:
        """Verify llms-full.txt provides exhaustive structured text without hallucinations."""
        full_file = self.temp_dir / "llms-full.txt"
        self.assertTrue(full_file.is_file(), "Missing llms-full.txt in build output")
        content = full_file.read_text(encoding="utf-8")

        # 1. Header with compilation date and election ID
        self.assertIn("# Archivo Integral de Datos Electorales · Elecciones Generales 2026", content)
        self.assertIn("Fecha de compilación: 2026-10-09 | Elección: es-gen-2026", content)

        # 2. Complete taxonomy dump with 8 core topics
        self.assertIn("## 1. Taxonomía Temática y Subtemas", content)
        self.assertIn("### Tema: Vivienda (`housing`)", content)
        self.assertIn("- `rental-regulation`: Regulación del alquiler y precios", content)
        self.assertIn("### Tema: Educación (`education`)", content)

        # 3. Candidacy register and official source status
        self.assertIn("## 2. Candidaturas y Fuentes Oficiales Registradas", content)
        self.assertIn("Criterio de inclusión:", content)

        # 4. Verified statements and quotes
        self.assertIn("## 3. Posiciones y Afirmaciones Electorales Verificadas", content)
        self.assertIn("Cita literal: «", content)
        self.assertIn("Estado de revisión:", content)

        # 5. Comparative relationships
        self.assertIn("## 4. Relaciones Comparativas Verificadas entre Candidaturas", content)
        self.assertIn("Resumen comparativo:", content)

        # 6. Quality criteria and rectification SLAs
        self.assertIn("## 5. Criterios de Calidad y Rectificación", content)
        self.assertIn("Sev-1 (crítica, resolución <= 12h)", content)

    def test_pilot_election_isolation_in_llms_files(self) -> None:
        """Verify pilot election 2023 generates isolated llms texts with required warnings."""
        ctx_pilot = load_and_validate_site_data(ROOT_DIR, election_id="es-gen-2023", canonical_base="https://pilot.test")
        pilot_txt = render_llms_txt(ctx_pilot)
        self.assertIn("Generales 2023 (Ensayo piloto)", pilot_txt)
        self.assertIn("Estricto aislamiento respecto a 2026", pilot_txt)

        pilot_full_txt = render_llms_full_txt(ctx_pilot)
        self.assertIn("Generales 2023 (Ensayo piloto)", pilot_full_txt)

    def test_json_ld_validity_and_schema_types_across_all_pages(self) -> None:
        """Verify every HTML page contains valid, parseable Schema.org JSON-LD graph."""
        html_files = list(self.temp_dir.rglob("*.html"))
        self.assertGreater(len(html_files), 10, "Expected at least 10 HTML pages")

        json_ld_regex = re.compile(
            r'<script\s+type="application/ld\+json">(.*?)</script>',
            re.DOTALL,
        )

        for path in html_files:
            rel = str(path.relative_to(self.temp_dir))
            content = path.read_text(encoding="utf-8")
            match = json_ld_regex.search(content)
            self.assertIsNotNone(match, f"Page {rel} lacks Schema.org JSON-LD block")

            raw_json = match.group(1).strip()
            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError as err:
                self.fail(f"Invalid JSON-LD on {rel}: {err}\nRaw:\n{raw_json}")

            self.assertEqual(data.get("@context"), "https://schema.org")
            graph = data.get("@graph")
            self.assertIsInstance(graph, list, f"JSON-LD @graph must be a list on {rel}")
            types = [node.get("@type") for node in graph]

            # All pages must include the publishing Organization
            self.assertIn("Organization", types, f"Missing Organization node on {rel}")

            # Specific route assertions
            if rel == "index.html":
                self.assertIn("WebSite", types)
                self.assertIn("ItemList", types)
                website_node = next(n for n in graph if n.get("@type") == "WebSite")
                self.assertIn("potentialAction", website_node)
                self.assertEqual(website_node["potentialAction"]["@type"], "SearchAction")
            elif rel.startswith("temas/"):
                if rel == "temas/index.html":
                    self.assertIn("CollectionPage", types)
                    self.assertIn("BreadcrumbList", types)
                else:
                    self.assertIn("ItemPage", types)
                    self.assertIn("BreadcrumbList", types)
            elif rel.startswith("partidos/"):
                if rel == "partidos/index.html":
                    self.assertIn("CollectionPage", types)
                    self.assertIn("BreadcrumbList", types)
                else:
                    self.assertIn("ItemPage", types)
                    self.assertIn("BreadcrumbList", types)
                    item_page = next(n for n in graph if n.get("@type") == "ItemPage")
                    self.assertEqual(item_page.get("about", {}).get("@type"), "PoliticalParty")
            elif rel in ("metodo/index.html", "correcciones/index.html"):
                self.assertIn("AboutPage", types)
                self.assertIn("BreadcrumbList", types)
            elif rel == "fuentes/index.html":
                self.assertIn("Dataset", types)
                self.assertIn("BreadcrumbList", types)

            # Validate breadcrumb list items sequential order if present
            if "BreadcrumbList" in types:
                b_node = next(n for n in graph if n.get("@type") == "BreadcrumbList")
                items = b_node.get("itemListElement", [])
                self.assertGreater(len(items), 0)
                positions = [item["position"] for item in items]
                self.assertEqual(positions, list(range(1, len(items) + 1)), f"Non-sequential breadcrumbs on {rel}")

    def test_seo_metadata_snippet_controls_and_twitter(self) -> None:
        """Verify robots snippet controls, Twitter cards, and markdown alternate links."""
        index_html = (self.temp_dir / "index.html").read_text(encoding="utf-8")

        # Robots snippet directive
        self.assertIn(
            '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">',
            index_html,
        )

        # Language alternates
        self.assertIn(f'<link rel="alternate" hreflang="es" href="{DEFAULT_CANONICAL_BASE}/">', index_html)
        self.assertIn(f'<link rel="alternate" hreflang="x-default" href="{DEFAULT_CANONICAL_BASE}/">', index_html)

        # Markdown alternate link
        self.assertIn('<link rel="alternate" type="text/markdown" href="./llms.txt" title="Documentación para LLMs">', index_html)

        # Twitter tags
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', index_html)
        self.assertIn('<meta name="twitter:title"', index_html)
        self.assertIn('<meta name="twitter:description"', index_html)
        self.assertIn('<meta name="twitter:image"', index_html)

    def test_sitemap_xml_contains_priority_and_all_routes(self) -> None:
        """Verify sitemap.xml includes RFC/schema compliant priorities for all indexed routes."""
        sitemap_path = self.temp_dir / "sitemap.xml"
        self.assertTrue(sitemap_path.is_file())
        tree = ET.parse(sitemap_path)
        root = tree.getroot()

        # Namespace
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall("sm:url", ns)
        self.assertGreater(len(urls), 20)

        for u in urls:
            loc = u.find("sm:loc", ns).text
            prio = u.find("sm:priority", ns).text
            self.assertIsNotNone(loc)
            self.assertIsNotNone(prio)
            prio_val = float(prio)
            self.assertGreaterEqual(prio_val, 0.0)
            self.assertLessEqual(prio_val, 1.0)

            if loc == f"{DEFAULT_CANONICAL_BASE}/":
                self.assertEqual(prio, "1.0")
            elif "/temas/" in loc:
                self.assertEqual(prio, "0.9")
            elif "/partidos/" in loc:
                self.assertEqual(prio, "0.8")

    def test_hostile_script_breakout_escaped_in_json_ld(self) -> None:
        """Verify safe_json_ld prevents script injection and hostile angle bracket attacks."""
        hostile_payload = {
            "@context": "https://schema.org",
            "name": "</script><script>alert('xss')</script>",
            "description": "Safe text with <tag> & special chars",
            "empty": None,
        }
        rendered = safe_json_ld(hostile_payload)
        self.assertNotIn("alert('xss')", rendered.split("\\u003c")[-1])
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("</script>", rendered[rendered.find("{"):rendered.rfind("}")])
        self.assertIn(r"\u003c/script\u003e", rendered)
        self.assertNotIn('"empty": null', rendered)

    def test_nginx_crawler_rules_and_cache_control(self) -> None:
        """Verify nginx/default.conf includes llms.txt and llms-full.txt under ADR-0001 caching policy."""
        nginx_conf = (ROOT_DIR / "nginx" / "default.conf").read_text(encoding="utf-8")
        self.assertIn("location ~* ^/(?:robots\\.txt|sitemap\\.xml|security\\.txt|\\.well-known/security\\.txt|llms\\.txt|llms-full\\.txt)$", nginx_conf)
        self.assertIn("charset utf-8;", nginx_conf)
        self.assertIn("max-age=3600, stale-while-revalidate=86400", nginx_conf)


if __name__ == "__main__":
    unittest.main()
