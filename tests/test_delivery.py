"""Exercise release evidence, credential isolation, and external publication boundaries."""
import copy
from contextlib import redirect_stdout
import io
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from elecciones2026.generator import build_site

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('delivery', ROOT / 'ops/delivery.py')
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)
IMAGE = 'ghcr.io/c2ventures/elecciones2026@sha256:' + 'a' * 64
RUN = {'id': 123, 'run_attempt': 1, 'event': 'push', 'head_branch': 'main',
       'path': '.github/workflows/ci.yml', 'status': 'completed', 'conclusion': 'success',
       'repository': {'full_name': delivery.TRUSTED_REPOSITORIES[0]},
       'head_repository': {'full_name': delivery.TRUSTED_REPOSITORIES[0]}, 'head_sha': 'b' * 40}
RECORD = {'schema': 1, 'run_id': '123', 'run_attempt': '1', 'revision': 'b' * 40,
          'platform': 'linux/amd64', 'classification': 'private-staging',
          'election_id': 'es-gen-2023', 'quiz_mode': 'unavailable',
          'pilot_mode': 'source-linked-provisional',
          'canonical_base': 'https://xn--eleccionesespaa2026-83b.es',
          'image': IMAGE, 'home_sha256': 'c' * 64}
RECORD_2026 = {'schema': 1, 'run_id': '123', 'run_attempt': '1', 'revision': 'b' * 40,
               'platform': 'linux/amd64', 'classification': 'private-staging',
               'election_id': 'es-gen-2026', 'quiz_mode': 'unavailable',
               'pilot_mode': 'approved-records-only',
               'canonical_base': 'https://xn--eleccionesespaa2026-83b.es',
               'image': IMAGE, 'home_sha256': 'c' * 64}
