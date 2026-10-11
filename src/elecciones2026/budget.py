"""Bounded offline official-budget import and immutable bundle validation (E10.2)."""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, localcontext
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlsplit

from elecciones2026.budget_source_audit import matrix, number
from elecciones2026.methodology import CORE_TOPIC_IDS

SCHEMA_VERSION = "1.0.0"
MAX_BYTES = 4 * 1024 * 1024
MAX_BUNDLE_BYTES = 16 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[2]
FILES = {"source.json", "measurement.json", "values.json", "mapping.json",
         "reviews.json", "corrections.json", "decisions.json", "sections.json"}
HASH = re.compile(r"^[a-f0-9]{64}$")
AMOUNT = re.compile(r"^(0|[1-9]\d*)(\.\d+)?$")


class BudgetError(ValueError):
    """Budget source, arithmetic, integrity, or publication check failed."""


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise BudgetError(f"Source is not a regular file: {path.name}")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise BudgetError(f"File exceeds {MAX_BYTES} bytes")
    return raw


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BudgetError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path):
    try:
        return json.loads(bounded_read(path), object_pairs_hook=unique_pairs,
                          parse_constant=lambda value: (_ for _ in ()).throw(BudgetError("Non-finite JSON number")))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise BudgetError(f"Invalid JSON: {Path(path).name}") from error


def schema_validate(kind, value):
    definitions = load_json(ROOT / "content/schemas/budget-records.schema.json")["$defs"]
    def check(rule, item, location):
        if "$ref" in rule:
            return check(definitions[rule["$ref"].split("/")[-1]], item, location)
        if "const" in rule and item != rule["const"]:
            raise BudgetError(f"{location}: unexpected constant")
        if "enum" in rule and item not in rule["enum"]:
            raise BudgetError(f"{location}: unexpected enum")
        types = rule.get("type", [])
        types = [types] if isinstance(types, str) else types
        tests = {"object": type(item) is dict, "array": type(item) is list,
                 "string": type(item) is str, "integer": type(item) is int,
                 "boolean": type(item) is bool, "null": item is None}
        if types and not any(tests[t] for t in types):
            raise BudgetError(f"{location}: invalid type")
        if type(item) is str:
            if len(item) < rule.get("minLength", 0) or ("pattern" in rule and not re.fullmatch(rule["pattern"], item)):
                raise BudgetError(f"{location}: invalid string")
        if type(item) is int and item < rule.get("minimum", item):
            raise BudgetError(f"{location}: below minimum")
        if type(item) is list and "items" in rule:
            for index, entry in enumerate(item):
                check(rule["items"], entry, f"{location}[{index}]")
        if type(item) is dict:
            properties = rule.get("properties", {})
            if set(rule.get("required", [])) - set(item):
                raise BudgetError(f"{location}: missing required fields")
            extra = set(item) - set(properties)
            additional = rule.get("additionalProperties", True)
            if extra and additional is False:
                raise BudgetError(f"{location}: unknown fields {sorted(extra)}")
            for key, entry in item.items():
                if key in properties:
                    check(properties[key], entry, f"{location}.{key}")
                elif isinstance(additional, dict):
                    check(additional, entry, f"{location}.{key}")
    check(definitions[kind], value, kind)


def decimal_amount(value):
    if not isinstance(value, str) or len(value) > 30 or not AMOUNT.fullmatch(value):
        raise BudgetError("Invalid exact decimal amount")
    return Decimal(value)


