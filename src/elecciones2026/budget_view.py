"""Spanish static budget views and bounded topic projections (E10.3)."""
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from html import escape
from pathlib import Path
import shutil

from elecciones2026.budget import ROOT, BudgetError, canonical, display_amount, load_bundle, share

MAX_PROJECTION_BYTES = 16 * 1024


def percentage(value, denominator):
    result = share(value, denominator)
    if result is None:
        return 'No disponible'
    if Decimal(value) > 0 and Decimal(result) == 0:
        return '< 0,01 %'
    return result.replace('.', ',') + ' %'


def table_url(payload):
    matches = [source['url'] for source in payload['source.json']['companion_sources']
               if source['id'] == 'pge-2023-matrix-html']
    if len(matches) != 1:
        raise BudgetError('A pinned official HTML companion is required for the view')
    return matches[0]


def locator_note(locator):
    return f"CSV: fila {locator['csv_line']}, columna {locator['column']}"


def source_link(payload, locator):
    return (f'<a href="{escape(table_url(payload), quote=True)}">Tabla oficial</a>'
            f' <span class="budget-locator">{escape(locator_note(locator))}</span>')


def figure(value, denominator):
    return f'{escape(display_amount(value) or "No disponible")} millones de euros · {escape(percentage(value, denominator))}'


def measurement_notes(payload, manifest):
    contract = payload['measurement.json']
    denominator = contract['denominator_amount_thousand_eur']
    notes = [contract[key] for key in ('historical_note_es', 'scope_note_es', 'scope_limit_es', 'rounding_note_es')]
    notes += ['Créditos aprobados consolidados, capítulos 1–8. No son datos de ejecución.',
              'Estas cifras no indican el coste de las propuestas de los partidos.',
              'Los temas pueden compartir políticas. Sus importes no forman un reparto aditivo del presupuesto.']
    reviewed = sorted(review['reviewed_at'] for review in payload['reviews.json'] if review['decision'] == 'approved')
    review_note = f'Última revisión: {reviewed[-1][:10]}.' if reviewed else 'Revisión financiera, de derechos y editorial pendiente.'
    return '<div class="budget-notes">' + ''.join(f'<p>{escape(note)}</p>' for note in notes) + (
        f'<p><strong>Denominador de todos los porcentajes:</strong> {escape(display_amount(denominator))} millones de euros '
        f'({escape(denominator.replace(".", ","))} miles de euros sin redondear). '
        f'{source_link(payload, contract["denominator_locator"])}</p>'
        f'<p>Versión de datos: {escape(manifest["dataset_version"])}. '
        f'Actualización: <time datetime="{escape(manifest["build_date"])}">{escape(manifest["build_date"])}</time>. '
        f'{escape(review_note)}</p></div>')


def topic_projection(payload, manifest, topic_id):
    contract = payload['measurement.json']
    mapping = next(item for item in payload['mapping.json']['mappings'] if item['topic_id'] == topic_id)
    policies = {item['code']: item for item in payload['values.json']['margins'] if item['kind'] == 'policy'}
    denominator = contract['denominator_amount_thousand_eur']
    refs = mapping['row_refs'] if mapping['coverage_state'] not in {'not_available', 'not_comparable'} else []
    rows = []
    for ref in refs:
        row = policies[ref['policy_code']]
        rows.append({'code': row['code'], 'label': row['label_es'],
                     'amount': display_amount(row['amount_thousand_eur']),
                     'share': percentage(row['amount_thousand_eur'], denominator),
                     'locator': locator_note(row['source_locator'])})
    result = {'topic_id': topic_id, 'title': 'Contexto presupuestario oficial · PGE 2023',
              'topic_label': mapping['label_es'], 'source_url': table_url(payload),
              'version': manifest['dataset_version'], 'rows': rows,
              'notes': [contract['historical_note_es'], contract['scope_note_es'], contract['scope_limit_es'],
                        mapping['coverage_note_es'], 'Estas cifras no indican el coste de las propuestas de los partidos.',
                        'Las políticas citadas pueden aparecer en otros temas. No se suman como partidas independientes.',
                        f'Denominador: {display_amount(denominator)} millones de euros ({denominator.replace(".", ",")} miles de euros sin redondear).',
                        contract['rounding_note_es']],
              'gap': 'No hay una cifra oficial separable para este tema con el ámbito y la fuente disponibles.'}
    if len(canonical(result)) > MAX_PROJECTION_BYTES:
        raise BudgetError('Topic projection exceeds 16 KiB')
    return result


