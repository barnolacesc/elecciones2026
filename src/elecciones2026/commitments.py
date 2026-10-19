"""Commitment tracking definitions, schema validation, and sovereign source verification.

Part of OpenSpec change commitment-follow-through (Epic E9, Gate G9).
Enforces the 8-state follow-through taxonomy, sovereign primary gazette rules,
the No-Lie Rule against accusatory framing, and the Four-Eyes dual review protocol.
"""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from elecciones2026.methodology import CORE_TOPIC_IDS

ID_PATTERN = re.compile(r"^cmt-[a-z0-9-]+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEMVER_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")

VALID_FOLLOW_THROUGH_STATUSES = {
    "enacted_as_pledged",
    "partially_enacted",
    "contrary_action_taken",
    "coalition_compromise",
    "blocked_by_parliament",
    "no_initiative_registered",
    "outside_state_competence",
    "unassessable",
}

VALID_GOVERNANCE_ROLES = {
    "governing_sole",
    "governing_senior",
    "governing_junior",
    "opposition",
}

VALID_SOURCE_TYPES = {
    "boe",
    "bocg_initiative",
    "bocg_vote",
    "igae",
    "ine",
}

VALID_AGREEMENT_STATUSES = {
    "unanimous",
    "lead_editor_resolved",
}

# Strict prohibition of subjective, moralizing, or accusatory words.
PROHIBITED_ACCUSATORY_TERMS = {
    "mentira",
    "mentiras",
    "mentiroso",
    "mentirosos",
    "engaño",
    "engaños",
    "traición",
    "falsedad",
    "falsedades",
    "lie",
    "lies",
    "liar",
    "hypocrisy",
}

# Permitted sovereign primary source host domains
SOVEREIGN_HOST_SUFFIXES = (
    "boe.es",
    "congreso.es",
    "senado.es",
    "hacienda.gob.es",
    "ine.es",
    "tribunalconstitucional.es",
    "lamoncloa.gob.es",
    "poderjudicial.es",
)


class CommitmentValidationError(ValueError):
    """Raised when a commitment record violates schema or methodology rules."""


@dataclass(frozen=True)
class PledgeRecord:
    summary_es: str
    source_id: str
    verbatim_quote: str | None = None
    page: int | str | None = None
    section: str | None = None


@dataclass(frozen=True)
class GovernanceContext:
    role: str
    legislature: str
    period_start: str | None = None
    period_end: str | None = None
    jurisdiction: str = "state"


@dataclass(frozen=True)
class EvidenceRecord:
    source_type: str
    official_id: str
    title: str
    url: str
    date: str
    finding_summary_es: str


@dataclass(frozen=True)
class EditorialReview:
    drafter: str
    reviewed_by_1: str
    reviewed_by_2: str
    lead_editor_signoff: str
    review_date: str
    agreement_status: str


@dataclass(frozen=True)
class CommitmentRecord:
    schema_version: str
    id: str
    election_id: str
    party_id: str
    topic_id: str
    pledge: PledgeRecord
    governance_context: GovernanceContext
    status: str
    evidence: list[EvidenceRecord]
    editorial_review: EditorialReview


def _scan_for_prohibited_terms(text: str, field_name: str) -> None:
    """Scan text for prohibited accusatory terms and raise error if detected."""
    normalized = text.lower()
    for term in PROHIBITED_ACCUSATORY_TERMS:
        # Match whole word boundaries to prevent false positives on substrings
        pattern = rf"\b{re.escape(term)}\b"
        if re.search(pattern, normalized):
            raise CommitmentValidationError(
                f"Field '{field_name}' contains prohibited accusatory term '{term}'. "
                "The methodology strictly forbids moralizing labels or subjective intent words."
            )


