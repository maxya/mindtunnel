# Verification log

## Phase 0 — handoff creation (2026-11-25)
Reference implementation and synthetic fixtures prepared. Actual execution results are appended after checks. No real data, remote provider, security audit, publication or CI runner execution has been performed.

Observed on Linux x86_64, Python 3.13.5: `bash bootstrap.sh` exit 0, 10 unit test methods pass (with additional subcases), demo returns food=2200 and transport=3000 cents and rejects extra command key. Public request does not contain synthetic private header/merchant canaries. See `phase-00-verification.txt`. No network provider tested, no packet capture or OS isolation proof. macOS and Python 3.11 CI defined but not run here. Owner acceptance pending.

## 2026-11-26 preflight

On main at 68dbdf7 only README was in HEAD. The CI workflow and ignore file were staged and the supplied implementation, tests and planning documents were untracked. Reviewed these files and checkpointed them at e35b09c before P1. Linux x86_64 with Python 3.14.10: make test passed all 10 tests, make demo produced 2200 food and 3000 transport cents and rejected the extra command, and bash bootstrap.sh passed both steps. No provider call. The earlier Linux 3.13.5 result is historical evidence. The configured grunt and sam roles identify their models as GPT-6.1 Sol.

## P1 contract hardening

Grunt implemented contract, plan and result schemas, strict UTF-8/integer JSON parsing, descriptor-based regular-file reads without symlinks, private atomic exclusive result writes, conformance vectors and seeded aggregation tests. Sam independently checked all 53 invalid vectors, four valid plans, and 30 hand-labeled synthetic results. Initial verdict PASS WITH NONBLOCKING OBSERVATIONS. The output permission test assumed mode 0600 even under a more restrictive umask. Grunt corrected the test and sam verified it. Final verdict PASS. Integration ran make test (25 passed), make demo (expected two totals and rejection) and git diff --check. OS isolation is a P2 gate. Held-out evaluation labels froze before scoring at SHA256 054dd9272369591d82e7fe2bac8ca9a50e593f88f13ff33e974153b85aedb12b.

## P2 public planner boundary

Grunt added preview, expiring one-attempt approval, the standalone fixed mock, response validation, tests and manual workflow. The orchestrator integrated the Linux mount/network namespace launcher and seccomp socket filter. The ordinary portable executor remains available for an explicitly owner-managed environment. Sam reviewed both components and returned PASS. Integration and sam independently ran make test (35 pass), make demo, python3 harness/verify_isolation.py and bash harness/isolation/capture.sh. The last two required running the confined workers on the host because the coding sandbox denies nested network namespace setup. Mock captured all 722 reviewed bytes; no synthetic canaries appeared. Network/Unix socket creation denied, two result groups matched gold. The outer synthetic loopback monitor detected its control packet and measured zero packets during the workflow. Live provider terms and planning quality are unverified. Manual transport and mock only. Next: P3 local report.

## P3 local analytical report

Grunt added the report CLI, bounded v1 result reader, escaped local text rendering, mapping documentation and demo. The frozen 30 feasible tasks fit v1, so no plan language extension was needed. Review during implementation identified allocation growth when parsing large invalid results. Grunt added a quote-aware structure limit and verified legitimate escaped results larger than 9 MiB. Sam returned PASS. Integration ran make test (43 passed), make demo (escaped table matched both expected totals and invalid plan was rejected), and git diff --check. Result validation cannot authenticate source provenance. Next: P4 evaluation.
