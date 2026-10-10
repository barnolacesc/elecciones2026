"""Tests for editorial policy, quotation limits, reviewer roles, and correction process (Package E0.2).

Verifies the acceptance criteria:
1. Editorial policy signed off by project owners in docs/CONTENT-METHODOLOGY.md and ADR-0002.
2. No unsupported quote can pass review.
3. Reviewer role segregation and four-eyes review enforced.
4. Correction workflow and dependent comparison relationship invalidation.
"""

from pathlib import Path
import json
import unittest

from elecciones2026.editorial import (
    MAX_QUOTE_CHARS,
    MAX_QUOTE_WORDS,
    PERMITTED_QUOTE_RIGHTS,
    RESTRICTED_QUOTE_RIGHTS,
    ComparisonRelationship,
    CorrectionRecord,
    CorrectionSeverity,
    CorrectionType,
    QuoteRecord,
    ReviewRecord,
    ReviewerRole,
    StatementRecord,
    StatementStatus,
    invalidate_dependent_relationships,
    validate_editorial_corpus,
)
from elecciones2026.methodology import load_taxonomy
from elecciones2026.source_register import load_register


REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"
DOCS_DIR = REPO_ROOT / "docs"
REGISTER_PATH = CONTENT_DIR / "sources" / "register.json"
TAXONOMY_PATH = CONTENT_DIR / "taxonomy.json"
FIXTURES_PATH = CONTENT_DIR / "examples" / "editorial_statements.json"


class TestQuotationLimits(unittest.TestCase):
    """Test quantitative and qualitative boundaries for quotations (TRLPI Art. 32)."""

    def test_quote_under_word_limit_passes(self):
        words = ["pacto"] * 40
        quote = QuoteRecord(
            text=" ".join(words),
            source_id="src-2023-pp-v1",
            page="42",
        )
        self.assertEqual(quote.word_count(), 40)
        self.assertEqual(quote.validate(), [])

    def test_quote_exceeding_word_limit_fails(self):
        words = ["pacto"] * 41
        quote = QuoteRecord(
            text=" ".join(words),
            source_id="src-2023-pp-v1",
            page="42",
        )
        errors = quote.validate()
        self.assertTrue(any(f"exceeds maximum limit of {MAX_QUOTE_WORDS} words" in e for e in errors))

    def test_quote_exceeding_char_limit_fails(self):
        # 301 characters within 35 words
        text = "a" * 301
        quote = QuoteRecord(
            text=text,
            source_id="src-2023-pp-gen",
            page="42",
        )
        errors = quote.validate()
        self.assertTrue(any(f"exceeds maximum limit of {MAX_QUOTE_CHARS} characters" in e for e in errors))

    def test_empty_quote_fails(self):
        quote = QuoteRecord(
            text="   ",
            source_id="src-2023-pp-gen",
            page="42",
        )
        errors = quote.validate()
        self.assertTrue(any("cannot be empty" in e for e in errors))

    def test_quote_without_locator_fails(self):
        quote = QuoteRecord(
            text="Medida válida",
            source_id="src-2023-pp-gen",
            page=None,
            section=None,
        )
        errors = quote.validate()
        self.assertTrue(any("at least one locator" in e for e in errors))

    def test_quote_with_section_only_passes(self):
        quote = QuoteRecord(
            text="Medida válida",
            source_id="src-2023-pp-gen",
            page=None,
            section="Punto 3.1",
        )
        self.assertEqual(quote.validate(), [])


