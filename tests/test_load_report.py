"""E3.4 report contracts: missing evidence and overload cannot pass capacity targets."""
import importlib.util
import json
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('load_report', ROOT / 'ops/load/report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
runner_spec = importlib.util.spec_from_file_location('load_runner', ROOT / 'ops/load/run.py')
runner = importlib.util.module_from_spec(runner_spec)
with patch.dict(sys.modules, {'report': report}):
    runner_spec.loader.exec_module(runner)


class TestQuizLoadFixtures(unittest.TestCase):
    def test_complete_local_quiz_assets_are_required_and_deduplicated(self):
        html = '''<link href="../styles.css"><link href="../styles.css">
        <link href="https://external.invalid/unrelated.css">
        <script src="../quiz-data.123.js"></script>
        <script src="../quiz-engine.123.js"></script>
        <script src="../quiz-ui.123.js"></script>'''
        self.assertEqual(runner.quiz_resources(html, 'http://127.0.0.1:1234'),
                         ['/quiz-data.123.js', '/quiz-engine.123.js', '/quiz-ui.123.js', '/styles.css'])
        with self.assertRaises(ValueError):
            runner.quiz_resources('<p>Unavailable</p>', 'http://127.0.0.1:1234')
        with self.assertRaises(ValueError):
            runner.quiz_resources(html.replace('styles.css', 'styles.css?answer=fixture'),
                                  'http://127.0.0.1:1234')

    def test_isolated_origin_overrides_disabled_logs_with_numeric_observations(self):
        original = (ROOT / 'nginx/default.conf').read_text()
        fixture = runner.fixture_origin_config(original)
        self.assertIn('access_log /tmp/load-origin.log load_measure if=$load_request;', fixture)
        self.assertIn('log_format load_measure "$msec $status $request_time $body_bytes_sent";', fixture)
        self.assertIn('location = /__load_origin_ready { access_log off;', fixture)
        self.assertIn('error_log /dev/null;', fixture)
        self.assertEqual((ROOT / 'nginx/default.conf').read_text(), original)


class TestLoadReport(unittest.TestCase):
    def client(self):
        return {'sent': 10000, 'completed': 10000, 'dropped': 0, 'network_errors': 0,
                'readers': 10000, 'readers_served': 10000,
                'scheduled_response_p95_ms': 40, 'cache_hit_p95_ms': 20,
                'scheduling_lag_p95_ms': 5, 'status': {'200': 10000},
                'cache': {'HIT': 9900, 'MISS': 100},
                'classes': {'html': {'responses': 8000, 'hits': 7900},
                            'asset': {'responses': 2000, 'hits': 2000}}}

    def origin(self):
        return report.origin_metrics('1.1 200 0.002 1000\n1.2 200 0.003 1000\n2.2 200 0.010 1000',
                                     2, [{'cpu_percent_of_quota': 10, 'memory_bytes': 10_000_000}])

    def test_origin_load_and_bytes_use_independent_numeric_observations(self):
        metrics = self.origin()
        self.assertEqual(metrics['requests'], 3)
        self.assertEqual(metrics['rps'], 1.5)
        self.assertEqual(metrics['peak_one_second_rps'], 2)
        self.assertEqual(metrics['response_p95_ms'], 10)
        self.assertEqual(metrics['body_bytes'], 3000)
        self.assertEqual(metrics['memory_peak_bytes'], 10_000_000)

    def test_threshold_boundaries_and_stricter_origin_limit(self):
        client, origin = self.client(), self.origin()
        self.assertTrue(all(c['status'] == 'pass' for c in report.evaluate(client, origin, 'steady').values()))
        client['scheduled_response_p95_ms'] = 150
        origin['peak_one_second_rps'] = 201
        checks = report.evaluate(client, origin, 'steady')
        self.assertEqual(checks['edge_scheduled_p95_ms']['status'], 'fail')
        self.assertEqual(checks['origin_peak_one_second_rps']['status'], 'fail')
        self.assertEqual(report.evaluate(client, origin, 'burst')['edge_scheduled_p95_ms']['status'], 'pass')

    def test_missing_cache_cpu_and_origin_latency_are_not_success(self):
        client, origin = self.client(), report.origin_metrics('', 2, [])
        client['cache']['UNKNOWN'] = 1
        client['classes']['asset']['unknown'] = 1
        checks = report.evaluate(client, origin, 'steady')
        for key in ('aggregate_hit_ratio', 'asset_hit_ratio', 'origin_p95_ms', 'origin_cpu_peak_percent_of_quota'):
            self.assertEqual(checks[key]['status'], 'not_measured')

    def test_network_failures_drops_and_reader_shortfall_cannot_pass(self):
        client = self.client()
        client.update(network_errors=1, dropped=1, readers_served=9999, scheduling_lag_p95_ms=101)
        checks = report.evaluate(client, self.origin(), 'steady')
        for key in ('network_errors', 'dropped_requests', 'all_readers_served', 'generator_scheduling_lag_p95_ms'):
            self.assertEqual(checks[key]['status'], 'fail')

    def test_cost_projection_does_not_turn_unknown_overage_into_zero_cost(self):
        assumptions = {'fixed_monthly_eur': 16, 'included_origin_egress_gb': 1,
                       'egress_eur_per_gb': None, 'monthly_scenario_hours': {'steady': 1}, 'budget_eur': 50}
        data = [{'name': 'steady', 'origin': {'body_bytes': 10**9}, 'client': {'measurement_seconds': 1}}]
        cost = report.project_cost(data, assumptions)
        self.assertEqual(cost['status'], 'projection_only')
        self.assertIsNone(cost['projected_monthly_eur'])
        self.assertIsNone(cost['within_proposed_budget'])
        assumptions['egress_eur_per_gb'] = 1
        self.assertGreater(report.project_cost(data, assumptions)['projected_monthly_eur'], 50)
        assumptions.update(included_origin_egress_gb=5000, egress_eur_per_gb=None)
        self.assertEqual(report.project_cost(data, assumptions)['projected_monthly_eur'], 16)

    def test_plan_models_readers_in_all_required_scenarios(self):
        plan = json.loads((ROOT / 'ops/load/plan.json').read_text())
        self.assertEqual(plan['readers'], 10000)
        self.assertEqual(plan['think_seconds'], [5, 10])
        self.assertEqual([s['name'] for s in plan['scenarios']], ['steady', 'cold-cache', 'burst'])
        self.assertTrue(plan['scenarios'][1]['cold_cache'])
        self.assertFalse(plan['scenarios'][0]['cold_cache'])
