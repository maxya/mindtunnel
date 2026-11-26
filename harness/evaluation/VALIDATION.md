# Manual multi-model validation protocol v1

This protocol prepares public requests and stores owner-side evidence for a frontier cloud model, a smaller cloud model, and a local model. Each run may register one through twelve available models. Assign each its actual `frontier_cloud`, `small_cloud`, or `local` role. Unavailable model classes remain outstanding comparisons. The code provides preparation, local recording, strict scoring, and result reports. Model interaction and exact-byte transfer are performed manually by the owner.

The frozen benchmark remains `heldout.json` with SHA-256 `054dd9272369591d82e7fe2bac8ca9a50e593f88f13ff33e974153b85aedb12b`. It has 30 feasible cases and 10 unsupported cases. Preserve all cases, intended plans, expected results, public questions, and the 85% primary feasible-task threshold. At least 26 of the 30 feasible cases must have both exact validated plan semantics and exact results to reach that threshold. Record unsupported and unauthorized behavior separately. This tooling supplies no actual model result until an owner performs and records the model run.

## 1. Register the run before collecting responses

Start from the checkout with an owner-controlled, Git-ignored work directory.

```sh
mkdir -p -m 700 work
cp harness/evaluation/validation-spec.example.json work/validation-spec.json
```

Edit `work/validation-spec.json` and fill in the exact provider, model/version, runtime/quantization for a local model, and settings. Remove unavailable models or add comparison models before registration. Settings must contain public configuration values. Keep credentials outside this workflow. Use `evidence_kind` equal to `manual_model_run` for owner-performed model observations. Use `synthetic_pipeline_check` for fixture-driven tooling checks, which always receive a synthetic-only gate label.

Choose the `ir` comparator for MindTunnel's v1 plan generation. Choose `sql` in a separate run specification for the schema-only SQL-generation comparator. Freeze the same models/settings across arms where available. The SQL arm has its own published output grammar and request hashes. It uses the same public contract, task, cases, order, and expected results. The two arms retain their own first and retry measurements.

Choose `retry_policy` equal to `none` or `one_blind_retry_all_cases`. The second policy predeclares one additional fresh interaction for every case. It uses the exact same request bytes, model, settings, and independent context as the first interaction. Collect the complete second pass regardless of which first responses appear correct. Keep validation results, source data, errors, and earlier responses out of every planner interaction. Avoid inspecting owner-side scores until both declared passes have been collected.

```sh
python3 -m harness.evaluation.validation prepare --spec work/validation-spec.json --directory work/model-study
```

The new directory contains `public/`, private `registration.json`, and private record directories. Registration binds the fixture, model configuration, retry policy, and request-set hash. IR requests are byte-for-byte the normal `mindtunnel request` CLI output. SQL requests contain the public aliases/types, public task, contract hash, and a fixed grammar description. The numbered filenames use the existing mixed ordering. The public directory contains no source rows, real header mapping, labels, gold plan, expected result, or feasibility flag. Keep the rest of this repository and the registration/records/report outside the planner context.

## 2. Transfer and collect each request manually

Review each complete public request before any outbound transfer, following MindTunnel's manual approval workflow. Transfer only its exact UTF-8 bytes to the registered model in a fresh context with tools, retrieval, file access, conversation history, and additional context disabled. A provider interface must preserve the registered request text. Record any required provider framing/settings in the run specification before starting. If the interface adds unrecorded context or changes the request, treat that observation as outside this protocol.

Save the model's exact response content into an owner-side file. Preserve invalid JSON, code fences, extra fields, or unsupported responses exactly. Keep provider transport envelopes and account identifiers outside the public export. Capture input/output token counts and provider usage from the owner-visible usage record when available. Measure response latency in integer milliseconds using an owner-controlled timing source with a documented start/stop definition. Estimates remain unknown.

Optionally prepare an owner-side metrics JSON object with exactly these fields. Null records unavailable observations.

```json
{"latency_ms":null,"input_tokens":null,"output_tokens":null,"cost_microusd":null,"interventions":null}
```

`cost_microusd` is an integer count of millionths of a US dollar. It records an observed charge and makes no pricing assumption. `interventions` counts extra owner actions beyond the prescribed transfer/save procedure. Describe what counted in the accompanying owner notes. A repair that changes request bytes or exposes private execution feedback makes the interaction outside this protocol, even if an intervention count is supplied.

Select one case at a time. The following command records case 001, after you have reviewed `public/case-001.json`, transferred its exact bytes, and saved that response as `work/raw-response.txt`. Compute its reviewed-byte digest and compare it with the case entry in `public/index.json`.

```sh
reviewed_request_sha256=$(python3 -c 'import hashlib,pathlib; print(hashlib.sha256(pathlib.Path("work/model-study/public/case-001.json").read_bytes()).hexdigest())')
python3 -m harness.evaluation.validation record --directory work/model-study --model frontier --case 1 --attempt 1 --response work/raw-response.txt --request-sha256 "$reviewed_request_sha256" --metrics work/metrics.json --attest-same-bytes-blind
```

