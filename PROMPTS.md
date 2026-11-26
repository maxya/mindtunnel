# Reusable Codex prompts

## First session — read-only preflight
Read AGENTS.md, RESUME.md, GOALS.md, PLANS.md and docs/*.md. Inspect the tree and Git status; run make test and make demo with synthetic fixtures. Compare results with harness/build-log.md. Identify actual gaps, conflicts and assumptions. Propose the next phase scope, test cases and gate. Do not write until the owner approves the phase.

## Full MVP orchestration (only when explicitly authorized)
Act as lead engineer for mindtunnel. Implement phases in PLANS.md in sequence through the MVP gate, excluding stretch goals. Use the existing local implementation, not a rewrite. For each phase: preflight, bounded plan and acceptance criteria; use grunt for implementation if available; use sam for independent security/code review if available; otherwise use distinct implementation and review passes. Fix all blocking findings, rerun tests and demo, record concrete evidence and update RESUME.md. Do not bypass critical security or evaluation gates. Do not push, publish, deploy, use private data or add a cloud provider without specific approval. Stop and explain if blocked; do not falsely mark phases complete. Report all open risks and exact commands to reproduce results.

## Review prompt
Review only the current phase diff and contracts. Prioritize trust boundaries, malformed input, failure recovery, privacy of logs/output, dependency changes, test adequacy and compatibility. Provide severity, file/line, reproducible case and suggested fix. Do not modify files in the review pass. Recheck fixes and distinguish tested from hypothetical issues.

## Resume prompt
Read RESUME.md and harness/build-log.md, then compare with current code and observed test results. Continue the next incomplete approved phase only. Keep scope stable, update the handoff, and explicitly state unresolved blockers.
