# DEPRECATED FILE - INFORMATION CONSOLIDATED
#
# This file has been consolidated into the main project README.md
# Please refer to: /README.md for all project information
#
# This Azure deployment strategy is now documented in the "Azure Deployment" section
# of the main README.md file.
#
# File deprecated as of: October 23, 2025
# Reason: Documentation consolidation for better organization

DEPRECATED - USE MAIN README.md INSTEAD

This deployment strategy is specifically designed for **Azure Student accounts** leveraging:
- ✅ **Azure for Students** free credits ($100/month for 12 months)
- ✅ **Azure Free Tier** services
- ✅ **GitHub Student Developer Pack** benefits
- ✅ **Educational pricing** and extended free tiers

---

## **💰 Cost Optimization Strategy**

### **Free Tier Services Used**
- **Azure Container Instances** (Free tier: 1M vCPU-seconds, 3.5 GB-seconds/month)
- **Azure Kubernetes Service** (Free tier: 2 vCPUs)
- **Azure Database for PostgreSQL** (Free tier: 250GB Basic Single Server)
- **Azure Cache for Redis** (Free tier: 250MB Basic Cache)
- **Azure Storage Account** (Free tier: 5GB LRS Hot Block Blob)
- **Azure App Service** (Free tier: 10 web apps)
- **Azure Functions** (Free tier: 1M requests/month)
- **Azure Monitor** (Free tier: 5GB logs, 1GB metrics)

### **Monthly Cost Estimate: $0 (Within Free Tiers)**
- **AKS**: 2 vCPUs (Free)
- **PostgreSQL**: Basic Single Server (Free)
- **Redis Cache**: 250MB Basic (Free)
- **Storage**: 5GB (Free)
- **App Service**: 1 Web App (Free)

---

## **🏗️ Azure Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    Azure Cloud                          │
├─────────────────────────────────────────────────────────┤
│  🌐 Azure Front Door (CDN)                              │
├─────────────────────────────────────────────────────────┤
│  🚀 Azure Kubernetes Service (AKS)                     │
│  ├─ Frontend (React) ────┐                              │
│  ├─ API Gateway (NGINX)  │                              │
│  ├─ Auth Service         │  Microservices              │
│  ├─ Finance Service      │                              │
│  ├─ Blockchain Service   │                              │
│  ├─ AI Service           │                              │
│  ├─ DeFi Service         │                              │
│  └─ IoT Service          │                              │
├─────────────────────────────────────────────────────────┤
│  🗄️  Azure Database Services                           │
│  ├─ PostgreSQL (Relational)                             │
│  ├─ Cosmos DB (NoSQL)                                   │
│  └─ Redis Cache (Caching)                               │
├─────────────────────────────────────────────────────────┤
│  🔒 Security & Identity                                 │
│  ├─ Azure AD B2C (Authentication)                      │
│  ├─ Azure Key Vault (Secrets)                          │
│  └─ Azure Security Center (Free)                       │
├─────────────────────────────────────────────────────────┤
│  📊 Monitoring & Logging                                │
│  ├─ Azure Monitor (Free tier)                          │
│  ├─ Application Insights (Free)                        │
│  └─ Log Analytics (5GB free)                           │
└─────────────────────────────────────────────────────────┘
```

---

## **📋 Prerequisites**

### **Azure Account Setup**
1. **Azure for Students** account (Free $100/month for 12 months)
2. **GitHub Student Developer Pack** activated
3. **Azure CLI** installed locally
4. **kubectl** configured for AKS
5. **Docker** installed for container builds

### **Required Azure Services**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set student subscription
az account set --subscription "Azure for Students"

# Create resource group
az group create --name supplychain-rg --location eastus
```

---

## **🚀 Deployment Steps**

### **Step 1: Infrastructure Setup**

#### **1.1 Create Azure Resources**
```bash
# Create resource group
az group create \
  --name supplychain-student-rg \
  --location eastus \
  --tags environment=student project=supplychain-finance

# Create Azure Container Registry (Free tier)
az acr create \
  --resource-group supplychain-student-rg \
  --name supplychainstudent \
  --sku Basic \
  --admin-enabled true

# Get ACR credentials
ACR_USERNAME=$(az acr credential show \
  --resource-group supplychain-student-rg \
  --name supplychainstudent \
  --query username -o tsv)

ACR_PASSWORD=$(az acr credential show \
  --resource-group supplychain-student-rg \
  --name supplychainstudent \
  --query passwords[0].value -o tsv)
```

