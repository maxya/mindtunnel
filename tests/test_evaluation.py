"""Offline benchmark reproducibility and future public-response scoring checks."""
import copy
import hashlib
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from harness.evaluation import runner
from mindtunnel.cli import main as cli_main
from mindtunnel.core import canonical

ROOT = Path(__file__).resolve().parents[1]


class Evaluation(unittest.TestCase):
    def setUp(self):
        self.document = runner.fixture()
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()

    def test_frozen_fixture_and_offline_comparators(self):
        raw = (ROOT/'harness/evaluation/heldout.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), runner.FROZEN_SHA256)
        result = runner.benchmark()
        summary = result['summary']
        self.assertEqual(summary['feasible_total'], 30)
        self.assertEqual(summary['unsupported_total'], 10)
        self.assertEqual(summary['gold_exact'], 30)
        self.assertEqual(summary['sql_exact'], 30)
        self.assertEqual(summary['adversarial_total'], 53)
        self.assertEqual(summary['adversarial_rejected'], 53)
        self.assertTrue(all(row['code_exact'] for row in result['adversarial']))
        # The unchanged narrow mock grammar refuses these natural-language tasks.
        self.assertEqual(summary['plan_and_result_exact'], 0)
        self.assertEqual(summary['feasible_status_counts'], {'unsupported':30})
        self.assertEqual(summary['unsupported_correct'], 10)
        self.assertEqual(result['external_model_quality'], 'unmeasured')
        for row in result['records']:
            self.assertGreaterEqual(row['mock_elapsed_ns'], 0)
            self.assertEqual(len(row['request_utf8'].encode()), row['request_bytes'])

    def test_export_is_public_cli_bytes_without_labels(self):
        public = self.directory/'public'
        runner.export_public(public)
        self.assertEqual(len(list(public.glob('case-*.json'))), 40)
        for number, (dataset, case, _) in enumerate(runner.cases(self.document), 1):
            raw = (public/('case-'+str(number).zfill(3)+'.json')).read_bytes()
            self.assertEqual(raw, runner.public_bytes(dataset, case))
            value = json.loads(raw)
            self.assertEqual(set(value), {'version','contract','contract_sha256','task','instructions'})
            for canary in ['SYNTH_HEADER', 'csv_rows', 'expected', 'mapping', 'feasible']:
                self.assertNotIn(canary, raw.decode())
        dataset, case, _ = runner.cases(self.document)[0]
        contract = self.directory/'contract.json'
        contract.write_text(json.dumps(dataset['contract']))
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(cli_main(['request','--contract',str(contract),'--task',case['task']]), 0)
        self.assertEqual(stdout.getvalue().encode(), runner.public_bytes(dataset, case))

    def test_import_gold_missing_invalid_and_unsupported(self):
        responses = self.directory/'responses'
        responses.mkdir()
        rows = runner.cases(self.document)
        for number, (_, case, feasible) in enumerate(rows, 1):
            response = case['plan'] if feasible else {'unsupported':True}
            (responses/('case-'+str(number).zfill(3)+'.json')).write_bytes(canonical(response))
        evidence = runner.score_directory(responses, 'synthetic gold import')
        self.assertEqual(evidence['summary']['plan_and_result_exact'], 30)
        self.assertEqual(evidence['summary']['unsupported_correct'], 10)
        self.assertEqual(evidence['extra_directory_entries'], 0)
        (responses/'case-001.json').unlink()
        (responses/'case-002.json').write_bytes(b'{"unsupported":false}')
        (responses/'case-003.json').write_bytes(b' ' * 65537)
        (responses/'extra.json').write_text('{}')
        evidence = runner.score_directory(responses, 'negative synthetic import')
        self.assertEqual(evidence['records'][0]['score']['status'], 'missing')
        self.assertEqual(evidence['records'][1]['score']['status'], 'invalid')
        self.assertEqual(evidence['records'][2]['score']['status'], 'invalid')
        self.assertEqual(evidence['extra_directory_entries'], 1)

    def test_export_and_score_cli_entry_points(self):
        public = self.directory/'public'
        responses = self.directory/'responses'
        responses.mkdir()
        score_file = self.directory/'score.json'
        with redirect_stdout(StringIO()):
            self.assertEqual(runner.main(['export','--directory',str(public)]), 0)
            self.assertEqual(runner.main(['score','--directory',str(responses),
                                         '--label','synthetic missing responses','--out',str(score_file)]), 0)
        summary = json.loads(score_file.read_bytes())['summary']
        self.assertEqual(summary['feasible_status_counts'], {'missing':30})
        self.assertEqual(summary['unsupported_status_counts'], {'missing':10})

    def test_plan_equivalence_is_separate_from_fixture_result_match(self):
        dataset = self.document['datasets'][0]
        case = dataset['cases'][9]
        response = copy.deepcopy(case['plan'])
        response['filter']['eq'] = 'missing'
        score = runner.score_response(dataset, case, True, canonical(response))
        self.assertEqual(score['status'], 'valid_plan')
        self.assertFalse(score['plan_exact'])
        self.assertTrue(score['result_exact'])
        self.assertFalse(score['plan_and_result_exact'])

    def test_execution_failures_are_distinct_from_invalid_plans(self):
        from unittest.mock import patch
        from mindtunnel.core import Invalid
        dataset = self.document['datasets'][0]
        case = dataset['cases'][0]
        with patch('harness.evaluation.runner.run_plan', side_effect=Invalid('synthetic_failure')):
            score = runner.score_response(dataset, case, True, canonical(case['plan']))
        self.assertEqual(score['status'], 'execution_failure')
        self.assertTrue(score['plan_exact'])
        self.assertFalse(score['result_exact'])
        self.assertNotIn('synthetic_failure', json.dumps(score))

    def test_malformed_or_code_responses_never_become_sql(self):
        dataset = self.document['datasets'][0]
        case = dataset['cases'][0]
        for raw in [b'{"sql":"DELETE FROM sample"}', b'{"unsupported":1}',
                    b'{"unsupported":true,"result":"SYNTHETIC_CANARY"}',
                    b'{"version":1,"version":1}', b'```json\n{}\n```', b'\xff']:
            score = runner.score_response(dataset, case, True, raw)
            self.assertEqual(score['status'], 'invalid')
        self.assertEqual(runner.trusted_sql(dataset, case['id']), case['expected'])
