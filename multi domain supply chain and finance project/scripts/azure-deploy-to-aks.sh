#!/bin/bash

# Azure Kubernetes Service Deployment Script for Student Project
# Deploys all services to AKS with Azure integrations

set -e

echo "☸️  Deploying Supply Chain Platform to Azure Kubernetes Service..."

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

# Load connection strings
if [ ! -f "azure-connection-strings.txt" ]; then
    print_error "azure-connection-strings.txt not found. Run azure-setup-infrastructure.sh first."
    exit 1
fi

source azure-connection-strings.txt

print_status "Verifying Kubernetes connection..."
if ! kubectl cluster-info > /dev/null 2>&1; then
    print_error "Cannot connect to Kubernetes cluster. Run: az aks get-credentials"
    exit 1
fi

print_status "Creating Azure service principal for AKS..."
AKS_SERVICE_PRINCIPAL=$(az ad sp create-for-rbac \
    --name supplychain-aks-sp \
    --role Contributor \
    --scopes $(az group show --name $RESOURCE_GROUP --query id -o tsv) \
    --query appId -o tsv)

AKS_CLIENT_SECRET=$(az ad sp credential reset \
    --name supplychain-aks-sp \
    --query password -o tsv)

print_status "Creating Kubernetes secrets from Azure Key Vault..."

# Create secret for database connections
kubectl create secret generic azure-secrets \
    --namespace supplychain \
    --from-literal=POSTGRES_CONNECTION="$POSTGRES_CONNECTION_STRING" \
    --from-literal=REDIS_CONNECTION="$REDIS_CONNECTION_STRING" \
    --from-literal=STORAGE_CONNECTION="$STORAGE_CONNECTION_STRING" \
    --from-literal=APP_INSIGHTS_KEY="$APP_INSIGHTS_INSTRUMENTATION_KEY" \
    --dry-run=client -o yaml | kubectl apply -f -

# Create Azure file share persistent volume
print_status "Creating Azure file share persistent volume..."
cat > k8s/azure-file-pvc.yaml << EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: azure-file-share
  namespace: supplychain
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: azurefile
  resources:
    requests:
      storage: 1Gi
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: azurefile
provisioner: kubernetes.io/azure-file
parameters:
  skuName: Standard_LRS
reclaimPolicy: Retain
EOF

kubectl apply -f k8s/azure-file-pvc.yaml

print_status "Creating Azure service bus for messaging..."
az servicebus namespace create \
    --resource-group $RESOURCE_GROUP \
    --name supplychain-servicebus \
    --location $LOCATION \
    --sku Basic

az servicebus queue create \
    --resource-group $RESOURCE_GROUP \
    --namespace-name supplychain-servicebus \
    --name invoice-processing

az servicebus queue create \
    --resource-group $RESOURCE_GROUP \
    --namespace-name supplychain-servicebus \
    --name payment-processing

# Create Kubernetes secrets for service bus
SERVICEBUS_CONNECTION_STRING=$(az servicebus namespace authorization-rule keys list \
    --resource-group $RESOURCE_GROUP \
    --namespace-name supplychain-servicebus \
    --name RootManageSharedAccessKey \
    --query primaryConnectionString -o tsv)

kubectl create secret generic servicebus-secrets \
    --namespace supplychain \
    --from-literal=connection-string="$SERVICEBUS_CONNECTION_STRING" \
    --dry-run=client -o yaml | kubectl apply -f -

print_status "Deploying Azure Monitor and logging..."

# Deploy Azure Monitor for containers
cat > k8s/azure-monitor.yaml << EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: container-azm-ms-agentconfig
  namespace: kube-system
data:
  schema-version: v1
  config-version: ver1
  log-data-collection-settings: |
    {
      "dataSources": {
        "syslog": {
          "facilityNames": [
            "auth",
            "authpriv",
            "cron",
            "daemon",
            "ftp",
            "kern",
            "local0",
            "local1",
            "local2",
            "local3",
            "local4",
            "local5",
            "local6",
            "local7",
            "lpr",
            "mail",
            "news",
            "syslog",
            "user",
            "uucp"
          ],
          "log_levels": [
            "LOG_EMERG",
            "LOG_ALERT",
            "LOG_CRIT",
            "LOG_ERR",
            "LOG_WARNING",
            "LOG_NOTICE",
            "LOG_INFO",
            "LOG_DEBUG"
          ]
        }
      },
      "namespaces": [
        {
          "namespace": "supplychain",
          "dataSources": [
            {
              "type": "syslog",
              "paths": [
                "/var/log/containers/*supplychain*/*.log"
              ]
            }
          ]
        }
      ]
    }
