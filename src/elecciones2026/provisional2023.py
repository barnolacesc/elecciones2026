"""Private, historical 2023 pilot. Never marks provisional claims as approved."""
from __future__ import annotations

import html
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

PARTIES = {"pp": "PP", "erc": "ERC", "pnv": "PNV", "sumar": "Sumar"}


def load(root: Path) -> dict:
    data = json.loads((root / "content/quiz/2023-provisional.json").read_text(encoding="utf-8"))
    register = json.loads((root / "content/sources/register.json").read_text(encoding="utf-8"))
    sources = {s["party_id"]: s for s in register["sources"] if s["election_id"] == "es-gen-2023"}
    assert data["election_id"] == "es-gen-2023" and data["status"] == "historical-provisional-private"
    assert set(sources) == set(PARTIES)
    assert len(data["positions"]) >= 12
    topic_ids = {t["id"] for t in data["topics"]}
    for position in data["positions"]:
        assert position["party"] in PARTIES
        assert position["topic"] in topic_ids
        source = sources[position["party"]]
        url = source["direct_url"]
        parsed = urlsplit(url)
        assert parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
        assert isinstance(source["sha256"], str) and len(source["sha256"]) == 64
        assert isinstance(position["page"], int) and position["page"] > 0
        assert all(position.get(k) for k in ("summary", "title", "locator", "qualification", "measure_id", "measure_title"))
        position["url"] = url + f'#page={position["page"]}'
        position["sha256"] = source["sha256"]
    return data


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def frame(title: str, body: str, *, nested: bool = False, image_url: str = "", extra_script: str = "") -> str:
    root = "../" if nested else "./"
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="referrer" content="no-referrer">
<meta property="og:image" content="{esc(image_url)}">
<title>{esc(title)} · Generales 2023 · piloto privado</title>
<link rel="stylesheet" href="{root}pilot-2023.css"></head>
<body><a class="skip" href="#principal">Saltar al contenido</a>
<header><a class="brand" href="{root}">Generales 2023 <small>piloto privado</small></a>
<nav class="desktop-nav" aria-label="Navegación principal"><a href="{root}">Comparador</a><a href="{root}cuestionario/">Cuestionario</a><a href="{root}presupuestos/">Presupuestos</a><a href="{root}simulador/">Simulador</a><a href="{root}compromisos/">Compromisos</a><a href="{root}fuentes/">Fuentes</a></nav>
<details class="mobile-nav"><summary aria-label="Menú de navegación">Menú</summary><nav aria-label="Navegación móvil"><a href="{root}">Comparador</a><a href="{root}cuestionario/">Cuestionario</a><a href="{root}presupuestos/">Presupuestos</a><a href="{root}simulador/">Simulador</a><a href="{root}compromisos/">Compromisos</a><a href="{root}fuentes/">Fuentes</a></nav></details></header>
<main id="principal">{body}</main>
<footer><p>Archivo histórico de las elecciones generales del 23 de julio de 2023. No describe programas de 2026 ni recomienda el voto.</p>
<p>Resúmenes provisionales de medidas concretas; consulta el documento original. Una medida no seleccionada o ausente no implica oposición.</p></footer>
<script src="{root}pilot-2023.js" defer></script>{extra_script}</body></html>'''


def citation(position: dict) -> str:
    return (f'<a href="{esc(position["url"])}" target="_blank" rel="noopener noreferrer" '
            f'referrerpolicy="no-referrer">Programa original, PDF pág. {position["page"]} ↗</a>'
            f'<span class="locator">{esc(position["locator"])}</span>')


def card(position: dict) -> str:
    return (f'<article class="card" data-party="{esc(position["party"])}" data-topic="{esc(position["topic"])}">'
            f'<span class="party">{esc(PARTIES[position["party"]])}</span>'
            f'<h3>{esc(position["title"])}</h3><p>{esc(position["summary"])}</p>'
            f'<p class="qualification">Matiz: {esc(position["qualification"])}</p>'
            f'<p class="citation">{citation(position)}</p></article>')


def comparison(data: dict, image_url: str = "") -> str:
    topics = ''.join(f'<option value="{esc(t["id"])}">{esc(t["name"])}</option>' for t in data["topics"])
    parties = ''.join(f'<option value="{esc(pid)}">{esc(name)}</option>' for pid, name in PARTIES.items())
    sections_parts = []
    for t in data["topics"]:
        topic_positions = [p for p in data["positions"] if p["topic"] == t["id"]]
        measures: dict[str, dict] = {}
        for p in topic_positions:
            m_id = p["measure_id"]
            if m_id not in measures:
                measures[m_id] = {"title": p["measure_title"], "positions": []}
            measures[m_id]["positions"].append(p)
        m_parts = []
        for m_id, m_data in measures.items():
            m_parts.append(
                f'<div class="measure-group"><h3 class="measure-title">{esc(m_data["title"])}</h3>'
                f'<div class="cards">'
                + ''.join(card(p) for p in m_data["positions"])
                + '</div></div>'
            )
        sections_parts.append(
            f'<section class="topic-section" data-topic="{esc(t["id"])}">'
            f'<h2>{esc(t["name"])}</h2>' + ''.join(m_parts) + '</section>'
        )
    sections = ''.join(sections_parts)
    num_positions = len(data["positions"])
    num_topics = len(data["topics"])
    body = f'''<div class="hero pilot-home-hero"><p class="eyebrow">23J 2023 · piloto privado</p>
