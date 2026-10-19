# SecureOps — Enterprise DevSecOps Platform

A production-oriented DevSecOps portfolio project demonstrating secure application delivery, containerization, Kubernetes operations, infrastructure automation, security gates, GitOps, observability, and production troubleshooting.

> **Implementation status:** built incrementally. This README distinguishes verified implementation from planned platform capabilities.

## Project Overview

SecureOps simulates an enterprise financial-services environment where application teams need a standardized and secure software delivery platform.

The engineering goal is to build a delivery path that is:

- repeatable
- testable
- security-aware
- observable
- recoverable
- suitable for Kubernetes/OpenShift environments

## Current Implementation

The following capabilities are implemented and tested today:

| Capability | Status | Evidence |
|---|---|---|
| FastAPI payment service | Implemented | `applications/payment-api` |
| Automated API tests | Implemented | pytest test suite |
| Docker containerization | Implemented | `applications/payment-api/Dockerfile` |
| Container security scanning | Implemented | Trivy image scanning |
| Kubernetes Deployment | Implemented | 2 replicas on Kind |
| Kubernetes Service | Implemented | ClusterIP service |
| Health/readiness probes | Implemented | `/health`, `/ready` |
| Resource requests/limits | Implemented | Deployment manifest |
| Prometheus metrics | Implemented | `/metrics/` |
| Kustomize base | Implemented | `kubernetes/base` |
| OpenShift deployment | Planned | Next platform stage |
| Jenkins pipeline | Example present; execution not verified | `ci/jenkins/Jenkinsfile` |
| Tekton | Planned | CI/CD stage |
| SonarQube SAST | Planned | Security stage |
| CycloneDX SBOM generation | Implemented | `.github/workflows/dependency-supply-chain.yml` |
| Argo CD GitOps | Manifests present; reconciliation not verified | `argocd/` |
| Terraform AWS infrastructure | Planned | Infrastructure stage |
| Ansible configuration management | Planned | Automation stage |
| Prometheus / Grafana configuration | Present; deployment not verified | `observability/` |
| Centralized ELK logging | Planned | Logging stage |

## Architecture Target

The target platform architecture is:

```text
Developer
    |
    v
GitHub
    |
    v
Jenkins / Tekton
    |
    +--> Unit Tests
    +--> SonarQube (SAST)
    +--> Dependency-Track / SBOM
    +--> Trivy
    |
    v
Docker Build
    |
    v
Container Registry
    |
    v
GitOps
    |
    v
Argo CD
    |
    v
OpenShift / Kubernetes
    |
    +--> payment-api
    +--> order-api
    +--> notification-api
    |
    +--> Prometheus
    +--> Grafana
    +--> Alertmanager
    |
    +--> Fluent Bit -> Logstash -> Elasticsearch -> Kibana

Terraform -> AWS infrastructure
Ansible  -> Linux configuration and hardening
```

> The architecture above is the **target design**. Individual components are marked implemented only after they are built and verified.

## Implemented Application: payment-api

The first application is a small FastAPI service designed to exercise the platform delivery path.

### Endpoints

| Endpoint | Purpose |
|---|---|
| `/` | Service status |
| `/health` | Liveness health check |
| `/ready` | Readiness check |
| `/metrics/` | Prometheus metrics |

Example service response:

```json
{"service":"payment-api","status":"running"}
```

### Application structure

```text
applications/payment-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_api.py
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── sonar-project.properties
```

## Kubernetes

The payment API is deployed to a local Kind cluster with:

- 2 replicas
- ClusterIP Service
- CPU and memory requests/limits
- HTTP readiness probe
- HTTP liveness probe
- Prometheus scrape annotations
- Kustomize-managed base manifests

Verified deployment flow:

```text
Docker Image
    |
    v
Kind Cluster
    |
    v
Deployment
    |
    +--> Pod
    +--> Pod
    |
    v
ClusterIP Service
    |
    v
Application
```

### Runtime Container Hardening

The `payment-api` Deployment applies Kubernetes container security controls:

- `runAsNonRoot: true` — prevents the container from running as root.
- `runAsUser: 10001` — runs the application with the non-root UID configured in the image.
- `allowPrivilegeEscalation: false` — disables privilege escalation.
- `capabilities.drop: [ALL]` — drops all Linux capabilities from the container.
- `seccompProfile.type: RuntimeDefault` — uses the container runtime's default seccomp profile.

**Runtime verification:** The rollout completed successfully with 2/2 replicas ready. Both new pods reported zero restarts at verification time. The `/health`, `/ready`, and `/metrics/` endpoints each returned HTTP 200.

## Security Engineering

Container images are scanned with Trivy as part of the development workflow.

The project treats security scanning as an engineering gate rather than a documentation checkbox.

Important distinction:

- **0 OS HIGH/CRITICAL findings** were observed for the verified `payment-api:0.3.0` image scan.
- The same scan reported Python-package/vendor metadata findings.
- Those findings were investigated rather than hidden or falsely reported as zero vulnerabilities.

This project intentionally documents security findings and their context instead of suppressing them merely to produce a clean badge.

## Implemented CI and Security Workflows

GitHub Actions workflows are configured for application CI, Kubernetes security, secret scanning, dependency review, dependency auditing and SBOM generation, and documentation validation.

