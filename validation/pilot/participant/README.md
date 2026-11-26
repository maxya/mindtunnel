# MindTunnel synthetic trial

Use the supplied fictional dispatch files for this trial. You can complete it offline with the supplied plans. Open a terminal in the extracted folder. Run the steps in order and capture your own observations in the questionnaire.

## Set up

Use Python 3.11 or newer with `venv` and pip on Linux or macOS. The kit includes the wheel. The commands below install it locally into a new environment.

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install --no-index --no-deps ./mindtunnel-0.0.1-py3-none-any.whl
mkdir -m 700 results
```

If your installation lacks pip, use an already available `uv` installer.

```sh
python3 -m venv --without-pip .venv
uv --no-config pip install --offline --no-index --no-deps --no-python-downloads \
  --python .venv/bin/python ./mindtunnel-0.0.1-py3-none-any.whl
mkdir -m 700 results
```

Use the setup route that matches the tools already present. Ask the facilitator if setup is blocked.

## Count dispatch records per route

Create a request and look at its contents.

```sh
.venv/bin/mindtunnel request --contract contract.json \
  --task 'Count rows by route' > results/public-request.json
cat results/public-request.json
```

Use the supplied plan to produce a result and report.

```sh
.venv/bin/mindtunnel run --contract contract.json --plan demo-plan.json \
  --mapping mapping.json --data dispatch.csv --out results/count.json
.venv/bin/mindtunnel report --result results/count.json --out results/count.txt
cat results/count.txt
```

## Sum packed units for east

Use `exercise-plan.json` to sum the units in the east route. Adapt the command from the count task and use `results/east.json` as your new destination. Read the output locally and record the result in the questionnaire.

## Check an extra action

The supplied rejected plan adds an action asking to send the CSV. Try it with a new destination. Record what happens and check which files the command left behind.

```sh
.venv/bin/mindtunnel run --contract contract.json --plan rejected-plan.json \
  --mapping mapping.json --data dispatch.csv --out results/rejected.json
ls results
```

Use fresh destination names to repeat a run. The CLI refuses to overwrite results. This trial uses the ordinary CLI and runs under your login account's process permissions.

Complete [the questionnaire](QUESTIONNAIRE.md) before reviewing your observations with the facilitator.
