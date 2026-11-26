# Synthetic demo recording

The reproducible demonstration is `python3 scripts/demo.py`. It uses invented transactions and a hand-authored plan, prints the public request, executes locally, writes the escaped private report, and rejects the malicious plan. Its result is verified against the bundled expected output. A separate isolated workflow demonstrates runtime controls. The basic demo supplies no live-provider performance evidence.

For a future GIF, use an owner-selected terminal recorder with an empty local shell history and a working directory containing only the public synthetic checkout. Review the recording for accidental ambient terminal content before sharing. Recording-tool installation and publication are separate owner decisions. The repository supplies this storyboard, runnable demo, and optional local GIF generator. A two-frame 1280×900 GIF was generated locally from the synthetic demo and inspected. Publication remains pending owner approval.

1. Show the MindTunnel command and the public `contract.json`. Explain that the task and aliases are the reviewed disclosure.
2. Run `python3 scripts/demo.py` in a terminal sized for readable JSON. Hold the complete public request long enough to inspect every field.
3. Show the local result and report, including food total `2200` and transport total `3000`.
4. Show the malicious-plan rejection and synthetic-demo success status.
5. Show the trust-boundary documentation and state the measured scope, hand-authored planning fixture, runtime isolation requirements, and pending external evaluation gates.

Record only the synthetic fixture. Keep the resulting capture local until the owner has reviewed it and authorized publication.

## Optional local GIF generator

With the optional Pillow `13.0` rendering tool already installed, run the local generator with a fresh destination.

```sh
python3 scripts/make_demo_gif.py --out /tmp/mindtunnel-synthetic-demo.gif
```

The generator invokes the actual bundled synthetic demo, captures that subprocess's stdout, wraps all lines into readable pages, and creates a local GIF. Every public-request field and the full instructions, local results/report, and malicious-plan rejection appear across its frames. It captures the demo process output directly. The demo's synthetic temporary result files are removed after execution. The generator disables bytecode-cache writes, creates its output exclusively with private local permissions, and retains only the requested GIF. The application and its normal checks require no Pillow dependency. Review all GIF frames before any owner-authorized sharing.
