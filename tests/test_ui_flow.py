"""Unit tests for Spanish home and one-topic/two-party selection flow (Package E2.2)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from elecciones2026.methodology import CORE_TOPIC_IDS, load_taxonomy
from elecciones2026.ui_flow import (
    validate_css_accessibility,
    validate_html_structure,
    validate_js_app,
    validate_selection,
    validate_ui_flow_files,
)


class TestUIFlow(unittest.TestCase):
    """Test suite for Spanish home, selection controls, accessibility, and zero horizontal overflow."""

    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.html_path = self.root / "site" / "index.html"
        self.css_path = self.root / "site" / "styles.css"
        self.js_path = self.root / "site" / "app.js"
        self.taxonomy_path = self.root / "content" / "taxonomy.json"
        self.taxonomy = load_taxonomy(self.taxonomy_path)

    def test_ui_flow_files_exist(self) -> None:
        """Verify all primary E2.2 files exist."""
        self.assertTrue(self.html_path.is_file(), f"Missing {self.html_path}")
        self.assertTrue(self.css_path.is_file(), f"Missing {self.css_path}")
        self.assertTrue(self.js_path.is_file(), f"Missing {self.js_path}")

    def test_full_ui_flow_validation_passes(self) -> None:
        """Verify aggregate validator passes without any errors."""
        result = validate_ui_flow_files(
            html_path=self.html_path,
            css_path=self.css_path,
            js_path=self.js_path,
            taxonomy_path=self.taxonomy_path,
        )
        self.assertTrue(result.valid, f"UI flow validation errors: {result.errors}")

    def test_spanish_language_and_no_catalan_leakage(self) -> None:
        """Verify artifact declares lang='es' and contains no accidental Catalan UI copy (Task 3.6)."""
        html = self.html_path.read_text(encoding="utf-8")
        self.assertIn('<html lang="es">', html)

        # Prohibit unintended Catalan words in public Spanish UI copy
        text_content = re.sub(r"<[^>]+>", " ", html.lower())
        catalan_indicators = [
            r"\bhabitatge\b",
            r"\beducaci[oó]\b",
            r"\bsanitat\b",
            r"\bserveis\s+socials\b",
            r"\btreball\b",
            r"\bimmigraci[oó]\b",
            r"\bdrets\b",
            r"\bm[eè]tode\b",
            r"\bfonts\b",
        ]
        for pattern in catalan_indicators:
            self.assertFalse(
                re.search(pattern, text_content),
                f"Found unintended Catalan copy in Spanish UI matching: '{pattern}'",
            )

    def test_topic_selector_contains_eight_core_topics(self) -> None:
        """Verify one-topic selector has all 8 core taxonomy topics (Task 3.2)."""
        html = self.html_path.read_text(encoding="utf-8")
        self.assertIn('id="topic-select"', html)

        for topic_id in CORE_TOPIC_IDS:
            self.assertIn(f'value="{topic_id}"', html, f"Missing topic '{topic_id}' in select options")

    def test_party_selectors_present_with_labels_and_alphabetical_order(self) -> None:
        """Verify two party selectors exist, with linked labels and alphabetical option ordering."""
        html = self.html_path.read_text(encoding="utf-8")

        self.assertIn('id="party-a-select"', html)
        self.assertIn('id="party-b-select"', html)
        self.assertIn('for="party-a-select"', html)
        self.assertIn('for="party-b-select"', html)

        # Extract party options from candidaturas group and verify alphabetical order
        for select_id in ["party-a-select", "party-b-select"]:
            match = re.search(
                rf'<select[^>]*id="{select_id}"[^>]*>(.*?)</select>',
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(match)
            select_content = match.group(1)

            optgroup_match = re.search(
                r'<optgroup[^>]*label="[^"]*(?:candidaturas|oficiales)[^"]*"[^>]*>(.*?)</optgroup>',
                select_content,
                re.DOTALL | re.IGNORECASE,
            )
            self.assertIsNotNone(optgroup_match)
            options = re.findall(r'<option[^>]*>(.*?)</option>', optgroup_match.group(1))
            texts = [re.sub(r"<.*?>", "", o).strip() for o in options]
            self.assertEqual(texts, sorted(texts, key=lambda s: s.lower()), f"Unsorted options in {select_id}")

    def test_selection_validation_logic(self) -> None:
        """Verify one-topic and two-party validation rules in Python model."""
        # 1. Identical parties must be rejected with descriptive Spanish error
        valid, err = validate_selection("housing", "pp", "pp", self.taxonomy)
        self.assertFalse(valid)
        self.assertIn("dos candidaturas distintas", err)

        # 2. Distinct parties must pass
        valid, err = validate_selection("housing", "pp", "psoe", self.taxonomy)
        self.assertTrue(valid)
        self.assertIsNone(err)

        # 3. Invalid topic must be rejected
        valid, err = validate_selection("invalid-topic", "pp", "psoe", self.taxonomy)
        self.assertFalse(valid)
        self.assertIn("Tema no válido", err)

        # 4. Empty party must be rejected
        valid, err = validate_selection("housing", "", "psoe", self.taxonomy)
        self.assertFalse(valid)

    def test_touch_target_sizes_meet_44px_requirement(self) -> None:
        """Verify touch targets meet WCAG 2.5.5 / 2.5.8 minimum 44px (and comfortable 48px)."""
        tokens_css = (self.root / "site" / "tokens" / "tokens.css").read_text(encoding="utf-8")
        self.assertIn("--touch-target-min: 44px", tokens_css)
        self.assertIn("--touch-target-comfortable: 48px", tokens_css)

        css = self.css_path.read_text(encoding="utf-8")
        # Selects, submit button, share button must have touch target heights >= 44px
        self.assertIn("min-height: var(--touch-target-comfortable)", css)
        self.assertIn("min-height: var(--touch-target-min)", css)

    def test_zero_horizontal_overflow_constraints(self) -> None:
        """Verify CSS contains zero horizontal overflow rules and mobile viewport baselines."""
        css = self.css_path.read_text(encoding="utf-8")

        # Global box-sizing reset
        self.assertIn("box-sizing: border-box", css)

        # Overflow containment
        self.assertIn("overflow-x: hidden", css)

        # Viewport target references
        self.assertIn("360px", css)
        self.assertIn("390px", css)
        self.assertIn("430px", css)

    def test_prohibitions_strictly_enforced(self) -> None:
        """Verify strict absence of accounts, logins, avatars, tracking, and fake verification."""
        html = self.html_path.read_text(encoding="utf-8").lower()
        js = self.js_path.read_text(encoding="utf-8").lower()

        # No user accounts or profiles
        self.assertNotIn("perfil", html)
        self.assertNotIn("avatar", html)
        self.assertNotIn("login", html)
        self.assertNotIn("mi cuenta", html)
        self.assertNotIn("iniciar sesión", html)

        # No fake verification claims
        self.assertNotIn("100% verificado", html)
        self.assertNotIn("100% oficial", html)
        self.assertNotIn("certificado oficial", html)

        # No telemetry or tracking in JS
        self.assertNotIn("cookie", js)
        self.assertNotIn("analytics", js)
        self.assertNotIn("fingerprint", js)

        # No external CDNs
        for bad in ["googleapis.com", "tailwindcss.com", "unpkg.com", "jsdelivr.net"]:
            self.assertNotIn(bad, html)

    def test_accessible_keyboard_and_error_flow(self) -> None:
        """Verify keyboard skip link, form live region, and aria-invalid attributes."""
        html = self.html_path.read_text(encoding="utf-8")

        # Skip link
        self.assertIn('class="skip-link"', html)
        self.assertIn('href="#contenido"', html)

        # Selection error live region
        self.assertIn('id="selection-error"', html)
        self.assertIn('role="alert"', html)
        self.assertIn('aria-live="assertive"', html)

        # Describedby connections
        self.assertIn('aria-describedby="selection-error"', html)

        # JS handles aria-invalid
        js = self.js_path.read_text(encoding="utf-8")
        self.assertIn("aria-invalid", js)
        self.assertIn("validateSelection", js)


if __name__ == "__main__":
    unittest.main()
