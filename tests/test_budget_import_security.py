"""E10.2 synthetic correction and offline import security acceptance."""
import copy
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

import test_budget as fixtures
from elecciones2026 import budget, budget_chart, budget_view
from elecciones2026.generator import BuildValidationError, build_site

ROOT = Path(__file__).resolve().parents[1]


class BudgetImportSecurityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.BudgetTests()
        self.fixture.setUp()
        self.bundle, self.payload = self.fixture.payload()
        self.manifest, _ = budget.load_bundle(self.bundle, require_publication=False)

    def tearDown(self):
        self.fixture.tearDown()

    def review(self, name, subject_id):
        subject = self.payload[name]
        return {"id": "fixture-review", "subject_id": subject_id,
                "subject_sha256": budget.digest(budget.canonical(subject)),
                "subject_version": subject.get("source_version", subject.get("version", subject.get("mapping_version", subject.get("schema_version")))),
                "role": "editorial", "human_reviewer_id": "fixture-only",
                "decision": "approved", "reviewed_at": "2026-10-12T12:00:00Z",
                "evidence_ref": "synthetic-not-human-approval"}

    def test_changed_source_measurement_mapping_and_sections_invalidate_reviews(self):
        cases = (("source.json", self.payload["source.json"]["id"], "retrieved_at", "2026-10-12T12:00:00Z"),
                 ("measurement.json", self.payload["measurement.json"]["id"], "scope_limit_es", "Nota corregida"),
                 ("mapping.json", "topic-mapping", "aggregation_note", "Corrected context"),
                 ("sections.json", "section-dictionary", "review_refs", ["new-review"]))
        for name, subject_id, field, value in cases:
            with self.subTest(subject=name):
                candidate = copy.deepcopy(self.payload)
                candidate["reviews.json"] = [self.review(name, subject_id)]
                budget.validate_payload(candidate, ROOT / "content/taxonomy.json")
                candidate[name][field] = value
                with self.assertRaisesRegex(budget.BudgetError, "invalidated"):
                    budget.validate_payload(candidate, ROOT / "content/taxonomy.json")

    def test_taxonomy_change_needs_new_mapping_review_even_with_updated_hash(self):
        candidate = copy.deepcopy(self.payload)
        candidate["reviews.json"] = [self.review("mapping.json", "topic-mapping")]
        taxonomy = budget.load_json(ROOT / "content/taxonomy.json")
        taxonomy["topics"][0]["label_es"] = "Tema corregido"
        path = self.fixture.root / "taxonomy.json"
        path.write_bytes(budget.canonical(taxonomy))
        with self.assertRaisesRegex(budget.BudgetError, "Taxonomy changed"):
            budget.validate_payload(candidate, path)
        candidate["mapping.json"]["taxonomy_sha256"] = budget.digest(path.read_bytes())
        with self.assertRaisesRegex(budget.BudgetError, "invalidated"):
            budget.validate_payload(candidate, path)

    def test_correction_record_removes_synthetic_approval(self):
        candidate = copy.deepcopy(self.payload)
        candidate["reviews.json"] = [self.review("mapping.json", "topic-mapping")]
        candidate["corrections.json"] = [{"id": "fixture-correction", "date": "2026-10-12",
            "reason": "Synthetic withdrawal", "prior_bundle": self.bundle.name,
            "replacement_bundle": None, "affected_record_ids": ["topic-mapping"],
            "invalidated_review_refs": ["fixture-review"], "review_refs": []}]
        # Test the role-set gate only; never make this fixture a real approval.
        candidate["source.json"].update(is_fixture=False, rights_status="approved_derived_display")
        with self.assertRaisesRegex(budget.BudgetError, "review required"):
            budget.validate_reviews(candidate["reviews.json"], candidate, candidate["corrections.json"], True)

    def test_source_urls_are_checked_during_import_and_bundle_validation(self):
        unsafe = ('javascript:alert(1)', 'file:///etc/passwd', 'http://example.invalid/data',
                  'https:///missing-host', 'https://user:secret@example.invalid/',
                  'https://example.invalid:8000/', 'https://example.invalid:bad/',
                  'https://example.invalid/\nspoof', 'https://example.invalid/\\escape')
        for value in unsafe:
            with self.subTest(url=value):
                candidate = copy.deepcopy(self.payload)
                candidate["source.json"]["url"] = value
                with self.assertRaises(budget.BudgetError):
                    budget.validate_payload(candidate, ROOT / "content/taxonomy.json")
                candidate = copy.deepcopy(self.payload)
                candidate["sections.json"]["sections"][0]["source_url"] = value
                with self.assertRaises(budget.BudgetError):
                    budget.validate_payload(candidate, ROOT / "content/taxonomy.json")
                register = copy.deepcopy(self.fixture.register)
                next(r for r in register["sources"] if r["role"] == "matrix_csv")["url"] = value
                with self.assertRaises(budget.BudgetError):
                    budget.normalize_source(register, self.fixture.raw)

    def test_source_directed_urls_and_formula_labels_never_execute_or_fetch(self):
        for label in ('=HYPERLINK("https://example.invalid/","x")', '+SUM(1,2)',
                      '-SUM(1,2)', '@SUM(1,2)', '\t=1+1', '<script>alert(1)</script>'):
            with self.subTest(label=label), patch.object(socket, "socket", side_effect=AssertionError("No network")):
                self.fixture.mapping["mappings"][0]["label_es"] = label
                self.fixture.flush()
                path = self.fixture.create()
                manifest, payload = budget.load_bundle(path, require_publication=False)
                payload["values.json"]["margins"][0]["label_es"] = label
                html = budget_view.render_budget_content(payload, manifest, path.name, {})
                svg = budget_chart.share_svg(payload, manifest, path.name)
                self.assertNotIn('<script>', html + svg)
                self.assertEqual({p.suffix for p in path.iterdir()}, {".json"})
                self.assertIn(label, budget.load_json(path / "mapping.json")["mappings"][0]["label_es"])

    def test_file_replacement_after_read_cannot_change_parsed_values(self):
        real_read = budget.bounded_read
        def replace_after_read(path):
            raw = real_read(path)
            if Path(path) == self.bundle / "values.json":
                Path(path).write_text("unchecked replacement")
            return raw
        with patch.object(budget, "bounded_read", side_effect=replace_after_read):
            manifest, payload = budget.load_bundle(self.bundle, require_publication=False)
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(payload, self.payload)
        with self.assertRaisesRegex(budget.BudgetError, "hash mismatch"):
            budget.load_bundle(self.bundle, require_publication=False)

    def test_payload_read_once_and_copy_uses_validated_snapshot(self):
        real_read = budget.bounded_read
        reads = []
        def count(path):
            reads.append(Path(path))
            return real_read(path)
        with patch.object(budget, "bounded_read", side_effect=count):
            budget.load_bundle(self.bundle, require_publication=False)
        for name in budget.FILES | {"manifest.json"}:
            self.assertEqual(reads.count(self.bundle / name), 1)
        with patch.object(budget, "load_bundle", return_value=(self.manifest, self.payload)):
            (self.bundle / "values.json").write_text("tampered after validation")
            target = budget.copy_reviewed_bundle(self.bundle, self.fixture.root / "site", expected_manifest=self.manifest)
        for name, value in self.payload.items():
            self.assertEqual((target / name).read_bytes(), budget.canonical(value))
        self.assertEqual((target / "manifest.json").read_bytes(), budget.canonical(self.manifest))

    def test_changed_snapshot_and_stage_failure_preserve_prior_site(self):
        output = self.fixture.root / "site"
        output.mkdir()
        (output / "index.html").write_text("previous release")
        changed = copy.deepcopy(self.manifest)
        changed["build_date"] = "2026-10-12"
        with patch.object(budget, "load_bundle", return_value=(changed, self.payload)):
            with self.assertRaisesRegex(budget.BudgetError, "changed after"):
                budget.copy_reviewed_bundle(self.bundle, output, expected_manifest=self.manifest)
        with patch.object(budget, "load_bundle", return_value=(self.manifest, self.payload)), \
             patch.object(budget, "copy_reviewed_bundle", side_effect=budget.BudgetError("Synthetic copy failure")):
            with self.assertRaises(BuildValidationError):
                build_site(ROOT, output, budget_bundle=self.bundle)
        self.assertEqual((output / "index.html").read_text(), "previous release")
        self.assertEqual(list(output.iterdir()), [output / "index.html"])

    def test_mixed_contract_and_size_limits_preserve_prior_artifact(self):
        candidate = copy.deepcopy(self.payload)
        candidate["measurement.json"]["source_sha256"] = "0" * 64
        with self.assertRaisesRegex(budget.BudgetError, "Mixed"):
            budget.validate_payload(candidate, ROOT / "content/taxonomy.json")
        with patch.object(budget, "MAX_BUNDLE_BYTES", 1), self.assertRaisesRegex(budget.BudgetError, "size limits"):
            self.fixture.create(output_dir=self.fixture.root / "rejected")
        self.assertFalse((self.fixture.root / "rejected").exists())
        self.assertEqual(budget.load_bundle(self.bundle, require_publication=False)[0], self.manifest)

    def test_symlinks_and_absolute_archive_paths_are_rejected(self):
        link = self.fixture.root / "linked.csv"
        link.symlink_to(self.fixture.source_path)
        with self.assertRaisesRegex(budget.BudgetError, "regular file"):
            budget.bounded_read(link)
        for value in ('/etc/passwd', 'a/../../private.csv', 'nested/values.json', 'C:\\private.csv'):
            with self.subTest(path=value):
                manifest = copy.deepcopy(self.manifest)
                manifest["files"][0]["path"] = value
                path = self.fixture.root / budget.digest(budget.canonical(manifest))
                path.mkdir()
                (path / "manifest.json").write_bytes(budget.canonical(manifest))
                with self.assertRaisesRegex(budget.BudgetError, "Unexpected bundle paths"):
                    budget.load_bundle(path, require_publication=False)
