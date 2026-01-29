# Backend configuration for development environment

terraform {
  backend "s3" {
    bucket         = "supplychain-finance-platform-tf-state-dev"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "supplychain-finance-platform-tf-locks-dev"
    encrypt        = true
  }
}