def render_context(projection, budget_url):
    rows = ''.join(f'<li><strong>{escape(row["label"])}</strong><p>{escape(row["amount"])} millones de euros · '
                   f'{escape(row["share"])}</p><a href="{escape(projection["source_url"], quote=True)}">Tabla oficial</a> '
                   f'<span class="budget-locator">{escape(row["locator"])}</span></li>' for row in projection['rows'])
    body = f'<ul class="budget-context-rows">{rows}</ul>' if rows else f'<p>{escape(projection["gap"])}</p>'
    return (f'<h2>{escape(projection["title"])}</h2><p>{escape(projection["topic_label"])}</p>{body}'
            + ''.join(f'<p>{escape(note)}</p>' for note in projection['notes'])
            + f'<p>Versión de datos: {escape(projection["version"])}. <a href="{escape(budget_url, quote=True)}">Ver el presupuesto completo de 2023</a></p>')


def render_budget_content(payload, manifest, bundle_id, topic_labels, root_path='../../', preview=False):
    denominator = payload['measurement.json']['denominator_amount_thousand_eur']
    policies = sorted((row for row in payload['values.json']['margins'] if row['kind'] == 'policy'),
                      key=lambda row: (-Decimal(row['amount_thousand_eur']), row['code']))
    sections = {row['code']: row for row in payload['sections.json']['sections']}
    ranked, table_rows = [], []
    for row in policies:
        code, amount = row['code'], row['amount_thousand_eur']
        section_items = []
        for cell in sorted((cell for cell in payload['values.json']['cells'] if cell['policy_code'] == code),
                           key=lambda cell: cell['section_code']):
            section = sections[cell['section_code']]
            value = cell['amount_thousand_eur']
            number = figure(value, denominator) if value is not None else 'No disponible en la celda de origen; no se interpreta como cero.'
            section_items.append(f'<li><strong>{escape(section["code"])} · {escape(section["name_es"])}</strong>'
                                 f'<p>{number}</p>{source_link(payload, cell["source_locator"])}</li>')
        ranked.append(f'<li id="politica-{escape(code)}" class="budget-policy"><h3>{escape(row["label_es"])}</h3>'
                      f'<p class="budget-figure">{figure(amount, denominator)}</p>'
                      f'<meter min="0" max="100" value="{share(amount, denominator)}" aria-hidden="true"></meter>'
                      f'<p>{source_link(payload, row["source_locator"])}</p>'
                      f'<details><summary>Secciones administrativas · {len(section_items)}</summary>'
                      f'<p>Porcentajes del mismo total consolidado; no son porcentajes dentro de esta política. '
                      f'No todas las secciones son ministerios.</p><ul class="budget-section-rows">{"".join(section_items)}</ul></details></li>')
        table_rows.append(f'<tr role="row"><th scope="row" role="rowheader">{escape(row["label_es"])}</th>'
                          f'<td role="cell" data-label="Millones de euros">{escape(display_amount(amount))}</td>'
                          f'<td role="cell" data-label="% del total">{escape(percentage(amount, denominator))}</td>'
                          f'<td role="cell" data-label="Fuente">{source_link(payload, row["source_locator"])}</td></tr>')
    section_rows = []
    for margin in sorted((item for item in payload['values.json']['margins'] if item['kind'] == 'section'), key=lambda row: row['code']):
        section_rows.append(f'<tr role="row"><th scope="row" role="rowheader">{escape(margin["code"])} · {escape(sections[margin["code"]]["name_es"])}</th>'
                            f'<td role="cell" data-label="Millones de euros">{escape(display_amount(margin["amount_thousand_eur"]))}</td>'
                            f'<td role="cell" data-label="% del total">{escape(percentage(margin["amount_thousand_eur"], denominator))}</td>'
                            f'<td role="cell" data-label="Fuente">{source_link(payload, margin["source_locator"])}</td></tr>')
    def table(caption, rows):
        return f'<table class="budget-table" role="table"><caption>{caption}</caption><thead role="rowgroup"><tr role="row"><th scope="col" role="columnheader">Clasificación</th><th scope="col" role="columnheader">Millones de euros</th><th scope="col" role="columnheader">% del total consolidado</th><th scope="col" role="columnheader">Fuente y localización</th></tr></thead><tbody role="rowgroup">{"".join(rows)}</tbody></table>'
    context = []
    for topic_id, label in topic_labels.items():
        projection = topic_projection(payload, manifest, topic_id)
        topic_link = '' if preview else f'<p><a href="{root_path}temas/{escape(topic_id)}/">Comparar propuestas sobre este tema</a></p>'
        context.append(f'<details id="tema-{escape(topic_id)}"><summary>{escape(label)}</summary>'
                       f'{render_context(projection, "./")}{topic_link}</details>')
    notice = '<aside class="notice" role="status"><strong>BORRADOR PRIVADO · No publicar.</strong> Revisión financiera, de derechos y editorial pendiente.</aside>' if preview else ''
    return (f'<section class="budget-page" aria-labelledby="budget-title">{notice}'
            '<p class="hero-eyebrow">CONTEXTO HISTÓRICO · PRESUPUESTOS GENERALES DEL ESTADO</p>'
            '<h1 id="budget-title">PGE 2023: presupuesto aprobado</h1>'
            f'<p class="budget-total">{escape(display_amount(denominator))} <span>millones de euros · total consolidado</span></p>'
            f'{measurement_notes(payload, manifest)}'
            '<h2>Políticas de gasto, de mayor a menor importe</h2>'
            f'<ol class="budget-ranked">{"".join(ranked)}</ol>'
            '<details><summary>Consultar tabla de políticas</summary>'
            f'{table("Políticas de gasto · PGE 2023, capítulos 1–8", table_rows)}</details>'
            '<details><summary>Consultar totales por sección administrativa</summary>'
            f'{table("Secciones administrativas · PGE 2023, capítulos 1–8", section_rows)}</details>'
            f'<h2>Contexto por tema</h2><div class="budget-topics">{"".join(context)}</div>'
            f'<p class="budget-locator">Identificador del conjunto: {escape(bundle_id)}.</p></section>')


