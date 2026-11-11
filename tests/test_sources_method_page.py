"""Unit tests for concise sources, method, and corrections pages (Package E2.4, Issue #11).

Verifies acceptance criteria for OpenSpec Task 3.4:
- Inclusion rule, source coverage, update date, and correction policy are readable on mobile.
- No working report form is implied (static notice + deferred reporting).
- Source coverage cards display status badges, version, date, SHA-256 hash/pending, and rights.
- Public 2026 pages do not expose the private historical pilot.
- 44px touch targets and responsive wrapping prevent horizontal overflow at 360/390/430px.
"""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import tempfile
import unittest

from elecciones2026.generator import (
    DEFAULT_BUILD_DATE,
    build_site,
    format_date_spanish,
    load_and_validate_site_data,
    render_source_coverage_card,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT_DIR / "site"
CONTENT_DIR = ROOT_DIR / "content"


class TestSourcesMethodCorrectionsPage(unittest.TestCase):
    """Test suite for sources, methodology, and corrections page requirements (E2.4)."""

    def setUp(self) -> None:
        self.metodo_html_path = SITE_DIR / "metodo" / "index.html"
        self.fuentes_html_path = SITE_DIR / "fuentes" / "index.html"
        self.correcciones_html_path = SITE_DIR / "correcciones" / "index.html"
        self.css_path = SITE_DIR / "styles.css"

        self.metodo_html = self.metodo_html_path.read_text(encoding="utf-8")
        self.fuentes_html = self.fuentes_html_path.read_text(encoding="utf-8")
        self.correcciones_html = self.correcciones_html_path.read_text(encoding="utf-8")
        self.css_content = self.css_path.read_text(encoding="utf-8")

        self.ctx = load_and_validate_site_data(ROOT_DIR)
        self.source_register = self.ctx.register
        self.parties = self.ctx.parties

    def test_pages_exist_and_declare_spanish_language(self) -> None:
        """Verify all three primary pages exist and declare lang='es'."""
        for path, html in [
            (self.metodo_html_path, self.metodo_html),
            (self.fuentes_html_path, self.fuentes_html),
            (self.correcciones_html_path, self.correcciones_html),
        ]:
            self.assertTrue(path.is_file(), f"Missing file: {path}")
            self.assertIn('<html lang="es">', html, f"Page {path} must declare lang='es'")

    def test_update_date_stamp_present_and_formatted(self) -> None:
        """Verify update date timestamp is present in ISO format and formatted in Spanish."""
        for name, html in [
            ("metodo", self.metodo_html),
            ("fuentes", self.fuentes_html),
            ("correcciones", self.correcciones_html),
        ]:
            self.assertIn('class="update-stamp"', html, f"Missing update-stamp in {name}")
            self.assertIn('<time class="update-date"', html, f"Missing update-date in {name}")
            # Verify datetime attribute has valid ISO date format YYYY-MM-DD
            datetime_match = re.search(r'<time class="update-date" datetime="(\d{4}-\d{2}-\d{2})">([^<]+)</time>', html)
            self.assertIsNotNone(datetime_match, f"Invalid time tag format in {name}")
            iso_date, formatted_text = datetime_match.group(1), datetime_match.group(2)
            self.assertEqual(iso_date, DEFAULT_BUILD_DATE)
            # Spanish text should contain "octubre de 2026"
            self.assertIn("octubre de 2026", formatted_text.lower(), f"Unexpected Spanish date format in {name}")

        # Unit test format_date_spanish helper
        self.assertEqual(format_date_spanish("2026-10-09"), "9 de octubre de 2026")
        self.assertEqual(format_date_spanish("2026-01-15"), "15 de enero de 2026")

    def test_inclusion_rules_detailed_and_clear(self) -> None:
        """Verify inclusion rules in methodology page clearly explain Criteria A and B."""
        # Check Criterion A: Previous parliamentary representation
        self.assertIn("Criterio A (Representación parlamentaria previa)", self.metodo_html)
        self.assertIn("Cortes Generales", self.metodo_html)
        self.assertIn("Parlamento Europeo", self.metodo_html)

        # Check Criterion B: Official proclamation in minimum constituencies
        self.assertIn("Criterio B (Proclamación nacional de candidaturas)", self.metodo_html)
        self.assertIn("Junta Electoral Central", self.metodo_html)
        self.assertIn("circunscripciones", self.metodo_html)

        # Check territorial neutrality and alphabetical ordering
        self.assertIn("Candidaturas de ámbito territorial o autonómico", self.metodo_html)
        self.assertIn("orden alfabético", self.metodo_html.lower())

    def test_source_coverage_cards_for_all_candidacies(self) -> None:
        """Verify coverage cards are rendered for all 2026 registered candidacies."""
        sources_2026 = [
            src for src in self.source_register.sources if src.election_id == "es-gen-2026"
        ]
        self.assertGreaterEqual(len(sources_2026), 9)

        # Both /metodo/ and /fuentes/ must expose coverage cards
        for page_name, html in [("metodo", self.metodo_html), ("fuentes", self.fuentes_html)]:
            self.assertIn('class="coverage-cards"', html, f"Missing .coverage-cards in {page_name}")
            for src in sources_2026:
                # Candidature name or publisher must appear inside coverage cards
                self.assertTrue(
                    src.publisher in html or src.candidature_name in html,
                    f"Candidacy {src.publisher} / {src.candidature_name} missing from {page_name}",
                )

    def test_coverage_card_details_and_badges(self) -> None:
        """Verify coverage card metadata fields: status badge, version, date, hash/pending, rights."""
        # Find all coverage-card occurrences in /metodo/
        self.assertIn('class="coverage-card"', self.metodo_html)
        self.assertIn('class="coverage-card-header"', self.metodo_html)
        self.assertIn('class="coverage-meta-row"', self.metodo_html)
        self.assertIn('class="coverage-card-footer"', self.metodo_html)

        # Verify status badges present
        self.assertIn("status-badge", self.metodo_html)
        self.assertTrue(
            "Programa no disponible" in self.metodo_html or "Programa oficial" in self.metodo_html,
            "Must contain localized status badge label",
        )

        # Verify hash and rights labels
        self.assertIn("SHA-256", self.metodo_html)
        self.assertIn("Derechos cita", self.metodo_html)
        self.assertIn("Enlace oficial", self.metodo_html)

        # Outbound links must have rel="noopener noreferrer"
        outbound_links = re.findall(r'<a\s+href="https?://[^"]+"[^>]*>', self.metodo_html)
        self.assertGreater(len(outbound_links), 0, "Should have outbound source links")
        for link in outbound_links:
            self.assertIn('rel="noopener noreferrer"', link, f"Outbound link missing rel in {link}")

    def test_public_2026_pages_exclude_historical_pilot(self) -> None:
        """The public source and method pages show only the current election."""
        for html in (self.metodo_html, self.fuentes_html):
            self.assertNotIn("Piloto 2023", html)
            self.assertNotIn("ensayos del piloto de 2023", html)
            self.assertIn("Elecciones 2026", html)

    def test_correction_policy_and_sla_guarantees(self) -> None:
        """Verify correction policy explains automatic invalidation, SLAs, Four-Eyes, and errata log."""
        for html in [self.metodo_html, self.correcciones_html]:
            # Invalidation of dependent comparisons
            self.assertIn("invalida", html.lower())

            # Four-Eyes segregation
            self.assertIn("cuatro ojos", html.lower())
            self.assertIn("segregación", html.lower())

            # SLA levels
            self.assertIn("sev-1", html.lower())
            self.assertIn("12 horas", html.lower())
            self.assertIn("sev-2", html.lower())
            self.assertIn("24 horas", html.lower())
            self.assertIn("sev-3", html.lower())
            self.assertIn("48 horas", html.lower())

        # Metodo must link to correcciones and correcciones must link to metodo
        self.assertIn('href="../correcciones/"', self.metodo_html)
        self.assertIn('href="../metodo/#rectificaciones"', self.correcciones_html)

        # Errata log entries must exist in correcciones
        self.assertIn("cor-2026-001", self.correcciones_html)
        self.assertIn("cor-2026-002", self.correcciones_html)

    def test_prohibited_report_form_absent_across_all_pages(self) -> None:
        """Verify no interactive report form is present; explicit static notice provided."""
        pages = [
            ("metodo", self.metodo_html),
            ("fuentes", self.fuentes_html),
            ("correcciones", self.correcciones_html),
        ]

        for name, html in pages:
            # Check for forbidden form tags
            self.assertNotRegex(
                html,
                r"<\s*form\b",
                f"Page {name} must not contain any <form> tag",
            )
            self.assertNotRegex(
                html,
                r"<\s*input\b",
                f"Page {name} must not contain any <input> tag",
            )
            self.assertNotRegex(
                html,
                r"<\s*textarea\b",
                f"Page {name} must not contain any <textarea> tag",
            )
            self.assertNotRegex(
                html,
                r'<\s*button[^>]*type=[\'"]submit[\'"]',
                f"Page {name} must not contain submit buttons",
            )

            # Check for static contact notice
            self.assertIn("editorial@elecciones2026.es", html, f"Page {name} must reference editorial email")

        # In metodo, check explicit notice that interactive form is deferred
        self.assertIn("Avisos de errores y rectificaciones", self.metodo_html)
        self.assertIn("estará disponible más adelante", self.metodo_html)

    def test_mobile_responsive_css_and_touch_targets(self) -> None:
        """Verify CSS defines mobile cards stack, desktop table container, and min touch targets."""
        self.assertIn(".coverage-cards", self.css_content)
        self.assertIn(".coverage-card", self.css_content)
        self.assertIn(".coverage-table-container", self.css_content)
        self.assertIn(".update-stamp", self.css_content)
        self.assertIn(".update-date", self.css_content)

        # Table is hidden on mobile screens
        self.assertIsNotNone(
            re.search(r"\.coverage-table-container\s*\{[^}]*display:\s*none", self.css_content),
            "CSS must hide .coverage-table-container by default for mobile viewports",
        )

        # Table appears at desktop breakpoint (>= 760px)
        self.assertIsNotNone(
            re.search(r"@media\s*\(min-width:\s*760px\)", self.css_content),
            "CSS must include desktop media query (>= 760px)",
        )
        self.assertIsNotNone(
            re.search(r"\.coverage-table-container\s*\{[^}]*display:\s*block", self.css_content),
            "CSS must set display: block for .coverage-table-container on desktop",
        )

        # Verify touch target compliance (>= 44px)
        self.assertIn("min-height: var(--touch-target-comfortable)", self.css_content)

        # Verify hash and wrapping properties to avoid mobile horizontal overflow
        self.assertIn("word-break: break-all", self.css_content)

    def test_fresh_build_output_matches_requirements(self) -> None:
        """Verify running build_site generates compliant /metodo/, /fuentes/, /correcciones/ pages."""
        temp_dir = Path(tempfile.mkdtemp(prefix="elecciones_test_sources_"))
        try:
            build_res = build_site(
                root_dir=ROOT_DIR,
                output_dir=temp_dir,
                build_date=DEFAULT_BUILD_DATE,
            )

            dist_metodo = (temp_dir / "metodo" / "index.html").read_text(encoding="utf-8")
            dist_fuentes = (temp_dir / "fuentes" / "index.html").read_text(encoding="utf-8")
            dist_correcciones = (temp_dir / "correcciones" / "index.html").read_text(encoding="utf-8")

            # Check update date
            self.assertIn('class="update-stamp"', dist_metodo)
            self.assertIn(DEFAULT_BUILD_DATE, dist_metodo)

            # Check coverage cards
            self.assertIn('class="coverage-cards"', dist_metodo)
            self.assertIn('class="coverage-cards"', dist_fuentes)

            # Check no forms in dist output
            for name, html in [("metodo", dist_metodo), ("fuentes", dist_fuentes), ("correcciones", dist_correcciones)]:
                self.assertNotRegex(html, r"<\s*form\b", f"Built page {name} has form tag")
                self.assertNotRegex(html, r"<\s*input\b", f"Built page {name} has input tag")
                self.assertIn("editorial@elecciones2026.es", html)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_no_catalan_leakage_in_methodology_copy(self) -> None:
        """Verify Spanish methodology copy does not inadvertently leak Catalan words."""
        catalan_indicators = [
            r"\bhabitatge\b",
            r"\beducaci[oó]\b",
            r"\bsanitat\b",
            r"\bserveis\s+socials\b",
            r"\btreball\b",
            r"\bimmigraci[oó]\b",
            r"\bdrets\b",
            r"\bmetodologia\b",  # Spanish is metodología, not metodologia
        ]
        for name, html in [
            ("metodo", self.metodo_html),
            ("fuentes", self.fuentes_html),
            ("correcciones", self.correcciones_html),
        ]:
            text_only = re.sub(r"<[^>]+>", " ", html.lower())
            for pattern in catalan_indicators:
                match = re.search(pattern, text_only)
                self.assertIsNone(
                    match,
                    f"Possible Catalan leakage in {name}: found '{match.group(0) if match else ''}'",
                )


if __name__ == "__main__":
    unittest.main()
