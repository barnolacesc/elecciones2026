"""E3.4 measurements and conservative capacity evaluation (standard library only)."""
from __future__ import annotations

import math


def percentile(values, fraction=0.95):
    if not values:
        return None
    return sorted(values)[math.ceil(len(values) * fraction) - 1]


def origin_metrics(log_text, seconds, samples):
    """Parse only numeric test access records; retain no visitor paths or addresses."""
    rows = [line.split() for line in log_text.splitlines() if line.strip()]
    counts = {}
    durations = []
    body_bytes = 0
    for row in rows:
        if len(row) != 4:
            raise ValueError('Malformed origin observation')
        timestamp, status, duration, size = float(row[0]), int(row[1]), float(row[2]), int(row[3])
        if not math.isfinite(timestamp) or not math.isfinite(duration) or duration < 0 or size < 0:
            raise ValueError('Invalid origin observation')
        bucket = math.floor(timestamp)
        counts[bucket] = counts.get(bucket, 0) + 1
        durations.append(duration * 1000)
        body_bytes += size
    cpus = [s['cpu_percent_of_quota'] for s in samples]
    memory = [s['memory_bytes'] for s in samples]
    return {
        'requests': len(rows), 'rps': len(rows) / seconds,
        'peak_one_second_rps': max(counts.values(), default=0),
        'response_p95_ms': percentile(durations), 'body_bytes': body_bytes,
        'body_mbps': body_bytes * 8 / seconds / 1e6,
        'cpu_average_percent_of_quota': sum(cpus) / len(cpus) if cpus else None,
        'cpu_peak_percent_of_quota': max(cpus) if cpus else None,
        'memory_peak_bytes': max(memory) if memory else None,
        'resource_samples': len(samples),
    }


def evaluate(client, origin, scenario_name):
    """Unknown observations cannot pass. HTTP failures and generator saturation stay visible."""
    normal = scenario_name == 'steady'
    checks = {}

    def check(name, value, operator, target):
        checks[name] = {'value': value, 'operator': operator, 'target': target,
                        'status': 'not_measured' if value is None else
                        ('pass' if (value < target if operator == '<' else
                                    value <= target if operator == '<=' else value >= target) else 'fail')}

    sent = client['sent']
    complete = client['completed']
    ratio = lambda n, d: n / d if d else None
    check('edge_scheduled_p95_ms', client['scheduled_response_p95_ms'], '<', 150 if normal else 200)
    check('edge_cache_hit_p95_ms', client['cache_hit_p95_ms'], '<', 150 if normal else 200)
    check('origin_p95_ms', origin['response_p95_ms'], '<', 250 if normal else 400)
    check('http_5xx_rate', ratio(sum(n for code, n in client['status'].items() if int(code) >= 500), sent), '<', 0.0005 if normal else 0.005)
    check('http_4xx_rate', ratio(sum(n for code, n in client['status'].items() if 400 <= int(code) < 500), sent), '<', 0.005 if normal else 0.01)
    check('network_errors', client['network_errors'], '<=', 0)
    check('dropped_requests', client['dropped'], '<=', 0)
    check('all_readers_served', client['readers_served'], '>=', client['readers'])
    check('generator_scheduling_lag_p95_ms', client['scheduling_lag_p95_ms'], '<=', 100)
    check('aggregate_hit_ratio', ratio(client['cache'].get('HIT', 0), complete)
          if not client['cache'].get('UNKNOWN') else None, '>=', 0.95 if normal else 0.85)
    for kind, target in [('html', 0.90 if normal else 0.85), ('asset', 0.99 if normal else 0.98)]:
        counts = client['classes'].get(kind, {})
        check(f'{kind}_hit_ratio', ratio(counts.get('hits', 0), counts.get('responses', 0))
              if not counts.get('unknown') else None, '>=', target)
    # Task 4.7 is stricter than ADR-0001's estimated 150–300 req/s cold-cache demand.
    check('origin_peak_one_second_rps', origin['peak_one_second_rps'], '<=', 200)
    check('origin_cpu_peak_percent_of_quota', origin['cpu_peak_percent_of_quota'], '<', 70)
    if normal:
        check('origin_cpu_average_percent_of_quota', origin['cpu_average_percent_of_quota'], '<', 30)
    check('origin_memory_bytes', origin['memory_peak_bytes'], '<', 150_000_000 if normal else 300_000_000)
    return checks


def project_cost(scenarios, assumptions):
    """Project body egress from explicitly supplied monthly traffic hours; do not claim billing proof."""
    gb = sum(s['origin']['body_bytes'] / s['client']['measurement_seconds'] *
             assumptions['monthly_scenario_hours'][s['name']] * 3600 for s in scenarios) / 1e9
    excess = max(0, gb - assumptions['included_origin_egress_gb'])
    rate = assumptions['egress_eur_per_gb']
    total = assumptions['fixed_monthly_eur'] if not excess else (
        assumptions['fixed_monthly_eur'] + excess * rate if rate is not None else None)
    return {'status': 'projection_only', 'assumptions': assumptions,
            'projected_origin_body_gb_per_month': gb,
            'projected_monthly_eur': total,
            'within_proposed_budget': total <= assumptions['budget_eur'] if total is not None else None,
            'limits': 'Body bytes exclude HTTP/TCP/TLS overhead. Short runs do not measure TTL-expiry traffic or monthly bills. No current invoice or price evidence; no uncapped spend authorized.'}


def markdown(report):
    lines = ['# E3.4 local load rehearsal', '',
             f"Date: {report['date']}. Revision: `{report['git_revision']}`.", '',
             'This is a Docker cache-fixture observation. It does not establish Hetzner/Cloudflare capacity.', '',
             '| Scenario | Readers | Offered req/s | Completed req/s | p95 ms (scheduled) | 5xx | Cache HIT | Origin peak req/s | Origin CPU peak % | Origin body MB |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for scenario in report['scenarios']:
        c, o = scenario['client'], scenario['origin']
        errors = sum(n for status, n in c['status'].items() if int(status) >= 500) / max(c['sent'], 1)
        hit = c['cache'].get('HIT', 0) / max(c['completed'], 1)
        p95 = c['scheduled_response_p95_ms']
        cpu = o['cpu_peak_percent_of_quota']
        lines.append(f"| {scenario['name']} | {c['readers_served']} | {c['offered_rps']:.1f} | {c['achieved_rps']:.1f} | {p95:.1f} | {errors:.3%} | {hit:.2%} | {o['peak_one_second_rps']} | {cpu:.1f} | {o['body_bytes']/1e6:.2f} |")
    lines += ['', '## Evaluation', '']
    for s in report['scenarios']:
        failed = [name for name, value in s['checks'].items() if value['status'] == 'fail']
        missing = [name for name, value in s['checks'].items() if value['status'] == 'not_measured']
        lines.append(f"- {s['name']}: " + (', '.join(failed) + ' failed.' if failed else 'Measured checks pass.') +
                     (' Unmeasured: ' + ', '.join(missing) + ' (a warm cache can serve all work without origin requests).' if missing else ''))
    lines += ['', f"Cost: {report['cost']['status']}; projected origin body egress {report['cost']['projected_origin_body_gb_per_month']:.2f} GB/month, projected monthly EUR {report['cost']['projected_monthly_eur']}. Inputs are proposed assumptions, not invoices.", '',
              '## Limits and next action', '']
    lines.extend(f'- {limit}' for limit in report['limits'])
    return '\n'.join(lines) + '\n'
