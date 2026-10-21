output "vpc_id" {
  description = "ID of the SecureOps VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets."
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets."
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "availability_zones" {
  description = "Availability zones used by the subnets."
  value       = data.aws_availability_zones.available.names
}
