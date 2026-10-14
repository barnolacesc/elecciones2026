"""Exercise the private provisional comparison and exploratory quiz in Chromium."""
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

    def end_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'")
        super().end_headers()


@unittest.skipUnless(os.environ.get('ELECTIONS_TEST_PROVISIONAL_BROWSER') == '1', 'Opt-in Chromium pilot test')
class ProvisionalBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.temp = tempfile.TemporaryDirectory(prefix='provisional-browser-')
        output = Path(cls.temp.name) / 'site'
        build_site(ROOT, output, election_id='es-gen-2023', quiz_mode='unavailable',
                   pilot_provisional=True, build_date='2026-10-14')
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

    def test_all_pairs_topics_and_quiz_sources(self):
        for width in (360, 390, 430):
            with self.subTest(width=width):
                context = self.browser.new_context(viewport={'width': width, 'height': 800}, has_touch=True)
                page = context.new_page()
                errors, requests = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: requests.append(request))
                page.goto(self.base + '/')
                page.locator('#pilot-topic').select_option('immigration')
                page.locator('#pilot-a').select_option('pnv')
                page.locator('#pilot-b').select_option('sumar')
                self.assertEqual(page.locator('#pilot-comparison .card').count(), 2)
                self.assertIn('page=10', page.locator('#pilot-comparison .card').first.locator('a').get_attribute('href'))
                self.assertIn('topic=immigration', page.url)
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                page.goto(self.base + '/cuestionario/')
                self.assertNotIn('PP:', page.locator('#pilot-quiz').inner_text())
                for _ in range(12):
                    page.locator('input[name="answer"][value="agree"]').check()
                    page.locator('#pilot-quiz button').click()
                self.assertEqual(page.locator('#pilot-results .card').count(), 12)
                self.assertIn('no son un porcentaje', page.locator('#pilot-results').inner_text())
                page.goto(self.base + '/fuentes/')
                self.assertIn('Fuentes del piloto', page.locator('h1').inner_text())
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                self.assertFalse(errors)
                self.assertTrue(all(request.url.startswith(self.base) for request in requests))
                context.close()


if __name__ == '__main__':
    unittest.main()
