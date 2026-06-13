# Security Policy

## Supported versions

`resource-id` is distributed on PyPI as
[`resource-id`](https://pypi.org/project/resource-id/). Security fixes are
released for the latest published version; please upgrade to the latest release
before reporting an issue.

## Reporting a vulnerability

Please report suspected security vulnerabilities **privately** through GitHub's
[private vulnerability reporting](https://github.com/declaresub/resource-id/security/advisories/new)
(the repository's **Security** tab → **Report a vulnerability**). Do **not** open
a public issue for a suspected vulnerability.

You can expect an initial response within a reasonable period. If a fix is
warranted, it will be released to PyPI and disclosed via a GitHub Security
Advisory.

## Supply-chain assurances

Releases are built and published from GitHub Actions with:

- **PyPI Trusted Publishing (OIDC)** — no long-lived API tokens exist to be
  compromised.
- **Protected environments** — publishing to PyPI requires explicit maintainer
  approval.
- **SHA-pinned GitHub Actions** and least-privilege (`permissions: {}` by
  default) workflows.
- **Sigstore signing** and **PEP 740 attestations** for verifiable build
  provenance.

The published distributions can be verified against their attestations on PyPI.
