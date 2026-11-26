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

## Outcome

**NO-GO for public release.** The current evidence demonstrates the local execution boundary and verified distributions. Zero real planner responses and zero human observations leave the product hypothesis open. The constrained SQL comparator could offer comparable usability and isolation with less effort. The deliberately public task and aliases also disclose semantics. The narrow grammar and review overhead both warrant measurement before further implementation.

| Phase | Independently verified here | Evidence still needed |
|---|---|---|
| V1 | Frozen first-attempt and retry scoring, error categories, known/unknown metrics, independent constrained SQL execution and fixture controls | Actual observations from registered models |
| V2 | Two inspected archives of 40 public requests, local capability inventory and owner instructions | Eligible isolated model and approved transfer; full per-model responses and scores |
| V3 | Linux 3.11.2 source, wheel and sdist verification; rebuilt and clean-installed archives; Mac guard and hosted configuration review | Successful native Apple Silicon and hosted jobs |
| V4 | Offline participant kit with independent software rehearsal and separate empty scoring sheet | Five outside attempts, at least three unaided explanations |
| V5 | Curated source and wheel, reproducible local builds, security/contact and license options, release notes and synthetic demo | Rights holder, license, monitored reporting route and owner release sign-off |

See [model packets and procedure](MODEL-RUNS.md), [platform evidence](platform-results.json), [pilot guide](pilot/FACILITATOR.md), [public artifact review](publication-scope.md) and [independent release verdict](reviews/v5.md). Maintain the current plan language until model performance and participant outcomes are available.
