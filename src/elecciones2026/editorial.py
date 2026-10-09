"""Editorial policy rules, quotation limits, reviewer roles, and correction processes.

Implements the editorial governance model defined in docs/CONTENT-METHODOLOGY.md
and ADR-0002 in docs/DECISION-RECORD.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from elecciones2026.methodology import (
    CORE_TOPIC_IDS,
    PartyRecord,
    ProgrammeRecord,
    ProgrammeStatus,
    Taxonomy,
    load_parties,
    load_programme,
    load_taxonomy,
)
from elecciones2026.source_register import SourceRecord, SourceRegister, load_register
from elecciones2026.schemas import (
    CorrectionRecord as SchemaCorrectionRecord,
    RelationshipRecord as SchemaRelationshipRecord,
    StatementRecord as SchemaStatementRecord,
    load_correction as load_schema_correction,
    load_relationship as load_schema_relationship,
    load_statement as load_schema_statement,
)

DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Quantitative quotation limits under Spanish Intellectual Property Law (TRLPI Art. 32)
MAX_QUOTE_WORDS = 40
MAX_QUOTE_CHARS = 300

# Rights statuses that permit verbatim quotation on the platform
PERMITTED_QUOTE_RIGHTS = {"link_and_short_quote", "public_domain"}

# Disallowing rights statuses
RESTRICTED_QUOTE_RIGHTS = {"link_only", "permission_denied", "not_reviewed"}


class ReviewerRole(str, Enum):
    """Reviewer roles in the editorial workflow."""

    DRAFTER = "drafter"
    REVIEWER_1 = "reviewer_1"  # Factual and citation auditor
    REVIEWER_2 = "reviewer_2"  # Neutrality and balance auditor
    LEAD_EDITOR = "lead_editor"  # Dispute resolver and release gatekeeper


class StatementStatus(str, Enum):
    """Publication lifecycle states for a policy statement."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    PUBLISHED = "published"
    INVALIDATED = "invalidated"


class CorrectionType(str, Enum):
    """Categories of editorial corrections."""

    FACTUAL_ERROR = "factual_error"
    CLASSIFICATION_ERROR = "classification_error"
    SOURCE_REPLACEMENT = "source_replacement"


class CorrectionSeverity(str, Enum):
    """Operational severity levels and SLA triage targets."""

    CRITICAL = "critical"  # Sev-1: Triage <= 4h, resolution <= 12h
    MAJOR = "major"  # Sev-2: Triage <= 12h, resolution <= 24h
    MINOR = "minor"  # Sev-3: Triage <= 24h, resolution <= 48h


@dataclass(frozen=True)
class QuoteRecord:
    """Verbatim excerpt extracted from an official electoral source."""

    text: str
    source_id: str
    page: Optional[str] = None
    section: Optional[str] = None

    def word_count(self) -> int:
        return len(self.text.strip().split())

    def validate(self) -> list[str]:
        """Validate quotation text and locators against statutory limits."""
        errors: list[str] = []
        clean_text = self.text.strip()
        if not clean_text:
            errors.append("Quotation text cannot be empty.")
            return errors

        words = self.word_count()
        if words > MAX_QUOTE_WORDS:
            errors.append(
                f"Quotation exceeds maximum limit of {MAX_QUOTE_WORDS} words (found {words} words)."
            )

        chars = len(clean_text)
        if chars > MAX_QUOTE_CHARS:
            errors.append(
                f"Quotation exceeds maximum limit of {MAX_QUOTE_CHARS} characters (found {chars} characters)."
            )

        if not self.source_id or not self.source_id.strip():
            errors.append("Quotation must reference a valid source_id.")

        if not (self.page and self.page.strip()) and not (self.section and self.section.strip()):
            errors.append(
                "Quotation must specify at least one locator: non-empty page or section."
            )

        return errors


@dataclass(frozen=True)
class ReviewRecord:
    """Audit record capturing independent dual review."""

    reviewed_by_1: str
    reviewed_by_2: str
    review_date_1: str
    review_date_2: str
    drafter: Optional[str] = None
    lead_editor_signoff: Optional[str] = None

    def validate(self) -> list[str]:
        """Validate dual-review integrity and role segregation."""
        errors: list[str] = []

        if not self.reviewed_by_1 or not self.reviewed_by_1.strip():
            errors.append("Primary reviewer (reviewed_by_1) is required.")
        if not self.reviewed_by_2 or not self.reviewed_by_2.strip():
            errors.append("Secondary reviewer (reviewed_by_2) is required.")

        # Four-eyes principle: reviewers must be distinct individuals
        if (
            self.reviewed_by_1
            and self.reviewed_by_2
            and self.reviewed_by_1.strip().lower() == self.reviewed_by_2.strip().lower()
        ):
            errors.append(
                f"Four-eyes principle violation: primary and secondary reviewers must be distinct "
                f"individuals, got '{self.reviewed_by_1}' for both."
            )

        # Segregation of duties: drafter cannot serve as secondary reviewer
        if (
            self.drafter
            and self.reviewed_by_2
            and self.drafter.strip().lower() == self.reviewed_by_2.strip().lower()
        ):
            errors.append(
                f"Segregation of duties violation: drafter '{self.drafter}' cannot serve as "
                f"secondary reviewer (reviewed_by_2)."
            )

        if not DATE_PATTERN.match(self.review_date_1):
            errors.append(
                f"Primary review date '{self.review_date_1}' must be in YYYY-MM-DD format."
            )
        if not DATE_PATTERN.match(self.review_date_2):
            errors.append(
                f"Secondary review date '{self.review_date_2}' must be in YYYY-MM-DD format."
            )

        return errors