#### **1.2 Database Setup**
```bash
# Create PostgreSQL server (Free tier)
az postgres server create \
  --resource-group supplychain-student-rg \
  --name supplychain-postgres \
  --location eastus \
  --admin-user adminuser \
  --admin-password SecureP@ssw0rd123 \
  --sku-name B_Gen5_1 \
  --storage-size 5120

# Create database
az postgres db create \
  --resource-group supplychain-student-rg \
  --server-name supplychain-postgres \
  --name supplychaindb

# Create Redis Cache (Free tier)
az redis create \
  --resource-group supplychain-student-rg \
  --name supplychain-redis \
  --location eastus \
  --sku Basic \
  --size C0
```

#### **1.3 Storage Setup**
```bash
# Create storage account (Free tier)
az storage account create \
  --resource-group supplychain-student-rg \
  --name supplychainstorage \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2

# Create blob container for static assets
az storage container create \
  --name static-assets \
  --account-name supplychainstorage \
  --public-access blob

# Upload frontend assets
az storage blob upload-batch \
  --source frontend/react-app/build \
  --destination static-assets \
  --account-name supplychainstorage
```

### **Step 2: Azure Kubernetes Service**

#### **2.1 Create AKS Cluster (Free tier)**
```bash
# Create AKS cluster with 2 vCPUs (Free tier)
az aks create \
  --resource-group supplychain-student-rg \
  --name supplychain-aks \
  --node-count 1 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --generate-ssh-keys \
  --tags environment=student project=supplychain-finance

# Get cluster credentials
az aks get-credentials \
  --resource-group supplychain-student-rg \
  --name supplychain-aks

# Create namespace
kubectl create namespace supplychain
```

#### **2.2 Deploy Azure Services Integration**
```yaml
# azure-integration.yaml
apiVersion: v1
kind: Secret
metadata:
  name: azure-secrets
  namespace: supplychain
type: Opaque
data:
  POSTGRES_CONNECTION: $(echo -n "postgresql://adminuser:SecureP@ssw0rd123@supplychain-postgres.postgres.database.azure.com:5432/supplychaindb" | base64)
  REDIS_CONNECTION: $(echo -n "supplychain-redis.redis.cache.windows.net:6380,password=SecureP@ssw0rd123,ssl=True,abortConnect=False" | base64)
  STORAGE_CONNECTION: $(echo -n "DefaultEndpointsProtocol=https;AccountName=supplychainstorage;AccountKey=your-storage-key;EndpointSuffix=core.windows.net" | base64)
```

### **Step 3: Container Deployment**

#### **3.1 Build and Push Images**
```bash
# Login to ACR
az acr login --name supplychainstudent

# Build and push auth service
docker build -t supplychainstudent.azurecr.io/auth-service:latest backend/auth-service/
docker push supplychainstudent.azurecr.io/auth-service:latest

# Build and push other services
services=("finance-service" "blockchain-service" "ai-service" "defi-service" "iot-service")
for service in "${services[@]}"; do
    docker build -t supplychainstudent.azurecr.io/$service:latest backend/$service/
    docker push supplychainstudent.azurecr.io/$service:latest
done

# Build and push frontend
docker build -t supplychainstudent.azurecr.io/frontend:latest frontend/react-app/
docker push supplychainstudent.azurecr.io/frontend:latest
```

#### **3.2 Deploy to AKS**
```bash
# Deploy all services
kubectl apply -f k8s/namespace-config.yaml
kubectl apply -f k8s/auth-service.yaml
kubectl apply -f k8s/finance-service.yaml
kubectl apply -f k8s/blockchain-service.yaml
kubectl apply -f k8s/ai-service.yaml
kubectl apply -f k8s/defi-service.yaml
kubectl apply -f k8s/iot-service.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/api-gateway.yaml

# Wait for deployments
kubectl wait --for=condition=ready pod --all --timeout=600s
```

