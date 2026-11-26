# Implementation roadmap

P0 verified, P1 accepted, P2 next. Updated 2026-11-26. See [execution ledger](todo/mvp-implementation-plan.md) and [observed results](RESUME.md).

Estimates are planning ranges, not commitments. Bootstrap (P0) is supplied. Target: focused public v0.1 in ~4–6 weeks of part-time work if quality gates pass; do not promise dates. No automatic pushes or license selection.

| Phase | Work packages / dependencies | Gate / evidence |
|---|---|---|
| P0 Foundation (delivered proof) | CLI, strict parser, bounded CSV aggregate, request builder, synthetic fixture, offline tests, docs | `make test`, `make demo`; record observed output. Owner review pending. |
| P1 Harden contract (2–4 sessions) | Add JSON schema files and conformance vectors, malformed/limit cases, property tests, deterministic result semantics, safe permissions; inspect no network imports in executor | Every test passes; independent review, red/green cases for known gaps; no private data. |
| P2 Planner boundary (3–6 sessions) | Public-only structured prompt, unsupported response, separate opt-in provider process/adapter, approval bound to exact bytes/destination/model, mock provider and outbound capture, network-isolated executor guide | No canary egress; manual fallback; no private files available to planner; errors remain local. Review isolation limits and provider terms. |
| P3 Useful analytics (3–5 sessions) | Prioritize actual benchmark cases; add min/max or multiple filters only if justified, local renderer, documented mappings and demo | Conformance for each new primitive; no expansion of egress. |
| P4 Evaluate (3–5 sessions) | Freeze 30+ cases and 10 unsupported, compare baseline, measure privacy/utility, recruit 5 testers | GOALS.md gates; publish raw synthetic evidence; unresolved security failures block. |
| P5 Release (2–3 sessions) | Name/license owner decision, packaging, reproducible instructions, SBOM/dependency review, tagged release plan, demo GIF script, security reporting | Maintainer approval, tests clean in macOS/Linux CI, no private data in archive. |
| P6 Later, separate approval | Audit-safe plan reuse, multi-table types, constrained local semantic adapter, optional MCP receipt transport, Go/Rust port only if evidence | No roadmap expansion until adoption/usefulness and security are proven. |

## Implementation order within each phase
Review previous evidence -> small design and acceptance tests -> implement -> independent review -> fix -> rerun tests/demo -> update RESUME.md and log -> owner gate. No skipping unresolved blockers.

## Public positioning
README demo: "This model has never seen the CSV. Here's the entire request. Here's a malicious plan rejected. Here's the result on my computer." Use a fake dataset and captured request. Ship conformance examples first. Reach privacy, local AI, data engineering and agent communities with measured results, not speculative marketing. Initial target 10 independent users and 100 GitHub stars; metrics are aspirational. Watch install success, repeat usage, independent integrations, issue quality. Avoid hosted service unless demand is proven.
