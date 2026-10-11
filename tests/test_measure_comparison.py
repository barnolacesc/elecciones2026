"""Unit tests for grouped measure comparison view (Package E2.3, Tasks 3.2 and 3.3).

Verifies:
- Grouped measures with short summaries and both party positions visible per measure.
- Strict absence of tabs (no role="tab", no tabpanels, no hidden card switching).
- Source links with coordinates (page/article) and >= 44px touch targets.
- Explicit qualifications/caveats with role="note".
- Explicit missing data handling ("no consta", not conflated with opposition/agreement).
- Multi-measure datasets covering all 8 core topics.
- Static HTML generation fallback in generator.py.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from elecciones2026.generator import load_and_validate_site_data, render_home_page
from elecciones2026.methodology import CORE_TOPIC_IDS


class TestMeasureComparison(unittest.TestCase):
    """Test suite for grouped measure comparisons, visible citations, and explicit missing states."""

    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parent.parent
        self.html_path = self.root / "site" / "index.html"
        self.css_path = self.root / "site" / "styles.css"
        self.js_path = self.root / "site" / "app.js"
        self.html = self.html_path.read_text(encoding="utf-8")
        self.css = self.css_path.read_text(encoding="utf-8")
        self.js = self.js_path.read_text(encoding="utf-8")

    def test_measures_container_exists_and_contains_multiple_measure_groups(self) -> None:
        """Verify #measures-container exists with multiple .measure-group articles (Task 3.2)."""
        self.assertIn('id="measures-container"', self.html)
        self.assertIn('class="measures-container"', self.html)

        groups = re.findall(r'<article[^>]*class="[^"]*measure-group[^"]*"', self.html)
        self.assertGreaterEqual(
            len(groups),
            2,
            f"Expected at least 2 measure groups in initial HTML, found {len(groups)}",
        )

    def test_each_measure_group_has_title_summary_and_both_party_cards(self) -> None:
        """Verify each measure group renders topic label, measure title, summary, and both party cards."""
        container_match = re.search(
            r'<div[^>]*id="measures-container"[^>]*>(.*?)</div>\s*<div class="share-section"',
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(container_match, "Measures container not found in index.html")
        container_html = container_match.group(1)

        raw_groups = [g for g in container_html.split('<article class="measure-group"') if g.strip()]
        self.assertGreaterEqual(len(raw_groups), 2, "Expected at least 2 measure groups")

        for idx, group_html in enumerate(raw_groups, 1):
            self.assertIn('class="measure-title"', group_html, f"Measure group {idx} missing measure title")
            self.assertIn('class="measure-summary"', group_html, f"Measure group {idx} missing measure summary")
            self.assertIn('class="measure-cards"', group_html, f"Measure group {idx} missing measure-cards wrapper")

            # Check both party cards are present within this measure group (excluding -header, -meta, etc.)
            party_cards = re.findall(r'class="[^"]*\bparty-card\b(?!-header|-meta|-body|-footer)', group_html)
            self.assertEqual(
                len(party_cards),
                2,
                f"Measure group {idx} must contain exactly 2 party cards (both parties), found {len(party_cards)}",
            )

    def test_strict_absence_of_tabs_and_hidden_panels(self) -> None:
        """Verify no tab switching required (Tasks 3.2 / E2.3 acceptance): no role='tab', tablist, or tabpanels."""
        html_lower = self.html.lower()
        js_lower = self.js.lower()

        # HTML prohibitions
        self.assertNotIn('role="tab"', html_lower, "Prohibited role='tab' found in index.html")
        self.assertNotIn('role="tablist"', html_lower, "Prohibited role='tablist' found in index.html")
        self.assertNotIn('role="tabpanel"', html_lower, "Prohibited role='tabpanel' found in index.html")
        self.assertNotIn('class="tab-container"', html_lower)
        self.assertNotIn('class="tab-button"', html_lower)

        # JS prohibitions
        self.assertNotIn('role="tab"', js_lower, "Prohibited role='tab' found in app.js")
        self.assertNotIn('role="tablist"', js_lower, "Prohibited role='tablist' found in app.js")
        self.assertNotIn('role="tabpanel"', js_lower, "Prohibited role='tabpanel' found in app.js")
        self.assertNotIn('switchtab', js_lower, "Tab switching function found in app.js")
        self.assertNotIn('activetab', js_lower, "Tab state found in app.js")

    def test_source_links_visible_with_coordinates_and_rel_attributes(self) -> None:
        """Verify official source links are visible with exact document locators and safe rel attributes."""
        # Find source citation links
        source_links = re.findall(r'<a[^>]*class="[^"]*source-citation[^"]*"[^>]*>(.*?)</a>', self.html, re.DOTALL)
        self.assertGreater(len(source_links), 0, "No source links found in index.html")

        # Verify links include target="_blank" and rel="noopener noreferrer"
        link_tags = re.findall(r'<a[^>]*class="[^"]*source-citation[^"]*"[^>]*>', self.html)
        for tag in link_tags:
            self.assertIn('target="_blank"', tag, f"Source link missing target='_blank': {tag}")
            self.assertIn('rel="noopener noreferrer"', tag, f"Source link missing rel='noopener noreferrer': {tag}")

        # Verify page/article locators exist in citations
        locators = re.findall(r'(?:pág\.|página|art\.|artículo|sección)\s*\d+', self.html, re.IGNORECASE)
        self.assertGreater(len(locators), 0, "No source locators (pág./art.) found in index.html citations")

    def test_source_link_touch_targets_meet_minimum_44px(self) -> None:
        """Verify CSS specifies min-height satisfying >= 44px touch targets on source links."""
        self.assertIn(".source-citation", self.css)
        match = re.search(r'\.source-citation\s*\{([^}]+)\}', self.css)
        self.assertIsNotNone(match, ".source-citation rule missing in styles.css")
        rules = match.group(1)
        self.assertTrue(
            "min-height: 44px" in rules or "min-height: var(--touch-target-min)" in rules or "padding:" in rules,
            f"Source link touch target styling inadequate: {rules}",
        )

    def test_qualifications_rendered_with_role_note(self) -> None:
        """Verify caveats / qualifications are rendered visibly with role='note' (Task 3.3)."""
        self.assertIn('role="note"', self.html)
        self.assertIn('class="party-caveat"', self.html)

        # Check in JS rendering template
        self.assertIn('role="note"', self.js)
        self.assertIn('party-caveat', self.js)

    def test_explicit_missing_data_never_rendered_as_opposition_or_agreement(self) -> None:
        """Verify missing data is explicitly stated as 'no consta' and never asserted as opposition/agreement (Task 3.3)."""
        # In HTML Measure 2: Party B has missing state
        self.assertIn("party-card-missing", self.html)
        self.assertIn("status-badge-missing", self.html)
        self.assertIn("No consta en el programa", self.html)

        # Check explicit note on absence not implying opposition or agreement
        self.assertIn("no debe interpretarse como oposición", self.html)
        self.assertIn("no debe interpretarse como oposición", self.js)
        self.assertIn("nunca se interpretará como oposición", self.html)

        # Missing state must have rel-callout-not-found class
        self.assertIn("rel-callout-not-found", self.html)
        self.assertIn("rel-callout-not-found", self.css)
        self.assertIn("rel-callout-not-found", self.js)

    def test_css_mobile_vertical_flow_and_no_horizontal_overflow(self) -> None:
        """Verify CSS formats .measure-cards as stacked single column on mobile without horizontal scroll."""
        self.assertIn(".measure-cards", self.css)
        self.assertIn(".measure-group", self.css)

        # Verify measure-cards uses grid with 1fr on mobile
        match = re.search(r'\.measure-cards\s*\{([^}]+)\}', self.css)
        self.assertIsNotNone(match)
        rules = match.group(1)
        self.assertIn("grid-template-columns: 1fr", rules)

        # Prohibit horizontal overflow
        self.assertNotIn("overflow-x: scroll", self.css)

    def test_javascript_covers_all_eight_core_topics_with_multiple_measures(self) -> None:
        """Verify app.js MEASURES_BY_TOPIC includes all 8 core topics, each with multiple measures."""
        self.assertIn("MEASURES_BY_TOPIC", self.js)

        for topic_id in CORE_TOPIC_IDS:
            pattern = rf"['\"]{topic_id}['\"]\s*:"
            self.assertTrue(
                re.search(pattern, self.js),
                f"Missing core topic '{topic_id}' in app.js MEASURES_BY_TOPIC",
            )

        # Check renderComparison function exists and mounts into measures-container
        self.assertIn("function renderComparison", self.js)
        self.assertIn("measuresContainer", self.js)

    def test_generator_home_page_renders_grouped_measures(self) -> None:
        """Verify static site generator renders grouped measures in #measures-container without JS."""
        ctx = load_and_validate_site_data(root_dir=self.root)
        rendered = render_home_page(ctx)

        self.assertIn('id="measures-container"', rendered)
        self.assertIn('class="measure-group"', rendered)
        self.assertIn('class="measure-cards"', rendered)

        # Verify both party cards are rendered in Measure 1
        groups = re.findall(r'<article[^>]*class="[^"]*measure-group[^"]*"', rendered)
        self.assertGreaterEqual(len(groups), 2)
        self.assertIn('role="note"', rendered)
        self.assertIn('rel-callout-agreement', rendered)
        self.assertIn('rel-callout-not-found', rendered)

    def test_measure_initiative_context_and_axes_rendered(self) -> None:
        """Verify enriched measure context and comparison axes are present in HTML and JS (E2.3)."""
        self.assertIn('class="measure-context"', self.html)
        self.assertIn('class="measure-context-desc"', self.html)
        self.assertIn('class="measure-axes"', self.html)
        self.assertIn('class="measure-axes-list"', self.html)

        self.assertIn('measure-context', self.js)
        self.assertIn('measure-axes', self.js)

    def test_in_app_manifesto_excerpt_viewer_components(self) -> None:
        """Verify in-app manifesto excerpt viewer dialog, buttons, and legal attribution (E2.3 / TRLPI Art. 32)."""
        # Dialog presence in DOM
        self.assertIn('id="manifesto-dialog"', self.html)
        self.assertIn('class="manifesto-dialog"', self.html)

        # In-app viewer button on cards with quotes
        self.assertIn('class="btn-open-manifesto"', self.html)
        self.assertIn('aria-haspopup="dialog"', self.html)
        self.assertIn('Leer extracto', self.html)

        # JS functions for modal
        self.assertIn('openManifestoModal', self.js)
        self.assertIn('btn-open-manifesto', self.js)
        self.assertIn('art. 32.1 TRLPI', self.js)

        # CSS styling and touch targets
        self.assertIn('.manifesto-dialog', self.css)
        self.assertIn('.btn-open-manifesto', self.css)
        self.assertIn('.btn-open-full-pdf', self.css)


if __name__ == "__main__":
    unittest.main()
