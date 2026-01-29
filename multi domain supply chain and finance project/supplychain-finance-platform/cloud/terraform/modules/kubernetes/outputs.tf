# Outputs for Kubernetes module

output "cluster_endpoint" {
  description = "Kubernetes cluster endpoint"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_ca_certificate" {
  description = "Kubernetes cluster CA certificate"
  value       = aws_eks_cluster.main.certificate_authority[0].data
  sensitive   = true
}

output "cluster_name" {
  description = "Name of the Kubernetes cluster"
  value       = aws_eks_cluster.main.name
}

output "cluster_id" {
  description = "ID of the Kubernetes cluster"
  value       = aws_eks_cluster.main.id
}

output "node_group_role_arn" {
  description = "ARN of the node group IAM role"
  value       = aws_iam_role.node_group.arn
}