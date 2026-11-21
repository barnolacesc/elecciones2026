"""E1.4 regression: a future 2023 record root cannot import pilot drafts."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from elecciones2026.generator import BuildValidationError, build_site, load_and_validate_site_data


ROOT = Path(__file__).resolve().parents[1]


class HistoricalRecordRootIsolationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.content = self.workspace / "content"
        shutil.copytree(ROOT / "content", self.content)
        self.records = self.workspace / "records"
        self.records.mkdir()

        # A technical fixture, not an approved 2023 taxonomy or corpus.
        taxonomy = json.loads((self.content / "taxonomy.json").read_text())
        taxonomy["election_id"] = "es-gen-2023"
        (self.records / "taxonomy.json").write_text(json.dumps(taxonomy))

    def test_empty_record_root_does_not_import_example_pilot(self):
        context = load_and_validate_site_data(
            ROOT, content_dir=self.content, records_dir=self.records,
            election_id="es-gen-2023")
        self.assertEqual(context.statements, {})
        self.assertEqual(context.relationships, {})
        self.assertEqual({source.party_id for source in context.register.sources},
                         set(context.parties))
        self.assertTrue(all(source.election_id == "es-gen-2023"
                            for source in context.register.sources))

        result = build_site(
            ROOT, self.workspace / "site", content_dir=self.content,
            records_dir=self.records, election_id="es-gen-2023",
            build_date="2026-11-21")
        self.assertEqual((result.statements_count, result.relationships_count), (0, 0))

    def test_unreviewed_disk_record_fails_closed(self):
        statements = self.records / "statements"
        statements.mkdir()
        shutil.copy2(
            self.content / "examples/statements/statement-2023-pilot-proposal.json",
            statements / "candidate.json")
        with self.assertRaisesRegex(BuildValidationError, "unreviewed status"):
            load_and_validate_site_data(
                ROOT, content_dir=self.content, records_dir=self.records,
                election_id="es-gen-2023", strict_approved=False)


if __name__ == "__main__":
    unittest.main()
