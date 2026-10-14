"""Private, historical 2023 pilot. Never marks provisional claims as approved."""
from __future__ import annotations

import html
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
    assert len(data["positions"]) == 12
    assert {(p["topic"], p["party"]) for p in data["positions"]} == {
        (t["id"], party) for t in data["topics"] for party in PARTIES
    }
    for position in data["positions"]:
        source = sources[position["party"]]
        url = source["direct_url"]
        parsed = urlsplit(url)
        assert parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password
        assert isinstance(source["sha256"], str) and len(source["sha256"]) == 64
        assert isinstance(position["page"], int) and position["page"] > 0
        assert all(position.get(k) for k in ("summary", "title", "locator", "qualification"))
        position["url"] = url + f'#page={position["page"]}'
        position["sha256"] = source["sha256"]
    return data


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def frame(title: str, body: str, *, nested: bool = False) -> str:
    root = "../" if nested else "./"
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="referrer" content="no-referrer">
<title>{esc(title)} · Generales 2023 · piloto privado</title>
<link rel="stylesheet" href="{root}pilot-2023.css"></head>
<body><a class="skip" href="#principal">Saltar al contenido</a>
<header><a class="brand" href="{root}">Generales 2023 <small>piloto privado</small></a>
<nav aria-label="Navegación principal"><a href="{root}">Comparador</a><a href="{root}cuestionario/">Cuestionario</a><a href="{root}fuentes/">Fuentes</a></nav></header>
<main id="principal">{body}</main>
<footer><p>Archivo histórico de las elecciones generales del 23 de julio de 2023. No describe programas de 2026 ni recomienda el voto.</p>
<p>Resúmenes provisionales de medidas concretas; consulta el documento original. Una medida no seleccionada o ausente no implica oposición.</p></footer>
<script src="{root}pilot-2023.js" defer></script></body></html>'''


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


def comparison(data: dict) -> str:
    topics = ''.join(f'<option value="{esc(t["id"])}">{esc(t["name"])}</option>' for t in data["topics"])
    parties = ''.join(f'<option value="{esc(pid)}">{esc(name)}</option>' for pid, name in PARTIES.items())
    sections = ''.join(f'<section class="topic-section" data-topic="{esc(t["id"])}">'
                       f'<h2>{esc(t["name"])}</h2><div class="cards">'
                       + ''.join(card(p) for p in data["positions"] if p["topic"] == t["id"])
                       + '</div></section>' for t in data["topics"])
    body = f'''<div class="hero"><p class="eyebrow">23J 2023 · privado · provisional</p>
<h1>Compara cuatro programas de 2023</h1>
<p>PP, ERC, PNV y Sumar. Doce medidas concretas en vivienda, inmigración y economía, enlazadas a los programas originales.</p>
<p class="warning"><strong>Lectura provisional:</strong> resúmenes asistidos por extracción de PDF, sin revisión editorial humana. Las propuestas no son equivalentes entre sí; no inferimos acuerdos, desacuerdos ni resultados de gobierno.</p>
<a class="button" href="./cuestionario/">Explorar con el cuestionario</a></div>
<div class="controls"><label>Tema <select id="pilot-topic">{topics}</select></label>
<label>Primera candidatura <select id="pilot-a">{parties}</select></label>
<label>Segunda candidatura <select id="pilot-b">{parties}</select></label>
<p id="pilot-error" role="alert" hidden>Selecciona dos candidaturas distintas.</p></div>
<div id="pilot-comparison" class="cards" aria-live="polite"></div>
<details><summary>Ver las doce medidas y sus fuentes</summary>{sections}</details>'''
    return frame("Comparador de programas", body)


def quiz(data: dict) -> str:
    questions = ''.join(f'<fieldset data-topic="{esc(t["id"])}"><legend>{esc(t["name"])}: ¿qué medida te interesa explorar?</legend>'
                        + ''.join(f'<label class="quiz-option"><input type="radio" name="{esc(t["id"])}" value="{esc(p["party"])}">'
                                  f'<strong>{esc(PARTIES[p["party"]])}: {esc(p["title"])}</strong><span>{esc(p["summary"])}</span></label>'
                                  for p in data["positions"] if p["topic"] == t["id"])
                        + '</fieldset>' for t in data["topics"])
    body = f'''<div class="hero"><p class="eyebrow">Cuestionario exploratorio · 2023</p><h1>Explora las medidas que priorizarías</h1>
<p>Elige una medida de cada tema. Verás tus elecciones y sus fuentes. Esto <strong>no calcula afinidad partidista</strong>: los programas ofrecen medidas diferentes y seleccionar una no implica rechazar las demás.</p>
<p class="warning">Piloto histórico y provisional, sin revisión editorial humana. Tus respuestas permanecen en esta pestaña; no se envían ni se guardan.</p></div>
<form id="pilot-quiz">{questions}<button type="submit" class="button">Ver mis elecciones y fuentes</button></form>
<div id="pilot-results" tabindex="-1" aria-live="polite"></div>'''
    return frame("Cuestionario exploratorio", body, nested=True)


def write(root: Path, staging: Path) -> None:
    data = load(root)
    (staging / "index.html").write_text(comparison(data), encoding="utf-8")
    quiz_dir = staging / "cuestionario"
    quiz_dir.mkdir(exist_ok=True)
    (quiz_dir / "index.html").write_text(quiz(data), encoding="utf-8")
    (staging / "pilot-2023.css").write_bytes((root / "site/pilot-2023.css").read_bytes())
    (staging / "pilot-2023.js").write_bytes((root / "site/pilot-2023.js").read_bytes())
    (staging / "pilot-2023-data.json").write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
