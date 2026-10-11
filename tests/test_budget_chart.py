"""E10.3 proportional overview and standalone share-image contracts."""
import copy
from decimal import Decimal
import unittest
import xml.etree.ElementTree as ET

import test_budget_view as fixtures
from elecciones2026 import budget_chart
from elecciones2026.budget import BudgetError


class BudgetChartTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BudgetViewTests()
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.tearDown()

    def test_area_is_proportional_to_unrounded_official_margins(self):
        rows = budget_chart.policies(self.fixture.payload)
        rectangles = budget_chart.layout(rows, 360, 280)
        total = sum(Decimal(row['amount_thousand_eur']) for row in rows)
        self.assertEqual(len(rectangles), len(rows))
        self.assertAlmostEqual(sum(w*h for _, _, _, w, h in rectangles), 360*280, places=6)
        for row, x, y, width, height in rectangles:
            self.assertGreaterEqual(x, 0)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(x+width, 360+1e-7)
            self.assertLessEqual(y+height, 280+1e-7)
            self.assertAlmostEqual(width*height/(360*280), float(Decimal(row['amount_thousand_eur'])/total), places=10)
        with_zero = rows + [dict(rows[0], code='99', amount_thousand_eur='0')]
        self.assertEqual(len(budget_chart.layout(with_zero, 360, 280)), len(rows))

    def test_image_is_deterministic_inert_and_source_bearing(self):
        args = (self.fixture.payload, self.fixture.manifest, self.fixture.bundle.name)
        image = budget_chart.share_svg(*args)
        self.assertEqual(image, budget_chart.share_svg(*args))
        root = ET.fromstring(image)
        self.assertEqual(root.attrib['width'], '1080')
        self.assertTrue(all(node.tag.split('}')[-1] in {'svg','g','title','desc','rect','text'} for node in root.iter()))
        for expected in ('2023', 'No son datos de ejecución', self.fixture.bundle.name,
                         self.fixture.manifest['dataset_version'], 'capítulos 1–8', 'No es todo el gasto público'):
            self.assertIn(expected, image)
        self.assertIn('https://www.sepg.pap.hacienda.gob.es/', image)
        for row in budget_chart.policies(self.fixture.payload):
            self.assertIn(row['label_es'], image)
        self.assertNotIn('BORRADOR PRIVADO', image)
        self.assertIn('BORRADOR PRIVADO', budget_chart.share_svg(*args, preview=True))

    def test_chart_uses_every_policy_and_not_overlapping_topic_mappings(self):
        original = budget_chart.overview(self.fixture.payload, './chart.svg')
        changed = copy.deepcopy(self.fixture.payload)
        changed['mapping.json']['mappings'] = []
        self.assertEqual(original, budget_chart.overview(changed, './chart.svg'))
        for row in budget_chart.policies(changed):
            self.assertIn(row['code'], original)
        self.assertIn('presupuesto', original)
        self.assertIn('no gasto ejecutado', original)
        self.assertIn('Compartir gráfico', original)

    def test_hostile_labels_are_inert_and_oversized_images_are_rejected(self):
        payload = copy.deepcopy(self.fixture.payload)
        payload['values.json']['margins'][0]['label_es'] = '<script>alert(1)</script>'
        image = budget_chart.share_svg(payload, self.fixture.manifest, self.fixture.bundle.name)
        self.assertNotIn('<script>', image)
        ET.fromstring(image)
        payload['values.json']['margins'][0]['label_es'] = 'oversized label ' * 5000
        with self.assertRaises(BudgetError):
            budget_chart.share_svg(payload, self.fixture.manifest, self.fixture.bundle.name)


if __name__ == '__main__':
    unittest.main()
