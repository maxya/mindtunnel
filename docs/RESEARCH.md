# Research and competitive analysis — 2026-11-25

## Findings and implications

| Evidence | Observation | Product implication |
|---|---|---|
| [Vanna data security FAQ](https://ask.vanna.ai/data-security-faq.html); [base implementation docs](https://try.vanna.ai/docs/base/) | Vanna already generates SQL with data visibility disabled by default in its legacy API; it can explicitly expose intermediate results for more capable queries. | Schema-only planning is NOT novel. Compete on explicit, portable plan semantics and a no-return execution boundary, not text-to-SQL. |
| [Vanna 2.0 docs](https://vanna.ai/docs/) | User-aware tools, memory, permissioned database agent. | Avoid building a full database agent. Vanna is a baseline and potential integration, not a straw man. |
| [PlanTwin, March 19 2026](https://arxiv.org/abs/2603.18377) (preprint) | Abstract local environment for cloud planning, gatekeeper and disclosure controls; reported evaluation across 60 tasks. | Closest conceptual overlap. Our proposed wedge is a deliberately simple, user-owned, no-result-return portable IR and single-shot request, not novel split-agent architecture. |
| [SplitAgent, March 9 2026](https://arxiv.org/abs/2603.08221) (preprint) | Separates enterprise-side privacy processing and cloud reasoning via context-dependent sanitization. | Do not claim invention of split execution; favor data minimization over automatic sanitization. |
| [FLOWSEAL, Sept 12 2026](https://arxiv.org/abs/2609.14003) (preprint) | External information-flow enforcement; reported markedly lower leakage in their evaluated attacks. | Enforce independently of model compliance. Consider provenance/declassification only after strict one-way MVP. |
| [PrivAgentFlow, EMNLP Findings Oct 2026](https://aclanthology.org/2026.findings-emnlp.1620/) | Per-node privacy policies in web agent workflows. | Compositional leakage matters; do not expose outputs for iterative cloud planning in MVP. |
| [AgentCIScope, Microsoft Research Oct 2026](https://www.microsoft.com/en-us/research/publication/agentciscope-grounded-contextual-integrity-evaluation-for-llm-agents/) | Reports 32.5–94.4% single-run leakage among 12 evaluated agents on 936 tasks under its contextual integrity criteria. | Strong agent performance is not equivalent to privacy; test egress and metadata, not just task success. |
| [POLAR-Bench, May 2026](https://arxiv.org/abs/2605.19127) (preprint) | Privacy/utility varied by models and attacks; some small models leaked substantially. | Local inference alone does not guarantee safe downstream disclosure. |
| [OnPrem.LLM](https://github.com/amaiya/onprem), [sediment](https://github.com/camharris93/sediment) | Local document intelligence and local analytics already exist. | Do not compete on fully offline chat or dashboards; show provider-agnostic planning without sending values. |
| [MCP specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-06-18/index.mdx), [OWASP MCP security](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html) | Tool annotations are not enforcement; consent, least privilege and isolation are implementation responsibilities. | Never return private results to a cloud-backed MCP host; adapter only after explicit threat-boundary design. |

## Pattern
The literature is converging on separation of reasoning, data access, and policy. The commercial wedge is a small developer-facing artifact rather than an entirely new research architecture: publish a safe public contract; receive a bounded plan; execute privately. Inspectability, conformance, adapter portability and reproducible demonstrations are the differentiators. A generic privacy proxy is not.

## Assumptions and counterarguments
- A task, column meaning, row count, category or schema can itself be confidential. Public contract and task must be manually approved; no sample rows, inferred schema, stats, actual paths or error feedback are automatically included.
- Many analytical tasks need value discovery or semantic reasoning over the contents. Refuse or offer a separate explicitly local model path; don't claim equal quality for every task.
- Local-only tools may be adequate. The hybrid product must empirically beat a reasonable local-planning baseline on difficult feasible tasks or be simpler/more reusable than schema-only SQL. If not, pivot or stop.
- Portable plan DSL may be too narrow or cumbersome. Test time-to-first-result; extension via audited primitives only.

## Research follow-ups / launch decision
Inspect current PlanTwin implementation and license if available, Vanna current code, SQL guard projects and names/trademarks before publishing; compare actual supported behaviors, not marketing claims. Re-run repository searches for constrained cloud-to-local query plans and inspect releases/issue activity. These references validate pain and adjacent work, not first-in-world novelty or a star forecast. No paper results have been independently reproduced here. Research snapshot is based on public abstracts/docs, not an exhaustive code audit.
