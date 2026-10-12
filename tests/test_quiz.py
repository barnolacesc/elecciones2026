"""Quiz authoring/build boundaries. All test data is explicitly fictional."""
from copy import deepcopy
from dataclasses import asdict, replace
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from elecciones2026.generator import build_site, BuildValidationError, load_and_validate_site_data
from elecciones2026.quiz import prepare_quiz, QuizValidationError, safe_url, dual_review, resolve_source
from elecciones2026.schemas import ReviewRecord, StatementRecord

ROOT = Path(__file__).resolve().parent.parent


class QuizBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = load_and_validate_site_data(ROOT)
        cls.raw = json.loads((ROOT / "content/quiz/mock.json").read_text())

    def prepare(self, raw, mock=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quiz.json"
            path.write_text(json.dumps(raw))
            return prepare_quiz(path, self.ctx, mock=mock)

    def test_mock_is_isolated_balanced_and_gap_is_not_opposition(self):
        bundle = self.prepare(self.raw)
        self.assertEqual(bundle['election_id'], 'quiz-fixture')
        self.assertTrue(bundle['available'])
        self.assertEqual(sum(p['eligible'] for p in bundle['parties']), 2)
        self.assertIsNone(bundle['parties'][2]['positions'][3]['value'])
        self.assertTrue(all(p['source'] is None for party in bundle['parties'] for p in party['positions']))

    def test_mock_never_enters_reviewed_mode(self):
        with self.assertRaisesRegex(QuizValidationError, 'election/mode mismatch'):
            self.prepare(self.raw, mock=False)

    def test_bad_taxonomy_and_versions_fail(self):
        for field in ('schema_version', 'method_version', 'taxonomy_version', 'election_id'):
            raw = deepcopy(self.raw); raw[field] = 'wrong'
            with self.subTest(field=field), self.assertRaises(QuizValidationError):
                self.prepare(raw)

    def test_duplicate_or_missing_items_and_measures_fail(self):
        for alteration in ('missing', 'item', 'measure', 'quota'):
            raw = deepcopy(self.raw)
            if alteration == 'missing': raw['items'].pop()
            if alteration == 'item': raw['items'][1]['id'] = raw['items'][0]['id']
            if alteration == 'measure': raw['items'][1]['measure_id'] = raw['items'][0]['measure_id']
            if alteration == 'quota': raw['items'][1]['topic_id'] = 'education'
            with self.subTest(alteration=alteration), self.assertRaises(QuizValidationError):
                self.prepare(raw)

    def test_position_status_value_and_identity_fail_closed(self):
        for value in (0, True, 0.5, None, '1'):
            raw = deepcopy(self.raw); raw['parties'][0]['positions'][0]['value'] = value
            with self.subTest(value=value), self.assertRaises(QuizValidationError):
                self.prepare(raw)
        raw = deepcopy(self.raw); raw['parties'][0]['positions'][1]['item_id'] = 'unknown'
        with self.assertRaises(QuizValidationError): self.prepare(raw)

    def test_each_gap_state_keeps_a_party_visible_without_numeric_imputation(self):
        for status in ('missing', 'partial', 'conflicting', 'unverified', 'replaced'):
            raw = deepcopy(self.raw)
            raw['parties'][2]['positions'][3]['status'] = status
            with self.subTest(status=status):
                bundle = self.prepare(raw)
                self.assertEqual(len(bundle['parties']), 3)
                self.assertFalse(bundle['parties'][2]['eligible'])
                self.assertIsNone(bundle['parties'][2]['positions'][3]['value'])
        raw = deepcopy(self.raw); raw['parties'][2]['positions'][3]['value'] = -1
        with self.assertRaises(QuizValidationError): self.prepare(raw)

    def test_missing_two_complete_parties_makes_set_unavailable(self):
        raw = deepcopy(self.raw)
        raw['parties'][1]['positions'][0] = {'item_id': raw['items'][0]['id'],
            'status': 'conflicting', 'value': None, 'reason': 'Conflicting test data.'}
        self.assertFalse(self.prepare(raw)['available'])

    def test_fake_or_incomplete_reviews_fail(self):
        for raw in ({'review_status': 'draft'}, {'review_status': 'approved', 'reviews': []},
                    {'review_status': 'approved', 'reviews': [{'reviewer_id': 'fixture'}]}):
            with self.assertRaises(QuizValidationError): dual_review(raw)

    def test_unsafe_citation_urls_fail(self):
        for url in ('javascript:alert(1)', 'http://example.invalid/', 'https://user:pass@example.invalid/', '/source'):
            with self.assertRaises(QuizValidationError): safe_url(url)
        self.assertEqual(safe_url('https://example.invalid/programme#page=2'), 'https://example.invalid/programme#page=2')

    def test_default_build_has_no_mock_data_or_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)/'site'; build_site(ROOT, out)
            page = (out/'cuestionario/index.html').read_text()
            self.assertIn('aún no está disponible', page)
            self.assertNotIn('Ejemplo A', page)
            self.assertFalse(list(out.glob('quiz-data.*')))
            self.assertNotIn('/cuestionario/', (out/'sitemap.xml').read_text())

    def test_mock_build_is_deterministic_fingerprinted_and_noindex(self):
        with tempfile.TemporaryDirectory() as directory:
            first = build_site(ROOT, Path(directory)/'one', quiz_mode='mock')
            second = build_site(ROOT, Path(directory)/'two', quiz_mode='mock')
            self.assertEqual(first.file_hashes, second.file_hashes)
            page = (first.output_dir/'cuestionario/index.html').read_text()
            self.assertIn('datos ficticios', page)
            self.assertIn('noindex, nofollow', page)
            self.assertIn('no-referrer', page)
            self.assertIn('Ejemplo C (ficticio)', page)
            self.assertNotIn('/cuestionario/', (first.output_dir/'sitemap.xml').read_text())
            self.assertLess(page.index('quiz-data.'), page.index('quiz-engine.'))
            self.assertLess(page.index('quiz-engine.'), page.index('quiz-ui.'))
            self.assertEqual(len(list(first.output_dir.glob('quiz-data.*.js'))), 1)

    def test_invalid_input_leaves_no_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory)/'invalid.json'; invalid.write_text('{}')
            out = Path(directory)/'site'
            with self.assertRaises(BuildValidationError):
                build_site(ROOT, out, quiz_mode='mock', quiz_file=invalid)
            self.assertFalse(out.exists())
            with self.assertRaises(BuildValidationError):
                build_site(ROOT, out, quiz_mode='reviewed', quiz_file=ROOT/'content/quiz/mock.json')
            self.assertFalse(out.exists())

    def test_default_rebuild_withdraws_previous_mock_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)/'site'
            build_site(ROOT, out, quiz_mode='mock')
            self.assertTrue(list(out.glob('quiz-data.*.js')))
            build_site(ROOT, out)
            self.assertFalse(list(out.glob('quiz-data.*.js')))
            self.assertIn('aún no está disponible', (out/'cuestionario/index.html').read_text())


