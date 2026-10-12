"""Election isolation and safe 2023 pilot output after the issue #42 audit.

Source bytes remain identified by their hashes. Reported human content approvals
are retained, while source release gates remain pending. Corrected drafts and the invalidated comparison must not enter output.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from elecciones2026.editorial import EditorialApprovalGate
from elecciones2026.generator import (
    BuildValidationError,
    build_site,
    load_and_validate_site_data,
    render_home_page,
)
from elecciones2026.importer import (
    import_source_from_file,
)
from elecciones2026.methodology import load_parties, load_taxonomy
from elecciones2026.schemas import (
    CandidacyCoverageRecord,
    ProgrammeRecord,
    RelationshipRecord,
    ReviewRecord,
    StatementRecord,
    load_coverage_record,
    load_programme,
    load_relationship,
    load_statement,
    validate_any_record,
)
from elecciones2026.source_register import load_register


class TestPilot2023Rehearsal(unittest.TestCase):
    """Test suite for the private 2023 pilot comparison rehearsal."""

    def setUp(self) -> None:
        self.root_dir = Path(__file__).resolve().parent.parent
        self.content_dir = self.root_dir / "content"
        self.register_file = self.content_dir / "sources" / "register.json"
        self.register = load_register(self.register_file)

    def test_2023_sources_recorded_in_register(self) -> None:
        """Verify hashes stay recorded and 2023 pilot sources require human rights review."""
        sources_2023 = [s for s in self.register.sources if s.election_id == "es-gen-2023"]
        self.assertGreaterEqual(len(sources_2023), 4, "Must track at least four 2023 pilot sources")

        sources_by_party = {s.party_id: s for s in sources_2023}
        self.assertIn("pp", sources_by_party, "PP 2023 source must be registered")
        self.assertIn("erc", sources_by_party, "ERC 2023 source must be registered")
        self.assertIn("sumar", sources_by_party, "Sumar 2023 source must be registered")
        self.assertIn("pnv", sources_by_party, "PNV 2023 source must be registered")

        # Verify PP 2023 source record
        pp_src = sources_by_party["pp"]
        self.assertEqual(pp_src.status, "published-unverified")
        self.assertEqual(pp_src.version, "23J-v1")
        self.assertTrue(pp_src.official_url.startswith("https://www.pp.es/"))
        self.assertEqual(
            pp_src.sha256,
            "c93baafc88bdcb33adcd7e8be9dc309b09056362183ad7b7767f3d5134313108",
        )
        self.assertEqual(pp_src.rights_review.status, "not_reviewed")
        self.assertIsNone(pp_src.rights_review.reviewed_by)
        self.assertIsNone(pp_src.rights_review.review_date)

        # Verify ERC 2023 source record
        erc_src = sources_by_party["erc"]
        self.assertEqual(erc_src.status, "published-unverified")
        self.assertEqual(erc_src.version, "23J-v1")
        self.assertTrue(erc_src.official_url.startswith("https://www.esquerra.cat/"))
        self.assertEqual(
            erc_src.sha256,
            "760db25e48422b74a9b0c3172cab16cf39d010345849e50b921ff8bf61be2854",
        )
        self.assertEqual(erc_src.rights_review.status, "not_reviewed")
        self.assertIsNone(erc_src.rights_review.reviewed_by)
        self.assertIsNone(erc_src.rights_review.review_date)

    def test_2023_programme_records_valid(self) -> None:
        """Verify 2023 programme fixture files pass ProgrammeRecord schema validation."""
        pp_prog_file = self.content_dir / "examples" / "programmes" / "pp-2023-official.json"
        erc_prog_file = self.content_dir / "examples" / "programmes" / "erc-2023-official.json"
        self.assertTrue(pp_prog_file.is_file(), "pp-2023-official.json must exist")
        self.assertTrue(erc_prog_file.is_file(), "erc-2023-official.json must exist")

        pp_prog = load_programme(pp_prog_file)
        self.assertEqual(pp_prog.election_id, "es-gen-2023")
        self.assertEqual(pp_prog.status, "published-unverified")
        self.assertEqual(pp_prog.validate(target_election_id="es-gen-2023"), [])

        erc_prog = load_programme(erc_prog_file)
        self.assertEqual(erc_prog.election_id, "es-gen-2023")
        self.assertEqual(erc_prog.status, "published-unverified")
        self.assertEqual(erc_prog.validate(target_election_id="es-gen-2023"), [])

    def test_2023_statement_records_valid_and_cited(self) -> None:
        """Verify reviewed candidates retain locators and remain unpublished."""
        pp_stmt_file = self.content_dir / "examples" / "statements" / "statement-2023-pilot-proposal.json"
        erc_stmt_file = self.content_dir / "examples" / "statements" / "statement-2023-pilot-erc-housing.json"
        self.assertTrue(pp_stmt_file.is_file())
        self.assertTrue(erc_stmt_file.is_file())

        pp_stmt = load_statement(pp_stmt_file)
        self.assertEqual(pp_stmt.election_id, "es-gen-2023")
        self.assertEqual(pp_stmt.review_status, "under_review")
        self.assertEqual({r.reviewer_id for r in pp_stmt.reviews}, {"barnolacesc", "carlesfito"})
        self.assertTrue(all(r.reviewer_kind == "human" and r.evidence_ref for r in pp_stmt.reviews))
        self.assertEqual(pp_stmt.source_page, "34")
        self.assertIsNone(pp_stmt.quote, "Pending rights must not imply quotation permission")
        self.assertEqual(pp_stmt.source_version, "23J-v1")
        self.assertEqual(
            pp_stmt.source_url,
            "https://www.pp.es/storage/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf",
        )
        self.assertIsNone(pp_stmt.last_reviewed_date)
        self.assertEqual(pp_stmt.validate(target_election_id="es-gen-2023"), [])

        erc_stmt = load_statement(erc_stmt_file)
        self.assertEqual(erc_stmt.election_id, "es-gen-2023")
        self.assertEqual(erc_stmt.review_status, "under_review")
        self.assertEqual({r.reviewer_id for r in erc_stmt.reviews}, {"barnolacesc", "carlesfito"})
        self.assertTrue(all(r.reviewer_kind == "human" and r.evidence_ref for r in erc_stmt.reviews))
        self.assertEqual(erc_stmt.source_page, "114")
        self.assertIsNone(erc_stmt.quote, "Pending rights must not imply quotation permission")
        self.assertEqual(erc_stmt.source_version, "23J-v1")
        self.assertEqual(
            erc_stmt.source_url,
            "https://static.esquerra.cat/uploads/20230905/e2023-programa.pdf",
        )
        self.assertIsNone(erc_stmt.last_reviewed_date)
        self.assertEqual(erc_stmt.validate(target_election_id="es-gen-2023"), [])

    def test_2023_relationship_record_valid(self) -> None:
        """Verify the PP/ERC comparison stays invalidated pending human review."""
        rel_file = self.content_dir / "examples" / "relationships" / "relationship-2023-pilot-housing-divergence.json"
        self.assertTrue(rel_file.is_file())

        rel = load_relationship(rel_file)
        self.assertEqual(rel.election_id, "es-gen-2023")
        self.assertEqual(rel.relationship_type, "divergence")
        self.assertEqual(rel.status, "invalidated")
        self.assertEqual(rel.review_status, "invalidated")
        self.assertEqual(rel.party_ids, ["pp", "erc"])
        self.assertEqual(rel.statement_ids, ["stmt-pilot-pp-housing-2023", "stmt-pilot-erc-housing-2023"])

        statements = {
            "stmt-pilot-pp-housing-2023": load_statement(
                self.content_dir / "examples" / "statements" / "statement-2023-pilot-proposal.json"
            ),
            "stmt-pilot-erc-housing-2023": load_statement(
                self.content_dir / "examples" / "statements" / "statement-2023-pilot-erc-housing.json"
            ),
        }
        self.assertEqual(rel.validate(target_election_id="es-gen-2023", statements_by_id=statements, for_build=False), [])

    def test_2023_coverage_records_valid(self) -> None:
        """Verify 2023 pilot coverage records pass schema validation."""
        cov_pp_file = self.content_dir / "examples" / "coverage" / "coverage-pilot-2023-pp.json"
        cov_erc_file = self.content_dir / "examples" / "coverage" / "coverage-pilot-2023-erc.json"
        self.assertTrue(cov_pp_file.is_file())
        self.assertTrue(cov_erc_file.is_file())

        cov_pp = load_coverage_record(cov_pp_file)
        self.assertEqual(cov_pp.election_id, "es-gen-2023")
        self.assertEqual(cov_pp.candidacy_id, "pp")
        self.assertEqual(cov_pp.status, "published-unverified")
        self.assertFalse(cov_pp.has_verified_programme)
        self.assertEqual(cov_pp.validate(target_election_id="es-gen-2023"), [])

        cov_erc = load_coverage_record(cov_erc_file)
        self.assertEqual(cov_erc.election_id, "es-gen-2023")
        self.assertEqual(cov_erc.candidacy_id, "erc")
        self.assertEqual(cov_erc.status, "published-unverified")
        self.assertFalse(cov_erc.has_verified_programme)
        self.assertEqual(cov_erc.validate(target_election_id="es-gen-2023"), [])

    def test_cross_election_rejection_at_all_boundaries(self) -> None:
        """Verify cross-election combinations are strictly rejected at statement, relationship, gate, and build levels."""
        pp_stmt = load_statement(
            self.content_dir / "examples" / "statements" / "statement-2023-pilot-proposal.json"
        )
        stmt_2026 = load_statement(
            self.content_dir / "examples" / "statements" / "statement-housing-proposal-approved.json"
        )

        # 1. Statement bound to 2023 rejected when target election is 2026
        errs = pp_stmt.validate(target_election_id="es-gen-2026")
        self.assertTrue(any("election mismatch" in e for e in errs), f"Expected election mismatch error: {errs}")

        # 2. Relationship model rejects mixed election statements
        cross_rel = RelationshipRecord(
            schema_version="1.0.0",
            election_id="es-gen-2023",
            id="rel-cross-election-invalid",
            topic_id="housing",
            subtopic_id="rental-regulation",
            measure_label="Medida de prueba",
            party_ids=["pp", "partido-ejemplo-a"],
            statement_ids=[pp_stmt.id, stmt_2026.id],
            relationship_type="divergence",
            summary="Intento inválido de comparar 2023 con 2026.",
            differences=["No permitido."],
            review_status="approved",
            reviews=[
                ReviewRecord(reviewer_id="r1", review_date="2026-10-10", verdict="approved", review_notes="ok"),
                ReviewRecord(reviewer_id="r2", review_date="2026-10-11", verdict="approved", review_notes="ok"),
            ],
            status="active",
        )
        rel_errs = cross_rel.validate(
            target_election_id="es-gen-2023",
            statements_by_id={pp_stmt.id: pp_stmt, stmt_2026.id: stmt_2026},
        )
        self.assertTrue(
            any("cross-election error" in e for e in rel_errs),
            f"Expected cross-election error in relationship validation: {rel_errs}",
        )

        # 3. EditorialApprovalGate rejects statement from wrong election
        gate_2026 = EditorialApprovalGate(target_election_id="es-gen-2026")
        gate_errs = gate_2026.validate_statement(pp_stmt)
        self.assertTrue(
            any("election mismatch" in e for e in gate_errs),
            f"Expected election mismatch in EditorialApprovalGate: {gate_errs}",
        )

        # 4. EditorialApprovalGate rejects relationship cross-referencing statements
        gate_2023 = EditorialApprovalGate(target_election_id="es-gen-2023")
        gate_rel_errs = gate_2023.validate_relationship(
            cross_rel,
            statements_by_id={pp_stmt.id: pp_stmt, stmt_2026.id: stmt_2026},
        )
        self.assertTrue(
            any("cross-election error" in e for e in gate_rel_errs),
            f"Expected cross-election error from gate: {gate_rel_errs}",
        )

        # 5. Build validation rejects cross-election relationship
        with self.assertRaises(BuildValidationError):
            load_and_validate_site_data(
                root_dir=self.root_dir,
                content_dir=self.content_dir,
                election_id="es-gen-2023",
                custom_relationships=[cross_rel],
                custom_statements=[pp_stmt, stmt_2026],
            )

    def test_offline_source_hash_verification(self) -> None:
        """Verify source verification pipeline verifies hashes offline without network access."""
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp_file:
            # Create mock PDF file matching expected structure
            pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF\n"
            tmp_file.write(pdf_bytes)
            tmp_file.flush()

            import hashlib

            expected_sha = hashlib.sha256(pdf_bytes).hexdigest()

            # Verify through isolated offline pipeline
            result = import_source_from_file(Path(tmp_file.name), expected_hash=expected_sha)
            self.assertEqual(result.status, "verified")
            self.assertEqual(result.sha256, expected_sha)
            self.assertEqual(result.pdf_version, "1.4")

    def test_deterministic_static_build_2023_pilot(self) -> None:
        """Verify full deterministic static build of 2023 pilot and check 'Generales 2023' appears on every view."""
        with tempfile.TemporaryDirectory() as tmp_out:
            out_dir = Path(tmp_out) / "pilot_2023"
            result = build_site(
                root_dir=self.root_dir,
                output_dir=out_dir,
                content_dir=self.content_dir,
                election_id="es-gen-2023",
                canonical_base="https://elecciones2026.es/pilot-2023",
                build_date="2026-10-18",
            )

            self.assertGreater(len(result.files_written), 0)
            self.assertGreater(len(result.file_hashes), 0)
            self.assertEqual(result.election_id, "es-gen-2023")

            # Verify every generated HTML file contains "Generales 2023"
            html_files = list(out_dir.glob("**/*.html"))
            self.assertGreater(len(html_files), 5, "Expected multiple generated HTML pages")

            for html_file in html_files:
                html_text = html_file.read_text(encoding="utf-8")
                self.assertIn(
                    "Generales 2023",
                    html_text,
                    f"Page {html_file.relative_to(out_dir)} must contain 'Generales 2023'",
                )
                # Verify that it is clearly labelled as a private pilot
                self.assertIn(
                    "ENSAYO PILOTO PRIVADO",
                    html_text,
                    f"Page {html_file.relative_to(out_dir)} must display private rehearsal banner",
                )

            # Inspect home page details
            index_html = (out_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("GENERALES 2023 · 23 JULIO 2023", index_html)
            self.assertIn("Aviso de ensayo privado (Generales 2023)", index_html)
            self.assertIn("no satisface la puerta de publicación G2 para 2026", index_html)
            self.assertEqual(result.statements_count, 0)
            self.assertEqual(result.relationships_count, 0)
            self.assertIn("Generales 2023 (piloto)", index_html)
            self.assertNotIn("Crearemos un programa de avales para jóvenes", index_html)
            self.assertNotIn("Garantir el dret", index_html)
            self.assertNotIn("Borrador sin revisión humana", index_html)
            self.assertNotIn("rel-pilot-2023-housing", (out_dir / "app.js").read_text())

            # Ensure 2026 fixture statements were NOT rendered in the 2023 pilot
            self.assertNotIn("Partido Ejemplo A", index_html)
            self.assertNotIn("Partido Ejemplo B", index_html)

    def test_mobile_grouped_measures_structure(self) -> None:
        """Verify mobile comparison constraints: no tabs, stacked cards, visible source links."""
        ctx = load_and_validate_site_data(
            root_dir=self.root_dir,
            content_dir=self.content_dir,
            election_id="es-gen-2023",
        )
        home_html = render_home_page(ctx)

        # Prohibition of tablist / tabs
        self.assertNotIn('role="tablist"', home_html)
        self.assertNotIn('role="tab"', home_html)
        self.assertNotIn('role="tabpanel"', home_html)

        # Both party cards present in single measure group
        self.assertIn("Contenido pendiente de publicación", home_html)
        self.assertNotIn('class="party-card party-card-a', home_html)
        self.assertNotIn('class="party-card party-card-b', home_html)
        self.assertEqual(len(ctx.statements), 0)
        self.assertEqual(len(ctx.relationships), 0)
        self.assertIn("Solo posiciones verificadas", home_html)


    def test_browser_artifact_excludes_unreviewed_political_measures(self) -> None:
        """No unvalidated browser claim can bypass the editorial build gate."""
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "pilot"
            build_site(self.root_dir, output, election_id="es-gen-2023")
            script = (output / "app.js").read_text()
            self.assertNotIn("electionId: 'es-gen-2023'", script)
            self.assertNotIn("-pilot-2023-measure", script)
            self.assertIn("Contenido pendiente de publicación", script)
            self.assertIn("La falta de contenido aprobado no indica", script)
            for statement_path in (self.content_dir / "examples/statements").glob("*2023*.json"):
                statement = load_statement(statement_path)
                if statement.quote:
                    self.assertNotIn(statement.quote, script)
                    for page in output.rglob("*.html"):
                        self.assertNotIn(statement.quote, page.read_text())


if __name__ == "__main__":
    unittest.main()
