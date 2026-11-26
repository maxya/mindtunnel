# Reproducible synthetic evaluation

`heldout.json` freezes 30 feasible tasks across three schemas and 10 unsupported tasks. Sam independently authored the rows, intended plans, and expected results before this runner was implemented. The file is copied byte for byte from that review handoff. Its SHA-256 is `054dd9272369591d82e7fe2bac8ca9a50e593f88f13ff33e974153b85aedb12b`. The runner checks this hash before evaluation. Questions, fixtures, or labels must remain fixed for a comparable run.

`offline-results.json` contains one actual local run, including exact public request strings, byte counts/hashes, returned results, raw case classifications, and measured nanosecond timings. The observed results are 30/30 exact gold executions, 30/30 exact trusted SQL executions, 53/53 adversarial rejections, and 10/10 correct unsupported responses from the mock. The unchanged `synthetic-v1` grammar mock returns unsupported on all 30 feasible natural-language tasks, producing 0/30 exact plans and 0/30 exact results. Its narrow grammar was preserved through this evaluation. These figures describe the offline components exercised here. Cloud-model and local-model quality, provider latency/cost, and outside-tester outcomes remain unmeasured.

## Run locally

Run from the source checkout with Python 3.11+ and the standard library. Choose a fresh output path in an existing owner-controlled directory.

```sh
python3 -m harness.evaluation.runner run --out work/evaluation-new.json
make test
```

The runner creates temporary synthetic CSV files, checks gold plans with the local interpreter, and runs the analyst-authored constants in `sql_baseline.py` against an in-memory SQLite table with the exact public aliases. Only those trusted constants are executable SQL. Imported model responses are accepted exclusively as bounded v1 plans or the strict unsupported object. The runner provides no SQL input interface. The SQL baseline demonstrates local query correctness and semantic coverage. It does not measure a model generating SQL, reproduce Vanna, or establish equivalent product usability. A connection is explicitly closed after each case.

Gold timing includes temporary CSV setup and interpreter execution. SQL timing includes database creation, insertion, and query execution. Mock timing measures direct invocation of the public deterministic grammar function and excludes result scoring. It exercises the same grammar as the isolated mock adapter, while isolation is verified separately. Timings use a local monotonic nanosecond clock. The automated run requires zero manual interventions after invocation. Human labeling effort, provider/model latency, model cost, and time to first success are recorded separately when measured. Repeated runs produce new timestamps and timings while preserving the fixture and comparator semantics.

## Export public requests and import responses

Export to a new directory. It contains 40 numbered requests plus an index of their byte counts and hashes. Each request is exactly the UTF-8 output of the normal `mindtunnel request` CLI for that case. The stable mixed ordering and generic filenames carry no feasible/unsupported label. Provide only the exported directory to the planner. Keep this repository's labels, source rows, mappings, gold plans, expected results, and prior scores outside that interaction.

```sh
python3 -m harness.evaluation.runner export --directory work/public-evaluation
```

Use one fresh planner interaction per request. Freeze the provider/model, prompt, settings, date, and any interventions before running. Save each raw response in a separate responses directory using the matching numbered filename, such as `case-001.json`. The response file must contain one raw JSON plan or exactly `{"unsupported":true}`. The scorer rejects wrappers, code fences, duplicate keys, booleans as integers, unsupported extra fields, and responses exceeding 64 KiB. It never repairs a response or sends execution feedback to a provider.

```sh
python3 -m harness.evaluation.runner score --directory work/model-responses --label 'provider model date settings' --out work/import-score.json
```

The import scorer reports missing responses, invalid JSON/plans, structured unsupported responses, valid plans, execution failures, and unexpected plans on unsupported tasks. Feasible and unsupported status counts are separate. Filesystem read failures are classified without including their raw diagnostics. Extra directory entries are counted. Record provider identity/settings and measured latency/cost/interventions alongside the score artifact. The free-text label records what the operator supplies and does not independently authenticate a provider or model.

## Scoring rules and gate interpretation

`plan_exact` means equal validated v1 semantics under canonical JSON, ignoring object-key order and JSON whitespace. This deliberately conservative comparator requires the same version, contract hash, grouping, aggregate, and typed equality filter. It does not treat different filters or operations as equivalent because they happen to produce the same result on six rows. `result_exact` compares the deterministic v1 output with the independently labeled expected result. `plan_and_result_exact` requires both. Tests include a semantically different plan that coincidentally returns the gold zero result and verify that it fails the combined metric.

Unsupported tasks require the exact unsupported object. A well-formed executable plan on such a task is an unexpected plan. Returning unsupported on a feasible task is a planning failure. An invalid response and a valid plan that fails local execution have distinct classifications. All 30 feasible tasks remain in the denominator, including missing or rejected responses.

The 85% model-quality gate remains pending an actual frozen external or local model run. The mock's 0/30 result shows its unsupported natural-language coverage. It supplies no evidence about frontier-model utility. Outside testers, human understanding of the boundary, macOS installation evidence, release decisions, and runtime isolation evidence are separate requirements. Passing this offline harness alone cannot close those gates.