def _validate_sovereign_url(url: str, field_name: str) -> None:
    """Ensure evidence URL points strictly to a recognized sovereign primary domain."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise CommitmentValidationError(
            f"Evidence URL '{url}' in '{field_name}' must use http or https scheme."
        )
    hostname = (parsed.hostname or "").lower()
    if not any(hostname == domain or hostname.endswith("." + domain) for domain in SOVEREIGN_HOST_SUFFIXES):
        raise CommitmentValidationError(
            f"Evidence URL '{url}' has non-sovereign host '{hostname}'. "
            "Evidence must strictly originate from official sovereign gazettes "
            f"({', '.join(SOVEREIGN_HOST_SUFFIXES)}). Journalistic or media URLs are prohibited."
        )


def validate_commitment_dict(data: dict[str, Any]) -> CommitmentRecord:
    """Validate a raw dictionary against commitment methodology and return a typed CommitmentRecord."""
    if not isinstance(data, dict):
        raise CommitmentValidationError("Commitment data must be a JSON object.")

    # 1. Structural requirements
    required_top = [
        "schema_version",
        "id",
        "election_id",
        "party_id",
        "topic_id",
        "pledge",
        "governance_context",
        "status",
        "evidence",
        "editorial_review",
    ]
    for req in required_top:
        if req not in data:
            raise CommitmentValidationError(f"Missing required field: '{req}'.")

    schema_version = data["schema_version"]
    if not SEMVER_PATTERN.match(str(schema_version)):
        raise CommitmentValidationError(f"Invalid schema_version: '{schema_version}'. Must be semver.")

    record_id = data["id"]
    if not ID_PATTERN.match(str(record_id)):
        raise CommitmentValidationError(f"Invalid id: '{record_id}'. Must match pattern ^cmt-[a-z0-9-]+$.")

    election_id = data["election_id"]
    party_id = data["party_id"]
    topic_id = data["topic_id"]
    if topic_id not in CORE_TOPIC_IDS:
        raise CommitmentValidationError(
            f"Invalid topic_id: '{topic_id}'. Must be one of {sorted(CORE_TOPIC_IDS)}."
        )

    # 2. Pledge validation
    pledge_raw = data["pledge"]
    if not isinstance(pledge_raw, dict):
        raise CommitmentValidationError("Field 'pledge' must be an object.")
    if "summary_es" not in pledge_raw or "source_id" not in pledge_raw:
        raise CommitmentValidationError("Pledge must contain 'summary_es' and 'source_id'.")

    summary_es = str(pledge_raw["summary_es"]).strip()
    if not summary_es or len(summary_es) > 500:
        raise CommitmentValidationError("Pledge 'summary_es' must be between 1 and 500 characters.")
    _scan_for_prohibited_terms(summary_es, "pledge.summary_es")

    verbatim_quote = pledge_raw.get("verbatim_quote")
    if verbatim_quote is not None:
        _scan_for_prohibited_terms(str(verbatim_quote), "pledge.verbatim_quote")

    pledge = PledgeRecord(
        summary_es=summary_es,
        source_id=str(pledge_raw["source_id"]),
        verbatim_quote=str(verbatim_quote) if verbatim_quote else None,
        page=pledge_raw.get("page"),
        section=str(pledge_raw["section"]) if pledge_raw.get("section") else None,
    )

    # 3. Governance context
    gov_raw = data["governance_context"]
    if not isinstance(gov_raw, dict):
        raise CommitmentValidationError("Field 'governance_context' must be an object.")
    role = gov_raw.get("role")
    if role not in VALID_GOVERNANCE_ROLES:
        raise CommitmentValidationError(
            f"Invalid governance role: '{role}'. Must be one of {sorted(VALID_GOVERNANCE_ROLES)}."
        )

    period_start = gov_raw.get("period_start")
    if period_start and not DATE_PATTERN.match(str(period_start)):
        raise CommitmentValidationError(f"Invalid period_start date: '{period_start}'.")
    period_end = gov_raw.get("period_end")
    if period_end and not DATE_PATTERN.match(str(period_end)):
        raise CommitmentValidationError(f"Invalid period_end date: '{period_end}'.")

    jurisdiction = gov_raw.get("jurisdiction", "state")
    if jurisdiction not in {"state", "regional", "local"}:
        raise CommitmentValidationError(f"Invalid jurisdiction: '{jurisdiction}'.")

    governance_context = GovernanceContext(
        role=role,
        legislature=str(gov_raw.get("legislature", "")),
        period_start=str(period_start) if period_start else None,
        period_end=str(period_end) if period_end else None,
        jurisdiction=jurisdiction,
    )

    # 4. Status validation
    status = data["status"]
    if status not in VALID_FOLLOW_THROUGH_STATUSES:
        raise CommitmentValidationError(
            f"Invalid status: '{status}'. Must be one of {sorted(VALID_FOLLOW_THROUGH_STATUSES)}."
        )

    # 5. Evidence records
    evidence_raw = data["evidence"]
    if not isinstance(evidence_raw, list) or len(evidence_raw) == 0:
        raise CommitmentValidationError("Commitment must have at least one evidence item in 'evidence'.")

    evidence_records: list[EvidenceRecord] = []
    has_parliamentary_evidence = False

    for idx, ev in enumerate(evidence_raw):
        if not isinstance(ev, dict):
            raise CommitmentValidationError(f"Evidence item {idx} must be an object.")
        source_type = ev.get("source_type")
        if source_type not in VALID_SOURCE_TYPES:
            raise CommitmentValidationError(
                f"Evidence item {idx} has invalid source_type '{source_type}'. "
                f"Must be one of {sorted(VALID_SOURCE_TYPES)}."
            )
        if source_type in {"bocg_vote", "bocg_initiative"}:
            has_parliamentary_evidence = True

        title = str(ev.get("title", "")).strip()
        url = str(ev.get("url", "")).strip()
        date_str = str(ev.get("date", "")).strip()
        finding = str(ev.get("finding_summary_es", "")).strip()

        if not title:
            raise CommitmentValidationError(f"Evidence item {idx} missing 'title'.")
        if not url:
            raise CommitmentValidationError(f"Evidence item {idx} missing 'url'.")
        if not DATE_PATTERN.match(date_str):
            raise CommitmentValidationError(f"Evidence item {idx} invalid date: '{date_str}'.")
        if not finding:
            raise CommitmentValidationError(f"Evidence item {idx} missing 'finding_summary_es'.")

        _validate_sovereign_url(url, f"evidence[{idx}].url")
        _scan_for_prohibited_terms(title, f"evidence[{idx}].title")
        _scan_for_prohibited_terms(finding, f"evidence[{idx}].finding_summary_es")

        evidence_records.append(
            EvidenceRecord(
                source_type=source_type,
                official_id=str(ev.get("official_id", "")),
                title=title,
                url=url,
                date=date_str,
                finding_summary_es=finding,
            )
        )

    # Check opposition evaluation rule: opposition parties must be audited against parliamentary acts
    if role == "opposition" and not has_parliamentary_evidence:
        raise CommitmentValidationError(
            f"Commitment '{record_id}' has role 'opposition' but lacks parliamentary voting or initiative "
            "evidence ('bocg_vote' or 'bocg_initiative'). Opposition parties must be audited on parliamentary "
            "records, not general absence of executive decrees."
        )

    # 6. Four-Eyes Editorial Review
    review_raw = data["editorial_review"]
    if not isinstance(review_raw, dict):
        raise CommitmentValidationError("Field 'editorial_review' must be an object.")

    drafter = str(review_raw.get("drafter", "")).strip()
    rev1 = str(review_raw.get("reviewed_by_1", "")).strip()
    rev2 = str(review_raw.get("reviewed_by_2", "")).strip()
    signoff = str(review_raw.get("lead_editor_signoff", "")).strip()
    review_date = str(review_raw.get("review_date", "")).strip()
    agreement = review_raw.get("agreement_status")

    if not drafter or not rev1 or not rev2 or not signoff:
        raise CommitmentValidationError(
            "Editorial review requires 'drafter', 'reviewed_by_1', 'reviewed_by_2', and 'lead_editor_signoff'."
        )
    if not DATE_PATTERN.match(review_date):
        raise CommitmentValidationError(f"Invalid review_date: '{review_date}'.")
    if agreement not in VALID_AGREEMENT_STATUSES:
        raise CommitmentValidationError(
            f"Invalid agreement_status: '{agreement}'. Must be one of {sorted(VALID_AGREEMENT_STATUSES)}."
        )

    # Segregation of duties: Four-Eyes Principle
    if rev1 == rev2:
        raise CommitmentValidationError(
            f"Four-Eyes Principle violation: 'reviewed_by_1' and 'reviewed_by_2' must be distinct ({rev1})."
        )
    if drafter == rev2:
        raise CommitmentValidationError(
            f"Four-Eyes Principle violation: drafter cannot serve as the second independent reviewer ({drafter})."
        )

    editorial_review = EditorialReview(
        drafter=drafter,
        reviewed_by_1=rev1,
        reviewed_by_2=rev2,
        lead_editor_signoff=signoff,
        review_date=review_date,
        agreement_status=agreement,
    )

    return CommitmentRecord(
        schema_version=str(schema_version),
        id=str(record_id),
        election_id=str(election_id),
        party_id=str(party_id),
        topic_id=str(topic_id),
        pledge=pledge,
        governance_context=governance_context,
        status=str(status),
        evidence=evidence_records,
        editorial_review=editorial_review,
    )


def load_commitment(path: str | Path) -> CommitmentRecord:
    """Load and validate a single commitment JSON file."""
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Commitment file not found: {path_obj}")
    with open(path_obj, "r", encoding="utf-8") as f:
        data = json.load(f)
    return validate_commitment_dict(data)


def load_all_commitments(directory: str | Path) -> list[CommitmentRecord]:
    """Load and validate all commitment JSON files within a directory."""
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Commitments directory not found: {dir_path}")
    commitments: list[CommitmentRecord] = []
    for file_path in sorted(dir_path.glob("*.json")):
        commitments.append(load_commitment(file_path))
    return commitments


STATUS_LABELS_ES: dict[str, str] = {
    "enacted_as_pledged": "Cumplida según programa",
    "partially_enacted": "Parcialmente cumplida",
    "contrary_action_taken": "Acción contraria documentada",
    "coalition_compromise": "Modificada por pacto",
    "blocked_by_parliament": "Iniciada pero rechazada en Cortes",
    "no_initiative_registered": "Sin iniciativa registrada",
    "outside_state_competence": "Competencia no estatal",
    "unassessable": "Evidencia no concluyente",
}

STATUS_CSS_CLASSES: dict[str, str] = {
    "enacted_as_pledged": "badge-status-enacted",
    "partially_enacted": "badge-status-partially",
    "contrary_action_taken": "badge-status-contrary",
    "coalition_compromise": "badge-status-compromise",
    "blocked_by_parliament": "badge-status-blocked",
    "no_initiative_registered": "badge-status-blocked",
    "outside_state_competence": "badge-status-blocked",
    "unassessable": "badge-status-blocked",
}

GOVERNANCE_ROLE_LABELS_ES: dict[str, str] = {
    "governing_sole": "Gobierno en solitario",
    "governing_senior": "Gobierno (socio principal)",
    "governing_junior": "Gobierno (socio minoritario)",
    "opposition": "Oposición parlamentaria",
}

PARTY_NAMES: dict[str, str] = {
    "psoe": "PSOE",
    "sumar": "Sumar",
    "pp": "PP",
    "vox": "Vox",
    "erc": "ERC",
    "pnv": "PNV",
}

TOPIC_NAMES: dict[str, str] = {
    "housing": "Vivienda",
    "education": "Educación",
    "health-social-services": "Sanidad y servicios sociales",
    "economy-work-tax": "Economía y empleo",
    "immigration": "Inmigración",
    "climate-energy": "Clima y energía",
    "foreign-policy-eu": "Política exterior y UE",
    "institutions-rights": "Instituciones y derechos",
}


def _esc(val: object) -> str:
    return html.escape(str(val), quote=True)


def render_commitment_card(cmt: CommitmentRecord) -> str:
    """Render a single commitment record into an accessible, semantic HTML article."""
    party_name = PARTY_NAMES.get(cmt.party_id, cmt.party_id.upper())
    topic_name = TOPIC_NAMES.get(cmt.topic_id, cmt.topic_id)
    status_label = STATUS_LABELS_ES.get(cmt.status, cmt.status)
    status_css = STATUS_CSS_CLASSES.get(cmt.status, "badge-status-blocked")
    role_label = GOVERNANCE_ROLE_LABELS_ES.get(cmt.governance_context.role, cmt.governance_context.role)

    cit_parts = []
    if cmt.pledge.page:
        cit_parts.append(f"pág. {cmt.pledge.page}")
    if cmt.pledge.section:
        cit_parts.append(cmt.pledge.section)
    cit_str = f"Programa electoral 2023 ({', '.join(cit_parts)})" if cit_parts else "Programa electoral 2023"

    ev_items_html = []
    for ev in cmt.evidence:
        source_label = ev.source_type.upper().replace("_", " ")
        ev_items_html.append(
            f'<li class="evidence-item">'
            f'<span class="evidence-type">[{_esc(source_label)}]</span> '
            f'<a href="{_esc(ev.url)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">'
            f'{_esc(ev.title)} ↗</a> '
            f'<span class="evidence-date">({_esc(ev.date)})</span>: '
            f'<span class="evidence-finding">{_esc(ev.finding_summary_es)}</span>'
            f'</li>'
        )
    evidence_html = "\n        ".join(ev_items_html)

    if cmt.governance_context.role == "opposition":
        context_note = (
            "Auditoría parlamentaria: Al ser fuerza de oposición sin competencias ejecutivas, "
            "se audita el sentido de su voto e iniciativas en Cortes (BOCG), no la ausencia de decretos."
        )
    else:
        context_note = (
            "Auditoría ejecutiva: Al formar parte del Gobierno del Estado, "
            "se auditan las leyes, decretos y resoluciones promulgadas en el Boletín Oficial del Estado (BOE)."
        )

    return (
        f'<article class="commitment-card" data-party="{_esc(cmt.party_id)}" data-topic="{_esc(cmt.topic_id)}" data-status="{_esc(cmt.status)}">\n'
        f'  <div class="commitment-header">\n'
        f'    <div class="commitment-badges">\n'
        f'      <span class="party">{_esc(party_name)}</span>\n'
        f'      <span class="badge-topic">{_esc(topic_name)}</span>\n'
        f'      <span class="badge-role">{_esc(role_label)}</span>\n'
        f'    </div>\n'
        f'    <span class="badge-status {status_css}">{_esc(status_label)}</span>\n'
        f'  </div>\n'
        f'  <div class="commitment-pledge">\n'
        f'    <p class="pledge-summary"><strong>Compromiso:</strong> {_esc(cmt.pledge.summary_es)}</p>\n'
        f'    <span class="commitment-pledge-citation">{_esc(cit_str)}</span>\n'
        f'  </div>\n'
        f'  <div class="commitment-evidence">\n'
        f'    <h4>Evidencia soberana primaria (BOE / Cortes Generales)</h4>\n'
        f'    <ul class="evidence-list">\n'
        f'        {evidence_html}\n'
        f'    </ul>\n'
        f'  </div>\n'
        f'  <p class="qualification">{_esc(context_note)}</p>\n'
        f'</article>'
    )


def render_commitments_content(commitments: list[CommitmentRecord]) -> str:
    """Render the inner HTML body for the commitments explorer."""
    topics_in_use = sorted({c.topic_id for c in commitments})
    topic_options = '<option value="all">Todos los temas</option>' + "".join(
        f'<option value="{_esc(tid)}">{_esc(TOPIC_NAMES.get(tid, tid))}</option>'
        for tid in topics_in_use
    )

    parties_in_use = sorted({c.party_id for c in commitments})
    party_options = '<option value="all">Todas las candidaturas</option>' + "".join(
        f'<option value="{_esc(pid)}">{_esc(PARTY_NAMES.get(pid, pid.upper()))}</option>'
        for pid in parties_in_use
    )

    statuses_in_use = sorted({c.status for c in commitments})
    status_options = '<option value="all">Todos los estados</option>' + "".join(
        f'<option value="{_esc(st)}">{_esc(STATUS_LABELS_ES.get(st, st))}</option>'
        for st in statuses_in_use
    )

    cards_html = "\n".join(render_commitment_card(c) for c in commitments)
    total_count = len(commitments)

    return f'''<div class="hero">
  <p class="eyebrow">Trazabilidad soberana · Legislatura previa (2023–2026)</p>
  <h1>Seguimiento de compromisos previos</h1>
  <p>Auditoría documental y contrastada de {total_count} medidas electorales de 2023 mediante fuentes soberanas primarias (BOE y Diario de Sesiones de las Cortes Generales).</p>
  <div class="warning">
    <strong>Criterio metodológico estricto:</strong> Este seguimiento no calcula porcentajes agregados de "honestidad" ni juzga intenciones políticas. Se basa exclusivamente en actos jurídicos y votaciones nominales oficiales. Las fuerzas de gobierno se auditan en el BOE y las de la oposición en sus votaciones en el Congreso.
  </div>
</div>

<div class="controls">
  <label>Tema
    <select id="commitment-topic-filter">{topic_options}</select>
  </label>
  <label>Candidatura
    <select id="commitment-party-filter">{party_options}</select>
  </label>
  <label>Estado de cumplimiento
    <select id="commitment-status-filter">{status_options}</select>
  </label>
</div>

<div id="commitments-results" class="commitments-grid">
{cards_html}
</div>
<p id="commitments-empty" class="empty-note" style="display: none; text-align: center; padding: 2rem;">No se encontraron compromisos que coincidan con los filtros seleccionados.</p>'''


def render_commitments_page(commitments: list[CommitmentRecord], *, nested: bool = True, image_url: str = "") -> str:
    """Render the full standalone commitments explorer page using the standard layout frame."""
    from elecciones2026.provisional2023 import frame
    content = render_commitments_content(commitments)
    return frame("Seguimiento de compromisos", content, nested=nested, image_url=image_url)

