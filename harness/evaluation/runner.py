"""Offline synthetic evaluation. SQL is restricted to reviewed local constants."""
import argparse
import base64
from collections import Counter
from contextlib import closing, contextmanager
import csv
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys
import tempfile
import time

from mindtunnel.core import (MAX_JSON, Invalid, canonical, contract_fields, execute,
                             parse, request, require, validate)
from mindtunnel.files import read_regular, write_private
from mindtunnel_planner.worker import generate
from .sql_baseline import QUERIES

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FROZEN_SHA256 = '054dd9272369591d82e7fe2bac8ca9a50e593f88f13ff33e974153b85aedb12b'


def fixture():
    raw = (HERE / 'heldout.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == FROZEN_SHA256, 'frozen_fixture_changed')
    return json.loads(raw)


def cases(document):
    rows = []
    datasets = {dataset['id']: dataset for dataset in document['datasets']}
    for dataset in datasets.values():
        for case in dataset['cases']:
            rows.append((dataset, case, True))
    for case in document['unsupported']:
        rows.append((datasets[case['dataset']], case, False))
    # Stable mixed ordering hides feasible/unsupported labels from exported filenames.
    return sorted(rows, key=lambda row: hashlib.sha256(row[1]['id'].encode()).digest())


def public_bytes(dataset, case):
    return (json.dumps(request(dataset['contract'], case['task']),
                       ensure_ascii=True, indent=2) + '\n').encode('utf-8')


@contextmanager
def csv_fixture(dataset):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory).resolve() / 'synthetic.csv'
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(dataset['csv_headers'])
            writer.writerows(dataset['csv_rows'])
        yield path


def run_plan(dataset, plan):
    with csv_fixture(dataset) as path:
        return execute(dataset['contract'], dataset['mapping'], plan, path)


@contextmanager
def synthetic_database(dataset):
    """Create a query-only in-memory database from the frozen synthetic fixture."""
    fields = contract_fields(dataset['contract'])
    columns = ','.join('"' + name + '" ' + ('TEXT' if kind == 'string' else 'INTEGER')
                       for name, kind in fields.items())
    indices = [dataset['csv_headers'].index(dataset['mapping'][name]) for name in fields]
    with closing(sqlite3.connect(':memory:')) as connection:
        connection.execute('CREATE TABLE sample (' + columns + ')')
        connection.executemany('INSERT INTO sample VALUES (' + ','.join('?' for _ in fields) + ')',
                               [tuple(row[index] for index in indices) for row in dataset['csv_rows']])
        connection.execute('PRAGMA query_only=ON')
        yield connection


def trusted_sql(dataset, case_id):
    """Run only analyst-authored constants against an ephemeral synthetic table."""
    with synthetic_database(dataset) as connection:
        sql, parameters = QUERIES[case_id]
        rows = connection.execute(sql, parameters).fetchall()
    return {'version':1, 'rows':[{'group':group, 'value':value} for group, value in rows]}


def score_response(dataset, case, feasible, raw):
    evidence = {'status':'missing', 'plan_exact':False, 'result_exact':False,
                'plan_and_result_exact':False, 'unsupported_correct':False}
    if raw is None:
        return evidence
    try:
        response = parse(raw)
        if type(response) is dict and set(response) == {'unsupported'}:
            require(response['unsupported'] is True, 'unsupported_response')
            evidence.update(status='unsupported', unsupported_correct=not feasible)
            return evidence
        validate(dataset['contract'], response)
    except (Invalid, UnicodeError, ValueError, TypeError, RecursionError):
        evidence['status'] = 'invalid'
        return evidence
    if not feasible:
        evidence['status'] = 'unexpected_plan'
        return evidence
    evidence['status'] = 'valid_plan'
    evidence['plan_exact'] = canonical(response) == canonical(case['plan'])
    try:
        evidence['result'] = run_plan(dataset, response)
    except (Invalid, OSError, UnicodeError, ValueError, TypeError, RecursionError):
        evidence['status'] = 'execution_failure'
        return evidence
    evidence['result_exact'] = evidence['result'] == case['expected']
    evidence['plan_and_result_exact'] = evidence['plan_exact'] and evidence['result_exact']
    return evidence


def summarize(records):
    feasible = [row for row in records if row['feasible']]
    unsupported = [row for row in records if not row['feasible']]
    return {'feasible_total':len(feasible), 'unsupported_total':len(unsupported),
            'feasible_status_counts':dict(Counter(row['score']['status'] for row in feasible)),
            'unsupported_status_counts':dict(Counter(row['score']['status'] for row in unsupported)),
            'plan_exact':sum(row['score']['plan_exact'] for row in feasible),
            'result_exact':sum(row['score']['result_exact'] for row in feasible),
            'plan_and_result_exact':sum(row['score']['plan_and_result_exact'] for row in feasible),
            'unsupported_correct':sum(row['score']['unsupported_correct'] for row in unsupported)}


