# Prometheus Alerting and Alertmanager Delivery Validation

## 1. Objective

Validate the SecureOps monitoring alert lifecycle, GitOps deployment of
Prometheus alert rules, and internal delivery of a firing alert to Alertmanager.

This validation covers automated rule regression tests and a live,
temporary alert probe. The probe was removed after successful verification.

## 2. Environment

- Project: SecureOps DevSecOps Platform
- Kubernetes namespace: `monitoring`
- GitOps controller: Argo CD
- Argo CD application: `monitoring-stack`
- Prometheus image: `prom/prometheus:v3.5.0`
- Prometheus service port: `9090`
- Alertmanager service port: `9093`
- Prometheus rules ConfigMap: `prometheus-alert-rules`
- Rule file: `/etc/prometheus/rules/alert-rules.yml`
- Git branch: `main`

## 3. Alerting architecture

1. Alert rules are maintained in Git under
   `observability/prometheus/alert-rules.yaml`.
2. Argo CD synchronizes the manifests into the Kubernetes `monitoring`
   namespace.
3. The `prometheus-alert-rules` ConfigMap is mounted into the Prometheus
   pod at `/etc/prometheus/rules/`.
4. Prometheus evaluates the rules and creates alert instances when their
   expressions meet the configured conditions.
5. Prometheus sends firing alerts to Alertmanager at
   `alertmanager.monitoring.svc.cluster.local:9093`.
6. Alertmanager receives and groups alerts according to its routing
   configuration.

## 4. Production alert rules

### PaymentAPIDown

Expression:

`up{job="kubernetes-services",service="payment-api"} == 0`

Condition: remains true for one minute.

Severity: `critical`

Purpose: detect a discovered Payment API target that is not being scraped
successfully.

### PaymentAPITargetsMissing

Expression:

`absent(up{job="kubernetes-services",service="payment-api"})`

Condition: remains true for one minute.

Severity: `critical`

Purpose: detect when Prometheus cannot find any matching Payment API targets.

These rules are distinct: one detects a failed scrape target, while the other
detects the absence of matching targets.

## 5. Automated regression tests

The rule tests are maintained in:

- `tests/observability/alert-test-rules.yml`
- `tests/observability/alert-tests.yml`

The synthetic test rule uses `test_metric > 0` with a one-minute pending
duration. The regression test checks that the alert is not firing before
the duration elapses, becomes firing at the expected evaluation time, and
resolves after the input metric returns to zero.

Run the tests locally from the repository root:

```bash
docker run --rm --entrypoint /bin/promtool \
  -v "$PWD:/workspace" \
  -w /workspace \
  prom/prometheus:v3.5.0 \
  test rules tests/observability/alert-tests.yml
```

Expected result: `SUCCESS`.

The GitHub Actions workflow runs this rule-test command as part of the
alert regression test job.

## 6. Live end-to-end delivery test

A temporary rule named `SecureOpsLiveDeliveryTest` was added to the
production alert ConfigMap manifest for a controlled runtime test.

Expression:

`vector(1)`

Because the expression continuously returns a sample, the alert should fire
without a `for` delay.

The temporary rule was deployed through the normal GitOps path:

1. Validate the rendered manifests and check the diff.
2. Commit and push the temporary rule to `main`.
3. Sync the `monitoring-stack` application in Argo CD.
4. Confirm Argo CD reports `Synced` and `Healthy`.
5. Verify the temporary rule exists in the deployed ConfigMap.
6. Reload Prometheus and query its rules and alerts APIs.
7. Query Alertmanager's alerts API to verify receipt.

### Verification commands

Check the deployed rule:

```bash
kubectl -n monitoring get configmap prometheus-alert-rules \
  -o go-template='{{index .data "alert-rules.yml"}}'
```

Reload Prometheus when needed:

```bash
curl -i -X POST http://localhost:19090/-/reload
```

Check the loaded rules:

```bash
curl -s http://localhost:19090/api/v1/rules
```

Check Prometheus alerts:

```bash
curl -s http://localhost:19090/api/v1/alerts
```

Check alerts received by Alertmanager:

```bash
curl -s http://localhost:19093/api/v2/alerts
```

The local ports above assume active port-forwards to the Prometheus and
Alertmanager services.

### Observed result

The live test returned the following evidence:

- Prometheus reported `SecureOpsLiveDeliveryTest` in the `firing` state.
- Alertmanager reported the same alert in the `active` state.
- The test alert's summary was `SecureOps live alert delivery test`.
- Prometheus and Alertmanager therefore demonstrated internal alert delivery
  for this test.

## 7. Troubleshooting: stale rule after cleanup

After the temporary rule was removed from Git and Argo CD synchronized the
updated ConfigMap, Prometheus initially continued reporting the old rule.

The investigation established that:

- The deployed ConfigMap contained only the two production rules.
- The mounted rule file in the Prometheus pod contained only those rules.
- The Prometheus rules API still reported the temporary rule in memory.
- A lifecycle reload returned HTTP 200 but did not remove the stale rule
  from the active rule group.

The Prometheus deployment was restarted to reconcile its runtime state with
the mounted configuration.

After the restart, the rules API showed both production rules and no
temporary rule. The alerts API also confirmed that the temporary alert was
no longer firing.

Operational lesson: a successful reload response is not sufficient proof
that the active rules match the intended configuration. Verify the loaded
rules through the Prometheus API and inspect the mounted file when results
disagree. If a restart is considered, first understand the persistence
configuration and its impact on monitoring data.

## 8. Cleanup and final state

The temporary test rule was removed from
`observability/prometheus/alert-rules.yaml`, committed, pushed, and synced
through Argo CD.

Final verification confirmed:

- Argo CD application `monitoring-stack`: `Synced` / `Healthy`.
- `PaymentAPIDown`: present in the loaded rules.
- `PaymentAPITargetsMissing`: present in the loaded rules.
- `SecureOpsLiveDeliveryTest`: absent from the loaded rules.
- Temporary alert: not firing.
- Git working tree: clean.

Relevant commits:

- `4c7db50` — `test: cover alert resolution lifecycle`
- `7883ff8` — `test: add temporary live alert delivery probe`
- `08c269b` — `test: remove temporary live alert delivery probe`

## 9. Scope and limitations

This validation proves the synthetic alert lifecycle in automated tests and
internal Prometheus-to-Alertmanager delivery for a live test alert.

It does not prove:

- External email, Slack, or webhook notification delivery.
- Successful notification delivery to an external on-call system.
- A real Payment API outage or recovery in production.

No external notification receiver was configured as part of this test.

## 10. Reproduction checklist

- [ ] Run Prometheus rule regression tests.
- [ ] Review the rendered Kubernetes manifests.
- [ ] Sync `monitoring-stack` through Argo CD.
- [ ] Confirm production rules are loaded by Prometheus.
- [ ] For a controlled test, add a temporary synthetic alert through Git.
- [ ] Verify Prometheus reports the alert as firing.
- [ ] Verify Alertmanager reports the alert as active.
- [ ] Remove the temporary rule through Git and sync Argo CD.
- [ ] Verify the temporary rule and firing alert are gone.
- [ ] Confirm the repository is clean.
