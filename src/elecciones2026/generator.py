"""Deterministic static site generator for Elecciones 2026.

Produces crawlable, accessible Spanish HTML without JavaScript dependencies,
conforming to WCAG 2.2 Level AA, ADR-0001, ADR-0002, site/COMPONENT-PLAN.md,
and OpenSpec change mvp-programme-comparison (Roadmap package E3.1).
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit

from elecciones2026.editorial import (
    MAX_QUOTE_CHARS,
    MAX_QUOTE_WORDS,
    PERMITTED_QUOTE_RIGHTS,
    PERMITTED_SUMMARY_RIGHTS,
    RESTRICTED_QUOTE_RIGHTS,
)
from elecciones2026.methodology import (
    CORE_TOPIC_IDS,
    Taxonomy,
    Topic,
    load_programme,
    load_taxonomy,
)
from elecciones2026.schemas import (
    CorrectionRecord,
    RelationshipRecord,
    ReviewRecord,
    StatementRecord,
    PLACEHOLDER_REVIEWER_PATTERN,
    load_correction,
    load_relationship,
    load_statement,
)
from elecciones2026.source_register import (
    SourceRecord,
    SourceRegister,
    load_register,
)

DEFAULT_CANONICAL_BASE = "https://xn--eleccionesespaa2026-83b.es"
DEFAULT_BUILD_DATE = "2026-10-09"
DEFAULT_ELECTION_ID = "es-gen-2026"


class BuildValidationError(Exception):
    """Raised when data validation fails during static site generation."""


@dataclass(frozen=True)
class PartyInfo:
    """Simplified party model for templating."""
    id: str
    official_name: str
    display_name: str
    short_name: str
    ballot_name: str
    is_coalition: bool = False
    coalition_members: list[str] = field(default_factory=list)
    territorial_scope: str = "national"
    inclusion_criterion: str = "criterion_a_parliamentary_representation"
    is_fixture: bool = False


@dataclass
class SiteContext:
    """Loaded and validated dataset for building the static site."""
    root_dir: Path
    content_dir: Path
    election_id: str
    canonical_base: str
    build_date: str
    taxonomy: Taxonomy
    register: SourceRegister
    parties: dict[str, PartyInfo]
    statements: dict[str, StatementRecord]
    relationships: dict[str, RelationshipRecord]
    corrections: list[CorrectionRecord]
    i18n: dict[str, Any]
    templates_dir: Path
    production_records: bool = False
    budget_payload: Optional[dict] = None
    budget_manifest: Optional[dict] = None
    budget_bundle_id: Optional[str] = None
    budget_projection_id: Optional[str] = None


@dataclass(frozen=True)
class SiteBuildResult:
    """Artifacts and verification metrics of a deterministic static build."""
    output_dir: Path
    build_date: str
    election_id: str
    files_written: list[str]
    file_hashes: dict[str, str]
    topics_count: int
    parties_count: int
    statements_count: int
    relationships_count: int


def escape(text: Optional[str]) -> str:
    """Safely escape text for inert HTML output, preventing XSS injection."""
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def load_translations(i18n_file: Path) -> dict[str, Any]:
    """Load UI string dictionary from versioned JSON."""
    if not i18n_file.exists():
        raise BuildValidationError(f"Translations file not found: {i18n_file}")
    with i18n_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_parties(parties_file: Path) -> dict[str, PartyInfo]:
    """Load party representations from JSON."""
    parties: dict[str, PartyInfo] = {}
    if not parties_file.exists():
        return parties
    with parties_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    for p in data.get("parties", []):
        party = PartyInfo(
            id=p["id"],
            official_name=p.get("official_name", p["id"]),
            display_name=p.get("display_name", p.get("official_name", p["id"])),
            short_name=p.get("short_name", p["id"]),
            ballot_name=p.get("ballot_name", p.get("display_name", p["id"])),
            is_coalition=p.get("is_coalition", False),
            coalition_members=p.get("coalition_members", []),
            territorial_scope=p.get("territorial_scope", "national"),
            inclusion_criterion=p.get("inclusion_criterion", "criterion_a_parliamentary_representation"),
            is_fixture=p.get("is_fixture", False),
        )
        parties[party.id] = party
    return parties


def load_and_validate_site_data(
    root_dir: Path,
    content_dir: Optional[Path] = None,
    election_id: str = DEFAULT_ELECTION_ID,
    canonical_base: str = DEFAULT_CANONICAL_BASE,
    build_date: Optional[str] = None,
    strict_approved: bool = True,
    custom_statements: Optional[list[StatementRecord]] = None,
    custom_relationships: Optional[list[RelationshipRecord]] = None,
    records_dir: Optional[Path] = None,
) -> SiteContext:
    """Load and strictly validate all source records before publishing."""
    if content_dir is None:
        content_dir = root_dir / "content"
    production_records = records_dir is not None
    record_root = records_dir if production_records else content_dir / "examples"
    if production_records:
        if not record_root.is_dir():
            raise BuildValidationError(f"Production records directory missing: {record_root}")
        strict_approved = True

    base = urlsplit(canonical_base)
    if (base.scheme not in {"http", "https"} or not base.hostname
            or base.username is not None or base.password is not None
            or base.query or base.fragment):
        raise BuildValidationError("Canonical base must be an absolute HTTP(S) URL without credentials, query, or fragment.")

    # Determine build date deterministically
    resolved_date = build_date
    if not resolved_date:
        resolved_date = os.environ.get("SOURCE_DATE_EPOCH_DATE")
    if not resolved_date:
        resolved_date = DEFAULT_BUILD_DATE

    # 1. Load taxonomy
    taxonomy_file = content_dir / "taxonomy.json"
    election_taxonomy = production_records and (record_root / "taxonomy.json").exists()
    if election_taxonomy:
        taxonomy_file = record_root / "taxonomy.json"
    if not taxonomy_file.exists():
        raise BuildValidationError(f"Taxonomy file missing: {taxonomy_file}")
    taxonomy = load_taxonomy(taxonomy_file)
    if production_records:
        taxonomy_errors = taxonomy.validate(allow_extensions=bool(election_taxonomy))
        if taxonomy.election_id != election_id:
            taxonomy_errors.append("Production taxonomy has an election mismatch.")
        if not re.fullmatch(r"\d+\.\d+\.\d+", taxonomy.taxonomy_version):
            taxonomy_errors.append("Production taxonomy requires a stable version, not a draft.")
        if taxonomy_errors:
            raise BuildValidationError("Invalid production taxonomy: " + "; ".join(taxonomy_errors))

    # 2. Load source register
    register_file = content_dir / "sources" / "register.json"
    if not register_file.exists():
        raise BuildValidationError(f"Source register missing: {register_file}")
    register = load_register(register_file)
    if production_records:
        if not build_date and not os.environ.get("SOURCE_DATE_EPOCH_DATE"):
            resolved_date = register.last_updated
        if election_id not in {e.id for e in register.elections}:
            raise BuildValidationError(f"Unknown production election: {election_id}")
        register = replace(register, sources=[s for s in register.sources
                                              if s.election_id == election_id and s.status != "replaced"])

    # 3. Load parties
    parties_file = record_root / "parties.json"
    parties = load_parties(parties_file)
    # Also add parties tracked in source register if missing
    for src in register.sources:
        if src.party_id not in parties:
            parties[src.party_id] = PartyInfo(
                id=src.party_id,
                official_name=src.candidature_name,
                display_name=src.publisher,
                short_name=src.party_id.upper(),
                ballot_name=src.candidature_name,
                is_coalition=False,
                coalition_members=[],
                territorial_scope="pending_verification" if production_records else src.scope,
                inclusion_criterion="pending_verification" if production_records else "criterion_a_parliamentary_representation",
            )

    # For 2023 pilot rehearsal, restrict parties strictly to candidacies with 2023 sources
    if election_id == "es-gen-2023":
        pilot_party_ids = {s.party_id for s in register.sources if s.election_id == "es-gen-2023"}
        parties = {pid: p for pid, p in parties.items() if pid in pilot_party_ids}
    if production_records:
        source_party_ids = {s.party_id for s in register.sources}
        if any(p.is_fixture or pid not in source_party_ids for pid, p in parties.items()):
            raise BuildValidationError("Production parties must be non-fixture election-scoped source records.")

    # 4. Load translations
    i18n_file = content_dir / "i18n" / "es.json"
    i18n = load_translations(i18n_file)

    # 5. Load statements
    statements: dict[str, StatementRecord] = {}
    if custom_statements is not None:
        for s in custom_statements:
            statements[s.id] = s
    else:
        stmt_dir = record_root / "statements"
        if stmt_dir.exists():
            for sf in sorted(stmt_dir.glob("*.json")):
                stmt = load_statement(sf)
                if stmt.id in statements:
                    raise BuildValidationError(f"Duplicate statement: {stmt.id}")
                statements[stmt.id] = stmt

    # 6. Load relationships
    relationships: dict[str, RelationshipRecord] = {}
    if custom_relationships is not None:
        for r in custom_relationships:
            relationships[r.id] = r
    else:
        rel_dir = record_root / "relationships"
        if rel_dir.exists():
            for rf in sorted(rel_dir.glob("*.json")):
                rel = load_relationship(rf)
                if rel.id in relationships:
                    raise BuildValidationError(f"Duplicate relationship: {rel.id}")
                relationships[rel.id] = rel

    # 7. Load corrections
    corrections: list[CorrectionRecord] = []
    corr_dir = record_root / "corrections"
    if corr_dir.exists():
        for cf in sorted(corr_dir.glob("*.json")):
            corrections.append(load_correction(cf))

    # Perform validation checks
    validation_errors: list[str] = []
    if production_records:
        for correction in corrections:
            validation_errors.extend(correction.validate(target_election_id=election_id))
            if correction.is_fixture:
                validation_errors.append(f"Correction '{correction.id}': production corrections cannot be fixtures.")
        for programme_file in sorted((record_root / "programmes").glob("*.json")):
            programme = load_programme(programme_file)
            validation_errors.extend(programme.validate(target_election_id=election_id))
            if programme.is_fixture:
                validation_errors.append("Production programmes cannot be fixtures.")

    # Filter statements for the target election and validate review status
    filtered_statements: dict[str, StatementRecord] = {}
    for stmt_id, stmt in statements.items():
        if stmt.election_id != election_id:
            if custom_statements is not None or production_records:
                validation_errors.append(f"Statement '{stmt.id}': explicit publish set has an election mismatch.")
            continue

        if election_id == "es-gen-2023" or production_records:
            # Repository drafts are audit material, outside the publish set.
            # Explicit caller-supplied drafts still fail strict publication checks.
            if stmt.review_status != "approved" and custom_statements is None and not production_records:
                continue
            validation_errors.extend(stmt.validate(target_election_id=election_id,
                                                   taxonomy=taxonomy if production_records else None))
            if stmt.review_status != "approved":
                validation_errors.append(f"Statement '{stmt.id}' has unreviewed status '{stmt.review_status}'.")
            if stmt.is_fixture:
                validation_errors.append(f"Statement '{stmt.id}': political pilot claims cannot be fixtures.")
            if production_records:
                for review in stmt.reviews:
                    validation_errors.extend(review.validate(require_human=True))
                    if review.content_sha256 != stmt.review_fingerprint():
                        validation_errors.append(f"Statement '{stmt.id}': human approval must bind to the current content hash.")
            sources = [s for s in register.sources if s.election_id == election_id and s.party_id == stmt.party_id
                       and s.version == stmt.source_version and stmt.source_url in (s.direct_url, s.official_url)]
            if len(sources) != 1:
                validation_errors.append(f"Statement '{stmt.id}': source URL/version must resolve to one election-scoped source.")
            else:
                src = sources[0]
                allowed_rights = PERMITTED_QUOTE_RIGHTS if stmt.quote is not None else PERMITTED_SUMMARY_RIGHTS
                if src.status != "verified" or src.rights_review.status not in allowed_rights:
                    validation_errors.append(f"Statement '{stmt.id}': source verification and applicable rights are not approved.")
                rights = src.rights_review
                validation_errors.extend(ReviewRecord(
                    rights.reviewed_by or "", rights.review_date or "", "approved", rights.terms_notes,
                ).validate())
                if PLACEHOLDER_REVIEWER_PATTERN.match(rights.reviewed_by or ""):
                    validation_errors.append(f"Statement '{stmt.id}': placeholder source rights reviewer cannot authorize publication.")
                if not rights.evidence_ref:
                    validation_errors.append(f"Statement '{stmt.id}': source-specific reuse decision requires an evidence reference.")
                if not rights.terms_notes.strip():
                    validation_errors.append(f"Statement '{stmt.id}': source-specific reuse decision requires its scope.")
                programme_path = record_root / "programmes"
                programmes = [json.loads(p.read_text()) for p in sorted(programme_path.glob("*.json"))]
                matches = [p for p in programmes if p.get("programme_id") == stmt.programme_id]
                if len(matches) != 1 or any(matches[0].get(k) != value for k, value in (
                    ("election_id", election_id), ("candidacy_id", stmt.party_id),
                    ("version", src.version), ("sha256", src.sha256),
                    ("status", "official"),
                    ("is_fixture", False),
                )):
                    validation_errors.append(f"Statement '{stmt.id}': programme provenance/hash/rights do not match its source.")
                elif matches[0].get("rights_status") != (
                    "verified_quotation_permitted" if src.rights_review.status in PERMITTED_QUOTE_RIGHTS
                    else "verified_link_only"
                ):
                    validation_errors.append(f"Statement '{stmt.id}': programme rights do not match the source decision.")
                elif not matches[0].get("publication_date") or not src.publication_date:
                    validation_errors.append(f"Statement '{stmt.id}': approved source and programme require publication dates.")
                elif matches[0]["publication_date"] != src.publication_date:
                    validation_errors.append(f"Statement '{stmt.id}': programme and source publication dates differ.")

        if strict_approved:
            # Rejection of unreviewed or draft statements
            if stmt.review_status != "approved":
                validation_errors.append(
                    f"Statement '{stmt.id}' has unreviewed status '{stmt.review_status}'. "
                    f"Only approved statements may enter the publish set."
                )

            if not (production_records and stmt.allows_single_review) and len({
                review.reviewer_id for review in stmt.reviews
            }) < 2:
                validation_errors.append(
                    f"Statement '{stmt.id}' violates Four-Eyes principle: "
                    f"must have at least 2 distinct reviewer IDs."
                )
            for review in stmt.reviews:
                if review.verdict != "approved":
                    validation_errors.append(
                        f"Statement '{stmt.id}' has non-approved review verdict '{review.verdict}'."
                    )

            # Topic taxonomy alignment
            allowed_topics = {t.id for t in taxonomy.topics} if production_records else set(CORE_TOPIC_IDS)
            if stmt.topic_id not in allowed_topics:
                validation_errors.append(
                    f"Statement '{stmt.id}' topic '{stmt.topic_id}' not in selected taxonomy {sorted(allowed_topics)}."
                )

            # Quotation constraints under Spanish Intellectual Property Law (TRLPI Art. 32)
            if stmt.quote:
                words = stmt.quote.split()
                if len(words) > MAX_QUOTE_WORDS:
                    validation_errors.append(
                        f"Statement '{stmt.id}' quote exceeds limit of {MAX_QUOTE_WORDS} words (has {len(words)} words)."
                    )
                if len(stmt.quote) > MAX_QUOTE_CHARS:
                    validation_errors.append(
                        f"Statement '{stmt.id}' quote exceeds limit of {MAX_QUOTE_CHARS} chars (has {len(stmt.quote)} chars)."
                    )
                if not (stmt.source_page or stmt.source_section):
                    validation_errors.append(
                        f"Statement '{stmt.id}' quote lacks exact locator (must specify source_page or source_section)."
                    )

        filtered_statements[stmt_id] = stmt

    # Filter and validate relationships
    filtered_relationships: dict[str, RelationshipRecord] = {}
    for rel_id, rel in relationships.items():
        if rel.election_id != election_id:
            if custom_relationships is not None or production_records:
                validation_errors.append(f"Relationship '{rel.id}': explicit publish set has an election mismatch.")
            continue

        if rel.status == "invalidated":
            # Exclude invalidated comparisons from active presentation
            continue

        if election_id == "es-gen-2023" or production_records:
            if rel.review_status != "approved" and custom_relationships is None and not production_records:
                continue
            validation_errors.extend(rel.validate(target_election_id=election_id, statements_by_id=filtered_statements,
                                                  for_build=True, taxonomy=taxonomy if production_records else None))
            if rel.is_fixture:
                validation_errors.append(f"Relationship '{rel.id}': political pilot comparisons cannot be fixtures.")
            if production_records:
                for review in rel.reviews:
                    validation_errors.extend(review.validate(require_human=True))

        if strict_approved:
            if rel.review_status != "approved":
                validation_errors.append(
                    f"Relationship '{rel.id}' has unapproved review_status '{rel.review_status}'."
                )

        # Cross-election check: make sure referenced statements belong to this election
        for sid in rel.statement_ids:
            if sid in statements:
                target_stmt = statements[sid]
                if target_stmt.election_id != election_id:
                    validation_errors.append(
                        f"Relationship '{rel.id}' mixes statements across elections: "
                        f"stmt '{sid}' belongs to '{target_stmt.election_id}', expected '{election_id}'."
                    )

        filtered_relationships[rel_id] = rel

    if validation_errors:
        err_msg = "\n  - ".join(validation_errors)
        raise BuildValidationError(f"Build validation failed with {len(validation_errors)} error(s):\n  - {err_msg}")

    templates_dir = root_dir / "site" / "templates"

    return SiteContext(
        root_dir=root_dir,
        content_dir=content_dir,
        election_id=election_id,
        canonical_base=canonical_base.rstrip("/"),
        build_date=resolved_date,
        taxonomy=taxonomy,
        register=register,
        parties=parties,
        statements=filtered_statements,
        relationships=filtered_relationships,
        corrections=corrections,
        i18n=i18n,
        templates_dir=templates_dir,
        production_records=production_records,
    )


# ==============================================================================
# HTML Rendering Helpers & Component Generators
# ==============================================================================

def preview_image_path(root_dir: Path) -> str:
    """Version the local preview asset for immutable serving caches."""
    image = root_dir / "site" / "assets" / "social-preview.png"
    return f"assets/social-preview-{compute_sha256(image)[:16]}.png"


def render_social_metadata(ctx: SiteContext, title: str, description: str, canonical_url: str) -> str:
    """Use page context only; never derive a party-pair claim from URL state."""
    pilot = ctx.election_id == "es-gen-2023"
    site_name = "Generales 2023 · Ensayo piloto privado" if pilot else ctx.i18n["meta"]["site_name"]
    notice = "Ensayo piloto privado de 2023." if pilot else "Vista previa · Datos de prueba."
    social_description = description if ctx.production_records else f"{notice} {description}"
    image_url = f"{ctx.canonical_base}/{preview_image_path(ctx.root_dir)}"
    properties = {
        "og:type": "website",
        "og:locale": "es_ES",
        "og:site_name": site_name,
        "og:title": title,
        "og:description": social_description,
        "og:url": canonical_url,
        "og:image": image_url,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": ctx.i18n["social_preview"]["image_alt"],
    }
    og_meta = "\n".join(
        f'  <meta property="{key}" content="{escape(value)}">'
        for key, value in properties.items()
    )
    twitter_tags = {
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": social_description,
        "twitter:image": image_url,
        "twitter:image:alt": ctx.i18n["social_preview"]["image_alt"],
    }
    tw_meta = "\n".join(
        f'  <meta name="{key}" content="{escape(value)}">'
        for key, value in twitter_tags.items()
    )
    return f"{og_meta}\n{tw_meta}"


def _clean_schema_data(obj: Any) -> Any:
    """Recursively strip None values from structured data objects."""
    if isinstance(obj, dict):
        return {k: _clean_schema_data(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_clean_schema_data(item) for item in obj if item is not None]
    return obj


def safe_json_ld(data: Any) -> str:
    """Serialize structured data to JSON-LD with strict HTML/XSS character escaping."""
    cleaned = _clean_schema_data(data)
    raw = json.dumps(cleaned, ensure_ascii=False, indent=2)
    escaped = raw.replace("<", r"\u003c").replace(">", r"\u003e").replace("&", r"\u0026")
    return f"""  <script type="application/ld+json">
{escaped}
  </script>"""


def build_structured_data(
    ctx: SiteContext,
    canonical_path: str,
    title: str,
    description: str,
    topic: Optional[Topic] = None,
    party: Optional[PartyInfo] = None,
) -> dict[str, Any]:
    """Build Schema.org JSON-LD graph tailored to each crawlable page route."""
    pilot = ctx.election_id == "es-gen-2023"
    canonical_url = f"{ctx.canonical_base}{canonical_path}"
    org_name = "Generales 2023 · Ensayo piloto privado" if pilot else ctx.i18n["meta"]["site_name"]
    org_desc = (
        "Ensayo técnico piloto de comparación de programas electorales para 2023."
        if pilot
        else "Proyecto cívico independiente para la comparación neutral de programas electorales en España con citas exactas."
    )
    logo_url = f"{ctx.canonical_base}/{preview_image_path(ctx.root_dir)}"

    org_node = {
        "@type": "Organization",
        "@id": f"{ctx.canonical_base}/#organization",
        "name": org_name,
        "url": f"{ctx.canonical_base}/",
        "logo": logo_url,
        "description": org_desc,
        "email": "editorial@elecciones2026.es",
        "publishingPrinciples": f"{ctx.canonical_base}/metodo/",
    }

    if canonical_path == "/":
        topics_items = [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": t.name_es,
                "url": f"{ctx.canonical_base}/temas/{t.id}/",
                "description": t.description_es,
            }
            for idx, t in enumerate(ctx.taxonomy.topics)
        ]
        parties_items = [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": p.display_name,
                "url": f"{ctx.canonical_base}/partidos/{pid}/",
            }
            for idx, (pid, p) in enumerate(sorted(ctx.parties.items()))
        ]
        website_node = {
            "@type": "WebSite",
            "@id": f"{ctx.canonical_base}/#website",
            "url": f"{ctx.canonical_base}/",
            "name": org_name,
            "description": description,
            "inLanguage": "es-ES",
            "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{ctx.canonical_base}/?topic={{topic}}&partyA={{partyA}}&partyB={{partyB}}",
                },
                "query-input": [
                    "name=topic",
                    "name=partyA",
                    "name=partyB",
                ],
            },
        }
        return {
            "@context": "https://schema.org",
            "@graph": [
                website_node,
                org_node,
                {
                    "@type": "ItemList",
                    "@id": f"{ctx.canonical_base}/#topics",
                    "name": "Temas de comparación electoral",
                    "itemListElement": topics_items,
                },
                {
                    "@type": "ItemList",
                    "@id": f"{ctx.canonical_base}/#parties",
                    "name": "Candidaturas electorales analizadas",
                    "itemListElement": parties_items,
                },
            ],
        }

    breadcrumbs: list[dict[str, Any]] = [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": f"{ctx.canonical_base}/"}
    ]

    if canonical_path == "/temas/":
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Temas", "item": canonical_url})
        topics_items = [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": t.name_es,
                "url": f"{ctx.canonical_base}/temas/{t.id}/",
                "description": t.description_es,
            }
            for idx, t in enumerate(ctx.taxonomy.topics)
        ]
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                {
                    "@type": "CollectionPage",
                    "@id": f"{canonical_url}#page",
                    "url": canonical_url,
                    "name": title,
                    "description": description,
                    "inLanguage": "es-ES",
                    "dateModified": ctx.build_date,
                    "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
                    "mainEntity": {
                        "@type": "ItemList",
                        "itemListElement": topics_items,
                    },
                },
            ],
        }

    if canonical_path.startswith("/temas/") and topic:
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Temas", "item": f"{ctx.canonical_base}/temas/"})
        breadcrumbs.append({"@type": "ListItem", "position": 3, "name": topic.name_es, "item": canonical_url})
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                {
                    "@type": "ItemPage",
                    "@id": f"{canonical_url}#page",
                    "url": canonical_url,
                    "name": title,
                    "description": description,
                    "inLanguage": "es-ES",
                    "dateModified": ctx.build_date,
                    "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
                    "about": {
                        "@type": "Thing",
                        "name": topic.name_es,
                        "description": topic.description_es,
                    },
                },
            ],
        }

    if canonical_path == "/partidos/":
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Candidaturas", "item": canonical_url})
        parties_items = [
            {
                "@type": "ListItem",
                "position": idx + 1,
                "name": p.display_name,
                "url": f"{ctx.canonical_base}/partidos/{pid}/",
            }
            for idx, (pid, p) in enumerate(sorted(ctx.parties.items()))
        ]
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                {
                    "@type": "CollectionPage",
                    "@id": f"{canonical_url}#page",
                    "url": canonical_url,
                    "name": title,
                    "description": description,
                    "inLanguage": "es-ES",
                    "dateModified": ctx.build_date,
                    "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
                    "mainEntity": {
                        "@type": "ItemList",
                        "itemListElement": parties_items,
                    },
                },
            ],
        }

    if canonical_path.startswith("/partidos/") and party:
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Candidaturas", "item": f"{ctx.canonical_base}/partidos/"})
        breadcrumbs.append({"@type": "ListItem", "position": 3, "name": party.display_name, "item": canonical_url})
        party_entity: dict[str, Any] = {
            "@type": "PoliticalParty",
            "name": party.display_name,
            "legalName": party.official_name,
            "alternateName": party.short_name,
        }
        if ctx.production_records and party.inclusion_criterion == "pending_verification":
            party_entity.pop("legalName")
        src = next((s for s in ctx.register.sources if s.party_id == party.id and s.election_id == ctx.election_id), None)
        citations = []
        if src and src.official_url:
            citations.append({
                "@type": "CreativeWork",
                "name": f"Documento registrado de {party.display_name}" if ctx.production_records and src.status != "verified" else f"Programa electoral {party.display_name}",
                "url": src.official_url,
                "version": src.version,
                "identifier": src.sha256 if src.sha256 else None,
            })
        page_node: dict[str, Any] = {
            "@type": "ItemPage",
            "@id": f"{canonical_url}#page",
            "url": canonical_url,
            "name": title,
            "description": description,
            "inLanguage": "es-ES",
            "dateModified": ctx.build_date,
            "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
            "about": party_entity,
        }
        if citations:
            page_node["citation"] = citations
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                page_node,
            ],
        }

    if canonical_path == "/metodo/":
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Metodología", "item": canonical_url})
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                {
                    "@type": "AboutPage",
                    "@id": f"{canonical_url}#page",
                    "url": canonical_url,
                    "name": title,
                    "description": description,
                    "inLanguage": "es-ES",
                    "dateModified": ctx.build_date,
                    "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
                },
            ],
        }

    if canonical_path == "/fuentes/":
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Fuentes", "item": canonical_url})
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                {
                    "@type": "Dataset",
                    "@id": f"{canonical_url}#dataset",
                    "url": canonical_url,
                    "name": title,
                    "description": description,
                    "inLanguage": "es-ES",
                    "dateModified": ctx.build_date,
                    "license": "https://www.boe.es/buscar/act.php?id=BOE-A-1996-8930",
                    "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
                },
            ],
        }

    if canonical_path == "/correcciones/":
        breadcrumbs.append({"@type": "ListItem", "position": 2, "name": "Registro de correcciones", "item": canonical_url})
        return {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "BreadcrumbList", "itemListElement": breadcrumbs},
                org_node,
                {
                    "@type": "AboutPage",
                    "@id": f"{canonical_url}#page",
                    "url": canonical_url,
                    "name": title,
                    "description": description,
                    "inLanguage": "es-ES",
                    "dateModified": ctx.build_date,
                    "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
                },
            ],
        }

    return {
        "@context": "https://schema.org",
        "@graph": [
            org_node,
            {
                "@type": "WebPage",
                "@id": f"{canonical_url}#page",
                "url": canonical_url,
                "name": title,
                "description": description,
                "inLanguage": "es-ES",
                "dateModified": ctx.build_date,
                "publisher": {"@id": f"{ctx.canonical_base}/#organization"},
            },
        ],
    }


def render_preview_banner(text: str) -> str:
    """Render a preview notice."""
    return f"""  <aside class="preview-banner" role="status" aria-label="Aviso de prototipo">
    {escape(text)}
  </aside>"""


def render_status_badge(ctx: SiteContext, status: str) -> str:
    """Render lifecycle status badge."""
    key = "official" if status == "verified" else status.replace("-", "_")
    label = ctx.i18n["status_badges"].get(key, "Estado pendiente de revisión")
    badge_class = f"status-badge status-badge-{escape(status)}"
    return f'<span class="{badge_class}">{escape(label)}</span>'


def rights_status_label(status: str) -> str:
    """Describe source reuse accurately in Spanish without implying publication."""
    return {
        "not_reviewed": "Uso pendiente de revisión",
        "link_only": "Solo resúmenes y enlaces; sin citas",
        "link_and_short_quote": "Enlaces y citas breves autorizadas",
        "public_domain": "Dominio público verificado",
        "permission_denied": "Uso no autorizado",
    }.get(status, "Uso pendiente de revisión")


def render_caveat(ctx: SiteContext, qualification: str) -> str:
    """Render qualification note."""
    label = escape(ctx.i18n["statement"]["caveat_label"])
    text = escape(qualification)
    return f"""<div class="party-caveat" role="note" aria-label="Matiz registrado">
                <strong>{label}</strong> {text}
              </div>"""


def statement_source_url(ctx: SiteContext, stmt: StatementRecord) -> Optional[str]:
    """Open the first physical PDF page while retaining the full visible locator."""
    link = stmt.source_url
    if ctx.production_records:
        link = next(
            (source.archived_url for source in ctx.register.sources
             if source.archived_url and source.election_id == stmt.election_id
             and source.party_id == stmt.party_id and source.version == stmt.source_version
             and link in (source.direct_url, source.official_url)),
            link,
        )
    if link and stmt.source_page and "#" not in link:
        first_page = re.match(r"^[1-9]\d*", stmt.source_page)
        if first_page:
            link += f"#page={first_page.group()}"
    return link


def render_source_citation(ctx: SiteContext, stmt: StatementRecord) -> str:
    """Render source citation link or missing note."""
    if stmt.statement_type == "not_found" or not stmt.source_url:
        return f"""<span class="source-citation">
                <span aria-hidden="true">↗</span> Fuente: <em>{escape(ctx.i18n['statement']['source_pending'])}</em>
              </span>"""

    locators = []
    if stmt.source_version:
        locators.append(f"v{stmt.source_version}")
    if stmt.source_page:
        locators.append(f"{ctx.i18n['statement']['page']} {stmt.source_page}")
    if stmt.source_section:
        locators.append(f"{ctx.i18n['statement']['section']} {stmt.source_section}")
    locator_text = " · ".join(locators) if locators else "Programa oficial"

    url = escape(statement_source_url(ctx, stmt))
    sr_notice = escape(ctx.i18n["statement"]["opens_new_window"])
    return f"""<a class="source-citation" href="{url}" target="_blank" rel="noopener noreferrer">
                <span aria-hidden="true">↗</span> Fuente: <span>{escape(locator_text)}</span>
                <span class="sr-only">{sr_notice}</span>
              </a>"""


def format_date_spanish(date_str: str) -> str:
    """Format an ISO date string (YYYY-MM-DD) into natural Spanish (e.g. 9 de octubre de 2026)."""
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    try:
        parts = date_str.strip().split("-")
        if len(parts) == 3:
            year, month_idx, day = int(parts[0]), int(parts[1]), int(parts[2])
            if 1 <= month_idx <= 12:
                return f"{day} de {months[month_idx - 1]} de {year}"
    except (ValueError, IndexError):
        pass
    return date_str


def render_source_coverage_card(ctx: SiteContext, src: SourceRecord) -> str:
    """Render a mobile-first single-column card for a source record (Package E2.4)."""
    badge = render_status_badge(ctx, src.status)
    retrieval_date = escape(src.retrieval_date) if src.retrieval_date else "Pendiente"
    version = escape(src.version) if src.version else "—"
    hash_code = f"<code>{src.sha256[:12]}...</code>" if src.sha256 else "—"
    rights = escape(rights_status_label(src.rights_review.status)) if src.rights_review else "Uso pendiente de revisión"

    if src.official_url:
        link_html = f'<a href="{escape(src.official_url)}" class="source-citation" target="_blank" rel="noopener noreferrer"><span>Enlace oficial</span> <span aria-hidden="true">↗</span> <span class="sr-only">(se abre en una ventana nueva)</span></a>'
    else:
        link_html = '<span class="source-date"><em>Enlace no disponible</em></span>'

    return f"""<article class="coverage-card">
      <div class="coverage-card-header">
        <h3 class="coverage-party-name">{escape(src.publisher)}</h3>
        {badge}
      </div>
      <div class="coverage-card-body">
        <div class="coverage-meta-row">
          <span class="coverage-meta-label">Denominación:</span>
          <span class="coverage-meta-value">{escape(src.candidature_name)}</span>
        </div>
        <div class="coverage-meta-row">
          <span class="coverage-meta-label">Versión:</span>
          <span class="coverage-meta-value">{version}</span>
        </div>
        <div class="coverage-meta-row">
          <span class="coverage-meta-label">Fecha consulta:</span>
          <time class="coverage-meta-value" datetime="{retrieval_date}">{retrieval_date}</time>
        </div>
        <div class="coverage-meta-row">
          <span class="coverage-meta-label">SHA-256:</span>
          <span class="coverage-meta-value">{hash_code}</span>
        </div>
        <div class="coverage-meta-row">
          <span class="coverage-meta-label">Uso autorizado:</span>
          <span class="coverage-meta-value">{rights}</span>
        </div>
      </div>
      <div class="coverage-card-footer">
        {link_html}
      </div>
    </article>"""


def render_party_card(
    ctx: SiteContext,
    stmt: Optional[StatementRecord],
    party_id: str,
    party_letter: str = "A",
) -> str:
    """Render Party Position Card complying with component plan."""
    party = ctx.parties.get(party_id)
    party_name = party.display_name if party else party_id
    pill_class = f"party-pill party-pill-{party_letter.lower()}"
    card_class = f"party-card party-card-{party_letter.lower()}"

    if stmt is None:
        card_class += " party-card-missing"
        status_badge = '<span class="status-badge status-badge-missing">Contenido pendiente de publicación</span>'
        statement_text = "El contenido de esta medida está pendiente de publicación."
        expl = "La falta de contenido aprobado no debe interpretarse como oposición ni como apoyo."
        source_footer = '<span class="source-citation-text text-muted">Contenido pendiente de publicación</span>'

        return f"""<article class="{card_class}" aria-labelledby="party-{party_letter.lower()}-name">
            <div class="party-card-header">
              <span class="{pill_class}" aria-hidden="true">{party_letter}</span>
              <div class="party-card-meta">
                <h4 id="party-{party_letter.lower()}-name" class="party-name">{escape(party_name)}</h4>
                {status_badge}
              </div>
            </div>
            <div class="party-card-body">
              <p class="party-statement party-statement-missing">{escape(statement_text)}</p>
              <p class="missing-explanation">{escape(expl)}</p>
            </div>
            <div class="party-card-footer">
              {source_footer}
            </div>
          </article>"""

    # Normal position
    status_badge = ('<span class="status-badge status-badge-missing">No consta en el programa</span>'
                    if stmt.statement_type == "not_found" else render_status_badge(ctx, "official"))
    caveats_html = "".join(render_caveat(ctx, q) for q in stmt.qualifications)
    if stmt.statement_type == "not_found":
        card_class += " party-card-missing"
        caveats_html += f'<p class="missing-explanation">{escape(ctx.i18n["statement"]["not_found_explanation"])}</p>'
    citation_html = render_source_citation(ctx, stmt)
    rev_date = stmt.last_reviewed_date or ctx.build_date

    quote_html = ""
    if stmt.quote:
        caveats_json = escape(json.dumps(stmt.qualifications or []))
        quote_html = f"""<div class="party-quote-wrapper">
                <span class="party-quote-label">Extracto literal del programa:</span>
                <blockquote class="party-quote"><p>«{escape(stmt.quote)}»</p></blockquote>
                <button type="button" class="btn-open-manifesto"
                  data-party-name="{escape(party_name)}"
                  data-party-pill="{escape(party_letter)}"
                  data-party-pill-class="{escape(pill_class)}"
                  data-status-label="Programa oficial"
                  data-source="{escape(stmt.source_version or 'Programa oficial')}"
                  data-section="{escape(' · '.join(filter(None, [f'pág. {stmt.source_page}' if stmt.source_page else '', stmt.source_section])))}"
                  data-instrument="{escape(stmt.policy_instrument or '')}"
                  data-quote="{escape(stmt.quote)}"
                  data-caveats="{caveats_json}"
                  data-source-url="{escape(stmt.source_url or '')}"
                  aria-haspopup="dialog">
                  <span aria-hidden="true">📖</span>
                  <span>Leer extracto</span>
                </button>
              </div>"""

    return f"""<article class="{card_class}" data-statement-id="{escape(stmt.id)}" aria-labelledby="party-{party_letter.lower()}-name">
            <div class="party-card-header">
              <span class="{pill_class}" aria-hidden="true">{party_letter}</span>
              <div class="party-card-meta">
                <h4 id="party-{party_letter.lower()}-name" class="party-name">{escape(party_name)}</h4>
                {status_badge}
              </div>
            </div>
            <div class="party-card-body">
              <p class="party-statement">{escape(stmt.summary)}</p>
              {quote_html}
              {caveats_html}
            </div>
            <div class="party-card-footer">
              {citation_html}
              <time class="source-date" datetime="{escape(rev_date)}">Rev. {escape(rev_date)}</time>
            </div>
          </article>"""


def render_base(
    ctx: SiteContext,
    title: str,
    description: str,
    canonical_path: str,
    content: str,
    root_path: str = "./",
    structured_data: Optional[dict[str, Any]] = None,
) -> str:
    """Render outer HTML frame with base layout."""
    canonical_url = f"{ctx.canonical_base}{canonical_path}"
    base_template_file = ctx.templates_dir / "base.html"

    if structured_data is None:
        structured_data = build_structured_data(
            ctx=ctx,
            canonical_path=canonical_path,
            title=title,
            description=description,
        )
    structured_data_html = safe_json_ld(structured_data)

    preview_banner = ""
    if ctx.election_id == "es-gen-2023":
        brand_link = f"""<a class="brand" href="{root_path}" aria-label="Generales 2023 - Ensayo Piloto">
        <span class="brand-mark" aria-hidden="true">■</span>
        <span class="brand-text">Generales<span class="brand-year">2023</span></span>
        <span class="pilot-badge">Privado</span>
      </a>"""
        preview_banner = render_preview_banner(
            "ENSAYO PILOTO PRIVADO · Cobertura parcial"
            if ctx.statements else "ENSAYO PILOTO PRIVADO · Publicación pendiente"
        )
        footer_org = "Generales 2023 (piloto) · Ensayo privado y confidencial"
        footer_values = ("Posiciones visibles verificadas · No satisface G2 para 2026"
                         if ctx.statements else
                         "Revisión humana y de derechos pendiente · No satisface G2 para 2026")
        nav_feedback_link = ""
        topbar_quiz_link = ""
        topbar_budget_link = ""
        menu_budget_link = ""
        if "Generales 2023" not in title:
            title = f"{title} · Generales 2023"
    else:
        brand_link = f"""<a class="brand" href="{root_path}" aria-label="Elecciones 2026 - Inicio">
        <span class="brand-mark" aria-hidden="true">■</span>
        <span class="brand-text">Elecciones<span class="brand-year">2026</span></span>
      </a>"""
        if not ctx.production_records:
            notice = ctx.i18n["preview_banner"]
            preview_banner = render_preview_banner(f"{notice['badge']} · {notice['text']}")
        footer_org = escape(ctx.i18n["footer"]["org"])
        footer_values = escape(ctx.i18n["footer"]["values"])
        feedback_label = escape(ctx.i18n.get("feedback", {}).get("link_text", "Buzón de propuestas"))
        nav_feedback_link = f'\n        <a class="nav-link" href="{root_path}propuestas/">{feedback_label}</a>'
        quiz_label = escape(ctx.i18n["nav"].get("quiz", "Cuestionario"))
        topbar_quiz_link = f'\n        <a class="nav-link" href="{root_path}cuestionario/">{quiz_label}</a>'
        budget_label = escape(ctx.i18n["nav"].get("budget", "Presupuestos"))
        topbar_budget_link = f'\n        <a class="nav-link nav-link-budget" href="{root_path}presupuestos/2023/">{budget_label}</a>'
        menu_budget_link = f'\n        <a class="nav-link" href="{root_path}presupuestos/2023/">{budget_label}</a>'

    if base_template_file.exists():
        template = base_template_file.read_text(encoding="utf-8")
    else:
        template = """<!doctype html>
