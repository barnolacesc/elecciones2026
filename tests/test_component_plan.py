"""Unit tests for accessible component plan and mobile wireframes validation."""

from __future__ import annotations

from pathlib import Path
import unittest

from elecciones2026.component_plan import (
    validate_component_plan_file,
    validate_component_plan_text,
)


class TestComponentPlan(unittest.TestCase):
    """Test suite for site/COMPONENT-PLAN.md and site/index.html conformity."""

    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.plan_path = self.root / "site" / "COMPONENT-PLAN.md"
        self.index_html_path = self.root / "site" / "index.html"
        self.stitch_review_path = self.root / "docs" / "STITCH-REVIEW.md"

    def test_component_plan_exists_and_passes_validation(self) -> None:
        """Verify COMPONENT-PLAN.md exists and passes all structural checks."""
        self.assertTrue(self.plan_path.is_file(), f"Missing file: {self.plan_path}")
        result = validate_component_plan_file(self.plan_path)
        self.assertTrue(result.valid, f"Component plan validation errors: {result.errors}")
        self.assertEqual(len(result.checked_viewports), 3)
        self.assertIn("360", result.checked_viewports)
        self.assertIn("390", result.checked_viewports)
        self.assertIn("430", result.checked_viewports)

    def test_phone_wireframes_detailed(self) -> None:
        """Verify wireframes include 360, 390, and 430 CSS px specifications."""
        content = self.plan_path.read_text(encoding="utf-8")
        self.assertIn("360 CSS px", content)
        self.assertIn("390 CSS px", content)
        self.assertIn("430 CSS px", content)
        self.assertIn("Content Width", content)
        self.assertIn("Touch Target Gap", content)

    def test_prohibitions_explicitly_stated(self) -> None:
        """Verify strict prohibitions on profile UI, fake verification, and report forms."""
        content = self.plan_path.read_text(encoding="utf-8").lower()
        self.assertIn("no profile ui", content)
        self.assertIn("100% verificado", content)
        self.assertIn("no fake report form", content)
        self.assertIn("no external cdn", content)

    def test_wcag_accessibility_criteria_covered(self) -> None:
        """Verify WCAG 2.2 AA accessibility audit criteria are documented."""
        content = self.plan_path.read_text(encoding="utf-8")
        self.assertIn("WCAG 2.2 Level AA", content)
        self.assertIn("1.4.3 Contrast", content)
        self.assertIn("1.4.10 Reflow", content)
        self.assertIn("2.1.1 Keyboard", content)
        self.assertIn("2.5.5 / 2.5.8 Target Size", content)

    def test_index_html_conforms_to_component_plan(self) -> None:
        """Verify site/index.html prototype adheres to component plan rules."""
        self.assertTrue(self.index_html_path.is_file(), f"Missing file: {self.index_html_path}")
        html = self.index_html_path.read_text(encoding="utf-8")

        # Spanish language declaration
        self.assertIn('<html lang="es">', html)

        # Responsive viewport meta tag
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', html)

        # Skip link
        self.assertIn('class="skip-link"', html)
        self.assertIn('href="#contenido"', html)

        # Prohibitions: No profile UI or account controls
        html_lower = html.lower()
        self.assertNotIn("perfil", html_lower)
        self.assertNotIn("cuenta", html_lower)
        self.assertNotIn("avatar", html_lower)
        self.assertNotIn("login", html_lower)

        # Prohibitions: No fake verification claims
        self.assertNotIn("100% verificado", html_lower)
        self.assertNotIn("100% oficial", html_lower)

        # Semantic landmarks
        self.assertIn("<header", html)
        self.assertIn("<main", html)
        self.assertIn("<footer", html)

    def test_stitch_review_references_component_plan(self) -> None:
        """Verify docs/STITCH-REVIEW.md references COMPONENT-PLAN.md and tokens."""
        self.assertTrue(self.stitch_review_path.is_file())
        review_content = self.stitch_review_path.read_text(encoding="utf-8")
        self.assertIn("COMPONENT-PLAN.md", review_content)
        self.assertIn("tokens.json", review_content)
        self.assertIn("tokens.css", review_content)
        self.assertIn("360, 390, and 430 CSS px", review_content)


if __name__ == "__main__":
    unittest.main()
