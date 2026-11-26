# Final independent MindTunnel engineering review

Local implementation verdict — PASS

Overall MVP release verdict — NOT RELEASE-READY. Mandatory external acceptance evidence and owner release decisions remain pending.

## Scope and reviewed target

Sam independently reviewed commit fe92165 and the complete accumulated implementation from P0 through P5, against AGENTS.md, GOALS.md, PLANS.md, docs/MVP.md, architecture/security/evaluation documentation and the execution ledger. This was a separate cross-phase review following the individual phase reviews. Actual code, package configuration, tests, schemas, synthetic fixtures, raw benchmark evidence, CI and operator documentation were inspected. The reviewer ran source, archive, installed-package and actual Linux runtime checks, using synthetic data only. No tracked sources were changed by this review.

The initial target worktree was clean. At the last check only the orchestrator's new harness/reviews/ directory was untracked. Local phase history was e35b09c, 15f1fb0, 021fcae, a9b4304, bd4916d and fe92165. No remote operation, publication, deployment, real provider interaction, real private data access or outside tester observation occurred.

## MVP traceability

| Requirement | Final review status | Implementation and observed evidence |
|---|---|---|
| MT-01 explicit public contract | Verified | core.contract_fields/request enforce bounded exact public contract; aliases/types are authored explicitly; no data/mapping/result argument exists in request builder; contract/task tests pass |
| MT-02 strict versioned plan | Verified | duplicate-aware parser, UTF-8/byte limits, strict integer types, exact keys/operations/references, contract hash and typed equality; 53 rejection vectors pass in source and both installed distributions |
| MT-03 read-only interpreter | Verified | execute validates before data access, bounded regular-file snapshot, exact integer sums/counts, string grouping and equality, deterministic order and empty semantics; source-byte checks, shuffled seeded cases, extremes and 30 independent gold labels pass |
| MT-04 private result sink | Verified | files.parent_directory/read_regular/write_private enforce descriptor-relative no-follow access, regular inputs, bounded reads, exclusive atomic publication and restrictive output mode; failure/concurrency/symlink/umask tests pass, generic CLI messages preserved |
| MT-05 egress review | Verified for manual and isolated mock paths | reviewed bytes, destination/model and hash displayed; confirmation, expiry, one-use state, drift/copy/concurrency checks; exact 722-byte capture and installed approval/capture workflow pass; private inputs omitted from planner mounts/interface |
| MT-06 planner quality | Partially verified | strict unsupported outcome and returned-plan validation work, no private feedback retry; deterministic mock supports documented grammar. Actual model planning quality remains unmeasured |
| MT-07 optional additional operations | Justified deferral | existing v1 primitives express all 30 frozen feasible plans. Additional primitives have no benchmark justification and remain outside this implementation |
| MT-08 usability | Local functionality verified, human validation pending | installed/source run/report commands, escaped text tables, mapping/setup docs and synthetic demo pass. Five-person comprehension and usability evidence remains absent |
| MT-09 evaluation | Partially verified | frozen 30 feasible/10 unsupported cases across 3 schemas; gold and trusted analyst SQL each 30/30; invalid vectors 53/53; mock 0/30 feasible and 10/10 unsupported. Blind public export and strict scoring retain missing/failed cases. Actual model comparison and pilot gate remain open |
| MT-10 release | Local preparation verified, acceptance incomplete | source/wheel archives inspected and rebuilt, clean installs pass, inventory/checklist/security policy/demo recording supplied. Hosted OS matrix, license grant, monitored reporting route and owner sign-off remain pending |

## Cross-component confidentiality and execution review

The planning coordinator reads only owner-selected public request and approval files. Its envelope carries the exact approved request plus fixed mock destination/model. It accepts no mapping, source dataset, execution result, private-error repair or history context. The standalone mock worker receives only that envelope. Returned data is treated as an untrusted plan and validated against the public contract, or recognized as precisely the unsupported object.

The executor accepts owner-selected local paths, with no plan-controlled executable code, SQL, shell, URL, plugin or filesystem operation. Source rows are parsed as typed values and have no model interpretation path. Result/report content is written to explicitly selected local files. Normal status, validation and argument errors avoid source content and paths. The report escapes terminal controls, multiline labels, Unicode controls, markup and link punctuation. The demo intentionally prints only invented data and output.

The Linux launcher is a trusted host component. It snapshots bounded inputs, pins selected read-only input files, mounts trusted runtime libraries and selected worker modules, clears environment, closes unrelated descriptors, creates fresh namespaces, drops capabilities and prevents nested user namespaces. Seccomp denies socket, socketpair and io_uring setup. Startup resource limits and a parent timeout bound the bundled workers. Actual synthetic probe checks denied IPv4/IPv6/Unix socket creation, absent host home/proc/private inputs and cleared canary environment. The same installed module layout successfully launched both workers from an unrelated directory.

