# MindTunnel 0.0.1 candidate notes

MindTunnel builds a reviewable planning request from a public question and a contract of aliases and types. The owner can pass that request to a planner and bring back a proposed JSON plan. MindTunnel validates the plan before it uses the local CSV and mapping, then writes the resulting aggregate and report to owner-selected paths.

## Included

- A versioned plan format for count and integer sum, with optional string grouping and one typed equality filter.
- Bounded plan validation, local CSV execution, exclusive result and report files, and generic diagnostics.
- A deterministic mock planner and an optional Linux worker profile using Bubblewrap and libseccomp.
- An offline synthetic demo that shows the entire request, bundled plan, local result and rejected extra action.
- A wheel with no third-party Python runtime dependencies, a source archive, and bundled examples and conformance cases.

Try the example through `make demo` or use the portable CLI with an installed wheel. [Synthetic demonstration](DEMO-STORYBOARD.md) · [Platform requirements](PLATFORMS.md)

## Verified scope

The portable workflow and clean installation paths have run on Linux with Python 3.11. The release verifier compares two builds under the same local toolchain. The Linux worker tests observed the approved 722-byte mock request and correct synthetic local result, verified socket denial, and observed no packets during the bounded synthetic capture run. Those measurements apply to the tested configuration. [Linux isolation procedure](ISOLATION.md)

## Known limitations and release gates

- The demo uses an authored plan. Real-planner quality, schema-only model comparison and five-person usability results remain pending.
- A manual planner can see whatever the user chooses to share. Review the request contents and destination before transfer. Model or provider retention depends on the chosen service.
- The portable CLI uses the caller's process permissions. Native Apple Silicon runs and hosted platform results remain pending, and kernel-level worker isolation targets compatible Linux systems.
- The v1 operation set omits joins, arbitrary expressions, raw-row output and arbitrary SQL. Unsupported operations are rejected before CSV execution.
- Public release requires owner approval of the project identity, reporting route and final artifacts.

MindTunnel is available under the [MIT License](../LICENSE). These notes describe a local release candidate. [Release checklist](RELEASE.md) · [Threat model](SECURITY.md)
