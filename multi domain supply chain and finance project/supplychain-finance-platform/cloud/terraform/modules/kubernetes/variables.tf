# Variables for Kubernetes module

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
}

variable "min_nodes" {
  description = "Minimum number of nodes in the cluster"
  type        = number
}

variable "max_nodes" {
  description = "Maximum number of nodes in the cluster"
  type        = number
}

variable "desired_nodes" {
  description = "Desired number of nodes in the cluster"
  type        = number
}