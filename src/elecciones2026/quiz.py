"""Offline quiz validation and static shell generation (E4.2).

Mock data has a separate election identity and requires explicit preview opt-in.
Political input must resolve to the site's approved source records.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
from html import escape
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from elecciones2026.methodology import CORE_TOPIC_IDS
from elecciones2026.schemas import ReviewRecord, PLACEHOLDER_REVIEWER_PATTERN
from elecciones2026.editorial import PERMITTED_QUOTE_RIGHTS


class QuizValidationError(ValueError):
    """The complete quiz input is unsafe or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise QuizValidationError(message)


def text(value, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"Missing {label}.")
    return value


def dual_review(record: dict) -> None:
    require(record.get("review_status") == "approved", "Quiz record is not approved.")
    reviewers = set()
    for raw in record.get("reviews", []):
        try:
            review = ReviewRecord(**raw)
        except (TypeError, ValueError) as error:
            raise QuizValidationError("Malformed quiz review.") from error
        require(not review.validate(require_human=True), "Invalid human quiz review.")
        require(review.verdict == "approved", "Unresolved quiz review.")
        reviewers.add(review.reviewer_id)
    require(len(reviewers) >= 2, "Quiz record needs two distinct human approvals.")


def safe_url(value: str) -> str:
    parsed = urlsplit(text(value, "source URL"))
    require(parsed.scheme == "https" and bool(parsed.hostname)
            and parsed.username is None and parsed.password is None,
            "Quiz citations require HTTPS without credentials.")
    return value


