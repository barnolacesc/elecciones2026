"""Deterministic overview and share image from official policy margins (E10.3)."""
from decimal import Decimal, localcontext
from html import escape
from textwrap import wrap

from elecciones2026.budget import BudgetError, display_amount, share

# Stable policy colours identify allocations, never parties or value judgements.
POLICY_CODES = ('11', '12', '13', '14', '21', '22', '23', '24', '25', '26', '28', '29',
                '31', '32', '33', '41', '42', '43', '44', '45', '46', '49', '91', '92', '93', '94', '95')
POLICY_PALETTE = ('#36576d', '#35655d', '#685471', '#79613c', '#65516a', '#48633f',
                  '#406778', '#735343', '#385c56', '#565a78', '#70595e', '#52663d',
                  '#30685f', '#485c85', '#79544d', '#63673c', '#3d6670', '#6e516e',
                  '#685d3e', '#3f607b', '#596b48', '#795943', '#575875', '#42706b',
                  '#725c76', '#756338', '#4d6272')
POLICY_COLORS = dict(zip(POLICY_CODES, POLICY_PALETTE))
COMPARISON_SCOPE = ('Sanidad y educación: solo las asignaciones recogidas en estos PGE 2023. '
                    'No representan todo el gasto público sanitario y educativo; '
                    'no incluyen todo el gasto autonómico y local.')


def policy_color(code):
    return POLICY_COLORS.get(code, '#24495d')


def policies(payload):
    return sorted((row for row in payload['values.json']['margins'] if row['kind'] == 'policy'),
                  key=lambda row: (-Decimal(row['amount_thousand_eur']), row['code']))


def layout(rows, width, height):
    """Squarified rectangle areas use unrounded margins, never topic mappings."""
    positive = [row for row in rows if Decimal(row['amount_thousand_eur']) > 0]
    total = sum((Decimal(row['amount_thousand_eur']) for row in positive), Decimal(0))
    if not total:
        return []
    remaining = [(row, float(Decimal(row['amount_thousand_eur']) / total) * width * height) for row in positive]
    rectangles, x, y = [], 0.0, 0.0

    def worst(group, side):
        areas = [area for _, area in group]
        summed = sum(areas)
        return max(side * side * max(areas) / summed**2, summed**2 / (side * side * min(areas)))

    while remaining:
        group = [remaining.pop(0)]
        side = min(width, height)
        while remaining and worst(group + [remaining[0]], side) <= worst(group, side):
            group.append(remaining.pop(0))
        area = sum(item[1] for item in group)
        if width >= height:
            strip = min(width, area / height)
            offset = y
            for row, item_area in group:
                length = item_area / strip
                rectangles.append((row, x, offset, strip, length))
                offset += length
            x += strip
            width = max(0, width - strip)
        else:
            strip = min(height, area / width)
            offset = x
            for row, item_area in group:
                length = item_area / strip
                rectangles.append((row, offset, y, length, strip))
                offset += length
            y += strip
            height = max(0, height - strip)
    return rectangles


def percentage(value, denominator):
    result = share(value, denominator)
    if Decimal(value) > 0 and Decimal(result) == 0:
        return '< 0,01 %'
    return result.replace('.', ',') + ' %'


def amount_label(value):
    return display_amount(value) + ' M€'


def pension_comparison(rows):
    """Explicit sum of two disjoint official margins, relative to pensions."""
    by_code = {row['code']: row for row in rows}
    if not all(code in by_code for code in ('21', '31', '32')):
        return None
    reference = Decimal(by_code['21']['amount_thousand_eur'])
    if reference <= 0:
        return None
    health = Decimal(by_code['31']['amount_thousand_eur'])
    education = Decimal(by_code['32']['amount_thousand_eur'])
    with localcontext() as context:
        context.prec = 50
        combined = health + education
    scale = max(reference, combined)
    entries = [('Pensiones', str(reference), [('21', reference)]),
               ('Sanidad', str(health), [('31', health)]),
               ('Educación', str(education), [('32', education)]),
               ('Sanidad + educación', str(combined), [('31', health), ('32', education)])]
    return {'reference': str(reference), 'combined': str(combined), 'scale': scale,
            'ratio': percentage(str(combined), str(reference)), 'entries': entries,
            'locators': [by_code[code]['source_locator'] for code in ('21', '31', '32')]}


