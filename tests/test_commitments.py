"""Unit tests for commitment tracking, validation, sovereign source rules, and Four-Eyes review.

Part of OpenSpec change commitment-follow-through (Epic E9, Gate G9).
"""

import json
from pathlib import Path
import unittest

from elecciones2026.commitments import (
    CommitmentValidationError,
    load_all_commitments,
    load_commitment,
    validate_commitment_dict,
)

ROOT = Path(__file__).resolve().parent.parent
COMMITMENTS_DIR = ROOT / "content" / "commitments"


class CommitmentTests(unittest.TestCase):
    """Test suite for commitment records, methodology, and validators."""

    def test_benchmark_dossier_contains_10_valid_records(self):
        """Verify that the 10 benchmark pilot commitment records validate successfully."""
        records = load_all_commitments(COMMITMENTS_DIR)
        self.assertEqual(len(records), 10)

        # Check balance: exactly 5 governing, 5 opposition
        governing_count = sum(
            1 for r in records if r.governance_context.role in {"governing_sole", "governing_senior", "governing_junior"}
        )
        opposition_count = sum(
            1 for r in records if r.governance_context.role == "opposition"
        )
        self.assertEqual(governing_count, 5)
        self.assertEqual(opposition_count, 5)

        # Verify all records have valid sovereign URLs
        for r in records:
            self.assertGreater(len(r.evidence), 0)
            for ev in r.evidence:
                self.assertTrue(ev.url.startswith("https://"))
                self.assertIn(ev.source_type, {"boe", "bocg_initiative", "bocg_vote", "igae", "ine"})

    def test_rejection_of_prohibited_accusatory_terms(self):
        """Verify that words like 'mentira' or 'engaño' trigger immediate validation failure."""
        sample_path = COMMITMENTS_DIR / "cmt-pilot-2023-psoe-housing-01.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Test in pledge summary
        data_corrupt = json.loads(json.dumps(data))
        data_corrupt["pledge"]["summary_es"] = "Esta promesa fue una mentira del candidato."
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt)
        self.assertIn("prohibited accusatory term 'mentira'", str(ctx.exception))

        # Test in finding summary
        data_corrupt2 = json.loads(json.dumps(data))
        data_corrupt2["evidence"][0]["finding_summary_es"] = "Comprobado el engaño electoral manifiesto."
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt2)
        self.assertIn("prohibited accusatory term 'engaño'", str(ctx.exception))

        # Test in English ('lie')
        data_corrupt3 = json.loads(json.dumps(data))
        data_corrupt3["pledge"]["summary_es"] = "This campaign pledge was a direct lie to voters."
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt3)
        self.assertIn("prohibited accusatory term 'lie'", str(ctx.exception))

    def test_rejection_of_non_sovereign_sources(self):
        """Verify that journalistic or non-official URLs are rejected."""
        sample_path = COMMITMENTS_DIR / "cmt-pilot-2023-sumar-economy-01.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data_corrupt = json.loads(json.dumps(data))
        data_corrupt["evidence"][0]["url"] = "https://elpais.com/economia/2024-02-07/subida-salario-minimo.html"
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt)
        self.assertIn("non-sovereign host 'elpais.com'", str(ctx.exception))

    def test_four_eyes_review_segregation_enforced(self):
        """Verify that two distinct reviewers are required and drafter cannot be reviewer 2."""
        sample_path = COMMITMENTS_DIR / "cmt-pilot-2023-pp-justice-01.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Reviewer 1 identical to Reviewer 2
        data_corrupt = json.loads(json.dumps(data))
        data_corrupt["editorial_review"]["reviewed_by_1"] = "auditor-01"
        data_corrupt["editorial_review"]["reviewed_by_2"] = "auditor-01"
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt)
        self.assertIn("Four-Eyes Principle violation", str(ctx.exception))

        # Drafter serving as Reviewer 2
        data_corrupt2 = json.loads(json.dumps(data))
        data_corrupt2["editorial_review"]["drafter"] = "lead-drafter"
        data_corrupt2["editorial_review"]["reviewed_by_2"] = "lead-drafter"
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt2)
        self.assertIn("drafter cannot serve as the second independent reviewer", str(ctx.exception))

    def test_opposition_role_requires_parliamentary_evidence(self):
        """Verify that opposition parties must be audited against parliamentary acts."""
        sample_path = COMMITMENTS_DIR / "cmt-pilot-2023-pp-energy-03.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Remove parliamentary evidence items and replace with decree audit
        data_corrupt = json.loads(json.dumps(data))
        data_corrupt["evidence"] = [
            {
                "source_type": "boe",
                "official_id": "BOE-SAMPLE",
                "title": "Muestra sin votación",
                "url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-1",
                "date": "2024-01-01",
                "finding_summary_es": "Ausencia de decreto gubernamental.",
            }
        ]
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt)
        self.assertIn("lacks parliamentary voting or initiative evidence", str(ctx.exception))

    def test_invalid_status_rejected(self):
        """Verify that unapproved statuses are rejected."""
        sample_path = COMMITMENTS_DIR / "cmt-pilot-2023-psoe-housing-01.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data_corrupt = json.loads(json.dumps(data))
        data_corrupt["status"] = "broken_promise"
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt)
        self.assertIn("Invalid status: 'broken_promise'", str(ctx.exception))

    def test_invalid_topic_rejected(self):
        """Verify that unrecognized topics outside the 8 core taxonomy topics are rejected."""
        sample_path = COMMITMENTS_DIR / "cmt-pilot-2023-psoe-housing-01.json"
        with open(sample_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data_corrupt = json.loads(json.dumps(data))
        data_corrupt["topic_id"] = "space-exploration"
        with self.assertRaises(CommitmentValidationError) as ctx:
            validate_commitment_dict(data_corrupt)
        self.assertIn("Invalid topic_id: 'space-exploration'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
