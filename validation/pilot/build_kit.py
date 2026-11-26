"""Build a participant ZIP using a wheel verified by the offline release verifier."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from mindtunnel import __version__
from mindtunnel.files import read_regular, write_private

WHEEL_NAME = f"mindtunnel-{__version__}-py3-none-any.whl"
PARTICIPANT_FILES = (
    "README.md",
    "QUESTIONNAIRE.md",
    "contract.json",
    "mapping.json",
    "dispatch.csv",
    "demo-plan.json",
    "exercise-plan.json",
    "rejected-plan.json",
)


def read_bounded(path, limit):
    raw = read_regular(path, limit)
    if len(raw) > limit:
        raise ValueError("pilot_input_limit")
    return raw


def build_kit(wheel, verification, target):
    wheel = Path(wheel)
    if wheel.name != WHEEL_NAME:
        raise ValueError("pilot_wheel_name")
    checks = json.loads(read_bounded(verification, 1024 * 1024))
    if checks.get("format_version") != 1:
        raise ValueError("pilot_verification_format")
    wheel_bytes = read_bounded(wheel, 1024 * 1024)
    if hashlib.sha256(wheel_bytes).hexdigest() != checks.get("wheel_sha256"):
        raise ValueError("pilot_wheel_hash")
    readme = ROOT / "validation/pilot/participant/README.md"
    with io.BytesIO() as buffer:
        with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
            archive.writestr(WHEEL_NAME, wheel_bytes)
            for name in PARTICIPANT_FILES:
                path = readme.with_name(name)
                archive.writestr(name, read_bounded(path, 16 * 1024))
        write_private(target, buffer.getvalue())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True)
    parser.add_argument("--verification", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        build_kit(args.wheel, args.verification, args.out)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        parser.exit(1, f"Pilot kit build failed: {error}\n")
    print("Participant ZIP written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
