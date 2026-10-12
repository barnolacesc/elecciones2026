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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlsplit

from elecciones2026.editorial import (
    MAX_QUOTE_CHARS,
    MAX_QUOTE_WORDS,
    PERMITTED_QUOTE_RIGHTS,
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
) -> SiteContext:
    """Load and strictly validate all source records before publishing."""
    if content_dir is None:
        content_dir = root_dir / "content"

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
    if not taxonomy_file.exists():
        raise BuildValidationError(f"Taxonomy file missing: {taxonomy_file}")
    taxonomy = load_taxonomy(taxonomy_file)

    # 2. Load source register
    register_file = content_dir / "sources" / "register.json"
    if not register_file.exists():
        raise BuildValidationError(f"Source register missing: {register_file}")
    register = load_register(register_file)

    # 3. Load parties
    parties_file = content_dir / "examples" / "parties.json"
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
                territorial_scope=src.scope,
            )

    # For 2023 pilot rehearsal, restrict parties strictly to candidacies with 2023 sources
    if election_id == "es-gen-2023":
        pilot_party_ids = {s.party_id for s in register.sources if s.election_id == "es-gen-2023"}
        parties = {pid: p for pid, p in parties.items() if pid in pilot_party_ids}

    # 4. Load translations
    i18n_file = content_dir / "i18n" / "es.json"
    i18n = load_translations(i18n_file)

    # 5. Load statements
    statements: dict[str, StatementRecord] = {}
    if custom_statements is not None:
        for s in custom_statements:
            statements[s.id] = s
    else:
        stmt_dir = content_dir / "examples" / "statements"
        if stmt_dir.exists():
            for sf in sorted(stmt_dir.glob("*.json")):
                stmt = load_statement(sf)
                statements[stmt.id] = stmt

    # 6. Load relationships
    relationships: dict[str, RelationshipRecord] = {}
    if custom_relationships is not None:
        for r in custom_relationships:
            relationships[r.id] = r
    else:
        rel_dir = content_dir / "examples" / "relationships"
        if rel_dir.exists():
            for rf in sorted(rel_dir.glob("*.json")):
                rel = load_relationship(rf)
                relationships[rel.id] = rel

    # 7. Load corrections
    corrections: list[CorrectionRecord] = []
    corr_dir = content_dir / "examples" / "corrections"
    if corr_dir.exists():
        for cf in sorted(corr_dir.glob("*.json")):
            corrections.append(load_correction(cf))

    # Perform validation checks
    validation_errors: list[str] = []

    # Filter statements for the target election and validate review status
    filtered_statements: dict[str, StatementRecord] = {}
    for stmt_id, stmt in statements.items():
        if stmt.election_id != election_id:
            # Skip statements belonging to other elections for this build
            continue

        if election_id == "es-gen-2023":
            # Repository drafts are audit material, outside the publish set.
            # Explicit caller-supplied drafts still fail strict publication checks.
            if stmt.review_status != "approved" and custom_statements is None:
                continue
            validation_errors.extend(stmt.validate(target_election_id=election_id))
            if stmt.review_status != "approved":
                validation_errors.append(f"Statement '{stmt.id}' has unreviewed status '{stmt.review_status}'.")
            if stmt.is_fixture:
                validation_errors.append(f"Statement '{stmt.id}': political pilot claims cannot be fixtures.")
            sources = [s for s in register.sources if s.election_id == election_id and s.party_id == stmt.party_id
                       and s.version == stmt.source_version and stmt.source_url in (s.direct_url, s.official_url)]
            if len(sources) != 1:
                validation_errors.append(f"Statement '{stmt.id}': source URL/version must resolve to one election-scoped source.")
            else:
                src = sources[0]
                if src.status != "verified" or src.rights_review.status not in PERMITTED_QUOTE_RIGHTS:
                    validation_errors.append(f"Statement '{stmt.id}': source verification and quotation rights are not approved.")
                rights = src.rights_review
                validation_errors.extend(ReviewRecord(
                    rights.reviewed_by or "", rights.review_date or "", "approved", rights.terms_notes,
                ).validate())
                if PLACEHOLDER_REVIEWER_PATTERN.match(rights.reviewed_by or ""):
                    validation_errors.append(f"Statement '{stmt.id}': placeholder source rights reviewer cannot authorize quotation.")
                programme_path = content_dir / "examples" / "programmes"
                programmes = [json.loads(p.read_text()) for p in sorted(programme_path.glob("*.json"))]
                matches = [p for p in programmes if p.get("programme_id") == stmt.programme_id]
                if len(matches) != 1 or any(matches[0].get(k) != value for k, value in (
                    ("election_id", election_id), ("candidacy_id", stmt.party_id),
                    ("version", src.version), ("sha256", src.sha256),
                    ("status", "official"), ("rights_status", "verified_quotation_permitted"),
                    ("is_fixture", False),
                )):
                    validation_errors.append(f"Statement '{stmt.id}': programme provenance/hash/rights do not match its source.")
                elif not matches[0].get("publication_date") or not src.publication_date:
                    validation_errors.append(f"Statement '{stmt.id}': approved source and programme require publication dates.")

        if strict_approved:
            # Rejection of unreviewed or draft statements
            if stmt.review_status != "approved":
                validation_errors.append(
                    f"Statement '{stmt.id}' has unreviewed status '{stmt.review_status}'. "
                    f"Only approved statements may enter the publish set."
                )

            # Independent dual review requirement (Four-Eyes Principle)
            if len(stmt.reviews) < 2:
                validation_errors.append(
                    f"Statement '{stmt.id}' has only {len(stmt.reviews)} review(s). "
                    f"Independent dual review (Four-Eyes principle, minimum 2 distinct reviewers) is strictly required."
                )
            else:
                reviewers = {r.reviewer_id for r in stmt.reviews}
                if len(reviewers) < 2:
                    validation_errors.append(
                        f"Statement '{stmt.id}' violates Four-Eyes principle: "
                        f"must have at least 2 distinct reviewer IDs."
                    )
                for r in stmt.reviews:
                    if r.verdict != "approved":
                        validation_errors.append(
                            f"Statement '{stmt.id}' has non-approved review verdict '{r.verdict}'."
                        )

            # Topic taxonomy alignment
            if stmt.topic_id not in CORE_TOPIC_IDS:
                validation_errors.append(
                    f"Statement '{stmt.id}' topic '{stmt.topic_id}' not in core topics {sorted(CORE_TOPIC_IDS)}."
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
            continue

        if rel.status == "invalidated":
            # Exclude invalidated comparisons from active presentation
            continue

        if election_id == "es-gen-2023":
            if rel.review_status != "approved" and custom_relationships is None:
                continue
            validation_errors.extend(rel.validate(target_election_id=election_id, statements_by_id=filtered_statements, for_build=True))
            if rel.is_fixture:
                validation_errors.append(f"Relationship '{rel.id}': political pilot comparisons cannot be fixtures.")

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
    image_url = f"{ctx.canonical_base}/{preview_image_path(ctx.root_dir)}"
    properties = {
        "og:type": "website",
        "og:locale": "es_ES",
        "og:site_name": site_name,
        "og:title": title,
        "og:description": f"{notice} {description}",
        "og:url": canonical_url,
        "og:image": image_url,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": ctx.i18n["social_preview"]["image_alt"],
    }
    return "\n".join(
        f'  <meta property="{key}" content="{escape(value)}">'
        for key, value in properties.items()
    )


def render_preview_banner(ctx: SiteContext) -> str:
    """Render preview notice banner."""
    badge = escape(ctx.i18n["preview_banner"]["badge"])
    text = escape(ctx.i18n["preview_banner"]["text"])
    return f"""<aside class="preview-banner" role="status" aria-label="Aviso de prototipo">
    {badge} · {text}
  </aside>"""


def render_status_badge(ctx: SiteContext, status: str) -> str:
    """Render lifecycle status badge."""
    label = ctx.i18n["status_badges"].get(status, status.capitalize())
    badge_class = f"status-badge status-badge-{escape(status)}"
    return f'<span class="{badge_class}">{escape(label)}</span>'


def render_caveat(ctx: SiteContext, qualification: str) -> str:
    """Render qualification note."""
    label = escape(ctx.i18n["statement"]["caveat_label"])
    text = escape(qualification)
    return f"""<div class="party-caveat" role="note" aria-label="Matiz registrado">
                <strong>{label}</strong> {text}
              </div>"""


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

    url = escape(stmt.source_url)
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
    rights = escape(src.rights_review.status) if src.rights_review else "not_reviewed"

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
          <span class="coverage-meta-label">Derechos cita:</span>
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

    if stmt is None or stmt.statement_type == "not_found":
        card_class += " party-card-missing"
        status_badge = '<span class="status-badge status-badge-missing">No consta en el programa</span>'
        statement_text = ctx.i18n["statement"]["not_found_statement"]
        expl = ctx.i18n["statement"]["not_found_explanation"]
        source_footer = f"""<span class="source-citation-text text-muted">Fuente analizada: Programa oficial</span>
              <time class="source-date" datetime="{ctx.build_date}">Rev. {ctx.build_date}</time>"""

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
    status_badge = render_status_badge(ctx, "official")
    caveats_html = "".join(render_caveat(ctx, q) for q in stmt.qualifications)
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
                  data-section="{escape(stmt.source_section or '')}"
                  data-instrument="{escape(stmt.policy_instrument or '')}"
                  data-quote="{escape(stmt.quote)}"
                  data-caveats="{caveats_json}"
                  data-source-url="{escape(stmt.source_url or '')}"
                  aria-haspopup="dialog">
                  <span aria-hidden="true">📖</span>
                  <span>Leer extracto</span>
                </button>
              </div>"""

    return f"""<article class="{card_class}" aria-labelledby="party-{party_letter.lower()}-name">
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
) -> str:
    """Render outer HTML frame with base layout."""
    canonical_url = f"{ctx.canonical_base}{canonical_path}"
    base_template_file = ctx.templates_dir / "base.html"

    if ctx.election_id == "es-gen-2023":
        brand_link = f"""<a class="brand" href="{root_path}" aria-label="Generales 2023 - Ensayo Piloto">
        <span class="brand-mark" aria-hidden="true">■</span>
        <span class="brand-text">Generales<span class="brand-year">2023</span></span>
        <span class="pilot-badge" style="background: var(--color-warning-subtle, #fef3c7); color: var(--color-warning, #92400e); font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: 8px;">Piloto Privado</span>
      </a>"""
        preview_banner_text = "ENSAYO PILOTO PRIVADO · Generales 2023 (piloto) · Revisión humana y de derechos pendiente · No satisface G2"
        footer_org = "Generales 2023 · Ensayo piloto privado y confidencial"
        footer_values = "Aislamiento estricto de elecciones · No satisface G2 para 2026"
        if "Generales 2023" not in title:
            title = f"{title} · Generales 2023"
    else:
        brand_link = f"""<a class="brand" href="{root_path}" aria-label="Elecciones 2026 - Inicio">
        <span class="brand-mark" aria-hidden="true">■</span>
        <span class="brand-text">Elecciones<span class="brand-year">2026</span></span>
      </a>"""
        preview_banner_text = f"{escape(ctx.i18n['preview_banner']['badge'])} · {escape(ctx.i18n['preview_banner']['text'])}"
        footer_org = escape(ctx.i18n["footer"]["org"])
        footer_values = escape(ctx.i18n["footer"]["values"])

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
  <title>{{ title }}</title>
  <link rel="canonical" href="{{ canonical_url }}">
{{ social_metadata }}
  <link rel="stylesheet" href="{{ root_path }}styles.css">
