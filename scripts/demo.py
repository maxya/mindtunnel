import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def cmd(*args,**kw):
    return subprocess.run([sys.executable,"-m","mindtunnel.cli",*args], cwd=ROOT, text=True, **kw)

with tempfile.TemporaryDirectory() as t:
    result=Path(t).resolve()/"result.json"
    p=cmd("request","--contract","examples/contract.json","--task","Sum amount_cents by category",capture_output=True,check=True)
    assert all(marker not in p.stdout for marker in ("CANARY", "MERCHANT_SECRET", "transactions.csv"))
    print("PUBLIC REQUEST (synthetic):\n"+p.stdout, flush=True)
    print("BUNDLED PLAN (hand-authored):\n"+(ROOT/"examples/plan.json").read_text(), flush=True)
    args=["run","--contract","examples/contract.json","--mapping","examples/mapping.json","--data","examples/transactions.csv"]
    cmd(*args,"--plan","examples/plan.json","--out",str(result),check=True)
    got=json.loads(result.read_text());expected=json.loads((ROOT/"examples/expected.json").read_text())
    assert got==expected
    print("LOCAL RESULT (synthetic only):\n"+json.dumps(got,indent=2))
    report=Path(t).resolve()/"report.txt"
    cmd("report","--result",str(result),"--out",str(report),check=True)
    assert report.read_text()== 'group | value\n"food" | 2200\n"transport" | 3000\n'
    print("LOCAL REPORT (synthetic only):\n"+report.read_text())
    rejected=result.with_name("rejected.json")
    r=cmd(*args,"--plan","examples/rejected-plan.json","--out",str(rejected),capture_output=True)
    assert r.returncode==2 and r.stderr=="Rejected: plan_keys\n" and not rejected.exists()
    print(r.stderr.rstrip())
    print("Malicious plan rejected. No result file created. Synthetic demo passed.")