### **Step 4: Azure App Service (Alternative)**

#### **4.1 App Service Deployment**
```bash
# Create App Service Plan (Free tier)
az appservice plan create \
  --name supplychain-plan \
  --resource-group supplychain-student-rg \
  --location eastus \
  --sku FREE

# Create web apps for each service
services=("auth-service" "finance-service" "blockchain-service" "ai-service")
for service in "${services[@]}"; do
    az webapp create \
      --resource-group supplychain-student-rg \
      --plan supplychain-plan \
      --name supplychain-$service \
      --runtime "JAVA|11-java11" \
      --deployment-container-image-name supplychainstudent.azurecr.io/$service:latest
done

# Deploy frontend to static web app (Free)
az staticwebapp create \
  --name supplychain-frontend \
  --resource-group supplychain-student-rg \
  --location eastus \
  --app-location "frontend/react-app" \
  --api-location "api" \
  --output-location "build" \
  --token $GITHUB_TOKEN
```

### **Step 5: Azure Functions for Serverless**

#### **5.1 Deploy AI Processing Functions**
```bash
# Create function app (Free tier)
az functionapp create \
  --resource-group supplychain-student-rg \
  --name supplychain-ai-functions \
  --storage-account supplychainstorage \
  --plan supplychain-plan \
  --runtime python \
  --runtime-version 3.9 \
  --functions-version 4

# Deploy AI functions
func azure functionapp publish supplychain-ai-functions \
  --python
```

---

## **📊 Monitoring & Management**

### **Application Insights (Free)**
```bash
# Enable Application Insights
az monitor app-insights component create \
  --app supplychain-app-insights \
  --resource-group supplychain-student-rg \
  --location eastus \
  --kind web

# Add monitoring to services
# Add to each service configuration
APPLICATION_INSIGHTS_IKEY=your-instrumentation-key
```

### **Azure Monitor Dashboard**
```bash
# Create custom dashboard
az portal dashboard create \
  --resource-group supplychain-student-rg \
  --name "Supply Chain Platform Dashboard" \
  --input-path dashboard-template.json \
  --location eastus
```

---

## **🔒 Security Configuration**

### **Azure AD Integration**
```bash
# Create Azure AD application
az ad app create \
  --display-name "Supply Chain Platform" \
  --identifier-uris "https://supplychain-student.com" \
  --app-roles @manifest.json

# Configure authentication
az ad app update \
  --id app-id \
  --set groupMembershipClaims=All
```

### **Azure Key Vault**
```bash
# Create Key Vault
az keyvault create \
  --name supplychain-keyvault \
  --resource-group supplychain-student-rg \
  --location eastus \
  --enabled-for-deployment true \
  --enabled-for-disk-encryption true \
  --enabled-for-template-deployment true

# Store secrets
az keyvault secret set \
  --vault-name supplychain-keyvault \
  --name "postgres-password" \
  --value "SecureP@ssw0rd123"

az keyvault secret set \
  --vault-name supplychain-keyvault \
  --name "redis-password" \
  --value "SecureP@ssw0rd123"
```

---

## **🚀 Deployment Scripts**

### **Complete Deployment Script**
```bash
#!/bin/bash
# deploy-to-azure-student.sh

set -e

echo "🚀 Deploying Supply Chain Platform to Azure Student..."

# Variables
RESOURCE_GROUP="supplychain-student-rg"
LOCATION="eastus"
ACR_NAME="supplychainstudent"

# Login and set subscription
az login
az account set --subscription "Azure for Students"

# Create infrastructure
echo "📦 Creating infrastructure..."
./scripts/azure-setup-infrastructure.sh

# Build and push containers
echo "🐳 Building and pushing containers..."
./scripts/azure-build-push-containers.sh

# Deploy to AKS
echo "☸️  Deploying to Kubernetes..."
./scripts/azure-deploy-to-aks.sh

# Configure monitoring
echo "📊 Setting up monitoring..."
./scripts/azure-setup-monitoring.sh

# Final validation
echo "✅ Validating deployment..."
./scripts/azure-validate-deployment.sh

echo "🎉 Deployment completed successfully!"
echo "Frontend URL: https://supplychain-frontend.azurestaticapps.net"
echo "API Gateway: http://supplychain-api-gateway.eastus.cloudapp.azure.com"
```

