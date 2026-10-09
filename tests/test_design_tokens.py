"""Unit tests for local design tokens and WCAG contrast validation."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from elecciones2026.tokens import (
    contrast_ratio,
    relative_luminance,
    srgb_to_linear,
    validate_tokens_data,
    validate_tokens_file,
)


class TestDesignTokens(unittest.TestCase):
    """Test suite for site/tokens/tokens.json and site/tokens/tokens.css."""

    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.tokens_json_path = self.root / "site" / "tokens" / "tokens.json"
        self.tokens_css_path = self.root / "site" / "tokens" / "tokens.css"
        self.styles_css_path = self.root / "site" / "styles.css"

    def test_tokens_json_exists_and_valid(self) -> None:
        """Verify tokens.json exists and passes all schema and value checks."""
        self.assertTrue(self.tokens_json_path.is_file(), f"Missing file: {self.tokens_json_path}")
        result = validate_tokens_file(self.tokens_json_path)
        self.assertTrue(result.valid, f"Validation errors: {result.errors}")
        self.assertGreater(result.token_count, 40)
        self.assertGreaterEqual(len(result.contrast_checks), 10)

    def test_wcag_contrast_ratios(self) -> None:
        """Verify all text/background pairs exceed WCAG 2.2 AA (4.5:1) requirement."""
        result = validate_tokens_file(self.tokens_json_path)
        for chk in result.contrast_checks:
            self.assertTrue(
                chk["passed"],
                f"Contrast check failed for '{chk['pair']}': {chk['ratio']}:1 < {chk['min_ratio']}:1",
            )
            self.assertGreaterEqual(chk["ratio"], 4.5)

    def test_touch_target_constraint(self) -> None:
        """Verify touchTargetMin meets WCAG 2.5.5 minimum 44px requirement."""
        with open(self.tokens_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        val = data["tokens"]["size"]["touchTargetMin"]["value"]
        self.assertEqual(val, "44px")

    def test_breakpoints_include_required_viewports(self) -> None:
        """Verify breakpoints include 360, 390, 430, and 760 px."""
        with open(self.tokens_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        bps = data["tokens"]["breakpoint"]
        self.assertEqual(bps["mobileCompact"]["value"], "360px")
        self.assertEqual(bps["mobileBaseline"]["value"], "390px")
        self.assertEqual(bps["mobileLarge"]["value"], "430px")
        self.assertEqual(bps["desktop"]["value"], "760px")

    def test_forbidden_tokens_prohibited(self) -> None:
        """Verify forbidden keys (profile, login, fake verification) are absent from tokens."""
        with open(self.tokens_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def assert_no_forbidden(d: dict, prefix: str = "") -> None:
            for k, v in d.items():
                k_lower = k.lower()
                self.assertNotIn("profile", k_lower, f"Forbidden key found: {prefix}{k}")
                self.assertNotIn("avatar", k_lower, f"Forbidden key found: {prefix}{k}")
                self.assertNotIn("hundredpercentverified", k_lower, f"Forbidden key found: {prefix}{k}")
                if isinstance(v, dict):
                    assert_no_forbidden(v, f"{prefix}{k}.")

        assert_no_forbidden(data["tokens"])

    def test_no_external_cdn_dependencies(self) -> None:
        """Verify no external CDN imports exist in tokens.css or styles.css."""
        for css_file in [self.tokens_css_path, self.styles_css_path]:
            self.assertTrue(css_file.is_file(), f"Missing file: {css_file}")
            content = css_file.read_text(encoding="utf-8")
            self.assertNotIn("googleapis.com", content)
            self.assertNotIn("tailwindcss.com", content)
            self.assertNotIn("http://", content)
            # Only local imports allowed
            for line in content.splitlines():
                if line.strip().startswith("@import"):
                    self.assertNotIn("https://", line, f"External @import detected: {line}")

    def test_tokens_css_contains_core_variables(self) -> None:
        """Verify tokens.css declares essential CSS variables."""
        content = self.tokens_css_path.read_text(encoding="utf-8")
        expected_vars = [
            "--color-bg-canvas",
            "--color-bg-surface",
            "--color-text-primary",
            "--color-text-secondary",
            "--color-party-a-bg",
            "--color-party-b-bg",
            "--touch-target-min",
            "--touch-target-comfortable",
            "--focus-ring",
            "--breakpoint-mobile-compact",
            "--breakpoint-mobile-baseline",
            "--breakpoint-mobile-large",
        ]
        for var in expected_vars:
            self.assertIn(var, content, f"Missing CSS variable: {var}")

    def test_luminance_and_contrast_helpers(self) -> None:
        """Test mathematical accuracy of luminance and contrast calculations."""
        # Pure black and pure white
        self.assertAlmostEqual(relative_luminance("#000000"), 0.0, places=4)
        self.assertAlmostEqual(relative_luminance("#ffffff"), 1.0, places=4)
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21.0, places=1)
        self.assertAlmostEqual(contrast_ratio("#ffffff", "#ffffff"), 1.0, places=1)

    def test_invalid_tokens_rejected(self) -> None:
        """Verify validator flags invalid tokens properly."""
        bad_data = {
            "tokens": {
                "color": {
                    "text": {"primary": {"value": "#ffffff"}},
                    "bg": {"canvas": {"value": "#ffffff"}},
                },
                "size": {"touchTargetMin": {"value": "32px"}},
                "userProfile": {"avatar": {"value": "url"}},
            }
        }
        res = validate_tokens_data(bad_data)
        self.assertFalse(res.valid)
        error_str = " ".join(res.errors)
        self.assertIn("32px", error_str)
        self.assertIn("Forbidden", error_str)


if __name__ == "__main__":
    unittest.main()
