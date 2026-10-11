"""Deterministic overview and share image from official policy margins (E10.3)."""
from decimal import Decimal
from html import escape
from textwrap import wrap

from elecciones2026.budget import BudgetError, display_amount, share


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


def proportional_amount(value, denominator):
    result = share(value, denominator)
    if Decimal(value) > 0 and Decimal(result) == 0:
        return '< 0,01'
    return result.replace('.', ',')


def draw_tiles(rows, denominator, width, height, font_size=11):
    result = []
    for row, x, y, w, h in layout(rows, width, height):
        title = f"{row['code']} · {row['label_es']}: {proportional_amount(row['amount_thousand_eur'], denominator)} € de cada 100 €"
        result.append(f'<g><title>{escape(title)}</title><rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="#24495d" stroke="#fff" stroke-width="2"/>')
        if w >= font_size * 2.5 and h >= font_size * 1.8:
            lines = [row['code']]
            if w >= font_size * 5 and h >= font_size * 3.5:
                label = row['label_es'].capitalize()
                capacity = max(1, int((w-16) / (font_size * .65)))
                wrapped = wrap(label, width=capacity, break_long_words=False, break_on_hyphens=False)
                count = max(1, int((h-16) / (font_size * 1.3)) - 1)
                if len(wrapped) <= count and all(len(line) <= capacity for line in wrapped):
                    lines = wrapped
                lines.append(proportional_amount(row['amount_thousand_eur'], denominator) + ' €')
            for index, line in enumerate(lines):
                result.append(f'<text x="{x + w/2:.3f}" y="{y + h/2 + (index - (len(lines)-1)/2)*font_size*1.3:.3f}" text-anchor="middle" dominant-baseline="middle" fill="#fff" font-size="{font_size}" font-weight="600">{escape(line)}</text>')
        result.append('</g>')
    return ''.join(result)


def overview(payload, chart_url, preview=False):
    rows = policies(payload)
    denominator = payload['measurement.json']['denominator_amount_thousand_eur']
    plot = draw_tiles(rows, denominator, 360, 280)
    def row_html(row):
        value = proportional_amount(row['amount_thousand_eur'], denominator)
        return (f'<li><span class="budget-chart-code">{escape(row["code"])}</span>'
                f'<span>{escape(row["label_es"].capitalize())}</span><strong>{escape(value)} €</strong></li>')
    first = ''.join(row_html(row) for row in rows[:6])
    rest = ''.join(row_html(row) for row in rows[6:])
    extra = f'<details class="budget-chart-more"><summary>Ver las {len(rows)} políticas</summary><ol class="budget-chart-key" start="7">{rest}</ol></details>' if len(rows) > 6 else ''
    return ('<section class="budget-overview" aria-labelledby="budget-overview-title">'
            '<h2 id="budget-overview-title">¿Cómo se reparte el presupuesto?</h2>'
            '<p class="budget-chart-lede">De cada <strong>100 € aprobados</strong>, esta es la parte de cada política.</p>'
            '<div class="budget-overview-body"><figure class="budget-map"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 280" role="img" aria-labelledby="budget-map-title budget-map-desc" style="font-family:Arial,sans-serif">'
            f'<title id="budget-map-title">Reparto proporcional del presupuesto aprobado de 2023</title>'
            f'<desc id="budget-map-desc">{len(rows)} políticas oficiales. El área de cada rectángulo representa su importe sin redondear. Los códigos corresponden a la lista siguiente.</desc>{plot}</svg>'
            '<figcaption>Más superficie = más presupuesto. Los códigos identifican las políticas de la lista.</figcaption></figure>'
            f'<div class="budget-legend"><ol class="budget-chart-key">{first}</ol>{extra}</div></div>'
            '<p class="budget-chart-scope">PGE 2023 · Capítulos 1–8 · Estado y Seguridad Social. Presupuesto aprobado, no gasto ejecutado. '
            'No incluye todo el gasto autonómico y local. Importes proporcionales redondeados; no son costes de propuestas.</p>'
            f'<div class="budget-chart-actions" data-chart-url="{escape(chart_url, quote=True)}">'
            '<button type="button" class="btn-primary" id="budget-chart-share" hidden>Compartir gráfico</button>'
            '<button type="button" class="btn-share" id="budget-chart-save" hidden>Guardar imagen (PNG)</button>'
            f'<a class="budget-chart-svg" href="{escape(chart_url, quote=True)}" download="pge-2023.svg">Descargar gráfico (SVG)</a></div>'
            '<p id="budget-chart-feedback" role="status" aria-live="polite"></p></section>')


def share_svg(payload, manifest, bundle_id, preview=False):
    """Standalone source-bearing image; private exports keep their draft notice."""
    rows = policies(payload)
    denominator = payload['measurement.json']['denominator_amount_thousand_eur']
    title = 'De cada 100 € aprobados'
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="2000" viewBox="0 0 1080 2000" role="img" aria-labelledby="title desc" style="font-family:Arial,sans-serif">'
               f'<title id="title">{title} · PGE 2023</title><desc id="desc">Reparto de las {len(rows)} políticas oficiales del presupuesto aprobado consolidado, capítulos 1–8. No son datos de ejecución.</desc>'
               '<rect width="1080" height="2000" fill="#f8f9f7"/>'
               f'<text x="40" y="62" font-size="24" fill="#526675">{"BORRADOR PRIVADO · PGE 2023 · NO PUBLICAR" if preview else "PRESUPUESTOS GENERALES DEL ESTADO · 2023"}</text>'
               f'<text x="40" y="125" font-size="48" font-weight="700" fill="#14253a">{title}</text>'
               '<text x="40" y="169" font-size="22" fill="#526675">El tamaño de cada área muestra su parte del presupuesto.</text>'
               f'<g transform="translate(40,200)">{draw_tiles(rows, denominator, 1000, 430, 24)}</g>']
    y = 688
    split = (len(rows) + 1) // 2
    left, right = rows[:split], rows[split:]
    for index in range(split):
        max_lines = 1
        for column, group in enumerate((left, right)):
            if index >= len(group):
                continue
            row = group[index]
            x = 40 + column * 510
            lines = wrap(row['label_es'].capitalize(), width=34, break_long_words=True, break_on_hyphens=False)
            max_lines = max(max_lines, len(lines))
            content.append(f'<text x="{x}" y="{y}" font-size="17" fill="#526675">{escape(row["code"])}</text>')
            for offset, line in enumerate(lines):
                content.append(f'<text x="{x+35}" y="{y+offset*22}" font-size="18" fill="#14253a">{escape(line)}</text>')
            value = proportional_amount(row['amount_thousand_eur'], denominator)
            content.append(f'<text x="{x+480}" y="{y}" text-anchor="end" font-size="18" font-weight="700" fill="#14253a">{escape(value)} €</text>')
        y += max(52, max_lines * 22 + 18)
    y = max(y + 25, 1700)
    source = next(item['url'] for item in payload['source.json']['companion_sources'] if item['id'] == 'pge-2023-matrix-html')
    reviewed = sorted(review['reviewed_at'] for review in payload['reviews.json'] if review['decision'] == 'approved')
    notes = ['Presupuesto aprobado, no gasto ejecutado. Datos históricos de 2023.',
             'Estado y Seguridad Social · Consolidado, capítulos 1–8. No es todo el gasto público en España.',
             f'Total: {display_amount(denominator)} millones de euros ({denominator.replace(".", ",")} miles sin redondear).',
             'Cada importe es una proporción redondeada de 100 €. No indica el coste de propuestas políticas.',
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
