# SecureOps — Enterprise DevSecOps Platform on OpenShift

A production-oriented DevSecOps platform demonstrating secure CI/CD, GitOps, container orchestration, Infrastructure as Code, configuration management, security scanning, observability, centralized logging, and production troubleshooting.

## Project Overview

SecureOps simulates an enterprise financial-services environment where application teams need a standardized and secure software delivery platform.

The platform is designed to address common enterprise DevOps challenges:

- Manual and inconsistent deployments
- Security vulnerabilities reaching deployment stages
- Lack of standardized CI/CD pipelines
- Infrastructure provisioning inconsistencies
- Configuration drift
- Limited application and infrastructure observability
- Centralized logging requirements
- Production troubleshooting and rollback
- Auditability and controlled deployment processes

The project brings these capabilities together into a single DevSecOps workflow running on Kubernetes/OpenShift.

## Architecture

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
    |
    +--> SonarQube (SAST)
    |
    +--> Dependency-Track (SCA / SBOM)
    |
    +--> Trivy (Container Security)
    |
    v
Docker Build
    |
    v
Container Registry
    |
    v
GitOps Repository
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
    +--> Fluent Bit
            |
            v
        Logstash
            |
            v
      Elasticsearch
            |
            v
         Kibana


Infrastructure provisioning and configuration management are handled separately through Terraform and Ansible.

```text
Terraform
    |
    v
AWS Infrastructure
    |
    +--> VPC
    +--> Subnets
    +--> Security Groups
    +--> IAM
    +--> EC2

Ansible
    |
    +--> Linux Configuration
    +--> Docker
    +--> Monitoring Agents
    +--> Security Hardening

## Core Capabilities

### CI/CD

- Jenkins pipeline automation
- Tekton Kubernetes-native pipelines
- Automated unit testing
- Security quality gates
- Container image build and publishing
- Deployment automation

### DevSecOps

- SonarQube SAST
- Dependency-Track software composition analysis
- CycloneDX SBOM generation
- Trivy container vulnerability scanning
- Security policy enforcement
- Secrets protection
- Deployment security controls

### Containers and Orchestration

- Docker
- Kubernetes
- OpenShift
- Kubernetes Services
- ConfigMaps
- Secrets
- Probes
- Resource limits
- Horizontal Pod Autoscaling
- Network Policies
- RBAC

### GitOps

- Argo CD
- Declarative deployment manifests
- Environment-specific configuration
- Drift detection
- Automated synchronization
- Self-healing
- Rollback

### Infrastructure as Code

- Terraform
- AWS VPC
- Subnets
- Security Groups
- IAM
- EC2
- Environment separation

### Configuration Management

- Ansible
- Linux administration
- Docker installation and configuration
- Node Exporter deployment
- Linux hardening

### Observability

- Prometheus metrics
- Grafana dashboards
- Alertmanager notifications
- Application health monitoring
- Infrastructure monitoring
- Kubernetes monitoring

### Centralized Logging

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

### Automation

- Bash operational scripts
- Python automation
- Health checks
- Deployment validation
- Incident debugging
- Rollback automation
- Image policy validation

## Applications

SecureOps contains three sample microservices:

| Application | Purpose |
|---|---|
| payment-api | Simulates payment processing |
| order-api | Simulates order management |
| notification-api | Simulates notification delivery |

Each application is designed to expose:

- Health endpoint
- Readiness endpoint
- Prometheus metrics
- Application API
- Container image
- Automated tests

## Environments

The platform models three deployment environments:

```text
Development
     |
     v
Staging
     |
     v
Production
```

Each environment uses controlled configuration and deployment policies.
## Security Gates

The CI/CD workflow is designed around security gates:

```text
Source Code
    |
    v
Unit Tests
    |
    v
SonarQube
    |
    v
Dependency-Track / SBOM
    |
    v
Docker Build
    |
    v
Trivy Scan
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
OpenShift
```

A failed security gate prevents the pipeline from progressing to the deployment stage.

## Production Troubleshooting Scenarios

The project intentionally demonstrates real-world operational incidents:

1. CrashLoopBackOff
2. Security gate failure
3. High CPU / memory utilization
4. Argo CD configuration drift
5. Failed deployment and rollback

Each incident includes investigation steps, commands, evidence, root cause, remediation, and preventive actions.
## Technology Stack

| Area | Technologies |
|---|---|
| Version Control | Git, GitHub |
| CI/CD | Jenkins, Tekton |
| GitOps | Argo CD |
| Containers | Docker |
| Orchestration | Kubernetes, OpenShift |
| Cloud | AWS |
| IaC | Terraform |
| Configuration Management | Ansible |
| SAST | SonarQube |
| SCA / SBOM | Dependency-Track, CycloneDX |
| Container Security | Trivy |
| Monitoring | Prometheus, Grafana |
| Alerting | Alertmanager |
| Logging | Fluent Bit, Logstash, Elasticsearch, Kibana |
| Automation | Python, Bash |
| OS | Linux |

## Repository Structure

```text
secureops-devsecops-platform/
|-- applications/
|-- ansible/
|-- argocd/
|-- ci/
|-- docs/
|-- gitops/
|-- incidents/
|-- kubernetes/
|-- logging/
|-- observability/
|-- openshift/
|-- scripts/
|-- security/
|-- terraform/
|-- .github/
|-- .editorconfig
|-- .gitignore
|-- LICENSE
`-- README.md
```

## Implementation Roadmap

The platform will be implemented incrementally:

- [ ] Application microservices
- [ ] Docker containerization
- [ ] Kubernetes manifests
- [ ] OpenShift deployment
- [ ] Jenkins CI pipeline
- [ ] Tekton pipeline
- [ ] SonarQube integration
- [ ] Dependency-Track and SBOM
- [ ] Trivy security scanning
- [ ] Argo CD GitOps deployment
- [ ] Terraform AWS infrastructure
- [ ] Ansible configuration management
- [ ] Prometheus monitoring
- [ ] Grafana dashboards
- [ ] Alertmanager
- [ ] Centralized logging with ELK
- [ ] Production troubleshooting scenarios
- [ ] Automated validation and operational scripts
- [ ] Documentation and interview guide
## DevOps Engineering Objectives

This project demonstrates practical experience across the complete DevOps lifecycle:

```text
Plan
 |
 v
Code
 |
 v
Build
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

The goal is not only to deploy applications, but to demonstrate how an enterprise DevOps engineer designs, secures, operates, monitors, and troubleshoots a production-oriented platform.

## Documentation

Detailed documentation will cover:

- Architecture
- CI/CD
- GitOps
- OpenShift
- AWS
- Terraform
- Ansible
- Security
- Observability
- Troubleshooting
- Production incidents
- Interview questions and project explanation

## Project Status

This project is under active development.

Individual components will be marked as implemented only after they are tested and verified.

## Author

**Gaurav Singh Ghodage**

DevOps / DevSecOps Engineering Portfolio Project
## Security Gates

The CI/CD workflow is designed around security gates:

```text
Source Code
    |
    v
Unit Tests
    |
    v
SonarQube
    |
    v
Dependency-Track / SBOM
    |
    v
Docker Build
    |
    v
Trivy Scan
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
OpenShift
```

A failed security gate prevents the pipeline from progressing to the deployment stage.

## Production Troubleshooting Scenarios

The project intentionally demonstrates real-world operational incidents:

1. CrashLoopBackOff
2. Security gate failure
3. High CPU / memory utilization
4. Argo CD configuration drift
5. Failed deployment and rollback

Each incident includes investigation steps, commands, evidence, root cause, remediation, and preventive actions.