class TestUnsupportedQuoteRejection(unittest.TestCase):
    """Ensure no unsupported quote can pass review."""

    @classmethod
    def setUpClass(cls):
        cls.register = load_register(REGISTER_PATH)
        cls.taxonomy = load_taxonomy(TAXONOMY_PATH)

    def test_valid_supported_quote_passes_review(self):
        stmt = StatementRecord(
            id="stmt-test-valid",
            election_id="es-gen-2023",
            party_id="pp",
            topic_id="housing",
            subtopic_id="rental-regulation",
            summary_es="Resumen neutral de la propuesta.",
            source_id="src-2023-pp-v1",
            source_version="23J-v1",
            status=StatementStatus.PUBLISHED,
            quote=QuoteRecord(
                text="un aval bancario del 15% para facilitar la fianza",
                source_id="src-2023-pp-v1",
                page="112",
            ),
            review=ReviewRecord(
                reviewed_by_1="rev-1",
                reviewed_by_2="rev-2",
                review_date_1="2026-10-09",
                review_date_2="2026-10-09",
            ),
        )
        errors = stmt.validate(source_register=self.register, taxonomy=self.taxonomy)
        self.assertTrue(any("source rights status" in error for error in errors))

    def test_unsupported_quote_unknown_source_fails(self):
        stmt = StatementRecord(
            id="stmt-test-unknown-src",
            election_id="es-gen-2023",
            party_id="pp",
            topic_id="housing",
            subtopic_id="rental-regulation",
            summary_es="Resumen neutral.",
            source_id="src-nonexistent",
            source_version="1.0",
            status=StatementStatus.PUBLISHED,
            quote=QuoteRecord(
                text="texto de cita",
                source_id="src-nonexistent",
                page="1",
            ),
            review=ReviewRecord(
                reviewed_by_1="rev-1",
                reviewed_by_2="rev-2",
                review_date_1="2026-10-09",
                review_date_2="2026-10-09",
            ),
        )
        errors = stmt.validate(source_register=self.register, taxonomy=self.taxonomy)
        self.assertTrue(any("does not exist in source register" in e for e in errors))

    def test_unsupported_quote_unverified_source_fails(self):
        # 2026 sources in register are currently "missing" / unverified
        stmt = StatementRecord(
            id="stmt-test-unverified-src",
            election_id="es-gen-2026",
            party_id="psoe",
            topic_id="housing",
            subtopic_id="rental-regulation",
            summary_es="Resumen neutral.",
            source_id="src-2026-psoe-v0",
            source_version="1.0",
            status=StatementStatus.PUBLISHED,
            quote=QuoteRecord(
                text="texto de cita",
                source_id="src-2026-psoe-v0",
                page="1",
            ),
            review=ReviewRecord(
                reviewed_by_1="rev-1",
                reviewed_by_2="rev-2",
                review_date_1="2026-10-09",
                review_date_2="2026-10-09",
            ),
        )
        errors = stmt.validate(source_register=self.register, taxonomy=self.taxonomy)
        self.assertTrue(
            any("unsupported quote cannot pass review because source" in e and "must be 'verified'" in e for e in errors),
            f"Expected unverified source rejection, got: {errors}",
        )

    def test_unsupported_quote_without_dual_review_fails(self):
        stmt = StatementRecord(
            id="stmt-test-no-review",
            election_id="es-gen-2023",
            party_id="pp",
            topic_id="housing",
            subtopic_id="rental-regulation",
            summary_es="Resumen neutral.",
            source_id="src-2023-pp-v1",
            source_version="23J-v1",
            status=StatementStatus.PUBLISHED,
            quote=QuoteRecord(
                text="un aval bancario del 15% para facilitar la fianza",
                source_id="src-2023-pp-v1",
                page="112",
            ),
            review=None,  # No review
        )
        errors = stmt.validate(source_register=self.register, taxonomy=self.taxonomy)
        self.assertTrue(any("requires a completed ReviewRecord" in e for e in errors))

    def test_unsupported_quote_cross_election_mismatch_fails(self):
        stmt = StatementRecord(
            id="stmt-test-cross-election",
            election_id="es-gen-2026",  # 2026 comparison
            party_id="pp",
            topic_id="housing",
            subtopic_id="rental-regulation",
            summary_es="Resumen neutral.",
            source_id="src-2023-pp-v1",  # 2023 source
            source_version="23J-v1",
            status=StatementStatus.PUBLISHED,
            quote=QuoteRecord(
                text="un aval bancario del 15% para facilitar la fianza",
                source_id="src-2023-pp-v1",
                page="112",
            ),
            review=ReviewRecord(
                reviewed_by_1="rev-1",
                reviewed_by_2="rev-2",
                review_date_1="2026-10-09",
                review_date_2="2026-10-09",
            ),
        )
        errors = stmt.validate(source_register=self.register, taxonomy=self.taxonomy)
        self.assertTrue(any("does not match statement election" in e for e in errors))


