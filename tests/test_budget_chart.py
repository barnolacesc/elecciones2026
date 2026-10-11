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
            self.assertIn(row['label_es'].capitalize(), image)
        self.assertNotIn('BORRADOR PRIVADO', image)
        self.assertIn('BORRADOR PRIVADO', budget_chart.share_svg(*args, preview=True))

    def test_chart_uses_every_policy_and_not_overlapping_topic_mappings(self):
        original = budget_chart.overview(self.fixture.payload, './chart.svg')
        changed = copy.deepcopy(self.fixture.payload)
        changed['mapping.json']['mappings'] = []
        self.assertEqual(original, budget_chart.overview(changed, './chart.svg'))
        for row in budget_chart.policies(changed):
            self.assertIn(row['label_es'].capitalize(), original)
        self.assertNotIn('budget-chart-code', original)
        self.assertNotIn('100 €', original)
        self.assertIn('M€', original)
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

    def test_tile_labels_use_percentages_and_real_amounts_without_codes(self):
        rows = [{'code': '94', 'label_es': 'TRANSFERENCIAS A OTRAS ADMINISTRACIONES PÚBLICAS',
                 'amount_thousand_eur': '100'}]
        small = ET.fromstring('<svg>' + budget_chart.draw_tiles(rows, '100', 80, 60) + '</svg>')
        labels = [node.text for node in small.iter('text')]
        self.assertEqual(labels, ['100,00 %', '0,10 M€'])
        large = ET.fromstring('<svg>' + budget_chart.draw_tiles(rows, '100', 360, 280) + '</svg>')
        labels = [node.text for node in large.iter('text')]
        self.assertEqual(' '.join(labels[:-2]), rows[0]['label_es'].capitalize())
        self.assertEqual(labels[-2:], ['100,00 %', '0,10 M€'])

    def test_forty_percent_policy_occupies_forty_percent_of_total_area(self):
        rows = [{'code': '21', 'label_es': 'PENSIONES', 'amount_thousand_eur': '40000'},
                {'code': '94', 'label_es': 'TRANSFERENCIAS', 'amount_thousand_eur': '35000'},
                {'code': '95', 'label_es': 'DEUDA PÚBLICA', 'amount_thousand_eur': '25000'}]
        for width, height in ((360, 280), (1000, 620)):
            rectangles = budget_chart.layout(rows, width, height)
            self.assertAlmostEqual(rectangles[0][3] * rectangles[0][4] / (width * height), .4)
            self.assertAlmostEqual(sum(w*h for _, _, _, w, h in rectangles), width*height)
            plot = ET.fromstring('<svg>' + budget_chart.draw_tiles(rows, '100000', width, height) + '</svg>')
            first_text = [node.text for node in plot.find('g').iter('text')]
            self.assertIn('40,00 %', first_text)
            self.assertIn('40,00 M€', first_text)
        self.assertEqual(budget_chart.percentage('0.01', '100000'), '< 0,01 %')
        self.assertEqual(budget_chart.amount_label('0.01'), '< 0,01 M€')


if __name__ == '__main__':
    unittest.main()
