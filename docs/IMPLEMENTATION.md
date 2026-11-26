# Implementation guide

## Implementation map

Python 3.11+ with a standard-library runtime. Run `make test` and `make demo` from the checkout. See [source setup](../BOOTSTRAP.md) for installation.

| Component | Responsibility |
|---|---|
| mindtunnel/core.py | Duplicate-aware JSON parsing, public contract/request, v1 validation, deterministic bounded CSV aggregates |
| mindtunnel/files.py | Descriptor-relative regular-file reads and exclusive private publication |
| mindtunnel/cli.py and report.py | Owner-selected paths, generic status and escaped plain-text reports |
| mindtunnel_planner | Exact-byte preview, one-use approval, mock worker and response validation |
| mindtunnel_isolation | Optional Linux namespace, resource and socket controls for the two workers |
| schemas/ and tests/fixtures | Structural v1 schemas and frozen conformance vectors |
| examples/ and scripts/demo.py | Invented inputs and an offline CLI demonstration |

The public CLI has no provider credential or endpoint setting. Manual transfer and the fixed local mock are the available planning paths. See [planning](PLANNING.md) and [Linux isolation](ISOLATION.md). Keep alias/type contracts deliberately public and mappings private.

## v1 conformance and local files

`schemas/` contains JSON Schema 2020-12 structural descriptions for the public contract, plan, and result. Runtime validation also enforces unique field IDs, contract hash identity, reference types, UTF-8 scalar text, duplicate-key rejection, integer lexical syntax, and byte limits. A schema validator alone cannot establish these properties. `tests/fixtures/conformance-v1.json` freezes accepted plans and rejected plan/parser cases. The standard-library suite adds seeded aggregation properties, actual resource boundaries, malformed CSV, generic errors, and local file failure/concurrency checks.

All input files must be regular files. The POSIX reader uses directory descriptors and refuses symlinks in every path component, including the final file, and refuses `..` components. Supply physical paths. On macOS, `/tmp` and `/var` commonly resolve through symlinks, so obtain the physical path of an owner-selected directory before using it. Bundled temporary examples resolve their freshly created directories. The reader takes a bounded snapshot and leaves source files untouched. Path validation is independent of plan validation, and plans cannot select any paths.

The result writer creates a random temporary file in the selected destination directory with mode 0600, flushes it, and publishes it using an exclusive hard link. An existing file or symlink is preserved. Recoverable write/publication errors remove the temporary file and expose no partial destination. An abrupt process or machine failure may leave a 0600 temporary file. Use a filesystem supporting POSIX directory descriptors and hard links. Keep the destination directory under owner control. Directory entry durability after power loss is outside this guarantee.

## Local mappings and private reports

Create the public contract by hand using approved aliases and either `string` or `integer`. Separately create a local mapping object whose keys exactly match every alias and whose values name distinct actual CSV headers. A header may contain spaces or Unicode. The mapping is supplied only to the local executor. Extra source columns remain local and are ignored. For example, public aliases `category` and `amount_cents` map to the synthetic headers in `examples/mapping.json`. Integer input uses signed 64-bit decimal values, and sums retain exact integer precision beyond that range. Grouping uses string values and returns deterministic lexicographic order. The current frozen feasible tasks use count, sum, grouping, and one typed equality filter, so P3 keeps the v1 operation set.

After local execution, explicitly create a private text report.

```sh
python3 -m mindtunnel.cli report --result work/result.json --out work/report.txt
```

The command reads a regular local result file, validates its v1 keys, version, types, row/group bounds, sorted unique groups, and possible integer aggregate bounds, then creates the report exclusively with the same private-output permissions and atomic publication as `run`. It reports generic status. The result and table remain local. A group is shown as a quoted ASCII-escaped string. Null identifies an ungrouped result. Embedded newlines, terminal controls, Unicode, markup, URL punctuation, and table delimiters are escaped. The report is plain text and contains no active markup or links. An empty grouped result has an explicit empty marker.

Result parsing has a separate 16 MiB bound. Before JSON materialization, a quote-aware scan caps structural separators to the v1 envelope size, limiting container allocation while permitting punctuation inside quoted labels. This accommodates all normal executor-produced v1 JSON, including 200 groups of 4096 supplementary Unicode characters encoded with 12-byte JSON escapes. Plans, contracts, and mappings retain their 64 KiB JSON limit. Aggregate values remain exact integers within the 50,000-row signed-64-bit input envelope. The result validator checks a conservative minimum number of input rows across groups. It cannot establish a result's provenance or correctness without its source and plan. Owner-selected result files may contain private values, so use the report only in a trusted local environment.
