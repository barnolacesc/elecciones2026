"""Tests for editorial approval gates and correction invalidation (Package E1.3).

Verifies Tasks 2.2 and 2.4 acceptance criteria:
1. Build rejects unreviewed/uncited claims and unlicensed quotes (Task 2.2).
2. Missing references and unknown programme versions fail the build (Task 2.2).
3. Versioned corrections invalidate dependent comparison relationships (Task 2.4).
4. Build rejects invalidated comparisons from static publication output (Task 2.4).
5. Filter publishable comparisons isolates active approved output from invalidated errata.
6. Re-audit and dual re-approval restores comparison publishability.
7. CLI entrypoints and CI build gate execution.
"""

from dataclasses import replace
from pathlib import Path
import json
import unittest

from elecciones2026.editorial import (
    MAX_QUOTE_CHARS,
    MAX_QUOTE_WORDS,
    PERMITTED_QUOTE_RIGHTS,
    ComparisonRelationship,
    EditorialApprovalGate,
    apply_correction_and_invalidate,
    filter_publishable_comparisons,
    invalidate_dependent_relationships,
    validate_build,
    validate_quote_limits,
)
from elecciones2026.methodology import (
    PartyRecord,
    ProgrammeRecord,
    ProgrammeStatus,
    Taxonomy,
    load_parties,
    load_programme,
    load_taxonomy,
)
from elecciones2026.schemas import (
    CorrectionRecord,
    RelationshipRecord,
    ReviewRecord,
    StatementRecord,
)
from elecciones2026.source_register import (
    RightsReview,
    SourceRecord,
    SourceRegister,
    load_register,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
TAXONOMY_PATH = CONTENT_DIR / "taxonomy.json"
REGISTER_PATH = CONTENT_DIR / "sources" / "register.json"
PARTIES_PATH = CONTENT_DIR / "examples" / "parties.json"


class TestEditorialApprovalGates(unittest.TestCase):
    """Task 2.2: Provenance, review-state, quote-licensing, and reference validation."""

    @classmethod
    def setUpClass(cls):
        cls.taxonomy = load_taxonomy(TAXONOMY_PATH)
        cls.register = load_register(REGISTER_PATH)
        cls.parties = load_parties(PARTIES_PATH)

        cls.programmes = []
        prog_dir = CONTENT_DIR / "examples" / "programmes"
        for p_file in prog_dir.glob("*.json"):
            cls.programmes.append(load_programme(p_file))

        cls.gate = EditorialApprovalGate(
            target_election_id="es-gen-2026",
            source_register=cls.register,
            taxonomy=cls.taxonomy,
            parties=cls.parties,
            programmes=cls.programmes,
        )

    def _make_valid_approved_statement(self, **overrides) -> StatementRecord:
        default_kwargs = {
            "schema_version": "1.0.0",
            "election_id": "es-gen-2026",
            "id": "stmt-valid-approved-001",
            "party_id": "partido-ejemplo-a",
            "programme_id": "prog-fixture-party-a-2026-v1",
            "topic_id": "housing",
            "subtopic_id": "rental-regulation",
            "statement_type": "explicit_proposal",
            "summary": "Establecer límites de precios vinculantes en zonas tensionadas.",
            "quote": "Tope vinculante a los precios del alquiler residencial.",
            "source_url": "https://partido-ejemplo-a.es/programa-2026.pdf",
            "source_version": "1.0.0",
            "source_page": "34",
            "source_section": "Capítulo 3: Vivienda",
            "review_status": "approved",
            "reviews": [
                ReviewRecord(
                    reviewer_id="rev-editorial-1",
                    review_date="2026-10-16",
                    verdict="approved",
                    review_notes="Factual audit against source PDF page 34.",
                ),
                ReviewRecord(
                    reviewer_id="rev-editorial-2",
                    review_date="2026-10-17",
                    verdict="approved",
                    review_notes="Neutrality audit confirmed descriptive non-evaluative language.",
                ),
            ],
            "last_reviewed_date": "2026-10-17",
            "is_fixture": True,
        }
        default_kwargs.update(overrides)
        return StatementRecord(**default_kwargs)

    def test_valid_statement_passes_approval_gate(self):
        stmt = self._make_valid_approved_statement()
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertEqual(errors, [])

    def test_unreviewed_claims_fail_build(self):
        """Unreviewed claims (draft, under_review, rejected, invalidated) must fail the build."""
        for invalid_status in ("draft", "under_review", "rejected", "invalidated"):
            stmt = self._make_valid_approved_statement(
                id=f"stmt-test-{invalid_status}",
                review_status=invalid_status,
            )
            errors = self.gate.validate_statement(stmt, require_approved=True)
            self.assertTrue(
                any(f"unreviewed claim with review_status '{invalid_status}' cannot pass build" in e for e in errors),
                f"Status '{invalid_status}' should have been rejected as unreviewed, got: {errors}",
            )

    def test_single_reviewer_claim_fails_build(self):
        """Claims with only a single reviewer must fail the build under Four-Eyes Principle."""
        stmt = self._make_valid_approved_statement(
            id="stmt-test-single-rev",
            reviews=[
                ReviewRecord(
                    reviewer_id="rev-editorial-1",
                    review_date="2026-10-16",
                    verdict="approved",
                    review_notes="Only one reviewer signed off.",
                )
            ],
        )
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("requires dual approval by at least two distinct reviewers" in e for e in errors))

    def test_four_eyes_violation_same_reviewer_fails_build(self):
        """Claim where the same reviewer is entered twice must fail the build."""
        stmt = self._make_valid_approved_statement(
            id="stmt-test-same-rev",
            reviews=[
                ReviewRecord(
                    reviewer_id="rev-alex",
                    review_date="2026-10-16",
                    verdict="approved",
                    review_notes="First signoff",
                ),
                ReviewRecord(
                    reviewer_id="rev-alex",
                    review_date="2026-10-17",
                    verdict="approved",
                    review_notes="Duplicate signoff",
                ),
            ],
        )
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("requires dual approval by at least two distinct reviewers" in e for e in errors))

    def test_drafter_acting_as_secondary_reviewer_fails_build(self):
        """Segregation of duties: drafter cannot serve as secondary reviewer."""
        stmt = self._make_valid_approved_statement(
            id="stmt-test-drafter-rev2",
            reviews=[
                ReviewRecord(
                    reviewer_id="rev-analyst",
                    review_date="2026-10-16",
                    verdict="approved",
                    review_notes="Drafter: rev-editor-sam extracted proposal.",
                ),
                ReviewRecord(
                    reviewer_id="rev-editor-sam",
                    review_date="2026-10-17",
                    verdict="approved",
                    review_notes="Second signoff by drafter.",
                ),
            ],
        )
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("Segregation of duties violation" in e for e in errors))

    def test_uncited_claims_fail_build(self):
        """Explicit proposals missing source_url, source_version, or locators must fail build."""
        # Missing source_url
        stmt_no_url = self._make_valid_approved_statement(
            id="stmt-no-url",
            source_url=None,
        )
        errors = self.gate.validate_statement(stmt_no_url, require_approved=True)
        self.assertTrue(any("uncited claim: explicit_proposal must specify source_url" in e for e in errors))

        # Missing source_version
        stmt_no_ver = self._make_valid_approved_statement(
            id="stmt-no-ver",
            source_version=None,
        )
        errors = self.gate.validate_statement(stmt_no_ver, require_approved=True)
        self.assertTrue(any("uncited claim: explicit_proposal must specify source_version" in e for e in errors))

        # Missing both page and section
        stmt_no_loc = self._make_valid_approved_statement(
            id="stmt-no-loc",
            source_page=None,
            source_section=None,
        )
        errors = self.gate.validate_statement(stmt_no_loc, require_approved=True)
        self.assertTrue(any("uncited claim: explicit_proposal must specify at least one of source_page or source_section" in e for e in errors))

    def test_not_found_statement_with_coordinates_or_quote_fails_build(self):
        """Absence statement cannot have quotes or page coordinates."""
        stmt_bad_not_found = self._make_valid_approved_statement(
            id="stmt-bad-not-found",
            statement_type="not_found",
            source_page="42",
            quote="Invented quote",
        )
        errors = self.gate.validate_statement(stmt_bad_not_found, require_approved=True)
        self.assertTrue(any("not_found statement must not specify source_page" in e for e in errors))
        self.assertTrue(any("not_found statement must not include quote" in e for e in errors))

    def test_unlicensed_quote_exceeding_word_limit_fails_build(self):
        """Verbatim quote exceeding 40 words must fail build."""
        long_quote = " ".join(["compromiso"] * 41)
        stmt = self._make_valid_approved_statement(
            id="stmt-long-quote",
            quote=long_quote,
        )
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("exceeds maximum limit of 40 words" in e for e in errors))

    def test_unlicensed_quote_exceeding_character_limit_fails_build(self):
        """Verbatim quote exceeding 300 characters must fail build."""
        long_text = "a" * 301
        stmt = self._make_valid_approved_statement(
            id="stmt-long-char-quote",
            quote=long_text,
        )
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("exceeds maximum limit of 300 characters" in e for e in errors))

    def test_unlicensed_quote_without_locators_fails_build(self):
        """Quote without page or section locator must fail build."""
        stmt = self._make_valid_approved_statement(
            id="stmt-quote-no-locator",
            quote="Cita sin localizador",
            source_page=None,
            source_section=None,
        )
        errors = self.gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("at least one locator" in e.lower() for e in errors))

    def test_unlicensed_quote_from_unverified_source_fails_build(self):
        """Quote referencing an unverified source must fail build."""
        source = next(s for s in self.register.sources if s.id == "src-2026-vox-v2")
        unverified_source = replace(
            source, id="src-test-unverified", status="published-unverified",
            official_url="https://example.test/programme", direct_url="https://example.test/programme.pdf",
        )
        gate = EditorialApprovalGate(
            target_election_id="es-gen-2026",
            source_register=replace(self.register, sources=[unverified_source]),
            taxonomy=self.taxonomy,
            parties=self.parties,
            programmes=self.programmes,
        )
        stmt = self._make_valid_approved_statement(
            id="stmt-unverified-src",
            programme_id=None,
            source_url=unverified_source.direct_url,
            quote="Cita de fuente no verificada",
        )
        errors = gate.validate_statement(stmt, require_approved=True)
        self.assertTrue(any(
            "unsupported quote cannot pass review because source 'src-test-unverified' "
            "status is 'published-unverified'" in e
            for e in errors
        ))

    def test_unlicensed_quote_from_restricted_rights_source_fails_build(self):
        """Quote from a source with restricted rights must fail build."""
        restricted_src = SourceRecord(
            id="src-test-restricted",
            election_id="es-gen-2026",
            party_id="partido-ejemplo-a",
            candidature_name="Partido Ejemplo A",
            publisher="PEA",
            scope="general",
            official_url="https://ejemplo.es/programa.pdf",
            direct_url="https://ejemplo.es/programa.pdf",
            filename=None,
            publication_date=None,
            retrieval_date="2026-10-09",
            language="es",
            version="1.0",
            sha256="a" * 64,
            status="verified",
            rights_review=RightsReview(
                status="link_only",
                reviewed_by="legal",
                review_date="2026-10-09",
                terms_notes="No quotes permitted",
            ),
            replacement_history=[],
            notes="",
        )
        gate_with_restricted = EditorialApprovalGate(
            target_election_id="es-gen-2026",
            source_register=SourceRegister(
                version="1.0.0",
                last_updated="2026-10-09",
                description="",
                elections=self.register.elections,
                sources=[restricted_src],
            ),
            taxonomy=self.taxonomy,
            parties=self.parties,
            programmes=self.programmes,
        )
        stmt = self._make_valid_approved_statement(
            id="stmt-restricted-rights",
            programme_id=None,
            source_url="https://ejemplo.es/programa.pdf",
            quote="Cita no autorizada por derechos",
        )
        errors = gate_with_restricted.validate_statement(stmt, require_approved=True)
        self.assertTrue(any("unsupported quote cannot pass review because source rights status 'link_only' does not allow quotation" in e for e in errors))

    def test_unknown_programme_version_fails_build(self):
        """Statement referencing unknown programme ID or mismatched version must fail build."""
        stmt_unknown_prog = self._make_valid_approved_statement(
            id="stmt-unknown-prog",
            programme_id="prog-nonexistent-2026",
        )
        errors = self.gate.validate_statement(stmt_unknown_prog, require_approved=True)
        self.assertTrue(any("unknown programme_id 'prog-nonexistent-2026'" in e for e in errors))

        # Mismatched version
        stmt_mismatched_ver = self._make_valid_approved_statement(
            id="stmt-mismatched-ver",
            programme_id="prog-fixture-party-a-2026-v1",
            source_version="9.9.9",
        )
        errors = self.gate.validate_statement(stmt_mismatched_ver, require_approved=True)
        self.assertTrue(any("unknown programme version: statement specifies '9.9.9' but registered programme version is '1.0.0'" in e for e in errors))

    def test_missing_references_fail_build(self):
        """Statements referencing non-existent parties or topics must fail build."""
        stmt_bad_party = self._make_valid_approved_statement(
            id="stmt-bad-party",
            party_id="partido-inexistente",
        )
        errors = self.gate.validate_statement(stmt_bad_party, require_approved=True)
        self.assertTrue(any("party_id 'partido-inexistente' not found in registered parties" in e for e in errors))

        stmt_bad_topic = self._make_valid_approved_statement(
            id="stmt-bad-topic",
            topic_id="deportes",
        )
        errors = self.gate.validate_statement(stmt_bad_topic, require_approved=True)
        self.assertTrue(any("topic_id 'deportes' not found in taxonomy" in e for e in errors))


