# Outputs for Multi-Cloud Deployment

output "aws_cluster_info" {
  description = "AWS EKS cluster information"
  value = {
    name     = aws_eks_cluster.main.name
    endpoint = aws_eks_cluster.main.endpoint
    region   = var.aws_region
  }
}

output "azure_cluster_info" {
  description = "Azure AKS cluster information"
  value = {
    name     = azurerm_kubernetes_cluster.main.name
    endpoint = azurerm_kubernetes_cluster.main.kube_config[0].host
    region   = var.azure_region
  }
}

output "gcp_cluster_info" {
  description = "GCP GKE cluster information"
  value = {
    name     = google_container_cluster.main.name
    endpoint = google_container_cluster.main.endpoint
    region   = var.gcp_region
  }
}

output "cluster_endpoints" {
  description = "All cluster endpoints"
  value = {
    aws  = aws_eks_cluster.main.endpoint
    azure = azurerm_kubernetes_cluster.main.kube_config[0].host
    gcp  = google_container_cluster.main.endpoint
  }
}