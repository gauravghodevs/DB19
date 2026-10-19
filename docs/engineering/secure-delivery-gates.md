# SecureOps Secure Delivery Gates

This document describes the implemented quality and security gates for the
SecureOps payment API. The objective is to detect correctness, dependency,
container, secret, and Kubernetes configuration issues before delivery.

## Delivery pipeline

The repository uses GitHub Actions for automated validation and image
delivery, with a Jenkins pipeline also maintained for CI practice.

### Implemented controls

1. **Source quality** — Ruff checks Python style and lint rules.
2. **Automated tests** — pytest runs the payment API test suite.
3. **Dependency vulnerability audit** — `pip-audit` checks declared Python
   development requirements against known vulnerability data.
4. **Software bill of materials** — CycloneDX generates a JSON SBOM from the
   resolved project dependency inventory.
5. **Dependency review** — the pull-request dependency review workflow applies
   a severity threshold to dependency changes.
6. **Secret scanning** — Gitleaks scans repository changes, with documented
   handling for the existing historical finding exception.
7. **Container build and smoke test** — CI builds the payment API image,
   checks that it runs as UID/GID `10001:10001`, and checks its health endpoint.
8. **Container vulnerability scanning** — Trivy scans operating-system and
   library packages for HIGH and CRITICAL findings, ignoring unfixed findings
   under the configured policy.
9. **Kubernetes manifest validation** — CI renders the base Kustomize
   configuration and validates the resulting resource schemas.
10. **Kubernetes configuration security** — a dedicated workflow scans
    Kubernetes configuration.
11. **Image publication** — on pushes to `main`, the CI workflow publishes the
    scanned image to GHCR using the commit SHA as its tag.
12. **Documentation validation** — a dedicated workflow validates repository
    documentation.

Workflow definitions live in `.github/workflows/`. Each workflow has its own
triggers and scope; a successful run of one workflow does not prove that all
other workflows passed.

## Local verification

Run these commands from the repository root, using the payment API virtual
environment:

```bash
cd applications/payment-api
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check app tests
.venv/bin/python -m pip_audit \
  --requirement requirements-dev.txt
```

To generate a CycloneDX SBOM locally, first ensure `cyclonedx-bom` is installed in the payment API virtual environment. Generate the resolved dependency inventory, then build the SBOM from it:

```bash
cd applications/payment-api
.venv/bin/python -m pip freeze > /tmp/payment-api-resolved-requirements.txt
.venv/bin/cyclonedx-py requirements /tmp/payment-api-resolved-requirements.txt --output-format JSON --output-file /tmp/payment-api-dependencies.cdx.json
```

The repository's CI workflows remain the authoritative place to verify the
hosted pipeline behavior. Local success does not guarantee that a hosted
workflow, registry publication, or deployment will succeed.

## Security and promotion policy

- Do not promote an image when required tests or security gates fail.
- Use immutable, commit-specific image tags instead of relying on `latest`.
- Keep credentials and tokens out of source control and build logs.
- Review vulnerability findings and documented exceptions; do not treat a
  suppressed finding as proof that a component is safe.
- Preserve audit and SBOM artifacts so dependency decisions can be reviewed.
- Verify deployment health and retain a documented rollback procedure.
- Treat Git as the source of truth for version-controlled deployment
  configuration; review changes before reconciling them to a cluster.

## Scope and limitations

The repository demonstrates a secure delivery workflow, but CI success alone
does not establish production readiness. A real deployment still requires
environment-specific configuration, access controls, registry and cluster
permissions, operational monitoring, and post-deployment verification.

A dedicated SAST gate and a release record linking commit SHA, image digest,
scan results, and deployment environment remain potential improvements unless
implemented in a separate workflow.
