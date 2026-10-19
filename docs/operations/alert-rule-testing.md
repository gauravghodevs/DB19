# Prometheus Alert Rule Testing

## Purpose

SecureOps uses `promtool test rules` to regression-test alert behavior with
synthetic input data, without causing an outage or changing live Kubernetes
resources.

## Run in GitHub Actions

The workflow at
`.github/workflows/observability-alert-tests.yml` runs the tests when relevant
test files or the workflow change in pushes and pull requests targeting `main`.
It can also be started manually using `workflow_dispatch`.

## Current test coverage

The synthetic `SecureOpsSyntheticAlert` rule evaluates `test_metric > 0` and
has a `for: 1m` duration. The test verifies that the alert is not firing at
45 seconds and is firing at 1 minute, with the expected labels and annotation.

The test uses synthetic input data. It does not cause a real application
outage, test Alertmanager notification delivery, or verify that a live
notification receiver is reachable.

## Live-cluster verification

See [Monitoring Stack Verification](monitoring-stack-verification.md) for
the documented live Prometheus and monitoring-stack checks.

Keep synthetic regression rules in `tests/observability/`. Do not add them to
the live Kustomize resources unless intentionally changing deployed behavior.
