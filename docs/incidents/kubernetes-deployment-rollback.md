# Kubernetes Deployment Rollback Runbook

## Purpose
Investigate failed Kubernetes rollouts, recover from a faulty release, and verify application health.

## Safety
- Verify the Kubernetes context, namespace, and Deployment before acting.
- Capture diagnostic evidence before changing the workload.
- Obtain approval before a production rollback.
- Do not roll back a healthy Deployment without a verified reason.
- A Deployment rollback does not reverse database migrations or external side effects.
- Never publish credentials or secret values in incident evidence.

## 1. Identify the target

    kubectl config current-context
    export NAMESPACE=default
    export DEPLOYMENT=payment-api
    kubectl -n "$NAMESPACE" get deployment "$DEPLOYMENT"
    kubectl -n "$NAMESPACE" get pods -o wide

Stop if the context or target is incorrect.

## 2. Investigate

    kubectl -n "$NAMESPACE" rollout status "deployment/$DEPLOYMENT" --timeout=120s
    kubectl -n "$NAMESPACE" describe deployment "$DEPLOYMENT"
    kubectl -n "$NAMESPACE" rollout history "deployment/$DEPLOYMENT"
    kubectl -n "$NAMESPACE" get events --sort-by=.metadata.creationTimestamp

Use an actual pod name from `kubectl get pods`; do not type the placeholder `POD_NAME` literally.

    kubectl -n "$NAMESPACE" describe pod ACTUAL_POD_NAME
    kubectl -n "$NAMESPACE" logs ACTUAL_POD_NAME --all-containers=true --tail=200
    kubectl -n "$NAMESPACE" logs ACTUAL_POD_NAME --all-containers=true --previous --tail=200

Replace `ACTUAL_POD_NAME` with a real pod name. Previous logs are available only when a container has restarted and Kubernetes retains its previous logs.

Look for unavailable replicas, scheduling failures, image-pull errors, probe failures, restarts, and warning events.

## 3. Capture evidence

    kubectl -n "$NAMESPACE" get deployment "$DEPLOYMENT" -o yaml > /tmp/payment-api-deployment-before-rollback.yaml
    kubectl -n "$NAMESPACE" rollout history "deployment/$DEPLOYMENT"
    kubectl -n "$NAMESPACE" get pods -o wide

Record the time, affected release, symptoms, logs/events, and actions. Review exported files before sharing them.

## 4. Roll back only when justified

Review the history and identify a known-good revision:

    kubectl -n "$NAMESPACE" rollout history "deployment/$DEPLOYMENT"

After verifying the target and obtaining required approval, roll back to the previous revision:

    kubectl -n "$NAMESPACE" rollout undo "deployment/$DEPLOYMENT"

Or select a verified numeric revision:

    kubectl -n "$NAMESPACE" rollout undo "deployment/$DEPLOYMENT" --to-revision=REVISION_NUMBER

Replace `REVISION_NUMBER` with an actual numeric revision. These commands change the live workload; do not execute them merely to test this runbook.

During documentation work, `payment-api` had two available replicas and a successful rollout, so no rollback was indicated.

## 5. Verify recovery

    kubectl -n "$NAMESPACE" rollout status "deployment/$DEPLOYMENT" --timeout=180s
    kubectl -n "$NAMESPACE" get deployment "$DEPLOYMENT"
    kubectl -n "$NAMESPACE" get pods -o wide
    kubectl -n "$NAMESPACE" get events --sort-by=.metadata.creationTimestamp

Verify application health and readiness using the configured service access method. For a local test, if the container listens on port 8000:

    kubectl -n "$NAMESPACE" port-forward "deployment/$DEPLOYMENT" 18080:8000

In a second terminal:

    curl --fail --show-error http://127.0.0.1:18080/health
    curl --fail --show-error http://127.0.0.1:18080/ready

Adjust the port and paths to the application. Stop port-forwarding with Ctrl+C.

## 6. If recovery fails
1. Keep the incident active and notify the incident owner.
2. Review pod conditions, events, and current or previous logs.
3. Check dependencies, configuration, secrets, storage, and networking.
4. Check whether external changes make the previous revision incompatible.
5. Follow the approved escalation plan instead of repeatedly rolling back.

## 7. Closeout
Record the incident timeline, Deployment and revision, symptoms, recovery action, verification results, root cause, and prevention work.

## Related documentation
- [Secure delivery gates](../engineering/secure-delivery-gates.md)
- [Payment API hardening verification](../security/payment-api-hardening-verification.md)
- [Payment API Kind node reboot incident](./payment-api-kind-node-reboot.md)
