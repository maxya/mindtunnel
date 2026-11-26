"""Record an offline release verification on native Apple Silicon."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

from verify_release import ROOT, verify
from mindtunnel.files import write_private


def platform_details():
    architecture = platform.machine().lower()
    if sys.platform != "darwin" or architecture != "arm64":
        raise ValueError("Native Apple Silicon macOS and an arm64 Python are required.")
    if sys.version_info < (3, 11):
        raise ValueError("Python 3.11 or newer is required.")
    return {
        "os": "macOS",
        "os_version": platform.mac_ver()[0],
        "process_architecture": architecture,
        "python_implementation": platform.python_implementation(),
    }


def check_linux_invocation():
    """Confirm that asking for Linux isolation on this host fails closed."""
    with tempfile.TemporaryDirectory() as directory:
        result = Path(directory).resolve() / "result.json"
        command = [sys.executable, "-m", "mindtunnel_isolation.linux"]
        for name, file in (("contract", "contract.json"), ("plan", "plan.json"),
                           ("mapping", "mapping.json"), ("data", "transactions.csv")):
            command.extend((f"--{name}", f"examples/{file}"))
        command.extend(("--out", str(result)))
        rejected = subprocess.run(
            command, cwd=ROOT, env={"PATH": os.defpath}, capture_output=True, timeout=20,
        )
        if (rejected.returncode, rejected.stdout, rejected.stderr) != (
            2, b"", b"Rejected: isolated_execution_failed\n",
        ) or result.exists():
            raise ValueError("Linux isolation rejection check failed.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="new evidence JSON path")
    parser.add_argument("--artifacts", help="new directory for the verified archives")
    args = parser.parse_args(argv)
    try:
        evidence = platform_details()
        check_linux_invocation()
        evidence["linux_isolation_request_rejected"] = True
        evidence["execution_mode"] = "ordinary CLI under user process permissions"
        evidence["distribution"] = verify(args.artifacts)
        raw = (json.dumps(evidence, indent=2, sort_keys=True) + "\n").encode("utf-8")
        write_private(Path(args.out), raw)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"macOS verification failed: {error}\n")
    print("Native Apple Silicon verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
