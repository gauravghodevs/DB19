#!/usr/bin/env bash
set -Eeuo pipefail

KIND_NODE="${KIND_NODE:-devops-control-plane}"
NAMESPACE="${NAMESPACE:-default}"

if ! docker inspect "$KIND_NODE" >/dev/null 2>&1; then
  echo "ERROR: Kind node container '$KIND_NODE' not found." >&2
  exit 1
fi

kube() {
  docker exec "$KIND_NODE" kubectl \
    --kubeconfig /etc/kubernetes/admin.conf \
    --namespace "$NAMESPACE" "$@"
}

echo "==> Checking deployment rollout"
kube rollout status deployment/payment-api --timeout=120s

echo "==> Checking replicas"
desired="$(kube get deployment payment-api -o jsonpath='{.spec.replicas}')"
ready="$(kube get deployment payment-api -o jsonpath='{.status.readyReplicas}')"
ready="${ready:-0}"

echo "Desired: $desired | Ready: $ready"

if [[ "$ready" != "$desired" || "$desired" -lt 1 ]]; then
  echo "ERROR: deployment replicas are not all ready." >&2
  exit 1
fi

echo "==> Checking Service endpoints"
endpoints="$(kube get endpoints payment-api \
  -o jsonpath='{.subsets[*].addresses[*].ip}')"

if [[ -z "$endpoints" ]]; then
  echo "ERROR: payment-api Service has no ready endpoints." >&2
  exit 1
fi

echo "Ready endpoints: $endpoints"

echo "==> Testing application endpoints from a payment-api pod"
pod="$(kube get pods -l app=payment-api \
  -o jsonpath='{.items[0].metadata.name}')"

if [[ -z "$pod" ]]; then
  echo "ERROR: no payment-api pod found." >&2
  exit 1
fi

kube exec "$pod" -- python -c '
import json
import urllib.request

base = "http://payment-api:8000"
checks = {
    "/": lambda b: json.loads(b).get("service") == "payment-api",
    "/health": lambda b: json.loads(b).get("status") == "healthy",
    "/ready": lambda b: json.loads(b).get("status") == "ready",
    "/metrics/": lambda b: "python_" in b or "process_" in b,
}

for path, validate in checks.items():
    with urllib.request.urlopen(base + path, timeout=5) as response:
        body = response.read().decode()
        if response.status != 200 or not validate(body):
            raise SystemExit("FAIL " + path + ": unexpected response")
        print("PASS", path, "HTTP", response.status)

print("All application endpoint checks passed.")
'

echo "SUCCESS: payment-api verification completed."
