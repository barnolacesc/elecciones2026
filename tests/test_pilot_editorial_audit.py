"""Issue #42: real-party pilot claims cannot use fixture review approvals."""

from dataclasses import replace
from datetime import date, timedelta
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from elecciones2026.editorial import EditorialApprovalGate
from elecciones2026.generator import BuildValidationError, build_site, load_and_validate_site_data
from elecciones2026.schemas import ReviewRecord, load_relationship, load_statement

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATEMENT = CONTENT / "examples/statements/statement-2023-pilot-proposal.json"
RELATIONSHIP = CONTENT / "examples/relationships/relationship-2023-pilot-housing-divergence.json"


class TestPilotEditorialAudit(unittest.TestCase):
    def approvals(self):
        # Simulated review evidence is local to these tests, never repository content.
        return [ReviewRecord("human-alex", "2026-10-09", "approved", "Simulated factual review",
                             "human", "test-evidence:alex"),
                ReviewRecord("human-sam", "2026-10-09", "approved", "Simulated neutrality review",
                             "human", "test-evidence:sam")]

    def approved_statement(self):
        statement = load_statement(STATEMENT)
        reviews = [replace(r, content_sha256=statement.review_fingerprint()) for r in self.approvals()]
        return replace(statement, review_status="approved",
                       reviews=reviews, last_reviewed_date="2026-10-09")

    def test_future_approval_and_invalid_calendar_date_rejected(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        review = replace(self.approvals()[0], review_date=future)
        self.assertIn("future-dated", " ".join(review.validate(require_human=True)))
        review = replace(review, review_date="2026-02-30")
        self.assertIn("calendar date", " ".join(review.validate(require_human=True)))

    def test_placeholder_reviews_cannot_become_human_by_adding_a_label(self):
        for reviewer_id in ("rev-pilot-1", "rev-editorial-2", "reviewer-1", "editorial-team"):
            review = replace(self.approvals()[0], reviewer_id=reviewer_id)
            self.assertIn("Placeholder", " ".join(review.validate(require_human=True)))

    def test_automated_or_undocumented_review_is_not_human_approval(self):
        for changes in ({"reviewer_kind": "automated"}, {"reviewer_kind": None},
                        {"evidence_ref": None}, {"evidence_ref": "  "}):
            errors = replace(self.approvals()[0], **changes).validate(require_human=True)
            self.assertIn("documented evidence_ref", " ".join(errors))

    def test_statement_and_editorial_gate_reject_future_review(self):
        stmt = self.approved_statement()
        future = (date.today() + timedelta(days=1)).isoformat()
        stmt = replace(stmt, reviews=[stmt.reviews[0], replace(stmt.reviews[1], review_date=future)],
                       last_reviewed_date=future)
        self.assertIn("future-dated", " ".join(stmt.validate()))
        self.assertIn("future-dated", " ".join(EditorialApprovalGate(
            target_election_id="es-gen-2023").validate_statement(stmt)))

    def test_fixture_flag_cannot_bypass_pilot_review_checks(self):
        stmt = replace(self.approved_statement(), is_fixture=True)
        self.assertIn("fixture approvals", " ".join(stmt.validate()))

    def test_last_reviewed_date_matches_approval_history(self):
        stmt = replace(self.approved_statement(), last_reviewed_date="2026-10-08")
        self.assertIn("latest approval", " ".join(stmt.validate()))

    def test_relationship_approvals_require_distinct_documented_humans(self):
        rel = replace(load_relationship(RELATIONSHIP), status="active", review_status="approved",
                      reviews=[self.approvals()[0], self.approvals()[0]], is_fixture=False)
        self.assertIn("distinct reviewers", " ".join(rel.validate(for_build=False)))
        rel = replace(rel, reviews=[replace(r, reviewer_kind="automated") for r in self.approvals()])
        self.assertIn("human reviewer", " ".join(rel.validate(for_build=False)))

    def test_repository_drafts_are_outside_publish_set_even_without_strict_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            shutil.copytree(CONTENT, content)
            draft_path = content / "examples/statements/draft-sample.json"
            draft_data = json.loads(STATEMENT.read_text(encoding="utf-8"))
            draft_data["id"] = "stmt-draft-test"
            draft_data["review_status"] = "draft"
            draft_data["reviews"] = []
            draft_path.write_text(json.dumps(draft_data), encoding="utf-8")
            for strict in (True, False):
                ctx = load_and_validate_site_data(ROOT, content_dir=content, election_id="es-gen-2023", strict_approved=strict)
                self.assertNotIn("stmt-draft-test", ctx.statements)

    def test_explicit_draft_publish_set_fails_before_output(self):
        draft_stmt = replace(self.approved_statement(), id="stmt-draft-test", review_status="draft", reviews=[])
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "site"
            with self.assertRaises(BuildValidationError):
                build_site(ROOT, output, election_id="es-gen-2023",
                           custom_statements=[draft_stmt], custom_relationships=[])
            self.assertFalse(output.exists())

    def test_reviews_alone_do_not_override_pending_source_rights(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            shutil.copytree(CONTENT, content)
            register_path = content / "sources/register.json"
            register = json.loads(register_path.read_text())
            for src in register["sources"]:
                if src["id"] == "src-2023-pp-v1":
                    src["rights_review"]["status"] = "not_reviewed"
            register_path.write_text(json.dumps(register))
            for strict in (True, False):
                with self.assertRaisesRegex(BuildValidationError, "applicable rights are not approved"):
                    load_and_validate_site_data(ROOT, content_dir=content, election_id="es-gen-2023",
                                                strict_approved=strict,
                                                custom_statements=[self.approved_statement()],
                                                custom_relationships=[])

    def test_approved_synthetic_corpus_requires_matching_programme_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            shutil.copytree(CONTENT, content)
            register_path = content / "sources/register.json"
            register = json.loads(register_path.read_text())
            for src in register["sources"]:
                if src["id"] == "src-2023-pp-v1":
                    src["status"] = "verified"
                    src["publication_date"] = "2023-07-01"
                    src["rights_review"].update(status="link_and_short_quote", reviewed_by="human-alex",
                                                review_date="2026-10-09", evidence_ref="private:rights:pp")
            register_path.write_text(json.dumps(register))
            prog_path = content / "examples/programmes/pp-2023-official.json"
            prog = json.loads(prog_path.read_text())
            prog.update(status="official", rights_status="verified_quotation_permitted",
                        publication_date="2023-07-01")
            prog_path.write_text(json.dumps(prog))
            kwargs = dict(content_dir=content, election_id="es-gen-2023",
                          custom_statements=[self.approved_statement()], custom_relationships=[])
            self.assertEqual(len(load_and_validate_site_data(ROOT, **kwargs).statements), 1)
            src = next(s for s in register["sources"] if s["id"] == "src-2023-pp-v1")
            src["rights_review"]["reviewed_by"] = "editorial-team"
            register_path.write_text(json.dumps(register))
            with self.assertRaisesRegex(BuildValidationError, "placeholder source rights reviewer"):
                load_and_validate_site_data(ROOT, **kwargs)
            src["rights_review"]["reviewed_by"] = "human-alex"
            src["rights_review"]["review_date"] = (date.today() + timedelta(days=1)).isoformat()
            register_path.write_text(json.dumps(register))
            with self.assertRaisesRegex(BuildValidationError, "future-dated"):
                load_and_validate_site_data(ROOT, **kwargs)
            src["rights_review"]["review_date"] = "2026-10-09"
            register_path.write_text(json.dumps(register))
            prog["sha256"] = "f" * 64
            prog_path.write_text(json.dumps(prog))
            with self.assertRaisesRegex(BuildValidationError, "provenance/hash/rights"):
                load_and_validate_site_data(ROOT, **kwargs)

    def test_link_only_neutral_summary_passes_but_quote_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            shutil.copytree(CONTENT, content)
            register_path = content / "sources/register.json"
            register = json.loads(register_path.read_text())
            source = next(s for s in register["sources"] if s["id"] == "src-2023-pp-v1")
            source.update(status="verified", publication_date="2023-07-04")
            source["rights_review"].update(status="link_only", reviewed_by="human-alex",
                                           review_date="2026-10-09", evidence_ref="private:rights:pp")
            register_path.write_text(json.dumps(register))
            programme_path = content / "examples/programmes/pp-2023-official.json"
            programme = json.loads(programme_path.read_text())
            programme.update(status="official", rights_status="verified_link_only",
                             publication_date="2023-07-04")
            programme_path.write_text(json.dumps(programme))
            statement = self.approved_statement()
            args = dict(content_dir=content, election_id="es-gen-2023",
                        custom_relationships=[])
            self.assertIn(statement.id, load_and_validate_site_data(
                ROOT, custom_statements=[statement], **args).statements)
            output = Path(tmp) / "published"
            result = build_site(ROOT, output, content_dir=content, election_id="es-gen-2023",
                                build_date="2026-10-12", custom_statements=[statement],
                                custom_relationships=[])
            self.assertEqual((result.statements_count, result.relationships_count), (1, 0))
            home_text = (output / "index.html").read_text()
            self.assertIn("Posiciones visibles verificadas", home_text)
            self.assertIn("PP, ERC, PNV y Sumar", home_text)
            html_text = "\n".join(p.read_text() for p in output.rglob("*.html"))
            browser_text = "\n".join(p.read_text() for p in output.glob("comparison-data.*.js"))
            payload = json.loads(json.loads(browser_text.removeprefix(
                "window.ComparisonData = JSON.parse(").rstrip(";\n)")))
            position = payload["measuresByTopic"]["housing"][0]["positions"]["pp"]
            self.assertIn(statement.id, html_text)
            self.assertIn(statement.source_section, html_text)
            self.assertIn(statement.qualifications[0], html_text)
            self.assertEqual(position["statementId"], statement.id)
            self.assertEqual(position["sourceSection"], statement.source_section)
            self.assertIn(statement.qualifications[0], position["qualifications"])
            self.assertNotIn("private:rights:pp", html_text + browser_text)
            source["rights_review"]["evidence_ref"] = None
            register_path.write_text(json.dumps(register))
            with self.assertRaisesRegex(ValueError, "rights grant requires a private evidence reference"):
                load_and_validate_site_data(ROOT, custom_statements=[statement], **args)
            source["rights_review"]["evidence_ref"] = "private:rights:pp"
            programme["publication_date"] = "2023-07-05"
            programme_path.write_text(json.dumps(programme))
            register_path.write_text(json.dumps(register))
            with self.assertRaisesRegex(BuildValidationError, "publication dates differ"):
                load_and_validate_site_data(ROOT, custom_statements=[statement], **args)
            programme["publication_date"] = "2023-07-04"
            programme_path.write_text(json.dumps(programme))
            quoted = replace(statement, quote="Una cita literal")
            quoted = replace(quoted, reviews=[replace(r, content_sha256=quoted.review_fingerprint())
                                              for r in quoted.reviews])
            with self.assertRaisesRegex(BuildValidationError, "applicable rights are not approved"):
                load_and_validate_site_data(ROOT, custom_statements=[quoted], **args)
            for status in ("not_reviewed", "permission_denied"):
                source["rights_review"]["status"] = status
                register_path.write_text(json.dumps(register))
                with self.assertRaisesRegex(BuildValidationError, "applicable rights are not approved"):
                    load_and_validate_site_data(ROOT, custom_statements=[statement], **args)
            source["rights_review"]["status"] = "link_only"
            source["publication_date"] = None
            register_path.write_text(json.dumps(register))
            with self.assertRaisesRegex(BuildValidationError, "publication dates"):
                load_and_validate_site_data(ROOT, custom_statements=[statement], **args)

    def test_reported_review_is_not_actual_dated_approval(self):
        candidate = load_statement(STATEMENT)
        self.assertEqual(candidate.review_status, "under_review")
        self.assertEqual({r.reported_date for r in candidate.reviews}, {"2026-10-12"})
        self.assertTrue(all(r.review_date is None for r in candidate.reviews))
        self.assertEqual(candidate.validate(), [])
        changed = replace(candidate, summary=candidate.summary + " Cambiada.")
        self.assertIn("fingerprint", " ".join(changed.validate()))
        approved = replace(candidate, review_status="approved", last_reviewed_date="2026-10-12")
        self.assertIn("actual review date", " ".join(approved.validate()))

    def test_audit_retains_prior_states_without_asserting_human_approval(self):
        audit = json.loads((CONTENT / "audits/2023-pilot-2026-10-10.json").read_text())
        self.assertEqual(audit["election_id"], "es-gen-2023")
        self.assertFalse(audit["human_editorial_approval"])
        self.assertFalse(audit["publication_allowed"])
        self.assertEqual(len(audit["source_checks"]), 2)
        for check in audit["source_checks"]:
            self.assertTrue(check["matches_registered_hash"])
            self.assertTrue(check["is_pdf"])
        old = audit["prior_records"][str(STATEMENT.relative_to(ROOT))]
        self.assertEqual(old["reviews"][1]["review_date"], "2026-10-11")

    def test_all_generated_pilot_pages_are_labelled_and_exclude_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "site"
            build_site(ROOT, output, election_id="es-gen-2023")
            for file in output.rglob("*.html"):
                text = file.read_text()
                self.assertIn("Generales 2023 (piloto)", text, str(file))
                self.assertNotIn("Borrador sin revisión humana", text, str(file))
                self.assertNotIn("Crearemos un programa de avales", text, str(file))
            script = (output / "app.js").read_text()
            self.assertNotIn("Garantir el dret", script)
            self.assertNotIn("rel-pilot-2023-housing", script)
            self.assertFalse(any(output.rglob("*.pdf")))


if __name__ == "__main__":
    unittest.main()
