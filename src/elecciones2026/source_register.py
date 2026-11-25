"""Versioned electoral programme source register schema and validation.

Tracks official candidacies, discovery paths, publication statuses,
cryptographic hashes, rights reviews, and replacement histories.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlsplit

SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

VALID_STATUSES = {
    "missing",
    "announced",
    "partial",
    "published-unverified",
    "verified",
    "replaced",
}

VALID_RIGHTS_STATUSES = {
    "not_reviewed",
    "link_only",
    "link_and_short_quote",
    "public_domain",
    "permission_denied",
}
RIGHTS_GRANT_STATUSES = {"link_only", "link_and_short_quote", "public_domain"}

VALID_ELECTION_STATUSES = {
    "active_monitoring",
    "pilot_rehearsal",
    "archived",
}


@dataclass(frozen=True)
class RightsReview:
    status: str
    reviewed_by: Optional[str]
    review_date: Optional[str]
    terms_notes: str
    evidence_ref: Optional[str] = None


@dataclass(frozen=True)
class ReplacementRecord:
    prior_version: str
    superseded_by: str
    replacement_date: str
    reason: str


@dataclass(frozen=True)
class SourceRecord:
    id: str
    election_id: str
    party_id: str
    candidature_name: str
    publisher: str
    scope: str
    official_url: str
    direct_url: Optional[str]
    filename: Optional[str]
    publication_date: Optional[str]
    retrieval_date: str
    language: Optional[str]
    version: str
    sha256: Optional[str]
    status: str
    rights_review: RightsReview
    replacement_history: list[ReplacementRecord]
    notes: str
    archived_url: Optional[str] = None


@dataclass(frozen=True)
class ElectionRecord:
    id: str
    name: str
    election_date: str
    call_decree: str
    status: str


@dataclass(frozen=True)
class SourceRegister:
    version: str
    last_updated: str
    description: str
    elections: list[ElectionRecord]
    sources: list[SourceRecord]


def _parse_rights_review(data: dict[str, Any], record_id: str) -> tuple[Optional[RightsReview], list[str]]:
    errors: list[str] = []
    status = data.get("status")
    if not status or status not in VALID_RIGHTS_STATUSES:
        errors.append(
            f"Record {record_id}: invalid rights_review status '{status}'. "
            f"Must be one of {sorted(VALID_RIGHTS_STATUSES)}."
        )

    review_date = data.get("review_date")
    if review_date and not DATE_PATTERN.match(review_date):
        errors.append(f"Record {record_id}: rights review date '{review_date}' must be YYYY-MM-DD.")

    terms_notes = data.get("terms_notes")
    if terms_notes is None or not isinstance(terms_notes, str):
        errors.append(f"Record {record_id}: rights_review terms_notes must be a string.")
    evidence_ref = data.get("evidence_ref")
    if evidence_ref is not None and (not isinstance(evidence_ref, str) or not evidence_ref.strip()):
        errors.append(f"Record {record_id}: rights_review evidence_ref must be a non-empty string when set.")

    if status in RIGHTS_GRANT_STATUSES:
        if not isinstance(data.get("reviewed_by"), str) or not data["reviewed_by"].strip():
            errors.append(f"Record {record_id}: rights grant requires a named reviewer.")
        if not review_date:
            errors.append(f"Record {record_id}: rights grant requires a review date.")
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            errors.append(f"Record {record_id}: rights grant requires a private evidence reference.")

    if errors:
        return None, errors

    return RightsReview(
        status=status,
        reviewed_by=data.get("reviewed_by"),
        review_date=review_date,
        terms_notes=terms_notes,
        evidence_ref=evidence_ref,
    ), []


def _parse_replacement(data: dict[str, Any], record_id: str) -> tuple[Optional[ReplacementRecord], list[str]]:
    errors: list[str] = []
    prior_version = data.get("prior_version")
    superseded_by = data.get("superseded_by")
    replacement_date = data.get("replacement_date")
    reason = data.get("reason")

    if not prior_version:
        errors.append(f"Record {record_id}: replacement record missing prior_version.")
    if not superseded_by:
        errors.append(f"Record {record_id}: replacement record missing superseded_by.")
    if not replacement_date or not DATE_PATTERN.match(replacement_date):
        errors.append(f"Record {record_id}: replacement date '{replacement_date}' must be YYYY-MM-DD.")
    if not reason:
        errors.append(f"Record {record_id}: replacement record missing reason.")

    if errors:
        return None, errors

    return ReplacementRecord(
        prior_version=prior_version,
        superseded_by=superseded_by,
        replacement_date=replacement_date,
        reason=reason,
    ), []


def load_register_from_dict(data: dict[str, Any]) -> tuple[Optional[SourceRegister], list[str]]:
    """Parse and validate a dictionary into a SourceRegister."""
    errors: list[str] = []

    version = data.get("version")
    if not version or not isinstance(version, str):
        errors.append("Missing or invalid register version.")

    last_updated = data.get("last_updated")
    if not last_updated:
        errors.append("Missing register last_updated timestamp.")

    description = data.get("description", "")

    elections_data = data.get("elections", [])
    if not elections_data or not isinstance(elections_data, list):
        errors.append("Register must define at least one election in 'elections'.")

    elections: list[ElectionRecord] = []
    election_ids: set[str] = set()
    for el in elections_data:
        el_id = el.get("id")
        if not el_id:
            errors.append("Election record missing 'id'.")
            continue
        if el_id in election_ids:
            errors.append(f"Duplicate election id: '{el_id}'.")
        election_ids.add(el_id)

        el_status = el.get("status")
        if el_status not in VALID_ELECTION_STATUSES:
            errors.append(
                f"Election {el_id}: invalid status '{el_status}'. "
                f"Must be one of {sorted(VALID_ELECTION_STATUSES)}."
            )

        elections.append(
            ElectionRecord(
                id=el_id,
                name=el.get("name", ""),
                election_date=el.get("election_date", ""),
                call_decree=el.get("call_decree", ""),
                status=el_status,
            )
        )

    sources_data = data.get("sources", [])
    if not isinstance(sources_data, list):
        errors.append("'sources' must be a list.")
        sources_data = []

    sources: list[SourceRecord] = []
    source_ids: set[str] = set()

    for item in sources_data:
        record_id = item.get("id", "unknown")
        if record_id in source_ids:
            errors.append(f"Duplicate source id '{record_id}'.")
        source_ids.add(record_id)

        election_id = item.get("election_id")
        if not election_id or election_id not in election_ids:
            errors.append(
                f"Record {record_id}: unknown or missing election_id '{election_id}'."
            )

        party_id = item.get("party_id")
        if not party_id:
            errors.append(f"Record {record_id}: missing party_id.")

        official_url = item.get("official_url")
        if not official_url or not official_url.startswith(("http://", "https://")):
            errors.append(f"Record {record_id}: missing or invalid official_url.")

        status = item.get("status")
        if not status or status not in VALID_STATUSES:
            errors.append(
                f"Record {record_id}: invalid status '{status}'. "
                f"Must be one of {sorted(VALID_STATUSES)}."
            )

        retrieval_date = item.get("retrieval_date")
        if not retrieval_date or not DATE_PATTERN.match(retrieval_date):
            errors.append(
                f"Record {record_id}: retrieval_date '{retrieval_date}' must be YYYY-MM-DD."
            )

        pub_date = item.get("publication_date")
        if pub_date and not DATE_PATTERN.match(pub_date):
            errors.append(
                f"Record {record_id}: publication_date '{pub_date}' must be YYYY-MM-DD."
            )

        sha256 = item.get("sha256")
        direct_url = item.get("direct_url")
        archived_url = item.get("archived_url")
        if archived_url is not None:
            try:
                parsed = urlsplit(archived_url)
                valid_archive_url = (
                    parsed.scheme == "https" and parsed.hostname and parsed.port in (None, 443)
                    and not (parsed.username or parsed.password or parsed.fragment)
                    and not any(ord(char) <= 32 or ord(char) == 127 or char == "\\" for char in archived_url)
                )
            except (TypeError, ValueError):
                valid_archive_url = False
            if not valid_archive_url or status != "verified":
                errors.append(f"Record {record_id}: archived_url requires a verified source and a safe HTTPS URL.")

        # The register schema constrains every supplied digest, not only
        # digests whose source has completed verification.
        if sha256 is not None and (
            not isinstance(sha256, str) or SHA256_PATTERN.fullmatch(sha256) is None
        ):
            errors.append(
                f"Record {record_id}: sha256 must be a 64-character lowercase hex digest when set."
            )

        # Invariant: verified records must have sha256 and direct_url
        if status == "verified":
            if sha256 is None:
                errors.append(
                    f"Record {record_id}: verified status requires a valid 64-character lowercase hex sha256 hash."
                )
            if not direct_url or not direct_url.startswith(("http://", "https://")):
                errors.append(
                    f"Record {record_id}: verified status requires a valid direct_url."
                )

        # Invariant: missing or announced must not invent hashes
        if status in ("missing", "announced"):
            if sha256 is not None:
                errors.append(
                    f"Record {record_id}: status '{status}' must not specify sha256 hash."
                )

        # Invariant: replaced status must have replacement history
        rep_history_data = item.get("replacement_history", [])
        if not isinstance(rep_history_data, list):
            errors.append(f"Record {record_id}: replacement_history must be a list.")
            rep_history_data = []

        if status == "replaced" and len(rep_history_data) == 0:
            errors.append(
                f"Record {record_id}: replaced status requires non-empty replacement_history."
            )

        replacement_records: list[ReplacementRecord] = []
        for rep in rep_history_data:
            rec, rep_errors = _parse_replacement(rep, record_id)
            if rep_errors:
                errors.extend(rep_errors)
            elif rec:
                replacement_records.append(rec)

        rights_data = item.get("rights_review", {})
        rights_review, rights_errors = _parse_rights_review(rights_data, record_id)
        if rights_errors:
            errors.extend(rights_errors)

        if not rights_review:
            rights_review = RightsReview(
                status="not_reviewed",
                reviewed_by=None,
                review_date=None,
                terms_notes="",
            )

        sources.append(
            SourceRecord(
                id=record_id,
                election_id=election_id or "",
                party_id=party_id or "",
                candidature_name=item.get("candidature_name", ""),
                publisher=item.get("publisher", ""),
                scope=item.get("scope", "general"),
                official_url=official_url or "",
                direct_url=direct_url,
                filename=item.get("filename"),
                publication_date=pub_date,
                retrieval_date=retrieval_date or "",
                language=item.get("language"),
                version=item.get("version", "0.0"),
                sha256=sha256,
                status=status or "missing",
                rights_review=rights_review,
                replacement_history=replacement_records,
                notes=item.get("notes", ""),
                archived_url=archived_url,
            )
        )

    if errors:
        return None, errors

    return (
        SourceRegister(
            version=version,
            last_updated=last_updated,
            description=description,
            elections=elections,
            sources=sources,
        ),
        [],
    )


def load_register(path: str | Path) -> SourceRegister:
    """Load and validate the source register from a JSON file.

    Raises ValueError with all validation errors if parsing fails.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Register file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    register, errors = load_register_from_dict(data)
    if errors:
        raise ValueError(f"Source register validation failed:\n" + "\n".join(f" - {e}" for e in errors))

    return register


def get_sources_for_election(register: SourceRegister, election_id: str) -> list[SourceRecord]:
    """Return sources belonging exclusively to the specified election ID."""
    return [s for s in register.sources if s.election_id == election_id]


def validate_file(path: str | Path) -> bool:
    """CLI helper to validate a file and print diagnostics."""
    try:
        reg = load_register(path)
        print(f"OK: Source register is valid. Version {reg.version}, {len(reg.sources)} sources across {len(reg.elections)} elections.")
        for el in reg.elections:
            el_sources = get_sources_for_election(reg, el.id)
            verified = sum(1 for s in el_sources if s.status == "verified")
            print(f"  Election '{el.id}': {len(el_sources)} sources ({verified} verified, {len(el_sources) - verified} pending/missing)")
        return True
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate election source register")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate source register JSON file")
    validate_parser.add_argument("path", help="Path to register.json")

    args = parser.parse_args()
    if args.command == "validate":
        success = validate_file(args.path)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