</head>
<body class="theme-swiss" data-election="{{ election_id }}" data-swiss-accent="monochrome">
  <a class="skip-link" href="#contenido">{{ skip_to_content }}</a>
  <aside class="preview-banner" role="status" aria-label="Aviso de prototipo">
    {{ preview_banner_text }}
  </aside>
  <header class="topbar" role="banner">
    <div class="topbar-inner">
      {{ brand_link }}
      <nav class="nav-links" aria-label="Navegación principal">
        <a class="nav-link" href="{{ root_path }}#comparador">{{ nav_comparator }}</a>
        <a class="nav-link" href="{{ root_path }}temas/">{{ nav_topics }}</a>
        <a class="nav-link" href="{{ root_path }}cuestionario/">{{ nav_quiz }}</a>
        <a class="nav-link" href="{{ root_path }}partidos/">{{ nav_parties }}</a>
        <a class="nav-link" href="{{ root_path }}metodo/">{{ nav_methodology }}</a>
        <a class="nav-link" href="{{ root_path }}fuentes/">{{ nav_sources }}</a>
        <a class="nav-link" href="{{ root_path }}correcciones/">{{ nav_corrections }}</a>
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
    </div>
  </footer>
</body>
</html>"""

    replacements = {
        "{{ lang }}": ctx.i18n["meta"]["language"],
        "{{ title }}": escape(title),
        "{{ description }}": escape(description),
        "{{ canonical_url }}": escape(canonical_url),
        "{{ social_metadata }}": render_social_metadata(ctx, title, description, canonical_url),
        "{{ root_path }}": root_path,
        "{{ brand_link }}": brand_link,
        "{{ skip_to_content }}": escape(ctx.i18n["nav"]["skip_to_content"]),
        "{{ preview_banner_text }}": preview_banner_text,
        "{{ nav_comparator }}": escape(ctx.i18n["nav"]["comparator"]),
        "{{ nav_topics }}": escape(ctx.i18n["nav"]["topics"]),
        "{{ nav_quiz }}": escape(ctx.i18n["nav"].get("quiz", "Cuestionario")),
        "{{ nav_parties }}": escape(ctx.i18n["nav"]["parties"]),
        "{{ nav_methodology }}": escape(ctx.i18n["nav"]["methodology"]),
        "{{ nav_sources }}": escape(ctx.i18n["nav"]["sources"]),
        "{{ nav_corrections }}": escape(ctx.i18n["nav"]["corrections"]),
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


def render_home_page(ctx: SiteContext) -> str:
    """Render index.html with accessible comparator and static fallback."""
    # Find sample active comparison
    if ctx.election_id == "es-gen-2023":
        active_rel = (
            ctx.relationships.get("rel-pilot-2023-housing-pp-erc-divergence")
            or next((r for r in ctx.relationships.values() if r.status == "active"), None)
        )
        party_a_id = active_rel.party_ids[0] if active_rel else "pp"
        party_b_id = active_rel.party_ids[1] if active_rel and len(active_rel.party_ids) > 1 else "erc"
        hero_eyebrow = "ENSAYO PILOTO PRIVADO · GENERALES 2023 (23 JUL 2023)"
        hero_title_part1 = "Los programas de 2023,"
        hero_title_part2 = "ensayo de comparación."
        hero_intro = "Generales 2023 (piloto): documentos de PP y ERC con revisión humana y de derechos pendiente. Sin posiciones aprobadas para comparar. No satisface la puerta G2 para 2026."
        mock_notice = """<aside class="notice" aria-label="Aviso del ensayo piloto">
      <strong>Aviso de ensayo privado (Generales 2023):</strong> Esta vista corresponde al ensayo técnico con documentos de PP y ERC. Las posiciones y sus derechos de cita requieren revisión humana antes de mostrarse. Este ensayo no satisface la puerta de publicación G2 para 2026 ni presenta información de 2026.
    </aside>"""
        selector_eyebrow = "01 / COMPARAR · GENERALES 2023"
        page_title = "Generales 2023 · Comparador de programas (Ensayo piloto)"
        page_description = "Generales 2023 (piloto) · Ensayo privado. Revisión humana y de derechos pendiente; sin posiciones aprobadas."
    else:
        active_rel = (
            ctx.relationships.get("rel-housing-rental-regulation-party-a-party-b")
            or next((r for r in ctx.relationships.values() if r.status == "active"), None)
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

    topic_options = []
    for t in ctx.taxonomy.topics:
        selected = ' selected' if (active_rel and t.id == active_rel.topic_id) or t.id == "housing" else ""
        topic_options.append(f'<option value="{escape(t.id)}"{selected}>{escape(t.name_es)}</option>')

    party_a_options = []
    party_b_options = []
    for pid in sorted(ctx.parties.keys()):
        p = ctx.parties[pid]
        sel_a = ' selected' if pid == party_a_id else ""
        sel_b = ' selected' if pid == party_b_id else ""
        party_a_options.append(f'<option value="{escape(pid)}"{sel_a}>{escape(p.display_name)}</option>')
        party_b_options.append(f'<option value="{escape(pid)}"{sel_b}>{escape(p.display_name)}</option>')

    # Get statements for party A and B
    stmt_a = None
    stmt_b = None
    if active_rel and len(active_rel.statement_ids) >= 2:
        stmt_a = ctx.statements.get(active_rel.statement_ids[0])
        stmt_b = ctx.statements.get(active_rel.statement_ids[1])
    if not stmt_a:
        stmt_a = next((s for s in ctx.statements.values() if s.party_id == party_a_id and (not active_rel or s.topic_id == active_rel.topic_id)), None)
    if not stmt_b:
        stmt_b = next((s for s in ctx.statements.values() if s.party_id == party_b_id and (not active_rel or s.topic_id == active_rel.topic_id)), None)

    party_a_card = render_party_card(ctx, stmt_a, party_a_id, "A")
    party_b_card = render_party_card(ctx, stmt_b, party_b_id, "B")

    # Relationship callout
    analysis_heading = ctx.i18n["analysis"]["heading"]
    analysis_text = ctx.i18n["analysis"]["note"]
    if active_rel:
        analysis_text = active_rel.summary
        rel_type_label = ctx.i18n["relationship_badges"].get(active_rel.relationship_type, active_rel.relationship_type)
        analysis_heading = f"Lectura comparada: {rel_type_label}"

    # Prepare grouped measures for the default topic (housing)
    stmt_a_2 = ctx.statements.get("stmt-party-a-housing-002")
    party_a_card_2 = render_party_card(ctx, stmt_a_2, party_a_id, "A")
    party_b_card_2 = render_party_card(ctx, None, party_b_id, "B")

    # Differences list for measure 1
    differences_html = ""
    if active_rel and active_rel.differences:
        items = "".join(f"<li>{escape(d)}</li>" for d in active_rel.differences)
        differences_html = f'<ul class="analysis-differences">{items}</ul>'

    rel_type = active_rel.relationship_type if active_rel else "agreement"
    if rel_type == "agreement":
        rel_callout_class = "rel-callout-agreement"
        rel_icon = "✓"
    elif rel_type == "divergence":
        rel_callout_class = "rel-callout-divergence"
        rel_icon = "≠"
    elif rel_type == "qualification":
        rel_callout_class = "rel-callout-qualification"
        rel_icon = "~"
    else:
        rel_callout_class = "rel-callout-not-found"
        rel_icon = "—"

    measure_1_html = f"""<article class="measure-group" aria-labelledby="measure-1-title">
            <div class="measure-head">
              <p id="measure-topic-label" class="measure-topic-label">TEMA: VIVIENDA</p>
              <h3 id="measure-1-title" class="measure-title">Medida: {escape(active_rel.measure_label if active_rel else 'Regulación de precios de alquiler en zonas de mercado tensionado')}</h3>
              <p id="measure-summary" class="measure-summary">Políticas de contención y límites obligatorios a los precios de arrendamiento de vivienda en áreas declaradas de mercado tensionado.</p>
              <div class="measure-context" role="region" aria-label="Alcance y claves de la iniciativa">
                <p class="measure-context-desc">Esta medida evalúa las políticas de contención del alquiler residencial frente al incremento de precios en áreas urbanas, analizando los modelos de índice de precios de referencia y el régimen sancionador a grandes tenedores.</p>
                <div class="measure-axes">
                  <span class="measure-axes-label">Claves de contraste en esta medida:</span>
                  <ul class="measure-axes-list">
                    <li>Modelo de contención: índice estatal homogéneo vinculante frente a índices de ajuste autonómico.</li>
                    <li>Régimen de excepciones: moratorias temporales por rehabilitación integral frente a aplicación general sin exenciones.</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="measure-cards">
              {party_a_card}
              {party_b_card}
            </div>

            <aside id="analysis-callout" class="analysis-callout {rel_callout_class}" aria-label="Lectura comparada">
              <span class="analysis-icon" aria-hidden="true">{rel_icon}</span>
              <div>
                <h4 id="analysis-title">{escape(analysis_heading)}</h4>
                <p id="analysis-text">{escape(analysis_text)}</p>
                {differences_html}
              </div>
            </aside>
          </article>"""

    measure_2_html = f"""<article class="measure-group" aria-labelledby="measure-2-title">
            <div class="measure-head">
              <p class="measure-topic-label">TEMA: VIVIENDA</p>
              <h3 id="measure-2-title" class="measure-title">Medida: Ayudas públicas directas y avales para acceso a la vivienda para jóvenes</h3>
              <p class="measure-summary">Instrumentos de apoyo financiero público para facilitar la emancipación y la adquisición o fianza de primera vivienda por jóvenes menores de 35 años.</p>
              <div class="measure-context" role="region" aria-label="Alcance y claves de la iniciativa">
                <p class="measure-context-desc">Esta medida analiza las fórmulas de intervención pública para facilitar el acceso de jóvenes a la vivienda habitual, contrastando subvenciones directas a intereses frente a coberturas crediticias de fianza o entrada.</p>
                <div class="measure-axes">
                  <span class="measure-axes-label">Claves de contraste en esta medida:</span>
                  <ul class="measure-axes-list">
                    <li>Instrumento financiero: bonificación de tipos de interés hipotecario frente a líneas directas de aval de entrada.</li>
                    <li>Criterios de elegibilidad: límites de renta basados en múltiplos del IPREM (3,5x frente a 4x).</li>
                  </ul>
                </div>
              </div>
            </div>

            <div class="measure-cards">
              {party_a_card_2}
              {party_b_card_2}
            </div>

            <aside class="analysis-callout rel-callout-not-found" aria-label="Lectura comparada">
              <span class="analysis-icon" aria-hidden="true">—</span>
              <div>
                <h4>Sin posición comparable en esta medida</h4>
                <p>Partido Ejemplo A propone bonificación de tipos de interés hipotecarios, mientras que en el documento revisado de Partido Ejemplo B no consta propuesta específica sobre este instrumento.</p>
                <p class="missing-explanation">«No consta» indica ausencia documental en el texto; nunca se interpretará como oposición política ni como acuerdo tácito.</p>
              </div>
            </aside>
          </article>"""

    if ctx.election_id == "es-gen-2023":
        measures_content = f"          {measure_1_html}"
    else:
        measures_content = f"          {measure_1_html}\n          {measure_2_html}"

    content = f"""    <section class="hero" aria-labelledby="hero-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="hero-title" class="hero-title">{hero_title_part1}<br><span class="hero-em">{hero_title_part2}</span></h1>
      <p class="hero-intro">{hero_intro}</p>
      <div class="hero-actions">
        <a class="btn-primary" href="#comparador">
          <span>{escape(ctx.i18n['hero']['cta'])}</span>
          <span aria-hidden="true">→</span>
        </a>
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
    <script src="./app.js" defer></script>

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
    )


