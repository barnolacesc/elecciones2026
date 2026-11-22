"""Exploratory questionnaire for 2026 general election (E4.2 / E4.3).

Presents 24 blind proposals (2 per topic across 12 topics) from approved party
manifestos with verified legal baseline subtitles. Answers remain strictly in
browser memory. Upon completion, reveals proposing parties and official PDF sources.
Zero tracking, zero cookies, and no political affinity calculation from unreviewed positions.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


class ExploratoryQuizError(ValueError):
    """The exploratory quiz bank is invalid or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExploratoryQuizError(message)


def validate_exploratory_bank(data: dict, ctx) -> dict:
    """Validate the 2026 exploratory bank and prepare it grouped by topic."""
    require(isinstance(data, dict), "Quiz bank must be a JSON object.")
    require(data.get("taxonomy_version") == ctx.taxonomy.taxonomy_version,
            "Quiz bank taxonomy version mismatch.")

    items = data.get("items")
    require(isinstance(items, list) and len(items) == 96,
            "Exploratory quiz bank needs exactly 96 items.")

    valid_topics = {t.id: t for t in ctx.taxonomy.topics}
    require(len(valid_topics) == 12, "Exploratory quiz requires 12 taxonomy topics.")

    seen_ids = set()
    topic_items = {t_id: [] for t_id in valid_topics}

    for item in items:
        item_id = item.get("id")
        require(isinstance(item_id, str) and bool(re.fullmatch(r"quiz-29n-[a-z0-9\-]+", item_id)),
                f"Invalid item ID: {item_id}")
        require(item_id not in seen_ids, f"Duplicate item ID: {item_id}")
        seen_ids.add(item_id)

        topic_id = item.get("topic_id")
        require(topic_id in valid_topics, f"Unknown topic ID: {topic_id} in {item_id}")

        statement = item.get("statement")
        require(isinstance(statement, str) and bool(statement.strip()),
                f"Missing statement text in {item_id}")

        qualifications = item.get("qualifications", [])
        require(isinstance(qualifications, list) and all(isinstance(q, str) for q in qualifications),
                f"Invalid qualifications in {item_id}")

        source = item.get("source")
        require(isinstance(source, dict), f"Missing source dict in {item_id}")
        require(isinstance(source.get("publisher"), str) and bool(source["publisher"].strip()),
                f"Missing source publisher in {item_id}")
        require(isinstance(source.get("page"), (str, int)), f"Missing source page in {item_id}")

        url = source.get("url")
        require(isinstance(url, str) and url.startswith("https://"),
                f"Source URL must be HTTPS in {item_id}")
        parsed_url = urlsplit(url)
        require(bool(parsed_url.hostname) and parsed_url.username is None and parsed_url.password is None,
                f"Unsafe source URL in {item_id}")

        stmt_id = source.get("statement_id")
        if stmt_id and ctx.statements:
            require(stmt_id in ctx.statements, f"Statement {stmt_id} not found in approved statements.")
            approved_stmt = ctx.statements[stmt_id]
            require(approved_stmt.review_status == "approved",
                    f"Statement {stmt_id} is not approved.")

        copy_url = source.get("verified_external_copy")
        if copy_url:
            require(isinstance(copy_url, str) and copy_url.startswith("https://"),
                    f"Verified copy URL must be HTTPS in {item_id}")

        context = item.get("context")
        clean_context = None
        if context is not None:
            require(isinstance(context, dict), f"Context must be a dict in {item_id}")
            c_text = context.get("text")
            require(isinstance(c_text, str) and bool(c_text.strip()),
                    f"Missing context text in {item_id}")
            refs = context.get("references", [])
            clean_refs = []
            for r in refs:
                require(isinstance(r, dict) and "label" in r and "url" in r,
                        f"Invalid reference in {item_id}")
                ref_url = r["url"]
                require(isinstance(ref_url, str) and ref_url.startswith("https://"),
                        f"Reference URL must be HTTPS in {item_id}")
                clean_refs.append({"label": r["label"], "url": ref_url})

            clean_context = {
                "kind": context.get("kind", "baseline"),
                "status": context.get("status", "draft"),
                "text": c_text,
                "reference_date": context.get("reference_date"),
                "period": context.get("period"),
                "references": clean_refs,
            }

        clean_item = {
            "id": item_id,
            "topic_id": topic_id,
            "statement": statement,
            "qualifications": qualifications,
            "source": {
                "publisher": source["publisher"],
                "page": str(source["page"]),
                "url": url,
            },
            "context": clean_context,
        }
        if copy_url:
            clean_item["source"]["verified_external_copy"] = copy_url

        topic_items[topic_id].append(clean_item)

    for topic_id, t_items in topic_items.items():
        require(len(t_items) == 8, f"Topic {topic_id} needs exactly 8 items, found {len(t_items)}.")

    prepared_topics = [
        {
            "id": topic.id,
            "name": topic.name_es,
            "items": topic_items[topic.id],
        }
        for topic in ctx.taxonomy.topics
    ]

    return {
        "batch_id": data.get("batch_id", "quiz-29n-subtitulos-v2"),
        "election_id": ctx.election_id,
        "taxonomy_version": ctx.taxonomy.taxonomy_version,
        "mode": "exploratory",
        "available": True,
        "total_items": len(items),
        "topics": prepared_topics,
    }