EOF

kubectl apply -f k8s/azure-monitor.yaml

print_status "Deploying services with Azure configurations..."

# Deploy auth service with Azure AD integration
envsubst < k8s/auth-service-azure.yaml | kubectl apply -f -

# Deploy finance service with Azure database
envsubst < k8s/finance-service-azure.yaml | kubectl apply -f -

# Deploy blockchain service with Azure storage
envsubst < k8s/blockchain-service-azure.yaml | kubectl apply -f -

# Deploy AI service with Azure ML integration
envsubst < k8s/ai-service-azure.yaml | kubectl apply -f -

# Deploy DeFi service
envsubst < k8s/defi-service-azure.yaml | kubectl apply -f -

# Deploy IoT service with Azure IoT Hub
envsubst < k8s/iot-service-azure.yaml | kubectl apply -f -

# Deploy frontend
envsubst < k8s/frontend-service-azure.yaml | kubectl apply -f -

# Deploy API Gateway with Azure Front Door
envsubst < k8s/api-gateway-azure.yaml | kubectl apply -f -

print_status "Waiting for all deployments to be ready..."
kubectl wait --for=condition=ready pod --all --namespace supplychain --timeout=600s

print_status "Creating Azure Application Gateway..."

# Create Application Gateway for load balancing
az network application-gateway create \
    --resource-group $RESOURCE_GROUP \
    --name supplychain-app-gateway \
    --location $LOCATION \
    --sku Standard_v2 \
    --capacity 1 \
    --vnet-name supplychain-vnet \
    --subnet supplychain-subnet \
    --http-settings-protocol Http \
    --frontend-port 80 \
    --routing-rule-type Basic \
    --http-settings-port 80

# Create Azure Front Door endpoint
print_status "Creating Azure Front Door endpoint..."
az afd endpoint create \
    --resource-group $RESOURCE_GROUP \
    --profile-name supplychain-cdn \
    --endpoint-name supplychain-frontend \
    --location Global

# Configure Front Door routing
az afd origin-group create \
    --resource-group $RESOURCE_GROUP \
    --profile-name supplychain-cdn \
    --origin-group-name supplychain-origins \
    --load-balancing-sample-size 4 \
    --load-balancing-successful-samples-required 3 \
    --load-balancing-additional-latency-milliseconds 50

# Add origins to Front Door
az afd origin create \
    --resource-group $RESOURCE_GROUP \
    --profile-name supplychain-cdn \
    --endpoint-name supplychain-frontend \
    --origin-group-name supplychain-origins \
    --origin-name supplychain-api \
    --host-name $(kubectl get service api-gateway -n supplychain -o jsonpath='{.status.loadBalancer.ingress[0].ip}').eastus.cloudapp.azure.com \
    --http-port 80 \
    --https-port 443 \
    --origin-host-header $(kubectl get service api-gateway -n supplychain -o jsonpath='{.status.loadBalancer.ingress[0].ip}').eastus.cloudapp.azure.com \
    --priority 1 \
    --weight 1000

print_status "Creating Azure API Management APIs..."

# Import API definitions to Azure API Management
az apim api import \
    --resource-group $RESOURCE_GROUP \
    --service-name supplychain-apim \
    --path supplychain-api \
    --specification-format OpenApi \
    --specification-url https://raw.githubusercontent.com/your-repo/supplychain-platform/main/docs/api-specs/openapi.yaml

# Create products and subscriptions
az apim product create \
    --resource-group $RESOURCE_GROUP \
    --service-name supplychain-apim \
    --product-id supplychain-product \
    --product-name "Supply Chain Finance Platform" \
    --description "APIs for supply chain finance operations"

az apim subscription create \
    --resource-group $RESOURCE_GROUP \
    --service-name supplychain-apim \
    --product-id supplychain-product \
    --subscription-id supplychain-subscription \
    --name "Supply Chain Platform Subscription"

print_status "Setting up Azure DevOps integration..."

# Create Azure DevOps project (if using Azure DevOps)
if command -v az devops &> /dev/null; then
    az devops project create \
        --name "supplychain-finance-platform" \
        --description "Multi-Domain Supply Chain Finance Platform" \
        --visibility private

    # Create build pipeline
    az devops build definition create \
        --name "SupplyChain-CI" \
        --project "supplychain-finance-platform" \
        --repository-type github \
        --repository-url "https://github.com/your-username/supplychain-platform" \
        --branch master \
        --yaml-path azure-pipelines.yml
