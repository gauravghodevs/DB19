# Payment API Operational Verification Runbook

## Purpose

Verify that the SecureOps Payment API is deployed, reachable through its Kubernetes Service, and responding correctly after a deployment or infrastructure event.

This runbook describes the local Kind development environment. It is not a substitute for an approved production change or incident-response process.

## Scope

- Kubernetes cluster: local Kind
- Kind node container: `devops-control-plane`
- Namespace: `default`
- Deployment: `payment-api`
- Service: `payment-api`
- Application port: `8000`
- Verification script: `scripts/verify-payment-api.sh`

## Prerequisites

- Docker is running.
- The Kind node container exists and is running.
- The Kubernetes API is reachable from the Kind node.
- The Payment API Deployment and Service exist.
- The verification script is executable.

Confirm the environment before investigating an application failure:

    docker ps --filter name=devops-control-plane
    docker inspect devops-control-plane --format '{{.State.Status}}'

The expected container state is `running`.

## Run the verification

From the repository root:

    ./scripts/verify-payment-api.sh

The script performs these checks in order:

1. Confirms the Kind node container exists.
2. Waits for the `payment-api` Deployment rollout.
3. Compares desired replicas with ready replicas.
4. Confirms that the Service has ready EndpointSlice addresses.
5. Sends requests to the application through the Kubernetes Service.
6. Fails with a non-zero exit status if a required check fails.

The script uses Kubernetes EndpointSlices rather than the deprecated Endpoints API.

## Success criteria

A successful run should confirm:

- Deployment rollout completed.
- All desired replicas are ready.
- At least one ready Service endpoint exists.
- `/` returns HTTP 200 and identifies `payment-api`.
- `/health` returns HTTP 200 with status `healthy`.
- `/ready` returns HTTP 200 with status `ready`.
- `/metrics/` returns HTTP 200 with Prometheus-format process or Python metrics.

Example output:

    Desired: 2 | Ready: 2
    Ready endpoints: <ready endpoint addresses>
    PASS / HTTP 200
    PASS /health HTTP 200
    PASS /ready HTTP 200
    PASS /metrics/ HTTP 200
    All application endpoint checks passed.
    SUCCESS: payment-api verification completed.

The endpoint addresses and pod names can change as Kubernetes recreates pods.

## Troubleshooting

### 1. Kind node container is missing

Inspect the available containers:

    docker ps -a --filter name=devops-control-plane

If the container is stopped, investigate why before restarting or recreating the cluster. Do not delete the cluster as an initial troubleshooting step.

### 2. Deployment rollout times out

Inspect the workload and recent events:

    docker exec devops-control-plane kubectl --kubeconfig /etc/kubernetes/admin.conf -n default get deployment payment-api
    docker exec devops-control-plane kubectl --kubeconfig /etc/kubernetes/admin.conf -n default get pods -o wide
    docker exec devops-control-plane kubectl --kubeconfig /etc/kubernetes/admin.conf -n default get events --sort-by=.metadata.creationTimestamp

Describe an affected pod and review its current or previous logs before changing the workload.

### 3. Desired and ready replicas differ

Check pod readiness, container restarts, resource limits, probe failures, and scheduling events. Do not increase replicas or change resource settings without evidence.

### 4. No ready EndpointSlice addresses

Inspect the Service, its selector, and the EndpointSlices:

    docker exec devops-control-plane kubectl --kubeconfig /etc/kubernetes/admin.conf -n default describe service payment-api
    docker exec devops-control-plane kubectl --kubeconfig /etc/kubernetes/admin.conf -n default get endpointslice -l kubernetes.io/service-name=payment-api -o wide

Check whether the Service selector matches the pod labels and whether the selected pods are Ready.

### 5. An application endpoint fails

Inspect pod logs, readiness status, and the Service configuration. The verification script requests the Service from inside a Payment API pod, so a failure may involve application behavior, Service routing, or pod readiness.

Do not restart or roll back a healthy workload merely to make the check pass.

## Operational safety

- Confirm the cluster and namespace before making changes.
- Capture logs, events, and workload state before remediation.
- Do not expose credentials, tokens, or secret values in incident reports.
- Use the deployment rollback runbook only when a rollback is justified.
- Re-run verification after remediation and record the result.
- A successful endpoint check confirms behavior at that moment; it does not prove long-term availability or production readiness.

## Related documentation

- [Kubernetes Deployment rollback](../incidents/kubernetes-deployment-rollback.md)
- [Kind node reboot incident report](../incidents/payment-api-kind-node-reboot.md)
- [Secure delivery gates](../engineering/secure-delivery-gates.md)

## Evidence record

For a deployment or incident, record:

- Date and time
- Git commit and deployed image tag
- Cluster and namespace
- Desired and ready replica counts
- Verification result
- Relevant warnings or errors
- Remediation performed, if any
- Follow-up actions and owner

Never claim a check passed unless its output was observed.
