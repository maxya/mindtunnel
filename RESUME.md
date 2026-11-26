# Resume MindTunnel

MindTunnel is the product and the Python package and CLI are both named mindtunnel. Canonical repository is https://github.com/maxya/mindtunnel. The owner accepted local P0–P5 engineering at 9284c1d. The active validation roadmap covers V1–V5. P6 requires separate approval. Keep synthetic inputs only in agent sessions.

## Current decision — NO-GO for public release

V1–V5 local engineering and independent review are complete. Actual model utility, unaided human understanding, native Apple Silicon, hosted CI and owner release approvals remain open. Continue with the numbered collection steps in [the model run guide](validation/MODEL-RUNS.md), the [five-person pilot](validation/pilot/FACILITATOR.md) and [platform verification](docs/PLATFORMS.md). The [final independent review](validation/reviews/v5.md), [archive inventory](validation/distribution-results.json), [candidate notes](docs/RELEASE-NOTES.md) and [validation ledger](validation/README.md) are the current evidence. Earlier P0–P5 reports and archives are historical. Use the curated V5 archives or rebuild from the current positive manifest; the full Git history contains held-out answers.

The current configured grunt and sam roles both use GPT-6.2 Sol. Fresh grunt and sam reported that runtime. The previously active grunt doing V1 reported GPT-6.1 Sol. Sam independently verified V1 using GPT-6.2 Sol.

## Live planner collection at e9afb89

The owner accepted V1–V5 local engineering and authorized transfer of the reviewed synthetic requests to approved, already available providers using included access with no additional charges. Sam cleared all 40 MindTunnel and 40 SQL request texts. The archives, grading materials and checkout stay on the operator side. The current collection record shows zero transfers, sessions and responses. Accuracy and failure attribution remain unknown. Continue with a tool-free, disconnected-from-the-checkout planner surface and confirmed included usage, or run the manual protocol with an eligible model. [Collection guide](validation/MODEL-RUNS.md) · [Live evidence](validation/planner-runs.json)

## Post-MVP checkpoints

The validation work starts from 9284c1d. Keep the frozen corpus and original 85% threshold fixed. The operator-side protocol is in [manual model evaluation](harness/evaluation/VALIDATION.md). The run order and requirements are in the [validation ledger](validation/README.md).

V1 was accepted at d18c4a0. V2 produced [two verified public request packets and collection instructions](validation/MODEL-RUNS.md). No real model session has run. At that checkpoint cloud transfer approval and eligible local weights were outstanding. The live collection record above supersedes that authorization status.

V2 is checkpointed at 53af712. V3 closed the Linux 3.11 minimum-version gap, including wheel and source installs outside the checkout. Run the [native Apple Silicon verification](docs/PLATFORMS.md) and retain its JSON evidence. Hosted CI remains open.

V3 is checkpointed at d92a878. The [participant kit](validation/pilot/participant-kit.zip) and [facilitator protocol](validation/pilot/FACILITATOR.md) are ready. The five-row scoring sheet is blank. Zero participants have been observed.

V4 is checkpointed at 186846c. V5 verified publication scope, final binaries and the [synthetic demo](validation/synthetic-demo.gif). No further local action can supply model responses, participant observations or native Mac results under the current authorization. Confirm a monitored private contact and select a project grant before any public release.

## Historical P0–P5 evidence on 2026-11-26

| Phase | Evidence and remaining work |
|---|---|
| P0 | Supplied reference checkpoint e35b09c. Re-ran bootstrap, all 10 tests and demo on Linux/Python 3.14.10. |
| P1 | Added v1 schemas, bounded parser and regular-file I/O, exclusive atomic result publication and 53 rejected plan vectors. 25 tests and demo passed, sam PASS. Commit 15f1fb0. |
| P2 | Exact-byte approval and separate Linux mock and private workers implemented. Sam PASS. Commit 021fcae. 35 tests passed. Capture matched 722 bytes, local result matched gold, socket creation denied and outer synthetic capture observed zero packets. |
| P3 | Private plain-text renderer, strict result validation and documented mappings. Commit a9b4304. 43 tests passed, sam PASS. |
| P4 | Commit bd4916d. Sam PASS for the local harness. 50 tests passed; gold and analyst SQL 30/30 each, mock 0/30 feasible and 10/10 unsupported, invalid vectors 53/53 rejected. Actual model comparisons and five testers pending. |
| P5 | Local package preparation verified, sam PASS. 54 tests on each of three Linux Python versions. Reproducible same-toolchain wheel and normalized sdist; clean installs checked. Commit fe92165. Full release gate open. Project-wide verification results follow. |

The plain executor is an ordinary process. Do not use real data inside a cloud-connected coding session. A model provider, hosted CI, macOS, external testers and licensing require separate evidence. No provider or license has been selected. No package publication, deployment or push is authorized.

Use git log --oneline for local phase commits. Start with PLANS.md and harness/build-log.md, then run make test and make demo. The implementer and reviewer share the filesystem and run separate checks.

## Final engineering handoff

**Local implementation PASS. Overall release acceptance remains blocked.** The P5 source checkpoint is fe92165. Grunt and sam independently exercised the installed wheel from clean environments outside the checkout. The installed planner captured exactly the 722 reviewed bytes, SHA-256 `029cd2e1e4a8a1b1408b4ebb707b2e5e346f7029c645def4553ee7c8d1b285f8`. The private worker produced 2200 and 3000 cents. The report matched gold. Replaying approval, overwriting output and submitting an unauthorized plan failed. The final independent review found no outstanding material defect in the local scope. See the repository's harness/reviews/ for phase reports and final MT-01–10 traceability.

The scripted demo took 0.21 seconds in the final review. Linux tests and demo passed with Python 3.12.12, 3.13.17 and 3.14.10. The packaging verifier compared 80 allowlisted source files, 30 wheel members and 87 source archive members with expected contents. The two archive formats reproduced byte for byte under the same local toolchain. The version is 0.0.1 and the package declares zero third-party Python runtime dependencies. Independently provisioning the build environment on another host remains unverified. The local build inventory includes a development snapshot of jaraco.context.

**External gates and next work**

1. Choose and review a real planner destination/model and a local comparison model. Export the 40 blinded public requests, review the exact bytes before external transfer, collect responses without feedback and run the local scorer. Record latency, cost, manual interventions, separate unsupported outcomes and actual plan-plus-result accuracy. The cloud gate requires at least 85% on the 30 feasible tasks. Collect a model-generated schema-only baseline through a reviewed synthetic evaluation procedure. The current SQL evidence is analyst-authored.
2. Run the five-person protocol. At least three participants must independently explain the boundary. See [pilot](docs/PILOT.md) and [scorer](harness/evaluation/README.md).
3. Obtain hosted Linux/macOS evidence, including Python 3.11. The ordinary CLI uses local process permissions on macOS. The isolated worker implementation is Linux-specific.
4. Confirm name clearance, license and copyright holder, monitored security reporting route and owner release sign-off. The current code carries no final open-source license grant. Re-run the release checklist after any change. [Release checklist](docs/RELEASE.md)
5. Reconsider optional operations, integrations and ports only in light of observed planner and pilot failures. P6 is outside this authorization.

Use [source setup](BOOTSTRAP.md), [usage](README.md), [threat model](docs/SECURITY.md), [build log](harness/build-log.md) and [roadmap](PLANS.md) for continuation. Start a new session with git status and the most recent local commits. Retain the fixed prompts, labels and denominators for comparable evaluation.
