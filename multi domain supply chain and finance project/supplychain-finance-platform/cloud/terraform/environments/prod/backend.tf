# Backend configuration for production environment

terraform {
  backend "s3" {
    bucket         = "supplychain-finance-platform-tf-state-prod"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "supplychain-finance-platform-tf-locks-prod"
    encrypt        = true
  }
}