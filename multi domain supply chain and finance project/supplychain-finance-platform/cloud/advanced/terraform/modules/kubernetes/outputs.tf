# Outputs for Kubernetes Module

output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = local.cluster_endpoint
}

output "cluster_ca_certificate" {
  description = "Kubernetes cluster CA certificate"
  value       = local.cluster_ca_certificate
  sensitive   = true
}

output "cluster_name" {
  description = "Kubernetes cluster name"
  value       = local.cluster_name
}