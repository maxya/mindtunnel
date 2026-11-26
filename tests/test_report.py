"""Private local report validation, resource bounds, escaping, and CLI behavior."""
import csv
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from mindtunnel.cli import main
from mindtunnel.core import MAX_CELL, MAX_GROUPS, MAX_ROWS, Invalid, execute, load
from mindtunnel.report import MAX_RESULT_JSON, MAX_TOTAL, MIN_TOTAL, load_result, render, validate_result

ROOT = Path(__file__).resolve().parents[1]


class LocalReport(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.source = self.directory / 'private-result.json'
        self.output = self.directory / 'private-report.txt'

    def test_gold_and_empty_report(self):
        value = load(ROOT / 'examples/expected.json')
        self.assertEqual(render(value), b'group | value\n"food" | 2200\n"transport" | 3000\n')
        self.assertEqual(render({'version':1, 'rows':[]}), b'group | value\n(empty)\n')
        for value in [MIN_TOTAL, MAX_TOTAL, 0]:
            result = {'version':1, 'rows':[{'group':None, 'value':value}]}
            self.assertIn(str(value).encode(), render(result))

    def test_plain_text_escapes_private_injection(self):
        malicious = '\x1b[2J\n\t\r\x00<script>alert(1)</script>https://example.invalid/`link`|&\u202e😀'
        result = {'version':1, 'rows':[{'group':malicious, 'value':-1}]}
        raw = render(result)
        text = raw.decode('ascii')
        self.assertEqual(text.count('\n'), 2)
        self.assertIn('\\u001b', text)
        self.assertIn('\\ud83d\\ude00', text)
        for unsafe in ['\x1b', '<', '>', 'https:', '//', '`', '&', '\u202e']:
            self.assertNotIn(unsafe, text)
        self.assertEqual(text.count('|'), 2)

    def test_reject_impossible_or_malformed_results(self):
        base = {'version':1, 'rows':[{'group':'a', 'value':1}]}
        variants = [dict(base, version=True), dict(base, version=2), dict(base, extra='SYNTHETIC_CANARY'),
                    dict(base, rows=None), dict(base, rows=[{'group':'a','value':True}]),
                    dict(base, rows=[{'group':'a','value':MAX_TOTAL+1}]),
                    dict(base, rows=[{'group':'a','value':MIN_TOTAL-1}]),
                    dict(base, rows=[{'group':'a','value':1,'private':'SYNTHETIC_CANARY'}]),
                    dict(base, rows=[{'group':'a'*(MAX_CELL+1),'value':1}]),
                    dict(base, rows=[{'group':'\ud800','value':1}]),
                    dict(base, rows=[{'group':1,'value':1}]),
                    dict(base, rows=[{'group':'a','value':1}]*2),
                    dict(base, rows=[{'group':'b','value':1},{'group':'a','value':2}]),
                    dict(base, rows=[{'group':None,'value':1},{'group':'a','value':2}]),
                    dict(base, rows=[{'group':str(i),'value':1} for i in range(MAX_GROUPS+1)]),
                    dict(base, rows=[{'group':'a','value':MAX_TOTAL},{'group':'b','value':1}])]
        for index, result in enumerate(variants):
            with self.subTest(result_index=index), self.assertRaises(Invalid):
                validate_result(result)

    def test_full_escaped_unicode_result_loads(self):
        # Each group is exactly 4096 code points, escaped to almost 49152 bytes.
        rows = [{'group':str(i).zfill(3) + '😀' * (MAX_CELL-3), 'value':2**63-1}
                for i in range(MAX_GROUPS)]
        data = self.directory / 'wide-unicode.csv'
        with data.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['kind','amount'])
            writer.writerows((row['group'], row['value']) for row in rows)
        result = execute(load(ROOT/'examples/contract.json'),
                         {'category':'kind', 'amount_cents':'amount'},
                         load(ROOT/'examples/plan.json'), data)
        self.assertEqual(result, {'version':1, 'rows':rows})
        raw = json.dumps(result, ensure_ascii=True, indent=2).encode()
        self.assertGreater(len(raw), 9 * 1024 * 1024)
        self.assertLess(len(raw), MAX_RESULT_JSON)
        self.source.write_bytes(raw)
        self.assertEqual(load_result(self.source), result)
        table = render(result)
        self.assertEqual(len(table.splitlines()), MAX_GROUPS+1)
        self.assertIn(str(2**63-1).encode(), table)

    def test_executor_extreme_integer_totals_render_exactly(self):
        data = self.directory / 'integer-limits.csv'
        contract = load(ROOT/'examples/contract.json')
        plan = load(ROOT/'examples/plan.json')
        for integer, expected in [(-(2**63), MIN_TOTAL), (2**63-1, MAX_TOTAL)]:
            data.write_text('kind,amount\n' + ('a,' + str(integer) + '\n') * MAX_ROWS)
            result = execute(contract, {'category':'kind','amount_cents':'amount'}, plan, data)
            self.assertEqual(result['rows'][0]['value'], expected)
            self.assertIn(str(expected).encode(), render(result))

    def test_structure_bound_precedes_json_materialization(self):
        from unittest.mock import patch
        self.source.write_bytes(b'[' + b'0,' * 100000 + b'0]')
        with patch('mindtunnel.report.parse') as parser:
            with self.assertRaisesRegex(Invalid, '^result_structure_limit$'):
                load_result(self.source)
            parser.assert_not_called()
        punctuation = ('{[,:]}"\\' * 600)[:MAX_CELL]
        result = {'version':1,'rows':[{'group':punctuation,'value':1}]}
        self.source.write_bytes(json.dumps(result).encode())
        self.assertEqual(load_result(self.source), result)

    def test_report_input_limit_and_duplicate_keys(self):
        for raw in [b' ' * (MAX_RESULT_JSON+1), b'{"version":1,"version":1,"rows":[]}',
                    b'{"version":1,"rows":[{"group":null,"value":1.0}]}', b'\xff']:
            self.source.write_bytes(raw)
            with self.assertRaises(Invalid):
                load_result(self.source)

    def test_cli_private_output_no_overwrite_and_generic_errors(self):
        self.source.write_bytes(json.dumps({'version':1,'rows':[{'group':'SYNTHETIC_PRIVATE_CANARY','value':1}]}).encode())
        args = ['report','--result',str(self.source),'--out',str(self.output)]
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(main(args), 0)
            self.assertEqual(main(args), 2)
        self.assertEqual(stdout.getvalue(), 'Local report written.\n')
        self.assertNotIn('CANARY', stderr.getvalue())
        self.assertIn(b'SYNTHETIC_PRIVATE_CANARY', self.output.read_bytes())
        self.source.write_text('{"version":1,"rows":[{"group":"SYNTHETIC_CANARY","value":true}]}')
        stdout, stderr = StringIO(), StringIO()
        other = self.directory / 'other.txt'
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(main(['report','--result',str(self.source),'--out',str(other)]), 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), 'Rejected: result_value\n')
        self.assertFalse(other.exists())
