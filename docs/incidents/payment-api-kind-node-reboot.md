# Incident Report: Payment API Probe Failures After Kind Node Reboot

## Incident Summary

| Field | Details |
|---|---|
| Service | SecureOps Payment API |
| Environment | Local Kind Kubernetes cluster (`devops`) |
| Namespace | `default` |
| Deployment | `payment-api` |
| Image | `secureops-payment-api:0.1.6` |
| Severity | Development-environment incident; no production impact assessed |
| Status | Recovered; monitoring verification completed |
| Observed | October 15, 2026 |
| Replicas | 2 |

## Summary

The Payment API experienced Kubernetes liveness and readiness probe failures around a Kind node reboot. Kubernetes reported that the pod sandboxes had changed and restarted the application containers.

Following recovery, both replicas returned to Ready status. Requests to all four application endpoints succeeded, and a subsequent monitoring window showed no additional container restarts.

The exact root cause of the probe timeouts has not been conclusively established.

## Impact

- Both Payment API pods experienced repeated container restarts.
- Liveness and readiness probes timed out or received connection-refused errors.
- The Deployment later reported two available replicas and zero unavailable replicas.
- All four tested application endpoints returned HTTP 200 during recovery verification.
- No production impact was assessed because this incident occurred in the local development cluster.

## Timeline

Times below are based on the collected command output. They are not a complete event-by-event timeline.

1. Kubernetes recorded liveness and readiness probe timeouts for both Payment API pods.
2. The Kind node reported a reboot.
3. Kubernetes reported `SandboxChanged` for both Payment API pods.
4. Liveness probes subsequently received connection-refused errors, and Kubernetes restarted both containers.
5. The containers started again using the existing `secureops-payment-api:0.1.6` image.
6. Both pods returned to `1/1 Running` and Ready status.
7. Requests to `/`, `/health`, `/ready`, and `/metrics/` succeeded.
8. An approximately two-minute monitoring check showed both pods remained Ready, with restart counts unchanged at five per pod.

## Evidence Collected

### Kubernetes state

The Deployment reported:

- Desired replicas: 2
- Updated replicas: 2
- Available replicas: 2
- Unavailable replicas: 0

Both pods reported `1/1 Running` and five restarts.

### Probe configuration

- Liveness endpoint: `/health`
- Readiness endpoint: `/ready`
- Probe timeout: 1 second
- Liveness period: 15 seconds
- Readiness period: 10 seconds
- Container CPU request: 100m
- Container CPU limit: 500m
- Container memory request: 128Mi
- Container memory limit: 256Mi

### Relevant events

Collected Kubernetes events included:

- Liveness and readiness probe failures with `context deadline exceeded`.
- Probe failures with `connect: connection refused`.
- A Kind node `Rebooted` event.
- `SandboxChanged` events for both Payment API pods.
- Container restart events following liveness probe failures.

### Container termination details

The last recorded termination for each pod showed:

- Reason: `Completed`
- Exit code: `0`

Previous container logs ended with `asyncio.exceptions.CancelledError` during the ASGI shutdown sequence. This is consistent with a shutdown being in progress but does not, by itself, identify the initiating cause.

Docker reported the Kind node container was running and `OOMKilled=false`. This does not rule out every possible resource-pressure condition inside the environment.

### Resource observations

At one sample, Docker reported approximately:

- Kind node CPU: 89.34%
- Kind node memory: 925.3 MiB of 2.843 GiB

A later sample reported CPU at 54.00% and memory at 888.8 MiB.

These are point-in-time measurements, not proof that CPU pressure caused the incident. Kubernetes Metrics API was unavailable, so per-pod metrics could not be retrieved using `kubectl top`.

## Recovery Verification

The following requests were executed from inside a Payment API pod against the Kubernetes Service:

| Endpoint | HTTP status | Observed response time |
|---|---:|---:|
| `/` | 200 | 0.709 s |
| `/health` | 200 | 0.066 s |
| `/ready` | 200 | 0.018 s |
| `/metrics/` | 200 | 0.255 s |

The root endpoint returned:

`{"service":"payment-api","status":"running"}`

The health endpoint returned:

`{"status":"healthy"}`

The readiness endpoint returned:

`{"status":"ready"}`

The metrics endpoint returned Prometheus-format metrics.

### Stability check

Both pods were checked eight times at approximately 15-second intervals.

At every observation:

- Both pods remained Ready.
- Both restart counts remained at five.
- No additional restarts were observed during the approximately two-minute window.

This confirms recovery during the observation period, not long-term stability.

## Root Cause Assessment

**Confirmed:** The Kind node rebooted, Kubernetes recreated the pod sandboxes, and the Payment API containers experienced probe failures and restarts.

**Not confirmed:** Whether the node reboot fully explains all probe timeouts, or whether transient CPU pressure, scheduling delays, or another node-level issue contributed.

The available evidence does not justify attributing the incident solely to an application defect, an out-of-memory kill, or an overly strict probe timeout.

## Corrective and Preventive Actions

### Completed

- [x] Checked pod readiness and restart counts.
- [x] Reviewed current and previous container logs.
- [x] Inspected Kubernetes events and Deployment conditions.
- [x] Checked Kind node memory usage and Docker OOM status.
- [x] Verified all four application endpoints from inside the cluster.
- [x] Monitored both replicas for approximately two minutes without additional restarts.

### Follow-up

- [ ] Investigate the Kind/Docker node reboot and correlate it with host events.
- [ ] Capture longer-duration CPU and memory observations if probe timeouts recur.
- [ ] Enable or repair Kubernetes Metrics API if per-pod resource monitoring is needed.
- [ ] Review probe timeout settings only if further evidence demonstrates that legitimate responses exceed the configured timeout.
- [ ] Consider adding a `startupProbe` if future startup measurements demonstrate that it is needed.
- [ ] Repeat the stability check after any infrastructure or probe configuration change.

## Lessons Learned

1. A Running pod does not automatically prove that its application is responsive.
2. Probe failures should be correlated with node events, container termination state, and application logs.
3. Shutdown exceptions must be interpreted in context; they are not sufficient evidence of an application crash.
4. Recovery should be verified with real endpoint requests and observed over time.
5. Root-cause conclusions must distinguish confirmed events from plausible explanations.

## Final Status

**Recovered and verified during a short observation window.**

Both replicas were Ready, all four application endpoints returned HTTP 200, and no new restarts occurred during the approximately two-minute monitoring period.

The underlying cause of the node reboot and probe timeouts remains under investigation.
