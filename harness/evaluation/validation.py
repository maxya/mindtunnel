"""Owner-side manual model comparison. This module has no model transport."""
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
import time

from mindtunnel.arguments import LocalArgumentParser
from mindtunnel.core import ID, MAX_JSON, Invalid, canonical, keys, pairs, parse, require, validate, valid_text
from mindtunnel.files import read_regular, write_private
from . import runner, sql_comparator

MAX_RAW = 1024 * 1024
MAX_RECORD = 2 * 1024 * 1024
METRICS = ('latency_ms','input_tokens','output_tokens','cost_microusd','interventions')
ROLES = {'frontier_cloud','small_cloud','local'}
FORBIDDEN_KEYS = {'command','shell','code','python','url','path','paths','file','files','tools','callback','network'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def config_json(path):
    raw = read_regular(path, MAX_JSON)
    require(len(raw) <= MAX_JSON, 'config_limit')
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs)
    # Canonical serialization rejects nonfinite numbers while allowing model settings such as 0.2.
    canonical(value)
    return value


def check_spec(spec):
    keys(spec, ('protocol_version','run_id','comparator','retry_policy','evidence_kind','models'), 'spec_keys')
    require(type(spec['protocol_version']) is int and spec['protocol_version'] == 1, 'spec_version')
    require(type(spec['run_id']) is str and ID.fullmatch(spec['run_id']), 'run_id')
    require(spec['comparator'] in ('ir','sql'), 'comparator')
    require(spec['retry_policy'] in ('none','one_blind_retry_all_cases'), 'retry_policy')
    require(spec['evidence_kind'] in ('manual_model_run','synthetic_pipeline_check'), 'evidence_kind')
    require(type(spec['models']) is list and 1 <= len(spec['models']) <= 12, 'models')
    seen = set()
    for model in spec['models']:
        keys(model, ('id','role','provider','model','settings'), 'model_keys')
        identifier = model['id']
        require(type(identifier) is str and ID.fullmatch(identifier) and identifier not in seen, 'model_id')
        require(type(model['role']) is str and model['role'] in ROLES, 'model_role')
        require(all(valid_text(model[key],200) and model[key].strip() for key in ('provider','model')), 'model_identity')
        require(type(model['settings']) is dict, 'model_settings')
        canonical(model['settings'])
        seen.add(identifier)
    return spec


def attempts(spec):
    return 2 if spec['retry_policy'] == 'one_blind_retry_all_cases' else 1


def request_rows(spec):
    rows = []
    for number, (dataset, case, feasible) in enumerate(runner.cases(runner.fixture()),1):
        if spec['comparator'] == 'ir':
            raw = runner.public_bytes(dataset,case)
        else:
            value = sql_comparator.public_request(dataset['contract'],case['task'])
            raw = (json.dumps(value,ensure_ascii=True,indent=2)+'\n').encode()
        rows.append((number,dataset,case,feasible,raw))
    return rows


def request_index(rows):
    return [{'file':'case-'+str(number).zfill(3)+'.json','bytes':len(raw),'sha256':sha(raw)}
            for number,_,_,_,raw in rows]


def prepare(spec_path, directory):
    spec = check_spec(config_json(spec_path))
    rows = request_rows(spec)
    index = request_index(rows)
    registered = {'version':1,'registered_at_unix':int(time.time()),'spec':spec,
                  'fixture_sha256':runner.FROZEN_SHA256,'request_set_sha256':sha(canonical(index))}
    registration_bytes = canonical(registered)+b'\n'
    require(len(registration_bytes)<=MAX_JSON,'registration_limit')
    directory = Path(directory)
    directory.mkdir(mode=0o700)
    public = directory/'public'
    public.mkdir(mode=0o700)
    for entry, row in zip(index,rows):
        write_private(public/entry['file'],row[4])
    write_private(public/'index.json',canonical({'version':1,'requests':index})+b'\n')
    write_private(directory/'registration.json',registration_bytes)
    for model in spec['models']:
        for attempt in range(1,attempts(spec)+1):
            (directory/'records'/model['id']/('attempt-'+str(attempt))).mkdir(parents=True,mode=0o700)


def registration(directory):
    raw = read_regular(Path(directory)/'registration.json',MAX_JSON)
    require(len(raw)<=MAX_JSON,'registration_limit')
    value = json.loads(raw.decode('utf-8'),object_pairs_hook=pairs)
    canonical(value)
    keys(value,('version','registered_at_unix','spec','fixture_sha256','request_set_sha256'),'registration_keys')
    require(type(value['version']) is int and value['version']==1,'registration_version')
    spec = check_spec(value['spec'])
    require(value['fixture_sha256']==runner.FROZEN_SHA256,'fixture_changed')
    require(value['request_set_sha256']==sha(canonical(request_index(request_rows(spec)))),'request_set_changed')
    return value,sha(raw)


