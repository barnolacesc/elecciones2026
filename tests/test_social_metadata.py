"""E3.1a contracts for crawler-visible metadata and local preview assets."""

from html.parser import HTMLParser
from pathlib import Path
import struct
import tempfile
import unittest
from urllib.parse import urlsplit

from elecciones2026.generator import (
    BuildValidationError, build_site, load_and_validate_site_data, render_base,
)

ROOT = Path(__file__).resolve().parents[1]


class HeadMetadata(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.properties = {}
        self.canonicals = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and 'property' in attrs:
            key = attrs['property']
            if key in self.properties:
                raise AssertionError(f'Duplicate metadata: {key}')
            self.properties[key] = attrs['content']
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])


class TestSocialMetadata(unittest.TestCase):
    def test_every_page_has_matching_canonical_and_local_png_for_both_elections(self):
        for election in ('es-gen-2026', 'es-gen-2023'):
            with self.subTest(election=election), tempfile.TemporaryDirectory() as tmp:
                output = Path(tmp) / 'dist'
                result = build_site(root_dir=ROOT, output_dir=output, election_id=election,
                                    canonical_base='https://preview.example/')
                for page in result.files_written:
                    if not page.endswith('.html'):
                        continue
                    with self.subTest(page=page):
                        head = HeadMetadata((output / page).read_text())
                        props = head.properties
                        path = '/' + page.removesuffix('index.html')
                        self.assertEqual(head.canonicals, ['https://preview.example' + path])
                        self.assertEqual(props['og:url'], head.canonicals[0])
                        self.assertEqual(props['og:type'], 'website')
                        self.assertEqual(props['og:locale'], 'es_ES')
                        self.assertTrue(props['og:title'])
                        self.assertTrue(props['og:description'])
                        self.assertTrue(props['og:image:alt'])
                        self.assertEqual(props['og:image:type'], 'image/png')
                        image = urlsplit(props['og:image'])
                        self.assertEqual(image.netloc, 'preview.example')
                        self.assertFalse(image.query or image.fragment)
                        self.assertRegex(image.path, r'^/assets/social-preview-[0-9a-f]{16}\.png$')
                        png = (output / image.path.lstrip('/')).read_bytes()
                        self.assertEqual(png, (ROOT / 'site/assets/social-preview.png').read_bytes())
                        self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
                        self.assertEqual(struct.unpack('>II', png[16:24]),
                                         (int(props['og:image:width']), int(props['og:image:height'])))
                        self.assertEqual((props['og:image:width'], props['og:image:height']), ('1200', '630'))
                        if election == 'es-gen-2023':
                            self.assertIn('2023', props['og:title'])
                            self.assertIn('privado', props['og:description'])
                            self.assertNotIn('2026', props['og:site_name'])
                        else:
                            self.assertIn('Datos de prueba', props['og:description'])
                housing = HeadMetadata((output / 'temas/housing/index.html').read_text()).properties
                education = HeadMetadata((output / 'temas/education/index.html').read_text()).properties
                self.assertIn('Vivienda', housing['og:title'])
                self.assertIn('Educación', education['og:title'])
                self.assertNotEqual(housing['og:description'], education['og:description'])

    def test_metadata_escapes_hostile_text(self):
        ctx = load_and_validate_site_data(ROOT)
        text = '\"><script>alert(1)</script> & "quoted"'
        markup = render_base(ctx, text, text, '/temas/housing/', '<p>Context</p>')
        self.assertNotIn('<script>', markup)
        props = HeadMetadata(markup).properties
        self.assertEqual(props['og:title'], text)
        self.assertTrue(props['og:description'].endswith(text))

    def test_pilot_path_prefix_is_preserved_in_all_metadata_urls(self):
        ctx = load_and_validate_site_data(ROOT, election_id='es-gen-2023',
                                          canonical_base='https://preview.example/pilot-2023/')
        head = HeadMetadata(render_base(ctx, 'Vivienda', 'Consulta las fuentes.',
                                       '/temas/housing/', '<p>Context</p>'))
        self.assertEqual(head.properties['og:url'],
                         'https://preview.example/pilot-2023/temas/housing/')
        self.assertTrue(head.properties['og:image'].startswith(
            'https://preview.example/pilot-2023/assets/'))

    def test_canonical_base_rejects_private_state_and_relative_urls(self):
        for base in ('/relative', 'javascript:alert(1)', 'https://example.com/?answer=yes',
                     'https://example.com/#private', 'https://user:pass@example.com'):
            with self.subTest(base=base), self.assertRaises(BuildValidationError):
                load_and_validate_site_data(ROOT, canonical_base=base)

    def test_query_comparisons_have_generic_static_context(self):
        # A static server serves the same HTML for all query strings. Metadata
        # must not imply that a selected party pair has its own reviewed preview.
        ctx = load_and_validate_site_data(ROOT)
        from elecciones2026.generator import render_home_page, render_topic_detail
        home = HeadMetadata(render_home_page(ctx)).properties
        topic = HeadMetadata(render_topic_detail(ctx, ctx.taxonomy.topics[0])).properties
        self.assertEqual(home['og:url'], 'https://elecciones2026.es/')
        self.assertEqual(topic['og:url'], 'https://elecciones2026.es/temas/housing/')
        for props in (home, topic):
            for text in props.values():
                self.assertNotIn('partyA=', text)
                self.assertNotIn('partyB=', text)
                self.assertNotIn('Partido Ejemplo', text)
                self.assertNotIn('Limitar los precios', text)

    def test_missing_preview_image_fails_before_output_is_written(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'dist'
            with patch('elecciones2026.generator.preview_image_path', side_effect=FileNotFoundError):
                with self.assertRaises(FileNotFoundError):
                    build_site(root_dir=ROOT, output_dir=output)
            self.assertFalse(output.exists())