def comparison_html(rows, payload):
    comparison = pension_comparison(rows)
    if comparison is None:
        return ''
    bars = []
    for label, amount, segments in comparison['entries']:
        fill = ''.join(f'<span style="width:{float(value / comparison["scale"] * 100):.8f}%;background:{policy_color(code)}"></span>'
                       for code, value in segments)
        bars.append(f'<li><div class="budget-comparison-label"><span>{label}</span>'
                    f'<span><strong>{escape(percentage(amount, comparison["reference"]))}</strong>'
                    f' · {escape(amount_label(amount))}</span></div>'
                    f'<div class="budget-comparison-track" aria-hidden="true">{fill}</div></li>')
    source = next(item['url'] for item in payload['source.json']['companion_sources'] if item['id'] == 'pge-2023-matrix-html')
    lines = ', '.join(f'fila {locator["csv_line"]}, columna {locator["column"]}' for locator in comparison['locators'])
    return ('<section class="budget-comparison" aria-labelledby="budget-comparison-title">'
            '<h3 id="budget-comparison-title">Para comparar magnitudes</h3>'
            f'<p>Sanidad + educación equivalen al <strong>{escape(comparison["ratio"])}</strong>'
            ' de la asignación de pensiones en estos PGE.</p>'
            '<p class="budget-comparison-scale">Barras a la misma escala. Porcentajes respecto a pensiones, no al presupuesto total.</p>'
            f'<ul class="budget-comparison-bars">{"".join(bars)}</ul>'
            f'<p class="budget-comparison-scope">{COMPARISON_SCOPE}</p>'
            f'<p class="budget-locator"><a href="{escape(source, quote=True)}">Fuente oficial: pensiones, sanidad y educación</a>'
            f' · CSV: {escape(lines)}. Suma de las dos partidas, sin estimaciones.</p></section>')


def comparison_svg(rows, y):
    comparison = pension_comparison(rows)
    if comparison is None:
        return '', y
    content = [f'<text x="40" y="{y}" font-size="30" font-weight="700" fill="#14253a">Para comparar magnitudes</text>']
    y += 36
    summary = f'Sanidad + educación equivalen al {comparison["ratio"]} de la asignación de pensiones en estos PGE.'
    for line in wrap(summary, width=85):
        content.append(f'<text x="40" y="{y}" font-size="20" fill="#14253a">{escape(line)}</text>')
        y += 26
    content.append(f'<text x="40" y="{y}" font-size="17" fill="#526675">Misma escala. Porcentajes respecto a pensiones, no al presupuesto total.</text>')
    y += 38
    for label, amount, segments in comparison['entries']:
        figures = f'{percentage(amount, comparison["reference"])} · {amount_label(amount)}'
        content.append(f'<text x="40" y="{y}" font-size="20" fill="#14253a">{label}</text>'
                       f'<text x="1040" y="{y}" text-anchor="end" font-size="18" fill="#14253a">{escape(figures)}</text>'
                       f'<rect x="40" y="{y+12}" width="1000" height="18" fill="#e5e9ec"/>')
        x = 40.0
        for code, value in segments:
            width = float(value / comparison['scale'] * 1000)
            content.append(f'<rect x="{x:.8f}" y="{y+12}" width="{width:.8f}" height="18" fill="{policy_color(code)}"/>')
            x += width
        y += 64
    for line in wrap(COMPARISON_SCOPE, width=103):
        content.append(f'<text x="40" y="{y}" font-size="17" fill="#526675">{escape(line)}</text>')
        y += 24
    locators = ', '.join(f'fila {item["csv_line"]}, columna {item["column"]}' for item in comparison['locators'])
    for line in wrap('Fuente: políticas de pensiones, sanidad y educación. CSV: ' + locators + '.', width=125):
        content.append(f'<text x="40" y="{y}" font-size="13" fill="#526675">{escape(line)}</text>')
        y += 20
    return ''.join(content), y + 45


def fit_tile_label(label, proportion, amount, width, height, ceiling, minimum):
    """Prefer complete information; shrink within bounds before removing lines."""
    sizes = [ceiling]
    while sizes[-1] - .5 > minimum:
        sizes.append(sizes[-1] - .5)
    if sizes[-1] > minimum:
        sizes.append(minimum)
    padding = min(6, min(width, height) * .08)
    for mode in ('complete', 'name-share', 'figures', 'share'):
        for size in sizes:
            capacity = max(0, int((width - 2 * padding) / (size * .65)))
            count = max(0, int((height - 2 * padding) / (size * 1.3)))
            if not capacity or not count:
                continue
            name = wrap(label, width=capacity, break_long_words=False, break_on_hyphens=False)
            money = [amount] if len(amount) <= capacity else amount.rsplit(' ', 1)
            lines = {'complete': name + [proportion] + money,
                     'name-share': name + [proportion],
                     'figures': [proportion] + money,
                     'share': [proportion]}[mode]
            if len(lines) <= count and all(len(line) <= capacity for line in lines):
                return lines, size
    return [], minimum


