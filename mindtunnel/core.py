"""Reference v1 plan interpreter. No networking, subprocesses or dynamic code."""
import csv
import hashlib
import io
import json
import re
from pathlib import Path

MAX_JSON = 65_536
MAX_FILE = 8 * 1024 * 1024
MAX_ROWS = 50_000
MAX_GROUPS = 200
MAX_CELL = 4096
ID = re.compile(r"[a-z][a-z0-9_]{0,31}\Z")
INT = re.compile(r"-?[0-9]{1,19}\Z")

class Invalid(ValueError):
    """Stable error code only; never include private data."""

def require(ok, code):
    if not ok:
        raise Invalid(code)

def pairs(items):
    out = {}
    for k, v in items:
        require(k not in out, "duplicate_key")
        out[k] = v
    return out

def reject_constant(_):
    raise Invalid("nonfinite_json")

def parse(raw):
    require(len(raw) <= MAX_JSON, "json_limit")
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError, OverflowError, ValueError) as exc:
        if isinstance(exc, Invalid):
            raise
        raise Invalid("invalid_json") from None

def load(path):
    with Path(path).open("rb") as f:
        return parse(f.read(MAX_JSON + 1))

def keys(obj, expected, code):
    require(type(obj) is dict and set(obj) == set(expected), code)

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def contract_fields(contract):
    keys(contract, ("version", "fields"), "contract_keys")
    require(type(contract["version"]) is int and contract["version"] == 1, "contract_version")
    fields = contract["fields"]
    require(type(fields) is list and 1 <= len(fields) <= 16, "field_count")
    out = {}
    for f in fields:
        keys(f, ("id", "type"), "field_keys")
        name = f["id"]
        require(type(name) is str and ID.fullmatch(name) is not None and name not in out and name not in ("value", "count"), "field_id")
        require(f["type"] in ("string", "integer"), "field_type")
        out[name] = f["type"]
    return out

def contract_hash(contract):
    contract_fields(contract)
    return hashlib.sha256(canonical(contract)).hexdigest()

def request(contract, task):
    contract_fields(contract)
    require(type(task) is str and 0 < len(task) <= 2000 and task.strip(), "task_limit")
    return {"version": 1, "contract": contract, "contract_sha256": contract_hash(contract), "task": task,
            "instructions": "Return one JSON plan only. Exact keys: version=1, contract_sha256, group_by (null or string field alias), aggregate {op:count,field:null} or {op:sum,field:integer alias}, filter (null or {field:alias,eq:typed literal}). No extra keys or tools. If unsupported return {unsupported:true}; this is not an executable plan. Do not ask for data or results."}

def field_of(fields, name, kind=None):
    require(type(name) is str and name in fields and (kind is None or fields[name] == kind), "field_reference")
    return fields[name]

def scalar(value, kind):
    if kind == "string":
        require(type(value) is str and len(value) <= MAX_CELL, "literal_type")
    else:
        require(type(value) is int and -(2**63) <= value < 2**63, "literal_type")
    return value

def validate(contract, plan):
    fields = contract_fields(contract)
    keys(plan, ("version", "contract_sha256", "group_by", "aggregate", "filter"), "plan_keys")
    require(type(plan["version"]) is int and plan["version"] == 1, "plan_version")
    require(plan["contract_sha256"] == contract_hash(contract), "contract_mismatch")
    if plan["group_by"] is not None:
        field_of(fields, plan["group_by"], "string")
    a = plan["aggregate"]
    keys(a, ("op", "field"), "aggregate_keys")
    require(a["op"] in ("count", "sum"), "unsupported_op")
    if a["op"] == "count":
        require(a["field"] is None, "count_field")
    else:
        field_of(fields, a["field"], "integer")
    f = plan["filter"]
    if f is not None:
        keys(f, ("field", "eq"), "filter_keys")
        scalar(f["eq"], field_of(fields, f["field"]))
    return fields

def read_value(text, kind):
    require(type(text) is str and len(text) <= MAX_CELL, "cell_limit")
    if kind == "string":
        return text
    require(INT.fullmatch(text) is not None, "invalid_integer")
    n = int(text)
    require(-(2**63) <= n < 2**63, "integer_range")
    return n

def execute(contract, mapping, plan, path):
    fields = validate(contract, plan)
    keys(mapping, fields, "mapping_keys")
    require(all(type(v) is str and 0 < len(v) <= MAX_CELL for v in mapping.values()), "mapping_header")
    require(len(set(mapping.values())) == len(mapping), "mapping_duplicate")
    # Read a bounded snapshot; no source mutation. OS-level isolation is external.
    with Path(path).open("rb") as f:
        raw = f.read(MAX_FILE + 1)
    require(len(raw) <= MAX_FILE, "file_limit")
    try:
        reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
        header = next(reader, None)
        require(header is not None and len(header) == len(set(header)) and all(len(x) <= MAX_CELL for x in header), "csv_header")
        require(all(v in header for v in mapping.values()), "missing_header")
        idx = {k: header.index(v) for k,v in mapping.items()}
        grouped = plan["group_by"] is not None
        sums = {} if grouped else {None: 0}
        for i, row in enumerate(reader, 1):
            require(i <= MAX_ROWS, "row_limit")
            require(len(row) == len(header) and all(len(x) <= MAX_CELL for x in row), "csv_row")
            data = {k: read_value(row[idx[k]], t) for k,t in fields.items()}
            f = plan["filter"]
            if f is not None and data[f["field"]] != f["eq"]:
                continue
            g = data[plan["group_by"]] if grouped else None
            a = plan["aggregate"]
            sums[g] = sums.get(g, 0) + (1 if a["op"] == "count" else data[a["field"]])
            require(len(sums) <= MAX_GROUPS, "group_limit")
        return {"version": 1, "rows": [{"group": g, "value": sums[g]} for g in sorted(sums, key=lambda x: "" if x is None else x)]}
    except (UnicodeError, csv.Error):
        raise Invalid("csv_format") from None
