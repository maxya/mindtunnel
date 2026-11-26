# Validation after the accepted implementation

Start from the accepted P0–P5 checkpoint at 9284c1d. Keep the public plan grammar, the 30 feasible cases, 10 unsupported cases, corpus digest and 85% gate fixed. Use one reviewed request in a fresh session with no tools, retrieval, repository access or chat history. All evaluation artifacts use invented data.

| Phase | Deliverables and evidence required |
|---|---|
| V1 | Owner-side first-attempt and separately reported retry scoring; public-only exports for three model classes and a constrained SQL comparator; coverage of validity, semantics, result, rejection, diagnostics, tokens and latency. Sam checks scorer behavior and leakage. |
| V2 | Inspect approved local capabilities, run only eligible models, otherwise prepare the actual public request files and an unmeasured ledger. Preserve original responses and provenance if present. |
| V3 | Verify minimum Python, clean installs and reproducible archives in available environments. Give the owner a standalone native Apple Silicon check. Review hosted CI locally. |
| V4 | Prepare a self-contained synthetic participant kit, unaided exercise, questionnaire and facilitator-only scoring sheet. Five independent people must attempt it; three must explain the boundary unaided. |
| V5 | Prepare release notes, demo, support and security docs, owner decisions and release checklist. Inspect prospective public files and archive contents. Sam reviews the final cross-phase recommendation. |

No network/provider enablement, new credentials, license adoption, publication or P6 changes are authorized. Independent platform and pilot preparation can run while model or participant evidence is pending. See RESUME.md and harness/build-log.md for phase results and local commit references.
