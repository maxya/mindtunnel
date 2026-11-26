# MindTunnel

**Send the plan, not the data.** MindTunnel lets a planner design a small aggregate calculation from an explicitly public question and alias/type contract. Its local Python interpreter checks the resulting v1 JSON plan and runs it against a CSV. It writes the result to a private local file. The planner has no result or error feedback channel.

**Experimental release candidate.** On Linux, the synthetic workflow passed from source and from clean package installs, including Python 3.11.2. Actual planner quality, participant usability, native macOS and hosted CI results, and release sign-off remain open. The bundled planner is a deterministic mock. Manual transfer supports a planner chosen by the owner.

## Run the synthetic demo

From the source checkout with Python 3.11 or newer:

```sh
make test
make demo
```

The demo uses the Python standard library and runs offline. It shows the complete public request, executes a supplied plan, verifies totals of 2200 and 3000 cents, renders the local report and rejects an unexpected command field. The demo deliberately displays invented results. Normal CLI commands write results to an owner-selected file and print generic status.

## Run a calculation

Use a new directory for the output. The CLI refuses to overwrite existing files. Supply physical paths without symlinks or parent traversal.

```sh
mkdir -m 700 work
python3 -m mindtunnel.cli request --contract examples/contract.json \
  --task 'Sum amount_cents by category' > work/public-request.json
python3 -m mindtunnel.cli run --contract examples/contract.json \
  --mapping examples/mapping.json --data examples/transactions.csv \
  --plan examples/plan.json --out work/result.json
python3 -m mindtunnel.cli report --result work/result.json --out work/report.txt
```

Inspect every alias and the full task before manually transferring a request. Only the public contract and approved question belong in the planning interaction. The example uses a hand-authored plan. The separate mock workflow previews the exact bytes, destination and model, consumes an expiring approval and compares the captured bytes with the preview. [Planner workflow](docs/PLANNING.md)

The ordinary executor runs with the local user's permissions. The optional Linux launcher enforces filesystem and network isolation for its workers with Bubblewrap and libseccomp. Keep real private data outside cloud-connected coding sessions, terminals, synced output directories and agent-readable storage. [Isolation and verification](docs/ISOLATION.md) · [Threat model](docs/SECURITY.md)

## Install and evaluate

Running directly from the checkout uses only Python's standard library. To install the packaged commands, build a wheel with the documented local build tools and install it into a new virtual environment. After installation, use `mindtunnel` in place of `python3 -m mindtunnel.cli` and `mindtunnel-planner` in place of `python3 -m mindtunnel_planner.cli`. [Source setup](BOOTSTRAP.md) · [Platform evidence and Apple Silicon check](docs/PLATFORMS.md)

The interpreter supports exact count and integer sum, optional grouping by a string alias, and one typed equality filter. It rejects unsupported versions, operations, extra keys and invalid references. Arithmetic semantics, limits and local mapping examples are documented. [Implementation guide](docs/IMPLEMENTATION.md) · [Architecture](docs/ARCHITECTURE.md)

The internal frozen evaluation covers 30 feasible questions across three synthetic schemas, 10 unsupported questions and 53 invalid plan vectors. Gold and analyst-written SQL each matched all 30 expected results. The narrow mock declined all 30 feasible questions. The external model comparison and pilot still need participants and measured responses. A reviewer can reproduce the boundary checks from the isolated-workflow instructions. [Candidate notes](docs/RELEASE-NOTES.md) · [Release checklist](docs/RELEASE.md)

## License

MindTunnel is available under the [MIT License](LICENSE).
