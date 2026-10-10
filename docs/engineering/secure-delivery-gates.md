# SecureOps Secure Delivery Gates

This document defines the quality gates for the SecureOps payment API. The goal is to catch correctness and security problems before an image is promoted to Kubernetes or OpenShift.

## Gate sequence

1. **Source validation** — check formatting and lint rules with Ruff.
2. **Automated tests** — run the pytest suite and fail the pipeline if a test fails.
3. **Dependency review** — inspect application dependencies and generate an SBOM as the dependency-scanning stage is added.
4. **Container build** — build the payment API image from the version-controlled Dockerfile.
5. **Image security scan** — run Trivy against the built image and apply an explicit policy for blocking critical findings.
6. **Deployment validation** — validate Kubernetes manifests before applying them.
7. **Post-deployment verification** — check rollout status and the application's health/readiness endpoints.

A failed required gate must stop promotion. A pipeline should not report success merely because an image was built.

## Current verification

The following checks have previously passed in the project workflow:

- pytest: **4 tests passed**
- Ruff: **all checks passed**
- Jenkins build for the commit adding the Ruff code-quality gate: **successful**

These are recorded as a point-in-time verification, not a guarantee that every later commit passes. Run the checks again after changing application code or pipeline configuration.

## Local commands

Run these from the repository root in the development environment:

```bash
python -m pytest
ruff check .
```

If Ruff is not installed in the active environment, install the project's development requirements first rather than silently skipping the lint gate.

## Promotion policy

- Do not deploy an image when tests or mandatory security checks fail.
- Pin image tags to a specific version; avoid relying on `latest`.
- Keep secrets out of source control and build logs.
- Record the image tag and commit SHA used for a deployment.
- Verify rollout health after deployment and retain a clear rollback path.

## Planned extensions

- Add an SBOM generation step and dependency vulnerability policy.
- Add a SAST stage and document severity thresholds.
- Integrate manifest validation and Argo CD sync/health checks.
- Add a release record linking commit SHA, image digest, scan result, and deployment environment.
