# Resume MindTunnel

MindTunnel is the product and the Python package and CLI are both named mindtunnel. Canonical repository is https://github.com/maxya/mindtunnel. The authorized roadmap covers P1–P5 and final verification. P6 requires separate approval. Keep synthetic inputs only in agent sessions.

## Observed progress on 2026-11-26

| Phase | Evidence and remaining work |
|---|---|
| P0 | Supplied reference checkpoint e35b09c. Re-ran bootstrap, all 10 tests and demo on Linux/Python 3.14.10. |
| P1 | Added v1 schemas, bounded parser and regular-file I/O, exclusive atomic result publication and 53 rejected plan vectors. 25 tests and demo passed, sam PASS. Commit 15f1fb0. |
| P2 | Exact-byte approval and separate Linux mock and private workers implemented. Sam PASS. Commit 021fcae. 35 tests passed. Capture matched 722 bytes, local result matched gold, socket creation denied and outer synthetic capture observed zero packets. |
| P3 | Private plain-text renderer, strict result validation and documented mappings. 43 tests passed, sam PASS. |
| P4–P5 | Next is the offline benchmark and external validation protocol. Benchmark labels frozen by sam before scoring. Product, release and external gates are in PLANS.md. |

The plain executor is an ordinary process. Do not use real data inside a cloud-connected coding session. A model provider, hosted CI, macOS, external testers and licensing require separate evidence. No provider or license has been selected. No package publication, deployment or push is authorized.

Use git log --oneline for local phase commits. Start with PLANS.md and harness/build-log.md, then run make test and make demo. The implementer and reviewer share the filesystem and run separate checks.
