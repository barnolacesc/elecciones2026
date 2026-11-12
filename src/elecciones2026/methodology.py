"""Methodology definitions and validation rules for election 2026.

Implements candidate inclusion criteria, party naming rules, programme status lifecycle,
and topic taxonomy according to docs/CONTENT-METHODOLOGY.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ProgrammeStatus(str, Enum):
    """Lifecycle states for an election programme."""

    MISSING = "missing"
    ANNOUNCED = "announced"
    PARTIAL = "partial"
    PUBLISHED_UNVERIFIED = "published-unverified"
    OFFICIAL = "official"
    REPLACED = "replaced"


VALID_STATUSES = {s.value for s in ProgrammeStatus}

# Exactly 8 core topics defined in the approved taxonomy (Version 1.0.0)
CORE_TOPIC_IDS = (
    "housing",
    "education",
    "health-social-services",
    "economy-work-tax",
    "immigration",
    "foreign-policy-eu",
    "climate-energy",
    "institutions-rights",
)


@dataclass(frozen=True)
class Subtopic:
    id: str
    name_es: str
    name_en: str


@dataclass(frozen=True)
class Topic:
    id: str
    name_es: str
    name_en: str
    description_es: str
    description_en: str
    subtopics: list[Subtopic] = field(default_factory=list)


@dataclass(frozen=True)
class Taxonomy:
    schema_version: str
    taxonomy_version: str
    election_id: str
    topics: list[Topic]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Taxonomy:
        topics = []
        for t in data.get("topics", []):
            subtopics = [
                Subtopic(
                    id=st["id"],
                    name_es=st["name_es"],
                    name_en=st["name_en"],
                )
                for st in t.get("subtopics", [])
            ]
            topics.append(
                Topic(
                    id=t["id"],
                    name_es=t["name_es"],
                    name_en=t["name_en"],
                    description_es=t["description_es"],
                    description_en=t["description_en"],
                    subtopics=subtopics,
                )
            )
        return cls(
            schema_version=data["schema_version"],
            taxonomy_version=data["taxonomy_version"],
            election_id=data["election_id"],
            topics=topics,
        )

    def validate(self, *, allow_extensions: bool = False) -> list[str]:
        """Validate taxonomy integrity against policy rules."""
        errors: list[str] = []
        topic_ids = [t.id for t in self.topics]

        # Must have exactly the 8 core topics
        if not allow_extensions and len(topic_ids) != len(CORE_TOPIC_IDS):
            errors.append(
                f"Expected exactly {len(CORE_TOPIC_IDS)} core topics, found {len(topic_ids)}."
            )

        missing_core = set(CORE_TOPIC_IDS) - set(topic_ids)
        if missing_core:
            errors.append(f"Missing core topics: {sorted(missing_core)}.")

        unexpected = set(topic_ids) - set(CORE_TOPIC_IDS)
        if unexpected and not allow_extensions:
            errors.append(f"Unexpected topics: {sorted(unexpected)}.")

        # Check subtopics uniqueness and labels
        seen_topic_ids = set()
        for topic in self.topics:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", topic.id):
                errors.append(f"Invalid topic ID: {topic.id}.")
            if topic.id in seen_topic_ids:
                errors.append(f"Duplicate topic ID: {topic.id}.")
            seen_topic_ids.add(topic.id)

            if not topic.name_es or not topic.name_en:
                errors.append(f"Topic '{topic.id}' must provide both Spanish and English names.")
            if not topic.subtopics:
                errors.append(f"Topic '{topic.id}' has no subtopics defined.")

            seen_subtopic_ids = set()
            for st in topic.subtopics:
                if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", st.id):
                    errors.append(f"Invalid subtopic ID: {st.id}.")
                if st.id in seen_subtopic_ids:
                    errors.append(
                        f"Duplicate subtopic ID '{st.id}' under topic '{topic.id}'."
                    )
                seen_subtopic_ids.add(st.id)
                if not st.name_es or not st.name_en:
                    errors.append(
                        f"Subtopic '{st.id}' in '{topic.id}' must have Spanish and English names."
                    )

        return errors


@dataclass(frozen=True)
class PartyRecord:
    id: str
    official_name: str
    display_name: str
    short_name: str
    ballot_name: str
    is_coalition: bool
    coalition_members: list[str]
    territorial_scope: str
    inclusion_criterion: str
    is_fixture: bool = False

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.id or not self.id.replace("-", "").isalnum() or self.id != self.id.lower():
            errors.append(
                f"Party ID '{self.id}' must be a non-empty lowercase alphanumeric hyphen-separated slug."
            )
        if not self.official_name:
            errors.append(f"Party '{self.id}' is missing official_name.")
        if not self.display_name:
            errors.append(f"Party '{self.id}' is missing display_name.")
        if not self.short_name:
            errors.append(f"Party '{self.id}' is missing short_name.")
        if self.is_coalition and not self.coalition_members:
            errors.append(
                f"Party '{self.id}' is marked as a coalition but has no coalition_members listed."
            )
        if not self.is_coalition and self.coalition_members:
            errors.append(
                f"Party '{self.id}' is not marked as a coalition but specifies coalition_members."
            )
        return errors


@dataclass(frozen=True)
class ProgrammeRecord:
    schema_version: str
    election_id: str
    programme_id: str
    candidacy_id: str
    title: str
    status: ProgrammeStatus
    version: Optional[str] = None
    publisher: Optional[str] = None
    official_url: Optional[str] = None
    publication_date: Optional[str] = None
    retrieval_date: Optional[str] = None
    language: str = "es"
    sha256: Optional[str] = None
    rights_status: str = "pending"
    coverage_notes: Optional[str] = None
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    replacement_reason: Optional[str] = None
    is_fixture: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProgrammeRecord:
        status_val = data.get("status")
        if status_val not in VALID_STATUSES:
            raise ValueError(f"Invalid programme status: {status_val}")
        return cls(
            schema_version=data["schema_version"],
            election_id=data["election_id"],
            programme_id=data["programme_id"],
            candidacy_id=data["candidacy_id"],
            title=data["title"],
            status=ProgrammeStatus(status_val),
            version=data.get("version"),
            publisher=data.get("publisher"),
            official_url=data.get("official_url"),
            publication_date=data.get("publication_date"),
            retrieval_date=data.get("retrieval_date"),
            language=data.get("language", "es"),
            sha256=data.get("sha256"),
            rights_status=data.get("rights_status", "pending"),
            coverage_notes=data.get("coverage_notes"),
            supersedes=data.get("supersedes"),
            superseded_by=data.get("superseded_by"),
            replacement_reason=data.get("replacement_reason"),
            is_fixture=data.get("is_fixture", False),
        )

    def validate(self, target_election_id: str = "es-gen-2026") -> list[str]:
        """Validate programme record according to status lifecycle and provenance requirements."""
        errors: list[str] = []

        if self.election_id != target_election_id:
            errors.append(
                f"Election mismatch: expected '{target_election_id}', found '{self.election_id}'."
            )

        if not self.programme_id:
            errors.append("Missing programme_id.")
        if not self.candidacy_id:
            errors.append("Missing candidacy_id.")

        # Status-specific rules
        if self.status == ProgrammeStatus.OFFICIAL:
            if not self.official_url:
                errors.append("Official programme must provide official_url.")
            if not self.version:
                errors.append("Official programme must provide version.")
            if not self.publication_date:
                errors.append("Official programme must provide publication_date.")
            if not self.retrieval_date:
                errors.append("Official programme must provide retrieval_date.")
            if not self.sha256 or len(self.sha256) != 64 or not all(c in "0123456789abcdefABCDEF" for c in self.sha256):
                errors.append("Official programme must provide valid 64-character hex SHA-256 hash.")
            if self.rights_status not in {"verified_public_manifesto", "verified_quotation_permitted", "verified_link_only"}:
                errors.append(
                    f"Official programme requires verified rights status, got '{self.rights_status}'."
                )

        elif self.status == ProgrammeStatus.PARTIAL:
            if not self.coverage_notes:
                errors.append("Partial programme must provide coverage_notes explaining limitations.")
            if not self.official_url:
                errors.append("Partial programme must provide official_url to source.")

        elif self.status == ProgrammeStatus.MISSING:
            if self.official_url is not None:
                errors.append("Missing programme must have null official_url.")
            if self.sha256 is not None:
                errors.append("Missing programme must have null sha256.")
            if not self.coverage_notes:
                errors.append("Missing programme must explain coverage state in coverage_notes.")

        elif self.status == ProgrammeStatus.REPLACED:
            if not self.superseded_by:
                errors.append("Replaced programme must specify superseded_by pointing to successor.")
            if not self.replacement_reason:
                errors.append("Replaced programme must specify replacement_reason.")
            if not self.sha256:
                errors.append("Replaced programme must preserve historical sha256.")

        return errors


def load_taxonomy(path: Path) -> Taxonomy:
    """Load taxonomy from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Taxonomy.from_dict(data)


def load_programme(path: Path | str) -> ProgrammeRecord:
    """Load programme record from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ProgrammeRecord.from_dict(data)


def load_parties(path: Path | str) -> list[PartyRecord]:
    """Load party records from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    parties = []
    for item in data.get("parties", []):
        parties.append(
            PartyRecord(
                id=item["id"],
                official_name=item["official_name"],
                display_name=item["display_name"],
                short_name=item["short_name"],
                ballot_name=item["ballot_name"],
                is_coalition=item.get("is_coalition", False),
                coalition_members=list(item.get("coalition_members", [])),
                territorial_scope=item.get("territorial_scope", "national"),
                inclusion_criterion=item.get("inclusion_criterion", ""),
                is_fixture=item.get("is_fixture", False),
            )
        )
    return parties
