# Resume MindTunnel

MindTunnel is the product and the Python package and CLI are both named mindtunnel. Canonical repository is https://github.com/maxya/mindtunnel. The authorized roadmap covers P1–P5 and final verification. P6 requires separate approval. Keep synthetic inputs only in agent sessions.

## Observed progress on 2026-11-26

| Phase | Evidence and remaining work |
|---|---|
| P0 | Supplied reference checkpoint e35b09c. Re-ran bootstrap, all 10 tests and demo on Linux/Python 3.14.10. |
| P1 | Added v1 schemas, bounded parser and regular-file I/O, exclusive atomic result publication and 53 rejected plan vectors. See build log for independent review. |
| P2 | Next implementation phase. Exact-byte approval, separate mock planner and network-isolated execution are required. |
| P3–P5 | Pending. Benchmark labels frozen by sam before scoring. Product, release and external gates are in PLANS.md. |

The plain executor is an ordinary process. Do not use real data inside a cloud-connected coding session. A model provider, hosted CI, macOS, external testers and licensing require separate evidence. No provider or license has been selected. No package publication, deployment or push is authorized.

Use git log --oneline for local phase commits. Start with PLANS.md and harness/build-log.md, then run make test and make demo. The implementer and reviewer share the filesystem and run separate checks.
