"""Exercise the real publication gates and package checks for E3.3 transfer."""
import io
import json
import os
from pathlib import Path
import re
from types import SimpleNamespace
import textwrap
import unittest
from unittest.mock import patch
import urllib.error

WORKFLOW = (Path(__file__).resolve().parents[1] / '.github/workflows/ci.yml').read_text()


class TransferWorkflowTests(unittest.TestCase):
    def test_candidate_gates_require_an_approved_main_push(self):
        # Evaluate the expressions actually used to save and publish candidates.
        gates = re.findall(r'^\s+if: (.*github\.repository.*)$', WORKFLOW, re.MULTILINE)
        self.assertEqual(len(gates), 3)
        for repository in ('c2ventures/elecciones2026', 'barnolacesc/elecciones2026',
                           'attacker/elecciones2026', 'barnolacesc/another-project'):
            for event in ('push', 'pull_request', 'pull_request_target'):
                for ref in ('refs/heads/main', 'refs/heads/feature'):
                    expected = (repository in ('c2ventures/elecciones2026', 'barnolacesc/elecciones2026')
                                and event == 'push' and ref == 'refs/heads/main')
                    context = {
                        '__builtins__': {}, 'fromJSON': json.loads,
                        'contains': lambda values, value: value in values,
                        'github': SimpleNamespace(repository=repository, event_name=event, ref=ref),
                    }
                    for gate in gates:
                        with self.subTest(repository=repository, event=event, ref=ref):
                            self.assertEqual(eval(gate.replace('&&', 'and'), context), expected)

    def test_registry_check_selects_account_type_and_rejects_public_packages(self):
        publisher = WORKFLOW.split('  publish-candidate:', 1)[1]
        code = textwrap.dedent(re.search(
            r"python3 - <<'PYTHON'\n(.*?)          PYTHON", publisher, re.DOTALL).group(1))
        for repository, account in (('c2ventures/elecciones2026', 'orgs/c2ventures'),
                                    ('barnolacesc/elecciones2026', 'users/barnolacesc')):
            endpoint = f'https://api.github.com/{account}/packages/container/elecciones2026'
            with patch.dict(os.environ, GITHUB_REPOSITORY=repository, REGISTRY_TOKEN='test-token'), \
                    patch('urllib.request.urlopen') as request:
                for visibility in ('private', 'public'):
                    response = io.BytesIO(json.dumps({'visibility': visibility}).encode())
                    request.return_value.__enter__.return_value = response
                    with self.subTest(repository=repository, visibility=visibility):
                        if visibility == 'private':
                            exec(code, {})
                        else:
                            with self.assertRaises(AssertionError):
                                exec(code, {})
                        self.assertEqual(request.call_args.args[0].full_url, endpoint)
                for status in (404, 403, 500):
                    error = urllib.error.HTTPError(endpoint, status, '', {}, io.BytesIO())
                    self.addCleanup(error.close)
                    request.side_effect = error
                    with self.subTest(repository=repository, status=status):
                        if status == 404:
                            exec(code, {})  # First publication creates a private package.
                        else:
                            with self.assertRaises(urllib.error.HTTPError):
                                exec(code, {})
        with patch.dict(os.environ, GITHUB_REPOSITORY='attacker/elecciones2026'), \
                patch('urllib.request.urlopen') as request, self.assertRaises(KeyError):
            exec(code, {})
        request.assert_not_called()
