# variables.tf

variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "env" {
  description = "Deployment environment: dev, staging, or prod"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.env)
    error_message = "env must be dev, staging, or prod"
  }
}

variable "project" {
  description = "Project identifier used in resource naming"
  type        = string
  default     = "dataops"
}

variable "snowflake_aws_account_arn" {
  description = "Snowflake AWS account ARN for storage integration trust policy"
  type        = string
  sensitive   = true
}

variable "snowflake_external_id" {
  description = "External ID from Snowflake storage integration for secure assume-role"
  type        = string
  sensitive   = true
}
