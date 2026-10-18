"""Offline seat and coalition simulator validation and static shell generation (Epic E5).

Maintains exact chamber rules, source citations, and private/reviewed isolation.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlsplit

from elecciones2026.schemas import ReviewRecord


class SimulatorValidationError(ValueError):
    """The simulator rule profile or scenario input is unsafe or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SimulatorValidationError(message)


def text(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"Missing or empty {label}.")
    return value.strip()


def safe_url(value: str) -> str:
    parsed = urlsplit(text(value, "source URL"))
    require(parsed.scheme == "https" and bool(parsed.hostname)
            and parsed.username is None and parsed.password is None,
            "Simulator citations require HTTPS without credentials.")
    return value


def dual_review(record: dict) -> None:
    require(record.get("review_status") == "approved", "Simulator profile is not approved.")
    reviewers = set()
    for raw in record.get("reviews", []):
        try:
            review = ReviewRecord(**raw)
        except (TypeError, ValueError) as error:
            raise SimulatorValidationError("Malformed simulator review record.") from error
        require(not review.validate(require_human=True), "Invalid human simulator review.")
        require(review.verdict == "approved", "Unresolved simulator review.")
        reviewers.add(review.reviewer_id)
    require(len(reviewers) >= 2, "Simulator profile requires two distinct human approvals.")


def prepare_simulator(path_or_dict: Path | dict, ctx: Any, *, mock: bool = False) -> dict:
    """Validate a simulator rule profile and return public bundle."""
    if isinstance(path_or_dict, Path):
        try:
            data = json.loads(path_or_dict.read_text(encoding="utf-8"))
        except (KeyError, TypeError, OSError, json.JSONDecodeError) as error:
            raise SimulatorValidationError(f"Malformed simulator input: {error}") from error
    else:
        data = path_or_dict

    require(data.get("schema_version") == "1.0.0", "Unsupported simulator schema version.")
    require(data.get("method_version") == "1.0.0", "Unsupported simulator method version.")
    text(data.get("chamber_id"), "chamber_id")
    text(data.get("chamber_name"), "chamber_name")

    total_seats = data.get("total_seats")
    require(isinstance(total_seats, int) and total_seats == 350, "Chamber total seats must be 350.")
    majority_threshold = data.get("majority_threshold")
    require(isinstance(majority_threshold, int) and majority_threshold == 176,
            "Chamber majority threshold must be 176.")
    require(data.get("rule_type") == "absolute_majority", "Rule type must be absolute_majority.")

    if mock:
        require(data.get("mode") == "mock" and data.get("election_id") == "simulator-fixture",
                "Mock simulator profile must declare mock mode and fixture election ID.")
    else:
        require(data.get("mode") == "reviewed" and data.get("election_id") == ctx.election_id,
                "Reviewed simulator profile must match target election ID.")
        dual_review(data)

    citations = data.get("citations", [])
    require(isinstance(citations, list) and len(citations) >= 2,
            "Simulator profile must cite at least two official legal sources.")

    public_citations = []
    for cit in citations:
        public_citations.append({
            "source_id": text(cit.get("source_id"), "citation source_id"),
            "title": text(cit.get("title"), "citation title"),
            "article": text(cit.get("article"), "citation article"),
            "url": safe_url(cit.get("url", "")),
            "summary": text(cit.get("summary"), "citation summary")
        })

    sample_groups = []
    for raw_g in data.get("sample_groups", []):
        sample_groups.append({
            "id": text(raw_g.get("id"), "sample group id"),
            "label": text(raw_g.get("label"), "sample group label"),
            "seats": str(raw_g.get("seats", "0"))
        })

    return {
        "available": True,
        "mode": "mock" if mock else "reviewed",
        "election_id": data["election_id"],
        "chamber_id": data["chamber_id"],
        "chamber_name": data["chamber_name"],
        "total_seats": total_seats,
        "majority_threshold": majority_threshold,
        "rule_type": data["rule_type"],
        "description": text(data.get("description", ""), "profile description"),
        "investiture_second_ballot_rule": data.get("investiture_second_ballot_rule", "simple_majority"),
        "investiture_second_ballot_note": data.get("investiture_second_ballot_note", ""),
        "citations": public_citations,
        "sample_groups": sample_groups
    }