<html lang="{{ lang }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <meta name="description" content="{{ description }}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <title>{{ title }}</title>
  <link rel="canonical" href="{{ canonical_url }}">
  <link rel="alternate" hreflang="es" href="{{ canonical_url }}">
  <link rel="alternate" hreflang="x-default" href="{{ canonical_url }}">
  <link rel="alternate" type="text/markdown" href="{{ root_path }}llms.txt" title="Documentación para LLMs">
{{ social_metadata }}
{{ structured_data }}
  <link rel="stylesheet" href="{{ root_path }}styles.css">
</head>
<body class="theme-swiss" data-election="{{ election_id }}" data-swiss-accent="monochrome">
  <a class="skip-link" href="#contenido">{{ skip_to_content }}</a>
{{ preview_banner }}
  <header class="topbar" role="banner">
    <div class="topbar-inner">
      {{ brand_link }}
      <nav class="nav-links" aria-label="Navegación principal">
        <a class="nav-link" href="{{ root_path }}#comparador">{{ nav_comparator }}</a>{{ topbar_quiz_link }}
        <a class="nav-link" href="{{ root_path }}temas/">{{ nav_topics }}</a>{{ topbar_budget_link }}
        <details class="site-menu">
          <summary class="nav-link menu-toggle">Menú <span aria-hidden="true">+</span></summary>
          <div class="menu-links">{{ menu_budget_link }}
        <a class="nav-link" href="{{ root_path }}cuestionario/">{{ nav_quiz }}</a>
        <a class="nav-link" href="{{ root_path }}partidos/">{{ nav_parties }}</a>
        <a class="nav-link" href="{{ root_path }}metodo/">{{ nav_methodology }}</a>
        <a class="nav-link" href="{{ root_path }}fuentes/">{{ nav_sources }}</a>
        <a class="nav-link" href="{{ root_path }}correcciones/">{{ nav_corrections }}</a>{{ nav_feedback_link }}
          </div>
        </details>
      </nav>
    </div>
  </header>
  <main id="contenido">
{{ content }}
  </main>
  <footer>
    <div class="footer-inner">
      <span>{{ footer_org }}</span>
      <span>{{ footer_values }}</span>
      <span>Desarrollado por <a href="https://github.com/barnolacesc" rel="noopener noreferrer">barnolacesc</a> · <a href="https://github.com/barnolacesc/elecciones2026" rel="noopener noreferrer">Código en GitHub</a></span>
    </div>
  </footer>
  <script src="{{ root_path }}pagination.js" defer></script>
