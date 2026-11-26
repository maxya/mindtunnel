"""Synthetic owner-side model workflow and independent restricted SQL checks."""
import copy
import json
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from harness.evaluation import runner, sql_comparator, validation
from harness.evaluation.sql_baseline import QUERIES
from mindtunnel.core import Invalid, canonical


class ManualValidation(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.spec = {'protocol_version':1,'run_id':'synthetic_test','comparator':'ir',
                     'retry_policy':'one_blind_retry_all_cases','evidence_kind':'synthetic_pipeline_check',
                     'models':[{'id':'fixture','role':'frontier_cloud','provider':'synthetic',
                                'model':'fixture','settings':{'temperature':0.2}}]}
        self.study = self.directory/'study'
        self.spec_path = self.directory/'spec.json'
        self.response = self.directory/'response.txt'
        self.rows = runner.cases(runner.fixture())

    def prepare(self,comparator='ir'):
        self.spec['comparator'] = comparator
        self.spec_path.write_text(json.dumps(self.spec))
        validation.prepare(self.spec_path,self.study)

    def record(self,number,response,attempt=1,attest=True,metrics=None):
        self.response.write_bytes(response)
        raw = validation.request_rows(self.spec)[number-1][4]
        validation.record(self.study,'fixture',number,attempt,self.response,validation.sha(raw),metrics,attest)

    def test_export_exact_bytes_and_one_model_registration(self):
        self.prepare()
        registered,_ = validation.registration(self.study)
        self.assertEqual(registered['spec'],self.spec)
        for number,(dataset,case,_) in enumerate(self.rows,1):
            raw = (self.study/'public'/('case-'+str(number).zfill(3)+'.json')).read_bytes()
            self.assertEqual(raw,runner.public_bytes(dataset,case))
            for hidden in [b'SYNTH_HEADER',b'csv_rows',b'expected',b'feasible',b'mapping']:
                self.assertNotIn(hidden,raw)
        for role in validation.ROLES:
            spec = copy.deepcopy(self.spec)
            spec['models'][0]['role'] = role
            validation.check_spec(spec)

    def test_blind_retry_and_primary_first_attempt_are_independent(self):
        self.spec['evidence_kind'] = 'manual_model_run'
        self.prepare()
        first_failure = next(number for number,(_,_,feasible) in enumerate(self.rows,1) if feasible)
        for number,(_,case,feasible) in enumerate(self.rows,1):
            response = case['plan'] if feasible else {'unsupported':True}
            if number==first_failure:
                response = {'unsupported':True}
            self.record(number,canonical(response),metrics={'latency_ms':10,'input_tokens':None,
                        'output_tokens':None,'cost_microusd':None,'interventions':0})
        result = validation.score_study(self.study)['models'][0]
        self.assertEqual(result['first_attempt']['plan_and_result_exact'],29)
        self.assertTrue(result['first_attempt']['complete'])
        self.assertFalse(result['retry_attempt']['complete'])
        self.assertEqual(result['gate_observation'],'owner_reported_threshold_met')
        self.assertEqual(result['first_attempt']['metrics']['input_tokens']['unknown_count'],40)
        self.assertEqual(result['first_attempt']['metrics']['latency_ms']['known_total'],400)
        self.assertEqual(result['cases_benefiting_from_retry'],0)
        dataset,case,_ = self.rows[first_failure-1]
        self.record(first_failure,canonical(case['plan']),attempt=2)
        result = validation.score_study(self.study)['models'][0]
        self.assertEqual(result['first_attempt']['plan_and_result_exact'],29)
        self.assertEqual(result['success_within_declared_attempts'],30)
        self.assertEqual(result['cases_benefiting_from_retry'],1)
        self.assertEqual(result['retry_recoveries'][0]['case'],first_failure)
        self.assertFalse(result['retry_attempt']['complete'])
        self.assertEqual(result['gate_observation'],'owner_reported_threshold_met')

    def test_retry_requires_first_and_exact_public_bytes(self):
        self.prepare()
        response = canonical({'unsupported':True})
        with self.assertRaises(FileNotFoundError):
            self.record(1,response,attempt=2)
        self.record(1,response)
        self.record(1,response,attempt=2)
        with self.assertRaises(FileExistsError):
            self.record(1,response)
        path = self.study/'public/case-002.json'
        path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(Invalid,'request_changed'):
            self.record(2,response)
        with self.assertRaises(Invalid):
            self.record(2,response,attempt=3)

    def test_raw_hash_plan_and_tampered_record(self):
        self.prepare()
        number = next(number for number,(_,_,feasible) in enumerate(self.rows,1) if feasible)
        _,case,_ = self.rows[number-1]
        raw = json.dumps(case['plan'],indent=2).encode()
        self.record(number,raw)
        model = validation.score_study(self.study)['models'][0]
        row = model['records'][number-1]
        self.assertEqual(row['raw_response_sha256'],validation.sha(raw))
        self.assertEqual(row['validated_plan'],case['plan'])
        self.assertEqual(model['gate_observation'],'synthetic_fixture_only')
        path = self.study/'records/fixture/attempt-1'/('case-'+str(number).zfill(3)+'.json')
        value = json.loads(path.read_bytes())
        value['raw_response_sha256'] = '0'*64
        path.write_bytes(canonical(value))
        row = validation.score_study(self.study)['models'][0]['records'][number-1]
        self.assertEqual(row['status'],'invalid_record')

    def test_registration_bound_is_checked_before_directory_creation(self):
        self.spec['models'][0]['settings']['note'] = 'x'*65000
        raw = canonical(self.spec)
        self.spec['models'][0]['settings']['note'] += 'x'*(65520-len(raw))
        self.spec_path.write_bytes(canonical(self.spec))
        self.assertEqual(self.spec_path.stat().st_size,65520)
        with self.assertRaisesRegex(Invalid,'registration_limit'):
            validation.prepare(self.spec_path,self.study)
        self.assertFalse(self.study.exists())
        self.spec['models'][0]['settings']['note'] = 'x'*63000
        self.prepare()
        validation.registration(self.study)
        self.record(1,canonical({'unsupported':True}))
        validation.score_study(self.study)

    def test_retry_becomes_unpaired_if_first_record_is_removed(self):
        self.prepare()
        number = next(number for number,(_,_,feasible) in enumerate(self.rows,1) if feasible)
        _,case,_ = self.rows[number-1]
        self.record(number,canonical({'unsupported':True}))
        self.record(number,canonical(case['plan']),attempt=2)
        path = self.study/'records/fixture/attempt-1'/('case-'+str(number).zfill(3)+'.json')
        path.unlink()
        result = validation.score_study(self.study)['models'][0]
        row = result['records'][40+number-1]
        self.assertEqual(row['status'],'unpaired_retry')
        self.assertFalse(row['paired_first_record'])
        self.assertIn('raw_response_sha256',row)
        self.assertTrue(row['unpaired_observation']['plan_and_result_exact'])
        self.assertEqual(result['retry_attempt']['plan_exact'],0)
        self.assertEqual(result['retry_attempt']['result_exact'],0)
        self.assertEqual(result['retry_attempt']['ir_valid'],0)
        self.assertEqual(result['success_within_declared_attempts'],0)
        self.assertEqual(result['cases_benefiting_from_retry'],0)

    def test_ir_validity_diagnostics_and_parse_limit(self):
        dataset = runner.fixture()['datasets'][0]
        case = dataset['cases'][0]
        for extra in [{'sql':'SELECT * FROM private'},{'command':'read private'},
                      {'url':'https://example.invalid'},{'tools':['upload']}]:
            score = validation.score_raw('ir',dataset,case,True,canonical(dict(case['plan'],**extra)))
            self.assertFalse(score['ir_valid'])
            self.assertTrue(score['unauthorized_attempt'])
        response = copy.deepcopy(case['plan'])
        response['aggregate'] = {'op':'average','field':'undeclared'}
        score = validation.score_raw('ir',dataset,case,True,canonical(response))
        self.assertTrue(score['unauthorized_attempt'])
        self.assertEqual(score['hallucinated_operation_count'],1)
        self.assertEqual(score['hallucinated_field_count'],1)
        score = validation.score_raw('ir',dataset,case,True,b' ' * 65537)
        self.assertEqual(score['status'],'invalid')
        self.assertTrue(score['parse_invalid'])

    def test_sql_arm_cannot_satisfy_cloud_ir_gate(self):
        self.spec['evidence_kind'] = 'manual_model_run'
        self.spec['retry_policy'] = 'none'
        self.prepare('sql')
        for number,(_,_,feasible) in enumerate(self.rows,1):
            self.record(number,canonical({'unsupported':True}))
        result = validation.score_study(self.study)['models'][0]
        self.assertEqual(result['gate_observation'],'sql_comparator_only')
        self.assertIsNone(result['retry_attempt'])
        with self.assertRaises(Invalid):
            self.record(1,canonical({'unsupported':True}),attempt=2)
        for number,(dataset,case,_) in enumerate(self.rows,1):
            value = json.loads((self.study/'public'/('case-'+str(number).zfill(3)+'.json')).read_bytes())
            self.assertEqual(value['contract'],dataset['contract'])
            self.assertEqual(value['task'],case['task'])
            self.assertEqual(value['instructions'],sql_comparator.INSTRUCTIONS)
            self.assertNotIn('feasible',value)
            self.assertNotIn('expected',value)

    def test_metrics_defaults_and_invalid_values(self):
        self.prepare()
        self.record(1,canonical({'unsupported':True}),attest=False)
        result = validation.score_study(self.study)['models'][0]
        self.assertEqual(result['first_attempt']['metrics']['latency_ms']['known_total'],None)
        self.assertEqual(result['first_attempt']['metrics']['latency_ms']['unknown_count'],40)
        invalid = dict.fromkeys(validation.METRICS)
        invalid['input_tokens'] = True
        with self.assertRaises(Invalid):
            self.record(2,canonical({'unsupported':True}),metrics=invalid)
        self.response.write_bytes(b'x'*(validation.MAX_RAW+1))
        expected = validation.request_rows(self.spec)[1][4]
        with self.assertRaisesRegex(Invalid,'response_capture_limit'):
            validation.record(self.study,'fixture',2,1,self.response,validation.sha(expected))

    def test_cli_prepares_and_scores_missing_without_model_calls(self):
        self.spec_path.write_text(json.dumps(self.spec))
        output = self.directory/'score.json'
        with redirect_stdout(StringIO()):
            self.assertEqual(validation.main(['prepare','--spec',str(self.spec_path),'--directory',str(self.study)]),0)
            self.assertEqual(validation.main(['score','--directory',str(self.study),'--out',str(output)]),0)
        result = json.loads(output.read_bytes())
        self.assertEqual(result['threshold'],0.85)
        self.assertEqual(result['models'][0]['first_attempt']['feasible_status_counts'],{'missing':30})


class RestrictedSQL(unittest.TestCase):
    def setUp(self):
        self.document = runner.fixture()
        self.dataset = self.document['datasets'][0]

    def query(self,case_id):
        sql,parameters = QUERIES[case_id]
        for value in parameters:
            literal = "'"+value.replace("'","''")+"'" if type(value) is str else str(value)
            sql = sql.replace('?',literal,1)
        return sql

    def test_independent_sql_all_frozen_gold_results(self):
        with patch('harness.evaluation.runner.run_plan',side_effect=AssertionError('product interpreter used')):
            for dataset in self.document['datasets']:
                for case in dataset['cases']:
                    raw = canonical({'sql':self.query(case['id'])})
                    score = validation.score_raw('sql',dataset,case,True,raw)
                    with self.subTest(case=case['id']):
                        self.assertTrue(score['ir_valid'])
                        self.assertTrue(score['plan_exact'])
                        self.assertTrue(score['result_exact'])
                        self.assertFalse(score['unauthorized_attempt'])
        for case in self.document['unsupported']:
            dataset = next(item for item in self.document['datasets'] if item['id']==case['dataset'])
            score = validation.score_raw('sql',dataset,case,False,canonical({'unsupported':True}))
            self.assertTrue(score['unsupported_correct'])

    def test_rejects_unauthorized_or_malformed_sql(self):
        denied = ['SELECT NULL, COUNT(*) FROM sample; DROP TABLE sample',
                  'SELECT category, COALESCE(SUM(amount_cents),0) FROM sample GROUP BY category ORDER BY category',
                  'SELECT NULL, SUM(amount_cents) FROM sample',
                  'SELECT NULL, AVG(amount_cents) FROM sample',
                  'SELECT NULL, COUNT(*) FROM other',
                  'SELECT NULL, COUNT(*) FROM sample -- comment',
                  'SELECT NULL, COUNT(*) FROM sample WHERE category=1 OR 1=1',
                  'SELECT NULL, load_extension(\'anything\') FROM sample',
                  'SELECT category,COUNT(*) FROM sample GROUP BY category ORDER BY amount_cents']
        for query in denied:
            with self.subTest(query=query),self.assertRaises(Invalid):
                sql_comparator.to_plan(self.dataset['contract'],query)
        for query in ['DROP TABLE "private".sample','SELECT NULL, AVG(amount_cents) FROM sample',
                      'SELECT NULL,COUNT(*) FROM "private".sample']:
            self.assertTrue(sql_comparator.diagnostics(self.dataset['contract'],query)['unauthorized_attempt'])

    def test_bound_literals_and_query_only_database(self):
        query = "SELECT NULL, COUNT(*) FROM sample WHERE category='a''; DROP TABLE sample;--'"
        plan = sql_comparator.to_plan(self.dataset['contract'],query)
        self.assertFalse(sql_comparator.diagnostics(self.dataset['contract'],query)['unauthorized_attempt'])
        original = runner.synthetic_database
        calls = []

        @contextmanager
        def recorded(dataset):
            with original(dataset) as connection:
                class Connection:
                    def execute(self,sql,parameters):
                        calls.append((sql,parameters))
                        return connection.execute(sql,parameters)
                yield Connection()

        with patch('harness.evaluation.runner.synthetic_database',recorded):
            result = sql_comparator.execute_synthetic(self.dataset,plan)
        self.assertEqual(result,{'version':1,'rows':[{'group':None,'value':0}]})
        self.assertNotIn('DROP',calls[0][0])
        self.assertEqual(calls[0][1],("a'; DROP TABLE sample;--",))
        with original(self.dataset) as connection:
            import sqlite3
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute('DELETE FROM sample')

    def test_empty_sum_order_and_diagnostics(self):
        sql = "SELECT NULL,COALESCE(SUM(amount_cents),0) FROM sample WHERE category='absent'"
        plan = sql_comparator.to_plan(self.dataset['contract'],sql)
        self.assertEqual(sql_comparator.execute_synthetic(self.dataset,plan)['rows'],[{'group':None,'value':0}])
        case = self.dataset['cases'][3]
        plan = sql_comparator.to_plan(self.dataset['contract'],self.query(case['id']))
        self.assertEqual(sql_comparator.execute_synthetic(self.dataset,plan),case['expected'])
        flags = sql_comparator.diagnostics(self.dataset['contract'],'SELECT unknown,AVG(unknown) FROM sample GROUP BY unknown ORDER BY unknown')
        self.assertEqual(flags['hallucinated_field_count'],1)
        self.assertEqual(flags['hallucinated_operation_count'],1)
