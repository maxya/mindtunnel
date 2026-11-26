# MVP specification — version 0.1 target

## Product experience and use cases
1. User defines a public contract of aliases/types separately from a local CSV mapping. `request` prints exact public payload; user reviews and manually gives it to chosen model. Model returns plan JSON, no tools. User saves response locally.
2. User runs `run` locally, receives a private aggregate JSON file. Local renderer (planned) can present a table/CSV; no automatic follow-up to cloud. Reuse the same plan on fresh data with same contract.
3. Unsupported task (e.g. “find unknown categories then ask the model to classify them”) returns a clear unsupported indication, not hidden fallback. For private questions use a separate wholly local planning path; not MVP.

First demo: synthetic transaction data, count rows and sum integer cents by category. Planner never sees merchant strings or real header names. Show request, valid plan, result and rejected malicious plan. Use `make demo`; the supplied plan is hand-authored, not a live model response.

## Prioritized backlog
| ID | Requirement | Acceptance | Phase |
|---|---|---|---|
| MT-01 | Explicit public contract | Valid aliases/types, bounded; no inferred private values | 0/1 |
| MT-02 | Strict versioned plan | Exact keys, hash binding, reject malformed and unknown ops, duplicates | 0/1 |
| MT-03 | Read-only interpreter | Correct exact aggregation and equality filter; deterministic result; source unchanged | 0/1 |
| MT-04 | Private result sink | Exclusive write, generic terminal status, no model/network | 0/1 |
| MT-05 | Egress review | Review exact bytes + hash and destination; explicit opt-in remote or manual path; no private mounts | 2 |
| MT-06 | Planner quality | Model can construct conformant plans or structured unsupported response; no retry with results | 2 |
| MT-07 | More useful tabular operations | Projection restricted to local display, count/sum/min/max, multi-filter; each operation has conformance tests; optional if benchmarks require | 3 |
| MT-08 | Usability | Local report/table, setup docs, no private content in logs | 3 |
| MT-09 | Evaluation | Gate in GOALS.md; raw evidence and baseline comparisons, adversarial tests | 4 |
| MT-10 | Release | License/name decision, reproducible install, security review, public synthetic demo | 5 |

Phase 0 delivers a small proof, not MT-05–10. All gates are proposals. Avoid expanding domains before evidence. A remote adapter may be omitted from initial release if manual transfer is the safest usable workflow; document that explicitly.

## Public API evolution
Version integer + strict parser. JSON Schema is documentation/conformance input; implementation must enforce semantic checks. Break incompatible contracts with version bump. Preserve rejected-plan fixtures. Optional later adapters use only core IR, with no plugin-supplied executable code. Never silently downgrade privacy policy.

## Open questions
Is the strict public contract expressive enough for real tasks? How much review friction is acceptable? Does a local model solve the same cases sufficiently? Is the architecture simpler than using schema-only SQL in Vanna? Validate these before further investment.
