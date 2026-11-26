"""Synthetic v1 conformance, bounded execution and local I/O regression checks."""
import ast
import csv
import json
import os
import random
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mindtunnel import core
from mindtunnel.files import read_regular, write_private

ROOT = Path(__file__).resolve().parents[1]


class Conformance(unittest.TestCase):
    def setUp(self):
        self.contract = core.load(ROOT / 'examples/contract.json')
        self.plan = core.load(ROOT / 'examples/plan.json')
        self.mapping = {'category': 'kind', 'amount_cents': 'cents'}
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.data = self.directory / 'synthetic.csv'

    def execute_rows(self, rows, plan=None):
        with self.data.open('w', newline='', encoding='utf-8') as output:
            writer = csv.writer(output)
            writer.writerow(['kind', 'cents'])
            writer.writerows(rows)
        before = self.data.read_bytes()
        result = core.execute(self.contract, self.mapping, plan or self.plan, self.data)
        self.assertEqual(before, self.data.read_bytes())
        return result['rows']

    def test_frozen_vectors(self):
        vectors = json.loads((ROOT / 'tests/fixtures/conformance-v1.json').read_text())
        self.assertGreaterEqual(len(vectors['invalid']), 30)
        for case in vectors['invalid']:
            with self.subTest(case=case['id']):
                with self.assertRaises(core.Invalid) as error:
                    core.validate(self.contract, core.parse(case['raw']))
                self.assertEqual(str(error.exception), case['error'])
        for plan in vectors['valid']:
            core.validate(self.contract, plan)

    def test_json_byte_limit_and_encoding(self):
        self.assertEqual(core.parse(b' ' * (core.MAX_JSON - 2) + b'{}'), {})
        for raw in [b' ' * (core.MAX_JSON + 1), 'é' * core.MAX_JSON, b'\xff', b'{"x":1}\x00', b'[' * 2000]:
            with self.subTest(raw_length=len(raw)), self.assertRaises(core.Invalid):
                core.parse(raw)
        for raw in [None, 1, []]:
            with self.assertRaises(core.Invalid):
                core.parse(raw)

    def test_contract_strictness(self):
        bad = [dict(self.contract, version=True), dict(self.contract, fields=[]),
               dict(self.contract, fields=self.contract['fields'] * 9)]
        for field in [{'id': 'count', 'type': 'integer'}, {'id': '../a', 'type': 'string'},
                      {'id': 'a', 'type': []}, {'id': 'a', 'type': True},
                      {'id': 'é', 'type': 'string'}, {'id': 'a'*33, 'type': 'integer'}]:
            bad.append({'version': 1, 'fields': [field]})
        bad.append({'version': 1, 'fields': [self.contract['fields'][0]] * 2})
        for contract in bad:
            with self.subTest(contract=contract), self.assertRaises(core.Invalid):
                core.contract_hash(contract)
        reordered = {'fields': self.contract['fields'], 'version': 1}
        self.assertEqual(core.contract_hash(reordered), core.contract_hash(self.contract))

    def test_public_task_limits(self):
        core.request(self.contract, 'x' * 2000)
        for task in ['', '   ', 'x' * 2001, '\ud800', None]:
            with self.assertRaises(core.Invalid):
                core.request(self.contract, task)

    def test_integer_and_empty_semantics(self):
        rows = [('a', -(2**63)), ('a', 2**63 - 1), ('a', 2**63 - 1)]
        self.assertEqual(self.execute_rows(rows), [{'group': 'a', 'value': 2**63 - 2}])
        self.assertEqual(self.execute_rows([]), [])
        for op in ['count', 'sum']:
            plan = dict(self.plan, group_by=None, aggregate={'op': op, 'field': None if op == 'count' else 'amount_cents'})
            self.assertEqual(self.execute_rows([], plan), [{'group': None, 'value': 0}])
        for value in ['+1', '1.0', ' 1', '1 ', str(2**63), str(-(2**63)-1), '١']:
            with self.subTest(value=value), self.assertRaises(core.Invalid):
                self.execute_rows([('a', value)])

    def test_seeded_aggregation_properties(self):
        generator = random.Random(7301)
        for _ in range(80):
            rows = [(generator.choice(['', 'a', 'é', 'z\nquoted,"']), generator.randint(-10000, 10000))
                    for _ in range(generator.randrange(40))]
            totals = {}
            for group, value in rows:
                totals[group] = totals.get(group, 0) + value
            expected = [{'group': group, 'value': totals[group]} for group in sorted(totals)]
            self.assertEqual(self.execute_rows(rows), expected)
            generator.shuffle(rows)
            self.assertEqual(self.execute_rows(rows), expected)

    def test_actual_resource_boundaries(self):
        self.assertEqual(len(self.execute_rows([('a', 1)] * core.MAX_ROWS)), 1)
        with self.assertRaisesRegex(core.Invalid, '^row_limit$'):
            self.execute_rows([('a', 1)] * (core.MAX_ROWS + 1))
        self.assertEqual(len(self.execute_rows([(str(i), 1) for i in range(core.MAX_GROUPS)])), core.MAX_GROUPS)
        with self.assertRaisesRegex(core.Invalid, '^group_limit$'):
            self.execute_rows([(str(i), 1) for i in range(core.MAX_GROUPS + 1)])
        self.assertEqual(self.execute_rows([('x' * core.MAX_CELL, 1)])[0]['value'], 1)
        with self.assertRaises(core.Invalid):
            self.execute_rows([('x' * (core.MAX_CELL + 1), 1)])
        self.data.write_bytes(b'x' * (core.MAX_FILE + 1))
        with self.assertRaisesRegex(core.Invalid, '^file_limit$'):
            core.execute(self.contract, self.mapping, self.plan, self.data)

    def test_malformed_csv_and_mapping(self):
        for raw in [b'', b'kind,cents,cents\na,1,1\n', b'kind,cents\na\n', b'kind,cents\n"unfinished,1', b'kind,cents\na,\xff\n', b'other,cents\na,1\n']:
            self.data.write_bytes(raw)
            with self.subTest(raw=raw), self.assertRaises(core.Invalid):
                core.execute(self.contract, self.mapping, self.plan, self.data)
        for mapping in [{}, {'category':'kind','amount_cents':'kind'}, {'category': [], 'amount_cents':'cents'}]:
            with self.assertRaises(core.Invalid):
                core.execute(self.contract, mapping, self.plan, self.data)

    def test_regular_files_and_symlink_components(self):
        self.data.write_bytes(b'{}')
        link = self.directory / 'link'
        link.symlink_to(self.data)
        with self.assertRaises(OSError):
            core.load(link)
        directory_link = self.directory / 'linked-directory'
        directory_link.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaises(OSError):
            core.load(directory_link / self.data.name)
        with self.assertRaises(ValueError):
            read_regular(self.directory, 20)
        fifo = self.directory / 'fifo'
        os.mkfifo(fifo)
        with self.assertRaises(ValueError):
            read_regular(fifo, 20)
        with self.assertRaises(ValueError):
            read_regular(self.directory / '..' / self.directory.name / self.data.name, 20)

    def test_private_atomic_output_and_cleanup(self):
        destination = self.directory / 'result.json'
        previous_umask = os.umask(0o022)
        try:
            write_private(destination, b'{"version":1}')
        finally:
            os.umask(previous_umask)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
        with self.assertRaises(FileExistsError):
            write_private(destination, b'changed')
        self.assertEqual(destination.read_bytes(), b'{"version":1}')
        destination.unlink()
        with patch('mindtunnel.files.os.fsync', side_effect=OSError('SYNTHETIC_CANARY')):
            with self.assertRaises(OSError):
                write_private(destination, b'partial')
        self.assertFalse(destination.exists())
        self.assertEqual(list(self.directory.iterdir()), [])
        destination.symlink_to(self.directory / 'absent')
        with self.assertRaises(FileExistsError):
            write_private(destination, b'changed')
        self.assertFalse((self.directory / 'absent').exists())
        self.assertEqual(len(list(self.directory.iterdir())), 1)

    def test_output_respects_restrictive_umask(self):
        for mask, expected_mode in [(0o000, 0o600), (0o077, 0o600), (0o777, 0o000)]:
            with self.subTest(umask=oct(mask)):
                destination = self.directory / ('result-' + str(mask))
                previous_umask = os.umask(mask)
                try:
                    write_private(destination, b'synthetic')
                finally:
                    os.umask(previous_umask)
                mode = stat.S_IMODE(destination.stat().st_mode)
                self.assertEqual(mode, expected_mode)
                self.assertEqual(mode & ~0o600, 0)

    def test_no_network_or_dynamic_execution_imports(self):
        forbidden = {'socket', 'urllib', 'http', 'requests', 'subprocess', 'ctypes'}
        for name in ['core.py', 'files.py', 'cli.py']:
            tree = ast.parse((ROOT / 'mindtunnel' / name).read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertTrue(forbidden.isdisjoint(alias.name.split('.')[0] for alias in node.names))
                if isinstance(node, ast.ImportFrom):
                    self.assertNotIn((node.module or '').split('.')[0], forbidden)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    self.assertNotIn(node.func.id, {'eval', 'exec', '__import__'})

    def test_rejects_plan_before_opening_data(self):
        with patch('mindtunnel.core.read_regular') as reader:
            with self.assertRaises(core.Invalid):
                core.execute(self.contract, self.mapping, dict(self.plan, command='SYNTHETIC_CANARY'), self.data)
            reader.assert_not_called()

    def test_cli_errors_keep_canaries_local(self):
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO
        from mindtunnel.cli import main

        self.data.write_text('kind,cents\na,SYNTHETIC_PRIVATE_CANARY\n')
        mapping = self.directory / 'mapping.json'
        mapping.write_text(json.dumps(self.mapping))
        output = self.directory / 'SYNTHETIC_PATH_CANARY.json'
        args = ['run', '--contract', str(ROOT / 'examples/contract.json'),
                '--plan', str(ROOT / 'examples/plan.json'), '--mapping', str(mapping),
                '--data', str(self.data), '--out', str(output)]
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(main(args), 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), 'Rejected: invalid_integer\n')
        self.assertFalse(output.exists())

    def test_concurrent_output_keeps_one_complete_result(self):
        from concurrent.futures import ThreadPoolExecutor
        destination = self.directory / 'result.json'

        def write(index):
            raw = str(index).encode() * 1000
            try:
                write_private(destination, raw)
                return raw
            except FileExistsError:
                return None

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(write, range(8)))
        winners = [result for result in results if result is not None]
        self.assertEqual(len(winners), 1)
        self.assertEqual(destination.read_bytes(), winners[0])
        self.assertEqual(list(self.directory.iterdir()), [destination])