---

## **💰 Cost Monitoring**

### **Azure Cost Management**
```bash
# Set up cost alerts (Free)
az monitor action-group create \
  --name supplychain-cost-alerts \
  --resource-group supplychain-student-rg \
  --short-name "CostAlert" \
  --email-receiver name="Student" email-address="student@domain.com"

# Create budget
az consumption budget create \
  --amount 50 \
  --name "StudentBudget" \
  --resource-group supplychain-student-rg \
  --category Cost \
  --time-grain Monthly \
  --time-period 2025-01-01T00:00:00Z 2025-12-31T23:59:59Z \
  --notification action-group="supplychain-cost-alerts" threshold=80 operator=GreaterThan
```

---

## **📚 Learning Objectives**

### **Azure Services Demonstrated**
- ✅ **Container Services** - AKS, ACR, ACI
- ✅ **Database Services** - PostgreSQL, Redis, Cosmos DB
- ✅ **Compute Services** - App Service, Functions
- ✅ **Storage Services** - Blob Storage, File Storage
- ✅ **Networking** - Load Balancer, Application Gateway
- ✅ **Security** - Key Vault, Azure AD, Security Center
- ✅ **Monitoring** - Application Insights, Log Analytics
- ✅ **DevOps** - Azure DevOps, GitHub Actions integration

### **Architecture Patterns**
- ✅ **Microservices Architecture** on Azure
- ✅ **Serverless Computing** with Azure Functions
- ✅ **Container Orchestration** with Kubernetes
- ✅ **Event-Driven Architecture** with Azure Service Bus
- ✅ **API Management** with Azure API Management (Free tier)

---

## **🔧 Management & Operations**

### **Daily Operations**
```bash
# Check cluster status
az aks show --resource-group supplychain-student-rg --name supplychain-aks

# View logs
az monitor log-analytics query \
  --workspace-name supplychain-log-analytics \
  --analytics-query "AzureActivity | where Level == 'Error'"

# Scale services (within free tier)
kubectl scale deployment auth-service --replicas=2
```

### **Backup Strategy**
```bash
# Automated backups (Free with Azure PostgreSQL)
az postgres server configuration set \
  --resource-group supplychain-student-rg \
  --server-name supplychain-postgres \
  --name backup.retention.days \
  --value 7

# Storage account backup
az backup vault create \
  --resource-group supplychain-student-rg \
  --name supplychain-backup-vault \
  --location eastus
```

---

## **🎓 Educational Value**

### **Skills Demonstrated**
1. **Cloud Architecture** - Multi-tier Azure deployment
2. **DevOps Practices** - CI/CD with Azure DevOps
3. **Container Orchestration** - Kubernetes on Azure
4. **Database Management** - Azure Database services
5. **Security Implementation** - Azure security best practices
6. **Monitoring & Observability** - Azure Monitor integration
7. **Cost Management** - Azure billing and cost optimization

### **Portfolio Value**
- ✅ **Real-world Azure deployment** experience
- ✅ **Enterprise architecture** implementation
- ✅ **Multi-domain technology** integration
- ✅ **Production-ready** configurations
- ✅ **Cost-effective** cloud solutions

---

## **🚀 Quick Start**

```bash
# 1. Setup Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Login to Azure
az login

# 3. Run complete deployment
chmod +x deploy-to-azure-student.sh
./deploy-to-azure-student.sh

# 4. Access your platform
echo "Frontend: https://supplychain-frontend.azurestaticapps.net"
echo "API: http://supplychain-api-gateway.eastus.cloudapp.azure.com"
```

---

## **💡 Tips for Students**

1. **Use Azure Free Services** - Stay within free tiers
2. **Monitor Costs** - Set up billing alerts early
3. **Document Everything** - Great for portfolio
4. **Use GitHub Integration** - Automated deployments
5. **Explore Azure Learn** - Free learning modules
6. **Join Azure Community** - Student forums and support

---

**🎓 Perfect for Azure Student Portfolio Project!**
