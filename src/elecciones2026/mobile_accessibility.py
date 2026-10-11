"""Rendered mobile regression checks (E2.5), not a WCAG conformance audit.

Requires the development-only Playwright dependency and Chromium. Human reader
and participant checks remain separate from these automated observations.
"""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
from threading import Thread

from elecciones2026.generator import build_site

VIEWPORTS = (360, 390, 430)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


# Inspect element rectangles as well as scrollWidth: overflow-x:hidden must not
# conceal clipped content from the regression check.
LAYOUT = """() => {
  const visible = el => {
    const r = el.getBoundingClientRect();
    return r.width > 1 && r.height > 1 && getComputedStyle(el).visibility !== 'hidden';
  };
  const controls = [...document.querySelectorAll('a[href],button,select,input')]
    .filter(visible).filter(el => !el.classList.contains('skip-link'));
  const clipped = [...document.querySelectorAll('main *,header *,footer *')]
    .filter(visible).filter(el => !el.classList.contains('sr-only'))
    .filter(el => { const r=el.getBoundingClientRect(); return r.left < -1 || r.right > innerWidth+1; });
  return {
    width: innerWidth,
    scroll_width: document.documentElement.scrollWidth,
    clipped: clipped.map(el => el.tagName+'.'+el.className),
    short_targets: controls.filter(el => el.getBoundingClientRect().height < 43.5)
      .map(el => ({text:el.textContent.trim(),height:el.getBoundingClientRect().height})),
    small_statements: [...document.querySelectorAll('.party-statement')]
      .filter(el => parseFloat(getComputedStyle(el).fontSize) < 16).length,
    unlabeled_selects: [...document.querySelectorAll('select')]
      .filter(el => !el.labels.length).length,
    language: document.documentElement.lang
  };
}"""


