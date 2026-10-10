"""Generated-artifact sharing contract for E2.6."""

from pathlib import Path
import tempfile
import unittest

from elecciones2026.generator import build_site


class TestSharingArtifact(unittest.TestCase):
    def test_share_controls_and_assets_survive_both_election_builds(self):
        root = Path(__file__).resolve().parent.parent
        for election in ('es-gen-2026', 'es-gen-2023'):
            with self.subTest(election=election), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp)
                build_site(root_dir=root, output_dir=output,
                           content_dir=root / 'content', election_id=election,
                           build_date='2026-10-10')
                self.assertEqual((output / 'sharing.js').read_bytes(),
                                 (root / 'site/sharing.js').read_bytes())
                pages = [output / 'index.html', *output.glob('temas/*/index.html')]
                self.assertEqual(len(pages), 9)
                for page in pages:
                    html = page.read_text()
                    self.assertEqual(html.count('id="share-button"'), 1, page)
                    self.assertEqual(html.count('id="copy-link-button"'), 1, page)
                    self.assertIn('id="share-fallback" hidden', html)
                    self.assertIn('for="share-link"', html)
                    self.assertIn('type="url" readonly', html)
                    self.assertIn('role="status" aria-live="polite"', html)
                    self.assertIn(f'data-election="{election}"', html)
                    self.assertIn('rel="canonical"', html)
                    self.assertIn('sharing.js" defer', html)
                    self.assertRegex(html, r'<time\b[^>]*datetime=')
                home = pages[0].read_text()
                self.assertLess(home.index('sharing.js"'), home.index('app.js"'))