def draw_tiles(rows, denominator, width, height, font_size=13):
    result = []
    rectangles = layout(rows, width, height)
    largest_area = max((w * h for _, _, _, w, h in rectangles), default=1)
    minimum = max(8, font_size * .55)
    for row, x, y, w, h in rectangles:
        proportion = percentage(row['amount_thousand_eur'], denominator)
        amount = amount_label(row['amount_thousand_eur'])
        title = f"{row['label_es'].capitalize()}: {proportion} del total · {amount}"
        result.append(f'<g><title>{escape(title)}</title><rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{policy_color(row["code"])}" stroke="#fff" stroke-width="2"/>')
        ceiling = max(minimum, font_size * (w * h / largest_area) ** .2)
        lines, size = fit_tile_label(row['label_es'].capitalize(), proportion, amount, w, h, ceiling, minimum)
        for index, line in enumerate(lines):
            result.append(f'<text x="{x + w/2:.3f}" y="{y + h/2 + (index - (len(lines)-1)/2)*size*1.3:.3f}" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-size="{size:.3f}" font-weight="600">{escape(line)}</text>')
        result.append('</g>')
    return ''.join(result)


def overview(payload, chart_url, preview=False):
    rows = policies(payload)
    denominator = payload['measurement.json']['denominator_amount_thousand_eur']
    plot = draw_tiles(rows, denominator, 360, 280)
    def row_html(row):
        value = percentage(row['amount_thousand_eur'], denominator)
        return (f'<li><span class="budget-chart-name"><span class="budget-chart-swatch" style="background:{policy_color(row["code"])}" aria-hidden="true"></span>{escape(row["label_es"].capitalize())}</span>'
                f'<span class="budget-chart-values"><strong>{escape(value)}</strong>'
                f'<span>{escape(amount_label(row["amount_thousand_eur"]))}</span></span></li>')
    key = ''.join(row_html(row) for row in rows)
    return ('<section class="budget-overview" aria-labelledby="budget-overview-title">'
            '<h2 id="budget-overview-title">¿Cómo se reparte el presupuesto?</h2>'
            '<p class="budget-chart-lede">La superficie de cada partida representa su porcentaje del total.</p>'
            '<p class="budget-chart-units">Porcentaje del total e importe real. M€ = millones de euros.</p>'
            '<div class="budget-overview-body"><figure class="budget-map"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 280" role="img" aria-labelledby="budget-map-title budget-map-desc" style="font-family:Arial,sans-serif">'
            f'<title id="budget-map-title">Reparto proporcional del presupuesto aprobado de 2023</title>'
            f'<desc id="budget-map-desc">{len(rows)} políticas oficiales. El área de cada rectángulo es proporcional a su porcentaje del total, calculado sin redondear. Todos los nombres, porcentajes e importes están en la lista siguiente.</desc>{plot}</svg>'
            '<figcaption>El área está a escala: una partida del 40 % ocupa el 40 % del gráfico. Las partidas pequeñas se pueden consultar debajo.</figcaption></figure>'
            '</div>'
            '<p class="budget-chart-scope">PGE 2023 · Capítulos 1–8 · Estado y Seguridad Social. Presupuesto aprobado, no gasto ejecutado. '
            'No incluye todo el gasto autonómico y local. Importes y porcentajes redondeados a dos decimales; no son costes de propuestas.</p>'
            f'<div class="budget-chart-actions" data-chart-url="{escape(chart_url, quote=True)}">'
            '<button type="button" class="btn-primary" id="budget-chart-share" hidden>Compartir gráfico</button>'
            '<button type="button" class="btn-share" id="budget-chart-save" hidden>Guardar imagen (PNG)</button>'
            f'<a class="budget-chart-svg" href="{escape(chart_url, quote=True)}" download="pge-2023.svg">Descargar gráfico (SVG)</a></div>'
            '<p id="budget-chart-feedback" role="status" aria-live="polite"></p>'
            f'{comparison_html(rows, payload)}'
            f'<div class="budget-legend"><ol class="budget-chart-key">{key}</ol></div></section>')


