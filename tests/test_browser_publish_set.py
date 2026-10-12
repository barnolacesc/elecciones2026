"""E1.4 browser/static parity and failure-safe publication using fictional records."""
import json
from dataclasses import replace
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from elecciones2026.generator import (
    BuildValidationError, build_comparison_payload, build_site,
    comparison_bundle_name, comparison_bundle_script, load_and_validate_site_data,
    publish_directory, render_comparison_measures,
)

ROOT = Path(__file__).resolve().parents[1]


class BrowserPublishSetTests(unittest.TestCase):
    def setUp(self):
        self.ctx = load_and_validate_site_data(ROOT)
        self.stmt = self.ctx.statements['stmt-party-a-housing-001']
        self.rel = self.ctx.relationships['rel-housing-rental-regulation-party-a-party-b']

    def test_projection_is_deterministic_and_has_only_the_publish_set(self):
        before = comparison_bundle_script(self.ctx)
        payload = build_comparison_payload(self.ctx)
        self.ctx.statements = dict(reversed(list(self.ctx.statements.items())))
        self.ctx.relationships = dict(reversed(list(self.ctx.relationships.items())))
        self.assertEqual(before, comparison_bundle_script(self.ctx))
        positions = [p for ms in payload['measuresByTopic'].values() for m in ms for p in m['positions'].values()]
        self.assertEqual({p['statementId'] for p in positions}, set(self.ctx.statements))
        self.assertNotIn('reviews', before)
        self.assertNotIn('review_notes', before)
        self.assertTrue(all(p['electionId'] == self.ctx.election_id for p in positions))

    def test_explicit_drafts_and_mixed_election_sets_fail_before_output(self):
        for stmt in [replace(self.stmt, review_status='draft'), replace(self.stmt, election_id='es-gen-2023')]:
            with self.subTest(stmt=stmt.review_status, election=stmt.election_id), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / 'site'
                with self.assertRaises(BuildValidationError):
                    build_site(ROOT, out, custom_statements=[stmt], custom_relationships=[])
                self.assertFalse(out.exists())
        with self.assertRaisesRegex(BuildValidationError, 'election mismatch'):
            load_and_validate_site_data(ROOT, custom_relationships=[replace(self.rel, election_id='es-gen-2023')])

    def test_projection_rejects_bad_urls_and_unreviewed_or_dangling_relationships(self):
        for url in ['javascript:alert(1)', 'data:text/html,evil', 'https://name:secret@example.test/x', 'https://@example.test/x',
                    'https://example.test:bad/x', 'https://example.test/\npath', 'https://example.test/\\path']:
            with self.subTest(url=url):
                ctx = replace(self.ctx, statements={self.stmt.id: replace(self.stmt, source_url=url)}, relationships={})
                with self.assertRaisesRegex(BuildValidationError, 'HTTP'):
                    build_comparison_payload(ctx)
        for rel in [replace(self.rel, review_status='draft'), replace(self.rel, statement_ids=['unknown']),
                    replace(self.rel, election_id='es-gen-2023')]:
            with self.subTest(rel=rel):
                with self.assertRaises(BuildValidationError):
                    build_comparison_payload(replace(self.ctx, relationships={rel.id: rel}))

    def test_invalidated_relationship_is_absent_and_does_not_reappear(self):
        ctx = load_and_validate_site_data(ROOT, custom_relationships=[replace(
            self.rel, status='invalidated', invalidation_reason='Synthetic correction')])
        payload = build_comparison_payload(ctx)
        self.assertFalse(any(m['relationships'] for ms in payload['measuresByTopic'].values() for m in ms))
        text = render_comparison_measures(ctx, payload, 'housing', *self.rel.party_ids)
        self.assertNotIn(self.rel.summary, text)
        self.assertIn('Comparación pendiente de revisión', text)

    def test_pending_2023_has_no_positions_or_fixture_fallback(self):
        ctx = load_and_validate_site_data(ROOT, election_id='es-gen-2023')
        self.assertTrue(all(not ms for ms in build_comparison_payload(ctx)['measuresByTopic'].values()))
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'site'
            build_site(ROOT, out, election_id='es-gen-2023')
            home = (out / 'index.html').read_text()
            self.assertIn('data-comparison="validated"', home)
            self.assertIn(comparison_bundle_name(ctx), home)
            self.assertNotIn('class="measure-group"', home)
            self.assertIn('Contenido pendiente de publicación', home)

    def test_hostile_strings_and_locators_have_browser_static_parity(self):
        hostile = '</script><img src=x onerror="alert(1)">&\u2028'
        stmt = replace(self.stmt, summary=hostile, quote=hostile, qualifications=[hostile], source_section=hostile)
        ctx = replace(self.ctx, statements={stmt.id: stmt}, relationships={})
        payload = build_comparison_payload(ctx)
        static = render_comparison_measures(ctx, payload, 'housing', self.rel.party_ids[0], self.rel.party_ids[1])
        self.assertNotIn('<img', static)
        self.assertIn('&lt;img', static)
        self.assertIn('Contenido pendiente de publicación', static)
        script = comparison_bundle_script(ctx)
        self.assertNotIn('</script>', script)
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / 'data.js'
            bundle.write_text(script)
            node = subprocess.run(['node', str(ROOT / 'tests/comparison_publish_behavior.cjs'), str(bundle)],
                                  cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stdout + node.stderr)
        browser = json.loads(node.stdout)
        self.assertNotIn('<img', browser['html'])
        self.assertIn('&lt;img', browser['html'])
        self.assertIn(stmt.source_url + '#page=34', static)
        self.assertIn(stmt.source_url + '#page=34', browser['html'])
        self.assertIn(stmt.last_reviewed_date, static)
        self.assertIn(stmt.last_reviewed_date, browser['html'])
        self.assertIn('Contenido pendiente de publicación', browser['html'])
        self.assertNotIn('Coincidencia', browser['html'])
        self.assertIn('election', browser)
        self.assertEqual(browser['election'], ctx.election_id)

    def test_late_candidate_failure_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'site'
            build_site(ROOT, out)
            before = {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()}
            from elecciones2026.generator import compute_sha256
            def fail_late(path):
                if path.name == 'sharing.js' and path.parent.name.startswith('.tmp_'):
                    raise OSError('late candidate failure')
                return compute_sha256(path)
            with patch('elecciones2026.generator.compute_sha256', side_effect=fail_late):
                with self.assertRaises(OSError):
                    build_site(ROOT, out, election_id='es-gen-2023')
            self.assertEqual(before, {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*') if p.is_file()})
            self.assertFalse(list(Path(tmp).glob('.tmp_*')))

    def test_failed_switch_restores_previous_directory_and_removes_owned_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, staging = Path(tmp) / 'site', Path(tmp) / 'candidate'
            out.mkdir(); staging.mkdir()
            (out / 'index.html').write_text('previous')
            (staging / 'index.html').write_text('candidate')
            rename = Path.rename
            def fail_switch(path, target):
                if path == staging:
                    raise OSError('injected rename failure')
                return rename(path, target)
            with patch.object(Path, 'rename', fail_switch), self.assertRaises(OSError):
                publish_directory(staging, out)
            self.assertEqual((out / 'index.html').read_text(), 'previous')
            self.assertFalse(list(Path(tmp).glob('.previous_*')))

    def test_complete_replacement_withdraws_stale_assets_and_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'site'
            build_site(ROOT, out, quiz_mode='mock')
            old = set(out.glob('quiz-data.*.js')) | set(out.glob('comparison-data.*.js'))
            (out / 'stale.html').write_text('obsolete claim')
            build_site(ROOT, out, election_id='es-gen-2023')
            self.assertFalse((out / 'stale.html').exists())
            self.assertTrue(all(not p.exists() for p in old))
            target = Path(tmp) / 'linked'
            target.symlink_to(out, target_is_directory=True)
            with self.assertRaisesRegex(BuildValidationError, 'symlink'):
                build_site(ROOT, target)
            staging = Path(tmp) / 'unsafe'
            staging.mkdir()
            (staging / 'link').symlink_to(out / 'index.html')
            with self.assertRaisesRegex(BuildValidationError, 'symlink'):
                publish_directory(staging, out)

    def test_approved_relationship_and_qualification_render_in_both_paths(self):
        payload = build_comparison_payload(self.ctx)
        static = render_comparison_measures(self.ctx, payload, 'housing', *self.rel.party_ids)
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / 'data.js'
            bundle.write_text(comparison_bundle_script(self.ctx))
            result = subprocess.run(['node', str(ROOT / 'tests/comparison_publish_behavior.cjs'), str(bundle)],
                                    cwd=ROOT, capture_output=True, text=True, check=True)
        browser = json.loads(result.stdout)['html']
        for text in [self.rel.summary, *self.rel.differences, self.stmt.summary, *self.stmt.qualifications]:
            self.assertIn(text, static)
            self.assertIn(text, browser)
        self.assertIn('rel-callout-agreement', static)
        self.assertIn('rel-callout-agreement', browser)

    def test_missing_bundle_and_wrong_election_never_use_fictional_positions(self):
        for script in ['/* failed bundle */', comparison_bundle_script(load_and_validate_site_data(ROOT, election_id='es-gen-2023'))]:
            with self.subTest(script=script[:30]), tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp) / 'data.js'
                bundle.write_text(script)
                result = subprocess.run(['node', str(ROOT / 'tests/comparison_publish_behavior.cjs'), str(bundle)],
                                        cwd=ROOT, capture_output=True, text=True, check=True)
                browser = json.loads(result.stdout)['html']
            self.assertNotIn('Limitar los precios de alquiler', browser)
            self.assertNotIn('party-statement', browser)

    def test_symlink_parent_and_failed_recovery_keep_prior_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = base / 'real'
            real.mkdir()
            linked = base / 'linked'
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(BuildValidationError, 'parents'):
                build_site(ROOT, linked / 'new' / 'site')
            self.assertFalse((real / 'new').exists())
            out, staging = base / 'site', base / 'candidate'
            out.mkdir(); staging.mkdir()
            (out / 'index.html').write_text('previous')
            rename = Path.rename
            def fail_recovery(path, target):
                if path == staging:
                    out.mkdir()  # A concurrent path cannot authorize deletion of the backup.
                    raise OSError('switch failed')
                if path.name.startswith('.previous_'):
                    raise OSError('recovery failed')
                return rename(path, target)
            with patch.object(Path, 'rename', fail_recovery), self.assertRaisesRegex(OSError, 'recovery'):
                publish_directory(staging, out)
            backups = list(base.glob('.previous_*'))
            self.assertEqual(len(backups), 1)
            self.assertEqual((backups[0] / 'index.html').read_text(), 'previous')

    def test_budget_withdrawal_removes_old_routes_and_snapshot(self):
        import test_budget as fixtures
        from elecciones2026.budget import load_bundle
        fixture = fixtures.BudgetTests()
        fixture.setUp()
        try:
            bundle = fixture.create()
            manifest, payload = load_bundle(bundle, require_publication=False)
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / 'site'
                def synthetic_copy(source, target, *args, **kwargs):
                    snapshot = target / 'static/budget' / source.name
                    snapshot.mkdir(parents=True, exist_ok=True)
                    (snapshot / 'snapshot.json').write_text('{}')
                with patch('elecciones2026.budget.load_bundle', return_value=(manifest, payload)), \
                     patch('elecciones2026.budget.copy_reviewed_bundle', side_effect=synthetic_copy):
                    build_site(ROOT, out, budget_bundle=bundle)
                self.assertTrue((out / 'presupuestos/2023/index.html').exists())
                self.assertTrue((out / 'static/budget').exists())
                build_site(ROOT, out)
                self.assertFalse((out / 'presupuestos').exists())
                self.assertFalse((out / 'static/budget').exists())
        finally:
            fixture.tearDown()