fi

print_status "Creating Azure Monitor dashboard..."

# Create custom dashboard JSON
cat > dashboard-template.json << EOF
{
  "properties": {
    "lenses": {
      "0": {
        "order": 0,
        "parts": {
          "0": {
            "position": {
              "x": 0,
              "y": 0,
              "colSpan": 6,
              "rowSpan": 4
            },
            "metadata": {
              "inputs": [
                {
                  "name": "id",
                  "value": "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerService/managedClusters/$AKS_NAME"
                }
              ],
              "type": "Extension/Microsoft_Azure_Monitor/PartType/KubernetesGrid"
            }
          }
        }
      }
    }
  }
}
EOF

# Create Azure portal dashboard
az portal dashboard create \
    --resource-group $RESOURCE_GROUP \
    --name "Supply Chain Platform Dashboard" \
    --input-path dashboard-template.json \
    --location $LOCATION

print_status "Configuring auto-scaling based on Azure Monitor metrics..."

# Enable horizontal pod autoscaling
kubectl autoscale deployment auth-service --namespace supplychain --cpu-percent=70 --min=1 --max=3
kubectl autoscale deployment finance-service --namespace supplychain --cpu-percent=80 --min=1 --max=5
kubectl autoscale deployment ai-service --namespace supplychain --cpu-percent=60 --min=1 --max=3
kubectl autoscale deployment frontend-service --namespace supplychain --cpu-percent=70 --min=1 --max=3

print_status "Setting up Azure backup for databases..."

# Configure automated backups for PostgreSQL
az postgres server configuration set \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_NAME \
    --name backup.retention.days \
    --value 7

print_status "Creating Azure cost management budget..."

# Set up cost alerts (very important for students!)
az monitor action-group create \
    --name supplychain-cost-alerts \
    --resource-group $RESOURCE_GROUP \
    --short-name "CostAlert" \
    --email-receiver name="Student" email-address="student@domain.com"

az consumption budget create \
    --amount 50 \
    --name "StudentBudget" \
    --resource-group $RESOURCE_GROUP \
    --category Cost \
    --time-grain Monthly \
    --time-period 2025-01-01T00:00:00Z 2025-12-31T23:59:59Z \
    --notification action-group="supplychain-cost-alerts" threshold=80 operator=GreaterThan

print_status "Getting service endpoints..."

API_GATEWAY_URL="http://$(kubectl get service api-gateway -n supplychain -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
FRONTEND_URL="https://supplychain-frontend.azurestaticapps.net"
APIM_URL="https://supplychain-apim.azure-api.net"

print_status "Creating deployment validation script..."

cat > validate-deployment.sh << EOF
#!/bin/bash
echo "🔍 Validating Azure deployment..."

# Test API Gateway
echo "Testing API Gateway..."
curl -f $API_GATEWAY_URL/health || exit 1

# Test individual services
echo "Testing services..."
curl -f $API_GATEWAY_URL/api/auth/health || exit 1
curl -f $API_GATEWAY_URL/api/finance/health || exit 1
curl -f $API_GATEWAY_URL/api/ai/health || exit 1

# Test database connectivity
echo "Testing database connectivity..."
kubectl run postgres-client --rm -i --restart=Never --image=postgres:13 -- psql "$POSTGRES_CONNECTION_STRING" -c "SELECT 1;" || exit 1

# Test Redis connectivity
echo "Testing Redis connectivity..."
kubectl run redis-client --rm -i --restart=Never --image=redis:6-alpine -- redis-cli -h $REDIS_NAME.redis.cache.windows.net -p 6380 ping || exit 1

echo "✅ All validation tests passed!"
EOF

chmod +x validate-deployment.sh

print_success "=== AZURE KUBERNETES DEPLOYMENT COMPLETED ==="
print_success "API Gateway: $API_GATEWAY_URL"
print_success "Frontend: $FRONTEND_URL"
print_success "API Management: $APIM_URL"
print_success "Resource Group: $RESOURCE_GROUP"
print_success "AKS Cluster: $AKS_NAME"

print_status "Next steps:"
print_status "1. Run: ./validate-deployment.sh"
print_status "2. Run: ./azure-setup-monitoring.sh"
print_status "3. Access your platform at: $FRONTEND_URL"

print_status "🎉 Azure Kubernetes deployment completed successfully!"
