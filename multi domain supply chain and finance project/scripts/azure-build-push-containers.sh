#!/bin/bash

# Azure Container Build and Push Script for Student Project
# Builds and pushes all containers to Azure Container Registry

set -e

echo "🐳 Building and pushing containers to Azure Container Registry..."

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

# Login to Azure and ACR
print_status "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

print_status "Verifying Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Create optimized Dockerfiles for Azure
print_status "Creating optimized Dockerfiles for Azure..."

# Create multi-stage Dockerfile for auth service
cat > backend/auth-service/Dockerfile.azure << EOF
# Multi-stage build for Azure
FROM maven:3.8.6-openjdk-17-slim AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM openjdk:17-jre-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-Xmx512m", "-Xms256m", "-jar", "app.jar"]
EOF

# Create multi-stage Dockerfile for finance service
cat > backend/finance-service/Dockerfile.azure << EOF
# Multi-stage build for Azure
FROM maven:3.8.6-openjdk-17-slim AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM openjdk:17-jre-slim
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-Xmx1g", "-Xms512m", "-jar", "app.jar"]
EOF

# Create Node.js Dockerfile for blockchain service
cat > backend/blockchain-service/Dockerfile.azure << EOF
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
EOF

# Create Python Dockerfile for AI service
cat > backend/ai-service/Dockerfile.azure << EOF
FROM python:3.9-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
EOF

# Create Node.js Dockerfile for DeFi service
cat > backend/defi-service/Dockerfile.azure << EOF
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
EOF

# Create Node.js Dockerfile for IoT service
cat > backend/iot-service/Dockerfile.azure << EOF
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 8080
CMD ["node", "server.js"]
EOF

# Create optimized React Dockerfile for frontend
cat > frontend/react-app/Dockerfile.azure << EOF
# Multi-stage build for React frontend
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# Create NGINX config for frontend
cat > frontend/react-app/nginx.conf << EOF
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api/ {
        proxy_pass http://api-gateway:80/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # SPA fallback
    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

print_status "Building and pushing auth service..."
docker build -f backend/auth-service/Dockerfile.azure -t $ACR_LOGIN_SERVER/auth-service:latest backend/auth-service/
docker push $ACR_LOGIN_SERVER/auth-service:latest

print_status "Building and pushing finance service..."
docker build -f backend/finance-service/Dockerfile.azure -t $ACR_LOGIN_SERVER/finance-service:latest backend/finance-service/
docker push $ACR_LOGIN_SERVER/finance-service:latest

print_status "Building and pushing blockchain service..."
docker build -f backend/blockchain-service/Dockerfile.azure -t $ACR_LOGIN_SERVER/blockchain-service:latest backend/blockchain-service/
docker push $ACR_LOGIN_SERVER/blockchain-service:latest

print_status "Building and pushing AI service..."
docker build -f backend/ai-service/Dockerfile.azure -t $ACR_LOGIN_SERVER/ai-service:latest backend/ai-service/
docker push $ACR_LOGIN_SERVER/ai-service:latest

print_status "Building and pushing DeFi service..."
docker build -f backend/defi-service/Dockerfile.azure -t $ACR_LOGIN_SERVER/defi-service:latest backend/defi-service/
docker push $ACR_LOGIN_SERVER/defi-service:latest

print_status "Building and pushing IoT service..."
docker build -f backend/iot-service/Dockerfile.azure -t $ACR_LOGIN_SERVER/iot-service:latest backend/iot-service/
docker push $ACR_LOGIN_SERVER/iot-service:latest

print_status "Building and pushing frontend..."
docker build -f frontend/react-app/Dockerfile.azure -t $ACR_LOGIN_SERVER/frontend:latest frontend/react-app/
docker push $ACR_LOGIN_SERVER/frontend:latest

print_status "Building and pushing API gateway..."
docker build -f k8s/Dockerfile.nginx -t $ACR_LOGIN_SERVER/api-gateway:latest k8s/
docker push $ACR_LOGIN_SERVER/api-gateway:latest

# Create Azure Function for AI processing
print_status "Creating Azure Function for AI processing..."
cd backend/ai-service/functions
func init SupplyChainAIFunctions --python
cd SupplyChainAIFunctions
func new --name DemandForecasting --template "HTTP trigger"
func new --name RiskAssessment --template "HTTP trigger"

# Update requirements.txt
cat > requirements.txt << EOF
azure-functions
pandas
numpy
scikit-learn
tensorflow
joblib
flask
EOF

# Update function code
cat > DemandForecasting/__init__.py << EOF
import azure.functions as func
import json
import joblib
import numpy as np

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Load model (would be downloaded from blob storage)
        model = joblib.load('model.pkl')
        data = req.get_json()
        prediction = model.predict([data['features']])
        return func.HttpResponse(json.dumps({'prediction': prediction.tolist()}))
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
EOF

cd ../../..

# Package and deploy function
print_status "Deploying AI Functions to Azure..."
func azure functionapp publish supplychain-ai-functions --python

print_success "All containers built and pushed successfully!"

# Verify images in ACR
print_status "Verifying images in Azure Container Registry..."
az acr repository list --name $ACR_NAME --output table

print_status "Container registry contents:"
az acr manifest list-metadata --name $ACR_NAME --repository auth-service --output table

print_success "=== CONTAINER BUILD AND PUSH COMPLETED ==="
print_success "All services are now available in Azure Container Registry:"
print_success "  - auth-service:latest"
print_success "  - finance-service:latest"
print_success "  - blockchain-service:latest"
print_success "  - ai-service:latest"
print_success "  - defi-service:latest"
print_success "  - iot-service:latest"
print_success "  - frontend:latest"
print_success "  - api-gateway:latest"

print_status "Next step: Run ./azure-deploy-to-aks.sh"

print_status "🎉 Container build and push completed successfully!"
