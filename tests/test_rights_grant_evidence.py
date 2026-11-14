"""Fail-closed metadata checks for fictional source-use decisions."""

import unittest

from elecciones2026.source_register import load_register_from_dict


def fictional_register(status: str) -> dict:
    return {
        "version": "1.0.0",
        "last_updated": "2026-11-14",
        "elections": [
            {
                "id": "fictional-election",
                "name": "Fictional election",
                "election_date": "2026-11-14",
                "call_decree": "Fictional decree",
                "status": "pilot_rehearsal",
            }
        ],
        "sources": [
            {
                "id": "fictional-source",
                "election_id": "fictional-election",
                "party_id": "fictional-party",
                "candidature_name": "Fictional party",
                "publisher": "Fictional publisher",
                "scope": "general",
                "official_url": "https://example.test/programme",
                "direct_url": "https://example.test/programme.pdf",
                "retrieval_date": "2026-11-14",
                "sha256": "a" * 64,
                "status": "verified",
                "rights_review": {
                    "status": status,
                    "reviewed_by": "Fictional reviewer",
                    "review_date": "2026-11-14",
                    "terms_notes": "Fictional use decision",
                    "evidence_ref": "private://fictional-decision",
                },
            }
        ],
    }


class TestRightsGrantEvidence(unittest.TestCase):
    def test_grants_require_human_attribution_and_private_evidence(self) -> None:
        for status in ("link_only", "link_and_short_quote", "public_domain"):
            for field, value in (("reviewed_by", " "), ("review_date", None), ("evidence_ref", " ")):
                with self.subTest(status=status, field=field):
                    data = fictional_register(status)
                    data["sources"][0]["rights_review"][field] = value
                    register, errors = load_register_from_dict(data)
                    self.assertIsNone(register)
                    self.assertTrue(any("rights grant requires" in error for error in errors), errors)

    def test_complete_fictional_grant_loads(self) -> None:
        for status in ("link_only", "link_and_short_quote", "public_domain"):
            with self.subTest(status=status):
                register, errors = load_register_from_dict(fictional_register(status))
                self.assertEqual(errors, [])
                self.assertEqual(register.sources[0].rights_review.status, status)

    def test_pending_and_denied_do_not_invent_grants(self) -> None:
        for status in ("not_reviewed", "permission_denied"):
            with self.subTest(status=status):
                data = fictional_register(status)
                review = data["sources"][0]["rights_review"]
                review.update(reviewed_by=None, review_date=None, evidence_ref=None)
                register, errors = load_register_from_dict(data)
                self.assertEqual(errors, [])
                self.assertEqual(register.sources[0].rights_review.status, status)


if __name__ == "__main__":
    unittest.main()
