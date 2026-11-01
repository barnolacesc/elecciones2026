"""Check the generated comparison site's reduced-motion scroll behavior."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from elecciones2026.generator import build_site


ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@unittest.skipUnless(os.environ.get('ELECTIONS_TEST_REDUCED_MOTION_BROWSER') == '1', 'Opt-in Chromium reduced-motion test')
class ReducedMotionBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright

        cls.temp = tempfile.TemporaryDirectory(prefix='reduced-motion-')
        output = Path(cls.temp.name) / 'site'
        build_site(ROOT, output, election_id='es-gen-2023', build_date='2026-10-29')
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(output)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temp.cleanup()

    def test_comparison_routes_respect_reduced_motion_at_phone_widths(self):
        for width in (360, 390, 430):
            for path in ('/', '/temas/', '/fuentes/'):
                with self.subTest(width=width, path=path):
                    context = self.browser.new_context(viewport={'width': width, 'height': 800}, reduced_motion='reduce')
                    page = context.new_page()
                    page.goto(self.base + path)
                    self.assertEqual(page.evaluate('getComputedStyle(document.documentElement).scrollBehavior'), 'auto')
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    context.close()

    def test_default_motion_setting_retains_existing_behavior(self):
        context = self.browser.new_context(viewport={'width': 390, 'height': 800}, reduced_motion='no-preference')
        page = context.new_page()
        page.goto(self.base + '/')
        self.assertEqual(page.evaluate('getComputedStyle(document.documentElement).scrollBehavior'), 'smooth')
        context.close()
