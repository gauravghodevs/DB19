# AWS Networking Foundation

Terraform configuration for a SecureOps portfolio VPC.

## Resources

- One VPC with DNS support and hostnames enabled.
- Two public subnets across available Availability Zones.
- Two private subnets across available Availability Zones.
- An internet gateway and public route table.
- A private route table with no default internet route.
- Tags identifying SecureOps-managed resources.

## Validate without deploying

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

These commands do not create AWS infrastructure. `terraform init` downloads the
provider plugin and therefore requires network access.

Do not run `terraform apply` without reviewing the plan, confirming AWS
credentials and permissions, and explicitly approving the potential costs.

Private subnets have no NAT gateway in this foundation, avoiding NAT gateway
hourly and data-processing charges. No EC2 instances or security groups are
created by this module yet.
