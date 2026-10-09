"""Editorial policy rules, quotation limits, reviewer roles, and correction processes.

Implements the editorial governance model defined in docs/CONTENT-METHODOLOGY.md
and ADR-0002 in docs/DECISION-RECORD.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from elecciones2026.methodology import CORE_TOPIC_IDS, Taxonomy
from elecciones2026.source_register import SourceRecord, SourceRegister

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


def invalidate_dependent_relationships(
    relationships: list[ComparisonRelationship],
    corrected_statement_id: str,
    reason: str,
) -> tuple[list[ComparisonRelationship], list[str]]:
    """Invalidate all comparison relationships that depend on a corrected statement.

    Returns the updated list of relationships and a list of invalidated relationship IDs.
    """
    updated: list[ComparisonRelationship] = []
    invalidated_ids: list[str] = []

    for rel in relationships:
        if corrected_statement_id in rel.statement_ids:
            new_rel = ComparisonRelationship(
                id=rel.id,
                election_id=rel.election_id,
                topic_id=rel.topic_id,
                party_ids=rel.party_ids,
                statement_ids=rel.statement_ids,
                relationship_type=rel.relationship_type,
                description_es=rel.description_es,
                status="invalidated",
                invalidation_reason=f"Dependent on corrected statement '{corrected_statement_id}': {reason}",
            )
            updated.append(new_rel)
            invalidated_ids.append(rel.id)
        else:
            updated.append(rel)

    return updated, invalidated_ids


def validate_editorial_corpus(
    statements: list[StatementRecord],
    relationships: list[ComparisonRelationship],
    corrections: list[CorrectionRecord],
    source_register: Optional[SourceRegister] = None,
    taxonomy: Optional[Taxonomy] = None,
) -> list[str]:
    """Validate an entire editorial corpus for integrity, citation rights, and consistency.

    Guarantees that no unsupported quote, single-reviewer statement, or unverified
    dependent comparison passes publication validation.
    """
    errors: list[str] = []

    statement_ids = set()
    for s in statements:
        if s.id in statement_ids:
            errors.append(f"Duplicate statement ID: '{s.id}'.")
        statement_ids.add(s.id)
        errors.extend(s.validate(source_register=source_register, taxonomy=taxonomy))

    for rel in relationships:
        errors.extend(rel.validate())
        for s_id in rel.statement_ids:
            if s_id not in statement_ids:
                errors.append(
                    f"Relationship '{rel.id}' references non-existent statement '{s_id}'."
                )

    for corr in corrections:
        errors.extend(corr.validate())
        if corr.statement_id not in statement_ids:
            errors.append(
                f"Correction '{corr.id}' references non-existent statement '{corr.statement_id}'."
            )

    return errors