class SourceGateTests(unittest.TestCase):
    """Synthetic metadata only; these objects do not assert actual human approvals."""

    def setUp(self):
        today = date.today().isoformat()
        reviews = [ReviewRecord(f'qa-human-{letter}', today, 'approved',
            'Synthetic test-only record, not editorial evidence.', 'human', 'test-only/evidence') for letter in ('a', 'b')]
        self.statement = StatementRecord('1.0.0', 'test-election', 'test-statement', 'test-party',
            'housing', 'test-subtopic', 'explicit_proposal', 'Numeric fixture only.', 'approved',
            programme_id='test-programme', source_url='https://example.invalid/source',
            source_version='1.0.0', source_page='1', reviews=reviews, last_reviewed_date=today)
        self.source = SimpleNamespace(party_id='test-party', election_id='test-election',
            version='1.0.0', official_url=self.statement.source_url, direct_url=None, status='verified',
            sha256='a'*64, publication_date=today, rights_review=SimpleNamespace(
                status='link_and_short_quote', reviewed_by='qa-rights-human', review_date=today))
        self.ctx = SimpleNamespace(election_id='test-election', statements={'test-statement': self.statement},
            register=SimpleNamespace(sources=[self.source]), corrections=[])
        self.programmes = {'test-programme': {'election_id': 'test-election', 'candidacy_id': 'test-party',
            'version': '1.0.0', 'sha256': 'a'*64, 'status': 'official',
            'rights_status': 'verified_quotation_permitted', 'is_fixture': False, 'publication_date': today}}
        self.mapping = {'statement_id': 'test-statement', 'review_status': 'approved',
            'reviews': [asdict(r) for r in reviews]}

    def resolve(self):
        return resolve_source(self.mapping, {'topic_id': 'housing'}, {'id': 'test-party'}, self.ctx, self.programmes)

    def test_validated_source_trace_strips_private_reviewer_details(self):
        result = self.resolve()
        self.assertEqual(result['sha256'], 'a'*64)
        self.assertEqual(result['page'], '1')
        self.assertNotIn('qa-human', json.dumps(result))
        self.assertNotIn('evidence', json.dumps(result))

    def test_unreviewed_and_uncited_statements_fail(self):
        for change in ({'review_status': 'draft'}, {'is_fixture': True}, {'source_url': None},
                       {'source_page': None}, {'election_id': 'different-election'}, {'reviews': []}):
            self.ctx.statements['test-statement'] = replace(self.statement, **change)
            with self.subTest(change=change), self.assertRaises(QuizValidationError): self.resolve()

    def test_programme_source_and_rights_fail_closed(self):
        for status in ('missing', 'partial', 'published-unverified', 'replaced'):
            self.source.status = status
            with self.subTest(status=status), self.assertRaises(QuizValidationError): self.resolve()
        self.source.status = 'verified'
        self.source.rights_review.status = 'not_reviewed'
        with self.assertRaises(QuizValidationError): self.resolve()
        self.source.rights_review.status = 'link_and_short_quote'
        self.programmes['test-programme']['sha256'] = 'b'*64
        with self.assertRaises(QuizValidationError): self.resolve()

    def test_correction_requires_review_of_the_corrected_version(self):
        self.ctx.corrections = [SimpleNamespace(target_type='statement', target_id='test-statement',
            id='test-correction', correction_date=date.today().isoformat())]
        with self.assertRaisesRegex(QuizValidationError, 'fresh review'): self.resolve()
        self.ctx.statements['test-statement'] = replace(self.statement, correction_id='test-correction')
        self.assertEqual(self.resolve()['statement_id'], 'test-statement')


if __name__ == '__main__': unittest.main()