def render_topic_index(ctx: SiteContext) -> str:
    """Render temas/index.html listing all 8 taxonomy core topics."""
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
    page_description = "Explora las propuestas electorales para las Elecciones Generales 2023 (Ensayo piloto)." if ctx.election_id == "es-gen-2023" else "Explora las propuestas electorales para las Elecciones Generales 2026 agrupadas en 8 temas clave."

    content = f"""    <section class="hero" aria-labelledby="topics-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="topics-title" class="hero-title">Temas electorales</h1>
      <p class="hero-intro">Explora las 8 áreas clave definidas en la metodología neutral del proyecto. Cada área desglosa propuestas concretas con trazabilidad documental directa.</p>
    </section>

    <section class="topics-grid" style="padding: var(--space-4) 0 var(--space-8);">
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
    {"".join(subtopics_sections)}
    {render_budget_context(ctx, topic.id, "../../")}"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=topic.description_es,
        canonical_path=f"/temas/{topic.id}/",
        content=content,
        root_path="../../",
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
        scope = party.territorial_scope

        cards.append(f"""<article class="party-card" style="margin-bottom: var(--space-4);">
        <div class="party-card-header">
          <span class="party-pill party-pill-a" aria-hidden="true">◧</span>
          <div class="party-card-meta">
            <h2 class="party-name"><a href="./{escape(pid)}/">{escape(party.display_name)}</a></h2>
            {badge}
          </div>
        </div>
        <p class="party-statement"><strong>Nombre oficial:</strong> {escape(party.official_name)} · <strong>Ámbito:</strong> {escape(scope)}</p>
        <div class="party-card-footer">
          <a class="source-citation" href="./{escape(pid)}/">Ver programa y propuestas →</a>
          <span class="source-date">{escape(party.short_name)}</span>
        </div>
      </article>""")

    hero_eyebrow = "ENSAYO PILOTO PRIVADO · CANDIDATURAS GENERALES 2023" if ctx.election_id == "es-gen-2023" else "CANDIDATURAS Y COBERTURA"
    page_title = "Candidaturas y partidos · Generales 2023 (Ensayo piloto)" if ctx.election_id == "es-gen-2023" else "Candidaturas y partidos · Elecciones 2026"
    page_description = "Consulta las candidaturas y el estado de sus programas para las Elecciones Generales 2023 (Ensayo piloto)." if ctx.election_id == "es-gen-2023" else "Consulta las candidaturas electorales y el estado de sus programas para las Elecciones Generales 2026."

    content = f"""    <section class="hero" aria-labelledby="parties-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="parties-title" class="hero-title">Candidaturas seguidas</h1>
      <p class="hero-intro">Registro oficial de partidos y coaliciones incluidos en el comparador bajo criterios públicos y auditables. Consulte el estado de publicación y las propuestas revisadas de cada formación.</p>
    </section>

    <section class="parties-list" style="padding: var(--space-4) 0 var(--space-8);">
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
          <li><strong>Derechos de cita:</strong> {escape(src.rights_review.status)}</li>
        </ul>"""

    stmts_sections = []
    if not party_stmts:
        stmts_sections.append("""<div class="notice" style="margin-top: var(--space-4);">
          <p><strong>Programa no disponible:</strong> No se han registrado aún afirmaciones revisadas para esta candidatura.</p>
        </div>""")
    else:
        for s in party_stmts:
            topic = next((t for t in ctx.taxonomy.topics if t.id == s.topic_id), None)
            topic_name = topic.name_es if topic else s.topic_id
            stmts_sections.append(f"""<div style="margin-bottom: var(--space-4);">
              <h3 style="font-size: var(--font-size-base); color: var(--color-text-brand); margin-bottom: var(--space-2);">{escape(topic_name)}</h3>
              {render_party_card(ctx, s, party.id, "A")}
            </div>""")

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

    <section style="margin-bottom: var(--space-10);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-4);">Propuestas y posiciones revisadas</h2>
      {"".join(stmts_sections)}
    </section>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path=f"/partidos/{party.id}/",
        content=content,
        root_path="../../",
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

    content = f"""    <section class="hero" aria-labelledby="method-title">
      <p class="hero-eyebrow">{hero_eyebrow}</p>
      <h1 id="method-title" class="hero-title">Compara con rigor y neutralidad</h1>
      <p class="hero-intro">El proyecto Elecciones 2026 se rige por un marco metodológico estricto de citas exactas, doble revisión humana independiente y ausencia total de recomendaciones de voto.</p>
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
        <h2>3. Principio de cuatro ojos (Four-Eyes Principle)</h2>
        <p class="party-statement">Toda afirmación publicada requiere la aprobación explícita de al menos dos revisores editoriales independientes:</p>
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
          <td style="padding: var(--space-3); border-bottom: 1px solid var(--color-border-subtle);">{escape(src.rights_review.status)}</td>
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

    content = f"""    <section class="hero" aria-labelledby="sources-title">
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
      <div class="coverage-cards" style="margin-bottom: var(--space-4);">
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

    <section style="margin-bottom: var(--space-10);">
      <h2 style="font-size: var(--font-size-xl); margin-bottom: var(--space-3);">2. Fuentes históricas de ensayo · Piloto 2023</h2>
      <aside class="notice" style="margin-bottom: var(--space-4);">
        <strong>Aislamiento de elecciones (Tarea 1.4):</strong> Los documentos de 2023 se emplean exclusivamente para ensayos técnicos y validación de esquemas. El comparador rechaza automáticamente cualquier intento de comparar un programa de 2023 con uno de 2026.
      </aside>
      <div class="coverage-cards" style="margin-bottom: var(--space-4);">
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

    content = f"""    <section class="hero" aria-labelledby="corrections-title">
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
      {"".join(cards)}
    </section>"""

    return render_base(
        ctx=ctx,
        title=page_title,
        description=page_description,
        canonical_path="/correcciones/",
        content=content,
        root_path="../",
    )



def render_sitemap(ctx: SiteContext, routes: list[tuple[str, str, str]]) -> str:
    """Render accurate sitemap.xml with all canonical routes."""
    entries = []
    # Sort deterministically by URL
    for loc, lastmod, freq in sorted(routes, key=lambda r: r[0]):
        entries.append(f"""  <url>
    <loc>{escape(loc)}</loc>
    <lastmod>{escape(lastmod)}</lastmod>
    <changefreq>{escape(freq)}</changefreq>
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
) -> SiteBuildResult:
    """Generate the complete static site deterministically into output_dir.

    Uses an atomic staging directory to ensure that any validation failure
    aborts without creating a partially published site.
    """
    budget_manifest, budget_payload = None, None
    if budget_bundle is not None:
        from elecciones2026.budget import BudgetError, load_bundle
        try:
            budget_manifest, budget_payload = load_bundle(budget_bundle, (content_dir or root_dir / "content") / "taxonomy.json")
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
    if quiz_mode not in {"unavailable", "mock", "reviewed"}:
        raise BuildValidationError("Invalid quiz mode.")
    quiz_bundle = None
    if quiz_mode != "unavailable":
        quiz_path = quiz_file or (ctx.content_dir / "quiz" / f"{quiz_mode}.json")
        try:
            quiz_bundle = prepare_quiz(quiz_path, ctx, mock=quiz_mode == "mock")
        except (ValueError, OSError, QuizValidationError) as error:
            raise BuildValidationError(f"Quiz validation failed: {error}") from error

    # Use atomic staging directory
    staging_dir = output_dir.parent / f".tmp_{output_dir.name}_{os.getpid()}"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

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

        if budget_bundle is not None:
            from elecciones2026.budget import copy_reviewed_bundle
            try:
                copy_reviewed_bundle(budget_bundle, staging_dir, ctx.content_dir / "taxonomy.json")
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
        if quiz_bundle is not None and quiz_bundle["available"]:
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
        quiz_content += ''.join(f'<script src="../{name}" defer></script>\n' for name in quiz_scripts)
        quiz_description = ("Demostración privada con datos ficticios. No representa programas reales."
                            if quiz_mode == "mock" else "Coincidencia con medidas revisadas."
                            if quiz_mode == "reviewed" else "El cuestionario aún no está disponible.")
        quiz_html = render_base(ctx, "Cuestionario de coincidencia", quiz_description,
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
        if quiz_mode != "reviewed":
            quiz_html = quiz_html.replace('<meta charset="utf-8">',
                '<meta charset="utf-8">\n<meta name="robots" content="noindex, nofollow">')
        else:
            routes.append((f"{ctx.canonical_base}/cuestionario/", ctx.build_date, "weekly"))
        write_file_deterministic(staging_dir / "cuestionario" / "index.html", quiz_html)

        # 9. Sitemap & crawler files
        sitemap_xml = render_sitemap(ctx, routes)
        write_file_deterministic(staging_dir / "sitemap.xml", sitemap_xml)

        robots_txt = render_robots_txt(ctx)
        write_file_deterministic(staging_dir / "robots.txt", robots_txt)

        security_txt = render_security_txt(ctx)
        write_file_deterministic(staging_dir / "security.txt", security_txt)
        write_file_deterministic(staging_dir / ".well-known" / "security.txt", security_txt)

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

        shutil.copy2(site_src / "sharing.js", staging_dir / "sharing.js")

        preview_target = staging_dir / preview_image_path(root_dir)
        preview_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(site_src / "assets" / "social-preview.png", preview_target)

        # Do not copy accidentally misplaced private sources or retain them in output.
        reject_private_source_artifacts(staging_dir)
        if output_dir.exists():
            reject_private_source_artifacts(output_dir)
            # Withdraw obsolete quiz bundles when changing mode or source version.
            for obsolete in output_dir.iterdir():
                generated_quiz_asset = re.fullmatch(
                    r"(?:quiz-(?:data|engine|ui)\.[0-9a-f]{16}\.js|quiz\.[0-9a-f]{16}\.css)", obsolete.name)
                if generated_quiz_asset and obsolete.is_file() and not (staging_dir / obsolete.name).exists():
                    obsolete.unlink()

        # Atomic swap / copy into output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        # Copy staging contents to output_dir
        for root, dirs, files in os.walk(staging_dir):
            rel_dir = Path(root).relative_to(staging_dir)
            target_sub = output_dir / rel_dir
            target_sub.mkdir(parents=True, exist_ok=True)
            for f in sorted(files):
                shutil.copy2(Path(root) / f, target_sub / f)

        # Collect hashes and written files
        files_written: list[str] = []
        file_hashes: dict[str, str] = {}
        for root, dirs, files in os.walk(output_dir):
            for f in sorted(files):
                file_path = Path(root) / f
                rel_path = str(file_path.relative_to(output_dir))
                files_written.append(rel_path)
                file_hashes[rel_path] = compute_sha256(file_path)

        files_written.sort()

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
    build_p.add_argument("--budget-bundle", type=Path, help="Optional immutable budget bundle; requires human review.")
    build_p.add_argument("--quiz-mode", choices=("unavailable", "mock", "reviewed"), default="unavailable",
                         help="Mock quiz is opt-in for private preview; reviewed mode requires approved input.")
    build_p.add_argument("--quiz-file", type=Path, help="Versioned quiz authoring JSON.")

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

    parsed = parser.parse_args(args)

    if parsed.command == "build":
        try:
            res = build_site(
                root_dir=parsed.root_dir,
                output_dir=parsed.output_dir,
                content_dir=parsed.content_dir,
                election_id=parsed.election_id,
                canonical_base=parsed.canonical_base,
                build_date=parsed.build_date,
                strict_approved=parsed.strict,
                budget_bundle=parsed.budget_bundle,
                quiz_mode=parsed.quiz_mode,
                quiz_file=parsed.quiz_file,
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