<h1>¿Qué proponen los partidos sobre lo que te importa?</h1>
<p class="pilot-home-lede">Elige un tema y compara medidas de PP, ERC, PNV y Sumar, con enlaces a sus programas originales.</p>
<div class="pilot-home-actions"><a class="button" href="#comparador">Comparar dos partidos →</a><a class="button button-secondary" href="./cuestionario/">Explorar el cuestionario →</a></div>
<p class="pilot-home-scope">{num_positions} medidas · {num_topics} temas · elecciones generales de 2023</p>
<details class="warning pilot-home-warning"><summary><strong>Piloto provisional:</strong> resúmenes sin revisión editorial humana. Lee los límites.</summary><p>Resúmenes asistidos por extracción de PDF. Las propuestas no son equivalentes entre sí; no inferimos acuerdos, desacuerdos ni resultados de gobierno. No es información de las elecciones de 2026. <a href="./fuentes/">Consulta las fuentes del piloto.</a></p></details></div>
<h2 id="comparador" tabindex="-1">Elige un tema y dos candidaturas</h2>
<div class="controls"><label>Tema <select id="pilot-topic">{topics}</select></label>
<label>Primera candidatura <select id="pilot-a">{parties}</select></label>
<label>Segunda candidatura <select id="pilot-b">{parties}</select></label>
<p id="pilot-error" role="alert" hidden>Selecciona dos candidaturas distintas.</p></div>
<div id="pilot-comparison" class="measure-groups" aria-live="polite"></div>
<details><summary>Ver las {num_positions} medidas y sus fuentes</summary>{sections}</details>'''
    return frame("Comparador de programas", body, image_url=image_url)


def quiz(data: dict, image_url: str = "") -> str:
    body = f'''<div class="hero"><p class="eyebrow">Cuestionario exploratorio · 2023</p><h1>Explora las medidas que priorizarías</h1>
