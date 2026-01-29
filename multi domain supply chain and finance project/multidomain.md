# Azure Deployment Guide for Multi-Domain Platform (Free Tier)

This guide provides a step-by-step procedure for deploying a scaled-down, developer-focused version of the application to an Azure for Students account, aiming to stay within the free tier limits.

**Disclaimer:** This method makes significant compromises and is **not suitable for production**. It consolidates services into a single instance and runs some databases as containers, sacrificing the high-availability and scalability of the original Kubernetes-based architecture.

---

### Prerequisites

1.  **Azure for Students Account:** Must be active.
2.  **Azure CLI:** Installed and logged in (`az login`).
3.  **Docker Desktop:** Installed and running.
4.  **Docker Hub Account:** A free account to store your container images.
5.  **Git:** A GitHub repository (or other Git provider) containing your project code.

---

### Step 1: Create a Modified `docker-compose.azure.yml`

This modified Docker Compose file is optimized for a single-instance deployment on Azure App Service. It removes the PostgreSQL service (to be replaced by Azure's offering) and non-essential monitoring tools.

1.  In the `supplychain-finance-platform` directory, create a new file named `docker-compose.azure.yml`.
2.  Copy the following content into the file. You will update the `YOUR_DOCKERHUB_USERNAME` placeholders later.

```yaml
version: '3.8'

services:
  # Frontend Service (This will be the main entrypoint)
  web-app:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-web-app # <-- UPDATE THIS
    ports:
      - "80:3000" # Maps internal port 3000 to the standard HTTP port 80
    environment:
      - API_URL=http://api-gateway:8080
    depends_on:
      - api-gateway

  # Backend Services
  api-gateway:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-api-gateway # <-- UPDATE THIS
    depends_on:
      - auth-service
      - finance-service
      - supplychain-service

  auth-service:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-auth-service # <-- UPDATE THIS
    environment:
      # These will be set in the App Service Configuration
      - DB_HOST=${DB_HOST}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - REDIS_HOST=redis
    depends_on:
      - redis

  finance-service:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-finance-service # <-- UPDATE THIS
    environment:
      - DB_HOST=${DB_HOST}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    depends_on:
      - mongodb

  supplychain-service:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-supplychain-service # <-- UPDATE THIS
    environment:
      - DB_HOST=${DB_HOST}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
    depends_on:
      - mongodb
      
  blockchain-service:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-blockchain-service # <-- UPDATE THIS

  ai-analytics:
    image: YOUR_DOCKERHUB_USERNAME/supplychain-ai-analytics # <-- UPDATE THIS
    volumes:
      - ./ai-ml/models:/app/models

  # Databases (running as containers)
  mongodb:
    image: mongo:5
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:6
    volumes:
      - redis_data:/data

volumes:
  mongo_data:
  redis_data:
```

---

### Step 2: Build and Push Container Images to Docker Hub

Each service defined in the compose file must be built and pushed to your personal Docker Hub repository.

1.  **Login to Docker Hub** via the terminal:
    ```shell
    docker login
    ```

2.  **For each service**, run `docker build` and `docker push`. **Image names must be lowercase**.

    ```shell
    # Example for web-app service
    docker build -t your_dockerhub_username/supplychain-web-app ./supplychain-finance-platform/frontend/react-app
    docker push your_dockerhub_username/supplychain-web-app

    # Example for api-gateway service
    docker build -t your_dockerhub_username/supplychain-api-gateway ./supplychain-finance-platform/backend/gateway
    docker push your_dockerhub_username/supplychain-api-gateway

    # --- Repeat this process for all services listed in docker-compose.azure.yml ---
    # auth-service, finance-service, supplychain-service, blockchain-service, ai-analytics
    ```

---

### Step 3: Deploy Infrastructure on Azure via CLI

These commands provision the necessary Azure resources.

1.  **Set up PowerShell variables** for your deployment:
    ```powershell
    $RESOURCE_GROUP="my-scf-project-rg"
    $LOCATION="eastus"
    $APP_SERVICE_PLAN="my-scf-free-plan"
    $WEBAPP_NAME="my-supplychain-webapp-$(Get-Random)"
    $POSTGRES_SERVER_NAME="my-scf-postgres-server-$(Get-Random)"
    $POSTGRES_DB_NAME="supplychain_db"
    $POSTGRES_ADMIN_USER="demoadmin"
    $POSTGRES_ADMIN_PASSWORD="MyPa$$w0rd123" # CHANGE THIS to a strong password
    $GITHUB_REPO_URL="https://github.com/your-username/your-repo.git" # <-- UPDATE THIS
    ```

2.  **Create a Resource Group:**
    ```shell
    az group create --name $RESOURCE_GROUP --location $LOCATION
    ```

3.  **Create a Free-Tier PostgreSQL Server:**
    This uses the `B_B1ms` SKU, which includes a free monthly allowance for 12 months.
    ```shell
    az postgres flexible-server create --resource-group $RESOURCE_GROUP --name $POSTGRES_SERVER_NAME --location $LOCATION --admin-user $POSTGRES_ADMIN_USER --admin-password $POSTGRES_ADMIN_PASSWORD --sku-name B_B1ms --tier Burstable --storage-size 32 --version 14
    ```

4.  **Create the database within the server:**
    ```shell
    az postgres flexible-server db create --resource-group $RESOURCE_GROUP --server-name $POSTGRES_SERVER_NAME --database-name $POSTGRES_DB_NAME
    ```

5.  **Configure Firewall to Allow Access from Azure Services:**
    ```shell
    az postgres flexible-server firewall-rule create --resource-group $RESOURCE_GROUP --name $POSTGRES_SERVER_NAME --rule-name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
    ```

6.  **Create a Free-Tier App Service Plan (F1 SKU):**
    ```shell
    az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku F1 --is-linux
    ```

7.  **Create the Web App for Containers:**
    This command creates the App Service, points it to your `docker-compose.azure.yml` in GitHub, and configures it to use your Docker Hub credentials.
    ```shell
    az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEBAPP_NAME --multicontainer-config-type COMPOSE --multicontainer-config-file "supplychain-finance-platform/docker-compose.azure.yml" --repo $GITHUB_REPO_URL --branch main --docker-registry-server-user "your_dockerhub_username" --docker-registry-server-password "your_dockerhub_password"
    ```
    
8.  **Set Database Environment Variables in App Service:**
    Injects the database credentials into the App Service, making them available to your containers.
    ```shell
    az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME --settings "DB_HOST=$POSTGRES_SERVER_NAME.postgres.database.azure.com" "DB_NAME=$POSTGRES_DB_NAME" "DB_USER=$POSTGRES_ADMIN_USER@$POSTGRES_SERVER_NAME" "DB_PASSWORD=$POSTGRES_ADMIN_PASSWORD"
    ```
    
---

### Step 4: Verification

Deployment and container startup can take **10-15 minutes**.

1.  **Monitor Logs:** Check the container startup progress in the Azure Portal. Navigate to your Web App resource and select "Log stream".
2.  **Access Application:** Once the logs indicate that the services have started successfully, browse to your application's URL: `http://<YOUR_WEBAPP_NAME>.azurewebsites.net`.