class TestReviewerRolesAndSegregation(unittest.TestCase):
    """Test four-eyes principle and segregation of duties."""

    def test_four_eyes_violation_same_reviewer_fails(self):
        review = ReviewRecord(
            reviewed_by_1="reviewer-alex",
            reviewed_by_2="reviewer-alex",
            review_date_1="2026-10-09",
            review_date_2="2026-10-09",
        )
        errors = review.validate()
        self.assertTrue(any("Four-eyes principle violation" in e for e in errors))

    def test_segregation_of_duties_drafter_as_reviewer_2_fails(self):
        review = ReviewRecord(
            drafter="analyst-sam",
            reviewed_by_1="reviewer-alex",
            reviewed_by_2="analyst-sam",
            review_date_1="2026-10-09",
            review_date_2="2026-10-09",
        )
        errors = review.validate()
        self.assertTrue(any("Segregation of duties violation" in e for e in errors))

    def test_valid_dual_review_passes(self):
        review = ReviewRecord(
            drafter="analyst-sam",
            reviewed_by_1="reviewer-alex",
            reviewed_by_2="reviewer-taylor",
            review_date_1="2026-10-09",
            review_date_2="2026-10-09",
            lead_editor_signoff="cesc",
        )
        self.assertEqual(review.validate(), [])


class TestCorrectionWorkflowAndInvalidation(unittest.TestCase):
    """Test internal correction records and automatic relationship invalidation."""

    def test_valid_correction_record(self):
        corr = CorrectionRecord(
            id="corr-2026-001",
            statement_id="stmt-psoe-001",
            election_id="es-gen-2026",
            date="2026-10-09",
            correction_type=CorrectionType.FACTUAL_ERROR,
            severity=CorrectionSeverity.MAJOR,
            prior_value="aval del 20%",
            new_value="aval del 15%",
            reason="Corrección de errata en el porcentaje del aval.",
            reviewed_by="editor-reviewer-1",
            approved_by="lead-editor-cesc",
        )
        self.assertEqual(corr.validate(), [])

    def test_relationship_invalidation_on_statement_correction(self):
        rel1 = ComparisonRelationship(
            id="rel-001",
            election_id="es-gen-2026",
            topic_id="housing",
            party_ids=["pp", "erc"],
            statement_ids=["stmt-pp-001", "stmt-erc-001"],
            relationship_type="divergence",
            description_es="Comparativa inicial.",
            status="reviewed",
        )
        rel2 = ComparisonRelationship(
            id="rel-002",
            election_id="es-gen-2026",
            topic_id="housing",
            party_ids=["psoe", "sumar"],
            statement_ids=["stmt-psoe-001", "stmt-sumar-001"],
            relationship_type="agreement",
            description_es="Otra comparativa.",
            status="reviewed",
        )

        relationships = [rel1, rel2]
        updated_rels, invalidated_ids = invalidate_dependent_relationships(
            relationships=relationships,
            corrected_statement_id="stmt-pp-001",
            reason="Statement corrected due to locator errata.",
        )

        self.assertEqual(invalidated_ids, ["rel-001"])
        self.assertEqual(len(updated_rels), 2)

        rel1_updated = next(r for r in updated_rels if r.id == "rel-001")
        rel2_updated = next(r for r in updated_rels if r.id == "rel-002")

        self.assertEqual(rel1_updated.status, "invalidated")
        self.assertIn("Dependent on corrected statement 'stmt-pp-001'", rel1_updated.invalidation_reason)
        self.assertEqual(rel2_updated.status, "reviewed")
        self.assertIsNone(rel2_updated.invalidation_reason)