</body>
</html>"""

    replacements = {
        "{{ lang }}": ctx.i18n["meta"]["language"],
        "{{ title }}": escape(title),
        "{{ description }}": escape(description),
        "{{ canonical_url }}": escape(canonical_url),
        "{{ social_metadata }}": render_social_metadata(ctx, title, description, canonical_url),
        "{{ structured_data }}": structured_data_html,
        "{{ root_path }}": root_path,
        "{{ brand_link }}": brand_link,
        "{{ skip_to_content }}": escape(ctx.i18n["nav"]["skip_to_content"]),
        "{{ preview_banner }}": preview_banner,
        "{{ nav_comparator }}": escape(ctx.i18n["nav"]["comparator"]),
        "{{ nav_topics }}": escape(ctx.i18n["nav"]["topics"]),
        "{{ nav_budget }}": escape(ctx.i18n["nav"].get("budget", "Presupuestos")),
        "{{ nav_quiz }}": escape(ctx.i18n["nav"].get("quiz", "Cuestionario")),
        "{{ nav_parties }}": escape(ctx.i18n["nav"]["parties"]),
        "{{ nav_methodology }}": escape(ctx.i18n["nav"]["methodology"]),
        "{{ nav_sources }}": escape(ctx.i18n["nav"]["sources"]),
        "{{ nav_correcciones }}": escape(ctx.i18n["nav"]["corrections"]),
        "{{ nav_corrections }}": escape(ctx.i18n["nav"]["corrections"]),
        "{{ nav_feedback }}": escape(ctx.i18n.get("feedback", {}).get("link_text", "Buzón de propuestas")),
        "{{ nav_feedback_link }}": nav_feedback_link,
        "{{ topbar_quiz_link }}": topbar_quiz_link,
        "{{ topbar_budget_link }}": topbar_budget_link,
        "{{ menu_budget_link }}": menu_budget_link,
        "{{ footer_org }}": footer_org,
        "{{ footer_values }}": footer_values,
        "{{ content }}": content,
        "{{ election_id }}": ctx.election_id,
    }

    result = template
    for placeholder, val in replacements.items():
        result = result.replace(placeholder, val)
    if ctx.budget_payload is not None:
        from elecciones2026.budget_view import stylesheet_path
        result = result.replace('</head>', f'<link rel="stylesheet" href="{root_path}{stylesheet_path(ctx.root_dir / "site")}">\n</head>')
    return result


# ==============================================================================
# Page Renderers
# ==============================================================================

def render_share_controls(ctx: SiteContext) -> str:
    """Render one accessible share control and an explicit copy fallback."""
    return f"""        <div class="share-section">
          <button type="button" class="btn-share" id="share-button">
            <span aria-hidden="true">🔗</span>
            <span>{escape(ctx.i18n['share']['button_text'])}</span>
          </button>
          <div id="share-feedback" class="sr-only" role="status" aria-live="polite"></div>
          <div id="share-fallback" hidden>
            <label for="share-link">{escape(ctx.i18n['share']['link_label'])}</label>
            <input id="share-link" class="control-select" type="url" readonly>
            <button id="copy-link-button" class="btn-share" type="button">{escape(ctx.i18n['share']['copy_button'])}</button>
          </div>
        </div>"""


def render_budget_context(ctx: SiteContext, topic_id: str, root_path: str, comparison: bool = False) -> str:
    """Render one shared topic region; absent bundles add no mandatory payload."""
    if ctx.budget_payload is None:
        return ""
    from elecciones2026.budget_view import render_context, topic_projection
    projection = topic_projection(ctx.budget_payload, ctx.budget_manifest, topic_id)
    attributes = (f'id="budget-context" data-topic="{escape(topic_id)}" '
                  f'data-base="{root_path}static/budget-topics/{ctx.budget_projection_id}/" '
                  f'data-budget-url="{root_path}presupuestos/2023/"') if comparison else ''
    return f'<section class="budget-context" {attributes} aria-label="Contexto presupuestario oficial">' + render_context(projection, root_path + 'presupuestos/2023/') + '</section>'


def build_comparison_payload(ctx: SiteContext) -> dict[str, Any]:
    """Project the validated HTML publish set; never load drafts or source bytes."""
    errors = []
    for stmt in ctx.statements.values():
        errors.extend(stmt.validate(target_election_id=ctx.election_id,
                                    taxonomy=ctx.taxonomy if ctx.production_records else None))
        if stmt.review_status != "approved":
            errors.append(f"Statement '{stmt.id}': only approved records may enter browser output.")
        if stmt.party_id not in ctx.parties:
            errors.append(f"Statement '{stmt.id}': unknown party.")
        if stmt.source_url:
            try:
                url = urlsplit(stmt.source_url)
                _ = url.port
                unsafe = (url.scheme not in {"https", "http"} or not url.hostname
                          or url.username is not None or url.password is not None
                          or "\\" in stmt.source_url
                          or any(ord(char) <= 32 or ord(char) == 127 for char in stmt.source_url))
            except ValueError:
                unsafe = True
            if unsafe:
                errors.append(f"Statement '{stmt.id}': source URL must be absolute HTTP(S) without credentials or unsafe characters.")
    for rel in ctx.relationships.values():
        errors.extend(rel.validate(target_election_id=ctx.election_id,
                                   statements_by_id=ctx.statements, for_build=True,
                                   taxonomy=ctx.taxonomy if ctx.production_records else None))
        if any(pid not in ctx.parties for pid in rel.party_ids):
            errors.append(f"Relationship '{rel.id}': unknown party.")
        targets = [ctx.statements[sid] for sid in rel.statement_ids if sid in ctx.statements]
        if (len({stmt.party_id for stmt in targets}) != len(targets)
                or any(stmt.party_id not in rel.party_ids or stmt.topic_id != rel.topic_id
                       or stmt.subtopic_id != rel.subtopic_id for stmt in targets)):
            errors.append(f"Relationship '{rel.id}': statement party/topic scope does not match its measure.")
    if errors:
        raise BuildValidationError("Comparison publication failed:\n  - " + "\n  - ".join(errors))

    topics = {t.id: {"id": t.id, "name": t.name_es, "description": t.description_es}
              for t in ctx.taxonomy.topics}
    sources = {src.party_id: src for src in ctx.register.sources
               if src.election_id == ctx.election_id and src.status != "replaced"}
    parties = {pid: {"id": pid, "name": p.display_name, "shortName": p.short_name,
                     "electionId": ctx.election_id, "isFixture": p.is_fixture,
                     "coverage": sources[pid].status if pid in sources else "missing"}
               for pid, p in sorted(ctx.parties.items())}
    measures = {tid: [] for tid in topics}

    def position(stmt: StatementRecord) -> dict[str, Any]:
        locators = [f"v{stmt.source_version}"] if stmt.source_version else []
        if stmt.source_page:
            locators.append(f"{ctx.i18n['statement']['page']} {stmt.source_page}")
        if stmt.source_section:
            locators.append(f"{ctx.i18n['statement']['section']} {stmt.source_section}")
        locator = " · ".join(locators)
        link = statement_source_url(ctx, stmt)
        return {"statementId": stmt.id, "electionId": stmt.election_id,
                "programmeId": stmt.programme_id, "sourceVersion": stmt.source_version,
                "sourcePage": stmt.source_page, "sourceSection": stmt.source_section,
                "status": "missing" if stmt.statement_type == "not_found" else "official",
                "statusLabel": "No consta en el programa" if stmt.statement_type == "not_found" else "Propuesta revisada",
                "statement": stmt.summary, "quote": stmt.quote,
                "policyInstrument": stmt.policy_instrument, "section": locator,
                "qualifications": stmt.qualifications,
                "source": locator, "sourceUrl": link,
                "date": stmt.last_reviewed_date or ctx.build_date}

    referenced = set()
    for rel in sorted(ctx.relationships.values(), key=lambda r: r.id):
        positions = {ctx.statements[sid].party_id: position(ctx.statements[sid])
                     for sid in rel.statement_ids}
        referenced.update(rel.statement_ids)
        measures[rel.topic_id].append({
            "id": rel.id, "electionId": ctx.election_id, "title": rel.measure_label,
            "summary": "", "positions": positions,
            "relationships": {":".join(rel.party_ids): {
                "relationshipId": rel.id, "statementIds": rel.statement_ids,
                "type": rel.relationship_type,
                "typeLabel": ctx.i18n["relationship_badges"].get(rel.relationship_type, rel.relationship_type),
                "icon": {"agreement": "✓", "divergence": "≠"}.get(rel.relationship_type, "—"),
                "summary": rel.summary, "differences": rel.differences,
            }},
        })
    for stmt in sorted(ctx.statements.values(), key=lambda s: s.id):
        if stmt.id not in referenced:
            measures[stmt.topic_id].append({
                "id": stmt.id, "electionId": ctx.election_id,
                "title": stmt.policy_instrument or topics[stmt.topic_id]["name"],
                "summary": "", "positions": {stmt.party_id: position(stmt)}, "relationships": {},
            })
    return {"version": 1, "electionId": ctx.election_id, "buildDate": ctx.build_date,
            "productionRecords": ctx.production_records,
            "topics": topics, "parties": parties, "measuresByTopic": measures}


def comparison_bundle_script(ctx: SiteContext) -> str:
    """Store inert strings in a local script with deterministic content and escaping."""
    encoded = json.dumps(build_comparison_payload(ctx), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    literal = json.dumps(encoded, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return f"window.ComparisonData = JSON.parse({literal});\n"


def comparison_bundle_name(ctx: SiteContext) -> str:
    digest = hashlib.sha256(comparison_bundle_script(ctx).encode()).hexdigest()[:16]
    return f"comparison-data.{digest}.js"


def render_independent_proposals(ctx: SiteContext, parties: dict[str, Any],
                                 measures: list[dict[str, Any]], party_a: str, party_b: str,
                                 *, has_linked_measures: bool) -> str:
    sections = []
    for letter, pid in (("A", party_a), ("B", party_b)):
        positions = [m["positions"][pid] for m in measures if pid in m["positions"]]
        title_id = f"proposal-list-{letter.lower()}"
        name = escape(parties[pid]["name"])
        count = len(positions)
        label = "1 ficha revisada" if count == 1 else f"{count} fichas revisadas"
        cards = []
        for index, position in enumerate(positions, 1):
            card = render_party_card(ctx, ctx.statements[position["statementId"]], pid, letter)
            cards.append(card.replace(f'party-{letter.lower()}-name', f'independent-{letter.lower()}-{index}-name'))
        if not positions:
            message = ("No hay otras fichas revisadas en este tema." if has_linked_measures
                       else "No hay fichas revisadas en este tema.")
            if parties[pid]["coverage"] == "partial":
                message = "El documento de campaña es parcial."
            cards.append(f'<p class="notice">{message}</p>')
        else:
            cards = [
                f'<div class="proposal-list-cards" data-paginate="5" data-paginate-item-name="propuestas" '
                f'data-paginate-label="Paginación de propuestas de {name}">{"".join(cards)}</div>'
            ]
        sections.append(
            f'<section class="proposal-list" aria-labelledby="{title_id}">'
            f'<h3 id="{title_id}">{name}</h3>'
            f'<p class="proposal-count">{label}</p>'
            f'<a class="action-link" href="./partidos/{escape(pid)}/">Consultar programa y cobertura</a>'
            f'{"".join(cards)}</section>'
        )
    return f'<div class="measure-cards proposal-lists">{"".join(sections)}</div>'


def render_comparison_measures(ctx: SiteContext, payload: dict[str, Any], topic_id: str,
                               party_a: str, party_b: str) -> str:
    """Render the same record projection that the browser uses, without inferred links."""
    measures = [m for m in payload["measuresByTopic"][topic_id]
                if party_a in m["positions"] or party_b in m["positions"]]
    independent = ""
    if payload["productionRecords"]:
        pair_keys = (f"{party_a}:{party_b}", f"{party_b}:{party_a}")
        linked = [m for m in measures if any(key in m["relationships"] for key in pair_keys)]
        standalone = [m for m in measures if not any(key in m["relationships"] for key in pair_keys)]
        if standalone or not linked:
            independent = render_independent_proposals(
                ctx, payload["parties"], standalone, party_a, party_b, has_linked_measures=bool(linked))
        measures = linked
    if not measures:
        if independent:
            return independent
        return '<div class="empty-measures" role="status" aria-live="polite"><h4>Contenido pendiente de publicación</h4><p>El contenido para estas candidaturas está pendiente de publicación.</p><p>La falta de contenido aprobado no indica que el programa carezca de propuestas. No implica apoyo ni oposición.</p><a class="action-link" href="./metodo/">Consultar cobertura y método</a></div>'
    output = []
    for idx, measure in enumerate(measures, 1):
        cards = []
        for letter, pid in (("A", party_a), ("B", party_b)):
            pos = measure["positions"].get(pid)
            if pos:
                card = render_party_card(ctx, ctx.statements[pos["statementId"]], pid, letter)
                # Several groups can contain the same party; give each heading a unique ID.
                card = card.replace(f'party-{letter.lower()}-name', f'party-{letter.lower()}-{idx}-name')
            else:
                card = f'<article class="party-card party-card-missing"><h4 class="party-name">{escape(ctx.parties[pid].display_name)}</h4><span class="status-badge status-badge-missing">Contenido pendiente de publicación</span><p class="party-statement">El contenido de esta medida está pendiente de publicación.</p><p class="missing-explanation">La falta de contenido aprobado no debe interpretarse como oposición ni como apoyo.</p></article>'
            cards.append(card)
        rel = measure["relationships"].get(f"{party_a}:{party_b}") or measure["relationships"].get(f"{party_b}:{party_a}")
        rel_type = rel["type"] if rel else "not-found"
        if rel_type not in {"agreement", "divergence", "qualification", "partial_overlap"}:
            rel_type = "not-found"
        if rel_type == "partial_overlap":
            rel_type = "qualification"
        label = rel["typeLabel"] if rel else "Comparación pendiente de revisión"
        summary = rel["summary"] if rel else "No consta una relación revisada entre las candidaturas seleccionadas. La falta de contenido aprobado no implica apoyo ni oposición."
        differences = '<ul class="analysis-differences">' + ''.join(f'<li>{escape(d)}</li>' for d in rel["differences"]) + '</ul>' if rel and rel["differences"] else ""
        output.append(f'<article class="measure-group" aria-labelledby="measure-{idx}-title"><div class="measure-head"><p class="measure-topic-label">TEMA: {escape(payload["topics"][topic_id]["name"].upper())}</p><h3 id="measure-{idx}-title" class="measure-title">{escape(measure["title"])}</h3><p class="measure-summary">{escape(measure["summary"])}</p></div><div class="measure-cards">{"".join(cards)}</div><aside class="analysis-callout rel-callout-{rel_type}" aria-label="Lectura comparada"><h4>{escape(label)}</h4><p>{escape(summary)}</p>{differences}</aside></article>')
    return "\n".join([*output, independent]) if independent else "\n".join(output)


def render_home_page(ctx: SiteContext) -> str:
    """Render index.html with accessible comparator and static fallback."""
    # Find sample active comparison
    if ctx.election_id == "es-gen-2023":
        active_rel = (
            ctx.relationships.get("rel-pilot-2023-housing-pp-erc-divergence")
            or next((r for r in sorted(ctx.relationships.values(), key=lambda r: r.id) if r.status == "active"), None)
        )
        party_a_id = active_rel.party_ids[0] if active_rel else "pp"
        party_b_id = active_rel.party_ids[1] if active_rel and len(active_rel.party_ids) > 1 else "erc"
        hero_eyebrow = "GENERALES 2023 · 23 JULIO 2023"
        hero_title_part1 = "Compara los programas"
        hero_title_part2 = "de 2023."
        hero_intro = "PP, ERC, PNV y Sumar: consulta el estado de cobertura y los documentos originales de 2023."
        mock_notice = """<details class="notice pilot-details">
      <summary>Sobre este piloto</summary>
      <p>
      <strong>Aviso de ensayo privado (Generales 2023):</strong> Esta vista corresponde al ensayo técnico con documentos de PP, ERC, PNV y Sumar. Las posiciones visibles dependen de la revisión editorial de cada fuente, derecho de reutilización y propuesta. Una posición ausente no implica oposición. Este ensayo no satisface la puerta de publicación G2 para 2026 ni presenta información de 2026.</p>
    </details>"""
        selector_eyebrow = "01 / COMPARAR · GENERALES 2023"
        page_title = "Generales 2023 · Comparador de programas (Ensayo piloto)"
        page_description = ("Generales 2023 (piloto) · Ensayo privado con posiciones revisadas y fuentes originales."
                            if ctx.statements else
                            "Generales 2023 (piloto) · Ensayo privado. Publicación de posiciones pendiente.")
    else:
        active_rel = (
            ctx.relationships.get("rel-housing-rental-regulation-party-a-party-b")
            or next((r for r in sorted(ctx.relationships.values(), key=lambda r: r.id) if r.status == "active"), None)
        )
        party_a_id = active_rel.party_ids[0] if active_rel else "partido-ejemplo-a"
        party_b_id = active_rel.party_ids[1] if active_rel and len(active_rel.party_ids) > 1 else "partido-ejemplo-b"
        hero_eyebrow = escape(ctx.i18n['hero']['eyebrow'])
        hero_title_part1 = escape(ctx.i18n['hero']['title_part1'])
        hero_title_part2 = escape(ctx.i18n['hero']['title_part2'])
        hero_intro = escape(ctx.i18n['hero']['intro'])
        mock_notice = f"""<aside class="notice" aria-label="Aviso de la maqueta">
      <strong>{escape(ctx.i18n['mock_notice']['title'])}</strong> {escape(ctx.i18n['mock_notice']['text'])}
    </aside>"""
        selector_eyebrow = escape(ctx.i18n['selector']['eyebrow'])
        page_title = f"{ctx.i18n['meta']['site_name']} · Comparador de programas electorales"
        page_description = ctx.i18n["meta"]["site_description"]

    if ctx.production_records:
        party_ids = sorted(ctx.parties)
        party_a_id = active_rel.party_ids[0] if active_rel else (party_ids[0] if party_ids else "")
        party_b_id = active_rel.party_ids[1] if active_rel else (party_ids[1] if len(party_ids) > 1 else "")
        received = sum(s.sha256 is not None and s.direct_url is not None for s in ctx.register.sources)
        mock_notice = f'''<aside class="notice" aria-label="Estado de incorporación">
      <strong>{received} documentos registrados para 2026.</strong>
      Las propuestas se incorporan tras comprobar la fuente y completar la revisión editorial.
      La falta de propuestas revisadas no implica apoyo ni oposición.
      <a href="./fuentes/">Consultar programas y cobertura</a>
    </aside>'''
        if not ctx.statements:
            hero_intro = "Consulta los documentos registrados y los temas del comparador. Las propuestas están pendientes de revisión editorial."

    topic_options = []
    for t in ctx.taxonomy.topics:
        selected = ' selected' if t.id == (active_rel.topic_id if active_rel else "housing") else ""
        topic_options.append(f'<option value="{escape(t.id)}"{selected}>{escape(t.name_es)}</option>')

    party_a_options = []
    party_b_options = []
    for pid in sorted(ctx.parties.keys()):
        p = ctx.parties[pid]
        sel_a = ' selected' if pid == party_a_id else ""
        sel_b = ' selected' if pid == party_b_id else ""
        party_a_options.append(f'<option value="{escape(pid)}"{sel_a}>{escape(p.display_name)}</option>')
        party_b_options.append(f'<option value="{escape(pid)}"{sel_b}>{escape(p.display_name)}</option>')

    payload = build_comparison_payload(ctx)
    default_topic = active_rel.topic_id if active_rel else "housing"
    measures_content = render_comparison_measures(ctx, payload, default_topic, party_a_id, party_b_id)

    budget_hero_btn = ""
    budget_home_section = ""
    if ctx.election_id != "es-gen-2023":
        budget_hero_btn = f"""
        <a class="btn-share" href="./presupuestos/2023/" style="min-height: 44px; display: inline-flex; align-items: center; text-decoration: none;">
          <span>Ver presupuestos (PGE)</span>
          <span aria-hidden="true">→</span>
        </a>"""
        budget_home_section = """
    <section id="presupuestos-seccion" class="budget-home-section" aria-labelledby="budget-home-title">
      <div class="section-head">
        <p class="hero-eyebrow">02 / PRESUPUESTOS DEL ESTADO</p>
        <h2 id="budget-home-title">¿A dónde va el dinero público?</h2>
        <p>Antes de evaluar las promesas de gasto de los programas electorales, consulta cómo se reparte el presupuesto oficial consolidado de España (PGE 2023: 485.986 millones de euros).</p>
      </div>
      <div class="budget-home-card">
        <div class="budget-home-grid">
          <div class="budget-home-item">
            <span class="budget-home-pct">~39 %</span>
            <strong>Pensiones públicas</strong>
            <p>190.687 M€ · La mayor partida del Estado con diferencia.</p>
          </div>
          <div class="budget-home-item">
            <span class="budget-home-pct">~14 %</span>
            <strong>Transferencias a CC.AA.</strong>
            <p>66.457 M€ · Financiación territorial que costea la sanidad y educación autonómicas.</p>
          </div>
          <div class="budget-home-item">
            <span class="budget-home-pct">~6,4 %</span>
            <strong>Deuda pública</strong>
            <p>31.275 M€ · Pago de intereses de la deuda estatal.</p>
          </div>
          <div class="budget-home-item">
            <span class="budget-home-pct">~40 %</span>
            <strong>Resto de servicios</strong>
            <p>Desempleo, I+D+i, infraestructuras, defensa, seguridad, justicia y agricultura.</p>
          </div>
        </div>
        <div class="budget-home-action">
          <a class="btn-primary" href="./presupuestos/2023/">
            <span>Ver gráfico proporcional y claves del presupuesto</span>
            <span aria-hidden="true">→</span>
          </a>
        </div>
      </div>
    </section>"""

    content = f"""    <section class="hero" aria-labelledby="hero-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="hero-title" class="hero-title">{hero_title_part1}<br><span class="hero-em">{hero_title_part2}</span></h1>
      <p class="hero-intro">{hero_intro}</p>
      <p class="site-update">Actualización del sitio: <time datetime="{escape(ctx.build_date)}">{escape(ctx.build_date)}</time></p>
      <div class="hero-actions">
        <a class="btn-primary" href="#comparador">
          <span>{escape(ctx.i18n['hero']['cta'])}</span>
          <span aria-hidden="true">→</span>
        </a>{budget_hero_btn}
      </div>
    </section>

    {mock_notice}

    <section id="comparador" class="compare-section" aria-labelledby="compare-title">
      <div class="section-head">
        <p class="hero-eyebrow">{selector_eyebrow}</p>
        <h2 id="compare-title">{escape(ctx.i18n['selector']['heading'])}</h2>
        <p>{escape(ctx.i18n['selector']['description'])}</p>
      </div>

      <form id="selection-form" class="controls-form" role="search" aria-label="Filtro de comparación">
        <div class="control-field">
          <label for="topic-select" class="control-label">{escape(ctx.i18n['selector']['topic_label'])}</label>
          <select id="topic-select" name="topic" class="control-select">
            {"".join(topic_options)}
          </select>
        </div>
        <div class="control-field">
          <label for="party-a-select" class="control-label">{escape(ctx.i18n['selector']['party_a_label'])}</label>
          <select id="party-a-select" name="partyA" class="control-select">
            {"".join(party_a_options)}
          </select>
        </div>
        <div class="control-field">
          <label for="party-b-select" class="control-label">{escape(ctx.i18n['selector']['party_b_label'])}</label>
          <select id="party-b-select" name="partyB" class="control-select">
            {"".join(party_b_options)}
          </select>
        </div>
        <div class="control-actions">
          <button type="submit" id="compare-submit" class="btn-compare">
            <span>Comparar propuestas</span>
            <span aria-hidden="true">→</span>
          </button>
        </div>
        <div id="selection-error" class="selection-error sr-only" role="alert" aria-live="assertive"></div>
      </form>

      <section class="measure-comparison" aria-labelledby="compare-results-heading">
        <h3 id="compare-results-heading" class="sr-only">Comparación de propuestas agrupadas por medida</h3>
        <div id="measures-container" class="measures-container">
{measures_content}
        </div>

