# Monitoring Stack Deployment and Verification

This runbook deploys the repository's Prometheus and Grafana configuration through Argo CD. It assumes a working Kubernetes context with Argo CD already installed. Run commands from the repository root.

## 1. Confirm the target cluster

Check the active context before changing anything:

```bash
kubectl config current-context
kubectl get nodes
kubectl -n argocd get applications.argoproj.io
```

Stop if this is not the intended lab cluster.

## 2. Create the Grafana admin Secret outside Git

The Grafana Deployment reads the `grafana-admin` Secret with keys `admin-user` and `admin-password`. The Secret is intentionally not committed to this repository.

Create the namespace and Secret locally:

```bash
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

umask 077
secret_dir="$(mktemp -d)"
trap 'rm -rf "$secret_dir"; unset GF_ADMIN_USER GF_ADMIN_PASSWORD' EXIT

read -r -p "Grafana admin username: " GF_ADMIN_USER
read -r -s -p "Grafana admin password: " GF_ADMIN_PASSWORD
printf '\n'

printf '%s' "$GF_ADMIN_USER" > "$secret_dir/admin-user"
printf '%s' "$GF_ADMIN_PASSWORD" > "$secret_dir/admin-password"

kubectl -n monitoring create secret generic grafana-admin \
  --from-file=admin-user="$secret_dir/admin-user" \
  --from-file=admin-password="$secret_dir/admin-password" \
  --dry-run=client -o yaml | kubectl apply -f -

rm -rf "$secret_dir"
unset GF_ADMIN_USER GF_ADMIN_PASSWORD
trap - EXIT

kubectl -n monitoring get secret grafana-admin
```

Use a unique password and do not paste it into Git, a ticket, or chat. For shared or production environments, use the organization's approved secret manager and rotation process.

## 3. Register the monitoring Application in Argo CD

From the repository root:

```bash
kubectl apply -f argocd/monitoring-stack-application.yaml
kubectl -n argocd get application monitoring-stack
```

If automated sync is not configured, sync `monitoring-stack` from the Argo CD UI or with the Argo CD CLI:

```bash
argocd app sync monitoring-stack
```

Do not assume that applying the Application object means its resources are deployed. Confirm sync and health status.

## 4. Verify rollout and application health

```bash
kubectl -n argocd get application monitoring-stack \
  -o jsonpath='{.status.sync.status}{" / "}{.status.health.status}{"\n"}'

kubectl -n monitoring rollout status deployment/prometheus --timeout=180s
kubectl -n monitoring rollout status deployment/grafana --timeout=180s
kubectl -n monitoring get pods,services
```

Both Deployments should complete their rollouts and the pods should become Ready. If Grafana is not Ready, inspect the pod events and logs; a missing `grafana-admin` Secret or a missing key will prevent it from starting.

```bash
kubectl -n monitoring get events --sort-by=.lastTimestamp
kubectl -n monitoring logs deployment/grafana --tail=100
kubectl -n monitoring logs deployment/prometheus --tail=100
```

## 5. Test the endpoints

Open separate terminals for port forwarding:

```bash
kubectl -n monitoring port-forward service/prometheus 9090:9090
```

```bash
kubectl -n monitoring port-forward service/grafana 3000:3000
```

From another terminal, verify health endpoints:

```bash
curl --fail --silent http://127.0.0.1:9090/-/ready
curl --fail --silent http://127.0.0.1:3000/api/health
```

In Prometheus, open `http://127.0.0.1:9090/targets` and confirm the payment API target is discovered and healthy. In Grafana, sign in with the credentials provisioned in Step 2 and confirm the Prometheus data source and the SecureOps payment API dashboard are loaded.

## 6. Troubleshooting

- **Argo CD OutOfSync:** inspect the diff in Argo CD and confirm the Application points at branch `main` and path `observability`.
- **Grafana pod not Ready:** check that Secret `grafana-admin` exists in namespace `monitoring` and contains both required keys.
- **Prometheus pod not Ready:** inspect logs for invalid Prometheus configuration or rule-file errors.
- **No payment API target:** confirm the payment API Service has the expected Prometheus scrape annotations and that the API is running in the same cluster.
- **No alert notification:** the repository defines Prometheus alert rules, but an alert receiver/delivery integration must be configured separately before notifications can be expected.

## Completion criteria

- Argo CD reports the Application as Synced and Healthy.
- Prometheus and Grafana Deployments roll out successfully.
- Both health endpoints return successful responses.
- The payment API target appears healthy in Prometheus.
- Grafana loads the Prometheus data source and payment API dashboard.

Record actual observed results in the project notes; do not mark a check complete solely because the manifest exists.
