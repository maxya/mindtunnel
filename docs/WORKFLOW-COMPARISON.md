# Comparing the disclosed inputs

Across 40 frozen questions on three invented CSVs, MindTunnel's reviewed public requests contained the public question, aliases/types, contract digest, version and planner instructions. The direct-answer comparator attached the same question, the local mapping and the entire six-row CSV. We constructed these messages locally. No request was sent to a model.

| Workflow | Planner sees | Private execution and feedback | Measured evidence |
|---|---|---|---|
| Direct cloud answer with attached CSV | Public question, raw headers, mapped aliases and all six source rows | Provider could compute or return an answer from those rows | 346–432 serialized bytes per question, 240 row attachments across 40 messages. No provider answer or latency measured. |
| Schema-only SQL | Public question and aliases/types suffice to author the benchmark queries | The benchmark executes fixed analyst-written SQL over an in-memory synthetic SQLite table. The user-facing interpreter accepts v1 plans only. | SQL agreement with independent labels is reported by the evaluation harness. This comparator has neither a live SQL-generating model nor an isolation guarantee for arbitrary SQL. |
| MindTunnel | Explicit public question, aliases/types and fixed protocol instructions | A separate local process applies the validated plan to the CSV. No automatic results or private-error feedback. | 709–790 serialized bytes per question, zero attached source rows. The Linux capture test separately checked the actual mock transport for one approved task. |

A larger public request can disclose fewer categories of information. A question such as “count rows whose category equals food” discloses that literal even when the CSV remains local. The byte totals describe these specific encodings. They cannot measure semantic leakage, usability or model quality. A conventional analyst can also run schema-only SQL without sending rows. Acceptance still depends on a comparison of actual planning success and user experience.

Reproduce the per-case measurements using `python3 harness/evaluation/disclosure.py`. See [raw local measurements](../harness/evaluation/disclosure-results.json).
