# Provider-Agnostic Modules for Multi-Cloud Deployment

# Kubernetes Cluster Module
module "kubernetes_cluster" {
  source = "./modules/kubernetes"

  providers = {
    aws    = aws
    azurerm = azurerm
    google = google
  }

  project_name  = var.project_name
  environment   = var.environment
  instance_type = var.instance_types[var.environment]
  node_count    = var.node_count[var.environment]
}

# Database Module
module "database" {
  source = "./modules/database"

  providers = {
    aws    = aws
    azurerm = azurerm
    google = google
  }

  project_name = var.project_name
  environment  = var.environment
}

# Cache Module
module "cache" {
  source = "./modules/cache"

  providers = {
    aws    = aws
    azurerm = azurerm
    google = google
  }

  project_name = var.project_name
  environment  = var.environment
}

# Load Balancer Module
module "load_balancer" {
  source = "./modules/load-balancer"

  providers = {
    aws    = aws
    azurerm = azurerm
    google = google
  }

  project_name = var.project_name
  environment  = var.environment
}