@dataclass(frozen=True)
class StatementRecord:
    """Editorial policy statement representing a party position on a specific topic."""

    id: str
    election_id: str
    party_id: str
    topic_id: str
    subtopic_id: str
    summary_es: str
    source_id: str
    source_version: str
    status: StatementStatus
    review: Optional[ReviewRecord] = None
    quote: Optional[QuoteRecord] = None
    qualification_es: Optional[str] = None
    superseded_by: Optional[str] = None

    def validate(
        self,
        source_register: Optional[SourceRegister] = None,
        taxonomy: Optional[Taxonomy] = None,
    ) -> list[str]:
        """Validate statement completeness, dual review, and quotation rights."""
        errors: list[str] = []

        if not self.id or not self.id.strip():
            errors.append("Statement missing id.")
        if not self.election_id or not self.election_id.strip():
            errors.append("Statement missing election_id.")
        if not self.party_id or not self.party_id.strip():
            errors.append("Statement missing party_id.")
        if not self.summary_es or not self.summary_es.strip():
            errors.append("Statement missing summary_es.")
        if not self.source_id or not self.source_id.strip():
            errors.append("Statement missing source_id.")
        if not self.source_version or not self.source_version.strip():
            errors.append("Statement missing source_version.")

        # Taxonomy checks
        if taxonomy:
            topic_ids = [t.id for t in taxonomy.topics]
            if self.topic_id not in topic_ids:
                errors.append(f"Statement topic_id '{self.topic_id}' not found in taxonomy.")
            else:
                topic = next(t for t in taxonomy.topics if t.id == self.topic_id)
                subtopic_ids = [st.id for st in topic.subtopics]
                if self.subtopic_id not in subtopic_ids:
                    errors.append(
                        f"Statement subtopic_id '{self.subtopic_id}' not found under topic '{self.topic_id}'."
                    )
        elif self.topic_id not in CORE_TOPIC_IDS:
            errors.append(f"Statement topic_id '{self.topic_id}' is not one of the core 8 topics.")

        # Review requirement for reviewed and published statements
        if self.status in (StatementStatus.REVIEWED, StatementStatus.PUBLISHED):
            if not self.review:
                errors.append(
                    f"Statement '{self.id}' with status '{self.status.value}' requires a completed ReviewRecord."
                )
            else:
                review_errors = self.review.validate()
                errors.extend(f"Statement '{self.id}': {e}" for e in review_errors)

        # Quotation limits and rights checks
        if self.quote is not None:
            quote_errors = self.quote.validate()
            errors.extend(f"Statement '{self.id}' quote error: {e}" for e in quote_errors)

            if self.quote.source_id != self.source_id:
                errors.append(
                    f"Statement '{self.id}': quote source_id '{self.quote.source_id}' does not match "
                    f"statement source_id '{self.source_id}'."
                )

            # A published or reviewed quote MUST have dual review recorded
            if self.status in (StatementStatus.REVIEWED, StatementStatus.PUBLISHED) and not self.review:
                errors.append(
                    f"Statement '{self.id}': quotation cannot pass review without recorded dual review."
                )

            # Validate against source register if provided
            if source_register:
                source = next((s for s in source_register.sources if s.id == self.source_id), None)
                if not source:
                    errors.append(
                        f"Statement '{self.id}': quotation references source '{self.source_id}' which does not exist in source register."
                    )
                else:
                    # Enforce election isolation
                    if source.election_id != self.election_id:
                        errors.append(
                            f"Statement '{self.id}': quotation source election '{source.election_id}' does not match "
                            f"statement election '{self.election_id}'."
                        )

                    # Source must be verified
                    if source.status != "verified":
                        errors.append(
                            f"Statement '{self.id}': unsupported quote cannot pass review because source "
                            f"'{self.source_id}' status is '{source.status}' (must be 'verified')."
                        )

                    # Source rights must permit quotation
                    rights_status = source.rights_review.status
                    if rights_status not in PERMITTED_QUOTE_RIGHTS:
                        errors.append(
                            f"Statement '{self.id}': unsupported quote cannot pass review because source rights "
                            f"status '{rights_status}' does not allow quotation (requires 'link_and_short_quote' or 'public_domain')."
                        )

        return errors


@dataclass(frozen=True)
class CorrectionRecord:
    """Immutable audit record documenting a factual or classification correction."""

    id: str
    statement_id: str
    election_id: str
    date: str
    correction_type: CorrectionType
    severity: CorrectionSeverity
    prior_value: str
    new_value: str
    reason: str
    reviewed_by: str
    approved_by: str

    def validate(self) -> list[str]:
        """Validate correction record integrity."""
        errors: list[str] = []
        if not self.id or not self.id.strip():
            errors.append("Correction record missing id.")
        if not self.statement_id or not self.statement_id.strip():
            errors.append("Correction record missing statement_id.")
        if not self.election_id or not self.election_id.strip():
            errors.append("Correction record missing election_id.")
        if not DATE_PATTERN.match(self.date):
            errors.append(f"Correction date '{self.date}' must be in YYYY-MM-DD format.")
        if not self.prior_value or not self.prior_value.strip():
            errors.append("Correction record missing prior_value.")
        if not self.new_value or not self.new_value.strip():
            errors.append("Correction record missing new_value.")
        if not self.reason or not self.reason.strip():
            errors.append("Correction record missing reason.")
        if not self.reviewed_by or not self.reviewed_by.strip():
            errors.append("Correction record missing reviewed_by.")
        if not self.approved_by or not self.approved_by.strip():
            errors.append("Correction record missing approved_by (Lead Editor signoff).")
        return errors


@dataclass(frozen=True)
class ComparisonRelationship:
    """Comparative relationship between parties on a specific proposal or subtopic."""

    id: str
    election_id: str
    topic_id: str
    party_ids: list[str]
    statement_ids: list[str]
    relationship_type: str  # agreement, divergence, qualification, distinct_focus
    description_es: str
    status: str = "reviewed"  # reviewed, published, invalidated
    invalidation_reason: Optional[str] = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id:
            errors.append("ComparisonRelationship missing id.")
        if not self.election_id:
            errors.append("ComparisonRelationship missing election_id.")
        if len(self.party_ids) != 2:
            errors.append(
                f"ComparisonRelationship '{self.id}' must compare exactly 2 parties, got {len(self.party_ids)}."
            )
        if len(self.statement_ids) < 1:
            errors.append(f"ComparisonRelationship '{self.id}' must reference at least 1 statement.")
        if self.status not in ("reviewed", "published", "invalidated"):
            errors.append(f"ComparisonRelationship '{self.id}' invalid status '{self.status}'.")
        if self.status == "invalidated" and not self.invalidation_reason:
            errors.append(
                f"ComparisonRelationship '{self.id}' marked invalidated must specify invalidation_reason."
            )
        return errors


