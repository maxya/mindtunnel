# Architecture decision log

| ID | Decision | Status | Reason / reconsider when |
|---|---|---|---|
| ADR-001 | Python 3.11+ standard library bootstrap | Accepted for MVP | Runs on macOS/Linux without a model or package install; revisit only on benchmark evidence. |
| ADR-002 | Single repository, CLI-first, no database service | Accepted for MVP | Reduce adoption friction; add persistence/API only after proving the core. |
| ADR-003 | No telemetry, cloud account or mandatory MCP | Accepted for MVP | User control and low friction. MCP is an optional adapter, never an alternate safety boundary. |
| ADR-004 | MIT project license | Accepted by the owner | See the [license](../LICENSE). Third-party components retain their own licenses. |
| ADR-005 | Keep fixtures synthetic, private work outside repository | Accepted for this bootstrap | Cloud-connected coding agents and CI may expose private artifacts. |
| ADR-006 | Manual transfer plus deterministic local mock | Accepted for this implementation | Keeps provider choice with the owner. A live adapter requires an approved destination and retention review. |
| ADR-007 | Optional Linux Bubblewrap and libseccomp worker profile | Verified locally | Plain source commands stay portable. Isolation for other platforms needs separate evidence. |
| ADR-008 | Retain the v1 operation set | Accepted for this benchmark | Count, sum, one grouping and one typed equality condition express all 30 feasible gold plans. |