def preview_bundle(bundle, output):
    """Render draft data only to a private directory outside the repository."""
    output = Path(output).resolve()
    if output.is_relative_to(ROOT.resolve()) or output.exists():
        raise BudgetError('Preview needs a new private directory outside the repository')
    manifest, payload = load_bundle(bundle, require_publication=False)
    taxonomy = json.loads((ROOT / 'content/taxonomy.json').read_text())
    labels = {topic['id']: topic['name_es'] for topic in taxonomy['topics']}
    content = render_budget_content(payload, manifest, Path(bundle).name, labels, preview=True)
    output.mkdir(parents=True, mode=0o700)
    target = output / 'presupuestos/2023'
    target.mkdir(parents=True)
    html = ('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow"><title>Borrador privado · PGE 2023</title>'
            '<link rel="stylesheet" href="../../styles.css"><link rel="stylesheet" href="../../budget.css"></head><body><a class="skip-link" href="#contenido">Saltar al contenido principal</a>'
            f'<main id="contenido">{content}</main></body></html>')
    (target / 'index.html').write_text(html)
    shutil.copy2(ROOT / 'site/styles.css', output / 'styles.css')
    shutil.copy2(ROOT / 'site/budget.css', output / 'budget.css')
    shutil.copytree(ROOT / 'site/tokens', output / 'tokens')
    for file in output.rglob('*'):
        file.chmod(0o700 if file.is_dir() else 0o600)
    return target / 'index.html'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--private-preview', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(preview_bundle(args.bundle, args.private_preview))
        return 0
    except (BudgetError, ValueError, KeyError, OSError) as error:
        parser.exit(1, f'Budget preview failed: {error}\n')


if __name__ == '__main__':
    raise SystemExit(main())
