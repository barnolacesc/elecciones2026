# P2 provisional source-index journey audit — 2026-10-24

**Package:** P2 / E2.4–E2.5, private 2023 pilot source-index journey. **Baseline:** `origin/main` `fe5e05e`. **Status:** reproducible implementation handoff, not source, editorial, accessibility, or release approval.

## Observed route and defect

The private `--pilot-provisional` build replaces the normal generated routes with `src/elecciones2026/provisional2023.py`. Its comparison cards use the position-specific `direct_url#page=<position page>`; that is the intended shape for a measure citation. The separate `/fuentes/` overview, however, builds a dictionary by party while iterating `data["positions"]`, so later positions overwrite earlier ones. It then calls the same position citation renderer for each party. Consequently each *document overview* link jumps to the final loaded measure's page, not to a document overview or a deliberately chosen cover/index. This selection depends on fixture ordering, not source metadata. It is not evidence that those pages or summaries have human approval.

At this baseline, the four overview links resolve to the last loaded pages: PP 75 (9 positions), ERC 20 (8), PNV 9 (9), and Sumar 129 (10). All four carry `#page=`. The page says “Los cuatro documentos originales usados en esta vista histórica” and presents a SHA-256 per card, but it does not explain why a document-level link opens that particular measure page. The exact measure-card citations should remain page-specific; the issue is the source-index link contract. No external PDF was fetched or inspected for this audit.

Reproduce with local fixture data, without network access or political answers:

```sh
PYTHONPATH=src python3 - <<'PY'
from html.parser import HTMLParser
from pathlib import Path
from elecciones2026.provisional2023 import load, sources

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href', '')
        if tag == 'a' and href.startswith('https://'):
            self.urls.append(href)

data = load(Path('.'))
links = Links()
links.feed(sources(data))
assert len(links.urls) == 4
for party in ('pp', 'erc', 'pnv', 'sumar'):
    positions = [item for item in data['positions'] if item['party'] == party]
    assert positions[-1]['url'] in links.urls
    print(party, len(positions), positions[-1]['page'])
PY
```

Reversing only `data["positions"]` changes the four overview hrefs while leaving the party set unchanged; this independent local assertion passed. The focused `test_provisional_2023.py` suite passed 9/9 under Python 3.11.2, and `git diff --check` passed. These checks do not establish browser/device behavior, source validity, or human approval.

The existing `tests/test_provisional_2023.py` checks that `/fuentes/` exists and that the comparison has source links; `tests/test_provisional_2023_browser.py` checks source hrefs on selected comparison cards and mobile overflow. Neither asserts the source-index destination contract. PR #135 adds comparison citation target geometry; it does not address overview target semantics. PR #133 edits this same Python renderer file for the home entry, and PR #134 edits the private pilot JavaScript. PR #131 audits the *normal generated* `/fuentes/` route, not this provisional source index. Implementing in the shared Python file before those PRs reconcile would overlap active work.

## Bounded acceptance handoff

1. For the private pilot's `/fuentes/` cards, derive one document-level destination per party from the registered 2023 source metadata, independent of the ordering of provisional measures. Label the destination according to the actual registered target; do not assume a PDF viewer will honor a page fragment. Keep each comparison/quiz measure citation tied to its own recorded page and locator.
2. Show the provisional/unreviewed and rights-pending boundary beside the source overview link. A registered URL and hash do not establish lawful reuse, exact printed-page correspondence, or approval. Do not change source, statement, rights, review, or publication records in this UX package.
3. Add an output-level regression that permutes fixture position order and verifies the four overview targets remain stable while measure citations retain their own pages. In a rendered 360/390/430 CSS-px journey, check home/deep comparison → source index → outbound target attributes and return navigation, keyboard focus, 44-px targets, and no horizontal overflow. Intercept outbound navigation in automation; separately record real-device and assistive-technology observations. Passing CI is not human review.

This audit adds no public artifact, political claim, PDF, approval, routing change, deployment, or merge. P0/P1 coverage and the real 2023 release gate remain separate.
