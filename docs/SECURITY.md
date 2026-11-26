# Threat model and security gates

## Protected assets and boundary
Source rows/headers, local mapping, values, local output, paths, credentials, private task text, metadata and derived facts. Public alias contract + explicit public question are intentionally discloseable only after owner inspection. User-selected public semantics still reveal meaning; use neutral aliases if appropriate, accepting utility loss. Cloud provider sees public request and ordinary connection metadata. Model-generated plans are untrusted. Trust owner, installed code and OS, not model/provider. This is a data-minimization architecture, not cryptography or a proof of zero leakage.

| Threat | Mitigation | Evidence/gap |
|---|---|---|
| Planner asks for raw data, file paths or arbitrary code | Strict keys/types/allowlisted IR; no private inputs to request command | Bootstrap tests; fuzz and independent review required |
| Sensitive names, counts or examples in metadata | Manually authored contract, no automatic inspection | User responsibility; preview only, cannot detect all secrets |
| Prompt injection in rows | Rows parsed as typed data, never used in prompt | No model in executor; adversarial fixture test |
| Unknown/duplicate JSON fields, version drift | Strict parse; reject unknown and duplicates; hash binding | Unit tests; parser fuzz pending |
| Result/error returned to cloud | Separate command, no model or networking in executor, generic errors and result file | Code review only; OS-level isolation and packet capture pending |
| Arbitrary path / symlink tricks | Plan cannot specify paths; owner supplies data/output explicitly; exclusive output | Same-user malicious filesystem/races not fully defended; add safe open / restrictive dirs if threat changes |
| Denial of service | File, row, cell, field and group limits; exact integers | Test boundary and memory/runtime; CPU OS limits pending |
| Malicious dependency/host, cloud terminal capture | Stdlib baseline; review dependency, isolate private worker, no real data via cloud-connected Codex | Not protected by current process; production gate |
| User chooses dangerous output location | Explain local private path and permissions, no auto sync | Cloud-synced directory or backup may disclose; user responsibility |
| Inference from repeated requests | Single-shot public request; no result/error feedback | Does not guarantee anonymity; public tasks themselves may reveal info |

## Gate before sensitive data use
Independent code review, boundary tests, runtime network-denied execution, inspect process/filesystem permissions, use data outside project, verify no telemetry/remote logs, validate outbound bytes with a mock server, document threat exclusions. Do not use on financial, health, employer or other sensitive real data until owner confirms environment and review. Do not claim HIPAA/GDPR compliance, formal IFC, anonymity, or security certification.

## MCP policy
MCP is a transport, not a privacy guarantee. No `get_result`, raw error or private path tool exposed to a cloud host. A future public `make_request`/`submit_plan` adapter returns generic status only; private result inspection is via owner-controlled local UI. Even status may reveal facts; keep it off by default, or explicitly define permitted disclosures. Do not pass local agent tool outputs to cloud automatically.

## P1 implemented local controls

Regular-file input validation uses `O_NOFOLLOW`, `O_NONBLOCK`, and descriptor-relative directory traversal, rejecting symlink ancestors and `..`. Inputs are bounded snapshots. Owner-selected physical paths are required, including on macOS systems with symlinked temporary-directory ancestors. Private output is published as a complete exclusive file with permissions restricted to 0600 or stricter by the owner's umask. Recoverable failure removes its temporary file. Concurrent creation preserves a single complete winner.

These controls assume a trusted OS and owner-controlled directories. They do not authenticate file contents, prevent an authorized same-user process from changing regular files, or establish filesystem isolation. Source/network restrictions still require an external runtime boundary. Tests inspect direct executor imports for network and dynamic-execution dependencies. That check provides source-level evidence only. OS network denial, packet capture, and independent security review remain separate gates.
