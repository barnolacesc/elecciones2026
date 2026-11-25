"""Tests for the electoral programme source register."""

import json
from pathlib import Path
import unittest

from elecciones2026.source_register import (
    VALID_RIGHTS_STATUSES,
    VALID_STATUSES,
    get_sources_for_election,
    load_register,
    load_register_from_dict,
)

REGISTER_PATH = Path(__file__).resolve().parent.parent / "content" / "sources" / "register.json"


class TestSourceRegister(unittest.TestCase):
    def test_register_file_exists_and_loads(self) -> None:
        self.assertTrue(REGISTER_PATH.exists(), f"Missing register file at {REGISTER_PATH}")
        register = load_register(REGISTER_PATH)
        self.assertEqual(register.version, "1.0.0")
        self.assertGreaterEqual(len(register.elections), 2)
        self.assertGreaterEqual(len(register.sources), 10)

    def test_mandatory_fields_present_in_all_sources(self) -> None:
        register = load_register(REGISTER_PATH)
        for s in register.sources:
            with self.subTest(source_id=s.id):
                self.assertTrue(s.id, "Source ID must not be empty")
                self.assertTrue(s.election_id, "election_id must not be empty")
                self.assertTrue(s.party_id, "party_id must not be empty")
                self.assertTrue(s.candidature_name, "candidature_name must not be empty")
                self.assertTrue(s.publisher, "publisher must not be empty")
                self.assertEqual(s.scope, "general", "scope must be 'general'")
                self.assertTrue(s.official_url.startswith(("http://", "https://")), "official_url must be HTTP(S)")
                self.assertTrue(s.retrieval_date, "retrieval_date must not be empty")
                self.assertIn(s.status, VALID_STATUSES, f"status '{s.status}' must be in VALID_STATUSES")
                self.assertIn(s.rights_review.status, VALID_RIGHTS_STATUSES)
                self.assertIsInstance(s.replacement_history, list)

    def test_2026_sources_tracking_status(self) -> None:
        register = load_register(REGISTER_PATH)
        sources_2026 = get_sources_for_election(register, "es-gen-2026")
        verified_parties = {
            "pp", "erc", "pnv", "bng", "coalicion-canaria", "salf", "partido-humanista",
            "psoe", "vox", "frente-amplio", "ehbildu", "junts",
            "podemos", "compromis-front-valencia",
        }
        partial_parties = {"upn-pp", "frente-obrero"}
        replacements = {
            "src-2026-bng-v1": "src-2026-bng-v2",
            "src-2026-vox-v1": "src-2026-vox-v2",
            "src-2026-frente-obrero-v1": "src-2026-frente-obrero-v2",
        }
        active = [source for source in sources_2026 if source.status != "replaced"]
        self.assertCountEqual([s.party_id for s in active], verified_parties | partial_parties)
        self.assertEqual({s.id for s in sources_2026 if s.status == "replaced"}, set(replacements))
        for s in sources_2026:
            with self.subTest(source_id=s.id):
                self.assertEqual(s.election_id, "es-gen-2026")
                if s.status == "replaced":
                    self.assertEqual(s.replacement_history[-1].superseded_by, replacements[s.id])
                    continue
                if s.party_id in verified_parties:
                    self.assertEqual(s.rights_review.status, "link_only")
                    self.assertEqual(s.status, "verified")
                    self.assertRegex(s.sha256 or "", r"^[0-9a-f]{64}$")
                    self.assertIsNotNone(s.direct_url, f"{s.id} must specify direct_url")
                else:
                    self.assertEqual(s.rights_review.status, "not_reviewed")
                    self.assertEqual(s.status, "partial")
                    self.assertIsNone(s.sha256)
                    self.assertIsNone(s.direct_url)

    def test_task_1_2_pilot_programmes_registered(self) -> None:
        """Verify source registration without asserting rights or human approval.
        """
        register = load_register(REGISTER_PATH)
        sources_2023 = get_sources_for_election(register, "es-gen-2023")
        self.assertGreaterEqual(len(sources_2023), 2, "Must register at least two pilot programmes")

        by_party = {s.party_id: s for s in sources_2023}

        # Verify PP 2023 pilot programme
        self.assertIn("pp", by_party)
        pp_source = by_party["pp"]
        self.assertEqual(pp_source.status, "published-unverified")
        self.assertEqual(pp_source.retrieval_date, "2026-10-10")
        self.assertEqual(pp_source.sha256, "c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108")
        self.assertIn("programa_electoral_pp_23j_feijoo_2023.pdf", pp_source.direct_url)
        self.assertEqual(pp_source.rights_review.status, "not_reviewed")

        # Verify ERC 2023 pilot programme
        self.assertIn("erc", by_party)
        erc_source = by_party["erc"]
        self.assertEqual(erc_source.status, "published-unverified")
        self.assertEqual(erc_source.retrieval_date, "2026-10-10")
        self.assertEqual(erc_source.sha256, "760db25e48422b74a9b0c3172cab16cf39d010345849e50b921ff8bf61be2854")
        self.assertIn("e2023-programa.pdf", erc_source.direct_url)
        self.assertEqual(erc_source.rights_review.status, "not_reviewed")

        # Verify Sumar and PNV 2023 pilot programmes
        self.assertIn("sumar", by_party)
        self.assertEqual(by_party["sumar"].status, "published-unverified")
        self.assertEqual(by_party["sumar"].rights_review.status, "not_reviewed")

        self.assertIn("pnv", by_party)
        self.assertEqual(by_party["pnv"].status, "published-unverified")
        self.assertEqual(by_party["pnv"].rights_review.status, "not_reviewed")

    def test_election_scoping_isolation(self) -> None:
        """Verify that 2023 pilot programmes and 2026 sources belong to disjoint election sets."""
        register = load_register(REGISTER_PATH)
        sources_2026 = get_sources_for_election(register, "es-gen-2026")
        sources_2023 = get_sources_for_election(register, "es-gen-2023")

        ids_2026 = {s.id for s in sources_2026}
        ids_2023 = {s.id for s in sources_2023}
        self.assertEqual(len(ids_2026.intersection(ids_2023)), 0, "Source IDs across elections must be disjoint")

    def test_validation_rejects_missing_mandatory_fields(self) -> None:
        invalid_data = {
            "version": "1.0.0",
            "last_updated": "2026-10-09T00:00:00Z",
            "elections": [{"id": "el1", "name": "Election 1", "election_date": "2026-11-29", "call_decree": "BOE", "status": "active_monitoring"}],
            "sources": [
                {
                    "id": "src-1",
                    "election_id": "el1",
                    # party_id missing
                    "candidature_name": "Party",
                    "publisher": "Party",
                    "scope": "general",
                    "official_url": "https://example.org",
                    "retrieval_date": "2026-10-09",
                    "status": "missing",
                    "rights_review": {"status": "not_reviewed", "terms_notes": "None"},
                }
            ],
        }
        reg, errors = load_register_from_dict(invalid_data)
        self.assertIsNone(reg)
        self.assertTrue(any("missing party_id" in e for e in errors))

    def test_validation_rejects_verified_without_hash(self) -> None:
        invalid_data = {
            "version": "1.0.0",
            "last_updated": "2026-10-09T00:00:00Z",
            "elections": [{"id": "el1", "name": "Election 1", "election_date": "2026-11-29", "call_decree": "BOE", "status": "active_monitoring"}],
            "sources": [
                {
                    "id": "src-1",
                    "election_id": "el1",
                    "party_id": "party1",
                    "candidature_name": "Party",
                    "publisher": "Party",
                    "scope": "general",
                    "official_url": "https://example.org",
                    "direct_url": "https://example.org/prog.pdf",
                    "retrieval_date": "2026-10-09",
                    "status": "verified",
                    # sha256 is None or missing
                    "sha256": None,
                    "rights_review": {"status": "link_and_short_quote", "terms_notes": "None"},
                }
            ],
        }
        reg, errors = load_register_from_dict(invalid_data)
        self.assertIsNone(reg)
        self.assertTrue(any("verified status requires a valid" in e for e in errors))

    def test_validation_rejects_malformed_present_hash_before_verification(self) -> None:
        source = {
            "id": "fictional-source-v1",
            "election_id": "fictional-election",
            "party_id": "fictional-party",
            "candidature_name": "Fictional Party",
            "publisher": "Fictional Party",
            "official_url": "https://example.org/programme",
            "direct_url": "https://example.org/programme.pdf",
            "retrieval_date": "2026-10-09",
            "status": "published-unverified",
            "rights_review": {"status": "not_reviewed", "terms_notes": "Pending"},
        }
        register = {
            "version": "1.0.0",
            "last_updated": "2026-10-09",
            "elections": [{
                "id": "fictional-election",
                "name": "Fictional election",
                "election_date": "2026-11-29",
                "call_decree": "Fictional decree",
                "status": "active_monitoring",
            }],
            "sources": [source],
        }

        for digest in ("a" * 63, "A" * 64, 123):
            with self.subTest(digest=digest):
                source["sha256"] = digest
                loaded, errors = load_register_from_dict(register)
                self.assertIsNone(loaded)
                self.assertTrue(any("sha256" in error for error in errors), errors)

        source["sha256"] = "a" * 64
        loaded, errors = load_register_from_dict(register)
        self.assertEqual(errors, [])
        self.assertIsNotNone(loaded)

    def test_validation_rejects_replaced_without_history(self) -> None:
        invalid_data = {
            "version": "1.0.0",
            "last_updated": "2026-10-09T00:00:00Z",
            "elections": [{"id": "el1", "name": "Election 1", "election_date": "2026-11-29", "call_decree": "BOE", "status": "active_monitoring"}],
            "sources": [
                {
                    "id": "src-1",
                    "election_id": "el1",
                    "party_id": "party1",
                    "candidature_name": "Party",
                    "publisher": "Party",
                    "scope": "general",
                    "official_url": "https://example.org",
                    "retrieval_date": "2026-10-09",
                    "status": "replaced",
                    "replacement_history": [],
                    "rights_review": {"status": "link_and_short_quote", "terms_notes": "None"},
                }
            ],
        }
        reg, errors = load_register_from_dict(invalid_data)
        self.assertIsNone(reg)
        self.assertTrue(any("replaced status requires non-empty replacement_history" in e for e in errors))

    def test_validation_accepts_valid_replaced_record(self) -> None:
        valid_data = {
            "version": "1.0.0",
            "last_updated": "2026-10-09T00:00:00Z",
            "elections": [{"id": "el1", "name": "Election 1", "election_date": "2026-11-29", "call_decree": "BOE", "status": "active_monitoring"}],
            "sources": [
                {
                    "id": "src-1-v1",
                    "election_id": "el1",
                    "party_id": "party1",
                    "candidature_name": "Party",
                    "publisher": "Party",
                    "scope": "general",
                    "official_url": "https://example.org",
                    "direct_url": "https://example.org/prog-v1.pdf",
                    "retrieval_date": "2026-10-09",
                    "status": "replaced",
                    "version": "1.0",
                    "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                    "replacement_history": [
                        {
                            "prior_version": "1.0",
                            "superseded_by": "src-1-v2",
                            "replacement_date": "2026-10-15",
                            "reason": "Errata corrigenda published by party",
                        }
                    ],
                    "rights_review": {"status": "not_reviewed", "terms_notes": "None"},
                }
            ],
        }
        reg, errors = load_register_from_dict(valid_data)
        self.assertEqual(errors, [])
        self.assertIsNotNone(reg)
        self.assertEqual(len(reg.sources[0].replacement_history), 1)

    def test_publication_date_cannot_follow_retrieval(self) -> None:
        source = {
            "id": "fictional-source",
            "election_id": "fictional-election",
            "party_id": "fictional-party",
            "official_url": "https://example.org/programme.pdf",
            "retrieval_date": "2023-07-01",
            "publication_date": "2023-07-02",
            "status": "published-unverified",
            "rights_review": {"status": "not_reviewed", "terms_notes": "Pending"},
        }
        data = {
            "version": "1.0.0",
            "last_updated": "2023-07-02T00:00:00Z",
            "elections": [
                {
                    "id": "fictional-election",
                    "name": "Fictional election",
                    "election_date": "2023-07-23",
                    "call_decree": "Fictional decree",
                    "status": "pilot_rehearsal",
                }
            ],
            "sources": [source],
        }

        register, errors = load_register_from_dict(data)
        self.assertIsNone(register)
        self.assertTrue(
            any("publication_date must not be after retrieval_date" in error for error in errors)
        )

        for publication_date in ("2023-07-01", "2023-06-30", None):
            with self.subTest(publication_date=publication_date):
                source["publication_date"] = publication_date
                register, errors = load_register_from_dict(data)
                self.assertEqual(errors, [])
                self.assertIsNotNone(register)


if __name__ == "__main__":
    unittest.main()
