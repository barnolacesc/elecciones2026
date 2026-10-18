"""Source-linked private pilot contract; no fabricated review claims."""
import re
import unittest
from pathlib import Path

from elecciones2026.provisional2023 import load, load_budget, load_simulator, comparison, quiz, sources, budget, simulator, write

ROOT = Path(__file__).resolve().parents[1]


class ProvisionalPilotTests(unittest.TestCase):
    def test_four_parties_eight_topics_and_exact_citations(self):
        data = load(ROOT)
        self.assertEqual(len(data["topics"]), 8)
        self.assertEqual(len(data["positions"]), 36)
        expected_topics = {
            "housing", "education", "health-social-services", "economy-work-tax",
            "immigration", "climate-energy", "foreign-policy-eu", "institutions-rights"
        }
        self.assertEqual({t["id"] for t in data["topics"]}, expected_topics)
        for position in data["positions"]:
            self.assertTrue(position["url"].startswith("https://"))
            self.assertTrue(position["url"].endswith(f'#page={position["page"]}'))
            self.assertRegex(position["sha256"], r"^[a-f0-9]{64}$")
            self.assertNotIn("approved", position)
            self.assertTrue(position.get("measure_id"))
            self.assertTrue(position.get("measure_title"))

    def test_provisional_notice_and_source_links(self):
        data = load(ROOT)
        home = comparison(data)
        questions = quiz(data)
        self.assertIn("sin revisión editorial humana", home)
        self.assertIn("no calcula afinidad partidista", questions)
        self.assertEqual(home.count('class="card"'), 36)
        self.assertIn('class="measure-group"', home)
        self.assertEqual(questions.count('class="quiz-option"'), 5)
        self.assertNotIn('PP:', questions)
        self.assertNotIn('Sumar:', questions)
        self.assertIn('Totalmente en desacuerdo', questions)
        self.assertIn('Más bien en desacuerdo', questions)
        self.assertIn('Indiferente', questions)
        self.assertIn('Más bien de acuerdo', questions)
        self.assertIn('Totalmente de acuerdo', questions)
        self.assertIn('Fuentes del piloto', sources(data))
        self.assertEqual(home.count('target="_blank"'), 36)
        self.assertNotIn("sam-neutrality", home + questions)
        self.assertNotIn("2026</h1>", home + questions)
        self.assertIn('href="./presupuestos/"', home)
        self.assertIn('href="../presupuestos/"', questions)
        self.assertIn('href="./simulador/"', home)
        self.assertIn('href="../simulador/"', questions)

    def test_quiz_options_balanced_scale(self):
        data = load(ROOT)
        questions = quiz(data)
        values = re.findall(r'value="([^"]+)"', questions)
        self.assertEqual(values, ['strongly-agree', 'agree', 'neutral', 'disagree', 'strongly-disagree'])

    def test_budget_provisional_loading_and_contract(self):
        budget_data = load_budget(ROOT)
        self.assertEqual(budget_data["election_id"], "es-gen-2023")
        self.assertEqual(budget_data["status"], "historical-provisional-private")
        self.assertEqual(budget_data["bundle_id"], "2023-provisional")
        policies = [m for m in budget_data["payload"]["values.json"]["margins"] if m["kind"] == "policy"]
        self.assertEqual(len(policies), 27)
        denominator = budget_data["payload"]["measurement.json"]["denominator_amount_thousand_eur"]
        self.assertEqual(denominator, "485985812.22")

    def test_budget_page_rendering_and_navigation(self):
        data = load(ROOT)
        budget_data = load_budget(ROOT)
        budget_html = budget(data, budget_data)
        self.assertIn("PGE 2023: presupuesto aprobado", budget_html)
        self.assertIn("¿Cómo se reparte el presupuesto?", budget_html)
        self.assertIn("Para comparar magnitudes", budget_html)
        self.assertIn("485.985,81", budget_html)
        self.assertIn('href="../presupuestos/"', budget_html)
        self.assertIn('data-chart-url="./grafico.svg"', budget_html)
        self.assertIn('<script src="../budget-chart.js" defer></script>', budget_html)
        self.assertIn("BORRADOR PRIVADO", budget_html)
        self.assertIn("Políticas de gasto, de mayor a menor importe", budget_html)

    def test_simulator_provisional_loading_and_contract(self):
        sim_data = load_simulator(ROOT)
        self.assertTrue(sim_data["available"])
        self.assertEqual(sim_data["election_id"], "es-gen-2023")
        self.assertEqual(sim_data["total_seats"], 350)
        self.assertEqual(sim_data["majority_threshold"], 176)
        self.assertEqual(len(sim_data["sample_groups"]), 11)
        total_sample = sum(int(g["seats"]) for g in sim_data["sample_groups"])
        self.assertEqual(total_sample, 350)

    def test_simulator_page_rendering_and_navigation(self):
        data = load(ROOT)
        sim_data = load_simulator(ROOT)
        sim_html = simulator(data, sim_data)
        self.assertIn("Simulador de escaños y mayorías", sim_html)
        self.assertIn("176 escaños", sim_html)
        self.assertIn("simulator-app", sim_html)
        self.assertIn('<script src="../simulator-data.js" defer></script>', sim_html)
        self.assertIn('<script src="../simulator-engine.js" defer></script>', sim_html)
        self.assertIn('<script src="../simulator-ui.js" defer></script>', sim_html)
        self.assertIn('href="../simulador/"', sim_html)
        self.assertIn("Reglamento del Congreso", sim_html)

    def test_write_provisional_pilot_generates_budget_and_assets(self):
        import tempfile
        data = load(ROOT)
        with tempfile.TemporaryDirectory() as tmpdir:
            staging = Path(tmpdir)
            write(ROOT, staging, "https://preview.example.com")
            self.assertTrue((staging / "index.html").exists())
            self.assertTrue((staging / "cuestionario/index.html").exists())
            self.assertTrue((staging / "fuentes/index.html").exists())
            self.assertTrue((staging / "presupuestos/index.html").exists())
            self.assertTrue((staging / "presupuestos/grafico.svg").exists())
            self.assertTrue((staging / "budget-chart.js").exists())
            self.assertTrue((staging / "simulador/index.html").exists())
            self.assertTrue((staging / "simulator-data.js").exists())
            self.assertTrue((staging / "simulator-engine.js").exists())
            self.assertTrue((staging / "simulator-ui.js").exists())
            self.assertTrue((staging / "pilot-2023.css").exists())
            self.assertTrue((staging / "pilot-2023.js").exists())
            self.assertTrue((staging / "pilot-2023-data.json").exists())
            svg_content = (staging / "presupuestos/grafico.svg").read_text(encoding="utf-8")
            self.assertIn("<svg", svg_content)
            self.assertIn("¿Cómo se reparte el presupuesto?", svg_content)
            sim_content = (staging / "simulador/index.html").read_text(encoding="utf-8")
            self.assertIn("Simulador de escaños y mayorías", sim_content)
            self.assertIn("simulator-app", sim_content)


if __name__ == "__main__":
    unittest.main()
