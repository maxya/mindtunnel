"""Prepare deterministic operator packets containing only the public requests."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.evaluation.validation import request_rows
from mindtunnel.files import write_private


def packet(comparator):
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        for number, _, _, _, raw in request_rows({"comparator": comparator}):
            info = ZipInfo(f"case-{number:03d}.json", (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100600 << 16
            archive.writestr(info, raw)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new or empty owner-controlled directory")
    args = parser.parse_args()
    args.output.mkdir(mode=0o700, parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        parser.error("select an empty output directory")
    fingerprints = {}
    for arm in ("ir", "sql"):
        data = packet(arm)
        filename = f"public-{arm}.zip"
        write_private(args.output / filename, data)
        fingerprints[filename] = hashlib.sha256(data).hexdigest()
    print(json.dumps(fingerprints, indent=2))


if __name__ == "__main__":
    main()
