"""Schema definitions, typed records, and validators for electoral data records.

Covers programme provenance, statement/claim positions, comparative relationships,
coverage tracking, and editorial corrections in accordance with docs/CONTENT-METHODOLOGY.md
and OpenSpec change mvp-programme-comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional

from elecciones2026.methodology import (
    CORE_TOPIC_IDS,
    ProgrammeRecord,
    ProgrammeStatus,
    load_programme,
)

ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_REVIEWER_PATTERN = re.compile(
    r"^(rev-(pilot|editorial)-\d+|reviewer-\d+|rev-\d+|r\d+|editorial-team|placeholder|fixture|test)(-|$)"
)
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")

VALID_PROGRAMME_STATUSES = {s.value for s in ProgrammeStatus}

VALID_STATEMENT_TYPES = {
    "explicit_proposal",
    "explicit_opposition",
    "qualification",
    "not_found",
}

VALID_STATEMENT_REVIEW_STATUSES = {
    "draft",
    "under_review",
    "approved",
    "rejected",
    "invalidated",
}

VALID_RELATIONSHIP_TYPES = {
    "agreement",
    "divergence",
    "partial_overlap",
    "single_party",
}

VALID_RELATIONSHIP_STATUSES = {
    "active",
    "invalidated",
}

VALID_CORRECTION_TYPES = {
    "factual_error",
    "topic_reclassification",
    "citation_update",
    "scope_amendment",
    "programme_replacement",
    "retraction",
}

VALID_TARGET_TYPES = {
    "statement",
    "programme",
    "relationship",
}

VALID_VERDICTS = {
    "approved",
    "rejected",
    "needs_changes",
}


@dataclass(frozen=True)
class ReviewRecord:
    reviewer_id: str
    review_date: Optional[str]
    verdict: str
    review_notes: str
    reviewer_kind: Optional[str] = None
    evidence_ref: Optional[str] = None
    reported_date: Optional[str] = None
    content_sha256: Optional[str] = None

    def validate(self, *, require_human: bool = False, fixture: bool = False) -> list[str]:
        errors: list[str] = []
        if not self.reviewer_id or not ID_PATTERN.match(self.reviewer_id):
            errors.append(f"Reviewer ID '{self.reviewer_id}' must be a valid lowercase kebab-case slug.")
        if self.review_date is None:
            if require_human and self.verdict == "approved":
                errors.append("Approval requires the actual review date; a report date is not a review date.")
        elif not DATE_PATTERN.match(self.review_date):
            errors.append(f"Review date '{self.review_date}' must follow YYYY-MM-DD.")
        else:
            try:
                reviewed = date.fromisoformat(self.review_date)
                if not fixture and reviewed > date.today():
                    errors.append("Review approval cannot be future-dated.")
            except ValueError:
                errors.append("Review date must be a valid calendar date.")
        if self.reported_date is not None:
            try:
                date.fromisoformat(self.reported_date)
            except (TypeError, ValueError):
                errors.append("Report date must be a valid calendar date.")
        if self.reviewer_kind not in (None, "human", "fixture", "automated"):
            errors.append("Reviewer kind must be human, fixture, or automated.")
        if self.evidence_ref is not None and not isinstance(self.evidence_ref, str):
            errors.append("Review evidence_ref must be a string.")
        if require_human and self.verdict == "approved":
            if self.reviewer_kind != "human" or not isinstance(self.evidence_ref, str) or not self.evidence_ref.strip():
                errors.append("Approval requires a human reviewer and a documented evidence_ref.")
            if PLACEHOLDER_REVIEWER_PATTERN.match(self.reviewer_id):
                errors.append("Placeholder reviewer IDs cannot approve political claims.")
        if self.verdict not in VALID_VERDICTS:
            errors.append(f"Verdict '{self.verdict}' must be one of {sorted(VALID_VERDICTS)}.")
        if not isinstance(self.review_notes, str):
            errors.append("Review notes must be a string.")
        return errors


@dataclass(frozen=True)
class StatementRecord:
    schema_version: str
    election_id: str
    id: str
    party_id: str
    topic_id: str
    subtopic_id: str
    statement_type: str
    summary: str
    review_status: str
    programme_id: Optional[str] = None
    summary_en: Optional[str] = None
    quote: Optional[str] = None
    source_url: Optional[str] = None
    source_version: Optional[str] = None
    source_page: Optional[str] = None
    source_section: Optional[str] = None
    qualifications: list[str] = field(default_factory=list)
    policy_instrument: Optional[str] = None
    reviews: list[ReviewRecord] = field(default_factory=list)
    last_reviewed_date: Optional[str] = None
    correction_id: Optional[str] = None
    is_fixture: bool = False

    def review_fingerprint(self) -> str:
        """Bind a decision to the exact claim, qualification and source locator."""
        fields = ("election_id", "id", "party_id", "programme_id", "topic_id", "subtopic_id",
                  "statement_type", "summary", "quote", "source_url", "source_version",
                  "source_page", "source_section", "qualifications", "policy_instrument")
        payload = {key: getattr(self, key) for key in fields}
        return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                         separators=(",", ":")).encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StatementRecord:
        reviews = [
            ReviewRecord(
                reviewer_id=r["reviewer_id"],
                review_date=r["review_date"],
                verdict=r["verdict"],
                review_notes=r.get("review_notes", ""),
                reviewer_kind=r.get("reviewer_kind"),
                evidence_ref=r.get("evidence_ref"),
                reported_date=r.get("reported_date"),
                content_sha256=r.get("content_sha256"),
            )
            for r in data.get("reviews", [])
        ]
        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            election_id=data.get("election_id", ""),
            id=data.get("id", ""),
            party_id=data.get("party_id", ""),
            programme_id=data.get("programme_id"),
            topic_id=data.get("topic_id", ""),
            subtopic_id=data.get("subtopic_id", ""),
            statement_type=data.get("statement_type", ""),
            summary=data.get("summary", ""),
            summary_en=data.get("summary_en"),
            quote=data.get("quote"),
            source_url=data.get("source_url"),
            source_version=data.get("source_version"),
            source_page=data.get("source_page"),
            source_section=data.get("source_section"),
            qualifications=list(data.get("qualifications", [])),
            policy_instrument=data.get("policy_instrument"),
            review_status=data.get("review_status", "draft"),
            reviews=reviews,
            last_reviewed_date=data.get("last_reviewed_date"),
            correction_id=data.get("correction_id"),
            is_fixture=data.get("is_fixture", False),
        )

    def validate(self, target_election_id: Optional[str] = None) -> list[str]:
        errors: list[str] = []

        if not SEMVER_PATTERN.match(self.schema_version):
            errors.append(f"Statement {self.id}: schema_version '{self.schema_version}' must be semantic versioning.")

        if not self.election_id or not ID_PATTERN.match(self.election_id):
            errors.append(f"Statement {self.id}: election_id '{self.election_id}' must be a lowercase slug.")

        if target_election_id and self.election_id != target_election_id:
            errors.append(
                f"Statement {self.id}: election mismatch: expected '{target_election_id}', found '{self.election_id}'."
            )

        if not self.id or not ID_PATTERN.match(self.id):
            errors.append(f"Statement ID '{self.id}' must be a valid lowercase kebab-case slug.")

        if not self.party_id or not ID_PATTERN.match(self.party_id):
            errors.append(f"Statement {self.id}: party_id '{self.party_id}' must be a valid slug.")

        if self.topic_id not in CORE_TOPIC_IDS:
            errors.append(
                f"Statement {self.id}: topic_id '{self.topic_id}' must be one of {CORE_TOPIC_IDS}."
            )

        if not self.subtopic_id or not ID_PATTERN.match(self.subtopic_id):
            errors.append(f"Statement {self.id}: subtopic_id '{self.subtopic_id}' must be a valid slug.")

        if self.statement_type not in VALID_STATEMENT_TYPES:
            errors.append(
                f"Statement {self.id}: statement_type '{self.statement_type}' must be one of {sorted(VALID_STATEMENT_TYPES)}."
            )

        if not self.summary or not self.summary.strip():
            errors.append(f"Statement {self.id}: summary cannot be empty.")

        if self.review_status not in VALID_STATEMENT_REVIEW_STATUSES:
            errors.append(
                f"Statement {self.id}: review_status '{self.review_status}' must be one of {sorted(VALID_STATEMENT_REVIEW_STATUSES)}."
            )

        # Reviews structural validation
        for r in self.reviews:
            if r.content_sha256 is not None and r.content_sha256 != self.review_fingerprint():
                errors.append(f"Statement {self.id}: review fingerprint does not match current content and provenance.")
            r_errors = r.validate(
                require_human=self.election_id == "es-gen-2023" and self.review_status == "approved",
                fixture=self.is_fixture and self.election_id != "es-gen-2023",
            )
            for re_err in r_errors:
                errors.append(f"Statement {self.id}: {re_err}")

        # Provenance and absence rules
        if self.statement_type == "not_found":
            if self.source_page is not None or self.source_section is not None:
                errors.append(
                    f"Statement {self.id}: not_found statement must not specify source_page or source_section coordinates."
                )
            if self.quote is not None:
                errors.append(f"Statement {self.id}: not_found statement must not include quote.")
            # Verify absence phrasing does not express opposition
            summary_lower = self.summary.lower()
            if any(term in summary_lower for term in ("se opone", "rechaza", "en contra", "combate")):
                errors.append(
                    f"Statement {self.id}: not_found statement must express absence of proposal, not opposition."
                )

        elif self.statement_type in ("explicit_proposal", "explicit_opposition"):
            if not self.source_url:
                errors.append(
                    f"Statement {self.id}: {self.statement_type} must specify source_url."
                )
            if not self.source_version:
                errors.append(
                    f"Statement {self.id}: {self.statement_type} must specify source_version."
                )
            if not self.source_page and not self.source_section:
                errors.append(
                    f"Statement {self.id}: {self.statement_type} must specify at least one of source_page or source_section."
                )

        # Quotation quantitative bounds and mandatory locators (TRLPI Art. 32)
        if self.quote is not None:
            clean_quote = self.quote.strip()
            if not clean_quote:
                errors.append(f"Statement {self.id}: quotation text cannot be empty or whitespace.")
            else:
                words = len(clean_quote.split())
                if words > 40:
                    errors.append(
                        f"Statement {self.id}: quotation exceeds maximum limit of 40 words (found {words} words)."
                    )
                chars = len(clean_quote)
                if chars > 300:
                    errors.append(
                        f"Statement {self.id}: quotation exceeds maximum limit of 300 characters (found {chars} characters)."
                    )
            if not self.source_page and not self.source_section:
                errors.append(
                    f"Statement {self.id}: quotation must specify at least one locator: source_page or source_section."
                )

        # Dual review requirement for approved status
        if self.review_status == "approved":
            if self.election_id == "es-gen-2023" and any(not r.content_sha256 for r in self.reviews):
                errors.append(f"Statement {self.id}: political pilot approval requires a review fingerprint for each reviewer.")
            if self.election_id == "es-gen-2023" and self.is_fixture:
                errors.append(f"Statement {self.id}: fixture approvals cannot publish political pilot claims.")
            approved_reviews = [r for r in self.reviews if r.verdict == "approved"]
            reviewer_ids = {r.reviewer_id for r in approved_reviews}
            if len(approved_reviews) < 2 or len(reviewer_ids) < 2:
                errors.append(
                    f"Statement {self.id}: approved review_status requires dual approval by at least two distinct reviewers (found {len(reviewer_ids)})."
                )
            if not self.last_reviewed_date or not DATE_PATTERN.match(self.last_reviewed_date):
                errors.append(
                    f"Statement {self.id}: approved statement must have last_reviewed_date in YYYY-MM-DD format."
                )
            else:
                try:
                    last_reviewed = date.fromisoformat(self.last_reviewed_date)
                    if (not self.is_fixture or self.election_id == "es-gen-2023") and last_reviewed > date.today():
                        errors.append(f"Statement {self.id}: last_reviewed_date cannot be future-dated.")
                    approved_dates = [r.review_date for r in approved_reviews if r.review_date]
                    if approved_dates and self.last_reviewed_date != max(approved_dates):
                        errors.append(f"Statement {self.id}: last_reviewed_date must match the latest approval.")
                except ValueError:
                    errors.append(f"Statement {self.id}: last_reviewed_date must be a valid calendar date.")

        return errors


@dataclass(frozen=True)
class RelationshipRecord:
    schema_version: str
    election_id: str
    id: str
    topic_id: str
    subtopic_id: str
    measure_label: str
    party_ids: list[str]
    statement_ids: list[str]
    relationship_type: str
    summary: str
    review_status: str
    status: str
    differences: list[str] = field(default_factory=list)
    reviews: list[ReviewRecord] = field(default_factory=list)
    invalidation_reason: Optional[str] = None
    invalidated_by_correction_id: Optional[str] = None
    is_fixture: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelationshipRecord:
        reviews = [
            ReviewRecord(
                reviewer_id=r["reviewer_id"],
                review_date=r["review_date"],
                verdict=r["verdict"],
                review_notes=r.get("review_notes", ""),
                reviewer_kind=r.get("reviewer_kind"),
                evidence_ref=r.get("evidence_ref"),
            )
            for r in data.get("reviews", [])
        ]
        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            election_id=data.get("election_id", ""),
            id=data.get("id", ""),
            topic_id=data.get("topic_id", ""),
            subtopic_id=data.get("subtopic_id", ""),
            measure_label=data.get("measure_label", ""),
            party_ids=list(data.get("party_ids", [])),
            statement_ids=list(data.get("statement_ids", [])),
            relationship_type=data.get("relationship_type", ""),
            summary=data.get("summary", ""),
            differences=list(data.get("differences", [])),
            review_status=data.get("review_status", "draft"),
            reviews=reviews,
            status=data.get("status", "active"),
            invalidation_reason=data.get("invalidation_reason"),
            invalidated_by_correction_id=data.get("invalidated_by_correction_id"),
            is_fixture=data.get("is_fixture", False),
        )

    def validate(
        self,
        target_election_id: Optional[str] = None,
        statements_by_id: Optional[dict[str, StatementRecord]] = None,
        for_build: bool = False,
    ) -> list[str]:
        errors: list[str] = []

        if not SEMVER_PATTERN.match(self.schema_version):
            errors.append(f"Relationship {self.id}: schema_version '{self.schema_version}' must be semantic versioning.")

        if not self.election_id or not ID_PATTERN.match(self.election_id):
            errors.append(f"Relationship {self.id}: election_id '{self.election_id}' must be a lowercase slug.")

        if target_election_id and self.election_id != target_election_id:
            errors.append(
                f"Relationship {self.id}: election mismatch: expected '{target_election_id}', found '{self.election_id}'."
            )

        if not self.id or not ID_PATTERN.match(self.id):
            errors.append(f"Relationship ID '{self.id}' must be a valid lowercase kebab-case slug.")

        if self.topic_id not in CORE_TOPIC_IDS:
            errors.append(
                f"Relationship {self.id}: topic_id '{self.topic_id}' must be one of {CORE_TOPIC_IDS}."
            )

        if not self.subtopic_id or not ID_PATTERN.match(self.subtopic_id):
            errors.append(f"Relationship {self.id}: subtopic_id '{self.subtopic_id}' must be a valid slug.")

        if not self.measure_label or not self.measure_label.strip():
            errors.append(f"Relationship {self.id}: measure_label cannot be empty.")

        if len(self.party_ids) != 2 or len(set(self.party_ids)) != 2:
            errors.append(
                f"Relationship {self.id}: party_ids must contain exactly 2 distinct party IDs (found {self.party_ids})."
            )

        if not self.statement_ids or len(self.statement_ids) > 2:
            errors.append(
                f"Relationship {self.id}: statement_ids must contain 1 or 2 statement IDs."
            )

        if self.relationship_type not in VALID_RELATIONSHIP_TYPES:
            errors.append(
                f"Relationship {self.id}: relationship_type '{self.relationship_type}' must be one of {sorted(VALID_RELATIONSHIP_TYPES)}."
            )

        if not self.summary or not self.summary.strip():
            errors.append(f"Relationship {self.id}: summary cannot be empty.")

        if self.review_status not in {"draft", "approved", "invalidated"}:
            errors.append(
                f"Relationship {self.id}: review_status '{self.review_status}' must be draft, approved, or invalidated."
            )

        if self.status not in VALID_RELATIONSHIP_STATUSES:
            errors.append(
                f"Relationship {self.id}: status '{self.status}' must be one of {sorted(VALID_RELATIONSHIP_STATUSES)}."
            )

        if self.status == "invalidated" and not self.invalidation_reason:
            errors.append(f"Relationship {self.id}: invalidated status requires invalidation_reason.")

        if for_build:
            if self.status == "invalidated":
                errors.append(
                    f"Relationship {self.id}: invalidated comparison cannot be published in build (reason: {self.invalidation_reason})."
                )
            if self.review_status != "approved":
                errors.append(
                    f"Relationship {self.id}: unreviewed comparison with review_status '{self.review_status}' cannot be published in build."
                )

        # Review structural validation
        for r in self.reviews:
            r_errors = r.validate(
                require_human=self.election_id == "es-gen-2023",
                fixture=self.is_fixture and self.election_id != "es-gen-2023",
            )
            for re_err in r_errors:
                errors.append(f"Relationship {self.id}: {re_err}")

        if self.review_status == "approved":
            if self.election_id == "es-gen-2023" and self.is_fixture:
                errors.append(f"Relationship {self.id}: fixture approvals cannot publish political pilot comparisons.")
            approved_reviews = [r for r in self.reviews if r.verdict == "approved"]
            reviewer_ids = {r.reviewer_id for r in approved_reviews}
            if len(approved_reviews) < 2 or len(reviewer_ids) < 2:
                errors.append(
                    f"Relationship {self.id}: approved review_status requires dual approval by at least two distinct reviewers."
                )

        # Referential statement validation if statements mapping provided
        if statements_by_id is not None:
            for s_id in self.statement_ids:
                stmt = statements_by_id.get(s_id)
                if not stmt:
                    errors.append(f"Relationship {self.id}: referenced statement '{s_id}' not found.")
                    continue

                # Cross-election isolation check (Task 1.4)
                if stmt.election_id != self.election_id:
                    errors.append(
                        f"Relationship {self.id}: cross-election error: relationship election '{self.election_id}' "
                        f"cannot reference statement '{s_id}' from election '{stmt.election_id}'."
                    )

                # Agreement constraint: cannot assert agreement with not_found statement
                if self.relationship_type == "agreement" and stmt.statement_type == "not_found":
                    errors.append(
                        f"Relationship {self.id}: agreement cannot be asserted with not_found statement '{s_id}'."
                    )

                if for_build:
                    if stmt.review_status == "invalidated":
                        errors.append(
                            f"Relationship {self.id}: cannot reference invalidated statement '{s_id}' in build."
                        )
                    elif stmt.review_status != "approved":
                        errors.append(
                            f"Relationship {self.id}: cannot reference unreviewed statement '{s_id}' (status '{stmt.review_status}') in build."
                        )

        return errors


@dataclass(frozen=True)
class CandidacyCoverageRecord:
    id: str
    election_id: str
    candidacy_id: str
    status: str
    banner_text_es: str
    has_verified_programme: bool
    programme_id: Optional[str] = None
    banner_text_en: Optional[str] = None
    topics_covered: list[str] = field(default_factory=list)
    topics_absent: list[str] = field(default_factory=list)
    total_statements: int = 0
    last_audit_date: str = ""
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CandidacyCoverageRecord:
        return cls(
            id=data.get("id", ""),
            election_id=data.get("election_id", ""),
            candidacy_id=data.get("candidacy_id", ""),
            programme_id=data.get("programme_id"),
            status=data.get("status", ""),
            banner_text_es=data.get("banner_text_es", ""),
            banner_text_en=data.get("banner_text_en"),
            has_verified_programme=data.get("has_verified_programme", False),
            topics_covered=list(data.get("topics_covered", [])),
            topics_absent=list(data.get("topics_absent", [])),
            total_statements=data.get("total_statements", 0),
            last_audit_date=data.get("last_audit_date", ""),
            notes=data.get("notes"),
        )

    def validate(self, target_election_id: Optional[str] = None) -> list[str]:
        errors: list[str] = []

        if not self.id or not ID_PATTERN.match(self.id):
            errors.append(f"Coverage record ID '{self.id}' must be a lowercase slug.")

        if not self.election_id or not ID_PATTERN.match(self.election_id):
            errors.append(f"Coverage record {self.id}: election_id '{self.election_id}' must be a lowercase slug.")

        if target_election_id and self.election_id != target_election_id:
            errors.append(
                f"Coverage record {self.id}: election mismatch: expected '{target_election_id}', found '{self.election_id}'."
            )

        if not self.candidacy_id or not ID_PATTERN.match(self.candidacy_id):
            errors.append(f"Coverage record {self.id}: candidacy_id '{self.candidacy_id}' must be a lowercase slug.")

        if self.status not in VALID_PROGRAMME_STATUSES:
            errors.append(
                f"Coverage record {self.id}: status '{self.status}' must be one of {sorted(VALID_PROGRAMME_STATUSES)}."
            )

        if not self.banner_text_es or not self.banner_text_es.strip():
            errors.append(f"Coverage record {self.id}: banner_text_es cannot be empty.")

        if not self.last_audit_date or not DATE_PATTERN.match(self.last_audit_date):
            errors.append(f"Coverage record {self.id}: last_audit_date '{self.last_audit_date}' must follow YYYY-MM-DD.")

        # Lifecycle state invariants
        if self.status == "missing":
            if self.has_verified_programme:
                errors.append(f"Coverage record {self.id}: missing status must have has_verified_programme=false.")
            if "Programa no disponible" not in self.banner_text_es:
                errors.append(
                    f"Coverage record {self.id}: missing status banner_text_es must contain 'Programa no disponible'."
                )
            if self.topics_covered:
                errors.append(f"Coverage record {self.id}: missing status must have empty topics_covered.")
            if self.total_statements != 0:
                errors.append(f"Coverage record {self.id}: missing status must have total_statements=0.")

        elif self.status == "partial":
            if self.has_verified_programme:
                errors.append(f"Coverage record {self.id}: partial status must have has_verified_programme=false.")
            if "Programa parcial" not in self.banner_text_es:
                errors.append(
                    f"Coverage record {self.id}: partial status banner_text_es must contain 'Programa parcial'."
                )

        elif self.status == "official":
            if not self.has_verified_programme:
                errors.append(f"Coverage record {self.id}: official status must have has_verified_programme=true.")

        # Topics consistency
        for t in self.topics_covered:
            if t not in CORE_TOPIC_IDS:
                errors.append(f"Coverage record {self.id}: invalid topic '{t}' in topics_covered.")
        for t in self.topics_absent:
            if t not in CORE_TOPIC_IDS:
                errors.append(f"Coverage record {self.id}: invalid topic '{t}' in topics_absent.")

        overlap = set(self.topics_covered).intersection(set(self.topics_absent))
        if overlap:
            errors.append(f"Coverage record {self.id}: topics {sorted(overlap)} cannot be both covered and absent.")

        return errors


@dataclass(frozen=True)
class ElectionCoverageSnapshot:
    schema_version: str
    election_id: str
    snapshot_id: str
    snapshot_date: str
    description: str
    candidacies: list[CandidacyCoverageRecord]
    is_fixture: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ElectionCoverageSnapshot:
        candidacies = [
            CandidacyCoverageRecord.from_dict(c)
            for c in data.get("candidacies", [])
        ]
        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            election_id=data.get("election_id", ""),
            snapshot_id=data.get("snapshot_id", ""),
            snapshot_date=data.get("snapshot_date", ""),
            description=data.get("description", ""),
            candidacies=candidacies,
            is_fixture=data.get("is_fixture", False),
        )

    def validate(self, target_election_id: Optional[str] = None) -> list[str]:
        errors: list[str] = []

        if not SEMVER_PATTERN.match(self.schema_version):
            errors.append(f"Snapshot {self.snapshot_id}: schema_version '{self.schema_version}' must be semver.")

        if not self.election_id or not ID_PATTERN.match(self.election_id):
            errors.append(f"Snapshot {self.snapshot_id}: election_id '{self.election_id}' must be a lowercase slug.")

        if target_election_id and self.election_id != target_election_id:
            errors.append(
                f"Snapshot {self.snapshot_id}: election mismatch: expected '{target_election_id}', found '{self.election_id}'."
            )

        if not self.snapshot_id or not ID_PATTERN.match(self.snapshot_id):
            errors.append(f"Snapshot ID '{self.snapshot_id}' must be a lowercase slug.")

        if not self.snapshot_date or not DATE_PATTERN.match(self.snapshot_date):
            errors.append(f"Snapshot {self.snapshot_id}: snapshot_date '{self.snapshot_date}' must follow YYYY-MM-DD.")

        if not self.candidacies:
            errors.append(f"Snapshot {self.snapshot_id}: must contain at least one candidacy coverage entry.")

        seen_cand_ids = set()
        for cand in self.candidacies:
            if cand.candidacy_id in seen_cand_ids:
                errors.append(f"Snapshot {self.snapshot_id}: duplicate candidacy '{cand.candidacy_id}'.")
            seen_cand_ids.add(cand.candidacy_id)

            cand_errors = cand.validate(target_election_id=self.election_id)
            for ce in cand_errors:
                errors.append(f"Snapshot {self.snapshot_id}: {ce}")

        return errors


@dataclass(frozen=True)
class CorrectionRecord:
    schema_version: str
    election_id: str
    id: str
    target_type: str
    target_id: str
    correction_type: str
    prior_state: dict[str, Any]
    corrected_state: dict[str, Any]
    reason: str
    correction_date: str
    reviewed_by: str
    approved_by: str
    reporter: Optional[str] = None
    invalidated_relationship_ids: list[str] = field(default_factory=list)
    is_fixture: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CorrectionRecord:
        return cls(
            schema_version=data.get("schema_version", "1.0.0"),
            election_id=data.get("election_id", ""),
            id=data.get("id", ""),
            target_type=data.get("target_type", ""),
            target_id=data.get("target_id", ""),
            correction_type=data.get("correction_type", ""),
            prior_state=dict(data.get("prior_state", {})),
            corrected_state=dict(data.get("corrected_state", {})),
            reason=data.get("reason", ""),
            correction_date=data.get("correction_date", ""),
            reporter=data.get("reporter"),
            reviewed_by=data.get("reviewed_by", ""),
            approved_by=data.get("approved_by", ""),
            invalidated_relationship_ids=list(data.get("invalidated_relationship_ids", [])),
            is_fixture=data.get("is_fixture", False),
        )

    def validate(self, target_election_id: Optional[str] = None) -> list[str]:
        errors: list[str] = []

        if not SEMVER_PATTERN.match(self.schema_version):
            errors.append(f"Correction {self.id}: schema_version '{self.schema_version}' must be semver.")

        if not self.election_id or not ID_PATTERN.match(self.election_id):
            errors.append(f"Correction {self.id}: election_id '{self.election_id}' must be a lowercase slug.")

        if target_election_id and self.election_id != target_election_id:
            errors.append(
                f"Correction {self.id}: election mismatch: expected '{target_election_id}', found '{self.election_id}'."
            )

        if not self.id or not ID_PATTERN.match(self.id):
            errors.append(f"Correction ID '{self.id}' must be a lowercase slug.")

        if self.target_type not in VALID_TARGET_TYPES:
            errors.append(
                f"Correction {self.id}: target_type '{self.target_type}' must be one of {sorted(VALID_TARGET_TYPES)}."
            )

        if not self.target_id or not ID_PATTERN.match(self.target_id):
            errors.append(f"Correction {self.id}: target_id '{self.target_id}' must be a lowercase slug.")

        if self.correction_type not in VALID_CORRECTION_TYPES:
            errors.append(
                f"Correction {self.id}: correction_type '{self.correction_type}' must be one of {sorted(VALID_CORRECTION_TYPES)}."
            )

        if not self.prior_state or not isinstance(self.prior_state, dict):
            errors.append(f"Correction {self.id}: prior_state must be a non-empty dictionary.")

        if not self.corrected_state or not isinstance(self.corrected_state, dict):
            errors.append(f"Correction {self.id}: corrected_state must be a non-empty dictionary.")

        if self.prior_state == self.corrected_state:
            errors.append(f"Correction {self.id}: prior_state and corrected_state must not be identical.")

        if not self.reason or len(self.reason.strip()) < 5:
            errors.append(f"Correction {self.id}: reason must be a detailed description (at least 5 characters).")

        if not self.correction_date or not DATE_PATTERN.match(self.correction_date):
            errors.append(f"Correction {self.id}: correction_date '{self.correction_date}' must follow YYYY-MM-DD.")

        # Dual human review gate for corrections
        if not self.reviewed_by or not ID_PATTERN.match(self.reviewed_by):
            errors.append(f"Correction {self.id}: reviewed_by must be a valid reviewer ID slug.")
        if not self.approved_by or not ID_PATTERN.match(self.approved_by):
            errors.append(f"Correction {self.id}: approved_by must be a valid reviewer ID slug.")
        if self.reviewed_by and self.approved_by and self.reviewed_by == self.approved_by:
            errors.append(
                f"Correction {self.id}: reviewed_by and approved_by must be distinct reviewers (found '{self.reviewed_by}')."
            )

        return errors


def invalidate_dependent_relationships(
    target_id: str,
    relationships: list[RelationshipRecord],
    reason: str,
    correction_id: Optional[str] = None,
) -> list[RelationshipRecord]:
    """Return a new list of relationship records with those referencing target_id marked invalidated."""
    updated: list[RelationshipRecord] = []
    for rel in relationships:
        if target_id in rel.statement_ids:
            updated.append(
                RelationshipRecord(
                    schema_version=rel.schema_version,
                    election_id=rel.election_id,
                    id=rel.id,
                    topic_id=rel.topic_id,
                    subtopic_id=rel.subtopic_id,
                    measure_label=rel.measure_label,
                    party_ids=rel.party_ids,
                    statement_ids=rel.statement_ids,
                    relationship_type=rel.relationship_type,
                    summary=rel.summary,
                    differences=rel.differences,
                    review_status="invalidated",
                    reviews=rel.reviews,
                    status="invalidated",
                    invalidation_reason=reason,
                    invalidated_by_correction_id=correction_id,
                    is_fixture=rel.is_fixture,
                )
            )
        else:
            updated.append(rel)
    return updated


def load_statement(path: Path | str) -> StatementRecord:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return StatementRecord.from_dict(data)


def load_relationship(path: Path | str) -> RelationshipRecord:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RelationshipRecord.from_dict(data)


def load_coverage_record(path: Path | str) -> CandidacyCoverageRecord:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return CandidacyCoverageRecord.from_dict(data)


def load_coverage_snapshot(path: Path | str) -> ElectionCoverageSnapshot:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ElectionCoverageSnapshot.from_dict(data)


def load_correction(path: Path | str) -> CorrectionRecord:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return CorrectionRecord.from_dict(data)


def validate_schema_document(schema_path: Path | str) -> list[str]:
    """Validate a JSON Schema draft 2020-12 file structure."""
    errors: list[str] = []
    path = Path(schema_path)
    if not path.exists():
        return [f"Schema file not found: {path}"]

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as err:
        return [f"Error decoding JSON schema {path}: {err}"]

    if "$schema" not in data or "2020-12" not in data["$schema"]:
        errors.append(f"{path.name}: must specify JSON Schema Draft 2020-12 in $schema.")
    if "$id" not in data or not data["$id"].startswith("https://"):
        errors.append(f"{path.name}: must specify canonical https $id URI.")
    if "title" not in data or not data["title"]:
        errors.append(f"{path.name}: must specify title.")
    if "type" not in data or data["type"] != "object":
        errors.append(f"{path.name}: top-level type must be 'object'.")
    if "properties" not in data or not isinstance(data["properties"], dict):
        errors.append(f"{path.name}: must declare properties object.")
    if "required" not in data or not isinstance(data["required"], list):
        errors.append(f"{path.name}: must declare required properties list.")

    return errors


def validate_any_record(path: Path | str, target_election_id: Optional[str] = None) -> list[str]:
    """Detect the record type and validate against the corresponding schema and business rules."""
    p = Path(path)
    if not p.exists():
        return [f"File not found: {p}"]

    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as err:
        return [f"Failed to read/decode JSON from {p}: {err}"]

    # Detection logic based on fields
    if "snapshot_id" in data and "candidacies" in data:
        snap = ElectionCoverageSnapshot.from_dict(data)
        return snap.validate(target_election_id=target_election_id)

    elif "has_verified_programme" in data and "topics_covered" in data:
        cov = CandidacyCoverageRecord.from_dict(data)
        return cov.validate(target_election_id=target_election_id)

    elif "target_type" in data and "prior_state" in data and "corrected_state" in data:
        corr = CorrectionRecord.from_dict(data)
        return corr.validate(target_election_id=target_election_id)

    elif "measure_label" in data and "party_ids" in data:
        rel = RelationshipRecord.from_dict(data)
        return rel.validate(target_election_id=target_election_id)

    elif "statement_type" in data and "summary" in data:
        stmt = StatementRecord.from_dict(data)
        return stmt.validate(target_election_id=target_election_id)

    elif "programme_id" in data and "candidacy_id" in data and "status" in data:
        prog = ProgrammeRecord.from_dict(data)
        t_id = target_election_id or data.get("election_id", "es-gen-2026")
        return prog.validate(target_election_id=t_id)

    else:
        return [f"Unknown or unrecognized record format in {p.name}"]


def validate_all_content(root_dir: Path) -> tuple[int, int, list[str]]:
    """Validate all schemas and example fixtures under content/. Returns (passed, failed, errors)."""
    passed = 0
    failed = 0
    all_errors: list[str] = []

    content_dir = root_dir / "content"
    schemas_dir = content_dir / "schemas"

    # 1. Validate schemas
    for schema_file in sorted(schemas_dir.glob("*.schema.json")):
        errs = validate_schema_document(schema_file)
        if errs:
            failed += 1
            all_errors.extend(errs)
        else:
            passed += 1

    # 2. Validate valid examples
    examples_dir = content_dir / "examples"
    for sub in ("programmes", "statements", "relationships", "coverage", "corrections"):
        sub_dir = examples_dir / sub
        if not sub_dir.exists():
            continue
        for fixture_file in sorted(sub_dir.glob("*.json")):
            errs = validate_any_record(fixture_file)
            if errs:
                failed += 1
                all_errors.append(f"Valid fixture {fixture_file.name} failed validation:\n" + "\n".join(f"  - {e}" for e in errs))
            else:
                passed += 1

    # 3. Validate invalid examples (must fail validation)
    invalid_dir = examples_dir / "invalid"
    if invalid_dir.exists():
        for inv_file in sorted(invalid_dir.glob("*.json")):
            # for cross-election relationship, test with statement context
            statements_ctx = {}
            # load sample statements for relational checks if needed
            for stmt_file in (examples_dir / "statements").glob("*.json"):
                s = load_statement(stmt_file)
                statements_ctx[s.id] = s

            with inv_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if "measure_label" in data and "party_ids" in data:
                rel = RelationshipRecord.from_dict(data)
                errs = rel.validate(statements_by_id=statements_ctx)
            else:
                errs = validate_any_record(inv_file)

            if not errs:
                failed += 1
                all_errors.append(f"Invalid fixture {inv_file.name} unexpectedly passed validation!")
            else:
                passed += 1

    return passed, failed, all_errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate content schemas and record fixtures")
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser("validate", help="Validate a record JSON file")
    validate_parser.add_argument("path", help="Path to JSON file")
    validate_parser.add_argument("--election-id", help="Expected election ID", default=None)

    validate_all_parser = subparsers.add_parser("validate-all", help="Validate all schemas and fixtures")
    validate_all_parser.add_argument("--root", help="Root directory of repository", default=None)

    args = parser.parse_args()

    if args.command == "validate":
        errs = validate_any_record(args.path, target_election_id=args.election_id)
        if errs:
            print(f"Validation FAILED for {args.path}:", file=sys.stderr)
            for e in errs:
                print(f" - {e}", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"OK: {args.path} passed schema and business rule validation.")
            sys.exit(0)

    elif args.command == "validate-all":
        root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent.parent
        passed, failed, errs = validate_all_content(root)
        print(f"Schema and Fixture Validation Report:")
        print(f"  Passed checks: {passed}")
        print(f"  Failed checks: {failed}")
        if errs:
            print("\nErrors encountered:", file=sys.stderr)
            for e in errs:
                print(f" - {e}", file=sys.stderr)
            sys.exit(1)
        else:
            print("OK: All schemas and fixtures valid.")
            sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