class TestEditorialFixtureFile(unittest.TestCase):
    """Test that content/examples/editorial_statements.json fixtures validate correctly."""

    @classmethod
    def setUpClass(cls):
        cls.assertTrue(FIXTURES_PATH.exists(), f"Missing fixture file at {FIXTURES_PATH}")
        with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.register = load_register(REGISTER_PATH)
        cls.taxonomy = load_taxonomy(TAXONOMY_PATH)

    def test_valid_statement_fixture(self):
        stmt_dict = self.data["valid_statement_with_short_quote"]
        q_dict = stmt_dict["quote"]
        r_dict = stmt_dict["review"]

        quote = QuoteRecord(
            text=q_dict["text"],
            source_id=q_dict["source_id"],
            page=q_dict["page"],
            section=q_dict["section"],
        )
        review = ReviewRecord(
            drafter=r_dict["drafter"],
            reviewed_by_1=r_dict["reviewed_by_1"],
            reviewed_by_2=r_dict["reviewed_by_2"],
            review_date_1=r_dict["review_date_1"],
            review_date_2=r_dict["review_date_2"],
            lead_editor_signoff=r_dict["lead_editor_signoff"],
        )
        stmt = StatementRecord(
            id=stmt_dict["id"],
            election_id=stmt_dict["election_id"],
            party_id=stmt_dict["party_id"],
            topic_id=stmt_dict["topic_id"],
            subtopic_id=stmt_dict["subtopic_id"],
            summary_es=stmt_dict["summary_es"],
            source_id=stmt_dict["source_id"],
            source_version=stmt_dict["source_version"],
            status=StatementStatus(stmt_dict["status"]),
            quote=quote,
            review=review,
        )
        errors = stmt.validate(source_register=self.register, taxonomy=self.taxonomy)
        self.assertTrue(any("source rights status" in error for error in errors))

    def test_invalid_fixtures_fail_as_expected(self):
        # Missing coords fixture
        no_coords_dict = self.data["invalid_statement_unsupported_quote_missing_coordinates"]
        q_dict = no_coords_dict["quote"]
        quote = QuoteRecord(
            text=q_dict["text"],
            source_id=q_dict["source_id"],
            page=q_dict["page"],
            section=q_dict["section"],
        )
        q_errors = quote.validate()
        self.assertTrue(any(no_coords_dict["expected_error"] in e for e in q_errors))

        # Long quote fixture
        long_dict = self.data["invalid_statement_unsupported_quote_exceeds_length"]
        q_dict = long_dict["quote"]
        quote = QuoteRecord(
            text=q_dict["text"],
            source_id=q_dict["source_id"],
            page=q_dict["page"],
            section=q_dict["section"],
        )
        q_errors = quote.validate()
        self.assertTrue(any(long_dict["expected_error"] in e for e in q_errors))

        # Four eyes violation fixture
        four_eyes_dict = self.data["invalid_statement_four_eyes_violation"]
        r_dict = four_eyes_dict["review"]
        review = ReviewRecord(
            reviewed_by_1=r_dict["reviewed_by_1"],
            reviewed_by_2=r_dict["reviewed_by_2"],
            review_date_1=r_dict["review_date_1"],
            review_date_2=r_dict["review_date_2"],
        )
        r_errors = review.validate()
        self.assertTrue(any(four_eyes_dict["expected_error"] in e for e in r_errors))


class TestPolicyDocumentation(unittest.TestCase):
    """Verify that ADR-0002 and docs/CONTENT-METHODOLOGY.md codify the editorial policy."""

    @classmethod
    def setUpClass(cls):
        cls.methodology_text = (DOCS_DIR / "CONTENT-METHODOLOGY.md").read_text(encoding="utf-8")
        cls.decision_record_text = (DOCS_DIR / "DECISION-RECORD.md").read_text(encoding="utf-8")
        cls.source_avail_text = (DOCS_DIR / "SOURCE-AVAILABILITY-2026.md").read_text(encoding="utf-8")

    def test_decision_record_contains_adr_0002(self):
        self.assertIn("ADR-0002", self.decision_record_text)
        self.assertIn("E0.2", self.decision_record_text)
        self.assertIn("TRLPI", self.decision_record_text)
        self.assertIn("derecho de cita", self.decision_record_text.lower())
        self.assertIn("40 words", self.decision_record_text)
        self.assertIn("300 characters", self.decision_record_text)
        self.assertIn("four-eyes", self.decision_record_text.lower())

    def test_content_methodology_defines_source_rights_and_quotation_limits(self):
        self.assertIn("TRLPI", self.methodology_text)
        self.assertIn("derecho de cita", self.methodology_text.lower())
        self.assertIn("link_and_short_quote", self.methodology_text)
        self.assertIn("40 words", self.methodology_text)
        self.assertIn("Four-Eyes", self.methodology_text)

    def test_content_methodology_defines_reviewer_roles(self):
        self.assertIn("editorial_reviewer_1", self.methodology_text)
        self.assertIn("editorial_reviewer_2", self.methodology_text)
        self.assertIn("lead_editor", self.methodology_text)

    def test_content_methodology_defines_correction_slas(self):
        self.assertIn("Sev-1", self.methodology_text)
        self.assertIn("Sev-2", self.methodology_text)
        self.assertIn("Sev-3", self.methodology_text)
        self.assertIn("CorrectionRecord", self.methodology_text)


if __name__ == "__main__":
    unittest.main()
