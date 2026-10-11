"""E10.2 tests use synthetic matrices; no network or political sources."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from elecciones2026 import budget
from elecciones2026.generator import BuildValidationError, build_site
from elecciones2026.methodology import CORE_TOPIC_IDS
from test_budget_source_audit import sources

ROOT = Path(__file__).resolve().parents[1]


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.raw, _ = sources()
        self.source_path = self.root / "input.csv"
        self.source_path.write_bytes(self.raw)
        register = json.loads((ROOT / "docs/budget-context/2023/source-register.json").read_text())
        register["is_fixture"] = True
        selected = next(r for r in register["sources"] if r["role"] == "matrix_csv")
        selected["sha256"] = budget.digest(self.raw)
        selected["byte_count"] = len(self.raw)
        self.register = register
        measurement = json.loads((ROOT / "docs/budget-context/2023/measurement.json").read_text())
        measurement["source_sha256"] = budget.digest(self.raw)
        measurement["denominator_amount_thousand_eur"] = "0.03"
        measurement["denominator_locator"] = {"csv_line": 11, "column": "Total"}
        self.measurement = measurement
        taxonomy = (ROOT / "content/taxonomy.json").read_bytes()
        self.mapping = {"mapping_version": "1.0.0", "dataset_version": register["source_version"],
            "taxonomy_version": "1.0.0", "taxonomy_sha256": budget.digest(taxonomy), "mappings": [],
            "unmapped_policy_codes": ["12"], "overlapping_policy_references": {"11": list(CORE_TOPIC_IDS)},
            "aggregate_topic_total": None, "aggregation_note": "Synthetic context links", "review_state": "draft"}
        for topic in CORE_TOPIC_IDS:
            self.mapping["mappings"].append({"id": "fixture-topic-" + topic, "topic_id": topic, "label_es": "Tema de prueba",
                "coverage_state": "mapped", "coverage_note_es": "Datos de prueba", "rationale": "Synthetic test reference",
                "aggregation_mode": "none", "topic_amount": None, "review_state": "draft", "review_refs": [],
                "row_refs": [{"source_ref": selected["id"], "source_version": register["source_version"], "policy_code": "11",
                              "relationship": "direct_context", "source_locator": {"csv_line": 9, "column": "Total"}}]})
        dictionary = json.loads((ROOT / "docs/budget-context/2023/section-dictionary.json").read_text())
        dictionary["sections"] = [row for row in dictionary["sections"] if row["code"] in {"01", "60"}]
        (self.root / "section-dictionary.json").write_bytes(budget.canonical(dictionary))
        self.flush()

    def tearDown(self):
        self.temporary.cleanup()

    def flush(self):
        for name, data in (("register", self.register), ("contract", self.measurement), ("mapping", self.mapping)):
            (self.root / (name + ".json")).write_bytes(budget.canonical(data))

    def create(self, **overrides):
        args = dict(source_path=self.source_path, contract_path=self.root / "contract.json", mapping_path=self.root / "mapping.json",
                    register_path=self.root / "register.json", output_dir=self.root / "bundles", build_date="2026-10-11", draft=True)
        args.update(overrides)
        return budget.import_bundle(**args)

    def payload(self):
        path = self.create()
        return path, budget.load_bundle(path, require_publication=False)[1]

    def test_offline_deterministic_bundle_and_null_cells(self):
        with patch.object(socket, "socket", side_effect=AssertionError("No network")):
            first = self.create()
            second = self.create(output_dir=self.root / "second")
            self.assertEqual(first.name, second.name)
            for path in first.iterdir():
                self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
            manifest, payload = budget.load_bundle(first, require_publication=False)
            self.assertEqual(manifest["publication_state"], "draft")
            missing = [c for c in payload["values.json"]["cells"] if c["value_state"] == "unavailable"]
            self.assertEqual(len(missing), 1)
            self.assertIsNone(missing[0]["amount_thousand_eur"])
            self.assertEqual(self.create(), first)

    def test_decimal_conversion_rounding_and_share(self):
        self.assertEqual(budget.display_amount("1234567.89"), "1.234,57")
        self.assertEqual(budget.display_amount("0.01"), "< 0,01")
        self.assertEqual(budget.display_amount("0.00"), "0,00")
        self.assertIsNone(budget.display_amount(None))
        self.assertEqual(budget.share("1", "3"), "33.33")
        self.assertEqual(budget.share("2", "3"), "66.67")
        with self.assertRaises(budget.BudgetError):
            budget.share("1", "0")

    def test_changed_source_preserves_existing_bundle(self):
        path = self.create()
        previous = (path / "manifest.json").read_bytes()
        self.source_path.write_bytes(self.raw + b"changed")
        with self.assertRaisesRegex(budget.BudgetError, "hash or size"):
            self.create()
        self.assertEqual((path / "manifest.json").read_bytes(), previous)

    def test_wrong_accounting_basis_or_unit_is_rejected(self):
        for field, value in (("accounting_basis", "payments"), ("source_unit", "million_eur"), ("budget_year", 2026)):
            with self.subTest(field=field):
                original = self.register[field]
                self.register[field] = value
                self.flush()
                with self.assertRaises(budget.BudgetError):
                    self.create()
                self.register[field] = original

    def test_unknown_schema_fields_and_imputation_are_rejected(self):
        _, payload = self.payload()
        values = payload["values.json"]
        values["cells"][0]["estimated_amount"] = "123"
        with self.assertRaisesRegex(budget.BudgetError, "unknown fields"):
            budget.validate_payload(payload, ROOT / "content/taxonomy.json")
        del values["cells"][0]["estimated_amount"]
        missing = next(c for c in values["cells"] if c["value_state"] == "unavailable")
        missing["amount_thousand_eur"] = "0"
        with self.assertRaisesRegex(budget.BudgetError, "imputed"):
            budget.validate_payload(payload, ROOT / "content/taxonomy.json")

    def test_duplicate_or_missing_cells_are_rejected(self):
        _, payload = self.payload()
        for change in (lambda cells: cells.append(copy.deepcopy(cells[0])), lambda cells: cells.pop()):
            candidate = copy.deepcopy(payload)
            change(candidate["values.json"]["cells"])
            with self.assertRaises(budget.BudgetError):
                budget.validate_payload(candidate, ROOT / "content/taxonomy.json")

    def test_cell_and_margin_mismatch_is_rejected(self):
        _, payload = self.payload()
        payload["values.json"]["cells"][0]["amount_thousand_eur"] = "10"
        with self.assertRaisesRegex(budget.BudgetError, "reconcile"):
            budget.validate_payload(payload, ROOT / "content/taxonomy.json")

    def test_taxonomy_and_mapping_scope_are_checked(self):
        self.mapping["taxonomy_sha256"] = "0" * 64
        self.flush()
        with self.assertRaisesRegex(budget.BudgetError, "Taxonomy changed"):
            self.create()

    def test_mapping_locator_unknown_policy_and_duplicate_are_checked(self):
        for mutator in (
            lambda refs: refs[0]["source_locator"].update(csv_line=10),
            lambda refs: refs[0].update(policy_code="99"),
            lambda refs: refs.append(copy.deepcopy(refs[0])),
        ):
            saved = copy.deepcopy(self.mapping)
            mutator(self.mapping["mappings"][0]["row_refs"])
            self.flush()
            with self.assertRaises(budget.BudgetError):
                self.create()
            self.mapping = saved

    def test_broad_context_cannot_be_summed_or_called_exact(self):
        topic = self.mapping["mappings"][0]
        topic["row_refs"][0]["relationship"] = "broad_related_context"
        self.flush()
        with self.assertRaisesRegex(budget.BudgetError, "Broad context"):
            self.create()
        topic["coverage_state"] = "partial"
        topic["aggregation_mode"] = "exact_sum"
        self.flush()
        with self.assertRaisesRegex(budget.BudgetError, "Broad context"):
            self.create()

    def test_draft_rejected_by_public_load_and_generator(self):
        path = self.create()
        with self.assertRaisesRegex(budget.BudgetError, "Draft budget"):
            budget.load_bundle(path)
        output = self.root / "existing-site"
        output.mkdir()
        (output / "index.html").write_text("previous safe release")
        with self.assertRaises(BuildValidationError):
            build_site(ROOT, output, budget_bundle=path)
        self.assertEqual((output / "index.html").read_text(), "previous safe release")
        self.assertEqual(list(output.iterdir()), [output / "index.html"])

    def test_public_import_requires_human_review(self):
        with self.assertRaises(budget.BudgetError):
            self.create(draft=False)
        self.assertFalse((self.root / "bundles").exists())

    def test_tampered_and_unmanifested_bundle_files_are_rejected(self):
        path = self.create()
        (path / "source.json").write_text("{}")
        with self.assertRaisesRegex(budget.BudgetError, "hash mismatch"):
            budget.load_bundle(path, require_publication=False)
        with self.assertRaisesRegex(budget.BudgetError, "immutable bundle differs"):
            self.create()

    def test_archive_paths_are_rejected(self):
        path = self.create()
        manifest = budget.load_json(path / "manifest.json")
        manifest["files"][0]["path"] = "../private.csv"
        new = self.root / budget.digest(budget.canonical(manifest))
        path.rename(new)
        (new / "manifest.json").write_bytes(budget.canonical(manifest))
        with self.assertRaisesRegex(budget.BudgetError, "Unexpected bundle paths"):
            budget.load_bundle(new, require_publication=False)

    def test_size_limit_and_duplicate_json_keys(self):
        with patch.object(budget, "MAX_BYTES", 4), self.assertRaises(budget.BudgetError):
            budget.bounded_read(self.source_path)
        path = self.root / "duplicate.json"
        path.write_text('{"value":1,"value":2}')
        with self.assertRaisesRegex(budget.BudgetError, "Duplicate JSON"):
            budget.load_json(path)

    def test_review_invalidated_by_source_or_mapping_change(self):
        _, payload = self.payload()
        review = {"id": "review-fixture", "subject_id": "topic-mapping", "subject_sha256": budget.digest(budget.canonical(payload["mapping.json"])),
                  "subject_version": "1.0.0", "role": "editorial", "human_reviewer_id": "fixture-editor", "decision": "approved",
                  "reviewed_at": "2026-10-11T12:00:00Z", "evidence_ref": "synthetic-fixture-only"}
        payload["reviews.json"] = [review]
        budget.validate_payload(payload, ROOT / "content/taxonomy.json")
        payload["mapping.json"]["mappings"][0]["coverage_note_es"] = "Nota corregida"
        with self.assertRaisesRegex(budget.BudgetError, "invalidated"):
            budget.validate_payload(payload, ROOT / "content/taxonomy.json")

    def test_html_in_labels_stays_inert_data(self):
        self.mapping["mappings"][0]["label_es"] = '<img src=x onerror="alert(1)">'
        self.flush()
        path, payload = self.payload()
        self.assertIn("<img", payload["mapping.json"]["mappings"][0]["label_es"])
        self.assertEqual({p.suffix for p in path.iterdir()}, {".json"})
        self.assertNotIn("input.csv", {p.name for p in path.iterdir()})

    def test_malformed_source_fails_after_hash_verification(self):
        malformed = self.raw.replace(b"0,01", b"=1+2", 1)
        self.source_path.write_bytes(malformed)
        source = next(r for r in self.register["sources"] if r["role"] == "matrix_csv")
        source.update(sha256=budget.digest(malformed), byte_count=len(malformed))
        self.measurement["source_sha256"] = budget.digest(malformed)
        self.flush()
        with self.assertRaisesRegex(budget.BudgetError, "Invalid source number"):
            self.create()


if __name__ == "__main__":
    unittest.main()
