import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def cmd(*args,**kw):
    return subprocess.run([sys.executable,"-m","mindtunnel.cli",*args], cwd=ROOT, text=True, **kw)

with tempfile.TemporaryDirectory() as t:
    result=Path(t)/"result.json"
    p=cmd("request","--contract","examples/contract.json","--task","Sum amount_cents by category",capture_output=True,check=True)
    assert "CANARY" not in p.stdout and "MERCHANT_SECRET" not in p.stdout
    print("PUBLIC REQUEST (synthetic):\n"+p.stdout)
    args=["run","--contract","examples/contract.json","--mapping","examples/mapping.json","--data","examples/transactions.csv","--out",str(result)]
    cmd(*args,"--plan","examples/plan.json",check=True)
    got=json.loads(result.read_text());expected=json.loads((ROOT/"examples/expected.json").read_text())
    assert got==expected
    print("LOCAL RESULT (synthetic only):\n"+json.dumps(got,indent=2))
    r=cmd(*args,"--plan","examples/rejected-plan.json",capture_output=True)
    assert r.returncode==2 and "plan_keys" in r.stderr
    print("Malicious plan rejected; synthetic demo passed.")
