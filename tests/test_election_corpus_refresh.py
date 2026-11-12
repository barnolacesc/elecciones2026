"""E1.4-2026 production isolation and incremental publication gates."""

from dataclasses import asdict, replace
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from elecciones2026.generator import (
    BuildValidationError, build_comparison_payload, build_site,
    load_and_validate_site_data, main,
)
from elecciones2026.schemas import ReviewRecord, load_statement

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "content/elections/es-gen-2026"


class ElectionCorpusRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.content = self.directory / "content"
        shutil.copytree(ROOT / "content", self.content)
        self.records = self.content / "elections/es-gen-2026"

    def load(self, **kwargs):
        return load_and_validate_site_data(
            ROOT, content_dir=self.content, records_dir=self.records, **kwargs)

    def synthetic_approved_statement(self):
        """Fabricated review evidence remains in the temporary test directory."""
        path = self.content / "sources/register.json"
        register = json.loads(path.read_text())
        source = next(s for s in register["sources"] if s["id"] == "src-2026-pp-v1")
        source.update(status="verified", direct_url="https://example.test/synthetic.pdf")
        source["rights_review"].update(
            status="link_only", reviewed_by="human-alex", review_date="2026-10-09",
            evidence_ref="test-only:rights", terms_notes="Synthetic test evidence only")
        path.write_text(json.dumps(register))
        programme = json.loads((ROOT / "content/examples/programmes/pp-2023-official.json").read_text())
        programme.update(
            election_id="es-gen-2026", programme_id="synthetic-programme",
            title="Synthetic test programme", status="official", version=source["version"],
            publication_date=source["publication_date"], sha256=source["sha256"],
            official_url=source["direct_url"], rights_status="verified_link_only")
        (self.records / "programmes").mkdir()
        (self.records / "programmes/test.json").write_text(json.dumps(programme))
        statement = replace(
            load_statement(ROOT / "content/examples/statements/statement-2023-pilot-proposal.json"),
            election_id="es-gen-2026", id="synthetic-statement", programme_id="synthetic-programme",
            summary="Propuesta sintética para comprobar la carga incremental.",
            quote=None, qualifications=[], source_url=source["direct_url"],
            source_version=source["version"], review_status="approved", reviews=[],
            last_reviewed_date="2026-10-09")
        reviews = [ReviewRecord(
            name, "2026-10-09", "approved", "Synthetic test evidence only",
            reviewer_kind="human", evidence_ref=f"test-only:{name}",
            content_sha256=statement.review_fingerprint(),
        ) for name in ("human-alex", "human-sam")]
        return replace(statement, reviews=reviews)

    def test_empty_production_never_falls_back_to_examples(self):
        ctx = self.load()
        self.assertEqual(ctx.statements, {})
        self.assertEqual(ctx.relationships, {})
        self.assertEqual(len(ctx.parties), 13)
        self.assertTrue(all(not p.is_fixture for p in ctx.parties.values()))
        self.assertTrue(all(s.election_id == "es-gen-2026" for s in ctx.register.sources))
        self.assertEqual([s.id for s in ctx.register.sources if s.party_id == "bng"], ["src-2026-bng-v2"])
        payload = build_comparison_payload(ctx)
        self.assertEqual(len(payload["topics"]), 8)
        self.assertFalse(any(payload["measuresByTopic"].values()))

    def test_missing_production_directory_fails(self):
        with self.assertRaisesRegex(BuildValidationError, "directory missing"):
            load_and_validate_site_data(ROOT, records_dir=self.directory / "missing")

    def test_wrong_election_and_fixture_records_fail(self):
        (self.records / "statements").mkdir()
        original = json.loads((ROOT / "content/examples/statements/statement-housing-proposal-approved.json").read_text())
        for election in ("es-gen-2023", "es-gen-2026"):
            original["election_id"] = election
            (self.records / "statements/test.json").write_text(json.dumps(original))
            with self.subTest(election=election), self.assertRaises(BuildValidationError):
                self.load(strict_approved=False)

    def test_pending_rights_cannot_publish_even_with_two_reviews(self):
        statement = self.synthetic_approved_statement()
        path = self.content / "sources/register.json"
        register = json.loads(path.read_text())
        next(s for s in register["sources"] if s["id"] == "src-2026-pp-v1")["rights_review"]["status"] = "not_reviewed"
        path.write_text(json.dumps(register))
        output = self.directory / "output"
        output.mkdir()
        (output / "index.html").write_text("previous output")
        with self.assertRaisesRegex(BuildValidationError, "applicable rights"):
            build_site(ROOT, output, content_dir=self.content, records_dir=self.records,
                       custom_statements=[statement], custom_relationships=[], strict_approved=False)
        self.assertEqual((output / "index.html").read_text(), "previous output")

    def test_incremental_disk_records_require_human_reviews_bound_to_content(self):
        statement = self.synthetic_approved_statement()
        (self.records / "statements").mkdir()
        path = self.records / "statements/test.json"
        path.write_text(json.dumps(asdict(statement)))
        self.assertEqual(list(self.load().statements), [statement.id])
        for changes in ({"reviewer_kind": "automated"}, {"content_sha256": None}):
            changed = replace(statement, reviews=[replace(r, **changes) for r in statement.reviews])
            path.write_text(json.dumps(asdict(changed)))
            with self.subTest(changes=changes), self.assertRaises(BuildValidationError):
                self.load(strict_approved=False)

    def test_production_output_is_deterministic_without_historical_inventory(self):
        results = [build_site(ROOT, self.directory / str(i), records_dir=RECORDS,
                              build_date="2026-11-11") for i in range(2)]
        self.assertEqual(results[0].file_hashes, results[1].file_hashes)
        for route in ("index.html", "fuentes/index.html", "metodo/index.html", "llms-full.txt"):
            text = (results[0].output_dir / route).read_text()
            self.assertNotIn("Piloto 2023", text)
            self.assertNotIn("src-2023-", text)
            self.assertNotIn("Partido Ejemplo", text)
        home = (results[0].output_dir / "index.html").read_text()
        self.assertIn("8 documentos registrados", home)
        self.assertIn("pendientes de revisión editorial", home)
        self.assertNotIn("Aviso de maqueta técnica", home)
        self.assertNotIn("Datos de prueba", home)
        sources = (results[0].output_dir / "fuentes/index.html").read_text()
        self.assertIn("Publicado sin verificar", sources)
        self.assertNotIn(">Published-unverified<", sources)

    def test_cli_defaults_to_production_records(self):
        output = self.directory / "cli"
        self.assertEqual(main(["build", "--root-dir", str(ROOT), "--output-dir", str(output)]), 0)
        self.assertNotIn("Partido Ejemplo", (output / "index.html").read_text())

    def extended_taxonomy(self):
        taxonomy = json.loads((self.content / "taxonomy.json").read_text())
        taxonomy["taxonomy_version"] = "1.1.0"
        taxonomy["topics"].append({
            "id": "synthetic-topic", "name_es": "Tema de prueba", "name_en": "Test topic",
            "description_es": "Solo pruebas", "description_en": "Tests only",
            "subtopics": [{"id": "synthetic-subtopic", "name_es": "Subtema", "name_en": "Subtopic"}],
        })
        path = self.records / "taxonomy.json"
        path.write_text(json.dumps(taxonomy))
        return path, taxonomy

    def test_election_taxonomy_extends_topics_without_approving_statements(self):
        self.extended_taxonomy()
        statement = replace(self.synthetic_approved_statement(), topic_id="synthetic-topic",
                            subtopic_id="synthetic-subtopic", reviews=[], review_status="draft",
                            last_reviewed_date=None, source_page="1-2, 5")
        (self.records / "statements").mkdir()
        path = self.records / "statements/test.json"
        path.write_text(json.dumps(asdict(statement)))
        with self.assertRaisesRegex(BuildValidationError, "unreviewed status"):
            self.load()
        approved = replace(statement, review_status="approved", last_reviewed_date="2026-10-09",
                           reviews=self.synthetic_reviews(statement))
        path.write_text(json.dumps(asdict(approved)))
        ctx = self.load()
        self.assertEqual(len(ctx.taxonomy.topics), 9)
        self.assertEqual(list(ctx.statements), [statement.id])
        payload = build_comparison_payload(ctx)
        position = payload["measuresByTopic"]["synthetic-topic"][0]["positions"][statement.party_id]
        self.assertEqual(position["sourcePage"], "1-2, 5")
        self.assertTrue(position["sourceUrl"].endswith("#page=1"))
        output = self.directory / "extended-output"
        result = build_site(ROOT, output, content_dir=self.content, records_dir=self.records)
        self.assertEqual(result.topics_count, 9)
        self.assertIn("9 temas", (output / "llms.txt").read_text())
        topic_html = (output / "temas/synthetic-topic/index.html").read_text()
        self.assertIn("#page=1", topic_html)
        self.assertIn("1-2, 5", topic_html)
        invalid = replace(approved, subtopic_id="rental-regulation")
        path.write_text(json.dumps(asdict(invalid)))
        with self.assertRaisesRegex(BuildValidationError, "not under topic"):
            self.load()

    @staticmethod
    def synthetic_reviews(statement):
        return [ReviewRecord(name, "2026-10-09", "approved", "Synthetic test evidence only",
                             reviewer_kind="human", evidence_ref=f"test-only:{name}",
                             content_sha256=statement.review_fingerprint())
                for name in ("human-alex", "human-sam")]

    def test_draft_cross_election_and_incomplete_taxonomies_fail(self):
        path, taxonomy = self.extended_taxonomy()
        for changes in ({"taxonomy_version": "1.1.0-draft"}, {"election_id": "es-gen-2023"},
                        {"topics": taxonomy["topics"][1:]}):
            path.write_text(json.dumps({**taxonomy, **changes}))
            with self.subTest(changes=list(changes)), self.assertRaises(BuildValidationError):
                self.load()


if __name__ == "__main__":
    unittest.main()