def check_metrics(value):
    keys(value,METRICS,'metrics_keys')
    require(all(item is None or type(item) is int and 0 <= item <= 10**15 for item in value.values()),'metrics_value')
    return value


def record(directory, model_id, case_number, attempt, response_path, request_sha256,
           metrics=None, attest=False):
    registered, registration_hash = registration(directory)
    spec = registered['spec']
    require(model_id in {model['id'] for model in spec['models']},'model_id')
    require(type(case_number) is int and 1 <= case_number <= 40,'case_number')
    require(type(attempt) is int and 1 <= attempt <= attempts(spec),'attempt')
    require(type(attest) is bool,'attestation')
    row = request_rows(spec)[case_number-1]
    expected = row[4]
    name = 'case-'+str(case_number).zfill(3)+'.json'
    actual = read_regular(Path(directory)/'public'/name,MAX_JSON)
    require(actual==expected and request_sha256==sha(expected),'request_changed')
    raw = read_regular(response_path,MAX_RAW)
    require(len(raw)<=MAX_RAW,'response_capture_limit')
    if attempt == 2:
        first = Path(directory)/'records'/model_id/'attempt-1'/name
        read_record(first,registration_hash,model_id,case_number,1,expected)
    metadata = check_metrics(dict.fromkeys(METRICS) if metrics is None else metrics)
    value = {'version':1,'registration_sha256':registration_hash,'model_id':model_id,
             'case':case_number,'attempt':attempt,'request_sha256':sha(expected),
             'raw_response_base64':base64.b64encode(raw).decode(),
             'raw_response_sha256':sha(raw),'raw_response_bytes':len(raw),
             'metrics':metadata,'same_bytes_blind_attested':attest}
    target = Path(directory)/'records'/model_id/('attempt-'+str(attempt))/name
    write_private(target,canonical(value)+b'\n')


def inspect_ir(contract, response, allow_sql=False):
    result = {'unauthorized_attempt':False,'hallucinated_field_count':0,'hallucinated_operation_count':0}
    if type(response) is not dict:
        return result
    forbidden = FORBIDDEN_KEYS if allow_sql else FORBIDDEN_KEYS | {'sql'}
    stack = [response]
    while stack:
        value = stack.pop()
        if type(value) is dict:
            result['unauthorized_attempt'] |= bool(set(value)&forbidden)
            stack.extend(value.values())
        elif type(value) is list:
            stack.extend(value)
    references = [response.get('group_by')]
    aggregate = response.get('aggregate')
    if type(aggregate) is dict:
        references.append(aggregate.get('field'))
        operation = aggregate.get('op')
        if type(operation) is str and operation not in ('count','sum'):
            result['hallucinated_operation_count'] = 1
            result['unauthorized_attempt'] = True
    predicate = response.get('filter')
    if type(predicate) is dict:
        references.append(predicate.get('field'))
    aliases = {field['id'] for field in contract['fields']}
    result['hallucinated_field_count'] = len({field for field in references if type(field) is str and field not in aliases})
    return result


def score_raw(comparator,dataset,case,feasible,raw):
    score = {'status':'invalid','ir_valid':False,'plan_exact':False,'result_exact':False,
             'plan_and_result_exact':False,'unsupported_correct':False,
             'unauthorized_attempt':False,'hallucinated_field_count':0,'hallucinated_operation_count':0}
    try:
        response = parse(raw)
    except (Invalid,ValueError,TypeError,UnicodeError,RecursionError):
        score['parse_invalid'] = True
        return score
    score.update(inspect_ir(dataset['contract'],response,allow_sql=comparator=='sql'))
    if comparator == 'sql' and type(response) is dict and 'sql' in response:
        diagnostic = sql_comparator.diagnostics(dataset['contract'],response['sql'])
        score['unauthorized_attempt'] |= diagnostic['unauthorized_attempt']
        score['hallucinated_field_count'] += diagnostic['hallucinated_field_count']
        score['hallucinated_operation_count'] += diagnostic['hallucinated_operation_count']
        if diagnostic.get('syntax_rejected'):
            score['syntax_rejected'] = True
    if type(response) is dict and set(response)=={'unsupported'} and response['unsupported'] is True:
        score.update(status='unsupported',unsupported_correct=not feasible)
        return score
    try:
        if comparator == 'sql':
            keys(response,('sql',),'sql_response')
            plan = sql_comparator.to_plan(dataset['contract'],response['sql'])
        else:
            plan = response
            validate(dataset['contract'],plan)
    except (Invalid,ValueError,TypeError,UnicodeError,RecursionError):
        return score
    score.update(status='valid_plan' if feasible else 'unexpected_plan',ir_valid=True,validated_plan=plan)
    if not feasible:
        return score
    score['plan_exact'] = canonical(plan)==canonical(case['plan'])
    try:
        score['result'] = (sql_comparator.execute_synthetic(dataset,plan) if comparator=='sql'
                           else runner.run_plan(dataset,plan))
    except (Invalid,OSError,ValueError,TypeError,UnicodeError,RecursionError,sqlite3.Error):
        score['status'] = 'execution_failure'
        return score
    score['result_exact'] = score['result']==case['expected']
    score['plan_and_result_exact'] = score['plan_exact'] and score['result_exact']
    return score


