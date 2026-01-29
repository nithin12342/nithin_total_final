# Backend configuration for staging environment

terraform {
  backend "s3" {
    bucket         = "supplychain-finance-platform-tf-state-staging"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "supplychain-finance-platform-tf-locks-staging"
    encrypt        = true
  }
}