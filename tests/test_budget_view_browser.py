"""E10.3 opt-in rendered checks with synthetic figures and mocked review gates."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from time import monotonic
from threading import Thread
import unittest

import test_budget_view as fixtures


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def end_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'")
        super().end_headers()


@unittest.skipUnless(os.environ.get('ELECTIONS_TEST_BUDGET_BROWSER') == '1', 'Opt-in Playwright budget checks')
class BudgetBrowserTests(unittest.TestCase):
    def test_color_comparison_scale_without_script(self):
        from playwright.sync_api import sync_playwright
        from elecciones2026 import budget_chart
        import shutil
        fixture = fixtures.BudgetViewTests()
        fixture.setUp()
        output = fixture.fixture.root / 'comparison'
        output.mkdir()
        template = budget_chart.policies(fixture.payload)[0]
        fixture.payload['values.json']['margins'] = [dict(template, code=code, label_es=label, amount_thousand_eur=amount)
            for code, label, amount in [('21', 'PENSIONES', '40000.00'), ('31', 'SANIDAD', '2000.01'), ('32', 'EDUCACIÓN', '1000.02')]]
        fixture.payload['measurement.json']['denominator_amount_thousand_eur'] = '43000.03'
        content = budget_chart.overview(fixture.payload, './fixture.svg')
        (output / 'index.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1"><title>Private synthetic fixture</title>'
            '<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="budget.css">'
            f'<main class="budget-page">{content}</main></html>')
        for name in ('styles.css', 'budget.css'):
            shutil.copy2(fixtures.ROOT / 'site' / name, output / name)
        shutil.copytree(fixtures.ROOT / 'site/tokens', output / 'tokens')
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(output)))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                for width in (360, 390, 430):
                    page = browser.new_page(viewport={'width': width, 'height': 844}, java_script_enabled=False)
                    page.goto(f'http://127.0.0.1:{server.server_port}/')
                    self.assertIn('7,50 %', page.locator('.budget-comparison').inner_text())
                    self.assertIn('No representan todo el gasto público', page.locator('.budget-comparison').inner_text())
                    self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                    widths = page.locator('.budget-comparison-track').evaluate_all('(tracks) => tracks.map(t => Array.from(t.children).reduce((sum,n)=>sum+n.getBoundingClientRect().width,0))')
                    self.assertAlmostEqual(widths[-1] / widths[0], .07500075, delta=.001)
                    self.assertEqual(page.locator('.budget-chart-swatch').count(), 3)
                    self.assertEqual(page.locator('.budget-map rect').first.get_attribute('fill'), budget_chart.policy_color('21'))
                    page.close()
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            fixture.tearDown()

    def test_image_download_native_share_cancel_and_failure(self):
        from playwright.sync_api import sync_playwright, expect
        fixture = fixtures.BudgetViewTests()
        fixture.setUp()
        output = fixture.fixture.root / 'site'
        fixture.build_fixture(output)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(output)))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                page = browser.new_page(viewport={'width': 390, 'height': 844})
                page.set_default_timeout(10000)
                page.add_init_script("""Object.defineProperty(navigator, 'canShare', {value: () => !window.unsupportedShare});
                Object.defineProperty(navigator, 'share', {value: async data => {
                  if(window.cancelShare) throw new DOMException('Canceled', 'AbortError');
                  window.sharedImage = {name:data.files[0].name, type:data.files[0].type, size:data.files[0].size};
                }});""")
                requested = []
                page.on('request', lambda request: requested.append(request.url))
                page.goto(f'http://127.0.0.1:{server.server_port}/presupuestos/2023/')
                self.assertFalse(page.locator('.budget-expanded').evaluate('(node) => node.open'))
                self.assertTrue(page.locator('.budget-map').is_visible())
                self.assertFalse(any(url.endswith('/grafico.svg') for url in requested))
                with page.expect_download() as download_info:
                    page.click('#budget-chart-save')
                download = download_info.value
                self.assertEqual(download.suggested_filename, 'pge-2023.png')
                from pathlib import Path
                self.assertEqual(Path(download.path()).read_bytes()[:8], b'\x89PNG\r\n\x1a\n')
                page.click('#budget-chart-share')
                expect(page.locator('#budget-chart-feedback')).to_have_text('Se ha compartido la imagen.')
                self.assertEqual(page.evaluate('window.sharedImage.type'), 'image/png')
                self.assertGreater(page.evaluate('window.sharedImage.size'), 1000)
                downloads = []
                page.on('download', lambda download: downloads.append(download))
                page.evaluate('window.cancelShare = true')
                page.click('#budget-chart-share')
                expect(page.locator('#budget-chart-share')).to_be_enabled()
                self.assertEqual(page.locator('#budget-chart-feedback').inner_text(), '')
                self.assertEqual(downloads, [])
                page.evaluate('window.unsupportedShare = true')
                with page.expect_download() as fallback:
                    page.click('#budget-chart-share')
                self.assertEqual(fallback.value.suggested_filename, 'pge-2023.png')
                expect(page.locator('#budget-chart-feedback')).to_contain_text('Imagen descargada')
                page.reload()
                page.route('**/grafico.svg', lambda route: route.fulfill(status=503, body='unavailable'))
                page.click('#budget-chart-save')
                expect(page.locator('#budget-chart-feedback')).to_contain_text('No se pudo')
                self.assertTrue(page.locator('.budget-map').is_visible())
                self.assertFalse(page.locator('#budget-chart-save').is_disabled())
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            fixture.tearDown()

    def test_mobile_context_network_and_keyboard(self):
        from playwright.sync_api import sync_playwright, expect
        fixture = fixtures.BudgetViewTests()
        fixture.setUp()
        # Stress wrapping independently of the official labels and approval state.
        for margin in fixture.payload['values.json']['margins']:
            if margin['kind'] == 'policy':
                margin['label_es'] += ' · ' + 'Descripción administrativa extensa ' * 8 + 'X' * 120
        output = fixture.fixture.root / 'candidate'
        fixture.build_fixture(output)
        from elecciones2026.generator import build_site
        baseline = fixture.fixture.root / 'baseline'
        build_site(fixtures.ROOT, baseline)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(fixture.fixture.root)))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        report = {'fixture_only': True, 'observations': [], 'network': [], 'human_review': 'pending'}
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                for width in (360, 390, 430):
                    page = browser.new_page(viewport={'width': width, 'height': 844})
                    page.set_default_timeout(10000)
                    requests = []
                    page.on('request', lambda request: requests.append(request.url))
                    page.goto(base + '/candidate/presupuestos/2023/')
                    self.assertEqual(page.locator('.budget-chart-key li').first.evaluate('(node) => getComputedStyle(node).display'), 'grid')
                    self.assertLessEqual(page.locator('.budget-map svg').bounding_box()['width'], width)
                    page.locator('summary').first.focus()
                    page.keyboard.press('Enter')
                    self.assertTrue(page.locator('details').first.evaluate('(node) => node.open'))
                    for details in page.locator('details').all():
                        details.evaluate('(node) => node.open = true')
                    for summary in page.locator('summary').all():
                        self.assertGreaterEqual(summary.bounding_box()['height'], 44)
                    overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth')
                    self.assertFalse(overflow)
                    self.assertEqual(page.locator('table[role="table"]').count(), 2)
                    self.assertEqual(page.get_by_role('columnheader').count(), 8)
                    self.assertEqual(page.get_by_role('rowheader').count(), 4)
                    page.add_style_tag(content='meter { display: none; }')
                    self.assertIn('millones de euros', page.locator('.budget-figure').first.inner_text())
                    report['observations'].append({'width': width, 'overflow': overflow, 'summary_min_height': 44,
                                                   'tables': 2, 'keyboard_disclosure': True})
                    page.goto(base + '/candidate/?topic=housing&partyA=partido-ejemplo-a&partyB=partido-ejemplo-b')
                    original = page.locator('#budget-context').inner_text()
                    before = len([url for url in requests if 'budget-topics/' in url])
                    page.select_option('#party-a-select', 'partido-ejemplo-b')
                    self.assertTrue(page.locator('#budget-context').evaluate('(node) => node.hidden'))
                    page.select_option('#party-b-select', 'partido-ejemplo-a')
                    self.assertEqual(page.locator('#budget-context').inner_text(), original)
                    self.assertEqual(len([url for url in requests if 'budget-topics/' in url]), before)
                    page.select_option('#topic-select', 'education')
                    expect(page.locator('#budget-context')).to_have_attribute('data-topic', 'education')
                    self.assertEqual(len([url for url in requests if 'budget-topics/' in url]), before + 1)
                    self.assertEqual(page.locator('#budget-context').count(), 1)
                    self.assertFalse(any('/static/budget/' in url or 'values.json' in url or '.zip' in url for url in requests))
                    page.route('**/health-social-services.json', lambda route: route.fulfill(status=503, body='unavailable'))
                    page.select_option('#topic-select', 'health-social-services')
                    expect(page.locator('#budget-context')).to_contain_text('no está disponible')
                    self.assertGreater(page.locator('#measures-container').inner_text().__len__(), 0)
                    self.assertNotIn('Descripción administrativa extensa', page.locator('#budget-context').inner_text())
                    page.close()
                # Static no-script readability includes cells, unavailable states, and denominator.
                context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
                page = context.new_page()
                page.goto(base + '/candidate/presupuestos/2023/')
                page.locator('.budget-expanded > summary').click()
                self.assertIn('sin redondear', page.locator('.budget-notes').inner_text())
                self.assertGreater(page.locator('.budget-policy').count(), 0)
                context.close()
                # Compare fresh initial navigations without a bulk data request.
                for name in ('baseline', 'candidate'):
                    routes = {'home': '/', 'topic': '/temas/education/',
                              'comparison': '/?topic=education&partyA=partido-ejemplo-a&partyB=partido-ejemplo-b'}
                    for view, route in routes.items():
                        context = browser.new_context(viewport={'width': 390, 'height': 844})
                        page = context.new_page()
                        session = context.new_cdp_session(page)
                        session.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150,
                                     'downloadThroughput': 200000, 'uploadThroughput': 93750})
                        responses = []
                        page.on('response', lambda response: responses.append(response))
                        started = monotonic()
                        page.goto(base + '/' + name + route, wait_until='networkidle')
                        elapsed = round((monotonic() - started) * 1000)
                        records = [{'path': response.url.split(base)[-1], 'bytes': len(response.body())} for response in responses]
                        self.assertFalse(any('/static/budget/' in item['path'] for item in records))
                        self.assertFalse(any('/budget-charts/' in item['path'] for item in records))
                        projections = [item for item in records if '/budget-topics/' in item['path']]
                        self.assertEqual(len(projections), 1 if name == 'candidate' and view == 'comparison' else 0)
                        if projections:
                            self.assertTrue(projections[0]['path'].endswith('/education.json'))
                            self.assertLessEqual(projections[0]['bytes'], 16384)
                        report['network'].append({'build': name, 'view': view, 'requests': len(records),
                                                  'response_bytes': sum(item['bytes'] for item in records),
                                                  'single_navigation_ms': elapsed, 'latency_ms': 150,
                                                  'download_bytes_per_second': 200000, 'resources': records})
                        context.close()
                browser.close()
            target = fixtures.ROOT / 'build/budget-view-e10-3.json'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(report, indent=2) + '\n')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            fixture.tearDown()


if __name__ == '__main__':
    unittest.main()
