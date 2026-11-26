# Reporting a security issue

Use the maintainer's designated private security channel once it is configured. The route remains pending for this candidate. Until it is available, keep sensitive reports local. Public issues can describe ordinary bugs using invented data.

For private security reports, include the version, operating system, Python version, affected mode, expected behavior, observed behavior and synthetic steps that reproduce the issue. Use invented rows and paths. Keep credentials, actual CSVs, model credentials, private task text, terminal transcripts and personal information out of reports. [Threat model and current controls](docs/SECURITY.md)

## Maintainer configuration before release

- Select a private channel with controlled access. Record who monitors it and who covers their absence.
- Check that an external reporter can submit a synthetic report privately and that the assigned recipient receives it. Record the observed check without personal details.
- Publish the verified route, supported versions, expected response process and coordinated disclosure policy with the release.
- Define who triages reports, owns remediation and verifies the fix. Keep confidentiality-boundary failures open until independent verification resolves them.
