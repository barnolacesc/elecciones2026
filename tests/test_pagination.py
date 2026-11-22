import os
import re
import unittest
import tempfile
import shutil
from pathlib import Path
from elecciones2026.generator import (
    SiteContext,
    build_site,
    load_and_validate_site_data,
    render_topic_detail,
    render_topic_index,
    render_party_index,
    render_party_detail,
    render_sources_page,
    render_corrections_page,
    verify_determinism,
)

ROOT_DIR = Path(__file__).resolve().parent.parent


class TestPagination(unittest.TestCase):
    """Test suite for site-wide pagination components and behavior (WCAG 2.2 AA)."""

    def setUp(self) -> None:
        self.css_path = ROOT_DIR / "site" / "styles.css"
        self.pagination_js_path = ROOT_DIR / "site" / "pagination.js"
        self.app_js_path = ROOT_DIR / "site" / "app.js"
        self.css = self.css_path.read_text(encoding="utf-8")
        self.pagination_js = self.pagination_js_path.read_text(encoding="utf-8")
        self.app_js = self.app_js_path.read_text(encoding="utf-8")

    def test_pagination_css_classes_and_tokens(self) -> None:
        """Verify CSS contains accessible pagination styles using local design tokens."""
        self.assertIn(".pagination-nav", self.css)
        self.assertIn(".pagination-controls", self.css)
        self.assertIn(".pagination-btn", self.css)
        self.assertIn(".pagination-info", self.css)
        self.assertIn(".pagination-ellipsis", self.css)

        # Must enforce minimum touch target >= 44px
        self.assertIn("min-height: var(--touch-target-min)", self.css)
        self.assertIn("min-width: var(--touch-target-min)", self.css)

        # Must support focus ring for keyboard navigation
        self.assertIn("box-shadow: var(--focus-ring)", self.css)
        self.assertIn(":focus-visible", self.css)

        # Must style active page and disabled states
        self.assertIn('[aria-current="page"]', self.css)
        self.assertIn('[aria-disabled="true"]', self.css)

    def test_strict_absence_of_tabs_in_pagination(self) -> None:
        """Verify pagination does NOT use prohibited tab semantics (role=tab, tablist, tabpanel)."""
        pagination_lower = self.pagination_js.lower()
        self.assertNotIn('role="tab"', pagination_lower)
        self.assertNotIn('role="tablist"', pagination_lower)
        self.assertNotIn('role="tabpanel"', pagination_lower)
        self.assertNotIn("switchtab", pagination_lower)
        self.assertNotIn("activetab", pagination_lower)

    def test_pagination_js_structure_and_exports(self) -> None:
        """Verify pagination.js exports EleccionesPagination with paginate and initAll."""
        self.assertIn("window.EleccionesPagination", self.pagination_js)
        self.assertIn("paginate:", self.pagination_js)
        self.assertIn("initAll:", self.pagination_js)
        self.assertIn("aria-label", self.pagination_js)
        self.assertIn("aria-live", self.pagination_js)
        self.assertIn("aria-current", self.pagination_js)

    def test_comparator_pagination_in_app_js(self) -> None:
        """Verify app.js includes comparator pagination with configurable page size and controls."""
        self.assertIn("COMPARATOR_PAGE_SIZE", self.app_js)
        self.assertIn("comparisonPage", self.app_js)
        self.assertIn("renderPaginationControlsHtml", self.app_js)
        self.assertIn("data-comparison-page", self.app_js)
        self.assertIn('aria-label="Paginación de ', self.app_js)

    def test_generator_renders_pagination_script_in_pages(self) -> None:
        """Verify generator includes pagination.js in base template."""
        ctx = load_and_validate_site_data(root_dir=ROOT_DIR)
        topic = ctx.taxonomy.topics[0]
        topic_html = render_topic_detail(ctx, topic)
        self.assertIn("pagination.js", topic_html)

        topics_html = render_topic_index(ctx)
        self.assertIn("pagination.js", topics_html)
        self.assertIn("data-paginate", topics_html)

        party = list(ctx.parties.values())[0]
        party_html = render_party_detail(ctx, party)
        self.assertIn("pagination.js", party_html)
        self.assertIn("proposals-list", party_html)

        parties_html = render_party_index(ctx)
        self.assertIn("pagination.js", parties_html)
        self.assertIn("data-paginate", parties_html)

        sources_html = render_sources_page(ctx)
        self.assertIn("pagination.js", sources_html)
        self.assertIn("data-paginate", sources_html)

        corrections_html = render_corrections_page(ctx)
        self.assertIn("pagination.js", corrections_html)
        self.assertIn("corrections-list", corrections_html)

    def test_build_site_copies_pagination_asset_and_preserves_determinism(self) -> None:
        """Verify build_site copies pagination.js and repeat builds are bit-for-bit identical."""
        temp_dir = Path(tempfile.mkdtemp(prefix="pagination_test_"))
        try:
            dir1 = temp_dir / "run1"
            dir2 = temp_dir / "run2"

            res1 = build_site(root_dir=ROOT_DIR, output_dir=dir1, build_date="2026-10-09")
            res2 = build_site(root_dir=ROOT_DIR, output_dir=dir2, build_date="2026-10-09")

            self.assertIn("pagination.js", res1.files_written)
            self.assertIn("pagination.js", res2.files_written)
            self.assertEqual(res1.file_hashes["pagination.js"], res2.file_hashes["pagination.js"])
            self.assertEqual(res1.files_written, res2.files_written)

            # Ensure every single file hash matches between runs
            for path in res1.files_written:
                self.assertEqual(res1.file_hashes[path], res2.file_hashes[path])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_crawlability_preserved_without_javascript(self) -> None:
        """Verify that all claims, cards, and source links remain directly in the HTML for non-JS scrapers."""
        ctx = load_and_validate_site_data(root_dir=ROOT_DIR)
        topic = ctx.taxonomy.topics[0]
        topic_html = render_topic_detail(ctx, topic)

        # Claims and quotes must be directly in HTML
        self.assertIn("party-card", topic_html)
        self.assertIn("party-statement", topic_html)
        self.assertIn("source-citation", topic_html)


if __name__ == "__main__":
    unittest.main()