The application CI workflow includes automated tests and linting, Kubernetes manifest validation, container build and smoke tests, and Trivy image scanning. The dependency supply-chain workflow audits Python dependencies and generates a CycloneDX SBOM.

Additional delivery configuration exists for Jenkins and Argo CD. These files demonstrate integration paths, but their presence alone does not establish that Jenkins jobs ran successfully or that Argo CD is synchronizing a live cluster.

Workflow configuration and execution results are separate evidence. Check the relevant GitHub Actions run before claiming a gate passed.


## Planned Infrastructure Automation

### Terraform

Target AWS infrastructure includes:

- VPC
- subnets
- security groups
- IAM
- EC2

### Ansible

Target configuration-management responsibilities include:

- Linux configuration
- Docker installation/configuration
- Node Exporter
- security hardening
- operational configuration

These components will be marked implemented only after testing.

## Planned Observability and Logging

### Metrics and alerting

```text
Application / Kubernetes
        |
        v
   Prometheus
        |
        +--> Grafana
        |
        +--> Alertmanager
```

### Centralized logging

```text
Application Logs
      |
      v
 Fluent Bit
      |
      v
 Logstash
      |
      v
Elasticsearch
      |
      v
  Kibana
```

## Production Troubleshooting Scenarios

The project will document practical incident-response scenarios such as:

1. CrashLoopBackOff
2. failed security gate
3. high CPU or memory utilization
4. GitOps configuration drift
5. failed deployment and rollback

Each scenario is intended to include:

- symptoms
- investigation commands
- evidence
- root cause
- remediation
- preventive controls

### Documented Incident Runbooks

- [Kubernetes Deployment rollback](docs/incidents/kubernetes-deployment-rollback.md)
- [Payment API Kind node reboot incident](docs/incidents/payment-api-kind-node-reboot.md)

## Technology Stack

| Area | Technologies |
|---|---|
| Version control | Git, GitHub |
| Application | Python, FastAPI |
| Testing | pytest |
| Containers | Docker |
| Orchestration | Kubernetes, OpenShift |
| Local platform | Kind |
| CI/CD | Jenkins, Tekton |
| GitOps | Argo CD |
| Cloud | AWS |
| IaC | Terraform |
| Configuration management | Ansible |
| SAST | SonarQube |
| SCA / SBOM | Dependency-Track, CycloneDX |
| Container security | Trivy |
| Monitoring | Prometheus, Grafana |
| Alerting | Alertmanager |
| Logging | Fluent Bit, Logstash, Elasticsearch, Kibana |
| Operating system | Linux |
| Automation | Python, Bash |

## Repository Structure

```text
secureops-devsecops-platform/
├── applications/
├── ansible/
├── argocd/
├── ci/
├── docs/
├── gitops/
├── incidents/
├── kubernetes/
├── logging/
├── observability/
├── openshift/
├── scripts/
├── security/
├── terraform/
├── .github/
├── .editorconfig
├── .gitignore
├── LICENSE
└── README.md
```

## Implementation Roadmap

### Completed or configured

- [x] FastAPI payment API and automated API tests
- [x] Docker containerization and non-root runtime hardening
- [x] Trivy image scanning and security finding investigation
- [x] Kubernetes Deployment, Service, health/readiness probes, and resource controls
- [x] Prometheus application metrics and Kustomize base
- [x] GitHub Actions workflows for application CI, Kubernetes security, secret scanning, dependency review, dependency audit/SBOM, and documentation validation
- [x] CycloneDX SBOM generation and Python dependency audit workflow
- [x] Prometheus/Grafana configuration, dashboard definition, and alert rules
- [x] Jenkins pipeline and Argo CD application configuration files added to the repository
- [x] Two incident runbooks documented

Configuration being present does not by itself prove a successful pipeline run, live Argo CD synchronization, or a deployed monitoring stack. Verify execution evidence separately.

### Remaining work

- [ ] Verify Jenkins pipeline execution and integrate it into the delivery path
- [ ] Add a Tekton pipeline
- [ ] Configure and verify a SonarQube SAST quality gate
- [ ] Integrate Dependency-Track, if required beyond SBOM generation
- [ ] Verify Argo CD synchronization against a live cluster
- [ ] Deploy and validate the Prometheus/Grafana stack and alert delivery
- [ ] Deploy to OpenShift
- [ ] Implement and test Terraform AWS infrastructure
- [ ] Implement and test Ansible configuration management
- [ ] Implement centralized logging with ELK
- [ ] Expand incident runbooks and operational automation
- [ ] Add final architecture, validation evidence, and interview documentation

## Engineering Principles

```text
Plan
 |
 v
Code
 |
 v
Test
 |
 v
Secure
 |
 v
Package
 |
 v
Deploy
 |
 v
Observe
 |
 v
Troubleshoot
 |
 v
Improve
```

The objective is not to list DevOps tools. It is to demonstrate how those tools are used to build, secure, deploy, observe, troubleshoot, and improve a production-oriented platform.

## Project Status

### Active development

The repository is intentionally implemented in verifiable stages. Documentation is updated as capabilities move from planned to tested implementation.

## Author

### Gaurav Singh Ghodage

DevOps / DevSecOps Engineering Portfolio Project