ENV = {'VPS_HOST': '192.0.2.10', 'VPS_USER': 'deployer', 'VPS_SSH_PORT': '22',
       'VPS_SSH_KEY': 'test-only-key', 'VPS_KNOWN_HOSTS': 'test-only-trust',
       'STAGING_BASIC_AUTH': 'test-user:test-password'}


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        context = patch.dict(delivery.os.environ, GITHUB_REPOSITORY=delivery.TRUSTED_REPOSITORIES[0])
        context.start()
        self.addCleanup(context.stop)

    def test_transfer_binds_run_and_image_to_the_active_repository(self):
        for repository in delivery.TRUSTED_REPOSITORIES:
            run = copy.deepcopy(RUN)
            run['repository']['full_name'] = repository
            run['head_repository']['full_name'] = repository
            record = dict(RECORD, image='ghcr.io/' + repository + '@sha256:' + 'a' * 64)
            with self.subTest(repository=repository), \
                    patch.dict(delivery.os.environ, GITHUB_REPOSITORY=repository):
                delivery.trusted_run(run, '123')
                self.assertEqual(delivery.candidate(record, run), record['image'])
                for other in (*delivery.TRUSTED_REPOSITORIES, 'fork/elecciones2026'):
                    if other == repository:
                        continue
                    with self.assertRaises(delivery.DeliveryError):
                        delivery.candidate(dict(record, image='ghcr.io/' + other + '@sha256:' + 'a' * 64), run)
                    foreign_run = copy.deepcopy(run)
                    foreign_run['head_repository']['full_name'] = other
                    with self.assertRaises(delivery.DeliveryError):
                        delivery.candidate(record, foreign_run)

    def test_run_api_uses_only_the_active_approved_repository(self):
        import json
        for repository in (*delivery.TRUSTED_REPOSITORIES, 'fork/elecciones2026', ''):
            run = copy.deepcopy(RUN)
            run['repository']['full_name'] = repository
            run['head_repository']['full_name'] = repository
            with self.subTest(repository=repository), \
                    patch.dict(delivery.os.environ, GITHUB_REPOSITORY=repository, GH_TOKEN='test-token'), \
                    patch.object(delivery.urllib.request, 'urlopen') as request:
                request.return_value.__enter__.return_value.read.return_value = json.dumps(run).encode()
                if repository in delivery.TRUSTED_REPOSITORIES:
                    self.assertEqual(delivery.read_run('123'), run)
                    self.assertEqual(request.call_args.args[0].full_url,
                                     f'https://api.github.com/repos/{repository}/actions/runs/123')
                else:
                    with self.assertRaises(delivery.DeliveryError):
                        delivery.read_run('123')
                    request.assert_not_called()

    def test_only_successful_canonical_main_push_is_trusted(self):
        delivery.trusted_run(RUN, '123')
        for field, value in [('event', 'pull_request'), ('head_branch', 'feature'),
                             ('conclusion', 'failure'), ('status', 'in_progress'),
                             ('path', '.github/workflows/other.yml'),
                             ('head_repository', {'full_name': 'fork/site'})]:
            with self.subTest(field=field):
                run = copy.deepcopy(RUN)
                run[field] = value
                with self.assertRaises(delivery.DeliveryError):
                    delivery.trusted_run(run, '123')
        with self.assertRaises(delivery.DeliveryError):
            delivery.trusted_run(RUN, '123; echo exploit')

    def test_candidate_must_match_run_attempt_revision_repository_and_classification(self):
        self.assertEqual(delivery.candidate(RECORD, RUN), IMAGE)
        for field, value in [('revision', 'd' * 40), ('run_id', '456'),
                             ('run_attempt', '2'), ('platform', 'linux/arm64'),
                             ('classification', 'public'), ('home_sha256', ''),
                             ('election_id', 'es-gen-2026'), ('election_id', None),
                             ('quiz_mode', 'mock'), ('quiz_mode', None),
                             ('pilot_mode', None), ('pilot_mode', 'other'),
                             ('canonical_base', 'https://example.invalid'), ('canonical_base', None),
                             ('image', 'ghcr.io/other/site@sha256:' + 'a' * 64)]:
            with self.subTest(field=field):
                record = dict(RECORD, **{field: value})
                with self.assertRaises(delivery.DeliveryError):
                    delivery.candidate(record, RUN)

    def test_2026_production_staging_candidate_and_mixed_mode_rejection(self):
        # Current 2026 approved-record candidate passes
        self.assertEqual(delivery.candidate(RECORD_2026, RUN), IMAGE)
        self.assertEqual(delivery.candidate(dict(RECORD_2026, quiz_mode='exploratory'), RUN), IMAGE)
        with self.assertRaises(delivery.DeliveryError):
            delivery.candidate(dict(RECORD, quiz_mode='exploratory'), RUN)
        # Historical 2023 provisional candidate passes for recovery
        self.assertEqual(delivery.candidate(RECORD, RUN), IMAGE)

        # Mixed election / pilot_mode combinations are rejected
        mixed_cases = [
            ({'election_id': 'es-gen-2026', 'pilot_mode': 'source-linked-provisional'},
             "Reject 2026 election with provisional 2023 pilot mode"),
            ({'election_id': 'es-gen-2023', 'pilot_mode': 'approved-records-only'},
             "Reject 2023 election with 2026 approved-records-only mode"),
            ({'election_id': 'es-gen-2026', 'pilot_mode': 'other'},
             "Reject unknown pilot mode with 2026 election"),
            ({'election_id': 'es-gen-2024', 'pilot_mode': 'approved-records-only'},
             "Reject unapproved election ID"),
        ]
        for changes, msg in mixed_cases:
            with self.subTest(msg=msg):
                record = dict(RECORD_2026, **changes)
                with self.assertRaises(delivery.DeliveryError):
                    delivery.candidate(record, RUN)

        # Public classifications must be strictly rejected
        for pub_class in ['public', 'public-production', 'staging-public', '']:
            with self.subTest(classification=pub_class):
                with self.assertRaises(delivery.DeliveryError):
                    delivery.candidate(dict(RECORD_2026, classification=pub_class), RUN)
                with self.assertRaises(delivery.DeliveryError):
                    delivery.candidate(dict(RECORD, classification=pub_class), RUN)

    def test_workflow_candidate_and_build_consistency(self):
        import re
        ci_yaml = (ROOT / '.github/workflows/ci.yml').read_text()
        # Verify Docker build step specifies 2026 production build args
        build_match = re.search(
            r'docker build [^\n]*--build-arg ELECTION_ID=(\S+)[^\n]*--build-arg QUIZ_MODE=(\S+)[^\n]*--build-arg PILOT_PROVISIONAL=(\S+)',
            ci_yaml,
        )
        self.assertIsNotNone(build_match, "Candidate docker build command must be present")
        election_arg, quiz_arg, pilot_arg = build_match.groups()
        self.assertEqual(election_arg, 'es-gen-2026')
        self.assertEqual(quiz_arg, 'exploratory')
        self.assertEqual(pilot_arg, '0')

        # Verify candidate release.json creation binds 2026 and approved-records-only consistently
        self.assertIn("'classification': 'private-staging'", ci_yaml)
        self.assertIn("'election_id': 'es-gen-2026'", ci_yaml)
        self.assertIn("'quiz_mode': 'exploratory'", ci_yaml)
        self.assertIn("'pilot_mode': 'approved-records-only'", ci_yaml)

        # Verify separate historical quiz rehearsal explicitly remains es-gen-2023
        quiz_rehearsal = re.search(
            r'docker build [^\n]*--build-arg ELECTION_ID=(\S+)[^\n]*--build-arg QUIZ_MODE=mock[^\n]*-t elecciones2026:quiz-ci',
            ci_yaml,
        )
        self.assertIsNotNone(quiz_rehearsal, "Quiz rehearsal docker build command must be present")
        self.assertEqual(quiz_rehearsal.group(1), 'es-gen-2023')

    def test_missing_credentials_invalid_connections_and_public_staging_do_not_mutate(self):
        for changes in [{'VPS_SSH_KEY': ''}, {'VPS_KNOWN_HOSTS': ''},
                        {'VPS_USER': 'root'}, {'VPS_HOST': '-oProxyCommand=bad'},
                        {'VPS_SSH_PORT': '65536'}, {'STAGING_BASIC_AUTH': ''}]:
            with patch.dict(delivery.os.environ, dict(ENV, **changes), clear=True), \
                    patch.object(delivery.subprocess, 'run') as run:
                with self.assertRaises(delivery.DeliveryError):
                    delivery.deliver(IMAGE, RECORD['home_sha256'])
                run.assert_not_called()
        with patch.dict(delivery.os.environ, ENV, clear=True), \
                patch.object(delivery, 'edge_probe', side_effect=delivery.DeliveryError('public')), \
                patch.object(delivery.subprocess, 'run') as run:
            with self.assertRaises(delivery.DeliveryError):
                delivery.deliver(IMAGE, RECORD['home_sha256'])
            run.assert_not_called()

    def test_key_files_removed_and_no_deploy_after_host_key_failure(self):
        paths = []
        def ssh_failure(command, **kwargs):
            path = Path(command[command.index('-i') + 1])
            paths.append(path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertIn('StrictHostKeyChecking=yes', command)
            self.assertEqual(command[-1], 'check')
            raise subprocess.CalledProcessError(255, 'ssh')
        with patch.dict(delivery.os.environ, ENV, clear=True), \
                patch.object(delivery, 'edge_probe'), \
                patch.object(delivery.subprocess, 'run', side_effect=ssh_failure):
            with self.assertRaises(subprocess.CalledProcessError):
                delivery.deliver(IMAGE, RECORD['home_sha256'])
        self.assertEqual(len(paths), 1)
        self.assertFalse(paths[0].exists())

    def test_success_verifies_content_and_removes_credentials(self):
        paths = []
        def ssh(command, **kwargs):
            paths.append(Path(command[command.index('-i') + 1]))
        with patch.dict(delivery.os.environ, ENV, clear=True), \
                patch.object(delivery, 'edge_probe') as probe, \
                patch.object(delivery.subprocess, 'run', side_effect=ssh) as run:
            delivery.deliver(IMAGE, RECORD['home_sha256'])
            self.assertEqual(run.call_args_list[-1].args[0][-1], 'deploy ' + IMAGE)
            self.assertEqual(probe.call_args_list[-1].args, (ENV['STAGING_BASIC_AUTH'], RECORD['home_sha256']))
        self.assertTrue(all(not path.exists() for path in paths))

    def test_public_staging_and_redirects_are_rejected(self):
        with patch.object(delivery.urllib.request, 'build_opener') as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.status = 200
            with self.assertRaises(delivery.DeliveryError):
                delivery.edge_probe(None)
            opener.return_value.open.side_effect = urllib.error.HTTPError('https://example.invalid', 401, '', {}, None)
            delivery.edge_probe(None)
            opener.return_value.open.side_effect = urllib.error.HTTPError('https://example.invalid', 302, '', {}, None)
            with self.assertRaises(delivery.DeliveryError):
                delivery.edge_probe(ENV['STAGING_BASIC_AUTH'])
        self.assertIsNone(delivery.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://elsewhere.invalid'))

    def test_edge_preflight_identifies_client_and_blocks_forbidden_responses(self):
        with patch.object(delivery.urllib.request, 'build_opener') as opener:
            def edge(request, **kwargs):
                self.assertEqual(request.get_header('User-agent'), 'elecciones2026-deployment/1')
                self.assertIsNone(request.get_header('Authorization'))
                raise urllib.error.HTTPError(request.full_url, 401, '', {}, None)
            opener.return_value.open.side_effect = edge
            delivery.edge_probe(None)
            opener.return_value.open.side_effect = urllib.error.HTTPError(
                'https://example.invalid', 403, '', {}, None)
            with patch.dict(delivery.os.environ, ENV, clear=True), \
                    patch.object(delivery.subprocess, 'run') as run:
                with self.assertRaises(delivery.DeliveryError):
                    delivery.deliver(IMAGE, RECORD['home_sha256'])
                run.assert_not_called()

    def test_approved_domain_in_generated_metadata_and_crawler_routes(self):
        base = 'https://xn--eleccionesespaa2026-83b.es'
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            build_site(root_dir=ROOT, output_dir=target, canonical_base=base)
            for path in target.rglob('*.html'):
                content = path.read_text()
                self.assertIn(f'<link rel="canonical" href="{base}/', content)
                self.assertIn(f'content="{base}/', content)
                self.assertNotIn('https://elecciones2026.es/', content)
            for filename in ('sitemap.xml', 'robots.txt'):
                content = (target / filename).read_text()
                self.assertIn(base, content)
                self.assertNotIn('https://elecciones2026.es/', content)

    def test_real_workflow_authorization_rejects_missing_approval_and_wrong_actor(self):
        import os
        import textwrap
        source = (ROOT / '.github/workflows/deliver.yml').read_text()
        code = textwrap.dedent(source.split("python3 - <<'PYTHON'\n", 1)[1].split("          PYTHON", 1)[0])
        environment = dict(os.environ, GITHUB_REPOSITORY=delivery.TRUSTED_REPOSITORIES[0],
                           GITHUB_REF='refs/heads/main', GITHUB_ACTOR='barnolacesc',
                           GITHUB_TRIGGERING_ACTOR='barnolacesc', APPROVED='true',
                           APPROVAL_RECORD='restricted-owner-review', READY='true')
        import sys
        result = subprocess.run([sys.executable, '-c', code], env=environment, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for repository in delivery.TRUSTED_REPOSITORIES:
            with self.subTest(repository=repository):
                result = subprocess.run([sys.executable, '-c', code],
                                        env=dict(environment, GITHUB_REPOSITORY=repository), capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
        pilot = dict(environment, GITHUB_ACTOR='chad-openclaw',
                     GITHUB_TRIGGERING_ACTOR='chad-openclaw',
                     APPROVAL_RECORD='Cesc Telegram 2026-10-14 private 2023 pilot')
        # Exercise both sides of the historical delegation expiry without
        # extending authorization or depending on the test runner's date.
        for day, expected in [('2026-10-31', 0), ('2026-11-01', 1)]:
            frozen = (
                "from datetime import date as RealDate\n"
                "from unittest.mock import patch\n"
                "class FrozenDate(RealDate):\n"
                "    @classmethod\n"
                f"    def today(cls): return cls.fromisoformat({day!r})\n"
                "with patch('datetime.date', FrozenDate):\n"
                f"    exec({code!r})\n"
            )
            with self.subTest(delegation_date=day):
                self.assertEqual(subprocess.run(
                    [sys.executable, '-c', frozen], env=pilot, capture_output=True,
                ).returncode, expected)
        self.assertNotEqual(subprocess.run([sys.executable, '-c', code],
                           env=dict(pilot, APPROVAL_RECORD='unrelated')).returncode, 0)
        for changes in [{'APPROVED': 'false'}, {'READY': ''}, {'APPROVAL_RECORD': ''},
                        {'GITHUB_REF': 'refs/heads/feature'}, {'GITHUB_ACTOR': 'someone-else'},
                        {'GITHUB_TRIGGERING_ACTOR': 'someone-else'},
                        {'GITHUB_REPOSITORY': 'fork/site'}]:
            with self.subTest(changes=changes):
                result = subprocess.run([sys.executable, '-c', code],
                                        env=dict(environment, **changes), capture_output=True)
                self.assertNotEqual(result.returncode, 0)

    def test_external_modified_content_and_unsafe_headers_fail(self):
        import hashlib
        body = b'tested private page'
        digest = hashlib.sha256(body).hexdigest()
        headers = {'Cache-Control': 'private, no-store', 'Content-Security-Policy': "default-src 'self'",
                   'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY'}
        with patch.object(delivery.urllib.request, 'build_opener') as opener:
            response = opener.return_value.open.return_value.__enter__.return_value
            response.status = 200
            response.headers = headers
            response.read.return_value = body
            delivery.edge_probe(ENV['STAGING_BASIC_AUTH'], digest)
            with self.assertRaises(delivery.DeliveryError):
                delivery.edge_probe(ENV['STAGING_BASIC_AUTH'], 'a' * 64)
            for field in headers:
                response.headers = {key: value for key, value in headers.items() if key != field}
                with self.subTest(field=field), self.assertRaises(delivery.DeliveryError):
                    delivery.edge_probe(ENV['STAGING_BASIC_AUTH'], digest)

    def test_http_failure_diagnostics_do_not_echo_credentials_or_response_details(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            record = Path(directory) / 'release.json'
            record.write_text(json.dumps(RECORD))
            output = io.StringIO()
            with patch.object(delivery, 'read_run', return_value=RUN), \
                    patch.object(delivery, 'deliver', side_effect=lambda *args: delivery.edge_probe(ENV['STAGING_BASIC_AUTH'])), \
                    patch.object(delivery.urllib.request, 'build_opener') as opener, \
                    patch('sys.argv', ['delivery', '123', '--candidate', str(record)]), \
                    redirect_stdout(output):
                opener.return_value.open.side_effect = urllib.error.HTTPError(
                    'https://example.invalid/' + ENV['STAGING_BASIC_AUTH'], 401,
                    ENV['VPS_SSH_KEY'], {'Secret': ENV['VPS_KNOWN_HOSTS']},
                    io.BytesIO(ENV['STAGING_BASIC_AUTH'].encode()))
                self.assertEqual(delivery.main(), 1)
            self.assertIn('Delivery blocked: External staging response failed: HTTP 401', output.getvalue())
            for name in ('STAGING_BASIC_AUTH', 'VPS_SSH_KEY', 'VPS_KNOWN_HOSTS'):
                self.assertNotIn(ENV[name], output.getvalue())

    def test_mismatch_metadata_identifies_response_without_exposing_raw_values(self):
        import hashlib
        import json
        body = b'private response containing ' + ENV['STAGING_BASIC_AUTH'].encode()
        output = io.StringIO()
        with patch.object(delivery.urllib.request, 'build_opener') as opener, redirect_stdout(output):
            response = opener.return_value.open.return_value.__enter__.return_value
            response.status = 200
            response.headers = {'Cache-Control': 'private, no-store',
                                'Content-Security-Policy': "default-src 'self'",
                                'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
                                'Content-Encoding': ENV['VPS_SSH_KEY']}
            response.read.return_value = body
            with self.assertRaisesRegex(delivery.DeliveryError, 'content hash'):
                delivery.edge_probe(ENV['STAGING_BASIC_AUTH'], 'a' * 64)
        details = json.loads(output.getvalue().split('Staging response metadata: ', 1)[1])
        self.assertEqual(details['response_bytes'], len(body))
        self.assertEqual(details['response_sha256'], hashlib.sha256(body).hexdigest())
        self.assertEqual(details['expected_sha256'], 'a' * 64)
        self.assertEqual(details['content_encoding'], 'other')
        self.assertNotIn(body.decode(), output.getvalue())
        self.assertNotIn(ENV['STAGING_BASIC_AUTH'], output.getvalue())
        self.assertNotIn(ENV['VPS_SSH_KEY'], output.getvalue())