def read_record(path,registration_hash,model_id,number,attempt,expected):
    value = parse(read_regular(path,MAX_RECORD),limit=MAX_RECORD)
    keys(value,('version','registration_sha256','model_id','case','attempt','request_sha256',
                'raw_response_base64','raw_response_sha256','raw_response_bytes','metrics','same_bytes_blind_attested'),'record_keys')
    bindings = {'version':1,'registration_sha256':registration_hash,'model_id':model_id,
                'case':number,'attempt':attempt,'request_sha256':sha(expected)}
    require(all(type(value[key]) is type(item) and value[key]==item for key,item in bindings.items()),'record_binding')
    require(type(value['same_bytes_blind_attested']) is bool,'attestation')
    check_metrics(value['metrics'])
    raw = base64.b64decode(value['raw_response_base64'],validate=True)
    require(len(raw)<=MAX_RAW and type(value['raw_response_bytes']) is int and len(raw)==value['raw_response_bytes']
            and sha(raw)==value['raw_response_sha256'],'response_changed')
    return value,raw


def metric_summary(rows):
    summary = {}
    for name in METRICS:
        values = [row['metrics'][name] for row in rows if row.get('metrics',{}).get(name) is not None]
        summary[name] = {'known_count':len(values),'unknown_count':len(rows)-len(values),
                         'known_total':sum(values) if values else None,
                         'known_mean':sum(values)/len(values) if values else None}
    return summary


