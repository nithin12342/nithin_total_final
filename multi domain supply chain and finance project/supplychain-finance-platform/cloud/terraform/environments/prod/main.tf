# Main configuration for production environment

module "vpc" {
  source              = "../../modules/vpc"
  project_name        = "supplychain-finance-platform"
  environment         = var.environment
  vpc_cidr            = var.vpc_cidr
  availability_zones  = var.availability_zones
  region              = var.region
}

module "kubernetes" {
  source              = "../../modules/kubernetes"
  project_name        = "supplychain-finance-platform"
  environment         = var.environment
  region              = var.region
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnets
  instance_type       = var.instance_type
  min_nodes           = var.min_nodes
  max_nodes           = var.max_nodes
  desired_nodes       = var.desired_nodes
}

module "database" {
  source              = "../../modules/database"
  project_name        = "supplychain-finance-platform"
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnets
  db_instance_class   = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_password         = var.db_password
}

module "load_balancer" {
  source              = "../../modules/load_balancer"
  project_name        = "supplychain-finance-platform"
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.public_subnets
  certificate_arn     = var.certificate_arn
}

module "monitoring" {
  source              = "../../modules/monitoring"
  project_name        = "supplychain-finance-platform"
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnets
}