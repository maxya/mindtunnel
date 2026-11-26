"""Validated, escaped local text reports for private v1 aggregates."""
import json

from .core import MAX_CELL, MAX_GROUPS, MAX_ROWS, keys, parse, require, valid_text
from .files import read_regular

# 200 groups * 4096 supplementary Unicode characters * 12 ASCII escape bytes
# is below 10 MiB, including keys, exact integer totals, and normal formatting.
MAX_RESULT_JSON = 16 * 1024 * 1024
MIN_TOTAL = -MAX_ROWS * 2**63
MAX_TOTAL = MAX_ROWS * (2**63 - 1)
ESCAPES = str.maketrans({character: '\\u%04x' % ord(character)
                         for character in '<>&:/`|'})


def validate_result(result):
    keys(result, ('version', 'rows'), 'result_keys')
    require(type(result['version']) is int and result['version'] == 1, 'result_version')
    rows = result['rows']
    require(type(rows) is list and len(rows) <= MAX_GROUPS, 'result_rows')
    previous = None
    minimum_rows = 0
    for row in rows:
        keys(row, ('group', 'value'), 'result_row_keys')
        group, value = row['group'], row['value']
        require(group is None or valid_text(group, MAX_CELL), 'result_group')
        require(type(value) is int and MIN_TOTAL <= value <= MAX_TOTAL, 'result_value')
        input_bound = 2**63 if value < 0 else 2**63 - 1
        needed = (abs(value) + input_bound - 1) // input_bound
        minimum_rows += max(1 if group is not None else 0, needed)
        require(minimum_rows <= MAX_ROWS, 'result_total_limit')
        if group is None:
            require(len(rows) == 1, 'result_order')
        else:
            require(previous is None or previous < group, 'result_order')
            previous = group
    return result


def check_structure(raw):
    """Bound JSON allocation growth before materializing a large result document."""
    require(len(raw) <= MAX_RESULT_JSON, 'json_limit')
    quoted = False
    escaped = False
    separators = 0
    for byte in raw:
        if escaped:
            escaped = False
        elif quoted and byte == 92:
            escaped = True
        elif byte == 34:
            quoted = not quoted
        elif not quoted and byte in b'{}[]:,':
            separators += 1
            require(separators <= MAX_GROUPS * 6 + 16, 'result_structure_limit')


def load_result(path):
    raw = read_regular(path, MAX_RESULT_JSON)
    check_structure(raw)
    return validate_result(parse(raw, limit=MAX_RESULT_JSON))


def render(result):
    validate_result(result)
    lines = ['group | value']
    for row in result['rows']:
        group = json.dumps(row['group'], ensure_ascii=True).translate(ESCAPES)
        lines.append(group + ' | ' + str(row['value']))
    if not result['rows']:
        lines.append('(empty)')
    return ('\n'.join(lines) + '\n').encode('ascii')