def prepare_quiz(path: Path, ctx, *, mock: bool = False) -> dict:
    """Resolve a private authoring set to a minimal public bundle, or reject it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return _prepare_quiz(data, ctx, mock=mock)
    except (KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        raise QuizValidationError("Malformed quiz input.") from error


def _prepare_quiz(data: dict, ctx, *, mock: bool) -> dict:
    require(data.get("schema_version") == "1.0.0", "Unsupported quiz schema.")
    require(data.get("method_version") == "1.0.0", "Unsupported quiz method.")
    require(data.get("taxonomy_version") == ctx.taxonomy.taxonomy_version,
            "Quiz taxonomy version mismatch.")
    text(data.get("version"), "set version")
    if mock:
        require(data.get("mode") == "mock" and data.get("election_id") == "quiz-fixture",
                "Mock quiz must use its isolated fixture identity.")
    else:
        require(data.get("mode") == "reviewed" and data.get("election_id") == ctx.election_id,
                "Quiz election/mode mismatch; mock data cannot enter reviewed output.")
        dual_review(data)

    items = data["items"]
    require(len(items) == 16, "Quiz needs exactly 16 items.")
    require(Counter(item["topic_id"] for item in items) == Counter({t: 2 for t in CORE_TOPIC_IDS}),
            "Quiz needs exactly two items per core topic.")
    require(len({item["id"] for item in items}) == 16, "Duplicate quiz item.")
    require(len({item["measure_id"] for item in items}) == 16, "Duplicate quiz measure.")
    ordered = sorted(items, key=lambda item: (CORE_TOPIC_IDS.index(item["topic_id"]), item["id"]))
    public_items = []
    for item in ordered:
        for key in ("id", "measure_id", "text"):
            text(item.get(key), f"item {key}")
        require(all(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", item[key]) for key in ('id', 'measure_id')),
                "Quiz item and measure IDs must be kebab-case identifiers.")
        require(isinstance(item.get("qualifications", []), list)
                and all(isinstance(q, str) for q in item.get("qualifications", [])),
                "Invalid item qualifications.")
        if not mock:
            dual_review(item)
            text(item.get("selection_rationale"), "item selection rationale")
        public_items.append({key: item.get(key, []) for key in
                             ("id", "measure_id", "topic_id", "text", "qualifications")})

    parties = data["parties"]
    require(len({p["id"] for p in parties}) == len(parties), "Duplicate quiz party.")
    if not mock:
        included = {s.party_id for s in ctx.register.sources if s.election_id == ctx.election_id}
        require({p["id"] for p in parties} == included, "Quiz must cover the full inclusion register.")
    programmes = {}
    if not mock:
        for filename in sorted((ctx.content_dir / "examples" / "programmes").glob("*.json")):
            programme = json.loads(filename.read_text())
            require(programme["programme_id"] not in programmes, "Duplicate programme reference.")
            programmes[programme["programme_id"]] = programme
    public_parties = []
    for party in parties:
        text(party["id"], "party ID")
        require(bool(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", party['id'])), "Invalid party identifier.")
        name = text(party.get("name"), "party name")
        if mock:
            require(party["id"].startswith("mock-") and "ficticio" in name,
                    "Mock parties must be visibly fictional.")
        else:
            require(party["id"] in ctx.parties and not ctx.parties[party["id"]].is_fixture,
                    "Unknown or fictional party in reviewed quiz.")
            require(name == ctx.parties[party["id"]].display_name, "Party name mismatch.")
        raw_positions = party["positions"]
        require(len(raw_positions) == 16 and len({p["item_id"] for p in raw_positions}) == 16,
                "Every party needs one position or gap for each item.")
        mappings = {p["item_id"]: p for p in raw_positions}
        require(set(mappings) == {i["id"] for i in ordered}, "Position item mismatch.")
        positions = []
        for item in ordered:
            mapping = mappings[item["id"]]
            status = mapping.get("status")
            require(status in {"support", "reject", "missing", "partial", "conflicting", "unverified", "replaced"},
                    "Invalid quiz coverage status.")
            if status in {"support", "reject"}:
                value = mapping.get("value")
                require(type(value) is int and value == (1 if status == "support" else -1),
                        "Numeric position contradicts its reviewed status.")
                source = None if mock else resolve_source(mapping, item, party, ctx, programmes)
                positions.append({"item_id": item["id"], "status": status, "value": value, "source": source})
            else:
                require(mapping.get("value") is None, "A source gap must not have a score.")
                positions.append({"item_id": item["id"], "status": status, "value": None,
                                  "reason": text(mapping.get("reason"), "gap reason"), "source": None})
        public_parties.append({"id": party["id"], "name": name, "positions": positions,
                               "eligible": all(p["value"] is not None for p in positions)})
    return {"schema_version": "1.0.0", "method_version": data["method_version"],
            "version": data["version"], "election_id": data["election_id"],
            "taxonomy_version": data["taxonomy_version"], "mode": data["mode"],
            "available": sum(p["eligible"] for p in public_parties) >= 2,
            "topics": [{"id": t.id, "name": t.name_es} for t in ctx.taxonomy.topics],
            "items": public_items, "parties": public_parties}


def resolve_source(mapping: dict, item: dict, party: dict, ctx, programmes: dict) -> dict:
    dual_review(mapping)
    statement = ctx.statements.get(mapping.get("statement_id"))
    require(statement is not None, "Quiz statement is not in the approved publish set.")
    require(not statement.is_fixture and not statement.validate(target_election_id=ctx.election_id)
            and statement.review_status == "approved", "Invalid quiz statement.")
    require(statement.party_id == party["id"] and statement.topic_id == item["topic_id"],
            "Quiz mapping party/topic mismatch.")
    for review in statement.reviews:
        require(not review.validate(require_human=True) and review.verdict == "approved",
                "Statement needs genuine human approval evidence.")
    require(len({r.reviewer_id for r in statement.reviews}) >= 2, "Statement lacks dual review.")
    sources = [s for s in ctx.register.sources if s.party_id == party["id"]
               and s.election_id == ctx.election_id and s.version == statement.source_version
               and statement.source_url in (s.official_url, s.direct_url)]
    require(len(sources) == 1, "Quiz citation does not resolve to one source.")
    source = sources[0]
    require(source.status == "verified" and source.rights_review.status in PERMITTED_QUOTE_RIGHTS,
            "Quiz programme verification or rights are pending.")
    rights = source.rights_review
    require(bool(rights.reviewed_by) and not PLACEHOLDER_REVIEWER_PATTERN.match(rights.reviewed_by)
            and bool(rights.review_date) and date.fromisoformat(rights.review_date) <= date.today(),
            "Invalid programme rights review.")
    programme = programmes.get(statement.programme_id, {})
    require(all(programme.get(k) == v for k, v in (
        ("election_id", ctx.election_id), ("candidacy_id", party["id"]),
        ("version", source.version), ("sha256", source.sha256), ("status", "official"),
        ("rights_status", "verified_quotation_permitted"), ("is_fixture", False))),
        "Quiz programme provenance mismatch or incomplete programme.")
    require(isinstance(source.sha256, str) and len(source.sha256) == 64
            and all(c in "0123456789abcdef" for c in source.sha256), "Invalid source checksum.")
    require(bool(statement.source_page or statement.source_section), "Quiz needs an exact source locator.")
    require(bool(programme.get("publication_date") and source.publication_date),
            "Quiz source publication dates are pending.")
    for correction in ctx.corrections:
        if correction.target_type == "statement" and correction.target_id == statement.id:
            require(statement.correction_id == correction.id
                    and statement.last_reviewed_date >= correction.correction_date
                    and all(r.review_date >= correction.correction_date for r in statement.reviews),
                    "Corrected quiz statement needs fresh review.")
    return {"statement_id": statement.id, "programme_id": statement.programme_id,
            "url": safe_url(statement.source_url), "version": source.version,
            "sha256": source.sha256, "page": statement.source_page, "section": statement.source_section,
            "qualifications": statement.qualifications, "summary": statement.summary,
            "rights_status": rights.status, "review_date": statement.last_reviewed_date}


def render_quiz_content(bundle: dict | None) -> str:
    """Render a no-script-readable shell; script only enhances an available set."""
    available = bundle is not None and bundle["available"]
    mock = bundle is not None and bundle["mode"] == "mock"
    notice = ('<p class="quiz-notice"><strong>Demostración con datos ficticios.</strong> '
              'Los ejemplos no son partidos reales ni medidas de un programa.</p>') if mock else ''
    coverage = []
    for party in (bundle or {}).get("parties", []):
        coverage.append(f'<h3>{escape(party["name"])}</h3>')
        coverage.append('<p>' + ('Cobertura completa.' if party['eligible'] else 'Cobertura insuficiente: sin porcentaje.') + '</p>')
        for index, position in enumerate(party['positions'], 1):
            source = position['source']
            coverage.append(f'<p>Pregunta {index}: {escape(position.get("reason", "Dato ficticio" if mock else "Posición documentada"))}</p>')
            if source:
                coverage.append(f'<p>Programa {escape(source["programme_id"])}. Derechos: {escape(source["rights_status"])}.</p>')
                coverage.append(f'<p>{escape(source["summary"])} · Versión {escape(source["version"])} · Página {escape(source["page"] or "—")} · Sección {escape(source["section"] or "—")} · Revisión {escape(source["review_date"])}</p>')
                coverage.extend(f'<p>{escape(q)}</p>' for q in source['qualifications'])
                coverage.append(f'<p>SHA-256: {escape(source["sha256"])}</p>')
                coverage.append(f'<a href="{escape(source["url"], quote=True)}" rel="noopener noreferrer" referrerpolicy="no-referrer" target="_blank">Fuente oficial (ventana nueva)</a>')
    if not available:
        return f'''<section class="quiz-shell">{notice}<h1>Cuestionario de coincidencia</h1>
        <p>El cuestionario aún no está disponible. Faltan preguntas y fuentes revisadas
        con cobertura suficiente.</p><p><a href="../metodo/">Consultar el método editorial</a></p>
        <p><a href="../fuentes/">Consultar las fuentes</a></p>
        {('<details><summary>Cobertura del conjunto</summary>' + ''.join(coverage) + '</details>') if bundle else ''}
        </section>'''
    return f'''<section class="quiz-shell">
      {notice}
      <div id="quiz-app" aria-label="Cuestionario">
        <h1>Explora la coincidencia, pregunta a pregunta</h1>
        <p>16 preguntas, 8 temas. Puedes omitir cualquier pregunta y cambiar tus respuestas.</p>
        <p>Las respuestas quedan solo en la memoria de esta pestaña. Al salir o recargar se borran.
        No hay cuentas ni envío de respuestas. Este resultado no recomienda a quién votar.</p>
        <noscript><p>Para calcular el resultado en tu navegador necesitas activar JavaScript.</p></noscript>
      </div>
      <p id="quiz-status" class="sr-only" role="status" aria-live="polite"></p>
      <details id="quiz-method"><summary>Cómo se calcula y qué fuentes usa</summary>
        <p>Cada tema tiene el mismo peso al empezar. Calculamos la coincidencia de cada respuesta
        con la posición documentada, hacemos la media de cada tema respondido y después la media
        de esos temas. Puedes dar el doble de peso a un tema.</p>
        <p>Omitir no significa estar en contra. Una respuesta neutral sí cuenta. Necesitas al menos
        8 respuestas en 4 temas para ver porcentajes. No es una medida de confianza estadística.</p>
        <p>Los partidos sin cobertura completa no reciben un porcentaje. La falta de información
        no equivale a estar en contra. Las preguntas omitidas pueden cambiar el cálculo completo.</p>
        <p>Los intervalos muestran escenarios posibles, no probabilidades. Los resultados se presentan
        por orden alfabético, sin recomendar un partido.</p>
        <p>Fórmula por pregunta: 1 − |respuesta − posición| / 2. Respuestas de −1 a 1;
        posiciones documentadas: −1 o 1.</p>
        <p>Versión del conjunto: {escape(bundle['version'])}. Método: {escape(bundle['method_version'])}.</p>
        <div id="quiz-coverage">{''.join(coverage)}</div>
      </details>
    </section>'''