def render_simulator_content(profile: Optional[dict], mode: str = "unavailable") -> str:
    """Render the inner HTML for /simulador/ depending on build mode."""
    if mode == "unavailable" or not profile or not profile.get("available"):
        return """
    <div class="simulator-shell">
      <p class="simulator-kicker">Herramientas parlamentarias</p>
      <h1>Simulador de escaños y mayorías</h1>
      <div class="simulator-threshold-banner chamber-overflow">
        <div class="simulator-threshold-title">Herramienta no disponible en esta versión</div>
        <p class="simulator-threshold-desc">
          El simulador interactivo no está habilitado en este despliegue. A continuación se explican las reglas parlamentarias y fuentes oficiales aplicables.
        </p>
      </div>

      <section class="simulator-legal-notes">
        <h2>Reglas de investidura y composición del Congreso</h2>
        <p>
          El Congreso de los Diputados está compuesto por <strong>350 Diputados</strong> (art. 68.1 de la Constitución Española y art. 162.1 de la LOREG).
        </p>
        <p>
          La investidura del Presidente del Gobierno se rige por el artículo 99.3 de la Constitución:
        </p>
        <ul class="simulator-legal-list">
          <li><strong>Primera votación:</strong> Requiere el voto de la mayoría absoluta de los miembros del Congreso (<strong>176 escaños</strong> de 350).</li>
          <li><strong>Segunda votación:</strong> Si no se alcanza la mayoría absoluta, se somete la propuesta a nueva votación 48 horas después, entendiéndose otorgada la confianza si se obtiene <strong>mayoría simple</strong> (más votos a favor que en contra).</li>
        </ul>
        <h3>Fuentes oficiales</h3>
        <ul class="simulator-legal-list">
          <li><a href="https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229" target="_blank" rel="noopener noreferrer">Constitución Española (BOE-A-1978-31229)</a>: Artículos 68.1 y 99.3.</li>
          <li><a href="https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672" target="_blank" rel="noopener noreferrer">Ley Orgánica 5/1985 del Régimen Electoral General (LOREG)</a>: Artículo 162.1.</li>
          <li><a href="https://www.boe.es/buscar/act.php?id=BOE-A-1982-5196" target="_blank" rel="noopener noreferrer">Reglamento del Congreso de los Diputados</a>: Artículo 171.5.</li>
        </ul>
      </section>
    </div>
"""

    is_mock = (mode == "mock")
    banner_mock = ""
    if is_mock:
        banner_mock = """
      <div class="quiz-notice" style="margin-bottom: 1.25rem;">
        <strong>Demostración técnica previa:</strong> Los datos y grupos son ficticios para probar el funcionamiento interactivo en el navegador.
      </div>
"""

    citations_html = "".join(f"""
          <li>
            <strong>{escape(c['title'])} ({escape(c['article'])}):</strong> {escape(c['summary'])}
            <br>
            <a href="{escape(c['url'])}" target="_blank" rel="noopener noreferrer">Consultar texto oficial en el BOE</a>
          </li>
""" for c in profile.get("citations", []))

    second_ballot_note = escape(profile.get("investiture_second_ballot_note", ""))

    return f"""
    <div class="simulator-shell" id="simulator-app">
      <p class="simulator-kicker">Herramientas parlamentarias · Congreso de los Diputados</p>
      <h1>Simulador de escaños y mayorías</h1>
      <p class="simulator-intro">
        Introduce un reparto hipotético de escaños para el Congreso de los Diputados (350 escaños) y comprueba combinaciones de investidura frente a la mayoría absoluta (176 escaños).
      </p>

      {banner_mock}

      <div id="simulator-status" class="sr-only" role="status" aria-live="polite"></div>

      <!-- Action buttons -->
      <div class="simulator-actions">
        <button type="button" id="simulator-add-group" class="simulator-primary">
          <span aria-hidden="true">+</span> Añadir grupo
        </button>
        <button type="button" id="simulator-sample">
          Cargar ejemplo
        </button>
        <button type="button" id="simulator-reset">
          Restablecer
        </button>
      </div>

      <!-- Summary Stat Cards -->
      <div class="simulator-summary-grid">
        <div class="simulator-stat-card">
          <span class="simulator-stat-label">Escaños asignados</span>
          <span class="simulator-stat-val" id="stat-assigned">0</span>
          <span class="simulator-stat-sub">de 350 escaños</span>
        </div>
        <div class="simulator-stat-card">
          <span class="simulator-stat-label">Sin asignar</span>
          <span class="simulator-stat-val" id="stat-unassigned">350</span>
          <span class="simulator-stat-sub">restantes</span>
        </div>
        <div class="simulator-stat-card">
          <span class="simulator-stat-label">Suma coalición</span>
          <span class="simulator-stat-val" id="stat-coalition">0</span>
          <span class="simulator-stat-sub">grupos marcados</span>
        </div>
        <div class="simulator-stat-card">
          <span class="simulator-stat-label">Mayoría absoluta</span>
          <span class="simulator-stat-val" id="stat-threshold">—</span>
          <span class="simulator-stat-sub">umbral 176</span>
        </div>
      </div>

      <!-- Coalition status banner -->
      <div id="simulator-threshold-banner" class="simulator-threshold-banner">
        <div class="simulator-threshold-title">Selecciona grupos para sumar sus escaños</div>
        <p class="simulator-threshold-desc">Marca las casillas de la columna «Coalición» para comprobar si alcanzan la mayoría absoluta de 176 escaños.</p>
      </div>

      <!-- Hemicycle Chart Card -->
      <section class="simulator-hemicycle-card" aria-label="Visualización gráfica del hemiciclo">
        <h2 class="sr-only">Hemiciclo del Congreso</h2>
        <div id="simulator-hemicycle-chart" class="simulator-hemicycle-wrapper"></div>
        <div id="simulator-hemicycle-legend" class="simulator-hemicycle-legend"></div>
      </section>

      <!-- Error summary if applicable -->
      <div id="simulator-errors-container" hidden></div>

      <!-- Groups data table -->
      <section class="simulator-table-container" aria-label="Tabla de reparto de escaños">
        <h2>Grupos parlamentarios</h2>
        <p style="font-size: 0.9rem; color: var(--color-text-secondary); margin-bottom: 0.8rem;">
          Puedes editar el nombre y los escaños de cada grupo (máximo 30 grupos y 350 escaños en total).
        </p>
        <table class="simulator-table">
          <thead>
            <tr>
              <th scope="col" style="min-width: 140px;">Grupo</th>
              <th scope="col" class="num-cell" style="min-width: 90px;">Escaños</th>
              <th scope="col" class="num-cell">% Cámara</th>
              <th scope="col" style="text-align: center;">Coalición</th>
              <th scope="col" style="text-align: right;">Acciones</th>
            </tr>
          </thead>
          <tbody id="simulator-groups-tbody"></tbody>
        </table>
      </section>

      <!-- Share scenario without tracking -->
      <section class="simulator-share-box" aria-label="Compartir escenario">
        <h3>Compartir escenario</h3>
        <p>
          Genera un enlace directo para compartir este reparto y combinación de coalición. No recopila datos personales ni utiliza rastreadores.
        </p>
        <div class="simulator-share-row">
          <input type="text" id="simulator-share-input" readonly aria-label="Enlace para compartir este escenario" />
          <button type="button" id="simulator-copy-btn">Copiar enlace</button>
          <button type="button" id="simulator-share-btn" class="simulator-primary">Compartir</button>
        </div>
        <div id="simulator-share-feedback" class="simulator-feedback" role="status" aria-live="polite"></div>
      </section>

      <!-- Legal & Constitutional notes -->
      <details class="simulator-legal-notes">
        <summary>Reglas de mayoría, investidura y fuentes constitucionales</summary>
        <p>
          El Congreso de los Diputados cuenta con <strong>350 escaños</strong>. La mayoría absoluta se sitúa en <strong>176 escaños</strong>.
        </p>
        {f'<p><em>Nota sobre la investidura:</em> {second_ballot_note}</p>' if second_ballot_note else ''}
        <ul class="simulator-legal-list">
          {citations_html}
        </ul>
      </details>
    </div>
"""
