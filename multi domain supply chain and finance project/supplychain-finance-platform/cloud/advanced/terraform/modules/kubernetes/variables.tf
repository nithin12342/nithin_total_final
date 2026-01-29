# Variables for Kubernetes Module

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "instance_type" {
  description = "Instance type for nodes"
  type        = string
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
}