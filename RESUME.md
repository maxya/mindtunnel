# RESUME — MindTunnel

**As of 2026-11-25 · Phase 0 reference complete locally; owner review pending.**

## Vision and decision
A portable public contract → untrusted constrained plan → private local execution. Not another SQL chatbot or privacy proxy. A near neighbor (PlanTwin) already researches abstract planning environments; Vanna already does schema-only SQL. Our differentiation hypothesis is a simple inspectable, one-way plan boundary and open conformance contract. Read `docs/RESEARCH.md` before making novelty claims. The name is provisional, proposed Apache-2.0 not approved.

## Implemented / tested
- Python 3.11+ stdlib CLI `request` and `run`, strict JSON/contract/plan validation; CSV count/sum, string grouping, optional typed equality filter, resource limits, local exclusive output.
- Synthetic transactions, public alias contract, private mapping example, known plan/expected result, malicious plan; no cloud credentials or networking code.
- `bash bootstrap.sh` on Linux / Python 3.13.5 passed 10 unit test methods and synthetic demo. See `harness/phase-00-verification.txt` and build log. No macOS execution or real provider calls.
- All required design, MVP, security, research, implementation and evaluation documents, editable diagrams, phase gates and Codex prompts supplied. CI config exists, not executed in actual CI.

## Not implemented / blockers
Remote planner adapter, cryptographic approval receipt, OS process isolation/packet capture, production-safe path hardening, formal schemas/fuzz corpus, unsupported-response UX, richer operations/local report, benchmark/pilot, license/name review, independent security review. The request builder cannot automatically establish that a manually authored task/schema is non-sensitive. A cloud-connected coding agent may read local files/output even if executor does not call a network. No use with real private data yet.

## Next session
Read AGENTS.md, GOALS.md, PLANS.md, docs/MVP.md, ARCHITECTURE.md, SECURITY.md, EVALUATION.md, RESEARCH.md, DECISIONS.md, PROMPTS.md. `bash bootstrap.sh` with synthetic fixtures, inspect Git status (not initialized in archive). Confirm P0 output; propose/execute P1 only with owner approval. Add JSON Schema and conformance vectors, test resource limits, strict type cases and file permissions; independent review, fix blockers, update this file and build log. See phase gates in PLANS.md. Do not start provider integration before P1 gate.

## Owner decisions
Approve name and license, language choice (Python proof vs eventual Go port), first planner provider/manual transport, and test data/security boundary. Default recommendation: keep Python until differentiation and benchmark are validated; no external publication or credentials. Time estimates are hypotheses, not deadlines.
