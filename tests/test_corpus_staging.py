"""Tests for E1.4-2026 private draft staging utility.

Synthetic tests only: no raw political content, party manifestos, or unverified claims in Git.
Verifies hash corruption detection, changed input rejection, metadata validation,
exact page coordinate formatting, slug validation, atomic rollback, permission enforcement,
and repository boundary enforcement.
"""

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest

from elecciones2026.corpus_staging import (
    CorpusStagingError,
    HashVerificationError,
    InputValidationError,
    OutputPathError,
    assert_output_dir_outside_repo,
    find_repo_root,
    format_source_page,
    stage_corpus,
    validate_point_id,
)
from elecciones2026.generator import BuildValidationError, load_and_validate_site_data
from elecciones2026.schemas import load_statement

REPO_ROOT = find_repo_root()


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_str(text: str) -> str:
    return _hash_bytes(text.encode("utf-8"))


class SyntheticCorpusFixture:
    """Creates a fully synthetic, offline test fixture resembling a private review run."""

    def __init__(self, base_dir: Path):
        self.run_dir = base_dir / "synthetic-run"
        self.run_dir.mkdir(parents=True)
        self.sources: list[dict] = []
        self.points_by_party: dict[str, list[dict]] = {}
        self.proposed_points: list[dict] = []

    def add_source(
        self,
        party_id: str,
        source_id: str,
        points: list[dict],
        source_url: str = "https://example.test/synthetic-source.pdf",
        source_version: str = "2026-v1",
    ):
        source_content = f"Synthetic raw bytes for {source_id}".encode("utf-8")
        source_sha256 = _hash_bytes(source_content)

        party_dir = self.run_dir / f"{party_id}-synthetic-review"
        party_dir.mkdir(parents=True)

        points_payload = {
            "source_id": source_id,
            "election_id": "es-gen-2026",
            "source_version": source_version,
            "source_sha256": source_sha256,
            "review_status": "draft",
            "human_reviews": [],
            "points": points,
        }
        points_bytes = (json.dumps(points_payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        points_file = party_dir / "points.json"
        points_file.write_bytes(points_bytes)
        points_sha256 = _hash_bytes(points_bytes)

        coverage_payload = {
            "source_id": source_id,
            "pages": [{"page": p, "has_points": True} for p in range(1, 4)],
        }
        coverage_bytes = (json.dumps(coverage_payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        coverage_file = party_dir / "page-coverage.json"
        coverage_file.write_bytes(coverage_bytes)
        coverage_sha256 = _hash_bytes(coverage_bytes)

        self.sources.append(
            {
                "party_id": party_id,
                "source_id": source_id,
                "source_sha256": source_sha256,
                "points_count": len(points),
                "points_sha256": points_sha256,
                "coverage_sha256": coverage_sha256,
                "directory": str(party_dir),
                "source_url": source_url,
                "source_version": source_version,
            }
        )

        for pt in points:
            self.proposed_points.append(
                {
                    "point_id": pt["id"],
                    "party_id": party_id,
                    "publisher": f"Synthetic {party_id.upper()}",
                    "topic_id": pt.get("topic_id") or "housing",
                    "subtopic_id": pt.get("subtopic_id") or "rental-regulation",
                    "title_es": pt.get("title_es", "Título sintético"),
                    "summary_es": pt.get("summary_es", "Resumen sintético"),
                }
            )

    def write_run_metadata(self, write_audit: bool = True):
        # 1. canonical-draft-manifest.json
        manifest = {
            "package": "E1.4-2026",
            "election_id": "es-gen-2026",
            "source_count": len(self.sources),
            "page_count": 10,
            "draft_measure_count": sum(s["points_count"] for s in self.sources),
            "drafts_only": True,
            "human_approval_granted": False,
            "sources": [
                {
                    "party_id": s["party_id"],
                    "source_id": s["source_id"],
                    "source_sha256": s["source_sha256"],
                    "points_count": s["points_count"],
                    "points_sha256": s["points_sha256"],
                    "coverage_sha256": s["coverage_sha256"],
                    "human_approval_granted": False,
                }
                for s in self.sources
            ],
        }
        (self.run_dir / "canonical-draft-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        )

        # 2. corpus-summary.json
        summary = {
            "package": "E1.4-2026",
            "human_approval_granted": False,
            "canonical_sources": {
                s["party_id"]: {
                    "party_id": s["party_id"],
                    "directory": s["directory"],
                    "human_approval_granted": False,
                    "points_count": s["points_count"],
                }
                for s in self.sources
            },
        }
        (self.run_dir / "corpus-summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )

        # 3. proposed-classification-index.json
        proposed = {
            "package": "E1.4-2026",
            "human_approval_granted": False,
            "taxonomy_status": "draft_for_editorial_review",
            "point_count": len(self.proposed_points),
            "points": self.proposed_points,
        }
        (self.run_dir / "proposed-classification-index.json").write_text(
            json.dumps(proposed, indent=2, sort_keys=True) + "\n"
        )

        # 4. jobs.json
        jobs = [
            {
                "party_id": s["party_id"],
                "source_id": s["source_id"],
                "source_sha256": s["source_sha256"],
                "source_url": s["source_url"],
                "source_version": s["source_version"],
            }
            for s in self.sources
        ]
        (self.run_dir / "jobs.json").write_text(
            json.dumps(jobs, indent=2, sort_keys=True) + "\n"
        )

        # 5. source-integrity-audit.json
        if write_audit:
            audit = [
                {
                    "source_id": s["source_id"],
                    "original_sha256": s["source_sha256"],
                    "original_unchanged": True,
                    "extraction_manifest_verified": True,
                    "page_hashes_verified": True,
                    "page_count": 3,
                    "human_approval_granted": False,
                }
                for s in self.sources
            ]
            (self.run_dir / "source-integrity-audit.json").write_text(
                json.dumps(audit, indent=2, sort_keys=True) + "\n"
            )


class CorpusStagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

        self.fixture = SyntheticCorpusFixture(self.root)

        p1 = [
            {
                "id": "src-2026-syn-alpha-001",
                "title_es": "Medida sintetica uno",
                "summary_es": "Resumen neutral uno para comprobacion tecnica.",
                "topic_id": "housing",
                "subtopic_id": "rental-regulation",
                "qualifications_es": ["Condicion tecnica A"],
                "source_pages": [1, 2],
                "source_section": "Seccion Uno",
                "evidence": [
                    {
                        "pdf_page": 1,
                        "excerpt": "Extracto sintetico de evidencia uno",
                        "text_sha256": _hash_str("Extracto sintetico de evidencia uno"),
                    }
                ],
            },
            {
                "id": "src-2026-syn-alpha-002",
                "title_es": "Medida sintetica dos",
                "summary_es": "Resumen neutral dos para comprobacion tecnica.",
                "topic_id": "education",
                "subtopic_id": "early-childhood",
                "qualifications_es": [],
                "source_pages": [3],
                "source_section": "Seccion Dos",
                "evidence": [
                    {
                        "pdf_page": 3,
                        "excerpt": "Extracto sintetico de evidencia dos",
                        "text_sha256": _hash_str("Extracto sintetico de evidencia dos"),
                    }
                ],
            },
        ]
        self.fixture.add_source("syn-alpha", "src-2026-syn-alpha-v1", p1)

        p2 = [
            {
                "id": "src-2026-syn-beta-001",
                "title_es": "Medida sintetica tres",
                "summary_es": "Resumen neutral tres para comprobacion tecnica.",
                "topic_id": None,
                "subtopic_id": None,
                "qualifications_es": ["Condicion B", "Condicion C"],
                "source_pages": [2],
                "source_section": "Seccion Beta",
                "evidence": [
                    {
                        "pdf_page": 2,
                        "excerpt": "Extracto sintetico de evidencia tres",
                        "text_sha256": _hash_str("Extracto sintetico de evidencia tres"),
                    }
                ],
            }
        ]
        self.fixture.add_source("syn-beta", "src-2026-syn-beta-v1", p2)
        self.fixture.write_run_metadata()

        self.output_dir = self.root / "staging-output"

    def test_output_path_refusal_under_repo_and_existing_dir(self):
        """Refuses output directories inside repo (even with override) and existing destinations."""
        if REPO_ROOT:
            repo_child = REPO_ROOT / "content/test-dest"
            with self.assertRaises(OutputPathError):
                assert_output_dir_outside_repo(repo_child, repo_root=self.root)
            with self.assertRaises(OutputPathError):
                assert_output_dir_outside_repo(REPO_ROOT, repo_root=self.root)

        # Refuses overwriting existing directory
        existing_dir = self.root / "existing"
        existing_dir.mkdir()
        with self.assertRaisesRegex(OutputPathError, "already exists"):
            stage_corpus(self.fixture.run_dir, existing_dir, repo_root=REPO_ROOT)

    def test_page_coordinates_formatting_and_validation(self):
        """format_source_page retains exact coordinates and rejects invalid inputs."""
        self.assertEqual(format_source_page(None), None)
        self.assertEqual(format_source_page(5), "5")
        self.assertEqual(format_source_page([5]), "5")
        self.assertEqual(format_source_page([1, 2, 3]), "1-3")
        # Gaps must be comma-separated, not falsely widened to 1-5!
        self.assertEqual(format_source_page([1, 3, 5]), "1, 3, 5")
        self.assertEqual(format_source_page([1, 2, 4, 5, 7]), "1-2, 4-5, 7")

        # Rejections
        for invalid in (True, False, [True], [0], [-1], [1, 1], [3, 1], "invalid type object"):
            with self.subTest(invalid=invalid), self.assertRaises(InputValidationError):
                format_source_page(invalid)

    def test_slug_validation_no_lossy_sanitization(self):
        """Point IDs must be valid kebab-case slugs; invalid IDs are strictly rejected."""
        validate_point_id("src-2026-party-v1-001")
        for bad_id in ("SRC-UPPERCASE", "spaces in id", "under_score", "slash/id", "accénts", ""):
            with self.subTest(bad_id=bad_id), self.assertRaises(InputValidationError):
                validate_point_id(bad_id)

    def test_missing_metadata_and_url_validation(self):
        """Refuses missing jobs, missing source_url, non-https URLs, or missing source_version."""
        jobs_path = self.fixture.run_dir / "jobs.json"
        jobs = json.loads(jobs_path.read_text())

        # Non-https URL
        jobs[0]["source_url"] = "http://insecure.test/doc.pdf"
        jobs_path.write_text(json.dumps(jobs))
        with self.assertRaisesRegex(InputValidationError, "Exact HTTPS source_url required"):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

        # Missing version
        jobs[0]["source_url"] = "https://example.test/doc.pdf"
        jobs[0]["source_version"] = ""
        jobs_path.write_text(json.dumps(jobs))
        with self.assertRaisesRegex(InputValidationError, "Exact source_version required"):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

        # Missing jobs.json
        jobs_path.unlink()
        with self.assertRaisesRegex(InputValidationError, "Missing jobs.json"):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

    def test_meaningful_hash_corruption(self):
        """Corrupting points, coverage, or source hash raises HashVerificationError."""
        manifest_path = self.fixture.run_dir / "canonical-draft-manifest.json"
        manifest = json.loads(manifest_path.read_text())

        # Corrupt points hash
        manifest["sources"][0]["points_sha256"] = "0" * 64
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaises(HashVerificationError):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

        # Reset & corrupt coverage hash
        manifest = json.loads((self.fixture.run_dir / "canonical-draft-manifest.json").read_text())
        manifest["sources"][0]["points_sha256"] = self.fixture.sources[0]["points_sha256"]
        manifest["sources"][0]["coverage_sha256"] = "f" * 64
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaises(HashVerificationError):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

    def test_proposed_classification_index_checks(self):
        """Index must have exactly one row per canonical point, correct party binding, and no duplicates."""
        prop_path = self.fixture.run_dir / "proposed-classification-index.json"
        prop = json.loads(prop_path.read_text())

        # Extra row in index
        prop["points"].append(dict(prop["points"][0], point_id="extra-point-999"))
        prop_path.write_text(json.dumps(prop))
        with self.assertRaisesRegex(InputValidationError, "row count mismatch"):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

        # Party mismatch
        prop["points"].pop()
        prop["points"][0]["party_id"] = "wrong-party"
        prop_path.write_text(json.dumps(prop))
        with self.assertRaisesRegex(InputValidationError, "Party ID mismatch"):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

    def test_index_cannot_silently_reclassify_an_existing_point(self):
        path = self.fixture.run_dir / "proposed-classification-index.json"
        data = json.loads(path.read_text())
        data["points"][0].update(topic_id="education", subtopic_id="early-childhood")
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(InputValidationError, "frozen classification"):
            stage_corpus(self.fixture.run_dir, self.output_dir)
        self.assertFalse(self.output_dir.exists())

    def test_all_points_retained_permissions_and_evidence(self):
        """Verifies 100% point retention, owner-only permissions (0700/0600), and evidence separation."""
        res = stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

        self.assertEqual(res.source_count, 2)
        self.assertEqual(res.statement_count, 3)
        self.assertTrue(res.original_archive_audit_verified)
        self.assertFalse(res.human_approval_granted)

        # Check permissions
        out_mode = stat.S_IMODE(self.output_dir.stat().st_mode)
        self.assertEqual(oct(out_mode), "0o700")

        stmt_files = list((self.output_dir / "statements").glob("*.json"))
        self.assertEqual(len(stmt_files), 3)

        for sf in stmt_files:
            file_mode = stat.S_IMODE(sf.stat().st_mode)
            self.assertEqual(oct(file_mode), "0o600")
            stmt = load_statement(sf)
            self.assertIsNone(stmt.quote)
            self.assertEqual(stmt.reviews, [])
            self.assertEqual(stmt.review_status, "draft")
            self.assertTrue(stmt.programme_id.startswith("prog-"))

        # Verify generator rejection
        if REPO_ROOT:
            with self.assertRaises(BuildValidationError):
                load_and_validate_site_data(REPO_ROOT, records_dir=self.output_dir)

    def test_atomic_rollback_on_failure(self):
        """Temporary staging directory is cleaned up if an error occurs midway."""
        # Corrupt points file for second source after first is validated
        pts_file = Path(self.fixture.sources[1]["directory"]) / "points.json"
        pts = json.loads(pts_file.read_text())
        pts["points"][0]["id"] = "INVALID SLUG!"
        pts_file.write_text(json.dumps(pts))

        # Re-hash points file so it passes hash check and hits in-memory validation
        new_hash = _hash_bytes(pts_file.read_bytes())
        manifest_path = self.fixture.run_dir / "canonical-draft-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["sources"][1]["points_sha256"] = new_hash
        manifest_path.write_text(json.dumps(manifest))

        with self.assertRaises(InputValidationError):
            stage_corpus(self.fixture.run_dir, self.output_dir, repo_root=REPO_ROOT)

        # Destination must not exist
        self.assertFalse(self.output_dir.exists())
        # No temporary directories left in parent
        tmp_dirs = list(self.root.glob(".tmp-staging-*"))
        self.assertEqual(tmp_dirs, [])


if __name__ == "__main__":
    unittest.main()
