"""Check the reviewed public source list against a freshly verified archive inventory."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mindtunnel.files import read_regular
from scripts.verify_release import manifest

INTERNAL = {"AGENTS.md", "PLANS.md", "PROMPTS.md", "RESUME.md", "harness/build-log.md"}
INTERNAL_PREFIXES = ("harness/evaluation/", "harness/reviews/", "validation/", "todo/",
                     ".git/", "private/", "work/", ".env")
SIGNATURES = {
    "private_key": rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----",
    "credential_prefix": rb"(?:github_pat_|ghp_|sk-proj-|AKIA)[A-Za-z0-9_]{16,}",
    "host_path": rb"/(?:home|Users)/[^/\s]+/|/media/mData/",
}


def audit(evidence):
    names = set(manifest())
    inventory = evidence["source_manifest"]
    if names != set(inventory):
        raise ValueError("source_inventory_drift")
    for name in sorted(names):
        if name in INTERNAL or name.startswith(INTERNAL_PREFIXES):
            raise ValueError("internal_member: " + name)
        raw = read_regular(ROOT / name, 16 * 1024 * 1024)
        if hashlib.sha256(raw).hexdigest() != inventory[name]:
            raise ValueError("source_hash_drift: " + name)
        for label, expression in SIGNATURES.items():
            if re.search(expression, raw):
                raise ValueError(label + ": " + name)
        if name.endswith(".md"):
            for target in re.findall(r"\]\(([^ )]+)\)", raw.decode("utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme or not parsed.path:
                    continue
                path = (ROOT / name).parent / parsed.path
                if path.resolve().relative_to(ROOT).as_posix() not in names:
                    raise ValueError("documentation_target_missing: " + name)
    return {"source_files_checked": len(names), "signature_checks": list(SIGNATURES),
            "internal_members": 0, "missing_relative_document_links": 0,
            "wheel_sha256": evidence["wheel_sha256"], "sdist_sha256": evidence["sdist_sha256"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_inventory", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(json.loads(args.release_inventory.read_bytes())), indent=2))
