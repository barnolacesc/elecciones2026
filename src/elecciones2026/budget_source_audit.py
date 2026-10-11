"""Offline E10.1 source audit; does not import or approve publication data."""
from __future__ import annotations

import argparse
import csv
import hashlib
from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin

MAX_BYTES = 4 * 1024 * 1024
NUMBER = re.compile(r"(?:0|[1-9]\d*|[1-9]\d{0,2}(?:\.\d{3})+),\d{2}\Z")


class SpanReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            if self.current is not None:
                raise ValueError("Nested spans are not supported by this audit")
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self.current is not None:
            self.values.append(" ".join("".join(self.current).split()))
            self.current = None


def number(text):
    if not NUMBER.fullmatch(text):
        raise ValueError(f"Invalid source number: {text!r}")
    return Decimal(text.replace(".", "").replace(",", "."))


def matrix(raw):
    rows = list(csv.reader(raw.decode("cp1252").splitlines(), delimiter=";"))
    if len(rows) < 10:
        raise ValueError("Incomplete source")
    if rows[3] != ["", "EJERCICIO PRESUPUESTARIO 2023", ""]:
        raise ValueError("Unexpected budget year")
    if "Capítulos 1 a 8 consolidado" not in rows[2][1]:
        raise ValueError("Unexpected chapters or consolidation")
    if rows[5] != ["", "(Miles de euros)", ""]:
        raise ValueError("Unexpected units")
    header = rows[7]
    if header[:2] != ["Clasif. por programas", "Explicación"] or header[-2:] != ["Total", ""]:
        raise ValueError("Unexpected header")
    sections = [re.fullmatch(r"Secc\. (\d{2})", value) for value in header[2:-2]]
    if not sections or not all(sections):
        raise ValueError("Invalid section code")
    section_codes = [match.group(1) for match in sections]
    if len(set(section_codes)) != len(section_codes):
        raise ValueError("Duplicate section code")
    data = [row for row in rows[8:] if any(row)]
    if any(len(row) != len(header) or row[-1] for row in data):
        raise ValueError("Unexpected row width or trailing field")
    total = data[-1]
    if total[:2] != ["", "TOTAL"]:
        raise ValueError("Missing final official total")
    policies = data[:-1]
    codes = [row[0] for row in policies]
    if not policies or any(not re.fullmatch(r"\d{2}", code) for code in codes):
        raise ValueError("Unexpected policy code")
    if len(set(codes)) != len(codes):
        raise ValueError("Duplicate policy code")
    return rows, header, policies, total, section_codes


def reconcile(raw_csv, raw_html):
    rows, header, policies, total, section_codes = matrix(raw_csv)
    reader = SpanReader()
    reader.feed(raw_html.decode("cp1252"))
    start = reader.values.index("Clasif. por programas")
    # The pinned HTML uses CSS table divs with one span for each matrix cell.
    expected = [[value.strip() for value in row[:-1]] for row in [header, *policies, total]]
    flattened = [value for row in expected for value in row]
    if reader.values[start:start + len(flattened)] != flattened:
        raise ValueError("HTML and CSV matrix differ")
    prefix = reader.values[:start]
    if not all(rows[index][1] in prefix for index in (0, 1, 2, 5)) or "2023" not in prefix:
        raise ValueError("HTML and CSV measurement headers differ")
    denominator = number(total[-2])
    policy_sum = sum((number(row[-2]) for row in policies), Decimal(0))
    section_sum = sum((number(value) for value in total[2:-2]), Decimal(0))
    if policy_sum != denominator or section_sum != denominator:
        raise ValueError("Official margin totals do not reconcile")
    blank_count = 0
    explicit_values = []
    for row in policies:
        present = [number(value) for value in row[2:-2] if value]
        blank_count += sum(not value for value in row[2:-2])
        explicit_values.extend(present)
        if sum(present, Decimal(0)) != number(row[-2]):
            raise ValueError(f"Policy margin mismatch: {row[0]}")
    for offset, code in enumerate(section_codes, 2):
        present_sum = sum((number(row[offset]) for row in policies if row[offset]), Decimal(0))
        if present_sum != number(total[offset]):
            raise ValueError(f"Section margin mismatch: {code}")
    return {
        "audit_version": "1.0.0",
        "publication_approved": False,
        "budget_year": 2023,
        "accounting_basis": "approved_credits",
        "unit": "thousand_eur",
        "denominator_amount_thousand_eur": str(denominator),
        "policy_count": len(policies),
        "section_count": len(section_codes),
        "explicit_numeric_cell_count": len(explicit_values),
        "blank_cell_count": blank_count,
        "explicit_zero_cell_count": sum(value == 0 for value in explicit_values),
        "html_csv_matrix_equal": True,
        "policy_margin_sum_thousand_eur": str(policy_sum),
        "section_margin_sum_thousand_eur": str(section_sum),
        "maximum_reconciliation_delta_thousand_eur": "0.00",
        "blank_convention": "unavailable_pending_human_review",
        "blank_note": "Sums of present cells match margins. This does not establish that individual blanks mean zero.",
        "source_sha256": {"csv": hashlib.sha256(raw_csv).hexdigest(), "html": hashlib.sha256(raw_html).hexdigest()},
    }