def share_svg(payload, manifest, bundle_id, preview=False):
    """Standalone source-bearing image; private exports keep their draft notice."""
    rows = policies(payload)
    denominator = payload['measurement.json']['denominator_amount_thousand_eur']
    title = '¿Cómo se reparte el presupuesto?'
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="2000" viewBox="0 0 1080 2000" role="img" aria-labelledby="title desc" style="font-family:Arial,sans-serif">'
               f'<title id="title">{title} · PGE 2023</title><desc id="desc">Reparto de las {len(rows)} políticas oficiales del presupuesto aprobado consolidado, capítulos 1–8. No son datos de ejecución.</desc>'
               '<rect width="1080" height="2000" fill="#f8f9f7"/>'
               f'<text x="40" y="62" font-size="24" fill="#526675">{"BORRADOR PRIVADO · PGE 2023 · NO PUBLICAR" if preview else "PRESUPUESTOS GENERALES DEL ESTADO · 2023"}</text>'
               f'<text x="40" y="125" font-size="48" font-weight="700" fill="#14253a">{title}</text>'
               f'<text x="40" y="169" font-size="22" fill="#526675">Total: {escape(display_amount(denominator))} millones de euros · M€ = millones de euros</text>'
               '<text x="40" y="204" font-size="22" fill="#526675">Área a escala: 40 % del presupuesto = 40 % del gráfico.</text>'
               f'<g transform="translate(40,235)">{draw_tiles(rows, denominator, 1000, 620, 22)}</g>']
    y = 912
    comparison, y = comparison_svg(rows, y)
    content.append(comparison)
    split = (len(rows) + 1) // 2
    left, right = rows[:split], rows[split:]
    for index in range(split):
        max_lines = 1
        for column, group in enumerate((left, right)):
            if index >= len(group):
                continue
            row = group[index]
            x = 40 + column * 510
            lines = wrap(row['label_es'].capitalize(), width=30, break_long_words=True, break_on_hyphens=False)
            max_lines = max(max_lines, len(lines))
            content.append(f'<rect x="{x}" y="{y-13}" width="14" height="14" fill="{policy_color(row["code"])}"/>')
            for offset, line in enumerate(lines):
                content.append(f'<text x="{x+22}" y="{y+offset*22}" font-size="18" fill="#14253a">{escape(line)}</text>')
            value = percentage(row['amount_thousand_eur'], denominator)
            content.append(f'<text x="{x+480}" y="{y}" text-anchor="end" font-size="18" font-weight="700" fill="#14253a">{escape(value)}</text>')
            amount = amount_label(row['amount_thousand_eur'])
            content.append(f'<text x="{x+480}" y="{y+24}" text-anchor="end" font-size="16" fill="#526675">{escape(amount)}</text>')
        y += max(64, max_lines * 22 + 18)
    y += 35
    source = next(item['url'] for item in payload['source.json']['companion_sources'] if item['id'] == 'pge-2023-matrix-html')
    reviewed = sorted(review['reviewed_at'] for review in payload['reviews.json'] if review['decision'] == 'approved')
    notes = ['Presupuesto aprobado, no gasto ejecutado. Datos históricos de 2023.',
             'Estado y Seguridad Social · Consolidado, capítulos 1–8. No es todo el gasto público en España.',
             f'Total: {display_amount(denominator)} millones de euros ({denominator.replace(".", ",")} miles sin redondear).',
             'Importes y porcentajes redondeados a dos decimales. No son costes de propuestas políticas.',
             f'Fuente: SEPG · Tabla {payload["source.json"]["table_id"]} · Versión {manifest["dataset_version"]}',
             f'Actualización: {manifest["build_date"]} · Revisión: {reviewed[-1][:10] if reviewed else "pendiente"}',
             source, f'Conjunto: {bundle_id}']
    if preview:
        notes.insert(0, 'BORRADOR PRIVADO · Revisión financiera, de derechos y editorial pendiente · No publicar')
    for note in notes:
        content.append(f'<text x="40" y="{y}" font-size="13" fill="#526675">{escape(note)}</text>')
        y += 24
    if y > 1980:
        # Keep all policy labels and provenance visible in longer fixture/source labels.
        new_height = y + 30
        content[0] = content[0].replace('height="2000"', f'height="{new_height}"').replace('1080 2000', f'1080 {new_height}')
    content.append('</svg>')
    result = ''.join(content)
    if y + 30 > 8192 or len(result.encode('utf-8')) > 131072:
        raise BudgetError('Share image exceeds its byte or dimension limit')
    return result
