# Variables for Multi-Cloud Deployment

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "supplychain-finance-platform"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "azure_region" {
  description = "Azure region"
  type        = string
  default     = "West US 2"
}

variable "gcp_project" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-west1"
}

variable "cluster_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.24"
}

variable "node_count" {
  description = "Number of nodes in the cluster"
  type        = number
  default     = 3
}

variable "node_instance_type" {
  description = "Instance type for nodes"
  type        = string
  default     = "t3.medium"
}

variable "max_node_count" {
  description = "Maximum number of nodes"
  type        = number
  default     = 10
}

variable "min_node_count" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}