def read_pinned(archive, record):
    path = archive / record["sha256"] / record["file"]
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or unsafe archived source")
    raw = path.read_bytes()
    if len(raw) != record["byte_count"] or hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError("Archived source integrity mismatch")
    return raw



class SectionReader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.href = None
        self.text = []
        self.sections = {}

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        if self.href:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag != "a" or not self.href:
            return
        label = " ".join("".join(self.text).split())
        match = re.fullmatch(r"Sección (\d{2})\. (.+)", label)
        if match and (re.fullmatch(r"N_23_E_R_31_1\d\d_1.htm", self.href) or match[1] == "60"):
            code, name = match.groups()
            if code in self.sections and self.sections[code][0] != name:
                raise ValueError("Conflicting section dictionary labels")
            self.sections.setdefault(code, (name, self.href))
        self.href = None


def check_records(directory, register, raw_sources, report):
    """Check draft audit references against pinned sources, without approving them."""
    stored_report = json.loads((directory / "reconciliation.json").read_text())
    if stored_report != report:
        raise ValueError("Stored audit report differs from source reconciliation")
    measurement = json.loads((directory / "measurement.json").read_text())
    if measurement["denominator_amount_thousand_eur"] != report["denominator_amount_thousand_eur"]:
        raise ValueError("Measurement denominator differs")
    if measurement["source_sha256"] != report["source_sha256"]["csv"]:
        raise ValueError("Measurement source differs")
    if any(record.get("publication_approved") for record in (register, measurement, stored_report)):
        raise ValueError("This audit accepts draft records only")
    rows, _, policies, _, codes = matrix(raw_sources["matrix_csv"])
    by_code = {row[0]: row for row in policies}
    section_reader = SectionReader()
    section_reader.feed(raw_sources["section_dictionary_index"].decode("cp1252"))
    dictionary = json.loads((directory / "section-dictionary.json").read_text())
    sections = dictionary["sections"]
    if len(sections) != len(codes) or {row["code"] for row in sections} != set(codes):
        raise ValueError("Section dictionary coverage differs")
    index_url = next(record["url"] for record in register["sources"] if record["role"] == "section_dictionary_index")
    for section in sections:
        name, href = section_reader.sections[section["code"]]
        if section["name_es"] != name or section["source_url"] != urljoin(index_url, href):
            raise ValueError("Section dictionary locator or label differs")
        if section["is_ministry"] != name.startswith("MINISTERIO "):
            raise ValueError("Section ministry classification differs")
    mappings = json.loads((directory / "topic-mapping.json").read_text())
    taxonomy_raw = (Path(__file__).resolve().parents[2] / "content/taxonomy.json").read_bytes()
    topics = json.loads(taxonomy_raw)["topics"]
    if mappings["taxonomy_sha256"] != hashlib.sha256(taxonomy_raw).hexdigest():
        raise ValueError("Taxonomy hash differs")
    if len(mappings["mappings"]) != len(topics) or {row["topic_id"] for row in mappings["mappings"]} != {row["id"] for row in topics}:
        raise ValueError("Topic mapping coverage differs")
    used = {}
    for mapping in mappings["mappings"]:
        if mapping["aggregation_mode"] != "none" or mapping["topic_amount"] is not None:
            raise ValueError("Audit mapping contains allocated topic amounts")
        for ref in mapping["row_refs"]:
            code = ref["policy_code"]
            locator = ref["source_locator"]
            if rows[locator["csv_line"] - 1] != by_code[code] or locator["column"] != "Total":
                raise ValueError("Topic source locator differs")
            if ref["source_version"] != register["source_version"]:
                raise ValueError("Topic source version differs")
            used.setdefault(code, []).append(mapping["topic_id"])
    if mappings["unmapped_policy_codes"] != sorted(set(by_code) - set(used)):
        raise ValueError("Unmapped policy inventory differs")
    if mappings["overlapping_policy_references"] != {code: refs for code, refs in used.items() if len(refs) > 1}:
        raise ValueError("Overlapping policy inventory differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--register", type=Path, required=True)
    parser.add_argument("--check-records", action="store_true", help="Verify sibling draft audit records")
    args = parser.parse_args()
    register = json.loads(args.register.read_text())
    records = {record["role"]: record for record in register["sources"]}
    raw_sources = {role: read_pinned(args.archive, record) for role, record in records.items()}
    result = reconcile(raw_sources["matrix_csv"], raw_sources["matrix_html"])
    if args.check_records:
        check_records(args.register.parent, register, raw_sources, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