def run_audit(root: Path) -> dict:
    from playwright.sync_api import sync_playwright

    observations = []
    failures = []
    tasks = []

    def check(name, passed, details=None):
        tasks.append({'check': name, 'passed': bool(passed), 'details': details})
        if not passed:
            failures.append(name)

    with tempfile.TemporaryDirectory(prefix='e2-5-') as temporary:
        output = Path(temporary)
        build_site(root, output)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(output)))
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                for width in VIEWPORTS:
                    context = browser.new_context(viewport={'width': width, 'height': 844}, has_touch=True)
                    page = context.new_page()
                    page_errors = []
                    page.on('pageerror', lambda error: page_errors.append(str(error)))
                    page.goto(base + '/')
                    page.keyboard.press('Tab')
                    check(f'{width}: skip link first', page.locator('.skip-link').evaluate('(el)=>el===document.activeElement'))
                    page.keyboard.press('Enter')
                    check(f'{width}: skip destination', page.evaluate('location.hash') == '#contenido')
                    page.locator('#topic-select').focus()
                    page.keyboard.press('e')
                    page.keyboard.press('Tab')
                    check(f'{width}: keyboard topic selection', page.locator('#topic-select').input_value() == 'education', page.locator('#topic-select').input_value())
                    page.locator('#topic-select').select_option('housing')
                    page.locator('#party-a-select').select_option('partido-ejemplo-a')
                    page.locator('#party-b-select').select_option('partido-ejemplo-a')
                    page.locator('#compare-submit').click()
                    check(f'{width}: duplicate error', 'dos candidaturas distintas' in page.locator('#selection-error').inner_text(), page.evaluate("({a:document.querySelector('#party-a-select').value,b:document.querySelector('#party-b-select').value,error:document.querySelector('#selection-error').textContent})"))
                    check(f'{width}: invalid state', page.locator('#party-b-select').get_attribute('aria-invalid') == 'true')
                    page.locator('#party-b-select').select_option('partido-ejemplo-b')
                    check(f'{width}: recovery', page.locator('#selection-error').inner_text() == '' and page.locator('#party-b-select').get_attribute('aria-invalid') is None)
                    page.locator('#compare-submit').focus()
                    page.keyboard.press('Enter')
                    page.locator('#compare-submit').tap()
                    check(f'{width}: touch submission', 'topic=housing' in page.url)
                    groups = page.locator('.measure-group')
                    check(f'{width}: comparison present', groups.count() > 0)
                    for i in range(groups.count()):
                        cards = groups.nth(i).locator('.party-card')
                        # Read both rectangles in one browser task: smooth scrolling
                        # can change viewport coordinates between separate calls.
                        boxes = cards.evaluate_all("""elements => elements.map(el => {
                          const r = el.getBoundingClientRect();
                          return {y: r.y, height: r.height, width: r.width};
                        })""")
                        check(f'{width}: stacked measure {i}', len(boxes) == 2
                              and all(box['width'] > 0 and box['height'] > 0 for box in boxes)
                              and boxes[1]['y'] >= boxes[0]['y'] + boxes[0]['height'] - 1,
                              boxes)
                    # Traverse actual keyboard order and inspect computed focus styling.
                    page.locator('#compare-submit').focus()
                    reached = False
                    for _ in range(80):
                        page.keyboard.press('Tab')
                        focused = page.evaluate("""() => {const el=document.activeElement,s=getComputedStyle(el);return {
                          citation:el.matches('a.source-citation'),
                          outline:s.outlineStyle!=='none' && parseFloat(s.outlineWidth)>=2,
                          notice:el.textContent.includes('ventana nueva')};}""")
                        if focused['citation']:
                            reached = True
                            check(f'{width}: citation focus ring', focused['outline'])
                            check(f'{width}: citation reader notice', focused['notice'])
                            break
                    check(f'{width}: citation reached by Tab', reached)
                    citation = page.locator('a.source-citation').first
                    check(f'{width}: accessible source name', citation.count() > 0 and 'Fuente:' in citation.aria_snapshot())
                    page.locator('#party-b-select').select_option('partido-ejemplo-d')
                    check(f'{width}: missing coverage', page.locator('.party-card-missing').count() > 0)
                    for route in ('/', '/metodo/', '/fuentes/', '/temas/housing/'):
                        page.goto(base + route)
                        result = page.evaluate(LAYOUT)
                        observations.append({'route': route, **result})
                        check(f'{width}: layout {route}', result['scroll_width'] <= width and not result['clipped'] and not result['short_targets'] and not result['small_statements'] and not result['unlabeled_selects'] and result['language'] == 'es', result)
                    check(f'{width}: no browser script errors', not page_errors, page_errors)
                    context.close()

                # Browser-observed navigation and paint timings, with cache disabled.
                # Local HTTP has no real DNS/TLS/edge/origin cost. No TTI is inferred.
                context = browser.new_context(viewport={'width': 390, 'height': 844})
                page = context.new_page()
                cdp = context.new_cdp_session(page)
                cdp.send('Network.enable')
                cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
                cdp.send('Network.emulateNetworkConditions', {
                    'offline': False, 'latency': 150,
                    'downloadThroughput': 1600 * 1000 / 8,
                    'uploadThroughput': 750 * 1000 / 8,
                })
                timing = []
                for _ in range(3):
                    page.goto(base + '/', wait_until='networkidle')
                    timing.append(page.evaluate("""() => {const n=performance.getEntriesByType('navigation')[0];return {
                      response_start_ms:n.responseStart,
                      dom_content_loaded_ms:n.domContentLoadedEventEnd,
                      load_ms:n.loadEventEnd,
                      fcp_ms:performance.getEntriesByName('first-contentful-paint')[0]?.startTime ?? null
                    };}"""))
                browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    return {
        'viewports': list(VIEWPORTS), 'checks': tasks, 'layouts': observations,
        'automated_checks_passed': sum(t['passed'] for t in tasks),
        'automated_checks_total': len(tasks), 'failures': failures,
        'network': {'latency_ms': 150, 'download_kbps': 1600, 'cache': 'disabled', 'samples': timing},
        'limits': ['Chromium emulation; not physical iOS/Android devices.',
                   'Accessibility names and keyboard checks do not replace VoiceOver/TalkBack review.',
                   'Automated task outcomes are not participant usability success rates.',
                   'Local HTTP timing excludes production DNS, TLS, edge and origin behavior.'],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root-dir', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = run_audit(args.root_dir.resolve())
    serialized = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding='utf-8')
    print(f"Mobile checks: {report['automated_checks_passed']}/{report['automated_checks_total']}")
    for failure in report['failures']:
        print(f'FAIL: {failure}')
    return 1 if report['failures'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
