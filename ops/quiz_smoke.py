#!/usr/bin/env python3
"""Rehearse mock rollback and quiz withdrawal in owned loopback Docker fixtures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]


def command(*args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f"Fixture command failed: {args[0:2]}; inspect local Docker tooling")
    return result.stdout.strip()


def fetch(base, route):
    with urllib.request.urlopen(base + route, timeout=5) as response:
        return response.read(), dict(response.headers)


def quiz_scripts(html):
    scripts = re.findall(r'<script src="\.\./(quiz-[^"]+\.js)" defer>', html)
    if len(scripts) != 3:
        raise AssertionError("Expected three local quiz scripts")
    return scripts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mock-image', default='quiz-preview:latest')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/quiz-release.json')
    args = parser.parse_args()
    mock_id = command('docker', 'image', 'inspect', args.mock_image, '--format', '{{.Id}}')
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', mock_id):
        raise ValueError('Expected a local immutable image identity')
    run_id = 'e44-quiz-' + uuid.uuid4().hex[:12]
    tags = [run_id + ':candidate', run_id + ':unavailable', run_id + ':base']
    active = None
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    base = f'http://127.0.0.1:{port}'
    report = {'package': 'E4.4', 'fixture': 'fictional local rollback/withdrawal',
              'images': {'mock': mock_id}, 'checks': [], 'production_acceptance': 'pending',
              'limits': ['Local fixture only; no approved real programme set or release approval.',
                         'No registry, public deployment, DNS/TLS, edge purge, or provider privacy validation.',
                         'Withdrawal cannot erase an already loaded page or a browser-managed cached artifact.']}

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        report['checks'].append(name)

    def activate(image):
        nonlocal active
        if active:
            command('docker', 'rm', '-f', active)
            active = None
        # Names are owned by this run; never reuse the human preview container.
        active = run_id + '-site'
        command('docker', 'run', '-d', '--rm', '--name', active, '--pull', 'never',
                '-p', f'127.0.0.1:{port}:8080', '--read-only', '--tmpfs', '/tmp',
                '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
                '--pids-limit', '64', '--memory', '256m', '--log-driver', 'none', image)
        for _ in range(50):
            try:
                fetch(base, '/cuestionario/')
                return
            except OSError:
                time.sleep(.1)
        raise RuntimeError('Fixture quiz route did not become ready')

    try:
        # BuildKit resolves local tags for FROM; retain the inspected identity in evidence.
        command('docker', 'image', 'tag', mock_id, tags[2])
        print('Checking local mock image and preparing isolated fixtures', flush=True)
        activate(mock_id)
        original, headers = fetch(base, '/cuestionario/')
        html = original.decode()
        scripts = quiz_scripts(html)
        data_script = next(name for name in scripts if name.startswith('quiz-data.'))
        data = fetch(base, '/' + data_script)[0].decode()
        check('Only explicit fictional data is rehearsed', '"mode":"mock"' in data)
        check('Mock is excluded from indexing', 'noindex, nofollow' in html)
        check('Quiz HTML has bounded cache lifetime', 'max-age=300' in headers.get('Cache-Control', ''))
        for script in scripts:
            payload, script_headers = fetch(base, '/' + script)
            check(f'Complete {script.split(".")[0]} delivered', bool(payload) and 'immutable' in script_headers.get('Cache-Control', ''))
        check('Runtime is nonprivileged', command('docker', 'exec', active, 'id', '-u') == '101')
        inspection = json.loads(command('docker', 'inspect', active))[0]
        check('Runtime filesystem is read-only', inspection['HostConfig']['ReadonlyRootfs'])

        with tempfile.TemporaryDirectory(prefix=run_id + '-') as temporary:
            root = Path(temporary)
            # A nonpolitical HTML marker distinguishes the candidate artifact.
            candidate = html.replace('</head>', '<meta name="quiz-fixture" content="candidate-b">\n</head>')
            (root / 'index.html').write_text(candidate)
            (root / 'Dockerfile').write_text(
                f'FROM {tags[2]}\nCOPY --chown=101:101 index.html /usr/share/nginx/html/cuestionario/index.html\n')
            command('docker', 'build', '--tag', tags[0], str(root))
            report['images']['candidate'] = command('docker', 'image', 'inspect', tags[0], '--format', '{{.Id}}')
            command('docker', 'build', '--build-arg', 'ELECTION_ID=es-gen-2023',
                    '--build-arg', 'QUIZ_MODE=unavailable', '--tag', tags[1], str(ROOT))
            report['images']['unavailable'] = command('docker', 'image', 'inspect', tags[1], '--format', '{{.Id}}')

        print('Rehearsing A -> B -> A and source-defect withdrawal', flush=True)
        activate(report['images']['candidate'])
        check('Candidate artifact served', fetch(base, '/cuestionario/')[0].decode() == candidate)
        started = time.monotonic()
        activate(mock_id)
        restored = fetch(base, '/cuestionario/')[0]
        check('Functional rollback restores exact mock artifact', restored == original)
        report['rollback_seconds'] = time.monotonic() - started
        report['restored_page_sha256'] = hashlib.sha256(restored).hexdigest()

        # Source defects use a disabled artifact, never the invalid old quiz.
        activate(report['images']['unavailable'])
        disabled = fetch(base, '/cuestionario/')[0].decode()
        check('Withdrawal shows unavailable explanation', 'El cuestionario aún no está disponible' in disabled)
        check('Withdrawal loads no scoring scripts', not re.search(r'<script[^>]+quiz-', disabled))
        check('Withdrawal removes answer application', 'id="quiz-app"' not in disabled)
        for script in scripts:
            try:
                fetch(base, '/' + script)
            except urllib.error.HTTPError as error:
                check(f'Withdrawn {script.split(".")[0]} absent at origin', error.code == 404)
            else:
                raise AssertionError('Withdrawn scoring artifact is still served')
        for route in ['/metodo/', '/fuentes/', '/correcciones/']:
            check(f'{route} remains available after withdrawal', bool(fetch(base, route)[0]))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print(f'PASS {len(report["checks"])} local recovery checks; rollback {report["rollback_seconds"]:.1f}s. G5 remains pending.')
    finally:
        if active:
            subprocess.run(['docker', 'rm', '-f', active], capture_output=True)
        for tag in tags:
            subprocess.run(['docker', 'image', 'rm', tag], capture_output=True)


if __name__ == '__main__':
    main()
