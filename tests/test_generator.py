"""Unit tests for deterministic Python 3.14 static site generator (Roadmap package E3.1).

Verifies acceptance criteria for OpenSpec tasks 3.1 and 3.7:
- Identical approved inputs produce byte-for-byte identical output.
- Unreviewed, draft, or invalid statements fail the build without partial output.
- All pages declare <html lang="es"> and accurate canonical URLs.
- Source-linked pages expose all claims, quotes, caveats, and citations without JavaScript.
- Sitemap.xml is valid XML and lists all published routes.
- Robots.txt allows public crawling, disallows /preview/, and references sitemap.
- HTML escaping prevents XSS injection from source fields.
- Prohibited elements (profile UI, fake verification claims, interactive report forms) are absent.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from elecciones2026.generator import (
    DEFAULT_BUILD_DATE,
    DEFAULT_CANONICAL_BASE,
    BuildValidationError,
    SiteBuildResult,
    build_site,
    load_and_validate_site_data,
    verify_determinism,
)
from elecciones2026.schemas import ReviewRecord, StatementRecord

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"


class TestStaticSiteGenerator(unittest.TestCase):
    """Test suite for deterministic static site generation."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="elecciones_test_gen_"))
        self.output_dir = self.temp_dir / "dist"

    def tearDown(self) -> None:
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_developer_profile_credit_preserves_both_election_footers(self) -> None:
        for election in ('es-gen-2023', 'es-gen-2026'):
            target = self.output_dir / election
            build_site(root_dir=ROOT_DIR, output_dir=target, election_id=election)
            pages = list(target.rglob('*.html'))
            self.assertTrue(pages)
            for page in pages:
                with self.subTest(election=election, page=page.relative_to(target)):
                    html = page.read_text()
                    self.assertIn('Desarrollado por <a href="https://github.com/barnolacesc" rel="noopener noreferrer">barnolacesc</a>', html)
                    if election == 'es-gen-2023':
                        self.assertIn('Ensayo privado y confidencial', html)
                    else:
                        self.assertIn('Neutralidad · Fuentes directas · Transparencia', html)

    def test_empty_2023_comparison_links_to_coverage_without_claims(self) -> None:
        """A source-gated empty comparison still has a useful next step without JS."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            election_id="es-gen-2023",
            build_date="2026-10-24",
        )
        home = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="./metodo/">Consultar cobertura y método</a>', home)
        self.assertIn('La falta de contenido aprobado no indica', home)
        self.assertNotIn('class="party-statement"', home)

    def test_task_3_1_deterministic_repeat_build_identical_hashes(self) -> None:
        """Verify Task 3.1: identical approved input produces identical output across multiple builds."""
        dir1 = self.temp_dir / "build_run_1"
        dir2 = self.temp_dir / "build_run_2"

        res1 = build_site(
            root_dir=ROOT_DIR,
            output_dir=dir1,
            build_date="2026-10-09",
        )
        res2 = build_site(
            root_dir=ROOT_DIR,
            output_dir=dir2,
            build_date="2026-10-09",
        )

        # File inventory must match exactly
        self.assertEqual(res1.files_written, res2.files_written)
        self.assertGreater(len(res1.files_written), 25)

        # Byte-for-byte hash comparison of every single file
        for rel_path in res1.files_written:
            h1 = res1.file_hashes[rel_path]
            h2 = res2.file_hashes[rel_path]
            self.assertEqual(
                h1,
                h2,
                f"File {rel_path} differs between builds: {h1} != {h2}",
            )

        # Also test the verify_determinism helper
        self.assertTrue(verify_determinism(root_dir=ROOT_DIR, runs=2))

    def test_task_3_1_draft_statement_fails_build_without_partial_output(self) -> None:
        """Verify Task 3.1: draft or unreviewed statement fails the build without leaving partial output."""
        output_dir = self.temp_dir / "abort_target"

        draft_stmt = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-test-draft-unapproved",
            party_id="partido-ejemplo-a",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Borrador no revisado de vivienda",
            review_status="draft",  # Invalid for publish set!
            reviews=[
                ReviewRecord("rev-1", "2026-10-09", "approved", "ok"),
                ReviewRecord("rev-2", "2026-10-09", "approved", "ok"),
            ],
        )

        with self.assertRaises(BuildValidationError) as ctx:
            build_site(
                root_dir=ROOT_DIR,
                output_dir=output_dir,
                custom_statements=[draft_stmt],
                strict_approved=True,
            )

        self.assertIn("unreviewed status 'draft'", str(ctx.exception))
        # Ensure no partially published site exists
        if output_dir.exists():
            files = list(output_dir.glob("**/*"))
            self.assertEqual(files, [], f"Target directory must be empty after build failure: {files}")

    def test_single_reviewer_statement_fails_four_eyes_check(self) -> None:
        """Verify statement with only one reviewer fails dual review requirement."""
        output_dir = self.temp_dir / "single_rev_target"

        single_rev_stmt = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-single-rev-test",
            party_id="partido-ejemplo-a",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Propuesta con un solo revisor",
            review_status="approved",
            reviews=[
                ReviewRecord("rev-1", "2026-10-09", "approved", "ok"),
            ],  # Missing second reviewer!
        )

        with self.assertRaises(BuildValidationError) as ctx:
            build_site(
                root_dir=ROOT_DIR,
                output_dir=output_dir,
                custom_statements=[single_rev_stmt],
                strict_approved=True,
            )

        self.assertIn("Four-Eyes", str(ctx.exception))

    def test_excessive_quote_fails_editorial_limits(self) -> None:
        """Verify quote exceeding 40 words fails build validation."""
        output_dir = self.temp_dir / "excess_quote_target"

        long_quote = " ".join(["palabra"] * 45)
        stmt = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-long-quote-test",
            party_id="partido-ejemplo-a",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Propuesta con cita excesiva",
            quote=long_quote,
            source_page="12",
            review_status="approved",
            reviews=[
                ReviewRecord("rev-1", "2026-10-09", "approved", "ok"),
                ReviewRecord("rev-2", "2026-10-09", "approved", "ok"),
            ],
        )

        with self.assertRaises(BuildValidationError) as ctx:
            build_site(
                root_dir=ROOT_DIR,
                output_dir=output_dir,
                custom_statements=[stmt],
                strict_approved=True,
            )

        self.assertIn("quote exceeds limit", str(ctx.exception))

    def test_task_3_7_all_html_files_declare_spanish_and_canonical(self) -> None:
        """Verify Task 3.7: every generated HTML page declares lang=es and has accurate canonical link."""
        res = build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        html_files = [f for f in res.files_written if f.endswith(".html")]
        self.assertGreater(len(html_files), 10)

        for rel_file in html_files:
            file_path = self.output_dir / rel_file
            content = file_path.read_text(encoding="utf-8")

            # 1. Spanish language declaration
            self.assertIn('<html lang="es">', content, f"Missing <html lang=\"es\"> in {rel_file}")

            # 2. Canonical link present and accurate
            self.assertIn('<link rel="canonical" href="https://xn--eleccionesespaa2026-83b.es/', content, f"Missing canonical in {rel_file}")

            # 3. Viewport tag
            self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', content)

            # 4. Skip link
            self.assertIn('class="skip-link"', content)
            self.assertIn('href="#contenido"', content)

            # 5. Semantic landmarks
            self.assertIn("<header", content)
            self.assertIn("<main", content)
            self.assertIn("<footer", content)

    def test_task_3_7_crawlable_without_javascript(self) -> None:
        """Verify Task 3.7: text-only fetch exposes approved claims and source references without JavaScript."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        # 1. Topic page test: housing
        housing_path = self.output_dir / "temas" / "housing" / "index.html"
        self.assertTrue(housing_path.is_file())
        housing_html = housing_path.read_text(encoding="utf-8")

        # Claims and quotes must be directly in HTML
        self.assertIn("Vivienda", housing_html)
        self.assertIn("Regulación del alquiler y precios", housing_html)
        self.assertIn("Partido Ejemplo A", housing_html)
        self.assertIn("Limitar los precios de alquiler", housing_html)
        self.assertIn("Estableceremos un límite de precios vinculante", housing_html)
        # Source citation link directly in HTML
        self.assertIn("href=\"https://partido-ejemplo-a.es/programa-2026.pdf#page=34\"", housing_html)
        self.assertIn("pág. 34", housing_html)
        # Explicit missing state rendered
        self.assertIn("No consta en el programa", housing_html)
        self.assertIn("La ausencia de una medida en el programa no debe interpretarse como oposición", housing_html)
        # Update date visible
        self.assertIn("<time datetime=\"2026-10-09\">", housing_html)

        # 2. Party page test: partido-ejemplo-a
        party_path = self.output_dir / "partidos" / "partido-ejemplo-a" / "index.html"
        self.assertTrue(party_path.is_file())
        party_html = party_path.read_text(encoding="utf-8")
        self.assertIn("Partido Ejemplo A", party_html)
        self.assertIn("Limitar los precios de alquiler", party_html)

        # 3. Methodology page test
        method_path = self.output_dir / "metodo" / "index.html"
        self.assertTrue(method_path.is_file())
        method_html = method_path.read_text(encoding="utf-8")
        self.assertIn("Principio de cuatro ojos", method_html)
        self.assertIn("40 palabras", method_html)
        self.assertIn("Aviso de privacidad y protección de datos", method_html)
        self.assertIn("privacidad@elecciones2026.es", method_html)
        self.assertIn("La función en línea para avisar de errores estará disponible más adelante", method_html)

        # 4. Sources page test
        fuentes_path = self.output_dir / "fuentes" / "index.html"
        self.assertTrue(fuentes_path.is_file())
        fuentes_html = fuentes_path.read_text(encoding="utf-8")
        self.assertIn("Fuentes oficiales y trazabilidad", fuentes_html)
        self.assertIn("Piloto 2023", fuentes_html)
        self.assertIn("Aislamiento de elecciones", fuentes_html)

        # 5. Corrections page test
        corrections_path = self.output_dir / "correcciones" / "index.html"
        self.assertTrue(corrections_path.is_file())
        corrections_html = corrections_path.read_text(encoding="utf-8")
        self.assertIn("Registro de correcciones", corrections_html)
        self.assertIn("cor-2026-001", corrections_html)

    def test_task_3_7_sitemap_xml_valid_and_comprehensive(self) -> None:
        """Verify Task 3.7: sitemap.xml is valid XML and covers all public routes."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        sitemap_path = self.output_dir / "sitemap.xml"
        self.assertTrue(sitemap_path.is_file())

        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        urls = [elem.text for elem in root.findall("sm:url/sm:loc", namespace)]
        self.assertGreater(len(urls), 20)

        # Must include core endpoints
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/", urls)
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/temas/", urls)
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/partidos/", urls)
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/metodo/", urls)
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/fuentes/", urls)
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/correcciones/", urls)

        # Must include all 8 core topics
        for tid in ["housing", "education", "health-social-services", "economy-work-tax",
                    "immigration", "foreign-policy-eu", "climate-energy", "institutions-rights"]:
            self.assertIn(f"https://xn--eleccionesespaa2026-83b.es/temas/{tid}/", urls)

        # Verify lastmod is formatted as YYYY-MM-DD
        for lastmod in root.findall("sm:url/sm:lastmod", namespace):
            self.assertRegex(lastmod.text, r"^\d{4}-\d{2}-\d{2}$")

    def test_task_3_7_robots_txt_accurate(self) -> None:
        """Verify Task 3.7: robots.txt contains required crawler directives and sitemap URL."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        robots_path = self.output_dir / "robots.txt"
        self.assertTrue(robots_path.is_file())
        content = robots_path.read_text(encoding="utf-8")

        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn("Disallow: /preview/", content)
        self.assertIn("Sitemap: https://xn--eleccionesespaa2026-83b.es/sitemap.xml", content)

    def test_safe_html_escaping_prevents_xss(self) -> None:
        """Verify hostile strings containing HTML/script tags are rendered as inert text."""
        malicious_summary = "<script>alert('xss_attack')</script>"
        malicious_quote = "Quote with <img src=x onerror=alert(1)> embedded"
        malicious_caveat = "Caveat with <iframe src='javascript:alert(2)'></iframe>"

        xss_stmt = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-xss-test",
            party_id="partido-ejemplo-a",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary=malicious_summary,
            quote=malicious_quote,
            qualifications=[malicious_caveat],
            source_page="1",
            source_url="https://example.com/source.pdf",
            source_version="1.0.0",
            last_reviewed_date="2026-10-09",
            is_fixture=True,
            review_status="approved",
            reviews=[
                ReviewRecord("rev-1", "2026-10-09", "approved", "verified"),
                ReviewRecord("rev-2", "2026-10-09", "approved", "verified"),
            ],
        )

        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            custom_statements=[xss_stmt],
            custom_relationships=[],
            build_date="2026-10-09",
        )

        topic_html = (self.output_dir / "temas" / "housing" / "index.html").read_text(encoding="utf-8")

        # Must NOT contain raw unescaped script or onerror tags
        self.assertNotIn("<script>", topic_html)
        self.assertNotIn("<img src=x onerror=", topic_html)
        self.assertNotIn("<iframe", topic_html)

        # Must contain safely escaped entities
        self.assertIn("&lt;script&gt;alert(&#x27;xss_attack&#x27;)&lt;/script&gt;", topic_html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", topic_html)
        self.assertIn("&lt;iframe src=&#x27;javascript:alert(2)&#x27;&gt;&lt;/iframe&gt;", topic_html)

    def test_prohibited_elements_absent_across_all_pages(self) -> None:
        """Verify no profile UI, fake verification badges, or interactive feedback forms exist."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        for root, _, files in os.walk(self.output_dir):
            for fname in files:
                if fname.endswith(".html"):
                    path = Path(root) / fname
                    text = path.read_text(encoding="utf-8").lower()
                    self.assertNotIn("100% verificado", text, f"Found fake verification in {fname}")
                    self.assertNotIn("100% oficial", text, f"Found fake verification in {fname}")
                    self.assertNotIn("mi perfil", text, f"Found profile UI in {fname}")
                    self.assertNotIn("iniciar sesión", text, f"Found login UI in {fname}")

    def test_rfc9116_security_txt_files(self) -> None:
        """Verify security.txt and .well-known/security.txt are generated with RFC 9116 contact."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        sec1 = self.output_dir / "security.txt"
        sec2 = self.output_dir / ".well-known" / "security.txt"
        self.assertTrue(sec1.is_file())
        self.assertTrue(sec2.is_file())

        content = sec1.read_text(encoding="utf-8")
        self.assertIn("Contact: mailto:seguridad@elecciones2026.es", content)
        self.assertIn("Expires: 2026-12-31T23:59:59.000Z", content)

    def test_task_e8_5_proposals_page_generation(self) -> None:
        """Verify Package E8.5: propuestas/index.html is generated with correct form, honeypot, and canonical."""
        build_site(
            root_dir=ROOT_DIR,
            output_dir=self.output_dir,
            build_date="2026-10-09",
        )

        prop_path = self.output_dir / "propuestas" / "index.html"
        self.assertTrue(prop_path.is_file())
        content = prop_path.read_text(encoding="utf-8")

        self.assertIn('<html lang="es">', content)
        self.assertIn('<link rel="canonical" href="https://xn--eleccionesespaa2026-83b.es/propuestas/">', content)
        self.assertIn('Buzón de propuestas', content)
        self.assertIn('name="_hp_company"', content)
        self.assertIn('minlength="10"', content)
        self.assertIn('maxlength="600"', content)
        self.assertIn('form id="proposal-form"', content)
        self.assertIn('Buzón de propuestas</a>', content)

        # Also check sitemap.xml contains /propuestas/
        sitemap_path = self.output_dir / "sitemap.xml"
        sitemap_content = sitemap_path.read_text(encoding="utf-8")
        self.assertIn("https://xn--eleccionesespaa2026-83b.es/propuestas/", sitemap_content)


if __name__ == "__main__":
    unittest.main()
