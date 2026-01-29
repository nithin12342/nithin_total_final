#!/bin/bash

# Azure ARM Template Deployment Script
# Uses Infrastructure as Code for Azure Student deployment

set -e

echo "🏗️  Deploying Azure infrastructure using ARM Template..."

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
ENVIRONMENT=${1:-student}
LOCATION="East US"
RESOURCE_GROUP="supplychain-${ENVIRONMENT}-rg"
TEMPLATE_FILE="azure-deploy-arm-template.json"
PARAMETERS_FILE="azure-deploy-parameters-${ENVIRONMENT}.json"

print_status "Environment: $ENVIRONMENT"
print_status "Location: $LOCATION"
print_status "Resource Group: $RESOURCE_GROUP"

# Check Azure CLI login
if ! az account show > /dev/null 2>&1; then
    print_error "Please login to Azure first: az login"
    exit 1
fi

# Set student subscription
print_status "Setting Azure for Students subscription..."
az account set --subscription "Azure for Students"

# Create parameters file
print_status "Creating parameters file..."
cat > $PARAMETERS_FILE << EOF
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environment": {
      "value": "$ENVIRONMENT"
    },
    "location": {
      "value": "$LOCATION"
    },
    "postgresPassword": {
      "value": "SecureP@ssw0rd123"
    },
    "studentEmail": {
      "value": "$(az account show --query user.name -o tsv)"
    }
  }
}
EOF

print_success "Parameters file created: $PARAMETERS_FILE"

# Validate template
print_status "Validating ARM template..."
az deployment group validate \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters $PARAMETERS_FILE \
    --output none

print_success "ARM template validation passed"

# Deploy infrastructure
print_status "Deploying Azure infrastructure..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file $TEMPLATE_FILE \
    --parameters $PARAMETERS_FILE \
    --query properties.outputs \
    --output json)

if [ $? -ne 0 ]; then
    print_error "ARM template deployment failed!"
    exit 1
fi

print_success "Infrastructure deployed successfully"

# Extract outputs
print_status "Extracting deployment outputs..."
ACR_LOGIN_SERVER=$(echo $DEPLOYMENT_OUTPUT | jq -r '.acrLoginServer.value')
ACR_USERNAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.acrUsername.value')
AKS_CLUSTER_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.aksClusterName.value')
POSTGRES_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.postgresServerName.value')
REDIS_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.redisName.value')
STORAGE_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.storageAccountName.value')
KEYVAULT_URI=$(echo $DEPLOYMENT_OUTPUT | jq -r '.keyVaultUri.value')
APP_INSIGHTS_KEY=$(echo $DEPLOYMENT_OUTPUT | jq -r '.appInsightsInstrumentationKey.value')

print_status "Creating connection strings file..."
cat > azure-connection-strings.txt << EOF
# Azure Connection Strings for Supply Chain Finance Platform
# Generated from ARM Template Deployment

# PostgreSQL
POSTGRES_CONNECTION_STRING="postgresql://adminuser:SecureP@ssw0rd123@${POSTGRES_NAME}.postgres.database.azure.com:5432/supplychaindb"

# Redis
REDIS_CONNECTION_STRING="${REDIS_NAME}.redis.cache.windows.net:6380,password=SecureP@ssw0rd123,ssl=True,abortConnect=False"

# Storage
STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=${STORAGE_NAME};AccountKey=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_NAME --query [0].value -o tsv);EndpointSuffix=core.windows.net"

# ACR
ACR_LOGIN_SERVER="${ACR_LOGIN_SERVER}"
ACR_USERNAME="${ACR_USERNAME}"
ACR_PASSWORD="$(az acr credential show --resource-group $RESOURCE_GROUP --name ${ACR_LOGIN_SERVER} --query passwords[0].value -o tsv)"

# Key Vault
KEYVAULT_URI="${KEYVAULT_URI}"

# Application Insights
APP_INSIGHTS_INSTRUMENTATION_KEY="${APP_INSIGHTS_KEY}"

# AKS Cluster
AKS_CLUSTER_NAME="${AKS_CLUSTER_NAME}"
RESOURCE_GROUP="${RESOURCE_GROUP}"
LOCATION="${LOCATION}"

# Static Web App (to be created)
STATIC_WEB_APP_URL="https://supplychain-${ENVIRONMENT}.azurestaticapps.net"

# API Management (to be created)
APIM_GATEWAY_URL="https://supplychain-apim-${ENVIRONMENT}.azure-api.net"

EOF

print_success "Connection strings saved to azure-connection-strings.txt"

# Get ACR password
ACR_PASSWORD=$(az acr credential show \
    --resource-group $RESOURCE_GROUP \
    --name ${ACR_LOGIN_SERVER} \
    --query passwords[0].value -o tsv)

# Update connection strings with ACR password
sed -i "s|ACR_PASSWORD=\".*\"|ACR_PASSWORD=\"${ACR_PASSWORD}\"|g" azure-connection-strings.txt

print_status "Setting up Azure Container Registry..."

# Login to ACR
az acr login --name ${ACR_LOGIN_SERVER}

# Attach ACR to AKS
print_status "Attaching ACR to AKS..."
az aks update \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --attach-acr ${ACR_LOGIN_SERVER} \
    --output none

print_success "ACR attached to AKS"

# Get AKS credentials
print_status "Getting AKS credentials..."
az aks get-credentials \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --overwrite-existing

