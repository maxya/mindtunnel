"""Standalone deterministic mock adapter. Receives only the public envelope on stdin."""
import base64
import json
import re
import sys

LIMIT = 256 * 1024


def generate(envelope):
    if type(envelope) is not dict or set(envelope) != {'request_base64', 'destination', 'model'}:
        raise ValueError('envelope')
    if envelope['destination'] != 'mock://local' or envelope['model'] != 'synthetic-v1':
        raise ValueError('destination')
    raw = base64.b64decode(envelope['request_base64'], validate=True)
    if len(raw) > 65536:
        raise ValueError('request_limit')
    request = json.loads(raw.decode('utf-8'))
    task = request['task']
    fields = {field['id']: field['type'] for field in request['contract']['fields']}
    match = re.fullmatch(r'(Count rows|Sum ([a-z][a-z0-9_]{0,31}))(?: by ([a-z][a-z0-9_]{0,31}))?', task)
    response = {'unsupported': True}
    if match:
        operation = 'count' if match[1] == 'Count rows' else 'sum'
        field = match[2]
        group = match[3]
        if (field is None or fields.get(field) == 'integer') and (group is None or fields.get(group) == 'string'):
            response = {'version': 1, 'contract_sha256': request['contract_sha256'],
                        'group_by': group, 'aggregate': {'op': operation, 'field': field}, 'filter': None}
    return {'captured_request_base64': base64.b64encode(raw).decode('ascii'), 'response': response}


def main():
    try:
        raw = sys.stdin.buffer.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('envelope_limit')
        result = generate(json.loads(raw.decode('utf-8')))
        sys.stdout.write(json.dumps(result, ensure_ascii=True, separators=(',', ':')))
        return 0
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError):
        sys.stderr.write('planner_worker_failed\n')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
