# Verification and research evaluation

## Correctness suite
Use synthetic CSV with Unicode, quotes, embedded newlines, empty categories, malformed/missing columns, integer boundary and invalid integer. Gold expected outputs hand-derived by independent reviewer. Test grouped/ungrouped count, sums with negatives, empty filtered groups, determinism, file and row limits, no source modification, output no-overwrite. Reject unknown version/op/keys, duplicate JSON key, unknown aliases, wrong literal type including boolean-as-integer, malformed mapping, group overflow, file paths in plan and arbitrary code. Add property/fuzz tests for parser and CSV limits; no production data.

## Privacy measurement
1. Generate unique synthetic canaries in private header, path, row, output. Capture exact planner bytes, fake provider request, logs/stdout/stderr, adapter return values, temporary files. Compare against all canaries including encodings; inspect full payload allowlist. Verify request builder works with data unavailable. Reject approval hash or destination changes. Test malformed plans that request exfiltration/echo or retry on private failures. Network deny executor in a sandbox; verify via denied socket and packet capture. No test implies comprehensive security.
2. Treat public contract and task as disclosed by design. Track bytes and manually annotate disclosure categories, not a misleading privacy percentage. Result of execution must not be used to repair a cloud plan. Log capture should be synthetic and remain local.

## Utility benchmark
At least 30 feasible held-out tasks over 3 synthetic schemas; 10 unsupported requests. Freeze tasks, gold outputs, planner configuration and IR version before evaluation. Compare (A) hand-authored gold, (B) cloud planner with public contract only, (C) local model with same public contract, (D) schema-only SQL baseline such as Vanna or carefully specified equivalent, evaluated locally on synthetic data. No production data in baseline. Measure exact result match (normalize order and integers), invalid/unsupported rate, latency, manual interventions, request bytes, cost if available, time-to-first-success. Report denominators and provider/model/date. No tuned test-set prompt. Include fail-closed rates and utility loss; distinguish planning failure, invalid plan, unsupported scope, execution failure.

## Kill criteria
If cloud plan success is below 85% on supported cases after reasonable prompt design, or schema-only SQL provides equal usability and equivalent isolation with less complexity, stop and reconsider. If any privacy gate fails, block sensitive use/release until remediated. If testers cannot use workflow in under five minutes, simplify, don't add unrelated features.

## Recorded local measurements

The [evaluation harness and scoring instructions](../harness/evaluation/README.md) cover the frozen tasks, raw results and blinded public requests. The [workflow comparison](WORKFLOW-COMPARISON.md) measures disclosed categories and bytes. The [pilot protocol](PILOT.md) defines participant tasks and unaided scoring. External model and participant measurements are pending.

## Real-model study

Use the [manual collection and scoring workflow](../harness/evaluation/VALIDATION.md) and the [operator handoff](../validation/MODEL-RUNS.md). Each model is preregistered and receives one public request per fresh tool-free interaction. Reports keep first-attempt results, retry outcomes and unknown metadata separate. The SQL arm accepts a restricted grammar and compares results using trusted parameterized queries on a synthetic in-memory database.