{render_budget_context(ctx, "housing", "./", comparison=True)}
{render_share_controls(ctx)}
      </section>
    </section>
    <script src="./sharing.js" defer></script>
    {'<script src="./budget-context.js" defer></script>' if ctx.budget_payload is not None else ""}
    <script src="./{comparison_bundle_name(ctx)}" defer></script>
    <script src="./app.js" defer></script>
{budget_home_section}
    <section class="lower-sections">
      <div id="metodo">
        <p class="hero-eyebrow">{escape(ctx.i18n['methodology_summary']['eyebrow'])}</p>
        <h2>{escape(ctx.i18n['methodology_summary']['heading'])}</h2>
        <p>{escape(ctx.i18n['methodology_summary']['text'])}</p>
      </div>
      <div id="fuentes">
        <p class="hero-eyebrow">{escape(ctx.i18n['coverage_summary']['eyebrow'])}</p>
        <h2>{escape(ctx.i18n['coverage_summary']['heading'])}</h2>
        <p>{escape(ctx.i18n['coverage_summary']['text'])}</p>
      </div>
    </section>

    <dialog id="manifesto-dialog" class="manifesto-dialog" aria-labelledby="dialog-party-name">
      <div class="dialog-content">
        <header class="dialog-header">
          <div class="dialog-header-meta">
            <span id="dialog-party-pill" class="party-pill party-pill-a" aria-hidden="true">A</span>
            <div>
              <span class="dialog-eyebrow">Visor de extracto del programa</span>
              <h3 id="dialog-party-name" class="dialog-party-name">Candidatura</h3>
            </div>
          </div>
          <button type="button" class="dialog-close-btn" id="dialog-close-btn" aria-label="Cerrar visor">✕</button>
        </header>
        <div class="dialog-body" id="dialog-body"></div>
        <footer class="dialog-footer" id="dialog-footer">
          <button type="button" class="btn-close-dialog" id="dialog-dismiss-btn">Cerrar visor</button>
        </footer>
      </div>
    </dialog>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/",
        content=content,
        root_path="./",
    ).replace('<body ', '<body data-comparison="validated" ', 1)


def render_topic_index(ctx: SiteContext) -> str:
    """Render temas/index.html listing the selected taxonomy topics."""
    cards_html = []
    for t in ctx.taxonomy.topics:
        # Count proposals
        topic_stmts = [s for s in ctx.statements.values() if s.topic_id == t.id]
        cards_html.append(f"""<article class="party-card" style="margin-bottom: var(--space-4);">
        <div class="party-card-header">
          <span class="party-pill party-pill-a" aria-hidden="true">◧</span>
          <div class="party-card-meta">
            <h2 class="party-name"><a href="./{escape(t.id)}/">{escape(t.name_es)}</a></h2>
            <span class="status-badge status-badge-official">{len(t.subtopics)} subtemas</span>
          </div>
        </div>
        <p class="party-statement">{escape(t.description_es)}</p>
        <div class="party-card-footer">
          <span class="source-citation">
            <a href="./{escape(t.id)}/">Ver comparador de {escape(t.name_es)} →</a>
          </span>
          <span class="source-date">{len(topic_stmts)} afirmaciones registradas</span>
        </div>
      </article>""")

    hero_eyebrow = "ENSAYO PILOTO PRIVADO · TAXONOMÍA GENERALES 2023" if ctx.election_id == "es-gen-2023" else "TAXONOMÍA ELECTORAL 2026"
    page_title = "Temas electorales · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else "Temas electorales · Elecciones 2026"
    page_description = "Explora las propuestas electorales para las Elecciones Generales 2023 (Ensayo piloto)." if ctx.election_id == "es-gen-2023" else f"Explora las propuestas electorales para las Elecciones Generales 2026 agrupadas en {len(ctx.taxonomy.topics)} temas clave."

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a>
    </nav>

    <section class="hero" aria-labelledby="topics-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="topics-title" class="hero-title">Temas electorales</h1>
      <p class="hero-intro">Explora las 8 áreas clave definidas en la metodología neutral del proyecto. Cada área desglosa propuestas concretas con trazabilidad documental directa.</p>
    </section>

    <section class="topics-grid" data-paginate="6" data-paginate-item-name="temas" style="padding: var(--space-4) 0 var(--space-8);">
      {"".join(cards_html)}
    </section>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/temas/",
        content=content,
        root_path="../",
    )