<p>Lee una propuesta cada vez y expresa tu opinión sin conocer antes la candidatura. Al terminar podrás consultar sus autores y fuentes. Esto <strong>no calcula afinidad partidista</strong> ni recomienda el voto.</p>
<p class="warning">Piloto histórico y provisional, sin revisión editorial humana. Tus respuestas permanecen en esta pestaña; no se envían ni se guardan.</p></div>
<form id="pilot-quiz"><p id="pilot-progress" aria-live="polite"></p><fieldset><legend id="pilot-question"></legend><p id="pilot-statement"></p><div class="quiz-options">
<label class="quiz-option"><input type="radio" name="answer" value="strongly-agree">Totalmente de acuerdo</label>
<label class="quiz-option"><input type="radio" name="answer" value="agree">Más bien de acuerdo</label>
<label class="quiz-option"><input type="radio" name="answer" value="neutral">Indiferente</label>
<label class="quiz-option"><input type="radio" name="answer" value="disagree">Más bien en desacuerdo</label>
<label class="quiz-option"><input type="radio" name="answer" value="strongly-disagree">Totalmente en desacuerdo</label></div></fieldset>
<p id="pilot-answer-error" role="alert" hidden>Selecciona una respuesta para continuar.</p><button type="submit" class="button" id="pilot-next">Siguiente propuesta</button></form>
<div id="pilot-results" tabindex="-1" aria-live="polite"></div>'''
    return frame("Cuestionario exploratorio", body, nested=True, image_url=image_url)


def sources(data: dict, image_url: str = "") -> str:
    documents = {}
    for position in data["positions"]:
        documents[position["party"]] = position
    cards = ''.join(f'<article class="card"><h2>{esc(PARTIES[party])}</h2><p>Programa de las elecciones generales de 2023.</p>'
                    f'<p class="citation">{citation(position)}</p><p class="locator">SHA-256: {esc(position["sha256"])}</p></article>'
                    for party, position in documents.items())
    body = f'''<div class="hero"><p class="eyebrow">23J 2023 · privado · provisional</p><h1>Fuentes del piloto</h1>