def display_amount(value):
    if value is None:
        return None
    amount = decimal_amount(value) / Decimal(1000)
    rounded = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "< 0,01" if amount > 0 and rounded == 0 else f"{rounded:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def share(value, denominator):
    if value is None:
        return None
    with localcontext() as context:
        context.prec = 50
        total = decimal_amount(denominator)
        if total <= 0:
            raise BudgetError("Denominator must be positive")
        return str((decimal_amount(value) * 100 / total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def normalize_source(register, raw):
    matches = [record for record in register["sources"] if record["role"] == "matrix_csv"]
    if len(matches) != 1:
        raise BudgetError("Exactly one audited CSV source is required")
    record = matches[0]
    if digest(raw) != record["sha256"] or len(raw) != record["byte_count"]:
        raise BudgetError("Source hash or size changed; a new audit is required")
    selected = {key: register[key] for key in ("source_version", "budget_year", "accounting_basis", "table_id",
                "source_unit", "institutional_scope", "chapters", "consolidation", "publication_date", "rights_status", "review_state", "review_refs")}
    selected.update({key: record[key] for key in ("id", "url", "sha256", "byte_count", "encoding", "retrieved_at")})
    selected.update(schema_version=SCHEMA_VERSION, is_fixture=register.get("is_fixture", False),
                    companion_sources=[{key: item[key] for key in ("id", "url", "sha256", "byte_count")}
                                       for item in register["sources"] if item["role"] != "matrix_csv"])
    schema_validate("Source", selected)
    for item in [selected, *selected["companion_sources"]]:
        url = urlsplit(item["url"])
        if url.scheme != "https" or url.username or url.password or url.port not in (None, 443):
            raise BudgetError("Source URL must be credential-free HTTPS")
    return selected


def normalize_measurement(contract, source):
    keys = load_json(ROOT / "content/schemas/budget-records.schema.json")["$defs"]["Measurement"]["properties"]
    result = {key: contract[key] for key in keys if key != "schema_version"}
    result["schema_version"] = SCHEMA_VERSION
    schema_validate("Measurement", result)
    if result["source_ref"] != source["id"] or result["source_sha256"] != source["sha256"]:
        raise BudgetError("Measurement contract is not bound to this source")
    if decimal_amount(result["denominator_amount_thousand_eur"]) <= 0:
        raise BudgetError("Invalid measurement denominator")
    return result


def normalize_values(raw, source):
    if len(raw.splitlines()) > 256:
        raise BudgetError("Source row limit exceeded")
    try:
        rows, header, policies, total, codes = matrix(raw)
    except (ValueError, IndexError, UnicodeError, csv.Error) as error:
        raise BudgetError(f"Invalid source matrix: {error}") from error
    if len(codes) > 128 or len(codes) * len(policies) > 4096:
        raise BudgetError("Source column limit exceeded")
    values = {"schema_version": SCHEMA_VERSION, "source_ref": source["id"], "source_version": source["source_version"],
              "budget_year": 2023, "accounting_basis": "approved_credits", "cells": [], "margins": []}
    line_numbers = {row[0]: index for index, row in enumerate(rows, 1) if row and row[0].isdigit()}
    def amount(text):
        try:
            return str(number(text)) if text else None
        except ValueError as error:
            raise BudgetError(str(error)) from error
    for row in policies:
        code = row[0]
        for index, section in enumerate(codes, 2):
            values["cells"].append({"id": f"cell-{code}-{section}", "source_ref": source["id"],
                "source_version": source["source_version"], "accounting_basis": "approved_credits", "policy_code": code,
                "section_code": section, "amount_thousand_eur": amount(row[index]), "value_state": "official" if row[index] else "unavailable",
                "source_locator": {"csv_line": line_numbers[code], "column": header[index]}})
        values["margins"].append({"id": f"policy-{code}", "kind": "policy", "code": code, "label_es": row[1].strip(),
            "amount_thousand_eur": amount(row[-2]), "source_locator": {"csv_line": line_numbers[code], "column": "Total"}})
    total_line = next(i for i, row in enumerate(rows, 1) if row and row[:2] == ["", "TOTAL"])
    for index, code in enumerate(codes, 2):
        values["margins"].append({"id": f"section-{code}", "kind": "section", "code": code, "label_es": header[index],
            "amount_thousand_eur": amount(total[index]), "source_locator": {"csv_line": total_line, "column": header[index]}})
    values["margins"].append({"id": "grand-total", "kind": "grand_total", "code": None, "label_es": "Total",
        "amount_thousand_eur": amount(total[-2]), "source_locator": {"csv_line": total_line, "column": "Total"}})
    return values


def validate_values(values, source, measurement):
    schema_validate("Values", values)
    if values["source_ref"] != source["id"] or values["source_version"] != source["source_version"]:
        raise BudgetError("Values are bound to another source version")
    margins = values["margins"]
    if len({row["id"] for row in margins}) != len(margins):
        raise BudgetError("Duplicate margin")
    groups = {kind: [row for row in margins if row["kind"] == kind] for kind in ("policy", "section", "grand_total")}
    if len(groups["grand_total"]) != 1:
        raise BudgetError("Exactly one grand total is required")
    grand_total = groups["grand_total"][0]
    if measurement["denominator_locator"] != grand_total["source_locator"]:
        raise BudgetError("Denominator source locator differs")
    total = decimal_amount(grand_total["amount_thousand_eur"])
    if total != decimal_amount(measurement["denominator_amount_thousand_eur"]):
        raise BudgetError("Official denominator differs from measurement")
    policy = {row["code"]: row for row in groups["policy"]}
    section = {row["code"]: row for row in groups["section"]}
    if len(policy) != len(groups["policy"]) or len(section) != len(groups["section"]):
        raise BudgetError("Duplicate margin classification code")
    for group in (policy, section):
        if not group or sum((decimal_amount(row["amount_thousand_eur"]) for row in group.values()), Decimal(0)) != total:
            raise BudgetError("Official margin reconciliation failed")
    keys = set()
    sums = {"policy": {code: Decimal(0) for code in policy}, "section": {code: Decimal(0) for code in section}}
    for cell in values["cells"]:
        key = (cell["policy_code"], cell["section_code"])
        if key in keys or key[0] not in policy or key[1] not in section:
            raise BudgetError("Duplicate or unknown cross-tab cell")
        keys.add(key)
        if cell["id"] != f"cell-{key[0]}-{key[1]}" or cell["source_locator"] != {
            "csv_line": policy[key[0]]["source_locator"]["csv_line"], "column": f"Secc. {key[1]}"
        }:
            raise BudgetError("Cell identity or source locator differs")
        if cell["source_ref"] != source["id"] or cell["source_version"] != source["source_version"]:
            raise BudgetError("Cell source version differs")
        if cell["value_state"] == "unavailable":
            if cell["amount_thousand_eur"] is not None:
                raise BudgetError("Unavailable cell has an imputed value")
        else:
            value = decimal_amount(cell["amount_thousand_eur"])
            sums["policy"][key[0]] += value
            sums["section"][key[1]] += value
    if len(keys) != len(policy) * len(section):
        raise BudgetError("Missing cross-tab cells")
    for kind, group in (("policy", policy), ("section", section)):
        for code, row in group.items():
            if sums[kind][code] != decimal_amount(row["amount_thousand_eur"]):
                raise BudgetError(f"Present cells do not reconcile to {kind} {code}")
    # This observes present-cell reconciliation; missing cells still remain null.


def normalize_sections(sections, source, values):
    result = {key: value for key, value in sections.items() if key != "record_version"}
    result.update(schema_version=SCHEMA_VERSION, review_refs=sections.get("review_refs", []))
    schema_validate("Sections", result)
    matches = [item for item in source["companion_sources"] if item["id"] == result["source_ref"]]
    if len(matches) != 1 or matches[0]["sha256"] != result["source_sha256"]:
        raise BudgetError("Section dictionary source differs")
    codes = {row["code"] for row in values["margins"] if row["kind"] == "section"}
    if len(result["sections"]) != len(codes) or {row["code"] for row in result["sections"]} != codes:
        raise BudgetError("Section dictionary coverage differs")
    for section in result["sections"]:
        if section["is_ministry"] != section["name_es"].startswith("MINISTERIO "):
            raise BudgetError("Section classification differs")
        if urlsplit(section["source_url"]).scheme != "https":
            raise BudgetError("Section locator must be HTTPS")
    return result


def normalize_mapping(mapping, source, values, taxonomy_path):
    result = {key: value for key, value in mapping.items() if key != "publication_approved"}
    result["schema_version"] = SCHEMA_VERSION
    schema_validate("Mapping", result)
    taxonomy_raw = bounded_read(taxonomy_path)
    taxonomy = load_json(taxonomy_path)
    if result["taxonomy_sha256"] != digest(taxonomy_raw) or result["taxonomy_version"] != taxonomy["taxonomy_version"]:
        raise BudgetError("Taxonomy changed; mapping review is required")
    expected = set(CORE_TOPIC_IDS)
    topics = result["mappings"]
    if len(topics) != len(expected) or {topic["topic_id"] for topic in topics} != expected:
        raise BudgetError("All eight taxonomy topics must have coverage records")
    if result["dataset_version"] != source["source_version"]:
        raise BudgetError("Mapping dataset version differs")
    policy = {row["code"]: row for row in values["margins"] if row["kind"] == "policy"}
    used = {}
    for topic in topics:
        refs = topic["row_refs"]
        if topic["coverage_state"] in ("not_available", "not_comparable") and refs:
            raise BudgetError("Gap record cannot reference comparable values")
        if topic["coverage_state"] in ("mapped", "partial") and not refs:
            raise BudgetError("Mapped topic needs source references")
        seen = set()
        for ref in refs:
            code = ref["policy_code"]
            if code in seen or code not in policy:
                raise BudgetError("Duplicate or unknown mapping policy")
            seen.add(code)
            if ref["source_ref"] != source["id"] or ref["source_version"] != source["source_version"] or ref["source_locator"] != policy[code]["source_locator"]:
                raise BudgetError("Mapping source locator/version differs")
            if ref["relationship"] == "broad_related_context" and (topic["aggregation_mode"] != "none" or topic["coverage_state"] != "partial"):
                raise BudgetError("Broad context cannot become an allocated topic total")
            used.setdefault(code, []).append(topic["topic_id"])
    if result["unmapped_policy_codes"] != sorted(set(policy) - set(used)) or result["overlapping_policy_references"] != {c: refs for c, refs in used.items() if len(refs) > 1}:
        raise BudgetError("Mapping coverage audit differs")
    return result


def validate_reviews(reviews, payload, corrections, require_publication):
    subjects = {payload[name]["id"]: (name, payload[name]) for name in ("source.json", "measurement.json")}
    subjects["topic-mapping"] = ("mapping.json", payload["mapping.json"])
    subjects["section-dictionary"] = ("sections.json", payload["sections.json"])
    approved = {key: set() for key in subjects}
    invalidated = {ref for correction in corrections for ref in correction["invalidated_review_refs"]}
    seen = set()
    for review in reviews:
        schema_validate("Review", review)
        if review["id"] in seen:
            raise BudgetError("Duplicate review ID")
        seen.add(review["id"])
        if review["subject_id"] not in subjects:
            raise BudgetError("Unknown review subject")
        name, subject = subjects[review["subject_id"]]
        expected_version = subject.get("source_version", subject.get("version", subject.get("mapping_version", subject.get("schema_version"))))
        if review["subject_sha256"] != digest(canonical(subject)) or review["subject_version"] != expected_version:
            raise BudgetError("Review is invalidated by changed data or mapping")
        try:
            datetime.fromisoformat(review["reviewed_at"].replace("Z", "+00:00"))
        except ValueError as error:
            raise BudgetError("Invalid review date") from error
        if require_publication and review["decision"] != "approved":
            raise BudgetError("Conflicting or withdrawn review blocks publication")
        if review["decision"] == "approved" and review["id"] not in invalidated:
            if re.search(r"^(fixture|test|placeholder|reviewer-\d+)", review["human_reviewer_id"], re.I):
                if require_publication:
                    raise BudgetError("Placeholder review cannot approve publication")
            approved[review["subject_id"]].add(review["role"])
    if require_publication:
        if payload["source.json"]["is_fixture"]:
            raise BudgetError("Fixture data cannot enter a public build")
        if payload["source.json"]["rights_status"] not in {"public_domain", "link_and_short_quote", "approved_derived_display"}:
            raise BudgetError("Source reuse rights are not approved")
        for key, (name, subject) in subjects.items():
            if subject["review_state"] != "approved" or approved[key] != {"financial", "rights", "editorial"}:
                raise BudgetError(f"Human financial, rights, and editorial review required for {key}")
        if any(topic["review_state"] != "approved" for topic in payload["mapping.json"]["mappings"]):
            raise BudgetError("Topic mapping review is pending")


def validate_payload(payload, taxonomy_path, require_publication=False):
    source, measurement, values = [payload[name] for name in ("source.json", "measurement.json", "values.json")]
    schema_validate("Source", source)
    schema_validate("Measurement", measurement)
    if measurement["source_ref"] != source["id"] or measurement["source_sha256"] != source["sha256"]:
        raise BudgetError("Mixed source/measurement versions")
    validate_values(values, source, measurement)
    sections = normalize_sections(payload["sections.json"], source, values)
    if sections != payload["sections.json"]:
        raise BudgetError("Noncanonical section dictionary")
    checked = normalize_mapping(payload["mapping.json"], source, values, taxonomy_path)
    if checked != payload["mapping.json"]:
        raise BudgetError("Noncanonical mapping")
    for kind, name in (("Correction", "corrections.json"), ("Decision", "decisions.json")):
        if not isinstance(payload[name], list):
            raise BudgetError(f"{name} must be an array")
        for item in payload[name]:
            schema_validate(kind, item)
    if not isinstance(payload["reviews.json"], list):
        raise BudgetError("Reviews must be an array")
    validate_reviews(payload["reviews.json"], payload, payload["corrections.json"], require_publication)


def import_bundle(source_path, contract_path, mapping_path, register_path, output_dir, build_date,
                  taxonomy_path=ROOT / "content/taxonomy.json", draft=False, reviews_path=None,
                  corrections_path=None, decisions_path=None, supersedes=None, sections_path=None):
    date.fromisoformat(build_date)
    if supersedes is not None and not HASH.fullmatch(supersedes):
        raise BudgetError("Invalid previous bundle ID")
    raw = bounded_read(source_path)
    register = load_json(register_path)
    source = normalize_source(register, raw)
    measurement = normalize_measurement(load_json(contract_path), source)
    values = normalize_values(raw, source)
    mapping = normalize_mapping(load_json(mapping_path), source, values, taxonomy_path)
    sections = normalize_sections(load_json(sections_path or Path(contract_path).parent / "section-dictionary.json"), source, values)
    payload = {"sections.json": sections, "source.json": source, "measurement.json": measurement, "values.json": values, "mapping.json": mapping,
               "reviews.json": load_json(reviews_path) if reviews_path else [],
               "corrections.json": load_json(corrections_path) if corrections_path else [],
               "decisions.json": load_json(decisions_path) if decisions_path else []}
    validate_payload(payload, taxonomy_path, require_publication=not draft)
    if not draft and source["review_state"] != "approved":
        raise BudgetError("Source is not approved")
    serialized = {name: canonical(value) for name, value in payload.items()}
    if sum(len(raw) for raw in serialized.values()) > MAX_BUNDLE_BYTES or any(len(raw) > MAX_BYTES for raw in serialized.values()):
        raise BudgetError("Normalized bundle exceeds size limits")
    manifest = {"schema_version": SCHEMA_VERSION, "dataset_version": source["source_version"], "budget_year": 2023,
                "accounting_basis": "approved_credits", "source_sha256": source["sha256"], "taxonomy_sha256": mapping["taxonomy_sha256"],
                "mapping_version": mapping["mapping_version"], "transform_version": SCHEMA_VERSION, "build_date": build_date,
                "publication_state": "draft" if draft else "reviewed", "is_fixture": source["is_fixture"],
                "files": [{"path": name, "bytes": len(raw), "sha256": digest(raw)} for name, raw in sorted(serialized.items())],
                "review_refs": [review["id"] for review in payload["reviews.json"]], "supersedes": supersedes,
                "correction_refs": [record["id"] for record in payload["corrections.json"]]}
    schema_validate("Manifest", manifest)
    serialized["manifest.json"] = canonical(manifest)
    bundle_id = digest(serialized["manifest.json"])
    output_dir = Path(output_dir)
    if draft:
        # Draft real data stays outside Git and all serving directories.
        resolved = output_dir.resolve()
        if resolved.is_relative_to(ROOT.resolve()):
            raise BudgetError("Draft budget bundles must stay outside the repository")
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = output_dir / bundle_id
    if target.exists():
        if target.is_symlink() or {p.name for p in target.iterdir()} != set(serialized) or any(bounded_read(target/name) != raw for name, raw in serialized.items()):
            raise BudgetError("Existing immutable bundle differs")
        return target
    with tempfile.TemporaryDirectory(prefix=".budget-", dir=output_dir) as temporary:
        staging = Path(temporary) / bundle_id
        staging.mkdir(mode=0o700)
        for name, raw in serialized.items():
            (staging/name).write_bytes(raw)
            (staging/name).chmod(0o600)
        staging.rename(target)
    return target


def load_bundle(path, taxonomy_path=ROOT / "content/taxonomy.json", require_publication=True):
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        raise BudgetError("Bundle must be a regular directory")
    manifest_raw = bounded_read(path / "manifest.json")
    manifest = load_json(path / "manifest.json")
    schema_validate("Manifest", manifest)
    if canonical(manifest) != manifest_raw or digest(manifest_raw) != path.name:
        raise BudgetError("Bundle identity mismatch")
    files = manifest["files"]
    if len(files) != len(FILES) or {entry["path"] for entry in files} != FILES:
        raise BudgetError("Unexpected bundle paths or missing files")
    if {entry.name for entry in path.iterdir()} != FILES | {"manifest.json"}:
        raise BudgetError("Unmanifested bundle files")
    if sum(entry["bytes"] for entry in files) > MAX_BUNDLE_BYTES:
        raise BudgetError("Bundle size limit exceeded")
    payload = {}
    for entry in files:
        raw = bounded_read(path / entry["path"])
        if len(raw) != entry["bytes"] or digest(raw) != entry["sha256"]:
            raise BudgetError(f"Bundle file hash mismatch: {entry['path']}")
        payload[entry["path"]] = load_json(path / entry["path"])
    source, mapping = payload["source.json"], payload["mapping.json"]
    if (manifest["source_sha256"] != source["sha256"] or manifest["dataset_version"] != source["source_version"] or
        manifest["taxonomy_sha256"] != mapping["taxonomy_sha256"] or manifest["mapping_version"] != mapping["mapping_version"] or
        manifest["is_fixture"] != source["is_fixture"] or manifest["review_refs"] != [r["id"] for r in payload["reviews.json"]] or
        manifest["correction_refs"] != [r["id"] for r in payload["corrections.json"]]):
        raise BudgetError("Manifest and payload versions differ")
    date.fromisoformat(manifest["build_date"])
    if require_publication and manifest["publication_state"] != "reviewed":
        raise BudgetError("Draft budget data cannot enter a public build")
    validate_payload(payload, taxonomy_path, require_publication)
    return manifest, payload


def copy_reviewed_bundle(bundle_path, destination, taxonomy_path=ROOT / "content/taxonomy.json"):
    load_bundle(bundle_path, taxonomy_path, require_publication=True)
    destination = Path(destination) / "static/budget" / Path(bundle_path).name
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundle_path, destination)
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import", help="Create a pinned offline budget bundle")
    for key in ("source", "contract", "mapping", "register", "output-dir"):
        importer.add_argument("--" + key, type=Path, required=True)
    importer.add_argument("--build-date", required=True)
    importer.add_argument("--draft", action="store_true", help="Private development only; publication still blocked")
    importer.add_argument("--reviews", type=Path)
    importer.add_argument("--corrections", type=Path)
    importer.add_argument("--decisions", type=Path)
    importer.add_argument("--supersedes")
    importer.add_argument("--sections", type=Path, help="Audited section dictionary (default: beside contract)")
    validator = commands.add_parser("validate", help="Validate integrity and public review gates")
    validator.add_argument("bundle", type=Path)
    validator.add_argument("--draft", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            result = import_bundle(args.source, args.contract, args.mapping, args.register, args.output_dir,
                                   args.build_date, draft=args.draft, reviews_path=args.reviews,
                                   corrections_path=args.corrections, decisions_path=args.decisions, supersedes=args.supersedes, sections_path=args.sections)
            print(result)
        else:
            manifest, _ = load_bundle(args.bundle, require_publication=not args.draft)
            print(f"Budget bundle valid ({manifest['publication_state']})")
        return 0
    except (BudgetError, ValueError, KeyError, OSError) as error:
        print(f"Budget error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
