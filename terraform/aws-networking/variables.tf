variable "aws_region" {
  description = "AWS region for the networking foundation."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name prefix for SecureOps resources."
  type        = string
  default     = "secureops"
}

variable "vpc_cidr" {
  description = "CIDR range for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR ranges for public subnets."
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]

  validation {
    condition     = length(var.public_subnet_cidrs) == 2
    error_message = "Provide exactly two public subnet CIDRs."
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR ranges for private subnets."
  type        = list(string)
  default     = ["10.20.11.0/24", "10.20.12.0/24"]

  validation {
    condition     = length(var.private_subnet_cidrs) == 2
    error_message = "Provide exactly two private subnet CIDRs."
  }
}
