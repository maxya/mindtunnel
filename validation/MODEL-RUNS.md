# Run a blinded planner comparison

**Blinded collection is on hold.** The canonical remote exposed the internal answer key at commit `dec76ef`. Retain these packets for historical reproduction and open-book comparisons. A future held-out claim requires a fresh independently protected corpus.

As of this checkpoint there are zero actual planner responses. Frontier, smaller cloud and local model outcomes are **unmeasured**. A local Ollama runtime image was available, but the checked locations contained no model weights. Engineering agents have access to the answer files and are ineligible. [Capability record](planner-runs.json)

The operator has two ready-made archives. Each contains 40 public request files and nothing else. Download or extract them locally. A session gets **one approved file's text**, never the archive, repository, index, model outputs, scoring sheet or answer key.

| Arm | Packet | SHA-256 |
|---|---|---|
| MindTunnel v1 | [Public plan requests](requests/public-ir.zip) | `6204dfe8affd2eddab1fea8271e8b7baa6097b67df916bd654c2cca91e457659` |
| Schema-only SQL | [Public SQL requests](requests/public-sql.zip) | `57549079308a67d0c8e7fd5c637d901045d4e9a7e14db0c6afc60eb37a43a67e` |

1. On the **grader machine**, register the exact model/version, role, settings, comparator and retry policy before obtaining responses. For local weights include the weights digest, quantization and runtime. For a cloud model identify the actual destination and obtain owner approval of the destination, disclosed bytes and any cost. Keep registration, labels and grading on this machine. [Registration and CLI commands](../harness/evaluation/VALIDATION.md)
2. On a **separate planning surface**, use an approved tool-free, retrieval-free session with no connected files, chat memory, shell or access to the checkout. A locally hosted model may run on a different offline machine or in a confined worker with only its trusted runtime and weights mounted. The planning surface must lack access to gold labels even if the model requests them. A general coding agent in this checkout fails that condition.
3. For each case compare the extracted file with the registered public bytes. Inspect the complete question, contract and instructions. Start a fresh interaction, submit only those bytes and save the first response verbatim. Record measured latency and any provider token counts. Record unavailable values as unknown. Do not add system instructions, examples or previous messages of your own. Record provider-managed prompts/settings that cannot be observed.
4. If a blind second attempt was preregistered, repeat the same approved request in a fresh session without feedback. Keep the first raw response. Collect before grading so private errors, outcomes and judgments cannot influence retries. Record unchanged raw responses even when they are refusals, invalid JSON or contain unsupported operations.
5. Run the owner-side scorer after collection. Report feasible validity, exact semantics and result over 30, unsupported rejection over ten, and separate first and retry outcomes. The original 85% threshold requires 26 of 30 exact plan-plus-result successes. Keep missing cases in the denominator. A comparator, synthetic rehearsal or incomplete run cannot establish real frontier-planner performance.

The operator's response records bind captured bytes to the run, request and attempt. Operator attestation does not authenticate the provider. Disallow web search for this corpus and record any known prior exposure. A model with access to published questions or answers is unsuitable for a held-out claim. The SQL arm measures the documented grammar, with only validated operations evaluated on the local synthetic fixture.

Regenerate both public archives from the internal checkout with `python3 validation/export_packets.py /path/to/fresh-directory`. Recheck their members if the protocol code or byte representation changes.
