# Implementation guide

## Setup
Python 3.11+; standard library only at runtime. `make test` / `make demo` or `python3 -m unittest discover -s tests -v` and `python3 scripts/demo.py`. Optional editable install `python3 -m venv .venv; source .venv/bin/activate; python -m pip install -e .` requires setuptools and may fetch packaging dependencies; not needed offline. Do not install unreviewed packages.

## Code map
`mindtunnel/core.py` owns strict parsing, contract, public request, plan and interpreter. `mindtunnel/cli.py` owns user path arguments, bounded loads and local output. `examples/` is synthetic. `tests/` verifies core and CLI. `scripts/demo.py` executes the proof without a network provider. Keep planner integration separate (e.g. `mindtunnel_planner/` with no import of executor modules) and test it in a separate process. Split modules if it reduces coupling, not for architecture theater.

## P1 tasks
1. Freeze contract/plan schemas and add positive/negative vectors. Use duplicate-aware JSON parsing; booleans not integers. Validate semantic references after structure; avoid mutable validated plans or revalidate immediately before execution.
2. Validate file/row/cell boundaries, encoding, malformed CSV, type errors, source immutability, resource exhaustion; fail closed with stable error codes. Test execution under no network and restrict permissions on output.
3. Add `validate` command if useful; never emit private diagnostic content. Avoid arbitrary SQL, eval, shell, plugin execution. Document public task/contract limitations.

## P2 tasks
Build exact reviewable request representation; use byte hash plus provider/model destination in an approval receipt; expiry and one-use token (local approval), no implicit chat history. Planner subprocess sees only public approved bytes and provider token, no private paths; executor sees plan+contract+local mapping/data and no network. For remote API, explicitly disable extra tools, uploads, web, state retention where supported; do not promise provider privacy or no retention. Use a mock provider fixture; actual endpoint requires owner approval. Reject unsupported response or invalid plan without returning private errors. Give user actionable generic diagnosis locally.

## P3–5
Implement only primitives with concrete benchmark cases. Add renderer with proper escaping and no external URLs/scripts. Test with synthetic datasets. Compare alternative approach fairly; record limitations, actual user feedback, license and naming review before public release. No vendor-specific lock-in. Keep CI offline except checkout/tool setup.

## Codex workflow reference

[OpenAI: Iterating Development Workflows with Codex (Aug 3, 2026)](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex) describes durable AGENTS.md, GOALS.md, PLANS.md, PROMPTS.md and phase-specific evidence. This repo follows an adapted lightweight version. `BOOTSTRAP.md` contains the initial prompt.

## v1 conformance and local files

`schemas/` contains JSON Schema 2020-12 structural descriptions for the public contract, plan, and result. Runtime validation also enforces unique field IDs, contract hash identity, reference types, UTF-8 scalar text, duplicate-key rejection, integer lexical syntax, and byte limits. A schema validator alone cannot establish these properties. `tests/fixtures/conformance-v1.json` freezes accepted plans and rejected plan/parser cases. The standard-library suite adds seeded aggregation properties, actual resource boundaries, malformed CSV, generic errors, and local file failure/concurrency checks.

All input files must be regular files. The POSIX reader uses directory descriptors and refuses symlinks in every path component, including the final file, and refuses `..` components. Supply physical paths. On macOS, `/tmp` and `/var` commonly resolve through symlinks, so obtain the physical path of an owner-selected directory before using it. Bundled temporary examples resolve their freshly created directories. The reader takes a bounded snapshot and leaves source files untouched. Path validation is independent of plan validation, and plans cannot select any paths.

The result writer creates a random temporary file in the selected destination directory with mode 0600, flushes it, and publishes it using an exclusive hard link. An existing file or symlink is preserved. Recoverable write/publication errors remove the temporary file and expose no partial destination. An abrupt process or machine failure may leave a 0600 temporary file. Use a filesystem supporting POSIX directory descriptors and hard links. Keep the destination directory under owner control. Directory entry durability after power loss is outside this guarantee.
