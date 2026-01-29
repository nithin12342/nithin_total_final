#!/bin/bash

# Azure Infrastructure Setup Script for Student Project
# This script sets up all Azure resources within free tiers

set -e

echo "🚀 Setting up Azure infrastructure for Supply Chain Finance Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Variables
RESOURCE_GROUP="supplychain-student-rg"
LOCATION="eastus"
ACR_NAME="supplychainstudent"
AKS_NAME="supplychain-aks"
POSTGRES_NAME="supplychain-postgres"
REDIS_NAME="supplychain-redis"
STORAGE_NAME="supplychainstorage"
KEYVAULT_NAME="supplychain-keyvault"

print_status "Checking Azure CLI login..."
if ! az account show > /dev/null 2>&1; then
    print_error "Please login to Azure first: az login"
    exit 1
fi

# Set student subscription
print_status "Setting Azure for Students subscription..."
az account set --subscription "Azure for Students"

print_status "Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --tags environment=student project=supplychain-finance \
    --output none

print_success "Resource group created: $RESOURCE_GROUP"

# Create Azure Container Registry (Basic - Free tier eligible)
print_status "Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output none

print_success "Container Registry created: $ACR_NAME"

# Get ACR credentials
print_status "Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query username -o tsv)

ACR_PASSWORD=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --query passwords[0].value -o tsv)

print_status "ACR Login Server: $ACR_NAME.azurecr.io"
print_status "ACR Username: $ACR_USERNAME"

# Create PostgreSQL server (Basic Single Server - Free tier)
print_status "Creating PostgreSQL database..."
az postgres server create \
    --resource-group $RESOURCE_GROUP \
    --name $POSTGRES_NAME \
    --location $LOCATION \
    --admin-user adminuser \
    --admin-password "SecureP@ssw0rd123" \
    --sku-name B_Gen5_1 \
    --storage-size 5120 \
    --backup-retention 7 \
    --output none

print_success "PostgreSQL server created: $POSTGRES_NAME"

# Create database
print_status "Creating database..."
az postgres db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_NAME \
    --name supplychaindb \
    --output none

# Configure PostgreSQL firewall to allow all Azure services
print_status "Configuring PostgreSQL firewall..."
az postgres server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_NAME \
    --name AllowAllAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0 \
    --output none

print_success "PostgreSQL firewall configured"

# Create Redis Cache (Basic C0 - Free tier)
print_status "Creating Redis Cache..."
az redis create \
    --resource-group $RESOURCE_GROUP \
    --name $REDIS_NAME \
    --location $LOCATION \
    --sku Basic \
    --size C0 \
    --output none

print_success "Redis Cache created: $REDIS_NAME"

# Create Storage Account (Standard LRS - Free tier)
print_status "Creating Storage Account..."
az storage account create \
    --resource-group $RESOURCE_GROUP \
    --name $STORAGE_NAME \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2 \
    --output none

print_success "Storage Account created: $STORAGE_NAME"

# Create blob container for static assets
print_status "Creating blob container for static assets..."
az storage container create \
    --name static-assets \
    --account-name $STORAGE_NAME \
    --public-access blob \
    --output none

# Create file share for shared data
print_status "Creating file share for shared data..."
az storage share create \
    --name shared-data \
    --account-name $STORAGE_NAME \
    --output none

print_success "Storage containers created"

# Create Key Vault
print_status "Creating Key Vault..."
az keyvault create \
    --name $KEYVAULT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --enabled-for-deployment true \
    --enabled-for-disk-encryption true \
    --enabled-for-template-deployment true \
    --output none

print_success "Key Vault created: $KEYVAULT_NAME"

# Store secrets in Key Vault
print_status "Storing secrets in Key Vault..."
az keyvault secret set \
    --vault-name $KEYVAULT_NAME \
    --name "postgres-password" \
    --value "SecureP@ssw0rd123" \
    --output none

az keyvault secret set \
    --vault-name $KEYVAULT_NAME \
    --name "redis-connection" \
    --value "$REDIS_NAME.redis.cache.windows.net:6380,password=SecureP@ssw0rd123,ssl=True,abortConnect=False" \
    --output none

az keyvault secret set \
    --vault-name $KEYVAULT_NAME \
    --name "storage-connection" \
    --value "DefaultEndpointsProtocol=https;AccountName=$STORAGE_NAME;AccountKey=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_NAME --query [0].value -o tsv);EndpointSuffix=core.windows.net" \
    --output none

print_success "Secrets stored in Key Vault"

# Create Azure Kubernetes Service (Free tier: 2 vCPUs)
print_status "Creating AKS cluster..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_NAME \
    --node-count 1 \
    --node-vm-size Standard_B2s \
    --enable-managed-identity \
    --generate-ssh-keys \
    --attach-acr $ACR_NAME \
    --tags environment=student project=supplychain-finance \
    --output none

print_success "AKS cluster created: $AKS_NAME"

# Get cluster credentials
print_status "Getting AKS credentials..."
az aks get-credentials \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_NAME \
    --overwrite-existing

