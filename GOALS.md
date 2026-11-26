# MindTunnel — goals and problem statement

**One-line promise:** send the plan, not the data. Ask a powerful model to design an analysis; run its constrained plan on your own machine without returning the private inputs or results to the planner.

## Problem
Cloud models can generate excellent analysis programs, but agent workflows often expose source data, schemas, sample rows, tool responses, logs and derived facts to those models. Local models avoid that exposure but may be expensive or less effective at planning. Existing schema-only SQL tools already solve a slice of this problem. The wedge is not another analyst chatbot: it is a portable, independently validated, data-free planning contract with a local executor and explicit separation between what may leave and what must not.

## User and first job
A developer or privacy-conscious analyst with a local CSV (e.g. a transaction export) wants aggregate answers using a frontier model's planning capability without sharing row contents. They can publish a deliberately designed abstract contract (aliases and types) and a non-sensitive task. The result is a local file. The model has no opportunity to inspect results and retry with private context.

## Goals
1. Show the exact request eligible for egress, without inspecting private inputs; human approves it outside the executor.
2. Accept a provider-neutral, typed, bounded plan; reject all undeclared operations, fields, and versions before execution.
3. Execute deterministic, read-only tabular operations offline; output locally; do not call a model with results, errors or raw data.
4. Run on macOS and Linux, no API key for the demo, no required GPU, service, account or telemetry.
5. Publish a small open plan contract plus conformance fixtures after a license/name decision. It must integrate with existing agents, not replace MCP.

## Non-goals
Arbitrary private reasoning, private document summarization, source-code repair, confidential computing, encryption of cloud model weights, anonymous or differential privacy guarantees, unrestricted SQL/Python/shell, an enterprise data platform, automated data declassification, or agent tool access to raw results. No claims of protecting against a compromised OS, malicious installed binary, cloud-connected terminal capture, or user-disclosed secrets.

## MVP gate (targets, not results)
- At least 30 independently labeled public-task cases over synthetic fixtures; at least 85% exact plan+result success on feasible tasks, report infeasible tasks separately. Compare with hand-authored gold and schema-only SQL baseline, not a vague chatbot.
- At least 30 adversarial plan cases, every unsupported action rejected; canary raw values absent from captured outbound request, normal logs, and remote tool responses. Tests cannot establish absolute non-leakage.
- Demo in under 60 seconds excluding optional model latency, clean install on macOS/Linux, no mandatory cloud.
- Five outside testers attempt the demo with invented data; at least three can explain the trust boundary without help. Do not claim demand before results.
