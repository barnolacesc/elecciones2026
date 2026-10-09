"""Tests for programme, statement, relationship, coverage, and correction schemas.

Verifies:
- JSON Schema Draft 2020-12 compliance for all 5 schemas.
- Valid versioned fixtures for all record types.
- Invalid record detection and specific diagnostics.
- Cross-election isolation and immutable election ID (Task 1.4).
- Dependent relationship invalidation engine upon correction (Task 1.3 / E1.1).
"""

import json
from pathlib import Path
import unittest

from elecciones2026.methodology import ProgrammeStatus, load_programme
from elecciones2026.schemas import (
    CandidacyCoverageRecord,
    CorrectionRecord,
    ElectionCoverageSnapshot,
    RelationshipRecord,
    ReviewRecord,
    StatementRecord,
    invalidate_dependent_relationships,
    load_correction,
    load_coverage_record,
    load_coverage_snapshot,
    load_relationship,
    load_statement,
    validate_all_content,
    validate_any_record,
    validate_schema_document,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
SCHEMAS_DIR = CONTENT_DIR / "schemas"
EXAMPLES_DIR = CONTENT_DIR / "examples"


class TestJsonSchemaDefinitions(unittest.TestCase):
    """Verify all 5 JSON schemas conform to Draft 2020-12 requirements."""

    def test_all_five_schema_files_exist(self):
        expected_schemas = [
            "programme.schema.json",
            "statement.schema.json",
            "relationship.schema.json",
            "coverage.schema.json",
            "correction.schema.json",
        ]
        for name in expected_schemas:
            schema_file = SCHEMAS_DIR / name
            self.assertTrue(schema_file.exists(), f"Schema file {name} must exist in content/schemas/")
            errors = validate_schema_document(schema_file)
            self.assertEqual(errors, [], f"Schema {name} failed validation: {errors}")

    def test_schema_identifiers_and_metadata(self):
        for schema_file in SCHEMAS_DIR.glob("*.schema.json"):
            with schema_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("https://json-schema.org/draft/2020-12/schema", data["$schema"])
            self.assertTrue(data["$id"].startswith("https://elecciones2026.es/schemas/"))
            self.assertEqual(data["type"], "object")
            self.assertIsInstance(data["properties"], dict)
            self.assertIsInstance(data["required"], list)
            self.assertFalse(data.get("additionalProperties", True), f"{schema_file.name} must disallow additionalProperties")


class TestProgrammeSchema(unittest.TestCase):
    """Verify programme provenance and lifecycle record validation."""

    def test_valid_programme_fixtures(self):
        prog_dir = EXAMPLES_DIR / "programmes"
        for prog_file in prog_dir.glob("*.json"):
            prog = load_programme(prog_file)
            self.assertEqual(prog.schema_version, "1.0.0")
            errors = prog.validate(target_election_id=prog.election_id)
            self.assertEqual(errors, [], f"Fixture {prog_file.name} failed: {errors}")

    def test_invalid_official_programme_missing_hash(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-programme-missing-hash.json"
        self.assertTrue(inv_file.exists())
        prog = load_programme(inv_file)
        errors = prog.validate()
        self.assertTrue(any("valid 64-character hex SHA-256 hash" in e for e in errors))


class TestStatementSchema(unittest.TestCase):
    """Verify statement / claim position schema, provenance, and dual review rules."""

    def test_valid_approved_proposal_fixture(self):
        stmt_file = EXAMPLES_DIR / "statements" / "statement-housing-proposal-approved.json"
        self.assertTrue(stmt_file.exists())
        stmt = load_statement(stmt_file)
        self.assertEqual(stmt.review_status, "approved")
        self.assertEqual(len(stmt.reviews), 2)
        errors = stmt.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_valid_not_found_absence_fixture(self):
        stmt_file = EXAMPLES_DIR / "statements" / "statement-housing-not-found.json"
        self.assertTrue(stmt_file.exists())
        stmt = load_statement(stmt_file)
        self.assertEqual(stmt.statement_type, "not_found")
        self.assertIsNone(stmt.source_page)
        self.assertIsNone(stmt.source_section)
        self.assertIsNone(stmt.quote)
        errors = stmt.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_valid_qualified_proposal_fixture(self):
        stmt_file = EXAMPLES_DIR / "statements" / "statement-economy-qualification.json"
        self.assertTrue(stmt_file.exists())
        stmt = load_statement(stmt_file)
        self.assertGreater(len(stmt.qualifications), 0)
        errors = stmt.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_valid_2023_pilot_statement_labeled_2023(self):
        stmt_file = EXAMPLES_DIR / "statements" / "statement-2023-pilot-proposal.json"
        self.assertTrue(stmt_file.exists())
        stmt = load_statement(stmt_file)
        self.assertEqual(stmt.election_id, "es-gen-2023")
        errors = stmt.validate(target_election_id="es-gen-2023")
        self.assertEqual(errors, [])

        # Mismatch against 2026
        mismatch_errors = stmt.validate(target_election_id="es-gen-2026")
        self.assertTrue(any("election mismatch" in e for e in mismatch_errors))

    def test_reject_unreviewed_statement_marked_approved(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-statement-unreviewed.json"
        self.assertTrue(inv_file.exists())
        stmt = load_statement(inv_file)
        errors = stmt.validate()
        self.assertTrue(any("requires dual approval by at least two distinct reviewers" in e for e in errors))

    def test_reject_not_found_with_page_coordinates(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-statement-not-found-with-page.json"
        self.assertTrue(inv_file.exists())
        stmt = load_statement(inv_file)
        errors = stmt.validate()
        self.assertTrue(any("must not specify source_page or source_section" in e for e in errors))

    def test_reject_explicit_proposal_missing_provenance(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-statement-missing-provenance.json"
        self.assertTrue(inv_file.exists())
        stmt = load_statement(inv_file)
        errors = stmt.validate()
        self.assertTrue(any("must specify source_url" in e for e in errors))
        self.assertTrue(any("must specify at least one of source_page or source_section" in e for e in errors))

    def test_reject_invalid_topic_taxonomy(self):
        stmt = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-invalid-topic",
            party_id="partido-a",
            topic_id="non-existent-topic",
            subtopic_id="sub",
            statement_type="explicit_proposal",
            summary="Invalid topic",
            review_status="draft",
        )
        errors = stmt.validate()
        self.assertTrue(any("topic_id 'non-existent-topic' must be one of" in e for e in errors))


class TestRelationshipSchema(unittest.TestCase):
    """Verify policy comparison relationship schema and cross-election rules."""

    def setUp(self):
        self.statements_by_id = {}
        for stmt_file in (EXAMPLES_DIR / "statements").glob("*.json"):
            s = load_statement(stmt_file)
            self.statements_by_id[s.id] = s

    def test_valid_agreement_relationship(self):
        rel_file = EXAMPLES_DIR / "relationships" / "relationship-housing-rent-control-agreement.json"
        self.assertTrue(rel_file.exists())
        rel = load_relationship(rel_file)
        self.assertEqual(rel.relationship_type, "agreement")
        self.assertEqual(len(rel.party_ids), 2)
        errors = rel.validate(target_election_id="es-gen-2026", statements_by_id=self.statements_by_id)
        self.assertEqual(errors, [])

    def test_valid_partial_overlap_relationship(self):
        rel_file = EXAMPLES_DIR / "relationships" / "relationship-housing-youth-subsidy-overlap.json"
        self.assertTrue(rel_file.exists())
        rel = load_relationship(rel_file)
        self.assertEqual(rel.relationship_type, "partial_overlap")
        errors = rel.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_valid_single_party_relationship(self):
        rel_file = EXAMPLES_DIR / "relationships" / "relationship-economy-minimum-wage-divergence.json"
        self.assertTrue(rel_file.exists())
        rel = load_relationship(rel_file)
        self.assertEqual(rel.relationship_type, "single_party")
        errors = rel.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_task_1_4_reject_cross_election_relationship(self):
        """Task 1.4: verify a 2023 source cannot appear in a 2026 comparison."""
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-relationship-cross-election.json"
        self.assertTrue(inv_file.exists())
        rel = load_relationship(inv_file)
        errors = rel.validate(statements_by_id=self.statements_by_id)
        self.assertTrue(any("cross-election error" in e for e in errors))
        self.assertTrue(any("cannot reference statement 'stmt-pilot-pp-housing-2023' from election 'es-gen-2023'" in e for e in errors))

    def test_reject_agreement_with_not_found_statement(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-relationship-agreement-with-not-found.json"
        self.assertTrue(inv_file.exists())
        rel = load_relationship(inv_file)
        errors = rel.validate(statements_by_id=self.statements_by_id)
        self.assertTrue(any("agreement cannot be asserted with not_found statement" in e for e in errors))

    def test_reject_invalidated_status_without_reason(self):
        rel = RelationshipRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="rel-no-reason",
            topic_id="housing",
            subtopic_id="rental-regulation",
            measure_label="Measure",
            party_ids=["partido-a", "partido-b"],
            statement_ids=["stmt-1", "stmt-2"],
            relationship_type="agreement",
            summary="Summary",
            review_status="invalidated",
            status="invalidated",
            invalidation_reason=None,
        )
        errors = rel.validate()
        self.assertTrue(any("invalidated status requires invalidation_reason" in e for e in errors))


class TestCoverageSchema(unittest.TestCase):
    """Verify candidacy coverage and election snapshot validation."""

    def test_valid_election_coverage_snapshot(self):
        snap_file = EXAMPLES_DIR / "coverage" / "coverage-2026-snapshot.json"
        self.assertTrue(snap_file.exists())
        snap = load_coverage_snapshot(snap_file)
        self.assertEqual(len(snap.candidacies), 4)
        errors = snap.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_valid_individual_coverage_records(self):
        cov_a = load_coverage_record(EXAMPLES_DIR / "coverage" / "coverage-party-a-official.json")
        self.assertTrue(cov_a.has_verified_programme)
        self.assertEqual(cov_a.validate(), [])

        cov_d = load_coverage_record(EXAMPLES_DIR / "coverage" / "coverage-party-d-missing.json")
        self.assertFalse(cov_d.has_verified_programme)
        self.assertEqual(cov_d.total_statements, 0)
        self.assertEqual(cov_d.validate(), [])

    def test_reject_missing_coverage_with_proposals(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-coverage-missing-with-proposals.json"
        self.assertTrue(inv_file.exists())
        cov = load_coverage_record(inv_file)
        errors = cov.validate()
        self.assertTrue(any("missing status must have has_verified_programme=false" in e for e in errors))
        self.assertTrue(any("missing status must have total_statements=0" in e for e in errors))
        self.assertTrue(any("missing status must have empty topics_covered" in e for e in errors))


class TestCorrectionSchemaAndInvalidation(unittest.TestCase):
    """Verify correction schema, dual review gate, and relationship invalidation engine."""

    def test_valid_topic_reclassification_correction(self):
        corr_file = EXAMPLES_DIR / "corrections" / "correction-topic-reclassification.json"
        self.assertTrue(corr_file.exists())
        corr = load_correction(corr_file)
        self.assertEqual(corr.correction_type, "topic_reclassification")
        self.assertNotEqual(corr.reviewed_by, corr.approved_by)
        errors = corr.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_valid_citation_update_correction(self):
        corr_file = EXAMPLES_DIR / "corrections" / "correction-source-page-update.json"
        self.assertTrue(corr_file.exists())
        corr = load_correction(corr_file)
        self.assertEqual(corr.correction_type, "citation_update")
        errors = corr.validate(target_election_id="es-gen-2026")
        self.assertEqual(errors, [])

    def test_reject_single_reviewer_correction(self):
        inv_file = EXAMPLES_DIR / "invalid" / "invalid-correction-single-reviewer.json"
        self.assertTrue(inv_file.exists())
        corr = load_correction(inv_file)
        errors = corr.validate()
        self.assertTrue(any("reviewed_by and approved_by must be distinct reviewers" in e for e in errors))

    def test_reject_identical_prior_and_corrected_state(self):
        corr = CorrectionRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="cor-identical",
            target_type="statement",
            target_id="stmt-1",
            correction_type="factual_error",
            prior_state={"summary": "Same"},
            corrected_state={"summary": "Same"},
            reason="No change actually made",
            correction_date="2026-10-18",
            reviewed_by="rev-1",
            approved_by="rev-2",
        )
        errors = corr.validate()
        self.assertTrue(any("prior_state and corrected_state must not be identical" in e for e in errors))

    def test_relationship_invalidation_engine(self):
        """Verify correcting a source statement marks dependent comparison relationships invalidated."""
        rel1 = RelationshipRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="rel-active-1",
            topic_id="housing",
            subtopic_id="rental-regulation",
            measure_label="Rent Cap",
            party_ids=["partido-a", "partido-b"],
            statement_ids=["stmt-party-a-housing-001", "stmt-party-b-housing-001"],
            relationship_type="agreement",
            summary="Agreement on rent cap",
            review_status="approved",
            status="active",
        )
        rel2 = RelationshipRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="rel-unrelated-2",
            topic_id="education",
            subtopic_id="vocational-training",
            measure_label="FP funding",
            party_ids=["partido-a", "coalicion-c"],
            statement_ids=["stmt-party-a-edu-001", "stmt-coalicion-c-edu-001"],
            relationship_type="partial_overlap",
            summary="FP funding overlap",
            review_status="approved",
            status="active",
        )

        invalidation_reason = "Statement stmt-party-a-housing-001 was reclassified under correction cor-2026-001"
        updated_rels = invalidate_dependent_relationships(
            target_id="stmt-party-a-housing-001",
            relationships=[rel1, rel2],
            reason=invalidation_reason,
            correction_id="cor-2026-001",
        )

        self.assertEqual(len(updated_rels), 2)
        # rel1 must be invalidated
        self.assertEqual(updated_rels[0].status, "invalidated")
        self.assertEqual(updated_rels[0].review_status, "invalidated")
        self.assertEqual(updated_rels[0].invalidation_reason, invalidation_reason)
        self.assertEqual(updated_rels[0].invalidated_by_correction_id, "cor-2026-001")
        # rel2 remains active
        self.assertEqual(updated_rels[1].status, "active")
        self.assertEqual(updated_rels[1].review_status, "approved")
        self.assertIsNone(updated_rels[1].invalidation_reason)


class TestValidateAllFixtures(unittest.TestCase):
    """Run full repository schema and fixture validation pass."""

    def test_all_schemas_and_fixtures_pass(self):
        passed, failed, errors = validate_all_content(ROOT_DIR)
        self.assertEqual(failed, 0, f"Validation failures encountered:\n" + "\n".join(errors))
        self.assertGreaterEqual(passed, 30, "Expected at least 30 passing checks across schemas and fixtures")


if __name__ == "__main__":
    unittest.main()
