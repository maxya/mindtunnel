"""Requires Linux user namespaces, /usr/bin/bwrap and libseccomp. Synthetic only."""
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mindtunnel.core import load, request
from mindtunnel_isolation.linux import _worker, run_private
from mindtunnel_planner.boundary import approve, generate_mock, preview


def main():
    os.environ["MINDTUNNEL_TEST_CANARY"] = "SYNTHETIC_ENV_VALUE"
    probe = _worker("/app/probe.py", [("harness/isolation/probe.py", "/app/probe.py")], {}, b"", 2048)
    if probe != b"isolated synthetic probe passed\n":
        raise SystemExit("probe failed")
    inputs = ROOT / "examples"
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary).resolve()
        contract = inputs / "contract.json"
        payload = request(load(contract), "Sum amount_cents by category")
        raw = (json.dumps(payload, ensure_ascii=True, indent=2) + "\n").encode()
        request_file, receipt = work / "public.json", work / "approval"
        request_file.write_bytes(raw)
        review = preview(request_file)
        approve(request_file, receipt, review["approval_sha256"])
        captured, plan = generate_mock(request_file, receipt)
        if captured != raw or plan != load(inputs / "plan.json"):
            raise SystemExit("mock output mismatch")
        for canary in (b"CANARY", b"MERCHANT_SECRET", b"transactions.csv", b"3000", str(work).encode()):
            if canary in captured:
                raise SystemExit("unexpected capture")
        plan_file, result_file = work / "plan.json", work / "result.json"
        plan_file.write_text(json.dumps(plan))
        run_private(contract, plan_file, inputs / "mapping.json", inputs / "transactions.csv", result_file)
        if load(result_file) != load(inputs / "expected.json"):
            raise SystemExit("local result mismatch")
        print(f"Mock capture matched all {len(raw)} reviewed bytes. Isolated result matched gold.")
        print("IPv4, IPv6 and Unix socket creation denied. Probe could not see host home or input mounts.")


if __name__ == "__main__":
    main()
