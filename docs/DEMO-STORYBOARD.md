# Synthetic demo

Run from the source checkout or extracted source archive.

```sh
python3 scripts/demo.py
```

The example asks for summed transaction cents per category. The CSV includes fictional merchant values and physical column names. The public request shows only the question, field aliases and types, contract identifier, version and plan instructions.

1. Read `PUBLIC REQUEST (synthetic)` to see exactly what a planner would receive.
2. Inspect `BUNDLED PLAN (hand-authored)` for the contract identifier and allowed aggregate. The demo runs the supplied plan locally.
3. See food total `2200` and transport total `3000` in the synthetic JSON result and local report.
4. See `Rejected: plan_keys` when a plan adds an instruction outside the plan schema. The demo checks that rejection leaves no result file.

This recording uses the portable CLI under the caller's process permissions. The scripted demo displays invented results so viewers can follow the workflow. Ordinary use writes results and reports to local files and prints generic status. The isolated mock workflow and its observed capture run have a separate procedure. [Linux isolation checks](ISOLATION.md) · [Threat model](SECURITY.md)

## Generate a local GIF

With Pillow already installed, run the generator at a fresh destination.

```sh
demo_dir="$(mktemp -d)"
demo_dir="$(cd "$demo_dir" && pwd -P)"
python3 scripts/make_demo_gif.py --out "$demo_dir/mindtunnel-synthetic-demo.gif"
```

The generator invokes the bundled demo and uses its stdout to render the request, plan, local results and rejection as paginated GIF frames. It creates the requested output exclusively with private local permissions. Review the frames before any owner-authorized sharing. The portable CLI and normal test suite use only the Python standard library.
