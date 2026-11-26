# Local release preparation

The package version remains `0.0.1`, an experimental preparation build. This numeric version has no PEP 440 prerelease suffix. Project status and the release checklist communicate its experimental state. The owner must approve the license, public release, and tag before publication. Local archive verification can proceed while those decisions and the external evaluation gates remain pending.

## Offline source and archive verification

The source entry requires Python 3.11+ and its standard library.

```sh
make test
make demo
```

Package verification additionally requires preinstalled setuptools `84.2.1`, wheel `0.48.0`, and uv `0.13.10`. The backend versions are pinned in `pyproject.toml`. Their actual active transitive dependencies are recorded in the inventory and each verification result. The local `jaraco.context` dependency has development-snapshot metadata, so reproducing that exact provisioning on another machine remains unverified. Runtime dependencies remain empty. The verification script uses local build tools directly and invokes uv with offline mode, index lookup disabled, Python downloads disabled, build isolation disabled, and dependency resolution disabled for the built wheel. It makes temporary environments with the standard-library venv module and needs no pip module.

```sh
python3 scripts/verify_release.py --out /tmp/mindtunnel-release-check.json
```

Choose a fresh evidence path. Add `--artifacts <new-owner-directory>` to retain the built wheel and source archive. Every source file staged for the build must be named in `harness/release-files.txt`. That positive manifest includes source, synthetic examples, schemas, conformance data, evaluation tools/evidence, and relevant documentation. The script refuses symlinks in source-path components and copies only those known files into a temporary source tree with mode 0644, runs its tests and demo, builds a wheel and source archive, inspects every archive member, rebuilds from the source archive, and installs both the first wheel and source-archive-built wheel into clean environments. Installed CLI request, aggregation, report, planner preview, conformance vectors, argument-error privacy, and package import locations are checked from an unrelated working directory.

Scripts in the source archive are invoked explicitly with `bash` or `python3` and use mode 0644. Source-archive verification builds its wheel using the same preinstalled build backend, then installs it into a clean runtime environment. The build environment is distinct from the clean runtime environments. The script records SHA-256 values for the source manifest and all inspected archive members. It checks source and wheel contents against the manifest, rejecting unexpected files. This scopes the privacy inspection to known repository material and generated packaging metadata. Inspect the final manifest and member inventory before any owner-approved publication.

Normal installed assets are located under `<environment-prefix>/share/mindtunnel/examples`, `schemas`, and `conformance`. Package code is installed under the environment's site-packages directory. The Linux isolation launcher finds its bundled worker modules relative to the installed packages. Runtime isolation and packet-capture evidence remain separate from package installation verification.

## Reproducibility scope

The script seeds and verifies canonical setuptools `[egg_info]` configuration only in the temporary build tree before source discovery. It sets `SOURCE_DATE_EPOCH` and `PYTHONHASHSEED`, records actual tool versions, compares wheel bytes between the direct and source-archive builds, and compares normalized member contents of both source archives. It normalizes the already inspected source archive by sorting members and fixing tar ownership/timestamps and the gzip header, preserving intended modes. Both final archive formats must be byte-identical between the two builds. Reproducibility claims must use the observed fields from the verification evidence and the exact source snapshot and toolchain recorded there.

The dependency inventory is `harness/dependency-inventory.json`. It covers the application, Python requirement, explicit build backend and wheel tool, installer used for verification, and optional Linux isolation components. Runtime OS/Python and bundled build-tool internals require their own upstream review. Local packaging checks supply no hosted-CI or external security-audit result.

## Release and tag checklist

- [ ] Approve the project name, license grant, copyright holder, final license text, package metadata, and publication scope.
- [ ] Complete the frozen model-quality comparisons, five-person synthetic pilot, and all mandatory evaluation gates in GOALS.md and PLANS.md.
- [ ] Confirm a private, monitored security reporting route and security maintenance policy.
- [ ] Review the threat model, supported guarantees, exclusions, conformance vectors, and all material independent-review findings.
- [ ] Run the full source, archive, clean-install, end-to-end, and Linux isolation verification against the final commit.
- [ ] Observe passing Linux and macOS CI results on the supported Python matrix. Preserve the actual job references and output.
- [ ] Inspect the positive source manifest, archive member inventory, synthetic fixtures, dependency inventory, and local Git status.
- [ ] Select the release version and changelog, verify installed version consistency, and rebuild final artifacts.
- [ ] Obtain explicit owner approval for a local tag, remote push, package publication, GitHub release, or any deployment before performing that action.

Use a signed or annotated tag according to the maintainer's approved release policy after the checklist passes. Tag creation, remote access, artifact upload, and publication are separate owner-controlled actions.
