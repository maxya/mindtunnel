# Public planning and approval

The manual workflow remains portable. `mindtunnel request` prints the public request for owner inspection. Transfer the reviewed bytes to a chosen planner yourself, save its response locally, and run the validated plan through the local executor. Keep data, mappings, results, and private errors outside the planning interaction. The software cannot determine whether an owner-authored public task or alias is sensitive.

The optional approval workflow uses a deterministic mock adapter on Linux. Its production entry requires the isolated launcher. The worker receives the public request, destination, and model through stdin. The launcher supplies the runtime boundary. See the isolation documentation for requirements and observed platform evidence. The mock implements the exact tasks `Count rows`, `Count rows by <string_alias>`, `Sum <integer_alias>`, and `Sum <integer_alias> by <string_alias>`. Other tasks produce exactly `{"unsupported":true}`. This mock supports boundary verification and supplies no evidence of model planning quality.

## Review and approve

Create an owner-controlled working directory and save the public request there. Use physical paths, as described in IMPLEMENTATION.md.

```sh
mkdir -m 700 work
python3 -m mindtunnel.cli request --contract examples/contract.json --task 'Sum amount_cents by category' > work/public.json
python3 -m mindtunnel_planner.cli preview --request work/public.json
```

The preview includes the exact request as an escaped UTF-8 string, its byte count and SHA-256, destination `mock://local`, model `synthetic-v1`, and `approval_sha256`. Inspect the entire request and target. Copy the displayed approval hash into the following command.

```sh
python3 -m mindtunnel_planner.cli approve --request work/public.json --approval work/approval.json --confirm-sha256 <approval_sha256>
python3 -m mindtunnel_planner.cli mock --request work/public.json --approval work/approval.json --plan-out work/returned-plan.json --capture-out work/captured-request.json
```

After installation, `mindtunnel-planner` is the equivalent console command. The destination and model can be supplied explicitly using `--destination mock://local --model synthetic-v1`. Unsupported destinations and models are rejected. The captured request file must match the approved request bytes exactly. A supported returned plan can be used by the ordinary executor or the isolated executor. A structured unsupported response is an explicit local outcome and is rejected as an execution plan.

Approval expires after 300 seconds by default. `approve --ttl` accepts 1 through 900 seconds. A receipt binds the exact request-byte hash, destination, model, expiry, and its own absolute path. An exclusive `.used` marker consumes the receipt before the worker attempt. Concurrent attempts have one winner. A copied receipt fails its location check. Keep both receipt and marker in the owner-controlled directory. Any worker, validation, isolation, or output failure still consumes that approval. Inspect the local situation and issue a fresh approval at a new path if another attempt is intended.

## Boundary and limitations

The coordinator validates the allowlisted public request shape without reading a data path, mapping, or execution result. It snapshots the request before consuming approval and sends that exact snapshot. The standalone mock worker imports only standard-library parsing modules and has no execution-result interface. Its return envelope carries the request capture and an untrusted response. The coordinator compares the capture byte for byte and validates a plan against the public contract, or accepts the exact unsupported object. Errors are reduced to a generic local code. The workflow makes one attempt and carries no history or private-error repair loop.

A receipt uses SHA-256 to bind reviewed content. Filesystem ownership protects approval state. An authorized same-user process can rewrite or delete local receipts and markers, so this mechanism assumes a trusted owner account and directories. Expiry depends on the local clock. Host compromise and cloud-connected terminal capture remain outside the protection boundary.

The MVP provides manual transport and the isolated mock. A programmatic remote-provider adapter requires separate endpoint, credentials, retention/terms, egress, and isolation review. No real provider request has been evaluated by the mock tests. Public request capture verifies the synthetic boundary exercised by those tests. It does not establish absence of every possible disclosure.