The attestation records the owner's statement that the interaction used the registered bytes/model/settings and fresh context without source data, result/error feedback, previous response, or hidden labels. Omit the metrics option to record all metrics as unknown. An unattested record remains available for inspection and scoring, while its first-pass observation remains ineligible for the primary gate label.

For a declared retry, use `--attempt 2`, the same case hash, and a fresh response file from a fresh interaction. Its first record must already exist and retain valid bindings. The recorder checks the actual exported request bytes before accepting either attempt. Preparation rejects a registration exceeding 64 KiB before creating the study directory, so every accepted registration remains readable. Records are exclusive, atomic, and private. A repeated record command preserves the existing record. Registration changes invalidate earlier record bindings. A raw response may be captured up to 1 MiB so oversized plan responses can still have a complete hash. Responses exceeding the 64 KiB plan parsing limit score invalid. Captures above 1 MiB are rejected at recording and remain missing from the scorer until a separately documented handling decision is made.

The code records the response's SHA-256, byte count, exact raw bytes encoded in base64, request hash, registration hash, model, case, attempt, metrics, and owner attestation. It provides no transport, provider authentication, or independent proof of what a manually operated interface actually sent. Filesystem ownership and the local operator protect these records.

## 3. Score locally after collection

```sh
python3 -m harness.evaluation.validation score --directory work/model-study --out work/model-study-score.json
```

The scorer retains all 30 feasible cases in every model/attempt denominator. A retry whose first record was later removed or corrupted is marked `unpaired_retry` and excluded from combined success and recovery counts, while its raw hash and semantic inspection remain available under `unpaired_observation`. Unpaired retries contribute zero to summary validity and success counts. Their recognized unauthorized-operation diagnostics remain visible. It distinguishes missing records, invalid record bindings, invalid responses, structured unsupported responses, valid plans, unexpected plans on unsupported tasks, and local execution failures. Accepted plans are included in the private report together with raw response hashes. Invalid response contents remain only in the private raw record and are excluded from normal terminal logs.

Per-attempt reports include validated IR counts, exact semantic plans, exact results, their intersection, correct unsupported outcomes, recognized unauthorized requests, hallucinated aliases/operations, response counts, and metric observations. A plan's semantic match compares the complete validated v1 IR with the independently authored gold IR, ignoring JSON whitespace and object-key order. A different plan that coincidentally returns the same fixture result fails the combined metric. SQL responses are translated to that same IR for semantic comparison and evaluated independently for result comparison.

Diagnostics identify recognized forbidden operation/path/tool/code keys, an executable SQL field in an IR response, unsupported operation names, undeclared field references, and recognizable denied SQL functions/tables/keywords. These are descriptive counts from parsed structures or a bounded diagnostic lexer. Malformed responses may have no reliable intent classification. Every rejected response remains invalid regardless of diagnostic counts. The strict validators determine acceptance. An absent diagnostic flag supplies no safety conclusion.

The first-attempt gate observation depends exclusively on complete attested first records. Missing optional retries leave first-attempt figures intact. Cloud IR arms may receive an owner-reported threshold label. Local IR runs receive a local-comparison label, and SQL runs receive a SQL-comparator label. Synthetic checks retain their synthetic label. These labels describe owner-side evidence and do not certify provider identity, complete security acceptance, or project release readiness.

A separate retry summary reports completion, attestation, and the same metrics. `success_within_declared_attempts` records whether either declared attempt succeeded. `retry_recoveries` identifies each failed first case that succeeded on retry, and `cases_benefiting_from_retry` counts them. Inspect each case's retry attestation and missing/invalid status before drawing a protocol-level conclusion. Combined success is an exploratory comparison and never substitutes for the frozen first-attempt threshold. Known metric totals/means are reported alongside known and unknown observation counts. Missing observations remain null.

## Schema-only SQL comparator boundary

The public grammar allows one `SELECT` against the synthetic `sample` table, exact public aliases, count or sum, an optional typed equality predicate, and the declared grouping/order form. Ungrouped sum requires `COALESCE(SUM(alias),0)` to define empty-input semantics. Grouped sums use `SUM(alias)`. String literals use SQL single quotes and doubled single quotes. Integer literals fit signed 64-bit input. Whitespace and keyword case may vary. Comments, joins, subqueries, writes, extra statements, arbitrary functions, and other clauses are rejected. The response must be exactly `{"sql":"QUERY"}` or `{"unsupported":true}`.

The parser constructs a validated v1 IR. The evaluator then composes its own allowlisted `SELECT` using known quoted aliases and bound literal parameters. It runs that locally composed query on a query-only in-memory SQLite database created from the frozen synthetic fixture. Model-supplied SQL text is never passed to SQLite. Tests replace the product interpreter with a failure and still obtain all 30 gold results through this independent SQL path. Empty sums, lexicographic grouping, multiline/Unicode strings, and SQL-looking string literals have targeted checks.

This constrained SQL-generation arm measures the declared grammar on the frozen cases. Its expressiveness matches the selected v1 primitives and excludes broader SQL capabilities. It does not reproduce a general SQL agent or a full Vanna workflow. SQLite's integer sum limits also differ from MindTunnel's exact Python totals outside these small-integer fixtures. Any such arithmetic failure is an execution failure. Extend comparisons through a newly registered, independently labeled study before making broader utility claims.
