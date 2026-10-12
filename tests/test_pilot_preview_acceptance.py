"""E1.4 acceptance of the pending pilot, without real political approval.

The browser lane is explicit so ordinary unit runs need no browser installation.
Approved-path and hostile-record contracts stay in test_browser_publish_set.py.
"""
from functools import partial
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from urllib.parse import parse_qs, urlsplit

from elecciones2026.generator import build_site
from elecciones2026.mobile_accessibility import LAYOUT
from elecciones2026.schemas import load_statement

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://preview.example.test/pilot-2023'
TOPICS = ('housing', 'education', 'health-social-services')


class Metadata(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.canonicals = []
        self.social_urls = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'link' and values.get('rel') == 'canonical':
            self.canonicals.append(values.get('href'))
        if tag == 'meta' and values.get('property') == 'og:url':
            self.social_urls.append(values.get('content'))


class PilotArtifactTests(unittest.TestCase):
    def test_all_routes_have_pilot_metadata_and_exclude_withdrawn_quotes(self):
        with tempfile.TemporaryDirectory(prefix='pilot-acceptance-') as tmp:
            output = Path(tmp) / 'site'
            result = build_site(ROOT, output, election_id='es-gen-2023',
                                canonical_base=CANONICAL, build_date='2026-10-12')
            self.assertEqual((result.statements_count, result.relationships_count), (0, 0))
            quotes = [load_statement(path).quote for path in
                      (ROOT / 'content/examples/statements').glob('*2023*.json')]
            pages = list(output.rglob('*.html'))
            self.assertGreater(len(pages), 15)
            for path in pages:
                with self.subTest(route=path.relative_to(output)):
                    html = path.read_text()
                    route = '/' + path.relative_to(output).as_posix().removesuffix('index.html')
                    metadata = Metadata(html)
                    self.assertEqual(metadata.canonicals, [CANONICAL + route])
                    self.assertEqual(metadata.social_urls, metadata.canonicals)
                    self.assertIn('data-election="es-gen-2023"', html)
                    self.assertIn('ENSAYO PILOTO PRIVADO', html)
                    self.assertIn('Solo posiciones verificadas', html)
                    self.assertRegex(html, r'<title>[^<]*2023[^<]*</title>')
                    self.assertNotIn('Partido Ejemplo A', html)
                    for quote in quotes:
                        if quote:
                            self.assertNotIn(quote, html)
            self.assertFalse(list(output.rglob('*.pdf')))
            self.assertFalse(list(output.glob('quiz-data.*.js')))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def end_headers(self):
        # Match the application CSP, without claiming hosting authentication.
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; "
                         "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                         "connect-src 'self'; object-src 'none'; base-uri 'none'")
        super().end_headers()


@unittest.skipUnless(os.environ.get('ELECTIONS_TEST_PILOT_BROWSER') == '1',
                     'Opt-in Playwright pending 2023 acceptance')
class PilotBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.temporary = tempfile.TemporaryDirectory(prefix='pilot-browser-')
        output = Path(cls.temporary.name) / 'site'
        build_site(ROOT, output, election_id='es-gen-2023', build_date='2026-10-12')
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
        cls.temporary.cleanup()

    def test_pending_topics_keyboard_share_and_mobile_layout(self):
        from playwright.sync_api import expect
        for width in (360, 390, 430):
            with self.subTest(width=width):
                context = self.browser.new_context(viewport={'width': width, 'height': 844}, has_touch=True)
                context.add_init_script("""Object.defineProperty(navigator, 'share', {value: async data => {
                    window.sharedPreview = data;
                }});""")
                page = context.new_page()
                errors, requests = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: requests.append(request))
                try:
                    page.goto(self.base + '/')
                    page.keyboard.press('Tab')
                    self.assertTrue(page.locator('.skip-link').evaluate('(el) => el === document.activeElement'))
                    page.keyboard.press('Enter')
                    self.assertEqual(urlsplit(page.url).fragment, 'contenido')
                    for topic in TOPICS:
                        page.locator('#topic-select').select_option(topic)
                        page.locator('#compare-submit').focus()
                        page.keyboard.press('Enter')
                        expect(page.locator('#measures-container')).to_contain_text('Contenido pendiente de publicación')
                        self.assertEqual(page.locator('.measure-group').count(), 0)
                        self.assertEqual(page.locator('.btn-view-source').count(), 0)
                        self.assertIn('No implica apoyo ni oposición', page.locator('#measures-container').inner_text())
                        layout = page.evaluate(LAYOUT)
                        self.assertLessEqual(layout['scroll_width'], width)
                        for key in ('clipped', 'short_targets', 'small_statements', 'unlabeled_selects'):
                            self.assertFalse(layout[key], layout)
                        page.locator('#share-button').focus()
                        page.keyboard.press('Enter')
                        expect(page.locator('#share-feedback')).to_contain_text('Enlace compartido')
                        shared = page.evaluate('window.sharedPreview')
                        self.assertIn('2023', shared['title'])
                        self.assertEqual(parse_qs(urlsplit(shared['url']).query),
                                         {'topic': [topic], 'partyA': ['pp'], 'partyB': ['erc'],
                                          'election': ['es-gen-2023']})
                        page.goto(shared['url'])
                        self.assertEqual(page.locator('#topic-select').input_value(), topic)
                    page.locator('#party-b-select').select_option('pp')
                    expect(page.locator('#selection-error')).to_contain_text('dos candidaturas distintas')
                    self.assertEqual(page.locator('#party-b-select').get_attribute('aria-invalid'), 'true')
                    page.locator('#party-b-select').select_option('erc')
                    expect(page.locator('#selection-error')).to_have_text('')
                    self.assertFalse(errors, errors)
                    self.assertTrue(all(request.method == 'GET' for request in requests))
                    self.assertTrue(all(urlsplit(request.url).netloc == urlsplit(self.base).netloc for request in requests))
                    self.assertEqual(context.cookies(), [])
                    # The visual accent preference is permitted; comparison choices are not a profile.
                    self.assertEqual(page.evaluate('Object.keys(localStorage)'), ['elecciones2026_swiss_accent'])
                    self.assertEqual(page.evaluate("localStorage.getItem('elecciones2026_swiss_accent')"), 'monochrome')
                    self.assertEqual(page.evaluate('sessionStorage.length'), 0)
                finally:
                    context.close()

    def test_static_pilot_routes_remain_readable_without_script(self):
        context = self.browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        page = context.new_page()
        try:
            for route in ('/', '/metodo/', '/fuentes/', '/correcciones/', '/cuestionario/',
                          '/partidos/pp/', *(f'/temas/{topic}/' for topic in TOPICS)):
                with self.subTest(route=route):
                    page.goto(self.base + route)
                    self.assertIn('2023', page.title())
                    self.assertIn('Publicación pendiente', page.locator('.preview-banner').inner_text())
                    self.assertIn('Solo posiciones verificadas', page.locator('body > footer').inner_text())
                    self.assertGreater(len(page.locator('main').inner_text()), 40)
                    layout = page.evaluate(LAYOUT)
                    self.assertLessEqual(layout['scroll_width'], 390)
                    self.assertFalse(layout['clipped'], layout)
            page.goto(self.base + '/')
            self.assertIn('Contenido pendiente de publicación', page.locator('#measures-container').inner_text())
            page.goto(self.base + '/fuentes/')
            links = page.locator('a.source-citation').evaluate_all('(nodes) => nodes.map(n => ({href:n.href,rel:n.rel}))')
            self.assertTrue(links)
            self.assertTrue(all(link['href'].startswith('https://') and 'noopener' in link['rel'] for link in links))
        finally:
            context.close()

    def test_compact_header_and_native_menu_without_script(self):
        context = self.browser.new_context(java_script_enabled=False)
        try:
            for width in (360, 390, 430):
                with self.subTest(width=width):
                    page = context.new_page()
                    page.set_viewport_size({'width': width, 'height': 780})
                    page.goto(self.base + '/')
                    bounds = page.evaluate("""() => ({
                        header: document.querySelector('.topbar').getBoundingClientRect().bottom,
                        action: document.querySelector('.hero-actions').getBoundingClientRect().bottom
                    })""")
                    self.assertLessEqual(bounds['header'], 150)
                    self.assertLessEqual(bounds['action'], 580)
                    menu = page.locator('.site-menu')
                    self.assertFalse(menu.evaluate('(node) => node.open'))
                    page.locator('.menu-toggle').focus()
                    page.keyboard.press('Enter')
                    self.assertTrue(menu.evaluate('(node) => node.open'))
                    links = page.locator('.menu-links a')
                    self.assertEqual(links.count(), 5)
                    for link in links.all():
                        self.assertTrue(link.is_visible())
                        box = link.bounding_box()
                        self.assertGreaterEqual(box['height'], 44)
                        self.assertGreaterEqual(box['x'], 0)
                        self.assertLessEqual(box['x'] + box['width'], width)
                    links.filter(has_text='Fuentes').click()
                    self.assertTrue(page.url.endswith('/fuentes/'))
                    self.assertFalse(page.locator('.site-menu').evaluate('(node) => node.open'))
                    page.close()
        finally:
            context.close()

    def test_missing_bundle_and_foreign_selection_fail_closed(self):
        from playwright.sync_api import expect
        context = self.browser.new_context(viewport={'width': 390, 'height': 844})
        context.route('**/comparison-data.*.js', lambda route: route.abort())
        page = context.new_page()
        try:
            page.goto(self.base + '/?topic=education&partyA=partido-ejemplo-a&partyB=partido-ejemplo-b&election=es-gen-2026')
            expect(page.locator('#measures-container')).to_contain_text('Contenido pendiente de publicación')
            self.assertEqual(page.locator('.party-statement, .measure-group').count(), 0)
            self.assertEqual(page.locator('#party-a-select').input_value(), 'pp')
            self.assertEqual(page.locator('#party-b-select').input_value(), 'erc')
            page.locator('#compare-submit').click()
            self.assertEqual(parse_qs(urlsplit(page.url).query)['election'], ['es-gen-2023'])
        finally:
            context.close()
