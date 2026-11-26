"""Owner-side approval coordination. Private execution never calls this module."""
import base64
import hashlib
import json
import os
import time
from pathlib import Path

from mindtunnel.core import Invalid, canonical, keys, parse, request, require, validate
from mindtunnel.files import parent_directory, read_regular, write_private

DESTINATION = 'mock://local'
MODEL = 'synthetic-v1'
MAX_WORKER = 256 * 1024


def public_request(path):
    raw = read_regular(path, 65536)
    value = parse(raw)
    keys(value, ('version', 'contract', 'contract_sha256', 'task', 'instructions'), 'request_keys')
    require(canonical(value) == canonical(request(value['contract'], value['task'])), 'request_mismatch')
    return raw, value


def preview(path, destination=DESTINATION, model=MODEL):
    raw, _ = public_request(path)
    return review_bytes(raw, destination, model)


def review_bytes(raw, destination, model):
    require(destination == DESTINATION and model == MODEL, 'unsupported_destination')
    binding = {'version': 1, 'request_sha256': hashlib.sha256(raw).hexdigest(),
               'destination': destination, 'model': model}
    return dict(binding, request_utf8=raw.decode('utf-8'), request_bytes=len(raw),
                approval_sha256=hashlib.sha256(canonical(binding)).hexdigest())


def receipt_path(path):
    # The absolute spelling binds a receipt to its owner-selected location.
    return str(Path(os.path.abspath(path)))


def approve(request_path, approval_path, confirmation, destination=DESTINATION,
            model=MODEL, ttl=300, now=None):
    require(type(ttl) is int and 1 <= ttl <= 900, 'approval_ttl')
    shown = preview(request_path, destination, model)
    require(type(confirmation) is str and confirmation == shown['approval_sha256'], 'approval_mismatch')
    issued = int(time.time()) if now is None else now
    receipt = {'version': 1, 'request_sha256': shown['request_sha256'],
               'destination': destination, 'model': model,
               'approval_sha256': confirmation, 'expires_at': issued + ttl,
               'receipt_path': receipt_path(approval_path)}
    write_private(approval_path, canonical(receipt) + b'\n')


def consume(request_path, approval_path, destination=DESTINATION, model=MODEL, now=None, request_bytes=None):
    raw = public_request(request_path)[0] if request_bytes is None else request_bytes
    shown = review_bytes(raw, destination, model)
    receipt = parse(read_regular(approval_path, 65536))
    keys(receipt, ('version', 'request_sha256', 'destination', 'model', 'approval_sha256',
                   'expires_at', 'receipt_path'), 'approval_keys')
    expected = {key: shown[key] for key in ('version', 'request_sha256', 'destination', 'model', 'approval_sha256')}
    require(all(type(receipt[key]) is type(value) and receipt[key] == value
                for key, value in expected.items()), 'approval_mismatch')
    require(receipt['receipt_path'] == receipt_path(approval_path), 'approval_location')
    current = int(time.time()) if now is None else now
    require(type(receipt['expires_at']) is int and current < receipt['expires_at'] <= current + 900,
            'approval_expired')
    # Exclusive marker creation serializes concurrent users of this exact receipt.
    # Its path binding prevents a copied receipt from being consumed elsewhere.
    with parent_directory(approval_path) as (directory, name):
        descriptor = os.open(name + '.used', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
        os.close(descriptor)


def generate_mock(request_path, approval_path, destination=DESTINATION, model=MODEL, now=None):
    from mindtunnel_isolation.linux import run_mock

    raw, value = public_request(request_path)
    consume(request_path, approval_path, destination, model, now, request_bytes=raw)
    envelope = canonical({'request_base64': base64.b64encode(raw).decode('ascii'),
                          'destination': destination, 'model': model})
    output = run_mock(envelope)
    require(type(output) is bytes and len(output) <= MAX_WORKER, 'planner_response')
    try:
        from mindtunnel.core import pairs, reject_constant, reject_float
        result = json.loads(output.decode('utf-8'), object_pairs_hook=pairs,
                            parse_constant=reject_constant, parse_float=reject_float)
        keys(result, ('captured_request_base64', 'response'), 'planner_response')
        captured = base64.b64decode(result['captured_request_base64'], validate=True)
        require(captured == raw, 'capture_mismatch')
        response = result['response']
        if type(response) is dict and set(response) == {'unsupported'}:
            require(response['unsupported'] is True, 'unsupported_response')
        else:
            validate(value['contract'], response)
        return captured, response
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise Invalid('planner_response') from None
