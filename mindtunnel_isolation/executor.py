"""Private worker protocol. stdout is a private file descriptor of the launcher."""
import json
import sys

from mindtunnel.core import execute, load

if __name__ == "__main__":
    result = execute(load("/input/contract"), load("/input/mapping"), load("/input/plan"), "/input/data")
    sys.stdout.buffer.write((json.dumps(result, ensure_ascii=True, indent=2) + "\n").encode("ascii"))
