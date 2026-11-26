# Reporting a security issue

MindTunnel is an experimental local analytics project. The threat model, implemented boundaries, and residual risks are documented in `docs/SECURITY.md` and `docs/ISOLATION.md`. Release acceptance remains subject to the documented evaluation and owner gates.

Use the repository's private vulnerability reporting channel if the maintainer has enabled it. The maintainer must confirm and publish a monitored private reporting route before release. During this preparation stage, keep sensitive findings local until a private channel is available. Public issues may describe a generic issue using invented data and synthetic canaries. Include the affected version, operating system, Python version, exact synthetic reproduction steps, expected behavior, observed generic status, and proposed mitigation when available.

Keep credentials, personal information, private documents, real source rows, result values, sensitive task text, private paths, and raw production errors out of issue reports. A synthetic reproduction is sufficient for initial triage. Confidentiality-boundary violations require remediation and independent re-verification before the relevant release gate can pass.

The project currently supplies no promised response time or supported production release. The maintainer must define supported versions, reporting ownership, response expectations, and advisory/publication handling before release. Avoid publishing a vulnerability demonstration that discloses another person's private information.
