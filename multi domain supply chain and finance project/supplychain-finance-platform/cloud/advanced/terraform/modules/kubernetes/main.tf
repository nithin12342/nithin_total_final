# Provider-Agnostic Kubernetes Module

# Local values to determine which provider to use
locals {
  # In a real implementation, this would be determined by a variable
  # For this example, we'll just use AWS
  provider_type = "aws"
  
  cluster_endpoint = {
    aws    = try(aws_eks_cluster.main[0].endpoint, "")
    azure  = try(azurerm_kubernetes_cluster.main[0].fqdn, "")
    gcp    = try(google_container_cluster.main[0].endpoint, "")
  }[local.provider_type]
  
  cluster_ca_certificate = {
    aws    = try(aws_eks_cluster.main[0].certificate_authority[0].data, "")
    azure  = try(azurerm_kubernetes_cluster.main[0].kube_config[0].cluster_ca_certificate, "")
    gcp    = try(google_container_cluster.main[0].master_auth[0].cluster_ca_certificate, "")
  }[local.provider_type]
  
  cluster_name = {
    aws    = try(aws_eks_cluster.main[0].name, "")
    azure  = try(azurerm_kubernetes_cluster.main[0].name, "")
    gcp    = try(google_container_cluster.main[0].name, "")
  }[local.provider_type]
}

# AWS EKS (if provider is AWS)
resource "aws_eks_cluster" "main" {
  count = local.provider_type == "aws" ? 1 : 0

  name     = "${var.project_name}-${var.environment}-eks"
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = "1.28"

  vpc_config {
    subnet_ids = var.subnet_ids
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]
}

resource "aws_eks_node_group" "main" {
  count = local.provider_type == "aws" ? 1 : 0

  cluster_name    = aws_eks_cluster.main[0].name
  node_group_name = "${var.project_name}-${var.environment}-node-group"
  node_role_arn   = aws_iam_role.eks_node_group[0].arn
  subnet_ids      = var.subnet_ids

  scaling_config {
    desired_size = var.node_count
    max_size     = var.node_count * 2
    min_size     = 1
  }
}

# Azure AKS (if provider is Azure)
resource "azurerm_kubernetes_cluster" "main" {
  count = local.provider_type == "azure" ? 1 : 0

  name                = "${var.project_name}-${var.environment}-aks"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "${var.project_name}-${var.environment}-aks"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.instance_type
  }

  identity {
    type = "SystemAssigned"
  }
}

# GCP GKE (if provider is GCP)
resource "google_container_cluster" "main" {
  count = local.provider_type == "gcp" ? 1 : 0

  name     = "${var.project_name}-${var.environment}-gke"
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

resource "google_container_node_pool" "main" {
  count = local.provider_type == "gcp" ? 1 : 0

  name       = "${var.project_name}-${var.environment}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.main[0].name
  node_count = var.node_count

  node_config {
    machine_type = var.instance_type

    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]
  }
}