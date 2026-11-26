"""Synthetic planning-boundary tests. Production mock execution requires isolation."""
import base64
import hashlib
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from mindtunnel.core import Invalid, canonical, load, request
from mindtunnel_planner import boundary
from mindtunnel_planner.cli import main
from mindtunnel_planner.worker import generate

ROOT = Path(__file__).resolve().parents[1]


class PlannerBoundary(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.request_path = self.directory / 'public.json'
        self.approval_path = self.directory / 'approval.json'
        self.contract = load(ROOT / 'examples/contract.json')
        self.raw = json.dumps(request(self.contract, 'Sum amount_cents by category'), indent=2).encode() + b'\n'
        self.request_path.write_bytes(self.raw)

    def approve(self, ttl=300):
        shown = boundary.preview(self.request_path)
        boundary.approve(self.request_path, self.approval_path, shown['approval_sha256'], ttl=ttl, now=1000)

    @staticmethod
    def mock_adapter(raw):
        return canonical(generate(json.loads(raw)))

    def test_exact_preview_and_public_allowlist(self):
        shown = boundary.preview(self.request_path)
        self.assertEqual(shown['request_utf8'].encode(), self.raw)
        self.assertEqual(shown['request_bytes'], len(self.raw))
        self.assertEqual(shown['request_sha256'], hashlib.sha256(self.raw).hexdigest())
        for canary in ['MERCHANT_SECRET', 'private_category_CANARY', 'SYNTHETIC_PRIVATE_PATH']:
            self.assertNotIn(canary, canonical(shown).decode())
        value = json.loads(self.raw)
        for extra in ['data', 'mapping', 'result', 'history', 'tools', 'file']:
            self.request_path.write_bytes(canonical(dict(value, **{extra:'SYNTHETIC_CANARY'})))
            with self.assertRaises(Invalid):
                boundary.preview(self.request_path)
        value['version'] = True
        self.request_path.write_bytes(canonical(value))
        with self.assertRaises(Invalid):
            boundary.preview(self.request_path)

    def test_explicit_confirmation_and_expiry(self):
        with self.assertRaises(Invalid):
            boundary.approve(self.request_path, self.approval_path, 'incorrect')
        self.assertFalse(self.approval_path.exists())
        self.approve(ttl=5)
        with self.assertRaisesRegex(Invalid, '^approval_expired$'):
            boundary.consume(self.request_path, self.approval_path, now=1005)
        self.assertFalse(self.approval_path.with_name('approval.json.used').exists())
        for ttl in [0, 901, True]:
            with self.assertRaises(Invalid):
                boundary.approve(self.request_path, self.directory / 'other', 'bad', ttl=ttl)

    def test_byte_destination_model_drift(self):
        self.approve()
        self.request_path.write_bytes(self.raw + b' ')
        with self.assertRaises(Invalid):
            boundary.consume(self.request_path, self.approval_path, now=1001)
        self.request_path.write_bytes(self.raw)
        for kwargs in [{'destination':'https://example.invalid'}, {'model':'other'}]:
            with self.assertRaises(Invalid):
                boundary.consume(self.request_path, self.approval_path, now=1001, **kwargs)
        self.assertFalse(self.approval_path.with_name('approval.json.used').exists())

    def test_replay_copy_and_concurrent_consumption(self):
        self.approve()
        copied = self.directory / 'copy.json'
        copied.write_bytes(self.approval_path.read_bytes())
        with self.assertRaisesRegex(Invalid, '^approval_location$'):
            boundary.consume(self.request_path, copied, now=1001)

        def consume(_):
            try:
                boundary.consume(self.request_path, self.approval_path, now=1001)
                return True
            except FileExistsError:
                return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(list(pool.map(consume, range(8))).count(True), 1)
        with self.assertRaises(FileExistsError):
            boundary.consume(self.request_path, self.approval_path, now=1001)

    def test_isolated_mock_capture_and_plan(self):
        self.approve()
        with patch('mindtunnel_isolation.linux.run_mock', side_effect=self.mock_adapter) as adapter:
            captured, response = boundary.generate_mock(self.request_path, self.approval_path, now=1001)
        self.assertEqual(captured, self.raw)
        self.assertEqual(response, load(ROOT / 'examples/plan.json'))
        envelope = json.loads(adapter.call_args.args[0])
        self.assertEqual(set(envelope), {'request_base64', 'destination', 'model'})
        self.assertEqual(base64.b64decode(envelope['request_base64']), self.raw)

    def test_snapshot_is_the_approved_payload(self):
        self.approve()
        original_consume = boundary.consume

        def changed_path(*args, **kwargs):
            self.request_path.write_bytes(canonical(request(self.contract, 'Count rows')))
            return original_consume(*args, **kwargs)

        with patch('mindtunnel_planner.boundary.consume', side_effect=changed_path):
            with patch('mindtunnel_isolation.linux.run_mock', side_effect=self.mock_adapter):
                captured, _ = boundary.generate_mock(self.request_path, self.approval_path, now=1001)
        self.assertEqual(captured, self.raw)

    def test_unsupported_is_strict_and_no_retry(self):
        self.raw = canonical(request(self.contract, 'Discover private merchant names'))
        self.request_path.write_bytes(self.raw)
        self.approve()
        with patch('mindtunnel_isolation.linux.run_mock', side_effect=self.mock_adapter) as adapter:
            _, response = boundary.generate_mock(self.request_path, self.approval_path, now=1001)
        self.assertEqual(response, {'unsupported': True})
        adapter.assert_called_once()

    def test_malformed_response_fails_closed(self):
        for response in [{'unsupported': False}, {'unsupported': 1}, {'unsupported': True, 'data':'SYNTHETIC_CANARY'},
                         {'version':1, 'command':'SYNTHETIC_CANARY'}]:
            with self.subTest(response=response):
                approval = self.directory / ('approval-' + str(len(list(self.directory.iterdir()))))
                shown = boundary.preview(self.request_path)
                boundary.approve(self.request_path, approval, shown['approval_sha256'], now=1000)
                output = canonical({'captured_request_base64': base64.b64encode(self.raw).decode(), 'response':response})
                with patch('mindtunnel_isolation.linux.run_mock', return_value=output):
                    with self.assertRaisesRegex(Invalid, '^planner_response$'):
                        boundary.generate_mock(self.request_path, approval, now=1001)
                self.assertTrue(approval.with_name(approval.name + '.used').exists())

    def test_failure_consumes_approval_and_has_generic_cli_error(self):
        self.approve()
        with patch('mindtunnel_isolation.linux.run_mock', side_effect=ValueError('SYNTHETIC_SECRET_ERROR')) as adapter:
            with self.assertRaises(ValueError):
                boundary.generate_mock(self.request_path, self.approval_path, now=1001)
            with self.assertRaises(FileExistsError):
                boundary.generate_mock(self.request_path, self.approval_path, now=1001)
            adapter.assert_called_once()
        fresh = self.directory / 'fresh.json'
        boundary.approve(self.request_path, fresh, boundary.preview(self.request_path)['approval_sha256'])
        stdout, stderr = StringIO(), StringIO()
        with patch('mindtunnel_isolation.linux.run_mock', side_effect=ValueError('SYNTHETIC_SECRET_ERROR')):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = main(['mock', '--request', str(self.request_path), '--approval', str(fresh),
                             '--plan-out', str(self.directory/'plan.json'), '--capture-out', str(self.directory/'capture.json')])
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), 'Rejected: planning_boundary_error\n')

    def test_mock_has_no_data_access_interface(self):
        envelope = {'request_base64':base64.b64encode(self.raw).decode(),
                    'destination':boundary.DESTINATION, 'model':boundary.MODEL}
        for extra in ['data', 'path', 'result', 'error', 'token', 'history']:
            with self.assertRaises(ValueError):
                generate(dict(envelope, **{extra:'SYNTHETIC_CANARY'}))