def render_exploratory_quiz_content() -> str:
    """Render the accessible static shell for the exploratory questionnaire."""
    return '''<section class="quiz-shell exploratory-quiz">
  <div class="exploratory-intro">
    <p class="quiz-kicker">Elecciones Generales · 29 de noviembre de 2026</p>
    <h1>Cuestionario de propuestas del 29-N</h1>
    <p class="quiz-lead">
      Lee cada propuesta y marca tu grado de acuerdo sin conocer la candidatura de antemano.
      La selección contiene 24 enunciados aleatorios y equilibrados: exactamente dos por cada uno
      de los 12 temas electorales.
    </p>
    <div class="quiz-notice">
      <strong>Privacidad y neutralidad:</strong> Tus respuestas se procesan únicamente en la memoria
      de esta pestaña y se borran al cerrarla o recargarla. No hay cuentas, cookies ni almacenamiento.
      Al terminar podrás consultar qué partido propuso cada medida y el enlace directo a la página
      de su programa original. Este ejercicio <em>no calcula afinidad partidista ni recomienda a quién votar</em>.
    </div>
  </div>

  <div class="exploratory-controls">
    <button type="button" id="draw" class="button button-secondary">Nuevo cuestionario (24 propuestas)</button>
    <p id="status" role="status" aria-live="polite" class="exploratory-status">24 enunciados en 12 temas</p>
  </div>

  <noscript>
    <div class="quiz-notice">
      <strong>JavaScript requerido:</strong> Para generar la selección aleatoria de propuestas y comprobar las fuentes al terminar, activa JavaScript en tu navegador.
    </div>
  </noscript>

  <form id="exploratory-form" onsubmit="return false;">
    <div id="topics" class="exploratory-topics"></div>
    <div class="exploratory-actions">
      <button type="button" id="finish" class="button quiz-primary">Terminar y ver las fuentes</button>
    </div>
  </form>

  <div id="results" class="exploratory-results" hidden tabindex="-1">
    <h2 id="results-heading" tabindex="-1">Tus respuestas y fuentes originales</h2>
    <p class="results-desc">
      A continuación puedes contrastar tu grado de acuerdo con la autoría de cada medida y abrir el documento oficial registrado.
    </p>
    <div class="results-toolbar">
      <button type="button" id="edit" class="button button-secondary">← Volver a mis respuestas</button>
      <button type="button" id="redraw-results" class="button">Nuevo cuestionario</button>
    </div>
    <div id="result-items" class="result-topics-list"></div>
  </div>
</section>'''