print_status "Creating Kubernetes namespace..."
kubectl create namespace supplychain --dry-run=client -o yaml | kubectl apply -f -

print_status "Setting up Azure Monitor..."

# Enable monitoring on AKS
LOG_ANALYTICS_ID=$(az monitor log-analytics workspace show \
    --resource-group $RESOURCE_GROUP \
    --workspace-name supplychain-logs-${ENVIRONMENT} \
    --query id -o tsv)

az aks enable-addons \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --addons monitoring \
    --workspace-resource-id $LOG_ANALYTICS_ID \
    --output none

print_success "Azure Monitor enabled on AKS"

print_status "Creating Azure Static Web App..."

# Create Static Web App for frontend
az staticwebapp create \
    --name supplychain-${ENVIRONMENT} \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --app-location "frontend/react-app" \
    --api-location "api" \
    --output-location "build" \
    --token $GITHUB_TOKEN \
    --tags environment=$ENVIRONMENT \
    --output none

print_success "Static Web App created"

print_status "Creating Azure API Management..."

# Create API Management
az apim create \
    --resource-group $RESOURCE_GROUP \
    --name supplychain-apim-${ENVIRONMENT} \
    --location $LOCATION \
    --publisher-email $(az account show --query user.name -o tsv) \
    --publisher-name "SupplyChain Student" \
    --sku-name Developer \
    --output none

print_success "API Management created"

print_status "Storing secrets in Key Vault..."

# Store secrets in Key Vault
az keyvault secret set \
    --vault-name ${KEYVAULT_URI} \
    --name "postgres-password" \
    --value "SecureP@ssw0rd123" \
    --output none

az keyvault secret set \
    --vault-name ${KEYVAULT_URI} \
    --name "redis-connection" \
    --value "${REDIS_NAME}.redis.cache.windows.net:6380,password=SecureP@ssw0rd123,ssl=True,abortConnect=False" \
    --output none

az keyvault secret set \
    --vault-name ${KEYVAULT_URI} \
    --name "storage-connection" \
    --value "DefaultEndpointsProtocol=https;AccountName=${STORAGE_NAME};AccountKey=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_NAME --query [0].value -o tsv);EndpointSuffix=core.windows.net" \
    --output none

print_success "Secrets stored in Key Vault"

print_status "Creating Azure Front Door..."

# Create Front Door for CDN
az afd profile create \
    --resource-group $RESOURCE_GROUP \
    --profile-name supplychain-cdn-${ENVIRONMENT} \
    --location Global \
    --sku Standard_AzureFrontDoor \
    --output none

az afd endpoint create \
    --resource-group $RESOURCE_GROUP \
    --profile-name supplychain-cdn-${ENVIRONMENT} \
    --endpoint-name supplychain-frontend-${ENVIRONMENT} \
    --location Global \
    --output none

print_success "Azure Front Door created"

print_status "Setting up cost management..."

# Create cost budget
az consumption budget create \
    --amount 50 \
    --name "${ENVIRONMENT}Budget" \
    --resource-group $RESOURCE_GROUP \
    --category Cost \
    --time-grain Monthly \
    --time-period 2025-01-01T00:00:00Z 2025-12-31T23:59:59Z \
    --notification action-group="supplychain-cost-alerts" threshold=80 operator=GreaterThan

print_success "Cost budget configured"

print_status "Creating deployment validation..."

# Create validation script
cat > validate-arm-deployment.sh << EOF
#!/bin/bash
echo "🔍 Validating ARM template deployment..."

# Test all Azure resources
echo "Testing PostgreSQL..."
az postgres db show \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_NAME \
    --name supplychaindb > /dev/null

echo "Testing Redis..."
az redis show \
    --resource-group $RESOURCE_GROUP \
    --name $REDIS_NAME > /dev/null

echo "Testing Storage..."
az storage account show \
    --resource-group $RESOURCE_GROUP \
    --name $STORAGE_NAME > /dev/null

echo "Testing AKS..."
az aks show \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME > /dev/null

echo "Testing ACR..."
az acr show \
    --resource-group $RESOURCE_GROUP \
    --name ${ACR_LOGIN_SERVER} > /dev/null

echo "Testing Key Vault..."
az keyvault show \
    --name ${KEYVAULT_URI} > /dev/null

echo "✅ All Azure resources are ready!"
EOF

chmod +x validate-arm-deployment.sh

print_success "=== ARM TEMPLATE DEPLOYMENT COMPLETED ==="
print_success "Resource Group: $RESOURCE_GROUP"
print_success "AKS Cluster: $AKS_CLUSTER_NAME"
print_success "PostgreSQL: $POSTGRES_NAME"
print_success "Redis: $REDIS_NAME"
print_success "Storage: $STORAGE_NAME"
print_success "ACR: ${ACR_LOGIN_SERVER}"
print_success "Key Vault: ${KEYVAULT_URI}"
print_success "Static Web App: supplychain-${ENVIRONMENT}.azurestaticapps.net"
print_success "API Management: supplychain-apim-${ENVIRONMENT}.azure-api.net"

print_status "Next steps:"
print_status "1. Run: ./azure-build-push-containers.sh"
print_status "2. Run: ./azure-deploy-to-aks.sh"
print_status "3. Run: ./validate-arm-deployment.sh"

print_status "🎉 ARM template deployment completed successfully!"
