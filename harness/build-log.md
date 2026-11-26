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

## P4 offline evaluation and external gates

Grunt built a frozen-fixture runner, blinded public export and strict response importer. Sam independently labeled the corpus and later reviewed the runner. The orchestrator supplied the fixed analyst SQL comparator, a local serialization comparison and a five-person pilot protocol. No model-generated SQL is executed. Integration reproduced the stored summaries and disclosure records, ran 50 passing tests and timed make demo at 0.20 seconds on this machine. On 30 feasible tasks gold plans and SQL each matched 30 results; the narrow mock declined all 30 and correctly declined the ten unsupported tasks. All 53 invalid vectors were rejected. Forty public planning messages attached zero source rows versus 240 row attachments in the locally constructed direct-answer comparator. No cloud or local model was evaluated. The reviewer returned PASS for local engineering. The full P4 gate remains open: real model quality/comparison and five external testers. Proceed only with independent P5 preparation and final verification. No release authorization follows from the local score.

## P5 local release preparation

Grunt added a positive source manifest, distribution assets, pinned build tools, inventory, release and security reporting instructions, optional synthetic GIF generator and hosted matrix configuration. The orchestrator reconciled the setup, architecture decisions and product docs. Argument parser diagnostics could echo user-supplied arguments; the shared product parser now emits only a generic error. Archive staging uses physical no-follow reads. Sam returned PASS for local P5 engineering and inspected both generated GIF frames. Integration verified the source suite and demo on Linux Python 3.12.12, 3.13.17 and 3.14.10 (54 tests on each). The offline verifier staged known files, exercised two clean installs, and compared wheel and normalized sdist builds on the same toolchain. Sam ran this independently. Clean installs exercised three bundled schemas and all 53 invalid vectors. Hosted CI, macOS, production security review and license approval remain external. Next: final project-wide engineering verification.

P5 staging found backend-generated setup.cfg contained trailing whitespace. Grunt moved the canonical generated settings into the temporary build and checked the archive's exact metadata bytes. Sam reverified both reproducible builds and clean installs, verdict PASS. Final staged diff passed git diff --cached --check.
