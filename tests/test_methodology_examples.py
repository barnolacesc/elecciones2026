"""Tests for candidate inclusion, party naming, programme status lifecycle, and taxonomy."""

import json
from pathlib import Path
import unittest

from elecciones2026.methodology import (
    CORE_TOPIC_IDS,
    PartyRecord,
    ProgrammeRecord,
    ProgrammeStatus,
    Taxonomy,
    load_programme,
    load_taxonomy,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
EXAMPLES_DIR = CONTENT_DIR / "examples"
PROGRAMMES_DIR = EXAMPLES_DIR / "programmes"


class TestTopicTaxonomy(unittest.TestCase):
    """Verify topic taxonomy definition against policy requirements."""

    def setUp(self):
        self.taxonomy_path = CONTENT_DIR / "taxonomy.json"
        self.assertTrue(
            self.taxonomy_path.exists(), f"Missing taxonomy file at {self.taxonomy_path}"
        )
        self.taxonomy = load_taxonomy(self.taxonomy_path)

    def test_taxonomy_version_and_election(self):
        self.assertEqual(self.taxonomy.schema_version, "1.0.0")
        self.assertEqual(self.taxonomy.taxonomy_version, "1.0.0")
        self.assertEqual(self.taxonomy.election_id, "es-gen-2026")

    def test_eight_core_topics_present(self):
        topic_ids = [t.id for t in self.taxonomy.topics]
        self.assertEqual(len(topic_ids), 8)
        self.assertCountEqual(topic_ids, CORE_TOPIC_IDS)

    def test_taxonomy_validation_passes(self):
        errors = self.taxonomy.validate()
        self.assertEqual(errors, [])

    def test_subtopics_defined_with_bilingual_labels(self):
        for topic in self.taxonomy.topics:
            self.assertGreater(
                len(topic.subtopics), 0, f"Topic '{topic.id}' should define subtopics"
            )
            for subtopic in topic.subtopics:
                self.assertTrue(subtopic.id)
                self.assertTrue(subtopic.name_es)
                self.assertTrue(subtopic.name_en)

    def test_taxonomy_validation_detects_missing_topic(self):
        bad_data = {
            "schema_version": "1.0.0",
            "taxonomy_version": "1.0.0",
            "election_id": "es-gen-2026",
            "topics": [
                {
                    "id": "housing",
                    "name_es": "Vivienda",
                    "name_en": "Housing",
                    "description_es": "Desc",
                    "description_en": "Desc",
                    "subtopics": [{"id": "rent", "name_es": "Alquiler", "name_en": "Rent"}],
                }
            ],
        }
        tax = Taxonomy.from_dict(bad_data)
        errors = tax.validate()
        self.assertTrue(any("Expected exactly 8 core topics" in e for e in errors))


class TestPartyNamingStandard(unittest.TestCase):
    """Verify party naming standard and candidate inclusion fixtures."""

    def setUp(self):
        self.parties_path = EXAMPLES_DIR / "parties.json"
        self.assertTrue(self.parties_path.exists())
        with open(self.parties_path, "r", encoding="utf-8") as f:
            self.parties_data = json.load(f)

    def test_parties_fixtures_valid(self):
        parties = self.parties_data.get("parties", [])
        self.assertGreaterEqual(len(parties), 4)

        for p_dict in parties:
            party = PartyRecord(
                id=p_dict["id"],
                official_name=p_dict["official_name"],
                display_name=p_dict["display_name"],
                short_name=p_dict["short_name"],
                ballot_name=p_dict["ballot_name"],
                is_coalition=p_dict["is_coalition"],
                coalition_members=p_dict["coalition_members"],
                territorial_scope=p_dict["territorial_scope"],
                inclusion_criterion=p_dict["inclusion_criterion"],
                is_fixture=p_dict.get("is_fixture", False),
            )
            self.assertTrue(party.is_fixture, f"Party {party.id} must be marked as fixture")
            errors = party.validate()
            self.assertEqual(errors, [], f"Validation errors for {party.id}: {errors}")

    def test_coalition_structure(self):
        parties = {p["id"]: p for p in self.parties_data.get("parties", [])}
        coalition = parties.get("coalicion-ejemplo-c")
        self.assertIsNotNone(coalition)
        self.assertTrue(coalition["is_coalition"])
        self.assertEqual(len(coalition["coalition_members"]), 2)


class TestProgrammeStatusLifecycle(unittest.TestCase):
    """Verify test examples for official, partial, replaced, and missing programmes."""

    def test_official_programme_fixture(self):
        file_path = PROGRAMMES_DIR / "party-a-official.json"
        self.assertTrue(file_path.exists())
        prog = load_programme(file_path)
        self.assertEqual(prog.status, ProgrammeStatus.OFFICIAL)
        self.assertTrue(prog.is_fixture)
        self.assertIsNotNone(prog.official_url)
        self.assertIsNotNone(prog.sha256)
        self.assertEqual(len(prog.sha256), 64)
        errors = prog.validate()
        self.assertEqual(errors, [])

    def test_partial_programme_fixture(self):
        file_path = PROGRAMMES_DIR / "party-b-partial.json"
        self.assertTrue(file_path.exists())
        prog = load_programme(file_path)
        self.assertEqual(prog.status, ProgrammeStatus.PARTIAL)
        self.assertTrue(prog.is_fixture)
        self.assertIsNotNone(prog.coverage_notes)
        self.assertIsNotNone(prog.official_url)
        errors = prog.validate()
        self.assertEqual(errors, [])

    def test_replaced_programme_fixture_and_successor(self):
        replaced_path = PROGRAMMES_DIR / "party-c-v1-replaced.json"
        successor_path = PROGRAMMES_DIR / "party-c-v2-official.json"
        self.assertTrue(replaced_path.exists())
        self.assertTrue(successor_path.exists())

        v1 = load_programme(replaced_path)
        v2 = load_programme(successor_path)

        self.assertEqual(v1.status, ProgrammeStatus.REPLACED)
        self.assertEqual(v2.status, ProgrammeStatus.OFFICIAL)
        self.assertEqual(v1.superseded_by, v2.programme_id)
        self.assertEqual(v2.supersedes, v1.programme_id)
        self.assertIsNotNone(v1.replacement_reason)
        self.assertEqual(v1.validate(), [])
        self.assertEqual(v2.validate(), [])

    def test_missing_programme_fixture(self):
        file_path = PROGRAMMES_DIR / "party-d-missing.json"
        self.assertTrue(file_path.exists())
        prog = load_programme(file_path)
        self.assertEqual(prog.status, ProgrammeStatus.MISSING)
        self.assertTrue(prog.is_fixture)
        self.assertIsNone(prog.official_url)
        self.assertIsNone(prog.sha256)
        self.assertIsNotNone(prog.coverage_notes)
        errors = prog.validate()
        self.assertEqual(errors, [])

    def test_validation_rejects_missing_programme_with_url(self):
        prog = ProgrammeRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            programme_id="prog-invalid",
            candidacy_id="party-x",
            title="Invalid missing",
            status=ProgrammeStatus.MISSING,
            official_url="https://example.com/bogus.pdf",
            coverage_notes="Notes",
            is_fixture=True,
        )
        errors = prog.validate()
        self.assertTrue(any("Missing programme must have null official_url" in e for e in errors))

    def test_validation_rejects_official_programme_without_hash(self):
        prog = ProgrammeRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            programme_id="prog-invalid",
            candidacy_id="party-x",
            title="Invalid official",
            status=ProgrammeStatus.OFFICIAL,
            version="1.0",
            official_url="https://example.com/prog.pdf",
            publication_date="2026-10-15",
            retrieval_date="2026-10-16T00:00:00Z",
            sha256=None,
            rights_status="verified_public_manifesto",
            is_fixture=True,
        )
        errors = prog.validate()
        self.assertTrue(any("valid 64-character hex SHA-256 hash" in e for e in errors))

    def test_validation_rejects_cross_election_comparison(self):
        prog = ProgrammeRecord(
            schema_version="1.0.0",
            election_id="es-gen-2023",  # Past election
            programme_id="prog-past",
            candidacy_id="party-x",
            title="Past election programme",
            status=ProgrammeStatus.OFFICIAL,
            version="1.0",
            official_url="https://example.com/prog2023.pdf",
            publication_date="2023-07-01",
            retrieval_date="2023-07-02T00:00:00Z",
            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            rights_status="verified_public_manifesto",
            is_fixture=True,
        )
        errors = prog.validate(target_election_id="es-gen-2026")
        self.assertTrue(any("Election mismatch" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