# Create namespace
print_status "Creating Kubernetes namespace..."
kubectl create namespace supplychain --dry-run=client -o yaml | kubectl apply -f -

# Create Azure Monitor resources (Free tier)
print_status "Creating Application Insights..."
az monitor app-insights component create \
    --app supplychain-app-insights \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --kind web \
    --output none

print_success "Application Insights created"

# Create Log Analytics workspace (Free tier: 5GB)
print_status "Creating Log Analytics workspace..."
az monitor log-analytics workspace create \
    --resource-group $RESOURCE_GROUP \
    --workspace-name supplychain-log-analytics \
    --location $LOCATION \
    --sku PerGB2018 \
    --output none

print_success "Log Analytics workspace created"

# Enable monitoring on AKS
print_status "Enabling monitoring on AKS..."
az aks enable-addons \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_NAME \
    --addons monitoring \
    --workspace-resource-id $(az monitor log-analytics workspace show \
        --resource-group $RESOURCE_GROUP \
        --workspace-name supplychain-log-analytics \
        --query id -o tsv) \
    --output none

print_success "AKS monitoring enabled"

# Create Azure Static Web App for frontend (Free)
print_status "Creating Static Web App for frontend..."
az staticwebapp create \
    --name supplychain-frontend \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --app-location "frontend/react-app" \
    --api-location "api" \
    --output-location "build" \
    --token $GITHUB_TOKEN \
    --tags environment=student project=supplychain-finance \
    --output none

print_success "Static Web App created"

# Create Azure Functions for serverless components (Free tier)
print_status "Creating Function App for AI processing..."
az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --name supplychain-ai-functions \
    --storage-account $STORAGE_NAME \
    --plan supplychain-consumption-plan \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --output none

print_success "Function App created"

# Create API Management (Developer tier - has free trial)
print_status "Creating API Management..."
az apim create \
    --resource-group $RESOURCE_GROUP \
    --name supplychain-apim \
    --location $LOCATION \
    --publisher-email student@domain.com \
    --publisher-name "SupplyChain Student" \
    --sku-name Developer \
    --output none

print_success "API Management created"

# Create Azure Front Door for CDN (Free tier available)
print_status "Creating Front Door for CDN..."
az afd profile create \
    --resource-group $RESOURCE_GROUP \
    --profile-name supplychain-cdn \
    --location Global \
    --sku Standard_AzureFrontDoor \
    --output none

print_success "Front Door profile created"

# Create output file with connection strings
print_status "Creating connection strings file..."
cat > azure-connection-strings.txt << EOF
# Azure Connection Strings for Supply Chain Finance Platform
# Copy these to your application configuration

# PostgreSQL
POSTGRES_CONNECTION_STRING="postgresql://adminuser:SecureP@ssw0rd123@${POSTGRES_NAME}.postgres.database.azure.com:5432/supplychaindb"

# Redis
REDIS_CONNECTION_STRING="${REDIS_NAME}.redis.cache.windows.net:6380,password=SecureP@ssw0rd123,ssl=True,abortConnect=False"

# Storage
STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=${STORAGE_NAME};AccountKey=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_NAME --query [0].value -o tsv);EndpointSuffix=core.windows.net"

# ACR
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
ACR_USERNAME="${ACR_USERNAME}"
ACR_PASSWORD="${ACR_PASSWORD}"

# Key Vault
KEYVAULT_URI="https://${KEYVAULT_NAME}.vault.azure.com/"

# Application Insights
APP_INSIGHTS_INSTRUMENTATION_KEY="$(az monitor app-insights component show --resource-group $RESOURCE_GROUP --app supplychain-app-insights --query instrumentationKey -o tsv)"

# Static Web App
STATIC_WEB_APP_URL="https://supplychain-frontend.azurestaticapps.net"

# API Management
APIM_GATEWAY_URL="https://supplychain-apim.azure-api.net"

# AKS Cluster
AKS_CLUSTER_NAME="${AKS_NAME}"
RESOURCE_GROUP="${RESOURCE_GROUP}"
EOF

print_success "Connection strings saved to azure-connection-strings.txt"

print_success "=== AZURE INFRASTRUCTURE SETUP COMPLETED ==="
print_success "Resource Group: $RESOURCE_GROUP"
print_success "Location: $LOCATION"
print_success "AKS Cluster: $AKS_NAME"
print_success "PostgreSQL: $POSTGRES_NAME"
print_success "Redis: $REDIS_NAME"
print_success "Storage: $STORAGE_NAME"
print_success "ACR: $ACR_NAME.azurecr.io"
print_success "Key Vault: $KEYVAULT_NAME"
print_success "Static Web App: supplychain-frontend.azurestaticapps.net"
print_success "API Management: supplychain-apim.azure-api.net"

print_status "Next steps:"
print_status "1. Run: ./azure-build-push-containers.sh"
print_status "2. Run: ./azure-deploy-to-aks.sh"
print_status "3. Run: ./azure-setup-monitoring.sh"

print_status "🎉 Azure infrastructure setup completed successfully!"
