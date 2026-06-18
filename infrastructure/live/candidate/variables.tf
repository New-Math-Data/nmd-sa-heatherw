variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "AWS CLI profile"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "sa-assessment"
}

variable "vpc_id" {
  description = "ID of the VPC created by the admin CloudFormation stack"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs (used by the ALB; at least 2 AZs)"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs (used by ECS tasks; at least 2 AZs)"
  type        = list(string)
}

variable "candidate_name" {
  description = "Candidate name (used for resource naming and tagging)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.candidate_name))
    error_message = "candidate_name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "ecr_repository_url" {
  description = "ECR repository URL (provided by the admin CloudFormation stack)"
  type        = string
}

variable "database_url" {
  description = "PostgreSQL connection URL (e.g. postgresql+asyncpg://user:pass@host:5432/dbname)"
  type        = string
  sensitive   = true
}
