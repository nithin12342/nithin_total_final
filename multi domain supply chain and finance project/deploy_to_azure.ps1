# ==============================================================================
# Azure Deployment Script for Multi-Domain Supply Chain Platform
# ==============================================================================
#
# This script automates the deployment to an Azure for Students account.
#
# PRE-REQUISITES:
# 1. Azure CLI installed and you are logged in (`az login`).
# 2. Docker Desktop installed and running.
# 3. You have updated the placeholder values in the "USER-CONFIGURABLE VARIABLES" section below.
#
# HOW TO RUN:
# 1. Open a PowerShell terminal.
# 2. Navigate to the project root directory.
# 3. Run the script: .\deploy_to_azure.ps1
#
# ==============================================================================

# --- USER-CONFIGURABLE VARIABLES (MUST BE EDITED BY THE USER) ---

$DOCKERHUB_USERNAME="your_dockerhub_username"  # <-- IMPORTANT: SET YOUR DOCKER HUB USERNAME
$DOCKERHUB_PASSWORD="your_dockerhub_password"  # <-- IMPORTANT: SET YOUR DOCKER HUB PASSWORD OR AN ACCESS TOKEN
$GITHUB_REPO_URL="https://github.com/your-username/your-repo.git" # <-- IMPORTANT: SET YOUR GITHUB REPO URL

# --- AZURE RESOURCE VARIABLES ---

$RESOURCE_GROUP="my-scf-project-rg"
$LOCATION="eastus"
$APP_SERVICE_PLAN="my-scf-free-plan"
$WEBAPP_NAME="my-supplychain-webapp-$(Get-Random)"
$POSTGRES_SERVER_NAME="my-scf-postgres-server-$(Get-Random)"
$POSTGRES_DB_NAME="supplychain_db"
$POSTGRES_ADMIN_USER="demoadmin"
$POSTGRES_ADMIN_PASSWORD="MyPa$$w0rd123!" # You can change this to a strong password

# ==============================================================================
# --- SCRIPT EXECUTION ---
# ==============================================================================

Write-Host "Starting Azure Deployment..." -ForegroundColor Green

# --- Step 1: Build and Push Docker Images ---
Write-Host "Step 1: Building and pushing Docker images to Docker Hub..." -ForegroundColor Cyan

# Login to Docker Hub
docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_PASSWORD
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker login failed. Please check your credentials." -ForegroundColor Red
    exit 1
}

# Define services to build
$services = @{
    "supplychain-web-app"           = "./supplychain-finance-platform/frontend/react-app";
    "supplychain-api-gateway"       = "./supplychain-finance-platform/backend/gateway";
    "supplychain-auth-service"      = "./supplychain-finance-platform/backend/auth-service";
    "supplychain-finance-service"   = "./supplychain-finance-platform/backend/finance-service";
    "supplychain-supplychain-service" = "./supplychain-finance-platform/backend/supplychain-service";
    "supplychain-blockchain-service"= "./supplychain-finance-platform/backend/blockchain-service";
    "supplychain-ai-analytics"      = "./supplychain-finance-platform/backend/ai-analytics-service";
}

foreach ($service in $services.GetEnumerator()) {
    $imageName = "$DOCKERHUB_USERNAME/$($service.Name)"
    $buildContext = $service.Value
    
    Write-Host "Building $($imageName)..." -ForegroundColor Yellow
    docker build -t $imageName $buildContext
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed for $($imageName)." -ForegroundColor Red
        exit 1
    }

    Write-Host "Pushing $($imageName)..." -ForegroundColor Yellow
    docker push $imageName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker push failed for $($imageName)." -ForegroundColor Red
        exit 1
    }
}

Write-Host "All Docker images pushed successfully." -ForegroundColor Green


# --- Step 2: Deploy Azure Infrastructure ---
Write-Host "Step 2: Deploying Azure infrastructure..." -ForegroundColor Cyan

# Create Resource Group
Write-Host "Creating resource group: $RESOURCE_GROUP..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Free-Tier PostgreSQL Server
Write-Host "Creating PostgreSQL server: $POSTGRES_SERVER_NAME (This may take several minutes)..." -ForegroundColor Yellow
az postgres flexible-server create --resource-group $RESOURCE_GROUP --name $POSTGRES_SERVER_NAME --location $LOCATION --admin-user $POSTGRES_ADMIN_USER --admin-password $POSTGRES_ADMIN_PASSWORD --sku-name B_B1ms --tier Burstable --storage-size 32 --version 14

# Create PostgreSQL Database
Write-Host "Creating database: $POSTGRES_DB_NAME..." -ForegroundColor Yellow
az postgres flexible-server db create --resource-group $RESOURCE_GROUP --server-name $POSTGRES_SERVER_NAME --database-name $POSTGRES_DB_NAME

# Configure PostgreSQL Firewall
Write-Host "Configuring PostgreSQL firewall..." -ForegroundColor Yellow
az postgres flexible-server firewall-rule create --resource-group $RESOURCE_GROUP --name $POSTGRES_SERVER_NAME --rule-name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# Create Free-Tier App Service Plan
Write-Host "Creating App Service Plan: $APP_SERVICE_PLAN..." -ForegroundColor Yellow
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku F1 --is-linux

# Create Web App for Containers
Write-Host "Creating Web App: $WEBAPP_NAME (This may take a few minutes)..." -ForegroundColor Yellow
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEBAPP_NAME --multicontainer-config-type COMPOSE --multicontainer-config-file "supplychain-finance-platform/docker-compose.azure.yml" --repo $GITHUB_REPO_URL --branch main --docker-registry-server-user $DOCKERHUB_USERNAME --docker-registry-server-password $DOCKERHUB_PASSWORD

# Set App Service Environment Variables for Database Connection
Write-Host "Setting database environment variables for the Web App..." -ForegroundColor Yellow
$dbHost = "$POSTGRES_SERVER_NAME.postgres.database.azure.com"
$dbUser = "$POSTGRES_ADMIN_USER@$POSTGRES_SERVER_NAME"
az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME --settings "DB_HOST=$dbHost" "DB_NAME=$POSTGRES_DB_NAME" "DB_USER=$dbUser" "DB_PASSWORD=$POSTGRES_ADMIN_PASSWORD"


# --- Step 3: Deployment Complete ---
Write-Host "Deployment script finished!" -ForegroundColor Green
Write-Host "Your application is being deployed and will be available shortly."
Write-Host "You can monitor the startup logs in the Azure Portal."
$appUrl = "http://$WEBAPP_NAME.azurewebsites.net"
Write-Host "Application URL: $appUrl" -ForegroundColor Cyan
