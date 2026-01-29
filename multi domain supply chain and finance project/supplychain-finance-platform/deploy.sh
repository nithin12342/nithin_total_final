#!/bin/bash

# Supply Chain Finance Platform - Complete Deployment Script
# This script deploys all components of the platform to production

set -e

echo "🚀 Starting Supply Chain Finance Platform Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check prerequisites
print_status "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { print_error "Docker is required but not installed. Aborting."; exit 1; }
command -v kubectl >/dev/null 2>&1 || { print_error "kubectl is required but not installed. Aborting."; exit 1; }
command -v terraform >/dev/null 2>&1 || { print_error "Terraform is required but not installed. Aborting."; exit 1; }

# Set environment
ENVIRONMENT=${1:-production}
print_status "Deploying to environment: $ENVIRONMENT"

# Create namespace
print_status "Creating Kubernetes namespace..."
kubectl apply -f k8s/namespace-config.yaml

# Deploy infrastructure with Terraform
print_status "Deploying infrastructure with Terraform..."
cd cloud/terraform/environments/$ENVIRONMENT
terraform init
terraform plan
terraform apply -auto-approve
cd ../../..

# Build and push Docker images
print_status "Building and pushing Docker images..."

# Backend services
services=("auth-service" "finance-service" "blockchain-service" "ai-service" "defi-service" "iot-service")
for service in "${services[@]}"; do
    print_status "Building $service..."
    docker build -t supplychain-finance-platform/$service:latest backend/$service/
    docker push supplychain-finance-platform/$service:latest
done

# Frontend
print_status "Building frontend..."
docker build -t supplychain-finance-platform/frontend:latest frontend/react-app/
docker push supplychain-finance-platform/frontend:latest

# Deploy to Kubernetes
print_status "Deploying services to Kubernetes..."

# Deploy backend services
for service in "${services[@]}"; do
    print_status "Deploying $service..."
    kubectl apply -f k8s/$service.yaml
done

# Deploy frontend
print_status "Deploying frontend..."
kubectl apply -f k8s/frontend-service.yaml

# Deploy API Gateway
print_status "Deploying API Gateway..."
kubectl apply -f k8s/api-gateway.yaml

# Wait for deployments to be ready
print_status "Waiting for deployments to be ready..."
kubectl wait --for=condition=ready pod -l app=auth-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=finance-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=blockchain-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=ai-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=defi-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=iot-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=api-gateway --timeout=300s

# Run tests
print_status "Running comprehensive tests..."

# Unit tests
print_status "Running unit tests..."
for service in "${services[@]}"; do
    kubectl run test-$service --image=supplychain-finance-platform/$service:latest --rm -i --restart=Never -- \
        ./mvnw test -Dspring.profiles.active=test
done

# Integration tests
print_status "Running integration tests..."
kubectl run integration-tests --image=supplychain-finance-platform/finance-service:latest --rm -i --restart=Never -- \
    ./mvnw test -Dtest="*IntegrationTest" -Dspring.profiles.active=test

# E2E tests
print_status "Running end-to-end tests..."
kubectl run e2e-tests --image=supplychain-finance-platform/frontend:latest --rm -i --restart=Never -- \
    npm test -- --testPathPattern=e2e

# Performance tests
print_status "Running performance tests..."
kubectl run performance-tests --image=supplychain-finance-platform/ai-service:latest --rm -i --restart=Never -- \
    python tests/performance/performance-tests.py

# Security validation
print_status "Running security validation..."
kubectl run security-tests --image=supplychain-finance-platform/security:latest --rm -i --restart=Never -- \
    python security/pentest-automation/security-scan.py

# Configure monitoring
print_status "Setting up monitoring and logging..."
kubectl apply -f devops/monitoring/prometheus-config.yaml
kubectl apply -f devops/monitoring/grafana-dashboards.yaml
kubectl apply -f devops/logging/elk-stack.yaml

# Setup backups
print_status "Configuring automated backups..."
kubectl apply -f devops/backup/backup-config.yaml

# Get service URLs
print_status "Getting service endpoints..."
API_GATEWAY_URL=$(kubectl get service api-gateway -n supplychain -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
print_success "Platform deployed successfully!"
print_success "API Gateway URL: http://$API_GATEWAY_URL"

# Health check
print_status "Performing final health check..."
sleep 30
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://$API_GATEWAY_URL/health)
if [ "$HEALTH_CHECK" -eq 200 ]; then
    print_success "Health check passed! Platform is ready."
else
    print_warning "Health check failed. Please check logs."
fi

# Display completion summary
print_success "=== DEPLOYMENT COMPLETED ==="
print_success "Environment: $ENVIRONMENT"
print_success "Services deployed: ${#services[@]} backend + frontend + gateway"
print_success "Tests completed: Unit, Integration, E2E, Performance, Security"
print_success "Monitoring configured: Prometheus, Grafana, ELK Stack"
print_success "Access the platform at: http://$API_GATEWAY_URL"

print_status "Deployment script completed successfully! 🎉"
