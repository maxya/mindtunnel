#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python_executable="${PYTHON:-python3}"
"$python_executable" -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ required"'
"$python_executable" -m unittest discover -s tests -v
"$python_executable" scripts/demo.py
printf '\nBootstrap checks complete. See README.md for the local CLI workflow.\n'