def render_topic_detail(ctx: SiteContext, topic: Topic) -> str:
    """Render crawlable HTML for a specific topic (temas/{topic_id}/index.html)."""
    subtopics_sections = []
    topic_stmts = [s for s in ctx.statements.values() if s.topic_id == topic.id]
    topic_rels = [r for r in ctx.relationships.values() if r.topic_id == topic.id and r.status == "active"]

    for sub in topic.subtopics:
        sub_stmts = [s for s in topic_stmts if s.subtopic_id == sub.id]
        sub_rels = [r for r in topic_rels if r.subtopic_id == sub.id]

        if not sub_stmts and not sub_rels:
            body = """<div class="notice" style="margin-top: var(--space-3);">
                <p>No se han registrado aún afirmaciones revisadas en este subtema para las candidaturas auditadas.</p>
              </div>"""
        else:
            cards = []
            for stmt in sub_stmts:
                cards.append(render_party_card(ctx, stmt, stmt.party_id, "A" if "a" in stmt.party_id else "B"))

            rel_callout = ""
            if sub_rels:
                r = sub_rels[0]
                rel_label = ctx.i18n["relationship_badges"].get(r.relationship_type, r.relationship_type)
                rel_callout = f"""<aside class="analysis-callout" aria-label="Relación comparada" style="margin-top: var(--space-4);">
                  <span class="analysis-icon" aria-hidden="true">↔</span>
                  <div>
                    <h3>{escape(rel_label)}: {escape(r.measure_label)}</h3>
                    <p>{escape(r.summary)}</p>
                  </div>
                </aside>"""

            body = f"""<div class="measure-cards" style="margin-top: var(--space-3);">
                {"".join(cards)}
              </div>
              {rel_callout}"""

        subtopics_sections.append(f"""<section class="subtopic-section" style="margin-bottom: var(--space-8);">
          <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-2);">{escape(sub.name_es)}</h2>
          {body}
        </section>""")

    hero_eyebrow = "ENSAYO PILOTO PRIVADO · GENERALES 2023" if ctx.election_id == "es-gen-2023" else "TEMA ELECTORAL · ELECCIONES 2026"
    page_title = f"{topic.name_es} · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else f"{topic.name_es} · Comparador Elecciones 2026"
    budget_ctx = render_budget_context(ctx, topic.id, "../../")
    budget_ctx_line = f"\n    {budget_ctx}" if budget_ctx else ""

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a> ·
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">Todos los temas</a>
    </nav>

    <section class="hero" aria-labelledby="topic-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="topic-title" class="hero-title">{escape(topic.name_es)}</h1>
      <p class="hero-intro">{escape(topic.description_es)}</p>
      <div style="font-size: var(--font-size-xs); color: var(--color-text-muted);">
        Última actualización: <time datetime="{ctx.build_date}">{ctx.build_date}</time>
      </div>
    </section>

    {render_share_controls(ctx)}
    <script src="../../sharing.js" defer></script>
    <div class="subtopics-container" data-paginate="3" data-paginate-item-name="subtemas">
    {"".join(subtopics_sections)}
    </div>{budget_ctx_line}"""

    topic_schema = build_structured_data(
        ctx=ctx,
        canonical_path=f"/temas/{topic.id}/",
        title=page_title,
        description=topic.description_es,
        topic=topic,
    )

    return render_base(
        ctx=ctx,
        title=page_title,
        description=topic.description_es,
        canonical_path=f"/temas/{topic.id}/",
        content=content,
        root_path="../../",
        structured_data=topic_schema,
    )


def render_party_index(ctx: SiteContext) -> str:
    """Render partidos/index.html listing tracked candidacies."""
    cards = []
    for pid in sorted(ctx.parties.keys()):
        party = ctx.parties[pid]
        # Look for source in register
        src = next((s for s in ctx.register.sources if s.party_id == pid and s.election_id == ctx.election_id), None)
        status = src.status if src else "missing"
        badge = render_status_badge(ctx, status)
        scope = "Pendiente de verificación" if party.territorial_scope == "pending_verification" else party.territorial_scope
        name_label = "Nombre registrado" if ctx.production_records else "Nombre oficial"

        cards.append(f"""<article class="party-card" style="margin-bottom: var(--space-4);">
        <div class="party-card-header">
          <span class="party-pill party-pill-a" aria-hidden="true">◧</span>
          <div class="party-card-meta">
            <h2 class="party-name"><a href="./{escape(pid)}/">{escape(party.display_name)}</a></h2>
            {badge}
          </div>
        </div>
        <p class="party-statement"><strong>{name_label}:</strong> {escape(party.official_name)} · <strong>Ámbito:</strong> {escape(scope)}</p>
        <div class="party-card-footer">
          <a class="source-citation" href="./{escape(pid)}/">Ver programa y propuestas →</a>
          <span class="source-date">{escape(party.short_name)}</span>
        </div>
      </article>""")

    hero_eyebrow = "ENSAYO PILOTO PRIVADO · CANDIDATURAS GENERALES 2023" if ctx.election_id == "es-gen-2023" else "CANDIDATURAS Y COBERTURA"
    page_title = "Candidaturas y partidos · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else "Candidaturas y partidos · Elecciones 2026"
    page_description = "Consulta las candidaturas y el estado de sus programas para las Elecciones Generales 2023 (Ensayo piloto)." if ctx.election_id == "es-gen-2023" else "Consulta las candidaturas electorales y el estado de sus programas para las Elecciones Generales 2026."
    registry_intro = ("Inventario del proyecto con las formaciones y los documentos registrados. Consulte el estado de verificación y las propuestas revisadas de cada formación."
                      if ctx.production_records else "Registro oficial de partidos y coaliciones incluidos en el comparador bajo criterios públicos y auditables. Consulte el estado de publicación y las propuestas revisadas de cada formación.")

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a>
    </nav>

    <section class="hero" aria-labelledby="parties-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="parties-title" class="hero-title">Candidaturas seguidas</h1>
      <p class="hero-intro">{registry_intro}</p>
    </section>

    <section class="parties-list" data-paginate="6" data-paginate-item-name="candidaturas" style="padding: var(--space-4) 0 var(--space-8);">
      {"".join(cards)}
    </section>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/partidos/",
        content=content,
        root_path="../",
    )


def render_party_detail(ctx: SiteContext, party: PartyInfo) -> str:
    """Render crawlable HTML for a single party (partidos/{party_id}/index.html)."""
    src = next((s for s in ctx.register.sources if s.party_id == party.id and s.election_id == ctx.election_id), None)
    status = src.status if src else "missing"
    status_badge = render_status_badge(ctx, status)

    party_stmts = [s for s in ctx.statements.values() if s.party_id == party.id]

    # Source info card
    src_info = "<p>No consta programa electoral oficial registrado para esta candidatura en la fecha de consulta.</p>"
    if src and src.official_url:
        sha_display = f"<code>{src.sha256[:16]}...</code>" if src.sha256 else "<em>pendiente de verificación</em>"
        src_info = f"""<ul style="list-style: none; padding: 0; margin: 0; line-height: 1.8;">
          <li><strong>URL oficial:</strong> <a href="{escape(src.official_url)}" target="_blank" rel="noopener noreferrer">{escape(src.official_url)}</a></li>
          <li><strong>Versión registrada:</strong> {escape(src.version)}</li>
          <li><strong>Fecha de consulta:</strong> {escape(src.retrieval_date)}</li>
          <li><strong>Hash SHA-256:</strong> {sha_display}</li>
          <li><strong>Uso autorizado:</strong> {escape(rights_status_label(src.rights_review.status))}</li>
        </ul>"""

    stmts_sections = []
    if not party_stmts:
        stmts_sections.append("""<div class="notice" style="margin-top: var(--space-4);">
          <p><strong>Propuestas pendientes de revisión:</strong> No se han registrado aún afirmaciones revisadas para esta candidatura.</p>
        </div>""")
    else:
        for s in party_stmts:
            topic = next((t for t in ctx.taxonomy.topics if t.id == s.topic_id), None)
            topic_name = topic.name_es if topic else s.topic_id
            stmts_sections.append(f"""<div style="margin-bottom: var(--space-4);">
              <h3 style="font-size: var(--font-size-base); color: var(--color-text-brand); margin-bottom: var(--space-2);">{escape(topic_name)}</h3>
              {render_party_card(ctx, s, party.id, "A")}
            </div>""")

    # Cross-linking shortcuts to compare this party against other candidacies
    compare_links = []
    for other_pid in sorted(ctx.parties.keys()):
        if other_pid == party.id:
            continue
        other_party = ctx.parties[other_pid]
        compare_links.append(
            f'<a href="../../?topic=housing&partyA={escape(party.id)}&partyB={escape(other_pid)}" class="action-link" style="margin-right: var(--space-2); margin-bottom: var(--space-2); display: inline-block;">'
            f'vs {escape(other_party.display_name)}</a>'
        )
    compare_section = f"""<section class="party-card" style="margin-bottom: var(--space-8);">
      <h2 style="font-size: var(--font-size-lg); margin-top: 0;">Comparar {escape(party.display_name)} con otras candidaturas</h2>
      <p style="font-size: var(--font-size-sm); color: var(--color-text-secondary); margin-bottom: var(--space-3);">Acceso directo a la comparación en el comparador interactivo:</p>
      <div style="display: flex; flex-wrap: wrap; gap: var(--space-2);">
        {"".join(compare_links)}
      </div>
    </section>"""

    hero_eyebrow = "ENSAYO PILOTO PRIVADO · CANDIDATURA GENERALES 2023" if ctx.election_id == "es-gen-2023" else "CANDIDATURA · ELECCIONES 2026"
    page_title = f"{party.display_name} · Programa y propuestas Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else f"{party.display_name} · Programa y propuestas Elecciones 2026"
    page_description = f"Consulta el programa electoral y propuestas revisadas de {party.display_name} para las Elecciones Generales 2023 (Ensayo piloto)." if ctx.election_id == "es-gen-2023" else f"Consulta el programa electoral y propuestas revisadas de {party.display_name} para las Elecciones 2026."

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a> ·
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">Todas las candidaturas</a>
    </nav>

    <section class="hero" aria-labelledby="party-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="party-title" class="hero-title">{escape(party.display_name)}</h1>
      <p class="hero-intro">{escape(party.official_name)} ({escape(party.short_name)})</p>
      <div style="display: flex; gap: var(--space-2); align-items: center; margin-top: var(--space-2);">
        <span>Estado del programa:</span> {status_badge}
      </div>
    </section>

    <section class="party-card" style="margin-bottom: var(--space-8);">
      <h2 style="font-size: var(--font-size-lg); margin-top: 0;">Documento y trazabilidad</h2>
      {src_info}
    </section>

    {compare_section}

    <section style="margin-bottom: var(--space-10);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-4);">Propuestas y posiciones revisadas</h2>
      <div class="proposals-list" data-paginate="5" data-paginate-item-name="propuestas">
      {"".join(stmts_sections)}
      </div>
    </section>"""

    party_schema = build_structured_data(
        ctx=ctx,
        canonical_path=f"/partidos/{party.id}/",
        title=page_title,
        description=page_description,
        party=party,
    )

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path=f"/partidos/{party.id}/",
        content=content,
        root_path="../../",
        structured_data=party_schema,
    )


