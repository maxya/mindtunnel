# Architecture and data flow

## Core abstraction
`PublicContract + public task -> Plan IR -> validated local execution -> private result`. Separate planning and execution commands serve different trust domains. The request builder never accepts a dataset path, local mapping or result. A human can manually transfer the reviewed request to any planner. The offline executor accepts local inputs and plan; it has no provider code, network calls or generic code execution. The plain run command is an ordinary process. The optional Linux launcher enforces mount and network separation for the bundled mock planner and executor. See [Linux process isolation](ISOLATION.md).

```mermaid
flowchart LR
  subgraph Public[Approved public material]
    C[Hand-authored alias/type contract]
    Q[Public question]
    R[Request builder + exact preview]
    C --> R
    Q --> R
  end
  R -->|Human-approved transfer| P[Cloud or local planner]
  P -->|Untrusted plan JSON| V[Strict validator]
  C --> V
  subgraph Private[Owner machine — private plane]
    D[CSV + local alias mapping]
    E[Bounded interpreter]
    O[Local JSON result]
    D --> E
    E --> O
  end
  V -->|Validated plan| E
```

**No arrow from private plane to planner.** This is the property, not merely a prompt instruction. The owner must not give the cloud coding agent access to real `private/` files or terminal results. `gitignore` is not a sandbox.

## Contract v1 (bootstrap)
Public JSON: `{version: 1, fields: [{id: "category", type: "string"}, {id: "amount_cents", type: "integer"}]}`. Field IDs match ASCII `[a-z][a-z0-9_]{0,31}`; max 16; reject duplicates, reserved special aliases `value` and `count`. No descriptions, inferred data or statistics by default. Mapping (private): exact dictionary `alias -> CSV header`. A manually created mapping is read only by executor. Contract hash uses canonical UTF-8 JSON with sorted object keys, separators `,`/`:`, no ASCII escaping; array order retained. Both sides verify SHA-256 before execution. This binds schema identity, not user approval or plan origin.

Plan v1 JSON has exactly `version`, `contract_sha256`, `group_by` (null or one string field), `aggregate` (`{op:"count",field:null}` or `{op:"sum",field:"amount_cents"}`), `filter` (null or `{field:"category",eq:"food"}`; literal type matches alias). No paths, shell, SQL, URLs, scripts, loops, network or callback arguments. Plan strings/literals are untrusted. Supported type integer = signed 64-bit input; sums are exact Python integers. CSV header mapping explicitly selected; no writes to source. Output schema: `{version:1, rows:[{group:..., value:...}]}` ordered lexicographically by string group; ungrouped aggregate has group null. Empty ungrouped count/sum=0; empty grouped rows empty. Max file 8 MiB, 50,000 rows, 200 output groups, cell length 4096, public task 2000 chars, JSON 64 KiB. Reject, never silently truncate. Limits are not calibrated for production.

## Commands
- `python -m mindtunnel.cli request --contract examples/contract.json --task 'Sum amount_cents by category'` prints only eligible public request + plan format. User manually transfers only if safe. No network, data inspection or auto approval.
- `python -m mindtunnel.cli run --contract ... --mapping ... --data ... --plan ... --out work/result.json` validates then executes locally, creates output exclusively (no overwrite), prints generic success. Errors shown as generic code, not values. Directory must already exist. Do not run on private data through a cloud-connected agent. No output export tool.
- `make demo` uses synthetic inputs and inspects output. No provider call.

## Planner interface

The owner-side coordinator snapshots the public request, verifies approval, and passes exactly those bytes and the fixed destination/model to the isolated mock. It validates the untrusted response or recognizes the strict unsupported object. Manual transfer is available on other platforms. See [planner commands](PLANNING.md). The executor validates the plan before reading CSV data. Only explicitly selected local outputs receive results.

## Storage / operations
No daemon or persistent DB. Private inputs/results should be outside the checkout, with owner-only permissions and disk encryption where available. Audit logs after MVP record only request/plan hash, operation category, version and status, not task, paths, values, counts, result hashes or raw provider errors by default; hashes of low-entropy secrets can leak. Explicit user-directed local export is outside the planner. Local dependencies are reviewed and pinned before releases.

## Rendered diagram

![Architecture](diagrams/architecture.svg)

Graphviz source: `diagrams/architecture.dot`; the Mermaid source above is also editable.

## Implemented public planning boundary

The optional `mindtunnel_planner` coordinator previews exact request bytes, requires an explicit matching approval hash, and consumes an expiring single-use receipt before launching the isolated deterministic mock worker. Only the standalone public worker is mounted into that worker process. Returned captures are compared byte for byte and returned plans are validated against the public contract. Manual transport remains available. Usage and trust assumptions are documented in [PLANNING.md](PLANNING.md).

## Local report

`mindtunnel report --result <local-result> --out <private-text-file>` performs bounded v1 result validation and creates an escaped local text table. Its 16 MiB result-input ceiling accommodates the largest normal ASCII-escaped v1 result. This command accepts no planner destination or network transport and prints generic status. It shares the exclusive private sink with execution. See IMPLEMENTATION.md for mapping and report semantics.