def score_study(directory):
    registered, registration_hash = registration(directory)
    spec = registered['spec']
    rows = request_rows(spec)
    models = []
    for model in spec['models']:
        records = []
        for attempt in range(1,attempts(spec)+1):
            for number,dataset,case,feasible,expected in rows:
                row = {'case':number,'attempt':attempt,'feasible':feasible,'id':case['id'],
                       'status':'missing','metrics':dict.fromkeys(METRICS),'same_bytes_blind_attested':False,
                       'ir_valid':False,'plan_exact':False,'result_exact':False,'plan_and_result_exact':False,
                       'unsupported_correct':False,'unauthorized_attempt':False,
                       'hallucinated_field_count':0,'hallucinated_operation_count':0}
                path = Path(directory)/'records'/model['id']/('attempt-'+str(attempt))/('case-'+str(number).zfill(3)+'.json')
                try:
                    value,raw = read_record(path,registration_hash,model['id'],number,attempt,expected)
                    observed_score = score_raw(spec['comparator'],dataset,case,feasible,raw)
                    row.update(observed_score)
                    row.update(metrics=value['metrics'],same_bytes_blind_attested=value['same_bytes_blind_attested'],
                               raw_response_sha256=value['raw_response_sha256'],raw_response_bytes=len(raw),
                               request_sha256=sha(expected))
                    if attempt==2:
                        paired = 'raw_response_sha256' in records[number-1]
                        row['paired_first_record'] = paired
                        if not paired:
                            row['status'] = 'unpaired_retry'
                            row['unpaired_observation'] = observed_score
                            for key in ('ir_valid','plan_exact','result_exact','plan_and_result_exact','unsupported_correct'):
                                row[key] = False
                            row.pop('validated_plan',None)
                            row.pop('result',None)
                except FileNotFoundError:
                    pass
                except (Invalid,OSError,ValueError,TypeError,UnicodeError,RecursionError):
                    row['status'] = 'invalid_record'
                records.append(row)
        summaries = []
        for attempt in range(1,attempts(spec)+1):
            selected = [row for row in records if row['attempt']==attempt]
            feasible = [row for row in selected if row['feasible']]
            unsupported = [row for row in selected if not row['feasible']]
            summaries.append({'attempt':attempt,'response_total':40,'feasible_total':30,'unsupported_total':10,
                              'feasible_ir_valid':sum(row['ir_valid'] for row in feasible),
                              'unsupported_ir_valid':sum(row['ir_valid'] for row in unsupported),
                              'feasible_status_counts':dict(Counter(row['status'] for row in feasible)),
                              'unsupported_status_counts':dict(Counter(row['status'] for row in unsupported)),
                              **{name:sum(row[name] for row in selected) for name in
                                 ('ir_valid','plan_exact','result_exact','plan_and_result_exact','unsupported_correct',
                                  'unauthorized_attempt','hallucinated_field_count','hallucinated_operation_count')},
                              'recorded_responses':sum('raw_response_sha256' in row for row in selected),
                              'complete':all(row['status'] not in ('missing','invalid_record','unpaired_retry') for row in selected),
                              'all_attested':all(row['same_bytes_blind_attested'] for row in selected),
                              'metrics':metric_summary(selected)})
        first_records = [row for row in records if row['attempt']==1]
        all_attested = all(row['same_bytes_blind_attested'] for row in first_records)
        complete = all(row['status'] not in ('missing','invalid_record','unpaired_retry') for row in first_records)
        gate = 'incomplete_or_unattested'
        if spec['evidence_kind']=='synthetic_pipeline_check':
            gate = 'synthetic_fixture_only'
        elif complete and all_attested:
            if spec['comparator']=='sql':
                gate = 'sql_comparator_only'
            elif model['role']=='local':
                gate = 'local_comparison_only'
            else:
                gate = 'owner_reported_threshold_met' if summaries[0]['plan_and_result_exact']/30 >= 0.85 else 'owner_reported_below_threshold'
        recoveries = []
        if attempts(spec)==2:
            for number,_,case,feasible,_ in rows:
                first = records[number-1]
                second = records[len(rows)+number-1]
                if feasible and 'raw_response_sha256' in first and not first['plan_and_result_exact'] and second['plan_and_result_exact']:
                    recoveries.append({'case':number,'id':case['id'],'first_status':first['status'],
                                       'retry_status':second['status'],
                                       'same_bytes_blind_attested':first['same_bytes_blind_attested'] and second['same_bytes_blind_attested']})
        success_after = sum(any(row['case']==number and row['plan_and_result_exact'] for row in records)
                            for number,_,_,feasible,_ in rows if feasible)
        models.append({'model':model,'gate_observation':gate,'first_attempt':summaries[0],
                       'retry_attempt':summaries[1] if len(summaries)>1 else None,
                       'success_within_declared_attempts':success_after,'feasible_denominator':30,
                       'retry_recoveries':recoveries,'cases_benefiting_from_retry':len(recoveries),
                       'declared_attempts_per_case':attempts(spec),'records':records})
    return {'format_version':1,'registration_sha256':registration_hash,'registration':registered,
            'scored_at_unix':int(time.time()),'threshold':0.85,'models':models,
            'transport_observation':'owner-reported manual transfer; no provider authenticity or network capture attested by this scorer',
            'sql_comparability':'strict documented SQL grammar and independent query-only SQLite on frozen small-integer synthetic fixtures'}


def main(argv=None):
    parser = LocalArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command',required=True)
    prepare_parser = commands.add_parser('prepare')
    prepare_parser.add_argument('--spec',required=True)
    prepare_parser.add_argument('--directory',required=True)
    record_parser = commands.add_parser('record')
    record_parser.add_argument('--directory',required=True)
    record_parser.add_argument('--model',required=True)
    record_parser.add_argument('--case',type=int,required=True)
    record_parser.add_argument('--attempt',type=int,required=True)
    record_parser.add_argument('--response',required=True)
    record_parser.add_argument('--request-sha256',required=True)
    record_parser.add_argument('--metrics')
    record_parser.add_argument('--attest-same-bytes-blind',action='store_true')
    score_parser = commands.add_parser('score')
    score_parser.add_argument('--directory',required=True)
    score_parser.add_argument('--out',required=True)
    args = parser.parse_args(argv)
    try:
        if args.command=='prepare':
            prepare(args.spec,args.directory)
        elif args.command=='record':
            metrics = config_json(args.metrics) if args.metrics else None
            record(args.directory,args.model,args.case,args.attempt,args.response,args.request_sha256,
                   metrics,args.attest_same_bytes_blind)
        else:
            evidence = score_study(args.directory)
            write_private(args.out,(json.dumps(evidence,ensure_ascii=True,indent=2,allow_nan=False)+'\n').encode())
        print('Manual validation artifact written locally.')
        return 0
    except (Invalid,OSError,ValueError,TypeError,UnicodeError,RecursionError):
        print('Rejected: validation_error',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
