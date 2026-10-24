# E2.2 / P2 — private 2023 home entry, 2026-10-23

## Baseline and boundary

At `fe5e05e` (`origin/main`), the `--pilot-provisional` build overwrites the normal generated home in `src/elecciones2026/generator.py` with `src/elecciones2026/provisional2023.py:comparison` (`generator.py:2847-2849`). That private home made the *unreviewed exploratory questionnaire* its only hero action; the topic/party selectors immediately below had no linked entry target. This conflicted with the 2023-first comparator flow in `docs/PRODUCT-ROADMAP-2023-2026.md` P2/P3. The provisional warning and source citations were already present. This package does not change the default reviewed-data home, the questionnaire, political content, source rights, or publication state.

## Change and evidence

The private provisional hero now leads to a named topic/two-candidature selector target. A secondary route opens the pilot source inventory. The existing provisional warning precedes both actions, and the questionnaire remains available through navigation but is not the primary home action. The target heading can receive fragment focus. Existing `.button` and `.button-secondary` styles already specify a minimum 44 CSS-px height; no new styling or political wording was introduced.

Local command: `PYTHONPATH=src python3 -m unittest discover -s tests -p test_provisional_2023.py -v` — 9/9 passed with Python 3.11.2. `git diff --check` passed. Source inspection verified the CTA href has a unique matching heading ID and the sources link is relative to the private root. No browser or physical-phone run was performed; 360/390/430-px touch, keyboard fragment focus, and screen-reader behavior remain for E2.5 human/device review. CI is not editorial approval.

## Coordination and gate

Open PRs #125/#128 edit the normal comparator, styling, sharing and the shared MVP task record; #101 edits the normal generator; #129 edits the quiz. This package changes none of those files. Reconcile this evidence into `tasks.md` after those PRs resolve; do not mark E2.5 or G5 complete. Private provisional measures remain unreviewed and must not be published as verified comparisons.
