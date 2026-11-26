# Source setup

Use Python 3.11 or newer. From the MindTunnel repository, run the synthetic bootstrap.

```sh
bash bootstrap.sh
```

The script runs the unit suite and demo without fetching dependencies or contacting a planner. On systems without make, use `python3 -m unittest discover -s tests -v` and `python3 scripts/demo.py`. The source CLI is available through `python3 -m mindtunnel.cli --help`. See [usage](README.md).

## Install the package

The offline release verifier can create a wheel and source archive from the reviewed source manifest. With the local build tools in [release preparation](docs/RELEASE.md) installed, choose a fresh evidence path and a new artifact directory:

```sh
python3 scripts/verify_release.py --out /tmp/mindtunnel-build-check.json --artifacts dist
```

Install the built wheel into an empty virtual environment. For example, on a machine with Python's pip and venv:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps dist/mindtunnel-0.0.1-py3-none-any.whl
.venv/bin/mindtunnel --help
.venv/bin/mindtunnel-planner --help
```

Keep build tools in the build environment. The installed project declares no third-party Python runtime dependencies. The ordinary executor and the isolated Linux launcher have different host requirements. See [isolation prerequisites](docs/ISOLATION.md).

## Resume engineering work

Check [observed progress](RESUME.md), [phase gates](PLANS.md), [agent instructions](AGENTS.md) and [build evidence](harness/build-log.md). Inspect the current branch and worktree. Use synthetic fixtures for all agent and CI runs. Release and external validation decisions remain with the owner.
