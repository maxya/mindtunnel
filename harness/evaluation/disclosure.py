"""Measure serialized disclosure categories locally using only the bundled synthetic corpus."""
import csv
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mindtunnel.core import request


def measure(source):
    corpus = json.loads(source.read_text(encoding="utf-8"))
    measures = []
    for dataset in corpus["datasets"]:
        stream = io.StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(dataset["csv_headers"])
        writer.writerows(dataset["csv_rows"])
        csv_text = stream.getvalue()
        tasks = dataset["cases"] + [c for c in corpus["unsupported"] if c["dataset"] == dataset["id"]]
        for case in tasks:
            contract, question = dataset["contract"], case["task"]
            payload = request(contract, question)
            ir_request = (json.dumps(payload, ensure_ascii=True, indent=2) + "\n").encode()
            # Concrete conventional comparator: one message asks for a direct answer
            # and includes the full invented source. No provider is contacted.
            direct = {"instructions": "Return the answer to the task using the attached CSV.",
                      "task": question, "alias_to_header": dataset["mapping"], "csv": csv_text}
            direct_bytes = (json.dumps(direct, ensure_ascii=True, indent=2) + "\n").encode()
            if any(header.encode() in ir_request for header in dataset["csv_headers"]):
                raise ValueError("unexpected synthetic header in public request")
            measures.append({"case": case["id"], "plan_request_bytes": len(ir_request),
                             "direct_message_bytes": len(direct_bytes),
                             "source_rows_in_direct_message": len(dataset["csv_rows"]),
                             "source_rows_attached_to_plan_request": 0})
    return {"method": "Local serialization of explicit public planning and direct CSV-answer messages",
            "live_provider_calls": 0, "cases": measures}


if __name__ == "__main__":
    print(json.dumps(measure(Path(__file__).with_name("heldout.json")), indent=2))