<p>Los cuatro documentos originales usados en esta vista histórica. Las citas del comparador y del cuestionario enlazan a páginas concretas. Los resúmenes no tienen revisión editorial humana.</p></div>
<div class="cards">{cards}</div>'''
    return frame("Fuentes", body, nested=True, image_url=image_url)


def load_budget(root: Path) -> dict:
    path = root / "content/budget/2023-provisional.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["election_id"] == "es-gen-2023"
    assert data["status"] == "historical-provisional-private"
    assert "payload" in data and "manifest" in data and "bundle_id" in data
    return data


def budget(data: dict, budget_data: dict, image_url: str = "") -> str:
    from elecciones2026.budget_view import render_budget_content
    topic_labels = {t["id"]: t["name"] for t in data["topics"]}
    content = render_budget_content(
        budget_data["payload"],
        budget_data["manifest"],
        budget_data["bundle_id"],
        topic_labels,
        root_path="../",
        preview=True,
        chart_url="./grafico.svg",
    )
    extra_script = '<script src="../budget-chart.js" defer></script>'
    return frame("Presupuestos 2023", content, nested=True, image_url=image_url, extra_script=extra_script)


def load_simulator(root: Path) -> dict:
    path = root / "content/simulator/rules.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.0.0"
    assert data["total_seats"] == 350
    assert data["majority_threshold"] == 176
    return {
        "available": True,
        "mode": "reviewed",
        "election_id": "es-gen-2023",
        "chamber_id": data["chamber_id"],
        "chamber_name": data["chamber_name"],
        "total_seats": data["total_seats"],
        "majority_threshold": data["majority_threshold"],
        "rule_type": data["rule_type"],
        "description": data["description"],
        "investiture_second_ballot_rule": data.get("investiture_second_ballot_rule", "simple_majority"),
        "investiture_second_ballot_note": data.get("investiture_second_ballot_note", ""),
        "citations": data["citations"],
        "sample_groups": [
            {"id": "pp", "label": "Partido Popular", "seats": "137"},
            {"id": "psoe", "label": "PSOE", "seats": "121"},
            {"id": "vox", "label": "VOX", "seats": "33"},
            {"id": "sumar", "label": "Sumar", "seats": "31"},
            {"id": "erc", "label": "ERC", "seats": "7"},
            {"id": "junts", "label": "Junts", "seats": "7"},
            {"id": "ehbildu", "label": "EH Bildu", "seats": "6"},
            {"id": "pnv", "label": "EAJ-PNV", "seats": "5"},
            {"id": "bng", "label": "BNG", "seats": "1"},
            {"id": "cc", "label": "CC", "seats": "1"},
            {"id": "upn", "label": "UPN", "seats": "1"},
        ],
    }


def simulator(data: dict, simulator_data: dict, image_url: str = "") -> str:
    from elecciones2026.simulator import render_simulator_content
    content = render_simulator_content(simulator_data, mode="reviewed")
    extra_script = '<script src="../simulator-data.js" defer></script><script src="../simulator-engine.js" defer></script><script src="../simulator-ui.js" defer></script>'
    return frame("Simulador de escaños y mayorías", content, nested=True, image_url=image_url, extra_script=extra_script)


def commitments(commitments_list: list, image_url: str = "") -> str:
    from elecciones2026.commitments import render_commitments_content
    content = render_commitments_content(commitments_list)
    return frame("Seguimiento de compromisos", content, nested=True, image_url=image_url)


def write(root: Path, staging: Path, canonical_base: str) -> None:
    data = load(root)
    image = root / "site/assets/social-preview.png"
    image_digest = hashlib.sha256(image.read_bytes()).hexdigest()[:16]
    image_url = f"{canonical_base}/assets/social-preview-{image_digest}.png"
    (staging / "index.html").write_text(comparison(data, image_url), encoding="utf-8")
    quiz_dir = staging / "cuestionario"
    quiz_dir.mkdir(exist_ok=True)
    (quiz_dir / "index.html").write_text(quiz(data, image_url), encoding="utf-8")
    sources_dir = staging / "fuentes"
    sources_dir.mkdir(exist_ok=True)
    (sources_dir / "index.html").write_text(sources(data, image_url), encoding="utf-8")
    commitments_dir = root / "content/commitments"
    if commitments_dir.exists():
        from elecciones2026.commitments import load_all_commitments
        all_commitments = load_all_commitments(commitments_dir)
        cmt_dir = staging / "compromisos"
        cmt_dir.mkdir(exist_ok=True)
        (cmt_dir / "index.html").write_text(commitments(all_commitments, image_url), encoding="utf-8")
    budget_data = load_budget(root)
    if budget_data:
        budget_dir = staging / "presupuestos"
        budget_dir.mkdir(exist_ok=True)
        (budget_dir / "index.html").write_text(budget(data, budget_data, image_url), encoding="utf-8")
        from elecciones2026.budget_chart import share_svg
        chart_svg = share_svg(budget_data["payload"], budget_data["manifest"], budget_data["bundle_id"], preview=True)
        (budget_dir / "grafico.svg").write_text(chart_svg, encoding="utf-8")
        (staging / "budget-chart.js").write_bytes((root / "site/budget-chart.js").read_bytes())
    simulator_data = load_simulator(root)
    if simulator_data:
        sim_dir = staging / "simulador"
        sim_dir.mkdir(exist_ok=True)
        (sim_dir / "index.html").write_text(simulator(data, simulator_data, image_url), encoding="utf-8")
        encoded_profile = json.dumps(simulator_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        (staging / "simulator-data.js").write_text(f"window.SimulatorProfile = {encoded_profile};\n", encoding="utf-8")
        (staging / "simulator-engine.js").write_bytes((root / "site/simulator-engine.js").read_bytes())
        (staging / "simulator-ui.js").write_bytes((root / "site/simulator-ui.js").read_bytes())
    (staging / "pilot-2023.css").write_bytes((root / "site/pilot-2023.css").read_bytes())
    (staging / "pilot-2023.js").write_bytes((root / "site/pilot-2023.js").read_bytes())
    (staging / "pilot-2023-data.json").write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