def validate_quote_limits(
    text: str,
    page: Optional[str] = None,
    section: Optional[str] = None,
) -> list[str]:
    """Validate quotation bounds and locators under Spanish Intellectual Property Law (TRLPI Art. 32)."""
    errors: list[str] = []
    clean = text.strip() if text else ""
    if not clean:
        errors.append("Quotation text cannot be empty.")
        return errors
    words = len(clean.split())
    if words > MAX_QUOTE_WORDS:
        errors.append(
            f"Quotation exceeds maximum limit of {MAX_QUOTE_WORDS} words (found {words} words)."
        )
    chars = len(clean)
    if chars > MAX_QUOTE_CHARS:
        errors.append(
            f"Quotation exceeds maximum limit of {MAX_QUOTE_CHARS} characters (found {chars} characters)."
        )
    if not (page and str(page).strip()) and not (section and str(section).strip()):
        errors.append(
            "Quotation must specify at least one locator: non-empty page or section."
        )
    return errors


def invalidate_dependent_relationships(
    relationships: Optional[list[Any]] = None,
    corrected_statement_id: Optional[str] = None,
    reason: str = "",
    target_id: Optional[str] = None,
    correction_id: Optional[str] = None,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Invalidate all comparison relationships that depend on a corrected statement.

    Supports both:
    - (relationships, corrected_statement_id, reason) -> tuple[list, list[str]]
    - (target_id, relationships, reason, correction_id=None) -> list[RelationshipRecord]
    """
    called_schemas_style = False
    if "target_id" in kwargs:
        called_schemas_style = True

    eff_target_id = kwargs.get("target_id") or target_id or kwargs.get("corrected_statement_id") or corrected_statement_id
    eff_relationships = kwargs.get("relationships") if "relationships" in kwargs else relationships
    eff_reason = kwargs.get("reason", reason)
    eff_corr_id = kwargs.get("correction_id", correction_id)

    if eff_relationships is None and len(args) > 0:
        eff_relationships = args[0]
    if eff_target_id is None and len(args) > 1:
        eff_target_id = args[1]

    if isinstance(eff_relationships, str) and isinstance(eff_target_id, (list, tuple)):
        eff_target_id, eff_relationships = eff_relationships, list(eff_target_id)
        called_schemas_style = True

    if not eff_relationships:
        eff_relationships = []
    if not eff_target_id:
        eff_target_id = ""

    updated: list[Any] = []
    invalidated_ids: list[str] = []

    for rel in eff_relationships:
        stmt_ids = getattr(rel, "statement_ids", [])
        if eff_target_id in stmt_ids:
            inv_reason = f"Dependent on corrected statement '{eff_target_id}': {eff_reason}"
            if isinstance(rel, ComparisonRelationship):
                new_rel = ComparisonRelationship(
                    id=rel.id,
                    election_id=rel.election_id,
                    topic_id=rel.topic_id,
                    party_ids=list(rel.party_ids),
                    statement_ids=list(rel.statement_ids),
                    relationship_type=rel.relationship_type,
                    description_es=rel.description_es,
                    status="invalidated",
                    invalidation_reason=inv_reason,
                )
            elif isinstance(rel, SchemaRelationshipRecord):
                new_rel = SchemaRelationshipRecord(
                    schema_version=rel.schema_version,
                    election_id=rel.election_id,
                    id=rel.id,
                    topic_id=rel.topic_id,
                    subtopic_id=rel.subtopic_id,
                    measure_label=rel.measure_label,
                    party_ids=list(rel.party_ids),
                    statement_ids=list(rel.statement_ids),
                    relationship_type=rel.relationship_type,
                    summary=rel.summary,
                    differences=list(rel.differences),
                    review_status="invalidated",
                    reviews=list(rel.reviews),
                    status="invalidated",
                    invalidation_reason=inv_reason,
                    invalidated_by_correction_id=eff_corr_id,
                    is_fixture=rel.is_fixture,
                )
            else:
                new_rel = rel
            updated.append(new_rel)
            invalidated_ids.append(getattr(rel, "id", ""))
        else:
            updated.append(rel)

    if called_schemas_style:
        return updated
    return updated, invalidated_ids


def apply_correction_and_invalidate(
    correction: Any,
    statements: list[Any],
    relationships: list[Any],
) -> tuple[list[Any], list[Any], list[str]]:
    """Apply a CorrectionRecord to target statement and invalidate dependent comparison relationships."""
    target_id = getattr(correction, "target_id", None) or getattr(correction, "statement_id", None)
    corr_id = getattr(correction, "id", "corr-unknown")
    reason = getattr(correction, "reason", "Editorial correction")

    updated_statements: list[Any] = []
    for stmt in statements:
        if getattr(stmt, "id", None) == target_id:
            if isinstance(stmt, SchemaStatementRecord):
                corr_dict = getattr(correction, "corrected_state", {})
                new_kwargs = {
                    "schema_version": stmt.schema_version,
                    "election_id": stmt.election_id,
                    "id": stmt.id,
                    "party_id": stmt.party_id,
                    "programme_id": stmt.programme_id,
                    "topic_id": corr_dict.get("topic_id", stmt.topic_id),
                    "subtopic_id": corr_dict.get("subtopic_id", stmt.subtopic_id),
                    "statement_type": corr_dict.get("statement_type", stmt.statement_type),
                    "summary": corr_dict.get("summary", stmt.summary),
                    "summary_en": corr_dict.get("summary_en", stmt.summary_en),
                    "quote": corr_dict.get("quote", stmt.quote),
                    "source_url": corr_dict.get("source_url", stmt.source_url),
                    "source_version": corr_dict.get("source_version", stmt.source_version),
                    "source_page": corr_dict.get("source_page", stmt.source_page),
                    "source_section": corr_dict.get("source_section", stmt.source_section),
                    "qualifications": list(corr_dict.get("qualifications", stmt.qualifications)),
                    "policy_instrument": corr_dict.get("policy_instrument", stmt.policy_instrument),
                    "review_status": stmt.review_status,
                    "reviews": list(stmt.reviews),
                    "last_reviewed_date": getattr(correction, "correction_date", stmt.last_reviewed_date),
                    "correction_id": corr_id,
                    "is_fixture": stmt.is_fixture,
                }
                updated_statements.append(SchemaStatementRecord(**new_kwargs))
            elif isinstance(stmt, StatementRecord):
                new_stmt = StatementRecord(
                    id=stmt.id,
                    election_id=stmt.election_id,
                    party_id=stmt.party_id,
                    topic_id=stmt.topic_id,
                    subtopic_id=stmt.subtopic_id,
                    summary_es=stmt.summary_es,
                    source_id=stmt.source_id,
                    source_version=stmt.source_version,
                    status=StatementStatus.INVALIDATED,
                    review=stmt.review,
                    quote=stmt.quote,
                    qualification_es=stmt.qualification_es,
                    superseded_by=corr_id,
                )
                updated_statements.append(new_stmt)
            else:
                updated_statements.append(stmt)
        else:
            updated_statements.append(stmt)

    updated_relationships, invalidated_ids = invalidate_dependent_relationships(
        relationships=relationships,
        corrected_statement_id=target_id,
        reason=reason,
        correction_id=corr_id,
    )

    return updated_statements, updated_relationships, invalidated_ids


class EditorialApprovalGate:
    """Editorial approval gate and build validation engine.

    Enforces:
    - Task 2.2: Provenance and review-state validation; rejection of missing
      references, unknown programme versions, unreviewed claims, and unlicensed quotes.
    - Task 2.4: Versioned corrections, automatic relationship invalidation, and
      rejection of invalidated comparisons from static build output.
    """

    def __init__(
        self,
        target_election_id: str = "es-gen-2026",
        source_register: Optional[SourceRegister] = None,
        taxonomy: Optional[Taxonomy] = None,
        parties: Optional[list[PartyRecord]] = None,
        programmes: Optional[list[ProgrammeRecord]] = None,
    ) -> None:
        self.target_election_id = target_election_id
        self.source_register = source_register
        self.taxonomy = taxonomy
        self.parties = parties or []
        self.programmes = programmes or []
        self.party_ids = {p.id for p in self.parties} if self.parties else set()
        self.programme_map = {p.programme_id: p for p in self.programmes} if self.programmes else {}

    def validate_statement(
        self,
        stmt: Any,
        require_approved: bool = True,
        target_election_id: Optional[str] = None,
    ) -> list[str]:
        """Validate an electoral claim against provenance, dual-review, and quote-licensing gates."""
        errors: list[str] = []
        stmt_id = getattr(stmt, "id", "")
        if not stmt_id:
            errors.append("Statement missing id.")
            return errors

        stmt_election_id = getattr(stmt, "election_id", "")
        expected_election = target_election_id or self.target_election_id
        if not stmt_election_id:
            errors.append(f"Statement '{stmt_id}' missing election_id.")
        elif expected_election and stmt_election_id != expected_election:
            errors.append(
                f"Statement '{stmt_id}': election mismatch: expected '{expected_election}', found '{stmt_election_id}'."
            )

        # 1. Review status validation (Task 2.2: unreviewed claims fail build)
        raw_status = getattr(stmt, "review_status", None) or getattr(stmt, "status", None)
        status = raw_status.value if hasattr(raw_status, "value") else str(raw_status or "")

        if require_approved:
            if status in ("draft", "under_review", "rejected", "invalidated"):
                errors.append(
                    f"Statement '{stmt_id}': unreviewed claim with review_status '{status}' cannot pass build."
                )

        # Dual-review verification
        reviews_list = getattr(stmt, "reviews", [])
        review_record = getattr(stmt, "review", None)
        if review_record:
            r_errs = review_record.validate()
            for e in r_errs:
                errors.append(f"Statement '{stmt_id}': {e}")
        elif reviews_list:
            approved_revs = [r for r in reviews_list if getattr(r, "verdict", "") == "approved"]
            rev_ids = {getattr(r, "reviewer_id", "") for r in approved_revs}
            if require_approved and (len(approved_revs) < 2 or len(rev_ids) < 2):
                errors.append(
                    f"Statement '{stmt_id}': approved review_status requires dual approval by at least two distinct reviewers (found {len(rev_ids)})."
                )
            for r in reviews_list:
                if hasattr(r, "validate"):
                    for e in r.validate():
                        errors.append(f"Statement '{stmt_id}': {e}")

            # Segregation of duties: drafter cannot serve as secondary reviewer
            drafter = getattr(stmt, "drafter", None)
            if not drafter:
                for r in reviews_list:
                    notes = getattr(r, "review_notes", "").lower()
                    if "drafter:" in notes:
                        drafter = notes.split("drafter:")[1].split()[0].strip()
            if drafter and len(approved_revs) >= 2:
                sec_rev = approved_revs[1].reviewer_id
                if drafter.strip().lower() == sec_rev.strip().lower():
                    errors.append(
                        f"Statement '{stmt_id}': Segregation of duties violation: drafter '{drafter}' cannot serve as secondary reviewer."
                    )
        elif require_approved and status in ("approved", "published"):
            errors.append(
                f"Statement '{stmt_id}' with status '{status}' requires a completed ReviewRecord."
            )

        # 2. Provenance and citation validation (Task 2.2: uncited claims fail build)
        stmt_type = getattr(stmt, "statement_type", "explicit_proposal")
        if stmt_type in ("explicit_proposal", "explicit_opposition"):
            s_url = getattr(stmt, "source_url", None)
            s_ver = getattr(stmt, "source_version", None)
            s_pg = getattr(stmt, "source_page", None)
            s_sec = getattr(stmt, "source_section", None)
            if isinstance(getattr(stmt, "quote", None), QuoteRecord):
                s_pg = s_pg or stmt.quote.page
                s_sec = s_sec or stmt.quote.section
                s_url = s_url or stmt.quote.source_id

            if not s_url or not str(s_url).strip():
                errors.append(
                    f"Statement '{stmt_id}': uncited claim: {stmt_type} must specify source_url."
                )
            if not s_ver or not str(s_ver).strip():
                errors.append(
                    f"Statement '{stmt_id}': uncited claim: {stmt_type} must specify source_version."
                )
            if not (s_pg and str(s_pg).strip()) and not (s_sec and str(s_sec).strip()):
                errors.append(
                    f"Statement '{stmt_id}': uncited claim: {stmt_type} must specify at least one of source_page or source_section."
                )

        elif stmt_type == "not_found":
            s_pg = getattr(stmt, "source_page", None)
            s_sec = getattr(stmt, "source_section", None)
            if s_pg is not None or s_sec is not None:
                errors.append(
                    f"Statement '{stmt_id}': not_found statement must not specify source_page or source_section coordinates."
                )
            if getattr(stmt, "quote", None) is not None:
                errors.append(f"Statement '{stmt_id}': not_found statement must not include quote.")

        # 3. Verbatim quotation limits & licensing (Task 2.2: unlicensed quotes fail build)
        q_obj = getattr(stmt, "quote", None)
        if q_obj is not None:
            if isinstance(q_obj, QuoteRecord):
                q_text = q_obj.text
                q_page = q_obj.page
                q_sec = q_obj.section
                q_source_id = q_obj.source_id
            else:
                q_text = str(q_obj)
                q_page = getattr(stmt, "source_page", None)
                q_sec = getattr(stmt, "source_section", None)
                q_source_id = getattr(stmt, "source_id", None) or getattr(stmt, "programme_id", None)

            q_limits_errs = validate_quote_limits(q_text, page=q_page, section=q_sec)
            for qe in q_limits_errs:
                errors.append(f"Statement '{stmt_id}' quote error: {qe}")

            # Rights review verification against SourceRegister
            if self.source_register:
                src = None
                if q_source_id:
                    src = next((s for s in self.source_register.sources if s.id == q_source_id), None)
                if not src and getattr(stmt, "source_url", None):
                    src = next(
                        (s for s in self.source_register.sources if s.official_url == stmt.source_url or s.direct_url == stmt.source_url),
                        None,
                    )

                if src:
                    if src.election_id != stmt_election_id:
                        errors.append(
                            f"Statement '{stmt_id}': quotation source election '{src.election_id}' does not match statement election '{stmt_election_id}'."
                        )
                    if src.status != "verified":
                        errors.append(
                            f"Statement '{stmt_id}': unsupported quote cannot pass review because source '{src.id}' status is '{src.status}' (must be 'verified')."
                        )
                    if src.rights_review.status not in PERMITTED_QUOTE_RIGHTS:
                        errors.append(
                            f"Statement '{stmt_id}': unsupported quote cannot pass review because source rights status '{src.rights_review.status}' does not allow quotation (requires 'link_and_short_quote' or 'public_domain')."
                        )
                elif self.programme_map and getattr(stmt, "programme_id", None) in self.programme_map:
                    prog = self.programme_map[stmt.programme_id]
                    if prog.rights_status not in ("verified_public_manifesto", "verified_quotation_permitted"):
                        errors.append(
                            f"Statement '{stmt_id}': unsupported quote cannot pass review because programme rights status is '{prog.rights_status}'."
                        )
                elif q_source_id and str(q_source_id).startswith("src-"):
                    errors.append(
                        f"Statement '{stmt_id}': quotation references source '{q_source_id}' which does not exist in source register."
                    )

        # 4. Missing references: party, taxonomy, and programme version
        party_id = getattr(stmt, "party_id", None)
        if self.party_ids and party_id not in self.party_ids:
            errors.append(
                f"Statement '{stmt_id}': missing reference: party_id '{party_id}' not found in registered parties."
            )

        topic_id = getattr(stmt, "topic_id", None)
        subtopic_id = getattr(stmt, "subtopic_id", None)
        if self.taxonomy:
            t_obj = next((t for t in self.taxonomy.topics if t.id == topic_id), None)
            if not t_obj:
                errors.append(f"Statement '{stmt_id}': topic_id '{topic_id}' not found in taxonomy.")
            else:
                st_ids = [st.id for st in t_obj.subtopics]
                if subtopic_id not in st_ids:
                    errors.append(
                        f"Statement '{stmt_id}': subtopic_id '{subtopic_id}' not found under topic '{topic_id}'."
                    )
        elif topic_id not in CORE_TOPIC_IDS:
            errors.append(f"Statement '{stmt_id}': topic_id '{topic_id}' is not one of the core 8 topics.")

        prog_id = getattr(stmt, "programme_id", None)
        if prog_id and self.programme_map:
            prog = self.programme_map.get(prog_id)
            if not prog:
                errors.append(
                    f"Statement '{stmt_id}': missing reference: unknown programme_id '{prog_id}'."
                )
            else:
                if prog.election_id != stmt_election_id:
                    errors.append(
                        f"Statement '{stmt_id}': cross-election mismatch: statement election '{stmt_election_id}' does not match programme election '{prog.election_id}'."
                    )
                s_ver = getattr(stmt, "source_version", None)
                if prog.version and s_ver and prog.version != s_ver:
                    errors.append(
                        f"Statement '{stmt_id}': unknown programme version: statement specifies '{s_ver}' but registered programme version is '{prog.version}'."
                    )
                if prog.status in (ProgrammeStatus.REPLACED, "replaced"):
                    errors.append(
                        f"Statement '{stmt_id}': references replaced programme '{prog_id}' superseded by '{prog.superseded_by}'."
                    )

        return errors

    def validate_relationship(
        self,
        rel: Any,
        statements_by_id: Optional[dict[str, Any]] = None,
        target_election_id: Optional[str] = None,
        allow_invalidated: bool = False,
    ) -> list[str]:
        """Validate a comparative relationship against build publication and invalidation gates."""
        errors: list[str] = []
        rel_id = getattr(rel, "id", "")
        if not rel_id:
            errors.append("Relationship missing id.")
            return errors

        election_id = getattr(rel, "election_id", "")
        expected_election = target_election_id or self.target_election_id
        if not election_id:
            errors.append(f"Relationship '{rel_id}' missing election_id.")
        elif expected_election and election_id != expected_election:
            errors.append(
                f"Relationship '{rel_id}': election mismatch: expected '{expected_election}', found '{election_id}'."
            )

        status = getattr(rel, "status", "active")
        rev_status = getattr(rel, "review_status", "approved")
        invalidation_reason = getattr(rel, "invalidation_reason", None)

        # Acceptance check: Build rejects invalidated comparisons
        if not allow_invalidated:
            if status == "invalidated":
                errors.append(
                    f"Relationship '{rel_id}': invalidated comparison cannot be published in build (reason: {invalidation_reason or 'unspecified'})."
                )
            if rev_status == "invalidated":
                errors.append(
                    f"Relationship '{rel_id}': comparison marked with review_status 'invalidated' cannot be published in build."
                )
            if rev_status not in ("approved", "published", "reviewed"):
                errors.append(
                    f"Relationship '{rel_id}': unreviewed comparison with review_status '{rev_status}' cannot be published in build."
                )
        else:
            if status == "invalidated" and not invalidation_reason:
                errors.append(
                    f"Relationship '{rel_id}': comparison marked invalidated must specify invalidation_reason."
                )

        party_ids = getattr(rel, "party_ids", [])
        if len(party_ids) != 2 or len(set(party_ids)) != 2:
            errors.append(
                f"Relationship '{rel_id}': party_ids must contain exactly 2 distinct party IDs (got {len(party_ids)})."
            )

        statement_ids = getattr(rel, "statement_ids", [])
        if len(statement_ids) < 1 or len(statement_ids) > 2:
            errors.append(
                f"Relationship '{rel_id}': statement_ids must contain 1 or 2 statement IDs."
            )

        if statements_by_id is not None:
            for s_id in statement_ids:
                stmt = statements_by_id.get(s_id)
                if not stmt:
                    errors.append(
                        f"Relationship '{rel_id}': referenced statement '{s_id}' not found."
                    )
                    continue

                stmt_election = getattr(stmt, "election_id", "")
                if stmt_election != election_id:
                    errors.append(
                        f"Relationship '{rel_id}': cross-election error: relationship election '{election_id}' "
                        f"cannot reference statement '{s_id}' from election '{stmt_election}'."
                    )

                stmt_status = getattr(stmt, "review_status", None) or getattr(stmt, "status", None)
                if hasattr(stmt_status, "value"):
                    stmt_status = stmt_status.value
                if stmt_status == "invalidated":
                    errors.append(
                        f"Relationship '{rel_id}': cannot reference invalidated statement '{s_id}'."
                    )
                elif not allow_invalidated and stmt_status not in ("approved", "published", "reviewed"):
                    errors.append(
                        f"Relationship '{rel_id}': cannot reference unreviewed statement '{s_id}' (status '{stmt_status}') in build."
                    )

                if getattr(rel, "relationship_type", "") == "agreement":
                    stmt_type = getattr(stmt, "statement_type", "")
                    if stmt_type == "not_found":
                        errors.append(
                            f"Relationship '{rel_id}': agreement cannot be asserted with not_found statement '{s_id}'."
                        )

        return errors

    def filter_publishable_comparisons(
        self,
        relationships: list[Any],
        statements_by_id: Optional[dict[str, Any]] = None,
    ) -> tuple[list[Any], list[Any]]:
        """Filter comparisons into publishable (active, approved) and excluded (invalidated/unreviewed).

        Returns (publishable, excluded).
        """
        publishable: list[Any] = []
        excluded: list[Any] = []

        for rel in relationships:
            rel_status = getattr(rel, "status", "active")
            rev_status = getattr(rel, "review_status", "approved")
            if hasattr(rel_status, "value"):
                rel_status = rel_status.value
            if hasattr(rev_status, "value"):
                rev_status = rev_status.value

            if rel_status == "invalidated" or rev_status == "invalidated":
                excluded.append(rel)
                continue

            if rev_status not in ("approved", "published", "reviewed"):
                excluded.append(rel)
                continue

            if statements_by_id:
                has_invalid_stmt = False
                for s_id in getattr(rel, "statement_ids", []):
                    stmt = statements_by_id.get(s_id)
                    if not stmt:
                        has_invalid_stmt = True
                        break
                    s_stat = getattr(stmt, "review_status", None) or getattr(stmt, "status", None)
                    if hasattr(s_stat, "value"):
                        s_stat = s_stat.value
                    if s_stat in ("invalidated", "draft", "under_review", "rejected"):
                        has_invalid_stmt = True
                        break
                if has_invalid_stmt:
                    excluded.append(rel)
                    continue

            publishable.append(rel)

        return publishable, excluded

    def validate_build_corpus(
        self,
        statements: list[Any],
        relationships: list[Any],
        corrections: Optional[list[Any]] = None,
        target_election_id: Optional[str] = None,
        allow_invalidated: bool = False,
    ) -> list[str]:
        """Validate an entire electoral comparison corpus for a static publication build.

        Guarantees that unreviewed/uncited claims and invalidated comparisons fail the build.
        """
        errors: list[str] = []
        election_id = target_election_id or self.target_election_id
        statements_by_id: dict[str, Any] = {}

        for stmt in statements:
            s_id = getattr(stmt, "id", "")
            if s_id in statements_by_id:
                errors.append(f"Duplicate statement ID: '{s_id}'.")
            statements_by_id[s_id] = stmt
            errors.extend(
                self.validate_statement(
                    stmt,
                    require_approved=True,
                    target_election_id=election_id,
                )
            )

        for rel in relationships:
            errors.extend(
                self.validate_relationship(
                    rel,
                    statements_by_id=statements_by_id,
                    target_election_id=election_id,
                    allow_invalidated=allow_invalidated,
                )
            )

        if corrections:
            for corr in corrections:
                if hasattr(corr, "validate"):
                    errors.extend(corr.validate())
                target_id = getattr(corr, "target_id", None) or getattr(corr, "statement_id", None)
                if target_id and target_id not in statements_by_id:
                    errors.append(
                        f"Correction '{getattr(corr, 'id', '')}' references non-existent statement '{target_id}'."
                    )

        return errors


def validate_editorial_corpus(
    statements: list[Any],
    relationships: list[Any],
    corrections: Optional[list[Any]] = None,
    source_register: Optional[SourceRegister] = None,
    taxonomy: Optional[Taxonomy] = None,
    parties: Optional[list[PartyRecord]] = None,
    programmes: Optional[list[ProgrammeRecord]] = None,
    target_election_id: Optional[str] = None,
    allow_invalidated: bool = False,
) -> list[str]:
    """Validate an entire editorial corpus for integrity, citation rights, and consistency."""
    gate = EditorialApprovalGate(
        target_election_id=target_election_id or "es-gen-2026",
        source_register=source_register,
        taxonomy=taxonomy,
        parties=parties,
        programmes=programmes,
    )
    return gate.validate_build_corpus(
        statements=statements,
        relationships=relationships,
        corrections=corrections or [],
        target_election_id=target_election_id,
        allow_invalidated=allow_invalidated,
    )


def validate_build_corpus(
    statements: list[Any],
    relationships: list[Any],
    corrections: Optional[list[Any]] = None,
    source_register: Optional[SourceRegister] = None,
    taxonomy: Optional[Taxonomy] = None,
    parties: Optional[list[PartyRecord]] = None,
    programmes: Optional[list[ProgrammeRecord]] = None,
    target_election_id: Optional[str] = None,
    allow_invalidated: bool = False,
) -> list[str]:
    """Validate an entire electoral comparison corpus for a static publication build."""
    return validate_editorial_corpus(
        statements=statements,
        relationships=relationships,
        corrections=corrections,
        source_register=source_register,
        taxonomy=taxonomy,
        parties=parties,
        programmes=programmes,
        target_election_id=target_election_id,
        allow_invalidated=allow_invalidated,
    )


def filter_publishable_comparisons(
    relationships: list[Any],
    statements_by_id: Optional[dict[str, Any]] = None,
) -> tuple[list[Any], list[Any]]:
    """Filter comparisons into publishable (active, approved) and excluded (invalidated/unreviewed)."""
    gate = EditorialApprovalGate()
    return gate.filter_publishable_comparisons(relationships, statements_by_id=statements_by_id)


def validate_build(root_dir: Path | str, target_election_id: str = "es-gen-2026") -> tuple[int, int, list[str]]:
    """Validate all editorial content under root_dir against approval gates and build rejection rules."""
    root = Path(root_dir)
    content_dir = root / "content"
    errors: list[str] = []
    checks_passed = 0

    # 1. Load taxonomy, source register, and parties
    taxonomy_path = content_dir / "taxonomy.json"
    taxonomy = load_taxonomy(taxonomy_path) if taxonomy_path.exists() else None

    register_path = content_dir / "sources" / "register.json"
    register = load_register(register_path) if register_path.exists() else None

    parties_path = content_dir / "examples" / "parties.json"
    parties = load_parties(parties_path) if parties_path.exists() else []

    # 2. Load programmes
    programmes: list[ProgrammeRecord] = []
    prog_dir = content_dir / "examples" / "programmes"
    if prog_dir.exists():
        for p_file in prog_dir.glob("*.json"):
            programmes.append(load_programme(p_file))

    # 3. Load statements
    statements: list[Any] = []
    stmt_dir = content_dir / "examples" / "statements"
    if stmt_dir.exists():
        for s_file in stmt_dir.glob("*.json"):
            statements.append(load_schema_statement(s_file))

    # 4. Load relationships
    relationships: list[Any] = []
    rel_dir = content_dir / "examples" / "relationships"
    if rel_dir.exists():
        for r_file in rel_dir.glob("*.json"):
            relationships.append(load_schema_relationship(r_file))

    # 5. Load corrections
    corrections: list[Any] = []
    corr_dir = content_dir / "examples" / "corrections"
    if corr_dir.exists():
        for c_file in corr_dir.glob("*.json"):
            corrections.append(load_schema_correction(c_file))

    gate = EditorialApprovalGate(
        target_election_id=target_election_id,
        source_register=register,
        taxonomy=taxonomy,
        parties=parties,
        programmes=programmes,
    )

    # Filter statements and relationships for target election
    target_stmts = [s for s in statements if getattr(s, "election_id", "") == target_election_id]
    target_rels = [r for r in relationships if getattr(r, "election_id", "") == target_election_id]
    target_corrs = [c for c in corrections if getattr(c, "election_id", "") == target_election_id]

    # Validate valid target election corpus
    corpus_errors = gate.validate_build_corpus(
        statements=target_stmts,
        relationships=target_rels,
        corrections=target_corrs,
        target_election_id=target_election_id,
        allow_invalidated=False,
    )
    if corpus_errors:
        errors.extend(corpus_errors)
    else:
        checks_passed += 1

    # 6. Verify Acceptance Gates: Build rejects unreviewed/uncited claims and invalidated comparisons

    # Negative Gate 1: unreviewed claim rejected
    test_unreviewed = SchemaStatementRecord(
        schema_version="1.0.0",
        election_id=target_election_id,
        id="stmt-test-gate-unreviewed",
        party_id="partido-ejemplo-a",
        topic_id="housing",
        subtopic_id="rental-regulation",
        statement_type="explicit_proposal",
        summary="Propuesta no revisada para test de gate.",
        review_status="draft",
        source_url="https://ejemplo.es",
        source_version="1.0.0",
        source_page="1",
    )
    errs_unreviewed = gate.validate_statement(test_unreviewed, require_approved=True)
    if any("unreviewed claim" in e for e in errs_unreviewed):
        checks_passed += 1
    else:
        errors.append("Gate verification failed: unreviewed claim was NOT rejected by the build gate.")

    # Negative Gate 2: uncited claim rejected
    test_uncited = SchemaStatementRecord(
        schema_version="1.0.0",
        election_id=target_election_id,
        id="stmt-test-gate-uncited",
        party_id="partido-ejemplo-a",
        topic_id="housing",
        subtopic_id="rental-regulation",
        statement_type="explicit_proposal",
        summary="Propuesta sin cita para test de gate.",
        review_status="approved",
        source_url=None,
        source_version=None,
        source_page=None,
        source_section=None,
    )
    errs_uncited = gate.validate_statement(test_uncited, require_approved=True)
    if any("uncited claim" in e for e in errs_uncited):
        checks_passed += 1
    else:
        errors.append("Gate verification failed: uncited claim was NOT rejected by the build gate.")

    # Negative Gate 3: unlicensed quote rejected (exceeds word limit)
    test_unlicensed = SchemaStatementRecord(
        schema_version="1.0.0",
        election_id=target_election_id,
        id="stmt-test-gate-unlicensed",
        party_id="partido-ejemplo-a",
        topic_id="housing",
        subtopic_id="rental-regulation",
        statement_type="explicit_proposal",
        summary="Propuesta con cita excesiva para test de gate.",
        quote=" ".join(["palabra"] * 45),
        source_url="https://ejemplo.es",
        source_version="1.0.0",
        source_page="10",
        review_status="approved",
    )
    errs_unlicensed = gate.validate_statement(test_unlicensed, require_approved=True)
    if any("exceeds maximum limit of 40 words" in e for e in errs_unlicensed):
        checks_passed += 1
    else:
        errors.append("Gate verification failed: unlicensed quote was NOT rejected by the build gate.")

    # Negative Gate 4: invalidated comparison rejected
    test_invalidated_rel = SchemaRelationshipRecord(
        schema_version="1.0.0",
        election_id=target_election_id,
        id="rel-test-gate-invalidated",
        topic_id="housing",
        subtopic_id="rental-regulation",
        measure_label="Medida",
        party_ids=["partido-ejemplo-a", "partido-ejemplo-b"],
        statement_ids=["stmt-party-a-housing-001"],
        relationship_type="single_party",
        summary="Comparativa invalidada",
        review_status="invalidated",
        status="invalidated",
        invalidation_reason="Test invalidation reason",
    )
    errs_inv_rel = gate.validate_relationship(test_invalidated_rel, allow_invalidated=False)
    if any("invalidated comparison cannot be published in build" in e for e in errs_inv_rel):
        checks_passed += 1
    else:
        errors.append("Gate verification failed: invalidated comparison was NOT rejected by the build gate.")

    # Negative Gate 5: changing source claim invalidates dependent comparison
    sample_rel = SchemaRelationshipRecord(
        schema_version="1.0.0",
        election_id=target_election_id,
        id="rel-test-gate-active",
        topic_id="housing",
        subtopic_id="rental-regulation",
        measure_label="Medida",
        party_ids=["partido-ejemplo-a", "partido-ejemplo-b"],
        statement_ids=["stmt-target-change-001", "stmt-party-b-housing-001"],
        relationship_type="agreement",
        summary="Comparativa activa",
        review_status="approved",
        status="active",
    )
    updated_rels, inv_ids = invalidate_dependent_relationships(
        relationships=[sample_rel],
        corrected_statement_id="stmt-target-change-001",
        reason="Errata en porcentaje",
    )
    if inv_ids == ["rel-test-gate-active"] and updated_rels[0].status == "invalidated":
        checks_passed += 1
    else:
        errors.append("Gate verification failed: correction did not invalidate dependent relationship.")

    checks_failed = len(errors)
    return checks_passed, checks_failed, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Editorial approval gates and build validation CLI")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("validate-build", help="Validate content against editorial build gates")
    build_parser.add_argument("--root", help="Root repository directory", default=None)
    build_parser.add_argument("--election-id", help="Target election ID", default="es-gen-2026")

    inv_parser = subparsers.add_parser("invalidate", help="Invalidate relationships dependent on statement")
    inv_parser.add_argument("--statement-id", required=True, help="Statement ID to invalidate")
    inv_parser.add_argument("--reason", required=True, help="Reason for invalidation")
    inv_parser.add_argument("--correction-id", help="Associated correction ID", default=None)

    args = parser.parse_args()

    if args.command == "validate-build":
        root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent.parent
        passed, failed, errors = validate_build(root, target_election_id=args.election_id)
        print("Editorial Approval and Build Gate Report:")
        print(f"  Passed gate checks: {passed}")
        print(f"  Failed gate checks: {failed}")
        if errors:
            print("\nErrors encountered:", file=sys.stderr)
            for err in errors:
                print(f" - {err}", file=sys.stderr)
            sys.exit(1)
        else:
            print("\nOK: Build rejects unreviewed/uncited claims and invalidated comparisons.")
            sys.exit(0)

    elif args.command == "invalidate":
        print(f"Invalidation requested for statement '{args.statement_id}'.")
        print(f"Reason: {args.reason}")
        if args.correction_id:
            print(f"Correction ID: {args.correction_id}")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
