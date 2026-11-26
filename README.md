# MindTunnel (working name)

**Send the plan, not the data.** Experimental local execution protocol for cloud-assisted private analytics. The public contract and question are deliberately authored; the planner returns a bounded JSON plan, not arbitrary SQL or code. Data and results remain in the local execution path. This repository is an offline reference proof, not a finished or security-audited product.

## Quick start (no API key, no dependencies)

```sh
make test
make demo
```

Or run `python3 -m unittest discover -s tests -v` and `python3 scripts/demo.py`. Python 3.11+. Demo uses invented transactions and a hand-written plan. It prints the public request, then a synthetic local result, and rejects an extra command field. The executor is offline by design but does not impose an OS sandbox. Do not run real private data inside a cloud-connected Codex session. `private/` and `work/` are ignored but Git ignore is not access control. Use an owner-only directory outside the repo for real data after review.

## Start building with Codex
Read [RESUME.md](RESUME.md), [AGENTS.md](AGENTS.md), [GOALS.md](GOALS.md), [PLANS.md](PLANS.md), and [PROMPTS.md](PROMPTS.md). Full product requirements, architecture, security, research, evaluation and implementation guidance in `docs/`. Phase 1 is next; the proposed license and name require owner approval. No live provider integration is included yet.
