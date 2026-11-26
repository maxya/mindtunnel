"""Offline CLI. Request and execution are separate commands."""
import argparse
import json
import os
import sys
from pathlib import Path
from .core import Invalid, execute, load, request

def main(argv=None):
    p = argparse.ArgumentParser(prog="mindtunnel")
    sub = p.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("request", help="Print only manually approved public request")
    q.add_argument("--contract", required=True)
    q.add_argument("--task", required=True)
    r = sub.add_parser("run", help="Execute a plan locally; no remote calls")
    for name in ("contract", "mapping", "data", "plan", "out"):
        r.add_argument("--"+name, required=True)
    a = p.parse_args(argv)
    try:
        c = load(a.contract)
        if a.cmd == "request":
            print(json.dumps(request(c, a.task), ensure_ascii=True, indent=2))
        else:
            result = execute(c, load(a.mapping), load(a.plan), a.data)
            # Owner-supplied destination only, exclusive creation, restrictive mode on POSIX.
            fd = os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=True, indent=2)
                f.write("\n")
            print("Local result written. No result sent to a model.")
        return 0
    except (Invalid, OSError, UnicodeError, TypeError, ValueError, RecursionError) as e:
        print("Rejected: " + (str(e) if isinstance(e, Invalid) else "local_input_or_io_error"), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
