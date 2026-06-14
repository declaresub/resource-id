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
- **CycloneDX SBOM** attached to each GitHub release (`resource-id.cdx.json`).
- **Dependency scanning** — `uv.lock` is scanned for known vulnerabilities
  (OSV) in CI, and Dependabot tracks dependency and GitHub Actions updates.

## Verifying a release

Each release on PyPI carries PEP 740 attestations. With a recent pip you can
require them at install time:

```
pip install resource-id --require-hashes  # plus a hashed requirements file
```

The build provenance attestation (which repository and workflow produced the
distribution) can be verified with the GitHub CLI against the GitHub release
assets:

```
gh attestation verify <downloaded-file> --repo declaresub/resource-id
```

Each GitHub release also includes Sigstore `.sigstore` bundles for the wheel and
sdist, and a CycloneDX SBOM (`resource-id.cdx.json`) enumerating the dependency
tree of that release.
