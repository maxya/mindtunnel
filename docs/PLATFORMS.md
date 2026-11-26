# Platform verification

The ordinary CLI runs as a process under the caller's permissions. The package targets Linux and macOS with Python 3.11 or newer. It requires a local filesystem that supports POSIX file permissions and hard links. Use physical input and output paths. On macOS, `pwd -P` and the verifier's resolved temporary directories avoid the symlinked `/var` and `/tmp` paths.

| Execution mode | Requirements | Verification scope |
|---|---|---|
| Source CLI and installed wheel | Python 3.11+, standard library and a suitable local filesystem | Request preview, validated CSV aggregation, local report and invalid plan rejection |
| Offline distribution build | Preinstalled build and installation tools from the release guide | Wheel and source-archive builds, archive inspection, clean installs outside the source tree and same-toolchain reproducibility |
| Isolated worker and isolated mock planner | Compatible Linux host with Bubblewrap, user namespaces and libseccomp | Filesystem and network restrictions exercised separately on Linux |

The portable commands and manual transfer workflow can be exercised on macOS. The Linux worker and isolated mock rely on Linux-specific kernel controls. The Apple Silicon verifier checks that the Linux executor command rejects a valid synthetic request and leaves the output absent. [Linux isolation details](ISOLATION.md)

## Run on an Apple Silicon Mac

Use a native `arm64` Python 3.11 or newer on an Apple Silicon system. Use the checkout or an extracted source archive containing this script. Select the interpreter with the preinstalled build tools in its environment and put the preinstalled `uv` executable on `PATH`. The verifier uses those local tools and disables downloads and dependency resolution for the clean installs. [Build prerequisites](RELEASE.md)

From the checkout or extracted archive, run these commands with a fresh evidence directory.

```sh
evidence_dir="$(mktemp -d)"
evidence_dir="$(cd "$evidence_dir" && pwd -P)"
python3 scripts/verify_macos.py --out "$evidence_dir/macos-verification.json" \
  --artifacts "$evidence_dir/dist"
```

Use an explicit interpreter path in place of `python3` to select Python 3.11 or another installed version. The script checks macOS and the Python process architecture before starting. It records the OS version, architecture, Python and build-tool versions, dependency inventory, archive hashes and clean-install results in the JSON file. Source tests and the synthetic CLI demo run with the selected interpreter from both the staged source and the extracted source archive. The build verifier compares two builds under that toolchain and exercises the installed CLI from an unrelated working directory. Archive artifacts are optional. A failed check exits nonzero.

Keep the run command, evidence JSON and the verified source commit or archive hash together. Apple Silicon platform acceptance requires a successful run on actual hardware. The script's Linux rejection check alone supplies no macOS evidence.

## Hosted workflow

The checked-in workflow declares Ubuntu and macOS jobs for Python 3.11, 3.13 and 3.14. Its tool setup uses the runner's package index. The tests and release verification then use local fixtures and package tools. A hosted job result is a separate release gate from local container or Apple Silicon verification. [Workflow definition](../.github/workflows/ci.yml)
