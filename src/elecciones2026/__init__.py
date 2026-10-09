"""Offline validation and static build pipeline for elecciones2026."""

from typing import Any

__all__ = [
    "CORE_TOPIC_IDS",
    "PartyRecord",
    "ProgrammeRecord",
    "ProgrammeStatus",
    "Taxonomy",
    "load_programme",
    "load_taxonomy",
    "ReviewRecord",
    "StatementRecord",
    "RelationshipRecord",
    "CandidacyCoverageRecord",
    "ElectionCoverageSnapshot",
    "CorrectionRecord",
    "invalidate_dependent_relationships",
    "load_statement",
    "load_relationship",
    "load_coverage_record",
    "load_coverage_snapshot",
    "load_correction",
    "validate_any_record",
    "ElectionRecord",
    "SourceRecord",
    "SourceRegister",
    "load_register",
    "ReviewerRole",
    "StatementStatus",
    "CorrectionType",
    "CorrectionSeverity",
    "QuoteRecord",
    "ComparisonRelationship",
    "validate_editorial_corpus",
    "validate_selection",
    "validate_ui_flow_files",
]


def __getattr__(name: str) -> Any:
    if name in {
        "CORE_TOPIC_IDS",
        "PartyRecord",
        "ProgrammeRecord",
        "ProgrammeStatus",
        "Taxonomy",
        "load_programme",
        "load_taxonomy",
    }:
        import elecciones2026.methodology as m

        return getattr(m, name)
    if name in {
        "ReviewRecord",
        "StatementRecord",
        "RelationshipRecord",
        "CandidacyCoverageRecord",
        "ElectionCoverageSnapshot",
        "CorrectionRecord",
        "invalidate_dependent_relationships",
        "load_statement",
        "load_relationship",
        "load_coverage_record",
        "load_coverage_snapshot",
        "load_correction",
        "validate_any_record",
    }:
        import elecciones2026.schemas as s

        return getattr(s, name)
    if name in {
        "ElectionRecord",
        "SourceRecord",
        "SourceRegister",
        "load_register",
    }:
        import elecciones2026.source_register as sr

        return getattr(sr, name)
    if name in {
        "ReviewerRole",
        "StatementStatus",
        "CorrectionType",
        "CorrectionSeverity",
        "QuoteRecord",
        "ComparisonRelationship",
        "validate_editorial_corpus",
    }:
        import elecciones2026.editorial as ed

        return getattr(ed, name)
    if name in {
        "validate_selection",
        "validate_ui_flow_files",
    }:
        import elecciones2026.ui_flow as uf

        return getattr(uf, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
