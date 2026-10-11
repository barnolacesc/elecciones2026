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

    def test_font_shrinks_to_keep_complete_names_and_figures(self):
        lines, size = budget_chart.fit_tile_label('Servicios de carácter general', '5,34 %',
                                                 '25.969,49 M€', 80, 90, 13, 8)
        self.assertLess(size, 13)
        self.assertGreaterEqual(size, 8)
        self.assertEqual(' '.join(lines).split(' 5,34 %')[0], 'Servicios de carácter general')
        self.assertIn('25.969,49 M€', ' '.join(lines))
        self.assertEqual(budget_chart.fit_tile_label('Small', '0,01 %', '0,01 M€', 8, 8, 13, 8)[0], [])

    def test_smaller_areas_receive_smaller_type_without_changing_geometry(self):
        rows = [{'code': '11', 'label_es': 'LARGE', 'amount_thousand_eur': '60000'},
                {'code': '12', 'label_es': 'SMALL', 'amount_thousand_eur': '30000'},
                {'code': '13', 'label_es': 'TINY', 'amount_thousand_eur': '10000'}]
        plot = ET.fromstring('<svg>' + budget_chart.draw_tiles(rows, '100000', 360, 280) + '</svg>')
        sizes = [float(group.find('text').attrib['font-size']) for group in plot.findall('g')]
        self.assertGreater(sizes[0], sizes[1])
        self.assertGreater(sizes[1], sizes[2])
        self.assertGreaterEqual(min(sizes), 8)
        for group, (_, x, y, width, height) in zip(plot.findall('g'), budget_chart.layout(rows, 360, 280)):
            rect = group.find('rect')
            for key, expected in zip(('x', 'y', 'width', 'height'), (x, y, width, height)):
                self.assertAlmostEqual(float(rect.attrib[key]), expected, places=3)

    def test_policy_colors_are_stable_distinct_and_contrast_with_white(self):
        self.assertEqual(len(set(budget_chart.POLICY_PALETTE)), len(budget_chart.POLICY_CODES))
        for color in budget_chart.POLICY_PALETTE:
            rgb = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
            linear = [value/12.92 if value <= .04045 else ((value+.055)/1.055)**2.4 for value in rgb]
            luminance = .2126*linear[0] + .7152*linear[1] + .0722*linear[2]
            self.assertGreaterEqual(1.05 / (luminance + .05), 4.5)
        rows = budget_chart.policies(self.fixture.payload)
        def colors(order):
            plot = ET.fromstring('<svg>' + budget_chart.draw_tiles(order, '0.03', 360, 280) + '</svg>')
            return {group.find('title').text: group.find('rect').attrib['fill'] for group in plot.findall('g')}
        self.assertEqual(colors(rows), colors(list(reversed(rows))))

    def comparison_rows(self):
        template = budget_chart.policies(self.fixture.payload)[0]
        return [dict(template, code=code, label_es=label, amount_thousand_eur=amount)
                for code, label, amount in [('21', 'PENSIONES', '40000.00'),
                                            ('31', 'SANIDAD', '2000.01'),
                                            ('32', 'EDUCACIÓN', '1000.02')]]

    def test_comparison_uses_unrounded_disjoint_margins_and_named_denominator(self):
        rows = self.comparison_rows()
        result = budget_chart.pension_comparison(rows)
        self.assertEqual(result['combined'], '3000.03')
        self.assertEqual(result['ratio'], '7,50 %')
        html = budget_chart.comparison_html(rows, self.fixture.payload)
        self.assertIn('respecto a pensiones, no al presupuesto total', html)
        self.assertIn('No representan todo el gasto público', html)
        self.assertIn('Fuente oficial', html)
        self.assertIn('CSV:', html)
        image, end = budget_chart.comparison_svg(rows, 0)
        self.assertGreater(end, 0)
        root = ET.fromstring('<svg>' + image + '</svg>')
        colored = [node for node in root.iter('rect') if node.attrib['fill'] != '#e5e9ec']
        self.assertAlmostEqual(float(colored[0].attrib['width']), 1000)
        self.assertAlmostEqual(sum(float(node.attrib['width']) for node in colored[-2:]), 75.00075)
        self.assertIn(result['ratio'], image)
        self.assertIn('No representan todo el gasto público', ' '.join(node.text for node in root.iter('text')))

    def test_comparison_missing_rows_zero_reference_and_larger_sum(self):
        rows = self.comparison_rows()
        self.assertIsNone(budget_chart.pension_comparison(rows[:2]))
        rows[0]['amount_thousand_eur'] = '0'
        self.assertIsNone(budget_chart.pension_comparison(rows))
        self.assertEqual(budget_chart.comparison_html(rows, self.fixture.payload), '')
        rows[0]['amount_thousand_eur'] = '1000'
        comparison = budget_chart.pension_comparison(rows)
        self.assertEqual(comparison['ratio'], '300,00 %')
        self.assertEqual(comparison['scale'], Decimal('3000.03'))
        image, _ = budget_chart.comparison_svg(rows, 0)
        root = ET.fromstring('<svg>' + image + '</svg>')
        for rect in root.iter('rect'):
            self.assertLessEqual(float(rect.attrib['x']) + float(rect.attrib['width']), 1040.00001)


if __name__ == '__main__':
    unittest.main()
