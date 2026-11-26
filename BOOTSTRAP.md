# Start on your laptop

1. Extract the standalone `mindtunnel.zip` into your normal development workspace. `cd mindtunnel`.
2. Run `bash bootstrap.sh` (or `make test && make demo`). Python 3.11+ is the only runtime requirement; this does not install packages or call a provider. Use only bundled synthetic fixtures.
3. Optional: initialize a local Git repository (`git init`); inspect `.gitignore` and the tree. Do not commit private data or publish before approving the license and name.
4. Start your installed `codex` from this directory. `AGENTS.md` contains persistent project instructions. Paste the first-session prompt from `PROMPTS.md` for an independent read-only review, or the full MVP orchestration prompt if you explicitly authorize all MVP phases.
5. Review P1 scope and gate in `PLANS.md`. The bootstrap is a verified offline reference, not a finished MVP. Keep real data outside the agent workspace and run sensitive experiments only after the security gate.

## Recommended first prompt

Read AGENTS.md, RESUME.md, GOALS.md, PLANS.md, PROMPTS.md and the docs. Perform the read-only preflight, independently verify the bootstrap, identify gaps, and propose P1 implementation/test scope. Do not write, publish, use real data, or add cloud access until approved. Use independent review (sam, if available) and record actual evidence. Then await phase authorization.

This handoff does not require a specific Codex model, subagent name, Git host or account. The project can be developed on macOS/Linux and eventually integrated into existing agents. No Git remote or credentials are configured.
