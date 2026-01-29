# Development targets
.PHONY: setup install test lint clean build run

# Development setup
setup:
	@echo "Setting up development environment..."
	npm install
	pip install -r requirements.txt
	docker-compose pull

# Install dependencies
install:
	@echo "Installing dependencies..."
	cd frontend/react-app && npm install
	cd backend/auth-service && mvn install
	cd backend/finance-service && mvn install
	cd backend/supplychain-service && mvn install

# Run tests
test:
	@echo "Running tests..."
	cd frontend/react-app && npm test
	cd backend/auth-service && mvn test
	cd backend/finance-service && mvn test
	cd backend/supplychain-service && mvn test

# Run linting
lint:
	@echo "Running linters..."
	cd frontend/react-app && npm run lint
	cd backend/auth-service && mvn checkstyle:check
	cd backend/finance-service && mvn checkstyle:check
	cd backend/supplychain-service && mvn checkstyle:check

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	cd frontend/react-app && npm run clean
	cd backend/auth-service && mvn clean
	cd backend/finance-service && mvn clean
	cd backend/supplychain-service && mvn clean
	docker-compose down -v

# Build all services
build:
	@echo "Building all services..."
	cd frontend/react-app && npm run build
	cd backend/auth-service && mvn package
	cd backend/finance-service && mvn package
	cd backend/supplychain-service && mvn package
	docker-compose build

# Run the application
run:
	@echo "Starting all services..."
	docker-compose up

# Deploy to development
deploy-dev:
	@echo "Deploying to development..."
	./scripts/deploy.sh dev

# Deploy to production
deploy-prod:
	@echo "Deploying to production..."
	./scripts/deploy.sh prod

# Generate API documentation
docs:
	@echo "Generating API documentation..."
	cd docs/api-docs && npm run generate-docs

# Security checks
security-check:
	@echo "Running security checks..."
	npm audit
	cd backend && mvn dependency-check:check
