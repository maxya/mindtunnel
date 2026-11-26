# Codex instructions — mindtunnel

Read `RESUME.md`, `GOALS.md`, `PLANS.md`, `docs/MVP.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/EVALUATION.md`, `docs/RESEARCH.md`, and `docs/DECISIONS.md` before implementation. `PLANS.md` is the source of truth for phase gates; `RESUME.md` records observed state. `PROMPTS.md` contains reusable orchestration prompts.

- Start with a read-only preflight: inspect the tree and Git status if initialized; run `make test` and `make demo`; inspect observed output. Distinguish current proof of concept from planned functionality.
- Use small, testable changes. Prefer stdlib and minimal dependencies. No framework, web UI, remote service, multi-agent runtime, database service, or new language without an approved need. Keep public contracts versioned and stable.
- Do not access, print, upload, or commit real private files, candidate content, preference profiles, tokens, or secrets. Tests and Codex runs use only synthetic fixtures. Never turn on network access or a cloud adapter silently.
- Work in phase order. Orchestrator plans and integrates; if supported, delegate implementation to a `grunt` worker and independent review to a `sam` reviewer; otherwise perform explicit separate implementation and review passes. No assumption that those agents exist. Address every material review finding, rerun checks, and record evidence.
- Update `RESUME.md`, `docs/DECISIONS.md` (if needed), and `harness/build-log.md` after each phase; record commands, actual results, unresolved risks and next step. A passing unit test is not a security audit or proof of product demand.
- Never invent benchmark results, research sources, test passes, or compatibility claims. Do not run on real private data through a cloud-connected agent. No pushes, publication, deployments, credentials or license adoption without owner approval. Stop at the approved phase boundary unless explicitly authorized to run the full roadmap.
