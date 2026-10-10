"""Run E3.4 scenarios against isolated local Docker containers; never deploy."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import threading
import time
import urllib.request
import uuid

from report import evaluate, markdown, origin_metrics, project_cost

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def command(*args, **kwargs):
    return subprocess.check_output(list(args), text=True, **kwargs).strip()


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def byte_size(value):
    match = re.fullmatch(r'([0-9.]+)\s*(B|kB|KB|KiB|MB|MiB|GB|GiB)', value.strip())
    if not match:
        raise ValueError(f'Unknown Docker memory unit: {value}')
    multiplier = {'B': 1, 'kB': 1000, 'KB': 1000, 'KiB': 1024, 'MB': 10**6,
                  'MiB': 1024**2, 'GB': 10**9, 'GiB': 1024**3}[match[2]]
    return float(match[1]) * multiplier


def sample_resources(name, stop, samples, errors):
    while not stop.is_set():
        try:
            data = json.loads(command('docker', 'stats', '--no-stream', '--format', '{{json .}}', name, timeout=10))
            samples.append({'cpu_percent_of_quota': float(data['CPUPerc'].rstrip('%')) / 2,
                            'memory_bytes': byte_size(data['MemUsage'].split('/')[0])})
        except (ValueError, subprocess.SubprocessError) as exc:
            errors.append(type(exc).__name__)
        stop.wait(0.5)


def local_run(plan, image, output):
    run_id = 'e34-' + uuid.uuid4().hex[:10]
    origin, edge = run_id + '-origin', run_id + '-edge'
    port = free_port()
    base = f'http://127.0.0.1:{port}'
    containers = []
    output.mkdir(parents=True, exist_ok=True)
    info = json.loads(command('docker', 'info', '--format', '{{json .}}'))
    report = {'schema_version': 1, 'package': 'E3.4', 'environment': 'local-rehearsal',
              'date': datetime.now(timezone.utc).isoformat(),
              'git_revision': command('git', '-C', str(ROOT), 'rev-parse', 'HEAD'),
              'image_id': command('docker', 'image', 'inspect', image, '--format', '{{.Id}}'),
              'harness_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [HERE / 'client.cjs', HERE / 'report.py', HERE / 'run.py',
                                           HERE / 'edge.conf', HERE / 'plan.json']},
              'docker': {k: info[k] for k in ('NCPU', 'MemTotal', 'OperatingSystem', 'ServerVersion')},
              'origin_limits': {'cpu_quota': 2, 'memory_limit_bytes': 300_000_000},
              'plan': plan, 'scenarios': [], 'production_acceptance': 'pending',
              'limits': [
                  'Local nginx caching is a fixture, not Cloudflare. No public DNS/TLS, geography, WAF, or live Hetzner evidence.',
                  'The origin has a two-core quota; Docker shares a host with the generator and edge. It is not a dedicated 2-vCPU/8-GB VM.',
                  'HTTP workload samples page navigation and 10% resource reloads; it does not execute JavaScript, fetch original programmes, or measure mobile rendering.',
                  'CPU is sampled container CPU divided by its two-core quota; whole-VM CPU, sub-sample peaks, monthly availability, and billing are unverified.',
                  'ADR-0001 is proposed pending G0 approval. Task 4.7 uses a stricter 200 origin req/s limit than ADR cold-cache estimates.',
                  'Any dropped requests or large scheduling delays invalidate capacity claims; distribute generators before a live rerun.',
                  'If origin targets fail, inspect cache-key cardinality/revalidation, then propose an owner-approved capacity increase within EUR 50/month and rerun.',
              ]}
    with tempfile.TemporaryDirectory(prefix='e34-load-') as tmp:
        tmp = Path(tmp)
        config = (ROOT / 'nginx/default.conf').read_text()
        # Numeric observations only: no URL, IP, user agent, or political selection.
        config = ('log_format load_measure "$msec $status $request_time $body_bytes_sent";\n'
                  'map $http_user_agent $load_request { default 0; "elecciones2026-load-rehearsal/1" 1; }\n') + config
        config = config.replace('    root   /usr/share/nginx/html;',
                                '    access_log /tmp/load-origin.log load_measure if=$load_request;\n    root   /usr/share/nginx/html;')
        config = config.replace('    # Compression',
                                '    location = /__load_origin_ready { access_log off; return 200 "ready\\n"; }\n\n    # Compression')
        origin_config = tmp / 'origin.conf'
        origin_config.write_text(config)
        try:
            command('docker', 'network', 'create', run_id)
            command('docker', 'run', '-d', '--rm', '--name', origin, '--network', run_id,
                    '--network-alias', 'load-origin', '--cpus', '2', '--memory', '300000000',
                    '--read-only', '--tmpfs', '/tmp', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
                    '--log-driver', 'none', '-v', f'{origin_config}:/etc/nginx/conf.d/default.conf:ro', image)
            containers.append(origin)

            def start_edge():
                command('docker', 'run', '-d', '--rm', '--name', edge, '--network', run_id,
                        '-p', f'127.0.0.1:{port}:8080', '--read-only', '--tmpfs', '/tmp',
                        '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true', '--log-driver', 'none',
                        '-v', f'{HERE / "edge.conf"}:/etc/nginx/conf.d/default.conf:ro', image)
                if edge not in containers:
                    containers.append(edge)
                for _ in range(50):
                    try:
                        with urllib.request.urlopen(base + '/__load_ready', timeout=1) as response:
                            if response.read() == b'ready\n':
                                return
                    except OSError:
                        time.sleep(0.1)
                raise RuntimeError('Local cache fixture did not become ready')

            start_edge()
            with urllib.request.urlopen(base + '/', timeout=5) as response:
                home = response.read().decode()
            preview = re.search(r'property="og:image" content="[^"]+(/assets/social-preview-[0-9a-f]+\.png)"', home)
            if not preview:
                raise ValueError('Generated artifact is missing a fingerprinted preview image')
            pages = ['/', '/metodo/', '/fuentes/', '/correcciones/'] + [
                f'/temas/{topic}/' for topic in ('housing', 'education', 'health-social-services',
                'economy-work-tax', 'immigration', 'foreign-policy-eu', 'climate-energy', 'institutions-rights')]
            # Shared comparisons preserve query strings in the real edge cache key.
            pages += ['/?topic=housing&partyA=partido-ejemplo-a&partyB=partido-ejemplo-b',
                      '/?topic=education&partyA=pp&partyB=erc']
            assets = ['/styles.css', '/app.js', '/sharing.js', '/tokens/tokens.css', preview[1]]
            for scenario in plan['scenarios']:
                if scenario['cold_cache']:
                    command('docker', 'stop', edge)
                    start_edge()  # A noncached readiness endpoint leaves workload URLs cold.
                else:
                    for path in pages + assets:
                        request = urllib.request.Request(base + path, headers={'Accept-Encoding': 'gzip'})
                        with urllib.request.urlopen(request, timeout=5) as response:
                            response.read()
                before = command('docker', 'exec', origin, 'cat', '/tmp/load-origin.log').splitlines()
                settings = {**plan, 'scenario': scenario, 'target': base, 'environment': 'local-rehearsal',
                            'pages': pages, 'assets': assets}
                settings_file = tmp / 'client.json'
                settings_file.write_text(json.dumps(settings))
                result_file = output / f'{scenario["name"]}-client.json'
                samples, errors, stop = [], [], threading.Event()
                sampler = threading.Thread(target=sample_resources, args=(origin, stop, samples, errors))
                sampler.start()
                print(f"Running {scenario['name']}: {plan['readers']} readers for {scenario['seconds']} seconds", flush=True)
                try:
                    subprocess.run(['node', str(HERE / 'client.cjs'), str(settings_file), str(result_file)],
                                   check=True, timeout=scenario['seconds'] + plan['request_timeout_ms'] / 1000 + 30)
                finally:
                    stop.set()
                    sampler.join(timeout=12)
                client = json.loads(result_file.read_text())
                after = command('docker', 'exec', origin, 'cat', '/tmp/load-origin.log').splitlines()
                measured = origin_metrics('\n'.join(after[len(before):]), scenario['seconds'], samples)
                entry = {'name': scenario['name'], 'client': client, 'origin': measured,
                         'resource_sampling_errors': errors, 'checks': evaluate(client, measured, scenario['name'])}
                report['scenarios'].append(entry)
                if not client['completed'] or not samples or errors:
                    raise RuntimeError('Incomplete workload or resource observations')
            report['cost'] = project_cost(report['scenarios'], plan['cost_assumptions'])
            report['local_measured_checks_pass'] = all(c['status'] == 'pass'
                for s in report['scenarios'] for c in s['checks'].values())
            (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            (output / 'report.md').write_text(markdown(report))
            return report
        finally:
            for name in reversed(containers):
                subprocess.run(['docker', 'rm', '-f', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['docker', 'network', 'rm', run_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', default='elecciones2026:load')
    parser.add_argument('--plan', type=Path, default=HERE / 'plan.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/load')
    parser.add_argument('--seconds', type=int, help='Override each scenario duration for a short CI rehearsal')
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text())
    if args.seconds is not None:
        if not 15 <= args.seconds <= 600:
            parser.error('Scenario duration must be between 15 and 600 seconds')
        for scenario in plan['scenarios']:
            scenario['seconds'] = args.seconds
    local_run(plan, args.image, args.output)
    print(f'Report: {args.output / "report.md"}; production acceptance remains pending.')


if __name__ == '__main__':
    main()