def render_methodology_page(ctx: SiteContext) -> str:
    """Render metodo/index.html with full editorial methodology, source coverage, update timestamp, and correction policy (Package E2.4)."""
    formatted_date = format_date_spanish(ctx.build_date)

    sources_2026 = [s for s in sorted(ctx.register.sources, key=lambda s: s.id) if s.election_id == "es-gen-2026"]
    coverage_cards_2026 = "\n".join(render_source_coverage_card(ctx, s) for s in sources_2026)

    sorted_corrections = sorted(ctx.corrections, key=lambda c: (c.correction_date, c.id), reverse=True)
    correction_items = []
    for c in sorted_corrections[:3]:
        correction_items.append(
            f"""<li style="margin-bottom: var(--space-2); line-height: 1.5;">
              <strong>{escape(c.correction_date)} · {escape(c.id)} ({escape(c.correction_type)}):</strong>
              {escape(c.reason)}
            </li>"""
        )
    corrections_summary_html = ""
    if correction_items:
        corrections_summary_html = f"""<div style="margin-top: var(--space-3); padding: var(--space-3); background: var(--color-bg-surface-subtle); border-radius: var(--radius-md);">
          <h3 style="font-size: var(--font-size-sm); margin-top: 0; margin-bottom: var(--space-2); color: var(--color-text-primary);">Últimas rectificaciones registradas:</h3>
          <ul style="margin: 0; padding-left: var(--space-4); font-size: var(--font-size-xs); color: var(--color-text-secondary);">
            {"".join(correction_items)}
          </ul>
        </div>"""

    hero_eyebrow = "METODOLOGÍA EDITORIAL · GENERALES 2023 (ENSAYO PILOTO)" if ctx.election_id == "es-gen-2023" else "METODOLOGÍA EDITORIAL, FUENTES Y RECTIFICACIONES · ELECCIONES 2026"
    page_title = "Metodología editorial y privacidad · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else "Metodología editorial y privacidad · Elecciones 2026"
    page_description = "Marco metodológico, gobernanza editorial y aviso de privacidad para el ensayo de las Elecciones Generales 2023." if ctx.election_id == "es-gen-2023" else "Marco metodológico, gobernanza editorial, política de citas y aviso de privacidad de Elecciones 2026."
    single_review = ctx.production_records and ctx.election_id == "es-gen-2026"
    review_heading = "Revisión editorial" if single_review else "Principio de cuatro ojos (Four-Eyes Principle)"
    review_rule = (
        "Cada resumen de una propuesta sin cita literal requiere la aprobación explícita de una persona. "
        "Esa persona comprueba la fuente, el alcance y las condiciones de la propuesta. "
        "Las citas literales y las relaciones entre propuestas requieren dos revisiones humanas independientes."
        if single_review
        else "Toda afirmación publicada requiere la aprobación explícita de al menos dos revisores editoriales independientes."
    )

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a>
    </nav>

    <section class="hero" aria-labelledby="method-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="method-title" class="hero-title">Compara con rigor y neutralidad</h1>
      <p class="hero-intro">El comparador enlaza cada propuesta a su fuente y aplica una revisión editorial humana. No recomienda el voto.</p>
      <div class="update-stamp" aria-label="Fecha de actualización">
        <span class="update-stamp-label">Última actualización:</span>
        <time class="update-date" datetime="{escape(ctx.build_date)}">{formatted_date}</time>
      </div>
    </section>

    <section style="display: grid; gap: var(--space-6); max-width: var(--content-max-width);">
      <article class="party-card">
        <h2>1. Principio de neutralidad cívica</h2>
        <p class="party-statement">No clasificamos candidaturas con puntuaciones opacas, no ordenamos partidos por simpatía política ni emitimos sugerencias de voto. El comparador presenta las propuestas con idéntico espacio, rigor documental y tipografía.</p>
      </article>

      <article class="party-card">
        <h2>2. Criterios objetivos de inclusión de candidaturas</h2>
        <p class="party-statement">El proyecto aplica umbrales objetivos y predecibles para seleccionar las candidaturas objeto de seguimiento, evitando inclusiones o exclusiones arbitrarias:</p>
        <ul style="color: var(--color-text-secondary); line-height: 1.6;">
          <li><strong>Criterio A (Representación parlamentaria previa):</strong> Fuerzas políticas que obtuvieron al menos un escaño en las Cortes Generales (Congreso de los Diputados o el Senado) en las elecciones generales anteriores (julio de 2023), o en las elecciones al Parlamento Europeo de junio de 2024.</li>
          <li><strong>Criterio B (Proclamación nacional de candidaturas):</strong> Fuerzas políticas cuyas listas sean proclamadas oficialmente por la Junta Electoral Central (JEC) en circunscripciones que sumen al menos el 50% del censo electoral estatal.</li>
          <li><strong>Candidaturas de ámbito territorial o autonómico:</strong> Las formaciones políticas que cumplen el Criterio A pero concurren exclusivamente en determinadas comunidades autónomas (como ERC, EAJ-PNV, EH Bildu, Junts, BNG, CC) se incluyen reflejando con claridad su ámbito territorial de votación.</li>
          <li><strong>Ordenación neutral:</strong> Las candidaturas se muestran en orden alfabético estricto según su denominación oficial o pública. Nunca se ordenan por intención de voto, escaños previos ni afinidad editorial.</li>
        </ul>
      </article>

      <article class="party-card">
        <h2>3. {review_heading}</h2>
        <p class="party-statement">{review_rule}</p>
        <p class="party-statement">Cuando se aplica el principio de cuatro ojos, las dos revisiones se reparten estas comprobaciones.</p>
        <ul style="color: var(--color-text-secondary); line-height: 1.6;">
          <li><strong>Revisor 1 (Factual):</strong> Comprueba la cita literal, la versión del documento, el hash SHA-256 y la localización exacta (página o sección).</li>
          <li><strong>Revisor 2 (Neutralidad):</strong> Verifica que el resumen sea descriptivo, objetivo y preserve los condicionantes o matices operativos.</li>
        </ul>
        <p class="party-statement">El redactor inicial que extrae la propuesta no puede actuar como segundo revisor (segregación estricta de funciones).</p>
      </article>

      <article class="party-card">
        <h2>4. Límites legales de citas textuales</h2>
        <p class="party-statement">En aplicación del artículo 32 del Texto Refundido de la Ley de Propiedad Intelectual (TRLPI), las citas directas tienen un límite máximo estricto de <strong>40 palabras</strong> y <strong>300 caracteres</strong>, van entrecomilladas e identifican siempre autor, documento oficial y número de página o sección. No se publica ninguna cita sin fuente verificada y derechos revisados.</p>
      </article>

      <article class="party-card">
        <h2>5. Distinción explícita de ausencia («No consta»)</h2>
        <p class="party-statement">Cuando un programa revisado no contiene una propuesta sobre una medida concreta, se cataloga como <code>not_found</code> y se muestra con el aviso explícito «No consta en el programa». <strong>Nunca se interpreta la ausencia de mención como rechazo u oposición política.</strong></p>
      </article>

      <article class="party-card" id="cobertura">
        <h2>6. Cobertura y estado de los programas (Elecciones 2026)</h2>
        <p class="party-statement">Cada candidatura incluida dispone de un estado público dentro del ciclo de vida documental (<code>missing</code>, <code>announced</code>, <code>partial</code>, <code>published-unverified</code>, <code>official</code>, <code>replaced</code>). Las candidaturas sin programa definitivo se identifican con la etiqueta explícita «Programa no disponible» y no generan posiciones deducidas:</p>
        <div class="coverage-cards" style="margin-top: var(--space-4);">
          {coverage_cards_2026}
        </div>
        <aside class="notice" style="margin-top: var(--space-4);">
          <strong>Aislamiento de elecciones y pruebas técnicas (Tarea 1.4):</strong> Los programas y ensayos del piloto de 2023 se emplean exclusivamente para la verificación técnica de esquemas. El comparador rechaza automáticamente cualquier comparación cruzada entre elecciones. Puede consultar el inventario técnico completo y sumas SHA-256 en la página de <a href="../fuentes/" class="action-link">registro de fuentes</a>.
        </aside>
      </article>

      <article class="party-card" id="rectificaciones">
        <h2>7. Política y registro de rectificaciones</h2>
        <p class="party-statement">Cualquier actualización o rectificación sobre una afirmación fuente invalida automáticamente las relaciones comparativas derivadas, que quedan retiradas del comparador público hasta que dos revisores las auditen de nuevo.</p>
        <p class="party-statement">El procedimiento de corrección clasifica las incidencias según su severidad con plazos de triaje estrictos:</p>
        <ul style="color: var(--color-text-secondary); line-height: 1.6;">
          <li><strong>Crítica (Sev-1):</strong> Inversión factual o error de atribución grave. Triaje inmediato en &lt;= 4 horas y publicación en &lt;= 12 horas.</li>
          <li><strong>Grave (Sev-2):</strong> Inexactitud sustantiva en el instrumento o localización errónea. Triaje en &lt;= 12 horas y publicación en &lt;= 24 horas.</li>
          <li><strong>Menor (Sev-3):</strong> Errata tipográfica o ajuste menor sin cambio de sentido. Triaje en &lt;= 24 horas y publicación en &lt;= 48 horas.</li>
        </ul>
        <p class="party-statement">Toda rectificación queda registrada de forma inmutable con fecha, identificador, valores previos y motivo. Consulte el <a href="../correcciones/" class="action-link">historial completo de rectificaciones</a>.</p>
        {corrections_summary_html}
      </article>

      <article class="party-card" id="avisos">
        <h2>8. Avisos de errores y rectificaciones</h2>
        <p class="party-statement">La función en línea para avisar de errores estará disponible más adelante. Mientras tanto, las solicitudes editoriales se gestionan de forma centralizada según el registro de correcciones auditable. Para remitir una observación o comunicar una errata, contacte con: <strong>editorial@elecciones2026.es</strong>.</p>
      </article>

      <article class="party-card" id="privacidad">
        <h2>9. Aviso de privacidad y protección de datos</h2>
        <p class="party-statement"><strong>Responsable del tratamiento:</strong> C2 Ventures<br>
        <strong>Contacto:</strong> privacidad@elecciones2026.es</p>
        <p class="party-statement">Este sitio web no utiliza cookies de seguimiento, no recopila datos personales, no solicita registros de usuario y no procesa respuestas de voto. Las comparaciones que realice se ejecutan exclusivamente en la memoria local de su navegador.</p>
      </article>
    </section>"""

    if ctx.production_records:
        content = re.sub(r'<aside class="notice"[^>]*>\s*<strong>Aislamiento de elecciones.*?</aside>',
                         '', content, flags=re.DOTALL)

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/metodo/",
        content=content,
        root_path="../",
    )


def render_sources_page(ctx: SiteContext) -> str:
    """Render fuentes/index.html with source register, mobile cards, and 2026/2023 isolation (Package E2.4)."""
    formatted_date = format_date_spanish(ctx.build_date)
    rows_2026 = []
    rows_2023 = []
    cards_2026 = []
    cards_2023 = []

    for src in sorted(ctx.register.sources, key=lambda s: s.id):
        badge = render_status_badge(ctx, src.status)
        url_link = f'<a href="{escape(src.official_url)}" target="_blank" rel="noopener noreferrer">Enlace oficial <span aria-hidden="true">↗</span> <span class="sr-only">(se abre en una ventana nueva)</span></a>' if src.official_url else "<em>No disponible</em>"
        hash_code = f"<code>{src.sha256[:12]}...</code>" if src.sha256 else "—"

        row = f"""<tr>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle); font-weight: bold;">{escape(src.publisher)}</td>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{badge}</td>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{escape(src.version)}</td>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{escape(src.retrieval_date)}</td>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{hash_code}</td>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{escape(rights_status_label(src.rights_review.status))}</td>
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{url_link}</td>
        </tr>"""

        card = render_source_coverage_card(ctx, src)

        if src.election_id == "es-gen-2026":
            rows_2026.append(row)
            cards_2026.append(card)
        else:
            rows_2023.append(row)
            cards_2023.append(card)

    cards_2026_html = "\n".join(cards_2026)
    cards_2023_html = "\n".join(cards_2023)
    rows_2026_html = "".join(rows_2026)
    rows_2023_html = "".join(rows_2023)

    hero_eyebrow = "REGISTRO DE FUENTES Y AUDITORÍA · GENERALES 2023 (ENSAYO PILOTO)" if ctx.election_id == "es-gen-2023" else "REGISTRO DE FUENTES Y AUDITORÍA"
    page_title = "Fuentes oficiales y trazabilidad · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else "Fuentes oficiales y trazabilidad · Elecciones 2026"
    page_description = "Inventario de fuentes primarias, versiones y hashes SHA-256 para el ensayo de las Elecciones Generales 2023." if ctx.election_id == "es-gen-2023" else "Inventario de fuentes primarias, versiones y hashes SHA-256 para las Elecciones 2026."

    historical_inventory = "" if ctx.production_records else f'''
    <section style="margin-bottom: var(--space-10);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-3);">2. Fuentes históricas de ensayo · Piloto 2023</h2>
      <aside class="notice" style="margin-bottom: var(--space-4);">
        <strong>Aislamiento de elecciones (Tarea 1.4):</strong> Los documentos de 2023 se emplean exclusivamente para ensayos técnicos y validación de esquemas. El comparador rechaza automáticamente cualquier intento de comparar un programa de 2023 con uno de 2026.
      </aside>
      <div class="coverage-cards" data-paginate="6" data-paginate-item-name="fuentes" style="margin-bottom: var(--space-4);">
        {cards_2023_html}
      </div>
      <div class="coverage-table-container">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: var(--font-size-sm);">
          <thead>
            <tr style="background: var(--color-bg-surface-subtle); border-bottom: 2px solid var(--color-border-subtle);">
              <th style="padding: var(--space-3);">Candidatura</th>
              <th style="padding: var(--space-3);">Estado</th>
              <th style="padding: var(--space-3);">Versión</th>
              <th style="padding: var(--space-3);">Fecha consulta</th>
              <th style="padding: var(--space-3);">SHA-256</th>
              <th style="padding: var(--space-3);">Derechos</th>
              <th style="padding: var(--space-3);">Acceso</th>
            </tr>
          </thead>
          <tbody>
            {rows_2023_html}
          </tbody>
        </table>
      </div>
    </section>

'''

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a>
    </nav>

    <section class="hero" aria-labelledby="sources-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="sources-title" class="hero-title">Fuentes oficiales y trazabilidad</h1>
      <p class="hero-intro">Inventario público de documentos electorales, fechas de consulta, versiones y sumas de verificación criptográfica (SHA-256). Solo los documentos verificados alimentan afirmaciones públicas.</p>
      <div class="update-stamp" aria-label="Fecha de actualización">
        <span class="update-stamp-label">Última actualización:</span>
        <time class="update-date" datetime="{escape(ctx.build_date)}">{formatted_date}</time>
      </div>
    </section>

    <section style="margin-bottom: var(--space-8);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-3);">1. Fuentes monitorizadas · Elecciones Generales 2026</h2>
      <div class="coverage-cards" data-paginate="6" data-paginate-item-name="fuentes" style="margin-bottom: var(--space-4);">
        {cards_2026_html}
      </div>
      <div class="coverage-table-container">
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: var(--font-size-sm);">
          <thead>
            <tr style="background: var(--color-bg-surface-subtle); border-bottom: 2px solid var(--color-border-subtle);">
              <th style="padding: var(--space-3);">Candidatura</th>
              <th style="padding: var(--space-3);">Estado</th>
              <th style="padding: var(--space-3);">Versión</th>
              <th style="padding: var(--space-3);">Fecha consulta</th>
              <th style="padding: var(--space-3);">SHA-256</th>
              <th style="padding: var(--space-3);">Derechos</th>
              <th style="padding: var(--space-3);">Acceso</th>
            </tr>
          </thead>
          <tbody>
            {rows_2026_html}
          </tbody>
        </table>
      </div>
    </section>

    {historical_inventory}

    <section style="margin-bottom: var(--space-8);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-3);">3. Observaciones y canales editoriales</h2>
      <article class="party-card">
        <p class="party-statement">Si detecta que una candidatura ha publicado un nuevo documento oficial, o que un enlace o suma de verificación difiere del original proclamado, remita la referencia a: <strong>editorial@elecciones2026.es</strong>. El registro de fuentes no admite formularios interactivos en línea en esta versión inicial (MVP) para preservar la cadena de custodia documental.</p>
        <p class="party-statement">Consulte el marco de inclusión y gobernanza en la <a href="../metodo/" class="action-link">página de metodología</a> o el <a href="../correcciones/" class="action-link">registro de correcciones</a>.</p>
      </article>
    </section>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/fuentes/",
        content=content,
        root_path="../",
    )


def render_corrections_page(ctx: SiteContext) -> str:
    """Render correcciones/index.html with public correction history (Package E2.4)."""
    formatted_date = format_date_spanish(ctx.build_date)
    cards = []
    sorted_corrections = sorted(ctx.corrections, key=lambda c: (c.correction_date, c.id), reverse=True)

    if not sorted_corrections:
        cards.append("""<div class="notice">
          <p>No se han registrado rectificaciones editoriales hasta la fecha.</p>
        </div>""")
    else:
        for c in sorted_corrections:
            invalidation_notice = ""
            if c.invalidated_relationship_ids:
                inv_list = ", ".join(f"<code>{escape(rid)}</code>" for rid in c.invalidated_relationship_ids)
                invalidation_notice = f"""<div class="party-caveat" style="margin-top: var(--space-3);">
                  <strong>Relaciones invalidadas preventivamente:</strong> {inv_list}
                </div>"""

            cards.append(f"""<article class="party-card" style="margin-bottom: var(--space-4);">
            <div class="party-card-header">
              <span class="party-pill party-pill-b" aria-hidden="true">✎</span>
              <div class="party-card-meta">
                <h2 class="party-name" style="font-size: var(--font-size-base);">{escape(c.id)} · {escape(c.correction_type)}</h2>
                <span class="status-badge status-badge-official">{escape(c.correction_date)}</span>
              </div>
            </div>
            <p class="party-statement"><strong>Objetivo:</strong> <code>{escape(c.target_type)}</code> · ID: <code>{escape(c.target_id)}</code></p>
            <p class="party-statement"><strong>Motivo:</strong> {escape(c.reason)}</p>
            {invalidation_notice}
            <div class="party-card-footer">
              <span class="source-date">Revisado por: {escape(c.reviewed_by)} / Aprobado por: {escape(c.approved_by)}</span>
              <span class="source-date">Notificado por: {escape(c.reporter)}</span>
            </div>
          </article>""")

    hero_eyebrow = "REGISTRO DE CORRECCIONES · GENERALES 2023 (ENSAYO PILOTO)" if ctx.election_id == "es-gen-2023" else "TRANSPARENCIA Y RECTIFICACIÓN"
    page_title = "Registro de correcciones editoriales · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else "Registro de correcciones editoriales · Elecciones 2026"
    page_description = "Historial público y transparente de correcciones y revisiones para el ensayo de las Elecciones Generales 2023." if ctx.election_id == "es-gen-2023" else "Historial público y transparente de correcciones y revisiones en los datos electorales."

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a>
    </nav>

    <section class="hero" aria-labelledby="corrections-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="corrections-title" class="hero-title">Registro de correcciones</h1>
      <p class="hero-intro">Historial auditable de correcciones de erratas, reubicaciones temáticas o actualizaciones de fuentes. Cada cambio invalida las relaciones comparativas dependientes hasta su nueva verificación.</p>
      <div class="update-stamp" aria-label="Fecha de actualización">
        <span class="update-stamp-label">Última actualización:</span>
        <time class="update-date" datetime="{escape(ctx.build_date)}">{formatted_date}</time>
      </div>
    </section>

    <section style="margin-bottom: var(--space-6);">
      <article class="party-card">
        <h2 style="font-size: var(--font-size-lg); margin-top: 0;">Compromisos y plazos de rectificación</h2>
        <p class="party-statement">Cualquier actualización o rectificación sobre una afirmación fuente invalida automáticamente las relaciones comparativas derivadas, que quedan retiradas del comparador público hasta que dos revisores las auditen de nuevo (principio de cuatro ojos y segregación estricta de funciones).</p>
        <ul style="color: var(--color-text-secondary); line-height: 1.6; font-size: var(--font-size-sm);">
          <li><strong>Crítica (Sev-1):</strong> Inversión factual o error de atribución grave. Triaje inmediato en &lt;= 4 horas y publicación en &lt;= 12 horas.</li>
          <li><strong>Grave (Sev-2):</strong> Inexactitud sustantiva en el instrumento o localización errónea. Triaje en &lt;= 12 horas y publicación en &lt;= 24 horas.</li>
          <li><strong>Menor (Sev-3):</strong> Errata tipográfica o ajuste menor sin cambio de sentido. Triaje en &lt;= 24 horas y publicación en &lt;= 48 horas.</li>
        </ul>
        <p class="party-statement"><strong>Canal estático de comunicación:</strong> No se ofrecen formularios interactivos de reporte en esta versión inicial (MVP). Cualquier comunicación o aviso de errata se gestiona por correo electrónico en: <strong>editorial@elecciones2026.es</strong>. Consulte los detalles normativos en la <a href="../metodo/#rectificaciones" style="text-decoration: underline; font-weight: bold;">metodología de rectificaciones</a>.</p>
      </article>
    </section>

    <section style="margin-bottom: var(--space-10);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-3);">Historial de rectificaciones auditadas</h2>
      <div class="corrections-list" data-paginate="5" data-paginate-item-name="correcciones">
      {"".join(cards)}
      </div>
    </section>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/correcciones/",
        content=content,
        root_path="../",
    )


def render_proposals_page(ctx: SiteContext) -> str:
    """Render propuestas/index.html with the Improvement Proposal Box (Package E8.5)."""
    feedback_i18n = ctx.i18n.get("feedback", {})
    title = feedback_i18n.get("title", "Buzón de propuestas de mejora")
    subtitle = feedback_i18n.get("subtitle", "¿Qué te gustaría ver diferente en esta aplicación?")
    intro = feedback_i18n.get("intro", "Tu opinión nos ayuda a hacer esta herramienta más útil y clara. Leemos todas las propuestas para priorizar nuevas funciones y ajustes.")
    privacy_notice = feedback_i18n.get("privacy_notice", "Aviso: No introduzcas datos personales ni información confidencial. No realizamos respuestas personalizadas.")

    hero_eyebrow = "PARTICIPACIÓN Y MEJORA CONTINUA"
    page_title = f"{title} · Elecciones 2026"
    page_description = "Buzón de propuestas y sugerencias anónimas para la mejora continua del comparador de programas electorales de las Elecciones Generales 2026."

    content = f"""    <nav aria-label="Miga de pan" style="padding: var(--space-4) 0 0;">
      <a href="../" class="nav-link" style="display: inline-flex; padding: 0;">← Volver al inicio</a>
    </nav>

    <section class="hero" aria-labelledby="proposals-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="proposals-title" class="hero-title">{escape(title)}</h1>
      <p class="hero-intro">{escape(subtitle)}</p>
    </section>

    <section style="margin-bottom: var(--space-8); max-width: 680px;">
      <article class="party-card">
        <p class="party-statement">{escape(intro)}</p>
        <div class="party-caveat" style="margin-top: var(--space-3);" role="note">
          <strong>Aviso de privacidad:</strong> {escape(privacy_notice)}
        </div>

        <form id="proposal-form" method="POST" action="/api/propuestas" style="margin-top: var(--space-6);">
          <!-- Honeypot anti-spam trap (invisible to humans, filled by automated spambots) -->
          <div style="display:none !important; position:absolute; left:-9999px;" aria-hidden="true">
            <label for="_hp_company">Empresa / Sitio web:</label>
            <input type="text" name="_hp_company" id="_hp_company" tabindex="-1" autocomplete="off" value="">
          </div>

          <!-- Cryptographic anti-replay token and client timing metadata -->
          <input type="hidden" name="token" id="proposal-token" value="">
          <input type="hidden" name="completion_time_ms" id="completion-time" value="0">

          <div style="margin-bottom: var(--space-4);">
            <label for="proposal-category" style="display: block; font-weight: bold; margin-bottom: var(--space-2);">
              Categoría de la propuesta:
            </label>
            <select id="proposal-category" name="category" class="filter-select" style="width: 100%; min-height: 44px; padding: var(--space-2) var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-sm); font-size: var(--font-size-base); background-color: var(--color-bg-surface); color: var(--color-text-primary);">
              <option value="general">General</option>
              <option value="comparator">Comparador de medidas</option>
              <option value="sources">Fuentes y citas originales</option>
              <option value="ui">Diseño, contraste y usabilidad</option>
              <option value="methodology">Metodología y criterios neutrales</option>
            </select>
          </div>

          <div style="margin-bottom: var(--space-4);">
            <label for="proposal-text" style="display: block; font-weight: bold; margin-bottom: var(--space-2);">
              Tu propuesta de mejora:
            </label>
            <textarea id="proposal-text" name="text" rows="5" minlength="10" maxlength="600" required placeholder="Describe qué cambio, función o ajuste propones..." style="width: 100%; box-sizing: border-box; padding: var(--space-3); border: 1px solid var(--color-border); border-radius: var(--radius-sm); font-family: inherit; font-size: var(--font-size-base); background-color: var(--color-bg-surface); color: var(--color-text-primary); resize: vertical;"></textarea>
            <div id="char-counter" style="font-size: var(--font-size-sm); color: var(--color-text-secondary); margin-top: var(--space-1);" aria-live="polite">
              0 / 600 caracteres (mínimo 10)
            </div>
          </div>

          <div id="proposal-feedback-msg" style="display: none; margin-bottom: var(--space-4); padding: var(--space-3); border-radius: var(--radius-sm);" role="status"></div>

          <div style="display: flex; gap: var(--space-3); flex-wrap: wrap; align-items: center;">
            <button type="submit" id="proposal-submit-btn" class="nav-link" style="min-height: 44px; padding: 0 var(--space-6); background-color: var(--color-text-primary); color: var(--color-bg-canvas); border: none; cursor: pointer; font-weight: bold;" disabled aria-disabled="true">
              Enviar propuesta
            </button>
            <a href="../" class="nav-link" style="min-height: 44px; display: inline-flex; align-items: center; padding: 0 var(--space-4);">
              Cancelar
            </a>
          </div>
        </form>

        <div id="proposal-success-card" style="display: none; margin-top: var(--space-4);" role="status" aria-live="polite">
          <div class="party-caveat" style="border-left-color: #107c41;">
            <h2 style="font-size: var(--font-size-base); margin: 0 0 var(--space-2); color: var(--color-text-primary);">¡Muchas gracias por tu idea!</h2>
            <p style="margin: 0 0 var(--space-3);">Hemos registrado tu propuesta en nuestro buzón. El equipo la revisará periódicamente para valorar su incorporación al comparador.</p>
            <a href="../" class="nav-link" style="display: inline-flex; min-height: 44px; align-items: center; font-weight: bold;">← Volver al comparador</a>
          </div>
        </div>
      </article>
    </section>

    <script>
      (function() {{
        var form = document.getElementById('proposal-form');
        var textarea = document.getElementById('proposal-text');
        var counter = document.getElementById('char-counter');
        var submitBtn = document.getElementById('proposal-submit-btn');
        var feedbackMsg = document.getElementById('proposal-feedback-msg');
        var successCard = document.getElementById('proposal-success-card');
        var tokenInput = document.getElementById('proposal-token');
        var timeInput = document.getElementById('completion-time');

        if (!form || !textarea) return;

        var startTime = Date.now();
        var cooldownKey = 'elecciones_proposal_cooldown';
        var lastSubmission = localStorage.getItem(cooldownKey);

        if (lastSubmission && (Date.now() - parseInt(lastSubmission, 10) < 300000)) {{
          if (feedbackMsg) {{
            feedbackMsg.style.display = 'block';
            feedbackMsg.style.backgroundColor = 'var(--color-bg-surface)';
            feedbackMsg.style.border = '1px solid var(--color-border)';
            feedbackMsg.textContent = 'Ya has enviado una propuesta recientemente. Por favor, espera unos minutos antes de enviar otra.';
          }}
        }}

        fetch('/api/propuestas/token', {{ method: 'GET' }})
          .then(function(res) {{ return res.json(); }})
          .then(function(data) {{
            if (data && data.token && tokenInput) {{
              tokenInput.value = data.token;
            }}
          }})
          .catch(function() {{
            if (tokenInput && !tokenInput.value) {{
              tokenInput.value = Math.floor(Date.now() / 1000) + '.' + Math.random().toString(36).substring(2);
            }}
          }});

        textarea.addEventListener('input', function() {{
          var len = textarea.value.trim().length;
          counter.textContent = len + ' / 600 caracteres (mínimo 10)';
          if (len >= 10 && len <= 600) {{
            submitBtn.removeAttribute('disabled');
            submitBtn.setAttribute('aria-disabled', 'false');
          }} else {{
            submitBtn.setAttribute('disabled', 'disabled');
            submitBtn.setAttribute('aria-disabled', 'true');
          }}
        }});

        form.addEventListener('submit', function(e) {{
          e.preventDefault();
          var len = textarea.value.trim().length;
          if (len < 10 || len > 600) return;

          submitBtn.setAttribute('disabled', 'disabled');
          submitBtn.textContent = 'Enviando propuesta...';
          timeInput.value = Date.now() - startTime;

          var payload = {{
            text: textarea.value,
            category: document.getElementById('proposal-category').value,
            completion_time_ms: parseInt(timeInput.value, 10),
            honeypot: document.getElementById('_hp_company').value,
            token: tokenInput.value
          }};

          fetch('/api/propuestas', {{
            method: 'POST',
            headers: {{
              'Content-Type': 'application/json; charset=utf-8',
              'X-Requested-With': 'Elections2026-Feedback'
            }},
            body: JSON.stringify(payload)
          }})
          .then(function(response) {{
            return response.json().then(function(data) {{
              return {{ status: response.status, data: data }};
            }});
          }})
          .then(function(res) {{
            if (res.status === 201 || (res.data && res.data.success)) {{
              localStorage.setItem(cooldownKey, Date.now().toString());
              form.style.display = 'none';
              if (successCard) successCard.style.display = 'block';
            }} else {{
              submitBtn.removeAttribute('disabled');
              submitBtn.textContent = 'Enviar propuesta';
              if (feedbackMsg) {{
                feedbackMsg.style.display = 'block';
                feedbackMsg.style.backgroundColor = '#fde7e9';
                feedbackMsg.style.color = '#a80000';
                feedbackMsg.textContent = (res.data && res.data.user_message_es) || 'No se pudo enviar la propuesta. Inténtalo de nuevo más tarde.';
              }}
            }}
          }})
          .catch(function() {{
            submitBtn.removeAttribute('disabled');
            submitBtn.textContent = 'Enviar propuesta';
            if (feedbackMsg) {{
              feedbackMsg.style.display = 'block';
              feedbackMsg.style.backgroundColor = '#fde7e9';
              feedbackMsg.style.color = '#a80000';
              feedbackMsg.textContent = 'Error de conexión. Por favor, comprueba tu conexión y vuelve a intentarlo.';
            }}
          }});
        }});
      }})();
    </script>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/propuestas/",
        content=content,
        root_path="../",
    )



