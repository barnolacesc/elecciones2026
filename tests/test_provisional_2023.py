"""Source-linked private pilot contract; no fabricated review claims."""
import re
import unittest
from pathlib import Path

from elecciones2026.provisional2023 import load, comparison, quiz, sources

ROOT = Path(__file__).resolve().parents[1]


class ProvisionalPilotTests(unittest.TestCase):
    def test_four_parties_three_topics_and_exact_citations(self):
        data = load(ROOT)
        self.assertEqual(len(data["positions"]), 12)
        for position in data["positions"]:
            self.assertTrue(position["url"].startswith("https://"))
            self.assertTrue(position["url"].endswith(f'#page={position["page"]}'))
            self.assertRegex(position["sha256"], r"^[a-f0-9]{64}$")
            self.assertNotIn("approved", position)

    def test_provisional_notice_and_source_links(self):
        data = load(ROOT)
        home = comparison(data)
        questions = quiz(data)
        self.assertIn("sin revisión editorial humana", home)
        self.assertIn("no calcula afinidad partidista", questions)
        self.assertEqual(home.count('class="card"'), 12)
        self.assertEqual(questions.count('class="quiz-option"'), 4)
        self.assertNotIn('PP:', questions)
        self.assertNotIn('Sumar:', questions)
        self.assertIn('Muy en desacuerdo', questions)
        self.assertIn('Indiferente', questions)
        self.assertIn('Fuentes del piloto', sources(data))
        self.assertEqual(home.count('target="_blank"'), 12)
        self.assertNotIn("sam-neutrality", home + questions)
        self.assertNotIn("2026</h1>", home + questions)


if __name__ == "__main__":
    unittest.main()
