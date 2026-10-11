"""E10.3 renderer tests; publication gates are mocked only for synthetic builds."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import test_budget as fixtures
from elecciones2026 import budget_view
from elecciones2026.budget import BudgetError, load_bundle
from elecciones2026.generator import build_site

ROOT = Path(__file__).resolve().parents[1]


class BudgetViewTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BudgetTests()
        self.fixture.setUp()
        self.bundle = self.fixture.create()
        self.manifest, self.payload = load_bundle(self.bundle, require_publication=False)
        self.labels = {item['topic_id']: item['label_es'] for item in self.payload['mapping.json']['mappings']}

    def tearDown(self):
        self.fixture.tearDown()

    def build_fixture(self, target):
        # Fixtures cannot satisfy real publication approvals. Test rendering after
        # a mocked validation boundary; real gate rejection is tested separately.
        with patch('elecciones2026.budget.load_bundle', return_value=(self.manifest, self.payload)), \
             patch('elecciones2026.budget.copy_reviewed_bundle'):
            return build_site(ROOT, target, budget_bundle=self.bundle)

    def test_policy_section_and_table_figures_have_source_locators(self):
        html = budget_view.render_budget_content(self.payload, self.manifest, self.bundle.name, self.labels)
        self.assertIn('PGE 2023: presupuesto aprobado', html)
        self.assertIn('CSV: fila 9, columna Total', html)
        self.assertIn('CSV: fila 9, columna Secc. 01', html)
        self.assertIn('No disponible en la celda de origen', html)
        self.assertIn('scope="row"', html)
        self.assertIn('scope="col"', html)
        self.assertIn('No todas las secciones son ministerios', html)
        self.assertIn('No son datos de ejecución', html)
        self.assertIn('no indican el coste', html)
        self.assertIn('sin redondear', html)
        self.assertIn(self.manifest['dataset_version'], html)
        self.assertEqual(html.count('class="budget-policy"'), 2)

    def test_projection_is_scoped_and_no_inferred_topic_sum(self):
        for topic in self.labels:
            projection = budget_view.topic_projection(self.payload, self.manifest, topic)
            self.assertEqual(projection['topic_id'], topic)
            self.assertEqual([row['code'] for row in projection['rows']], ['11'])
            self.assertNotIn('cells', projection)
            self.assertNotIn('topic_amount', projection)
            self.assertLess(len(json.dumps(projection).encode()), 16384)
        changed = copy.deepcopy(self.payload)
        changed['mapping.json']['mappings'][0].update(coverage_state='not_available', row_refs=[])
        gap = budget_view.topic_projection(changed, self.manifest, self.labels.__iter__().__next__())
        self.assertEqual(gap['rows'], [])
        self.assertIn('No hay una cifra oficial separable', budget_view.render_context(gap, './'))

    def test_hostile_labels_and_locators_are_escaped(self):
        payload = copy.deepcopy(self.payload)
        for margin in payload['values.json']['margins']:
            margin['label_es'] = '<img src=x onerror=alert(1)>'
        html = budget_view.render_budget_content(payload, self.manifest, self.bundle.name, self.labels)
        self.assertNotIn('<img', html)
        self.assertIn('&lt;img', html)
        projection = budget_view.topic_projection(payload, self.manifest, 'housing')
        self.assertNotIn('<img', budget_view.render_context(projection, './'))

    def test_tiny_share_remains_positive(self):
        self.assertEqual(budget_view.percentage('0.01', '100000'), '< 0,01 %')
        self.assertEqual(budget_view.percentage('0', '100000'), '0,00 %')
        self.assertEqual(budget_view.percentage(None, '100000'), 'No disponible')

    def test_build_routes_context_and_determinism(self):
        first = self.build_fixture(self.fixture.root / 'first')
        second = self.build_fixture(self.fixture.root / 'second')
        self.assertEqual(first.file_hashes, second.file_hashes)
        home = (first.output_dir / 'index.html').read_text()
        self.assertEqual(home.count('id="budget-context"'), 1)
        self.assertIn('budget-context.js', home)
        self.assertNotIn('values.json', home)
        budget_html = (first.output_dir / 'presupuestos/2023/index.html').read_text()
        self.assertIn('https://elecciones2026.es/presupuestos/2023/', budget_html)
        self.assertIn('/presupuestos/2023/', (first.output_dir / 'sitemap.xml').read_text())
        for topic in self.labels:
            page = (first.output_dir / f'temas/{topic}/index.html').read_text()
            self.assertEqual(page.count('class="budget-context"'), 1)
            projections = list(first.output_dir.glob(f'static/budget-topics/*/{topic}.json'))
            self.assertEqual(len(projections), 1)

        original_projection = next(first.output_dir.glob('static/budget-topics/*')).name
        self.payload['mapping.json']['mappings'][0]['coverage_note_es'] += ' Nota corregida.'
        corrected = self.build_fixture(self.fixture.root / 'corrected')
        self.assertNotEqual(next(corrected.output_dir.glob('static/budget-topics/*')).name, original_projection)

    def test_default_build_has_no_budget_requests_or_routes(self):
        result = build_site(ROOT, self.fixture.root / 'default')
        home = (result.output_dir / 'index.html').read_text()
        self.assertNotIn('budget-context.js', home)
        self.assertNotIn('budget.css', home)
        self.assertFalse((result.output_dir / 'presupuestos').exists())

    def test_stylesheet_corrections_cannot_reuse_an_immutable_url(self):
        site_dir = self.fixture.root / 'styles'
        site_dir.mkdir()
        stylesheet = site_dir / 'budget.css'
        stylesheet.write_text('.budget-chart-key { display: grid; }')
        original = budget_view.stylesheet_path(site_dir)
        output = self.fixture.root / 'assets'
        budget_view.copy_stylesheet(site_dir, output)
        self.assertEqual((output / original).read_bytes(), stylesheet.read_bytes())
        stylesheet.write_text('.budget-chart-key { display: block; }')
        corrected = budget_view.stylesheet_path(site_dir)
        self.assertNotEqual(original, corrected)
        budget_view.copy_stylesheet(site_dir, output)
        self.assertTrue((output / original).exists())
        self.assertEqual((output / corrected).read_bytes(), stylesheet.read_bytes())
        result = self.build_fixture(self.fixture.root / 'styled-build')
        path = budget_view.stylesheet_path(ROOT / 'site')
        self.assertTrue((result.output_dir / path).is_file())
        for page in ('index.html', 'presupuestos/2023/index.html'):
            self.assertIn(path, (result.output_dir / page).read_text())

    def test_private_preview_rejects_repository_and_existing_output(self):
        with self.assertRaises(BudgetError):
            budget_view.preview_bundle(self.bundle, ROOT / 'build/budget-preview')
        output = self.fixture.root / 'preview'
        page = budget_view.preview_bundle(self.bundle, output)
        self.assertIn('BORRADOR PRIVADO', page.read_text())
        self.assertIn('noindex,nofollow', page.read_text())
        self.assertNotIn('Comparar propuestas sobre este tema', page.read_text())
        self.assertFalse(list(output.rglob('values.json')))
        self.assertTrue((output / budget_view.stylesheet_path(ROOT / 'site')).is_file())
        charts = list(output.glob('static/budget-charts/*/grafico.svg'))
        self.assertEqual(len(charts), 1)
        self.assertIn(charts[0].relative_to(output).as_posix(), page.read_text())
        with self.assertRaises(BudgetError):
            budget_view.preview_bundle(self.bundle, output)


if __name__ == '__main__':
    unittest.main()