class TestCorrectionAndRelationshipInvalidation(unittest.TestCase):
    """Task 2.4: Versioned corrections, relationship invalidation, and rejection of invalidated comparisons."""

    @classmethod
    def setUpClass(cls):
        cls.taxonomy = load_taxonomy(TAXONOMY_PATH)
        cls.register = load_register(REGISTER_PATH)
        cls.parties = load_parties(PARTIES_PATH)

        cls.programmes = []
        prog_dir = CONTENT_DIR / "examples" / "programmes"
        for p_file in prog_dir.glob("*.json"):
            cls.programmes.append(load_programme(p_file))

        cls.gate = EditorialApprovalGate(
            target_election_id="es-gen-2026",
            source_register=cls.register,
            taxonomy=cls.taxonomy,
            parties=cls.parties,
            programmes=cls.programmes,
        )

    def _make_active_relationship(self, **overrides) -> RelationshipRecord:
        default_kwargs = {
            "schema_version": "1.0.0",
            "election_id": "es-gen-2026",
            "id": "rel-housing-rent-001",
            "topic_id": "housing",
            "subtopic_id": "rental-regulation",
            "measure_label": "Tope al alquiler residencial",
            "party_ids": ["partido-ejemplo-a", "partido-ejemplo-b"],
            "statement_ids": ["stmt-party-a-housing-001", "stmt-party-b-housing-001"],
            "relationship_type": "agreement",
            "summary": "Ambas candidaturas coinciden en limitar los precios del alquiler en áreas tensionadas.",
            "differences": ["Exención de dos años en Partido A."],
            "review_status": "approved",
            "reviews": [
                ReviewRecord(
                    reviewer_id="rev-editorial-1",
                    review_date="2026-10-17",
                    verdict="approved",
                    review_notes="Acuerdo verificado.",
                ),
                ReviewRecord(
                    reviewer_id="rev-editorial-2",
                    review_date="2026-10-18",
                    verdict="approved",
                    review_notes="Neutralidad verificada.",
                ),
            ],
            "status": "active",
            "invalidation_reason": None,
            "invalidated_by_correction_id": None,
            "is_fixture": True,
        }
        default_kwargs.update(overrides)
        return RelationshipRecord(**default_kwargs)

    def test_statement_correction_invalidates_dependent_comparisons(self):
        """Task 2.4: Changing a source claim via CorrectionRecord invalidates all dependent comparisons."""
        stmt1 = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-party-a-housing-001",
            party_id="partido-ejemplo-a",
            programme_id="prog-fixture-party-a-2026-v1",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Limitar alquileres al 15% del ingreso medio.",
            quote="Límite del 15%.",
            source_url="https://partido-ejemplo-a.es/programa-2026.pdf",
            source_version="1.0.0",
            source_page="34",
            review_status="approved",
            reviews=[
                ReviewRecord(reviewer_id="r1", review_date="2026-10-16", verdict="approved", review_notes=""),
                ReviewRecord(reviewer_id="r2", review_date="2026-10-17", verdict="approved", review_notes=""),
            ],
            last_reviewed_date="2026-10-17",
        )
        stmt2 = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-party-b-housing-001",
            party_id="partido-ejemplo-b",
            programme_id="prog-fixture-party-b-2026-partial",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Topar alquileres abusivos.",
            quote="Toparemos alquileres abusivos.",
            source_url="https://partido-ejemplo-b.es/manifiesto-2026-resumen.pdf",
            source_version="0.9.0-partial",
            source_page="8",
            review_status="approved",
            reviews=[
                ReviewRecord(reviewer_id="r1", review_date="2026-10-16", verdict="approved", review_notes=""),
                ReviewRecord(reviewer_id="r2", review_date="2026-10-17", verdict="approved", review_notes=""),
            ],
            last_reviewed_date="2026-10-17",
        )
        stmt3 = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-party-a-edu-001",
            party_id="partido-ejemplo-a",
            programme_id="prog-fixture-party-a-2026-v1",
            topic_id="education",
            subtopic_id="early-childhood-education",
            statement_type="explicit_proposal",
            summary="Gratuidad 0-3 años.",
            quote="Escolarización 0 a 3 años gratuita.",
            source_url="https://partido-ejemplo-a.es/programa-2026.pdf",
            source_version="1.0.0",
            source_page="50",
            review_status="approved",
            reviews=[
                ReviewRecord(reviewer_id="r1", review_date="2026-10-16", verdict="approved", review_notes=""),
                ReviewRecord(reviewer_id="r2", review_date="2026-10-17", verdict="approved", review_notes=""),
            ],
            last_reviewed_date="2026-10-17",
        )

        rel_dependent = self._make_active_relationship(
            id="rel-housing-rent-001",
            statement_ids=["stmt-party-a-housing-001", "stmt-party-b-housing-001"],
        )
        rel_unrelated = self._make_active_relationship(
            id="rel-edu-001",
            topic_id="education",
            subtopic_id="early-childhood-education",
            measure_label="Educación 0-3",
            statement_ids=["stmt-party-a-edu-001"],
            relationship_type="single_party",
        )

        correction = CorrectionRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="cor-2026-errata-housing",
            target_type="statement",
            target_id="stmt-party-a-housing-001",
            correction_type="factual_error",
            prior_state={"summary": "Limitar alquileres al 15% del ingreso medio."},
            corrected_state={"summary": "Limitar alquileres al 30% del ingreso medio (corrección de errata)."},
            reason="Subsanación de errata en porcentaje de esfuerzo máximo para alquiler de vivienda.",
            correction_date="2026-10-19",
            reviewed_by="rev-editorial-1",
            approved_by="lead-editor-cesc",
        )

        upd_stmts, upd_rels, inv_ids = apply_correction_and_invalidate(
            correction=correction,
            statements=[stmt1, stmt2, stmt3],
            relationships=[rel_dependent, rel_unrelated],
        )

        # 1. Statement was updated with correction_id
        target_stmt = next(s for s in upd_stmts if s.id == "stmt-party-a-housing-001")
        self.assertEqual(target_stmt.correction_id, "cor-2026-errata-housing")
        self.assertIn("30%", target_stmt.summary)

        # 2. Only dependent relationship was invalidated
        self.assertEqual(inv_ids, ["rel-housing-rent-001"])
        rel_dep_updated = next(r for r in upd_rels if r.id == "rel-housing-rent-001")
        rel_unrel_updated = next(r for r in upd_rels if r.id == "rel-edu-001")

        self.assertEqual(rel_dep_updated.status, "invalidated")
        self.assertEqual(rel_dep_updated.review_status, "invalidated")
        self.assertEqual(rel_dep_updated.invalidated_by_correction_id, "cor-2026-errata-housing")
        self.assertIn("Subsanación de errata", rel_dep_updated.invalidation_reason)

        # 3. Unrelated comparison remains active and approved
        self.assertEqual(rel_unrel_updated.status, "active")
        self.assertEqual(rel_unrel_updated.review_status, "approved")
        self.assertIsNone(rel_unrel_updated.invalidation_reason)

    def test_build_rejects_invalidated_comparisons(self):
        """Acceptance Criteria: Build rejects invalidated comparisons."""
        inv_rel = self._make_active_relationship(
            id="rel-invalidated-for-test",
            status="invalidated",
            review_status="invalidated",
            invalidation_reason="Dependent statement corrected due to citation errata.",
        )
        errors = self.gate.validate_relationship(inv_rel, allow_invalidated=False)
        self.assertTrue(any("invalidated comparison cannot be published in build" in e for e in errors))
        self.assertTrue(any("Dependent statement corrected due to citation errata" in e for e in errors))

    def test_build_rejects_comparison_referencing_invalidated_statement(self):
        """Build rejects active comparison if one of its referenced statements is invalidated."""
        stmt_valid = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-ok-001",
            party_id="partido-ejemplo-a",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Medida válida",
            review_status="approved",
            reviews=[
                ReviewRecord(reviewer_id="r1", review_date="2026-10-16", verdict="approved", review_notes=""),
                ReviewRecord(reviewer_id="r2", review_date="2026-10-17", verdict="approved", review_notes=""),
            ],
        )
        stmt_invalidated = StatementRecord(
            schema_version="1.0.0",
            election_id="es-gen-2026",
            id="stmt-retracted-002",
            party_id="partido-ejemplo-b",
            topic_id="housing",
            subtopic_id="rental-regulation",
            statement_type="explicit_proposal",
            summary="Medida retractada",
            review_status="invalidated",
        )

        active_rel = self._make_active_relationship(
            id="rel-referencing-invalidated-stmt",
            statement_ids=["stmt-ok-001", "stmt-retracted-002"],
            status="active",
        )

        stmts_map = {
            "stmt-ok-001": stmt_valid,
            "stmt-retracted-002": stmt_invalidated,
        }
        errors = self.gate.validate_relationship(active_rel, statements_by_id=stmts_map, allow_invalidated=False)
        self.assertTrue(any("cannot reference invalidated statement 'stmt-retracted-002'" in e for e in errors))

    def test_filter_publishable_comparisons(self):
        """filter_publishable_comparisons segregates active approved comparisons from invalidated ones."""
        rel1 = self._make_active_relationship(id="rel-1-active", status="active")
        rel2 = self._make_active_relationship(
            id="rel-2-invalidated",
            status="invalidated",
            invalidation_reason="Invalidated by correction",
        )

        publishable, excluded = filter_publishable_comparisons(
            relationships=[rel1, rel2],
        )
        self.assertEqual([r.id for r in publishable], ["rel-1-active"])
        self.assertEqual([r.id for r in excluded], ["rel-2-invalidated"])

    def test_reaudit_and_reapproval_restores_publishability(self):
        """After re-auditing an invalidated comparison with new reviews, it passes the build."""
        inv_rel = self._make_active_relationship(
            id="rel-reaudit-test",
            status="invalidated",
            review_status="invalidated",
            invalidation_reason="Old error",
        )
        # Fails publication
        errors_before = self.gate.validate_relationship(inv_rel, allow_invalidated=False)
        self.assertTrue(len(errors_before) > 0)

        # Re-audited version with updated reviews
        reaudited_rel = RelationshipRecord(
            schema_version=inv_rel.schema_version,
            election_id=inv_rel.election_id,
            id=inv_rel.id,
            topic_id=inv_rel.topic_id,
            subtopic_id=inv_rel.subtopic_id,
            measure_label=inv_rel.measure_label,
            party_ids=inv_rel.party_ids,
            statement_ids=inv_rel.statement_ids,
            relationship_type=inv_rel.relationship_type,
            summary="Resumen re-auditado y validado tras corrección de la propuesta fuente.",
            differences=inv_rel.differences,
            review_status="approved",
            reviews=[
                ReviewRecord(
                    reviewer_id="rev-editorial-1",
                    review_date="2026-10-20",
                    verdict="approved",
                    review_notes="Re-auditoría factual completada contra la declaración corregida.",
                ),
                ReviewRecord(
                    reviewer_id="rev-editorial-2",
                    review_date="2026-10-20",
                    verdict="approved",
                    review_notes="Re-auditoría de neutralidad completada.",
                ),
            ],
            status="active",
            invalidation_reason=None,
            invalidated_by_correction_id=None,
            is_fixture=True,
        )

        # Now passes publication
        errors_after = self.gate.validate_relationship(reaudited_rel, allow_invalidated=False)
        self.assertEqual(errors_after, [])


class TestEditorialGateCLIAndBuildValidation(unittest.TestCase):
    """Test full build gate validation command and reporting."""

    def test_cli_validate_build_succeeds_on_repo(self):
        passed, failed, errors = validate_build(ROOT_DIR, target_election_id="es-gen-2026")
        self.assertEqual(failed, 0, f"validate_build failed with errors: {errors}")
        self.assertGreaterEqual(passed, 6, "Expected at least 6 passing gate checks")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
