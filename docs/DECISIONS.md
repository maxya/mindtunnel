# Architecture decision log

| ID | Decision | Status | Reason / reconsider when |
|---|---|---|---|
| ADR-001 | Python 3.11+ standard library bootstrap | Proposed / used in reference | Runs on macOS/Linux without a model or package install; revisit only on benchmark evidence. |
| ADR-002 | Single repository, CLI-first, no database service | Proposed / used | Reduce adoption friction; add persistence/API only after proving the core. |
| ADR-003 | No telemetry, cloud account or mandatory MCP | Proposed / used | User control and low friction. MCP is an optional adapter, never an alternate safety boundary. |
| ADR-004 | Apache-2.0 candidate | Pending owner | Do not publish as licensed until approved. |
| ADR-005 | Keep fixtures synthetic, private work outside repository | Accepted for this bootstrap | Cloud-connected coding agents and CI may expose private artifacts. |