def benchmark():
    document = fixture()
    records = []
    for dataset, case, feasible in cases(document):
        raw = public_bytes(dataset, case)
        record = {'id':case['id'], 'dataset':dataset['id'], 'feasible':feasible,
                  'request_utf8':raw.decode(), 'request_bytes':len(raw),
                  'request_sha256':hashlib.sha256(raw).hexdigest()}
        if feasible:
            started = time.perf_counter_ns()
            result = run_plan(dataset, case['plan'])
            record['gold'] = {'result':result, 'exact':result == case['expected'],
                              'elapsed_ns':time.perf_counter_ns()-started}
            started = time.perf_counter_ns()
            result = trusted_sql(dataset, case['id'])
            record['trusted_sql'] = {'result':result, 'exact':result == case['expected'],
                                     'elapsed_ns':time.perf_counter_ns()-started}
        envelope = {'request_base64':base64.b64encode(raw).decode(),
                    'destination':'mock://local', 'model':'synthetic-v1'}
        started = time.perf_counter_ns()
        response = generate(envelope)['response']
        record['mock_elapsed_ns'] = time.perf_counter_ns()-started
        record['mock_response'] = response
        record['score'] = score_response(dataset, case, feasible, canonical(response))
        records.append(record)
    vectors = json.loads((ROOT / 'tests/fixtures/conformance-v1.json').read_bytes())['invalid']
    invalid = []
    contract = document['datasets'][0]['contract']
    for case in vectors:
        error = None
        try:
            validate(contract, parse(case['raw']))
        except Invalid as caught:
            error = str(caught)
        invalid.append({'id':case['id'], 'rejected':error is not None,
                        'error':error, 'expected_error':case['error'], 'code_exact':error == case['error']})
    return {'format_version':1, 'fixture_sha256':FROZEN_SHA256,
            'sql_sha256':hashlib.sha256((HERE/'sql_baseline.py').read_bytes()).hexdigest(),
            'mock_worker_sha256':hashlib.sha256((ROOT/'mindtunnel_planner/worker.py').read_bytes()).hexdigest(),
            'conformance_sha256':hashlib.sha256((ROOT/'tests/fixtures/conformance-v1.json').read_bytes()).hexdigest(),
            'measured_at_unix':int(time.time()), 'python':platform.python_version(),
            'platform':platform.platform(), 'sqlite':sqlite3.sqlite_version,
            'mock_configuration':'unchanged synthetic-v1 grammar, direct pure-function invocation, no model/provider or isolation measurement',
            'timing_scope':'local monotonic nanoseconds; gold includes temporary CSV setup; SQL includes database setup; mock excludes scoring',
            'automated_run_interventions':0,
            'summary':dict(summarize(records),
                           gold_exact=sum(row.get('gold',{}).get('exact',False) for row in records),
                           sql_exact=sum(row.get('trusted_sql',{}).get('exact',False) for row in records),
                           adversarial_total=len(invalid), adversarial_rejected=sum(row['rejected'] for row in invalid)),
            'records':records, 'adversarial':invalid,
            'external_model_quality':'unmeasured', 'outside_testers':'not_run'}


def export_public(directory):
    directory = Path(directory)
    directory.mkdir(mode=0o700)
    index = []
    for number, (dataset, case, _) in enumerate(cases(fixture()), 1):
        raw = public_bytes(dataset, case)
        name = 'case-' + str(number).zfill(3) + '.json'
        write_private(directory/name, raw)
        index.append({'file':name, 'sha256':hashlib.sha256(raw).hexdigest(), 'bytes':len(raw)})
    write_private(directory/'index.json', canonical({'version':1, 'requests':index}) + b'\n')


def score_directory(directory, label):
    records = []
    directory = Path(directory)
    expected_names = set()
    for number, (dataset, case, feasible) in enumerate(cases(fixture()), 1):
        name = 'case-' + str(number).zfill(3) + '.json'
        expected_names.add(name)
        try:
            raw = read_regular(directory/name, MAX_JSON)
            score = score_response(dataset, case, feasible, raw)
        except FileNotFoundError:
            score = score_response(dataset, case, feasible, None)
        except (OSError, ValueError):
            score = {'status':'invalid', 'plan_exact':False, 'result_exact':False,
                     'plan_and_result_exact':False, 'unsupported_correct':False}
        records.append({'id':case['id'], 'response_file':name, 'feasible':feasible, 'score':score})
    extras = sum(path.name not in expected_names for path in directory.iterdir())
    return {'format_version':1, 'fixture_sha256':FROZEN_SHA256, 'label':label,
            'measured_at_unix':int(time.time()), 'summary':summarize(records),
            'extra_directory_entries':extras, 'records':records,
            'latency_cost_interventions':'unmeasured by import scorer'}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Offline synthetic evaluation only')
    commands = parser.add_subparsers(dest='command', required=True)
    run = commands.add_parser('run')
    run.add_argument('--out', required=True)
    export = commands.add_parser('export')
    export.add_argument('--directory', required=True)
    score = commands.add_parser('score')
    score.add_argument('--directory', required=True)
    score.add_argument('--label', required=True)
    score.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'export':
            export_public(args.directory)
        else:
            evidence = benchmark() if args.command == 'run' else score_directory(args.directory, args.label)
            write_private(args.out, (json.dumps(evidence, ensure_ascii=True, indent=2)+'\n').encode())
        print('Synthetic evaluation artifact written locally.')
        return 0
    except (OSError, ValueError, TypeError, UnicodeError, RecursionError):
        print('Rejected: evaluation_error', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