def render_sitemap(ctx: SiteContext, routes: list[tuple[str, str, str]]) -> str:
    """Render accurate sitemap.xml with all canonical routes and priorities."""
    entries = []
    # Sort deterministically by URL
    for loc, lastmod, freq in sorted(routes, key=lambda r: r[0]):
        norm_loc = loc.rstrip("/")
        norm_base = ctx.canonical_base.rstrip("/")
        if norm_loc == norm_base:
            priority = "1.0"
        elif "/temas/" in loc:
            priority = "0.9"
        elif "/partidos/" in loc:
            priority = "0.8"
        elif "/metodo/" in loc or "/fuentes/" in loc:
            priority = "0.7"
        else:
            priority = "0.6"

        entries.append(f"""  <url>
    <loc>{escape(loc)}</loc>
    <lastmod>{escape(lastmod)}</lastmod>
    <changefreq>{escape(freq)}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(entries)}
</urlset>
"""


def render_robots_txt(ctx: SiteContext) -> str:
    """Render robots.txt policy with sitemap reference."""
    return f"""User-agent: *
Allow: /
Disallow: /preview/

Sitemap: {ctx.canonical_base}/sitemap.xml
"""


def render_security_txt(ctx: SiteContext) -> str:
    """Render standard RFC 9116 security.txt contact file."""
    return f"""Contact: mailto:seguridad@elecciones2026.es
Expires: 2026-12-31T23:59:59.000Z
Preferred-Languages: es, en
Canonical: {ctx.canonical_base}/.well-known/security.txt
"""


def render_llms_txt(ctx: SiteContext) -> str:
    """Render standard /llms.txt specification for AI models and search engines."""
    pilot = ctx.election_id == "es-gen-2023"
    title_suffix = " · Generales 2023 (Ensayo piloto)" if pilot else " · Elecciones Generales 2026"
    election_title = f"# Comparador de Programas Electorales{title_suffix}"

    if pilot:
        summary_intro = (
            "> Ensayo técnico y metodológico privado con programas de las Elecciones Generales de 2023 (23J). "
            "Datos de ensayo con revisión de derechos y humana en curso. Estricto aislamiento respecto a 2026."
        )
    else:
        summary_intro = (
            "> Comparador neutral e independiente de programas electorales para las Elecciones Generales del 29 de noviembre de 2026 en España (BOE-A-2026-20742). "
            "Trazabilidad a fuentes oficiales, revisión humana y ausencia de recomendaciones de voto."
        )

    topic_lines = []
    for t in ctx.taxonomy.topics:
        topic_lines.append(f"- [{t.name_es}]({ctx.canonical_base}/temas/{t.id}/): {t.description_es}")

    party_lines = []
    for pid in sorted(ctx.parties.keys()):
        p = ctx.parties[pid]
        party_lines.append(f"- [{p.display_name} ({p.short_name})]({ctx.canonical_base}/partidos/{pid}/): {p.official_name}")

    query_example = (
        f"{ctx.canonical_base}/?election=es-gen-2023&topic=housing&partyA=pp&partyB=erc"
        if pilot
        else f"{ctx.canonical_base}/?topic=housing&partyA=pp&partyB=psoe"
    )
    review_rule = (
        "Los resúmenes sin cita literal requieren una aprobación humana. Las citas literales y las relaciones entre propuestas requieren dos revisiones independientes."
        if ctx.production_records and not pilot
        else "Toda afirmación o relación comparada requiere la verificación de dos revisores independientes antes de su publicación."
    )

    content = f"""{election_title}
{summary_intro}

## Principios y Metodología
- Neutralidad política estricta: Este proyecto no califica partidos, no emite recomendaciones de voto y no elabora sondeos.
- Trazabilidad documental: Cada afirmación publicada enlaza al documento original, versión registrada, página o sección y fecha de revisión.
- Citas literales y derechos de autor: Citas breves con estricto fin de análisis y contraste, conforme al artículo 32 del Texto Refundido de la Ley de Propiedad Intelectual (TRLPI).
- Transparencia en lagunas: La ausencia de una medida en el programa («no consta») nunca se interpreta como oposición política ni como apoyo tácito.
- Integridad de datos: Verificación criptográfica mediante sumas SHA-256 de los documentos fuente en formato PDF original.
- Revisión editorial: {review_rule}

## Páginas Principales
- [Inicio y Comparador]({ctx.canonical_base}/): Comparador interactivo de medidas políticas por tema y candidatura.
- [Metodología de Verificación]({ctx.canonical_base}/metodo/): Criterios objetivos de inclusión de candidaturas (Criterios A y B), límites de cita y política de rectificación.
- [Registro de Fuentes Oficiales]({ctx.canonical_base}/fuentes/): Inventario de fuentes registradas, hashes SHA-256 y estados de cobertura.
- [Registro de Correcciones Editoriales]({ctx.canonical_base}/correcciones/): Historial auditable de correcciones y tiempos de respuesta (SLAs Sev-1, Sev-2, Sev-3).
- [Índice de Temas]({ctx.canonical_base}/temas/): Los {len(ctx.taxonomy.topics)} temas de la taxonomía de comparación.
- [Índice de Candidaturas]({ctx.canonical_base}/partidos/): Candidaturas monitorizadas según criterios objetivos de representación.

## Temas Electorales
{"".join(f"{line}\n" for line in topic_lines)}
## Candidaturas Monitorizadas
{"".join(f"{line}\n" for line in party_lines)}
## Sintaxis de Consulta para LLMs y Comparativas
Para contrastar dos candidaturas sobre un tema específico, utiliza el comparador con los parámetros normalizados:
`{query_example}`

Parámetros admitidos:
- `topic`: Identificador del tema oficial (ej. `housing`, `education`, `health-social-services`, `economy-work-tax`, `immigration`, `foreign-policy-eu`, `climate-energy`, `institutions-rights`).
- `partyA`: Identificador de la primera candidatura.
- `partyB`: Identificador de la segunda candidatura (debe ser distinta de `partyA`).

## Formato Completo para LLMs
Para acceder a la transcripción textual completa de taxonomías, candidaturas y propuestas verificadas:
- [Archivo completo para LLMs]({ctx.canonical_base}/llms-full.txt)
"""
    return content.strip() + "\n"


def render_llms_full_txt(ctx: SiteContext) -> str:
    """Render comprehensive /llms-full.txt containing full structured dataset for LLM grounding."""
    pilot = ctx.election_id == "es-gen-2023"
    title_suffix = " · Generales 2023 (Ensayo piloto)" if pilot else " · Elecciones Generales 2026"

    sections = [
        f"# Archivo Integral de Datos Electorales{title_suffix}",
        f"Fecha de compilación: {ctx.build_date} | Elección: {ctx.election_id} | URL canónica: {ctx.canonical_base}/",
        "",
        "## 1. Taxonomía Temática y Subtemas",
    ]

    for t in ctx.taxonomy.topics:
        sections.append(f"### Tema: {t.name_es} (`{t.id}`)")
        sections.append(f"{t.description_es}")
        sections.append("Subtemas:")
        for sub in t.subtopics:
            sections.append(f"- `{sub.id}`: {sub.name_es}")
        sections.append("")

    sections.append("## 2. Candidaturas y Fuentes Oficiales Registradas")
    for pid in sorted(ctx.parties.keys()):
        p = ctx.parties[pid]
        src = next((s for s in ctx.register.sources if s.party_id == pid and s.election_id == ctx.election_id), None)
        sections.append(f"### Candidatura: {p.display_name} (`{p.id}`)")
        sections.append(f"- {'Nombre registrado' if ctx.production_records else 'Nombre oficial'}: {p.official_name}")
        sections.append(f"- Siglas: {p.short_name}")
        sections.append(f"- Ámbito territorial: {'Pendiente de verificación' if p.territorial_scope == 'pending_verification' else p.territorial_scope}")
        sections.append(f"- Criterio de inclusión: {'Pendiente de verificación' if p.inclusion_criterion == 'pending_verification' else p.inclusion_criterion}")
        if src:
            sections.append(f"- Estado del programa: {src.status}")
            sections.append(f"- URL oficial: {src.official_url or 'No disponible'}")
            sections.append(f"- Versión: {src.version}")
            sections.append(f"- Fecha de consulta: {src.retrieval_date}")
            sections.append(f"- Hash SHA-256: {src.sha256 or 'Pendiente de verificación'}")
            sections.append(f"- Derechos de cita: {src.rights_review.status}")
        else:
            sections.append("- Estado del programa: missing (no disponible)")
        sections.append("")

    sections.append("## 3. Posiciones y Afirmaciones Electorales Verificadas")
    active_stmts = sorted(ctx.statements.values(), key=lambda s: (s.topic_id, s.party_id, s.id))
    if not active_stmts:
        sections.append("No hay posiciones publicadas o aprobadas en esta versión.")
    else:
        for s in active_stmts:
            sections.append(f"### Afirmación `{s.id}`: {s.party_id} en `{s.topic_id}` / `{s.subtopic_id}`")
            sections.append(f"- Tipo: {s.statement_type}")
            sections.append(f"- Resumen neutral: {s.summary}")
            if s.quote:
                sections.append(f"- Cita literal: «{s.quote}»")
            if s.qualifications:
                for q in s.qualifications:
                    sections.append(f"- Matiz / condición: {q}")
            last_rev = getattr(s, "last_reviewed_date", getattr(s, "last_reviewed", None))
            sections.append(f"- Estado de revisión: {s.review_status} (Última revisión: {last_rev or 'N/A'})")
            sections.append("")

    sections.append("## 4. Relaciones Comparativas Verificadas entre Candidaturas")
    active_rels = [r for r in ctx.relationships.values() if r.status == "active"]
    if not active_rels:
        sections.append("No hay relaciones comparativas activas en esta versión.")
    else:
        for r in sorted(active_rels, key=lambda x: (x.topic_id, x.measure_label)):
            sections.append(f"### Comparativa `{r.id}`: {r.measure_label} (`{r.topic_id}` / `{r.subtopic_id}`)")
            sections.append(f"- Partidos comparados: {', '.join(r.party_ids)}")
            sections.append(f"- Tipo de relación: {r.relationship_type}")
            sections.append(f"- Resumen comparativo: {r.summary}")
            if r.differences:
                sections.append("- Diferencias identificadas:")
                for diff in r.differences:
                    sections.append(f"  * {diff}")
            sections.append(f"- Afirmaciones fuente vinculadas: {', '.join(r.statement_ids)}")
            sections.append("")

    sections.append("## 5. Criterios de Calidad y Rectificación")
    sections.append("- Criterio de inclusión A: Representación parlamentaria obtenida en las anteriores Cortes Generales o Parlamento Europeo.")
    sections.append("- Criterio de inclusión B: Candidaturas proclamadas que alcancen al menos el 50% del censo electoral estatal.")
    sections.append("- Niveles de rectificación: Sev-1 (crítica, resolución <= 12h), Sev-2 (grave, <= 24h), Sev-3 (menor, <= 48h).")
    sections.append("- Cualquier rectificación sobre una afirmación fuente invalida automáticamente las relaciones comparativas derivadas.")
    sections.append("- Contacto editorial: editorial@elecciones2026.es")

    return "\n".join(sections).strip() + "\n"


# ==============================================================================
# Build Execution & File Generation
# ==============================================================================

def write_file_deterministic(path: Path, content: str) -> None:
    """Write text file using UTF-8 and standard Unix newlines."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def compute_sha256(path: Path) -> str:
    """Compute SHA-256 digest of file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def reject_private_source_artifacts(directory: Path) -> None:
    """Fail before copying private source bundles into a public artifact."""
    private_names = {"original.pdf", "retrieval.json", "pages.json", "review.md"}
    for path in directory.rglob("*"):
        if path.name in private_names or path.suffix.lower() == ".pdf":
            raise ValueError(f"Private source artifact cannot enter static output: {path.relative_to(directory)}")


def reject_symlink_output_path(output_dir: Path) -> None:
    """Reject caller-selected symlinks before creating publication directories."""
    for path in (output_dir.absolute(), *output_dir.absolute().parents):
        if path.is_symlink():
            # macOS exposes these system directories through fixed OS aliases.
            system_alias = (sys.platform == "darwin" and str(path) in {"/var", "/tmp"}
                            and str(path.resolve()) == f"/private{path}")
            if not system_alias:
                raise BuildValidationError("Output directory and its parents must not be symlinks.")


def publish_directory(staging_dir: Path, output_dir: Path) -> None:
    """Replace the full artifact and restore its predecessor if the switch fails.

    A two-rename switch can briefly leave the path absent. It never exposes a
    mixed tree. This offline builder is not a live hosting release controller.
    """
    reject_symlink_output_path(output_dir)
    if output_dir.is_symlink() or staging_dir.is_symlink():
        raise BuildValidationError("Publication directories must not be symlinks.")
    if any(p.is_symlink() for p in staging_dir.rglob("*")):
        raise BuildValidationError("Candidate artifact must not contain symlinks.")
    backup = Path(tempfile.mkdtemp(prefix=f".previous_{output_dir.name}_", dir=output_dir.parent))
    backup.rmdir()
    moved_previous = False
    switched = False
    try:
        if output_dir.exists():
            output_dir.rename(backup)
            moved_previous = True
        try:
            staging_dir.rename(output_dir)
            switched = True
        except BaseException:
            if moved_previous:
                backup.rename(output_dir)
            raise
    finally:
        # If recovery itself failed, retain the previous artifact for inspection.
        if switched and backup.exists():
            shutil.rmtree(backup, ignore_errors=True)


def build_site(
    root_dir: Path,
    output_dir: Path,
    content_dir: Optional[Path] = None,
    election_id: str = DEFAULT_ELECTION_ID,
    canonical_base: str = DEFAULT_CANONICAL_BASE,
    build_date: Optional[str] = None,
    strict_approved: bool = True,
    custom_statements: Optional[list[StatementRecord]] = None,
    custom_relationships: Optional[list[RelationshipRecord]] = None,
    budget_bundle: Optional[Path] = None,
    quiz_mode: str = "unavailable",
    quiz_file: Optional[Path] = None,
    simulator_mode: str = "unavailable",
    simulator_file: Optional[Path] = None,
    pilot_provisional: bool = False,
    records_dir: Optional[Path] = None,
    strict_budget: Optional[bool] = None,
) -> SiteBuildResult:
    """Generate the complete static site deterministically into output_dir.

    Uses an atomic staging directory to ensure that any validation failure
    aborts without creating a partially published site.
    """
    if strict_budget is None:
        strict_budget = strict_approved
    if pilot_provisional and (election_id != "es-gen-2023" or quiz_mode != "unavailable"):
        raise BuildValidationError("Provisional pilot is limited to the private 2023 build without the standard quiz.")
    budget_manifest, budget_payload = None, None
    if budget_bundle is not None:
        from elecciones2026.budget import BudgetError, load_bundle
        try:
            budget_manifest, budget_payload = load_bundle(
                budget_bundle,
                (content_dir or root_dir / "content") / "taxonomy.json",
                require_publication=strict_budget,
            )
        except (BudgetError, ValueError, KeyError, OSError) as error:
            raise BuildValidationError(f"Budget validation failed: {error}") from error

    ctx = load_and_validate_site_data(
        root_dir=root_dir,
        content_dir=content_dir,
        election_id=election_id,
        canonical_base=canonical_base,
        build_date=build_date,
        strict_approved=strict_approved,
        custom_statements=custom_statements,
        custom_relationships=custom_relationships,
        records_dir=records_dir,
    )

    ctx.budget_payload = budget_payload
    ctx.budget_manifest = budget_manifest
    ctx.budget_bundle_id = Path(budget_bundle).name if budget_bundle is not None else None
    budget_projections = {}
    if budget_payload is not None:
        from elecciones2026.budget import canonical, digest
        from elecciones2026.budget_view import topic_projection
        budget_projections = {topic.id: topic_projection(budget_payload, budget_manifest, topic.id)
                              for topic in ctx.taxonomy.topics}
        ctx.budget_projection_id = digest(canonical(budget_projections))

    from elecciones2026.quiz import QuizValidationError, prepare_quiz, render_quiz_content
    if quiz_mode not in {"unavailable", "mock", "reviewed", "exploratory"}:
        raise BuildValidationError("Invalid quiz mode.")
    quiz_bundle = None
    exploratory_bundle = None
    if quiz_mode == "exploratory":
        from elecciones2026.quiz_exploratory import (
            ExploratoryQuizError,
            validate_exploratory_bank,
            render_exploratory_quiz_content,
        )
        exploratory_path = (
            quiz_file
            or (records_dir / "quiz-bank.json" if records_dir else None)
            or (ctx.content_dir / "quiz-bank.json")
            or (ctx.content_dir / "elections" / ctx.election_id / "quiz-bank.json")
        )
        if exploratory_path and exploratory_path.exists():
            try:
                raw_exploratory = json.loads(exploratory_path.read_text(encoding="utf-8"))
                exploratory_bundle = validate_exploratory_bank(raw_exploratory, ctx)
            except (ValueError, OSError, ExploratoryQuizError) as error:
                raise BuildValidationError(f"Exploratory quiz validation failed: {error}") from error
        else:
            quiz_mode = "unavailable"
    elif quiz_mode != "unavailable":
        quiz_path = quiz_file or (ctx.content_dir / "quiz" / f"{quiz_mode}.json")
        try:
            quiz_ctx = ctx
            if quiz_mode == "mock" and quiz_file is None:
                # The bundled demonstration uses the shared core taxonomy.
                quiz_ctx = replace(ctx, taxonomy=load_taxonomy(ctx.content_dir / "taxonomy.json"))
            quiz_bundle = prepare_quiz(quiz_path, quiz_ctx, mock=quiz_mode == "mock")
        except (ValueError, OSError, QuizValidationError) as error:
            raise BuildValidationError(f"Quiz validation failed: {error}") from error

    from elecciones2026.simulator import SimulatorValidationError, prepare_simulator, render_simulator_content
    if simulator_mode not in {"unavailable", "mock", "reviewed"}:
        raise BuildValidationError("Invalid simulator mode.")
    simulator_bundle = None
    if simulator_mode != "unavailable":
        simulator_path = simulator_file or (ctx.content_dir / "simulator" / f"{simulator_mode}.json")
        if not simulator_path.exists() and simulator_mode == "reviewed":
            simulator_path = ctx.content_dir / "simulator" / "rules.json"
        try:
            simulator_bundle = prepare_simulator(simulator_path, ctx, mock=simulator_mode == "mock")
        except (ValueError, OSError, SimulatorValidationError) as error:
            raise BuildValidationError(f"Simulator validation failed: {error}") from error


    # Use a private sibling directory so rename stays on the output filesystem.
    reject_symlink_output_path(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_dir.is_symlink():
        raise BuildValidationError("Output directory must not be a symlink.")
    staging_dir = Path(tempfile.mkdtemp(prefix=f".tmp_{output_dir.name}_", dir=output_dir.parent))

    try:
        routes: list[tuple[str, str, str]] = []

        # 1. Home page (/)
        home_html = render_home_page(ctx)
        write_file_deterministic(staging_dir / "index.html", home_html)
        routes.append((f"{ctx.canonical_base}/", ctx.build_date, "daily"))

        # 2. Topics index (/temas/)
        topics_idx_html = render_topic_index(ctx)
        write_file_deterministic(staging_dir / "temas" / "index.html", topics_idx_html)
        routes.append((f"{ctx.canonical_base}/temas/", ctx.build_date, "daily"))

        # 3. Topic detail pages (/temas/{topic_id}/)
        for topic in ctx.taxonomy.topics:
            t_html = render_topic_detail(ctx, topic)
            write_file_deterministic(staging_dir / "temas" / topic.id / "index.html", t_html)
            routes.append((f"{ctx.canonical_base}/temas/{topic.id}/", ctx.build_date, "daily"))

        # 4. Parties index (/partidos/)
        parties_idx_html = render_party_index(ctx)
        write_file_deterministic(staging_dir / "partidos" / "index.html", parties_idx_html)
        routes.append((f"{ctx.canonical_base}/partidos/", ctx.build_date, "daily"))

        # 5. Party detail pages (/partidos/{party_id}/)
        for pid, party in sorted(ctx.parties.items()):
            p_html = render_party_detail(ctx, party)
            write_file_deterministic(staging_dir / "partidos" / pid / "index.html", p_html)
            routes.append((f"{ctx.canonical_base}/partidos/{pid}/", ctx.build_date, "daily"))

        # 6. Methodology page (/metodo/)
        method_html = render_methodology_page(ctx)
        write_file_deterministic(staging_dir / "metodo" / "index.html", method_html)
        routes.append((f"{ctx.canonical_base}/metodo/", ctx.build_date, "weekly"))

        # 7. Sources page (/fuentes/)
        sources_html = render_sources_page(ctx)
        write_file_deterministic(staging_dir / "fuentes" / "index.html", sources_html)
        routes.append((f"{ctx.canonical_base}/fuentes/", ctx.build_date, "daily"))

        # 8. Corrections page (/correcciones/)
        corr_html = render_corrections_page(ctx)
        write_file_deterministic(staging_dir / "correcciones" / "index.html", corr_html)
        routes.append((f"{ctx.canonical_base}/correcciones/", ctx.build_date, "daily"))

        # 9. Proposals page (/propuestas/) - only for 2026 application
        if ctx.election_id != "es-gen-2023":
            proposals_html = render_proposals_page(ctx)
            write_file_deterministic(staging_dir / "propuestas" / "index.html", proposals_html)
            routes.append((f"{ctx.canonical_base}/propuestas/", ctx.build_date, "weekly"))

        if budget_bundle is not None:
            from elecciones2026.budget import copy_reviewed_bundle
            try:
                copy_reviewed_bundle(budget_bundle, staging_dir, ctx.content_dir / "taxonomy.json",
                                     expected_manifest=ctx.budget_manifest,
                                     require_publication=strict_budget)
            except (BudgetError, ValueError, KeyError, OSError) as error:
                raise BuildValidationError(f"Budget staging failed: {error}") from error

        if ctx.budget_payload is not None:
            from elecciones2026.budget import canonical
            from elecciones2026.budget_view import render_budget_content, topic_projection
            from elecciones2026.budget_chart import share_svg
            labels = {topic.id: topic.name_es for topic in ctx.taxonomy.topics}
            chart_svg = share_svg(ctx.budget_payload, ctx.budget_manifest, ctx.budget_bundle_id)
            chart_id = hashlib.sha256(chart_svg.encode('utf-8')).hexdigest()
            chart_path = f"static/budget-charts/{chart_id}/grafico.svg"
            write_file_deterministic(staging_dir / chart_path, chart_svg)
            budget_content = render_budget_content(ctx.budget_payload, ctx.budget_manifest, ctx.budget_bundle_id, labels,
                                                   chart_url='../../' + chart_path)
            budget_html = render_base(ctx, "PGE 2023: presupuesto aprobado · Contexto histórico",
                                     "Presupuesto aprobado consolidado de 2023, capítulos 1–8. Contexto histórico con fuentes oficiales.",
                                     "/presupuestos/2023/", budget_content + render_share_controls(ctx)
                                     + '<script src="../../sharing.js" defer></script><script src="../../budget-chart.js" defer></script>', "../../")
            write_file_deterministic(staging_dir / "presupuestos/2023/index.html", budget_html)
            routes.append((f"{ctx.canonical_base}/presupuestos/2023/", ctx.build_date, "yearly"))
            for topic in ctx.taxonomy.topics:
                projection = budget_projections[topic.id]
                target = staging_dir / "static/budget-topics" / ctx.budget_projection_id / f"{topic.id}.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(canonical(projection))
            shutil.copy2(root_dir / "site/budget-context.js", staging_dir / "budget-context.js")
            from elecciones2026.budget_view import copy_stylesheet
            copy_stylesheet(root_dir / "site", staging_dir)
            shutil.copy2(root_dir / "site/budget-chart.js", staging_dir / "budget-chart.js")

        # Quiz authoring records stay private; only validated public fields enter the bundle.
        quiz_style = root_dir / "site" / "quiz.css"
        quiz_style_name = f"quiz.{compute_sha256(quiz_style)[:16]}.css"
        shutil.copy2(quiz_style, staging_dir / quiz_style_name)
        quiz_scripts = []
        if exploratory_bundle is not None and exploratory_bundle.get("available"):
            source = root_dir / "site" / "quiz-exploratory.js"
            target = f"{source.stem}.{compute_sha256(source)[:16]}{source.suffix}"
            shutil.copy2(source, staging_dir / target)
            encoded = json.dumps(exploratory_bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            bundle_script = f"window.QuizExploratoryBundle = {encoded};\n"
            digest = hashlib.sha256(bundle_script.encode()).hexdigest()[:16]
            bundle_name = f"quiz-exploratory-data.{digest}.js"
            write_file_deterministic(staging_dir / bundle_name, bundle_script)
            quiz_scripts = [bundle_name, target]
            quiz_content = render_exploratory_quiz_content()
            quiz_title = "Cuestionario de propuestas · Elecciones 2026"
            quiz_description = "Explora propuestas de los programas electorales del 29-N y consulta sus fuentes directas sin calcular afinidad partidista."
        elif quiz_bundle is not None and quiz_bundle["available"]:
            for name in ("quiz-engine.js", "quiz-ui.js"):
                source = root_dir / "site" / name
                target = f"{source.stem}.{compute_sha256(source)[:16]}{source.suffix}"
                shutil.copy2(source, staging_dir / target)
                quiz_scripts.append(target)
            encoded = json.dumps(quiz_bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            bundle_script = f"window.QuizBundle = {encoded};\n"
            digest = hashlib.sha256(bundle_script.encode()).hexdigest()[:16]
            bundle_name = f"quiz-data.{digest}.js"
            write_file_deterministic(staging_dir / bundle_name, bundle_script)
            quiz_scripts.insert(0, bundle_name)
            quiz_content = render_quiz_content(quiz_bundle)
            quiz_title = "Cuestionario de coincidencia"
            quiz_description = ("Demostración privada con datos ficticios. No representa programas reales."
                                if quiz_mode == "mock" else "Coincidencia con medidas revisadas.")
        else:
            quiz_content = render_quiz_content(quiz_bundle)
            quiz_title = "Cuestionario de coincidencia"
            quiz_description = "El cuestionario aún no está disponible."

        quiz_content += ''.join(f'<script src="../{name}" defer></script>\n' for name in quiz_scripts)
        quiz_html = render_base(ctx, quiz_title, quiz_description,
                                "/cuestionario/", quiz_content, root_path="../")
        # Fetch imported design tokens with the main stylesheet, avoiding a
        # second stylesheet request round trip before the local quiz can start.
        quiz_html = quiz_html.replace('<link rel="stylesheet" href="../styles.css">',
            '<link rel="preload" href="../tokens/tokens.css" as="style">\n'
            '  <link rel="stylesheet" href="../styles.css">')
        quiz_html = quiz_html.replace('</head>', f'<link rel="stylesheet" href="../{quiz_style_name}">\n</head>')
        quiz_html = quiz_html.replace('<meta charset="utf-8">',
            '<meta charset="utf-8">\n<meta name="referrer" content="no-referrer">'
            f'\n<link rel="icon" href="../{preview_image_path(root_dir)}">')
        if quiz_mode not in {"reviewed", "exploratory"}:
            quiz_html = quiz_html.replace('<meta charset="utf-8">',
                '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">')
        else:
            routes.append((f"{ctx.canonical_base}/cuestionario/", ctx.build_date, "weekly"))
        write_file_deterministic(staging_dir / "cuestionario" / "index.html", quiz_html)

        # Simulator assets and shell
        simulator_style = root_dir / "site" / "simulator.css"
        simulator_style_name = f"simulator.{compute_sha256(simulator_style)[:16]}.css"
        shutil.copy2(simulator_style, staging_dir / simulator_style_name)
        simulator_scripts = []
        if simulator_bundle is not None and simulator_bundle.get("available"):
            for name in ("simulator-engine.js", "simulator-ui.js"):
                source = root_dir / "site" / name
                target = f"{source.stem}.{compute_sha256(source)[:16]}{source.suffix}"
                shutil.copy2(source, staging_dir / target)
                simulator_scripts.append(target)
            encoded = json.dumps(simulator_bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            bundle_script = f"window.SimulatorProfile = {encoded};\n"
            digest = hashlib.sha256(bundle_script.encode()).hexdigest()[:16]
            bundle_name = f"simulator-data.{digest}.js"
            write_file_deterministic(staging_dir / bundle_name, bundle_script)
            simulator_scripts.insert(0, bundle_name)
        simulator_content = render_simulator_content(simulator_bundle, mode=simulator_mode)
        simulator_content += ''.join(f'<script src="../{name}" defer></script>\n' for name in simulator_scripts)
        simulator_description = ("Demostración técnica de simulación de escaños y mayorías."
                                 if simulator_mode == "mock" else "Simulador interactivo de escaños y coaliciones para el Congreso de los Diputados."
                                 if simulator_mode == "reviewed" else "Reglas parlamentarias y mayorías de investidura para el Congreso de los Diputados.")
        simulator_html = render_base(ctx, "Simulador de escaños y mayorías", simulator_description,
                                     "/simulador/", simulator_content, root_path="../")
        simulator_html = simulator_html.replace('<link rel="stylesheet" href="../styles.css">',
            '<link rel="preload" href="../tokens/tokens.css" as="style">\n'
            '  <link rel="stylesheet" href="../styles.css">')
        simulator_html = simulator_html.replace('</head>', f'<link rel="stylesheet" href="../{simulator_style_name}">\n</head>')
        simulator_html = simulator_html.replace('<meta charset="utf-8">',
            '<meta charset="utf-8">\n<meta name="referrer" content="no-referrer">'
            f'\n<link rel="icon" href="../{preview_image_path(root_dir)}">')
        if simulator_mode != "reviewed":
            simulator_html = simulator_html.replace('<meta charset="utf-8">',
                '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">')
        else:
            routes.append((f"{ctx.canonical_base}/simulador/", ctx.build_date, "weekly"))
        write_file_deterministic(staging_dir / "simulador" / "index.html", simulator_html)

        # 9. Sitemap & crawler files

        sitemap_xml = render_sitemap(ctx, routes)
        write_file_deterministic(staging_dir / "sitemap.xml", sitemap_xml)

        robots_txt = render_robots_txt(ctx)
        write_file_deterministic(staging_dir / "robots.txt", robots_txt)

        security_txt = render_security_txt(ctx)
        write_file_deterministic(staging_dir / "security.txt", security_txt)
        write_file_deterministic(staging_dir / ".well-known" / "security.txt", security_txt)

        llms_txt = render_llms_txt(ctx)
        write_file_deterministic(staging_dir / "llms.txt", llms_txt)

        llms_full_txt = render_llms_full_txt(ctx)
        write_file_deterministic(staging_dir / "llms-full.txt", llms_full_txt)

        # 10. Copy static stylesheets, scripts, and design tokens
        site_src = root_dir / "site"
        if (site_src / "styles.css").exists():
            shutil.copy2(site_src / "styles.css", staging_dir / "styles.css")
        if (site_src / "themes.css").exists():
            shutil.copy2(site_src / "themes.css", staging_dir / "themes.css")
        if (site_src / "tokens").exists():
            shutil.copytree(site_src / "tokens", staging_dir / "tokens", dirs_exist_ok=True)
        if (site_src / "app.js").exists():
            shutil.copy2(site_src / "app.js", staging_dir / "app.js")
        if (site_src / "pagination.js").exists():
            shutil.copy2(site_src / "pagination.js", staging_dir / "pagination.js")

        write_file_deterministic(staging_dir / comparison_bundle_name(ctx), comparison_bundle_script(ctx))
        shutil.copy2(site_src / "sharing.js", staging_dir / "sharing.js")

        preview_target = staging_dir / preview_image_path(root_dir)
        preview_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(site_src / "assets" / "social-preview.png", preview_target)

        if pilot_provisional:
            from elecciones2026.provisional2023 import write as write_provisional_pilot
            write_provisional_pilot(root_dir, staging_dir, ctx.canonical_base)

        # Do not copy accidentally misplaced private sources or retain them in output.
        reject_private_source_artifacts(staging_dir)
        if output_dir.exists():
            reject_private_source_artifacts(output_dir)
        # Hash the complete candidate before changing the published directory.
        publish_files = sorted(p for p in staging_dir.rglob("*") if p.is_file())
        candidate_hashes = {str(p.relative_to(staging_dir)): compute_sha256(p) for p in publish_files}
        publish_directory(staging_dir, output_dir)

        files_written = sorted(candidate_hashes)
        file_hashes = candidate_hashes

        return SiteBuildResult(
            output_dir=output_dir,
            build_date=ctx.build_date,
            election_id=ctx.election_id,
            files_written=files_written,
            file_hashes=file_hashes,
            topics_count=len(ctx.taxonomy.topics),
            parties_count=len(ctx.parties),
            statements_count=len(ctx.statements),
            relationships_count=len(ctx.relationships),
        )

    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def verify_determinism(
    root_dir: Path,
    content_dir: Optional[Path] = None,
    runs: int = 2,
) -> bool:
    """Verify that multiple builds from the same input yield identical byte-for-byte outputs."""
    scratch_dir = root_dir / ".tmp_determinism_test"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    build_results: list[SiteBuildResult] = []
    try:
        for i in range(runs):
            run_out = scratch_dir / f"run_{i}"
            res = build_site(
                root_dir=root_dir,
                output_dir=run_out,
                content_dir=content_dir,
                build_date=DEFAULT_BUILD_DATE,
            )
            build_results.append(res)

        # Compare results
        ref = build_results[0]
        for idx, other in enumerate(build_results[1:], start=1):
            if ref.files_written != other.files_written:
                diff = set(ref.files_written).symmetric_difference(set(other.files_written))
                raise AssertionError(f"Run {idx} file set differs: {diff}")
            for fname in ref.files_written:
                h_ref = ref.file_hashes[fname]
                h_other = other.file_hashes[fname]
                if h_ref != h_other:
                    raise AssertionError(f"Run {idx} hash mismatch for {fname}: {h_ref} != {h_other}")

        return True
    finally:
        if scratch_dir.exists():
            shutil.rmtree(scratch_dir, ignore_errors=True)


# ==============================================================================
# CLI Interface
# ==============================================================================

def main(args: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="elecciones2026.generator",
        description="Deterministic static site generator for Elecciones 2026.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: build
    build_p = subparsers.add_parser("build", help="Build static site.")
    build_p.add_argument("--root-dir", type=Path, default=Path.cwd(), help="Repository root directory.")
    build_p.add_argument("--content-dir", type=Path, default=None, help="Content directory (default: root/content).")
    build_p.add_argument("--output-dir", type=Path, default=Path("site"), help="Output directory (default: site).")
    build_p.add_argument("--build-date", type=str, default=None, help="Deterministic build date (YYYY-MM-DD).")
    build_p.add_argument("--election-id", type=str, default=DEFAULT_ELECTION_ID, help="Target election ID.")
    build_p.add_argument("--canonical-base", type=str, default=DEFAULT_CANONICAL_BASE, help="Canonical base URL.")
    build_p.add_argument("--strict", action="store_true", default=True, help="Enforce strict approved status.")
    build_p.add_argument("--no-strict", dest="strict", action="store_false", help="Disable strict review gates for private preview.")
    build_p.add_argument("--draft-budget", action="store_true", help="Allow draft budget bundle for preview.")
    build_p.add_argument("--budget-bundle", type=Path, help="Optional immutable budget bundle; requires human review.")
    build_p.add_argument("--quiz-mode", choices=("unavailable", "mock", "reviewed", "exploratory"), default=None,
                         help="Quiz mode: exploratory (2026 proposals), mock (fixture demo), reviewed (scored set), or unavailable.")
    build_p.add_argument("--quiz-file", type=Path, help="Versioned quiz authoring JSON.")
    build_p.add_argument("--simulator-mode", choices=("unavailable", "mock", "reviewed"), default="unavailable",
                         help="Simulator mode: unavailable (static info), mock (private preview), or reviewed.")
    build_p.add_argument("--simulator-file", type=Path, help="Versioned simulator profile JSON.")
    build_p.add_argument("--pilot-provisional", action="store_true", help="Private source-linked 2023 pilot only.")
    build_p.add_argument("--records-dir", type=Path, help="Production records directory; defaults to content/elections/es-gen-2026 for 2026 builds.")

    # Command: check-determinism
    det_p = subparsers.add_parser("check-determinism", help="Verify build determinism across repeated runs.")
    det_p.add_argument("--root-dir", type=Path, default=Path.cwd(), help="Repository root directory.")
    det_p.add_argument("--content-dir", type=Path, default=None, help="Content directory.")
    det_p.add_argument("--runs", type=int, default=2, help="Number of test runs (default: 2).")

    # Command: validate
    val_p = subparsers.add_parser("validate", help="Validate content dataset without writing output.")
    val_p.add_argument("--root-dir", type=Path, default=Path.cwd(), help="Repository root directory.")
    val_p.add_argument("--content-dir", type=Path, default=None, help="Content directory.")
    val_p.add_argument("--election-id", type=str, default=DEFAULT_ELECTION_ID, help="Target election ID.")
    val_p.add_argument("--records-dir", type=Path, help="Production records directory.")

    parsed = parser.parse_args(args)
    records_dir = getattr(parsed, "records_dir", None)
    if parsed.command in {"build", "validate"} and records_dir is None and parsed.election_id == "es-gen-2026":
        records_dir = (parsed.content_dir or parsed.root_dir / "content") / "elections" / parsed.election_id

    if parsed.command == "build":
        quiz_mode = parsed.quiz_mode
        if quiz_mode is None:
            if parsed.election_id == "es-gen-2026" and records_dir and (records_dir / "quiz-bank.json").exists():
                quiz_mode = "exploratory"
            else:
                quiz_mode = "unavailable"
        try:
            strict_budget = not parsed.draft_budget and parsed.strict
            res = build_site(
                root_dir=parsed.root_dir,
                output_dir=parsed.output_dir,
                content_dir=parsed.content_dir,
                election_id=parsed.election_id,
                canonical_base=parsed.canonical_base,
                build_date=parsed.build_date,
                strict_approved=parsed.strict,
                budget_bundle=parsed.budget_bundle,
                strict_budget=strict_budget,
                quiz_mode=quiz_mode,
                quiz_file=parsed.quiz_file,
                simulator_mode=parsed.simulator_mode,
                simulator_file=parsed.simulator_file,
                pilot_provisional=parsed.pilot_provisional,
                records_dir=records_dir,
            )
            print(f"Build completed successfully in {res.output_dir}:")
            print(f"  - Topics: {res.topics_count}")
            print(f"  - Parties: {res.parties_count}")
            print(f"  - Statements: {res.statements_count}")
            print(f"  - Relationships: {res.relationships_count}")
            print(f"  - Files written: {len(res.files_written)}")
            print(f"  - Build date: {res.build_date}")
            return 0
        except BuildValidationError as err:
            print(f"Build error: {err}", file=sys.stderr)
            return 1

    elif parsed.command == "check-determinism":
        try:
            verify_determinism(
                root_dir=parsed.root_dir,
                content_dir=parsed.content_dir,
                runs=parsed.runs,
            )
            print(f"Determinism verified across {parsed.runs} independent runs: outputs are byte-for-byte identical.")
            return 0
        except Exception as err:
            print(f"Determinism check failed: {err}", file=sys.stderr)
            return 1

    elif parsed.command == "validate":
        try:
            ctx = load_and_validate_site_data(
                root_dir=parsed.root_dir,
                content_dir=parsed.content_dir,
                election_id=parsed.election_id,
                records_dir=records_dir,
            )
            print(f"Data valid for election {ctx.election_id}:")
            print(f"  - {len(ctx.taxonomy.topics)} topics")
            print(f"  - {len(ctx.parties)} parties")
            print(f"  - {len(ctx.statements)} statements")
            print(f"  - {len(ctx.relationships)} relationships")
            return 0
        except BuildValidationError as err:
            print(f"Validation error: {err}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
