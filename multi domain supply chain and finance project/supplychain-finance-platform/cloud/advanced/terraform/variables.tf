# Variables for Multi-Cloud Deployment

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "supply-chain-platform"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

# AWS Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_availability_zones" {
  description = "AWS availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

# Azure Variables
variable "azure_region" {
  description = "Azure region"
  type        = string
  default     = "West US 2"
}

variable "azure_resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "supply-chain-platform-rg"
}

# GCP Variables
variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
  default     = "supply-chain-platform"
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-west1"
}

# Common Variables
variable "instance_types" {
  description = "Instance types for different environments"
  type = object({
    dev     = string
    staging = string
    prod    = string
  })
  default = {
    dev     = "t3.medium"
    staging = "t3.large"
    prod    = "m5.xlarge"
  }
}

variable "node_count" {
  description = "Number of nodes per environment"
  type = object({
    dev     = number
    staging = number
    prod    = number
  })
  default = {
    dev     = 2
    staging = 3
    prod    = 5
  }
}

variable "enable_monitoring" {
  description = "Enable comprehensive monitoring"
  type        = bool
  default     = true
}

variable "enable_security" {
  description = "Enable advanced security features"
  type        = bool
  default     = true
}

variable "enable_disaster_recovery" {
  description = "Enable disaster recovery setup"
  type        = bool
  default     = true
}