These controls depend on trusted OS, runtime libraries, installed code, owner account, clock and owner-controlled directories. The ordinary CLI uses normal host privileges. System runtime directories must contain only trusted public runtime material. Local backups, sync, crash leftovers, hostile same-user software, manually disclosed sensitive questions and cloud-connected terminal capture remain residual risks. The review establishes observed defensive behavior within these assumptions. It supplies neither a formal confidentiality proof nor a comprehensive independent security audit.

## Findings and release blockers

No unresolved CRITICAL, HIGH or MEDIUM local implementation defect was confirmed in this review. P1's LOW permission-test issue was corrected and independently rechecked. The packaging metadata whitespace issue was corrected by temporary canonical generation and exact archive inspection, then reverified.

The following are release-blocking acceptance requirements, already disclosed by the repository. They are outstanding evidence/owner decisions, rather than newly discovered source regressions.

- RG-01, HIGH acceptance gap — docs/EVALUATION.md and GOALS.md require actual model comparisons and at least 85% combined plan/result success on supported tasks. Raw offline evidence labels external model quality unmeasured. Conduct a frozen, owner-approved model evaluation with public requests only and record provider/model/settings, outcomes, latency/cost and interventions. The trusted SQL constants establish local semantics only.
- RG-02, HIGH acceptance gap — GOALS.md requires five outside testers and at least three unaided boundary explanations. docs/PILOT.md contains empty participant rows. Run the approved anonymous synthetic pilot and retain actual attempts, failures and understanding scores.
- RG-03, HIGH release evidence gap — required macOS/Linux hosted CI results and the Python 3.11 minimum-version run are unavailable here. The inspected matrix defines those jobs. Observe and preserve passing actual job results and fix any platform failures before release.
- RG-04, HIGH release authorization gap — LICENSE-NOTES.md, SECURITY.md and docs/RELEASE.md retain pending license/copyright/publication decisions, monitored private reporting route and maintenance policy, and maintainer release sign-off. Complete those owner decisions before issuing a release.

P6 reuse/multi-table/semantic/MCP/port ideas require separate authorization and remain outside the approved MVP implementation.

## Independent execution evidence

| Command/check | Actual result |
|---|---|
| bash bootstrap.sh, Python 3.14.10 | Exit 0, 54 tests in 0.860 seconds, demo and report matched gold, malicious extra command rejected |
| python3.12 -m unittest discover -s tests -v; python3.12 scripts/demo.py | Both exit 0, 54 tests in 0.743 seconds, Python 3.12.12 |
| python3.13 -m unittest discover -s tests -v; python3.13 scripts/demo.py | Both exit 0, 54 tests in 1.064 seconds, Python 3.13.17 |
| scripts/verify_release.py with fresh /tmp evidence | Exit 0, 80 source files, 30 wheel members and 87 source-archive members inspected; byte-identical wheel and normalized sdist rebuilds; clean installs and all installed conformance/CLI checks pass |
| python3 harness/verify_isolation.py | Coding sandbox blocked namespace setup. Approved outside-sandbox retry exit 0, all 722 captured bytes match, isolated gold result and socket denial probe pass |
| bash harness/isolation/capture.sh | Coding sandbox blocked namespace setup. Approved outside-sandbox retry exit 0, control datagram observed, zero packets during measured synthetic workflow |
| Installed wheel from /tmp, Python -I, public approval/mock/private execution | Outside-sandbox run exit 0, captured approved bytes and gold result match; no checkout imports |
| Timed independent synthetic demo | Exit 0, 0.2101 seconds on this Linux host |
| compileall over all known modules/tests/harness/scripts; git diff --check | Exit 0 |

Release evidence is /tmp/mindtunnel-sam-final-release.json, with retained final build evidence at /tmp/mindtunnel-sam-final-artifacts-check.json. Optional GIF generation and both frames were independently inspected in P5. Evaluation reproducibility, original held-out file identity, stable raw results, disclosure measurements and public-export/missing-response denominators were independently verified in P4 and re-exercised by the final source tests.

The local interpreter inventory includes Python 3.12, 3.13 and 3.14, with no installed 3.11. Python 3.11 and macOS remain explicitly unverified. Build dependencies are recorded from the local preinstalled toolchain, including jaraco.context development-snapshot metadata. Same-toolchain reproducibility passed. Independently provisioned cross-machine build dependency resolution and external advisory audits remain unverified. Third-party JSON Schema execution is unavailable locally, so schemas were inspected statically and runtime semantic validation exercised.

## Final acceptance

The local implementation and its documented defensive boundaries pass the reviewed synthetic engineering checks. The full approved MVP and public release remain incomplete until RG-01 through RG-04 have actual supporting evidence and owner decisions. Continue from the existing frozen evaluation and release checklist without changing labels to improve scores or bypassing those gates. Preserve synthetic-only operation in connected coding sessions.
