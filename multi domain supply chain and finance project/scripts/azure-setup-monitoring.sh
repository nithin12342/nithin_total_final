#!/bin/bash

# Azure Monitoring Setup Script for Student Project
# Sets up comprehensive monitoring using Azure Monitor and Application Insights

set -e

echo "📊 Setting up Azure monitoring and logging..."

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

print_status "Configuring Azure Monitor..."

# Enable Azure Monitor for containers
az aks enable-addons \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --addons monitoring \
    --workspace-resource-id $(az monitor log-analytics workspace show \
        --resource-group $RESOURCE_GROUP \
        --workspace-name supplychain-log-analytics \
        --query id -o tsv)

print_success "Azure Monitor for containers enabled"

print_status "Creating custom metrics and alerts..."

# Create alert rules for key metrics
az monitor metrics alert create \
    --name "HighCPUUsage" \
    --resource-group $RESOURCE_GROUP \
    --scopes $(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --query id -o tsv) \
    --condition "avg Percentage CPU > 80" \
    --description "Alert when CPU usage exceeds 80%" \
    --evaluation-frequency 5m \
    --window-size 15m \
    --action supplychain-cost-alerts \
    --severity 2

az monitor metrics alert create \
    --name "HighMemoryUsage" \
    --resource-group $RESOURCE_GROUP \
    --scopes $(az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER_NAME --query id -o tsv) \
    --condition "avg Memory utilization > 85" \
    --description "Alert when memory usage exceeds 85%" \
    --evaluation-frequency 5m \
    --window-size 15m \
    --action supplychain-cost-alerts \
    --severity 2

# Database performance alerts
az monitor metrics alert create \
    --name "HighDatabaseCPU" \
    --resource-group $RESOURCE_GROUP \
    --scopes $(az postgres server show --resource-group $RESOURCE_GROUP --name $POSTGRES_NAME --query id -o tsv) \
    --condition "avg cpu_percent > 70" \
    --description "Alert when database CPU usage exceeds 70%" \
    --evaluation-frequency 5m \
    --window-size 15m \
    --action supplychain-cost-alerts \
    --severity 2

# Redis cache alerts
az monitor metrics alert create \
    --name "RedisMemoryUsage" \
    --resource-group $RESOURCE_GROUP \
    --scopes $(az redis show --resource-group $RESOURCE_GROUP --name $REDIS_NAME --query id -o tsv) \
    --condition "avg usedmemorypercentage > 80" \
    --description "Alert when Redis memory usage exceeds 80%" \
    --evaluation-frequency 5m \
    --window-size 10m \
    --action supplychain-cost-alerts \
    --severity 2

print_status "Setting up Application Insights..."

# Enable Application Insights for all services
APP_INSIGHTS_ID=$(az monitor app-insights component show \
    --resource-group $RESOURCE_GROUP \
    --app supplychain-app-insights \
    --query id -o tsv)

# Update Kubernetes configurations with Application Insights
kubectl set env deployment/auth-service APP_INSIGHTS_ID=$APP_INSIGHTS_ID -n supplychain
kubectl set env deployment/finance-service APP_INSIGHTS_ID=$APP_INSIGHTS_ID -n supplychain
kubectl set env deployment/ai-service APP_INSIGHTS_ID=$APP_INSIGHTS_ID -n supplychain

print_status "Creating Azure Monitor dashboards..."

# Create custom dashboard for supply chain metrics
cat > supplychain-dashboard.json << EOF
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
              "colSpan": 12,
              "rowSpan": 6
            },
            "metadata": {
              "inputs": [
                {
                  "name": "id",
                  "value": "$APP_INSIGHTS_ID"
                },
                {
                  "name": "Version",
                  "value": "1.0"
                }
              ],
              "type": "Extension/Microsoft_Azure_ApplicationInsights/PartType/ApplicationInsightsOverviewBlade"
            }
          },
          "1": {
            "position": {
              "x": 0,
              "y": 6,
              "colSpan": 6,
              "rowSpan": 4
            },
            "metadata": {
              "inputs": [
                {
                  "name": "id",
                  "value": "$APP_INSIGHTS_ID"
                }
              ],
              "type": "Extension/Microsoft_Azure_ApplicationInsights/PartType/RequestBlade"
            }
          },
          "2": {
            "position": {
              "x": 6,
              "y": 6,
              "colSpan": 6,
              "rowSpan": 4
            },
            "metadata": {
              "inputs": [
                {
                  "name": "id",
                  "value": "$APP_INSIGHTS_ID"
                }
              ],
              "type": "Extension/Microsoft_Azure_ApplicationInsights/PartType/PerformanceBlade"
            }
          }
        }
      }
    },
    "metadata": {
      "model": {
        "timeRange": {
          "value": {
            "relative": {
              "duration": 24,
              "timeUnit": 1
            }
          },
          "type": "MsPortalFx.Composition.Configuration.ValueTypes.TimeRange"
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
    --input-path supplychain-dashboard.json \
    --location $LOCATION

print_status "Setting up log analytics queries..."

# Create custom log queries for supply chain insights
cat > log-queries.kql << EOF
// Supply Chain Platform - Key Performance Indicators
AzureActivity
| where Level != "Informational"
| where ResourceProvider == "Microsoft.ContainerService"
| where ActivityStatus == "Started"
| summarize count() by bin(TimeGenerated, 1h), ResourceId

// Service Health Status
Heartbeat
| where Computer contains "supplychain"
| summarize LastHeartbeat=max(TimeGenerated) by Computer, Category
| where LastHeartbeat < ago(10m)

// API Performance
requests
| where timestamp > ago(1h)
| where name contains "api"
| summarize avg(duration), count() by bin(timestamp, 5m), name

// Error Analysis
exceptions
| where timestamp > ago(1h)
| where type contains "supplychain"
| summarize count() by bin(timestamp, 10m), type

// Database Performance
AzureMetrics
| where ResourceProvider == "Microsoft.DBforPostgreSQL"
| where MetricName == "cpu_percent"
| summarize avg(Maximum) by bin(TimeGenerated, 5m), ResourceId

// Cache Performance
AzureMetrics
| where ResourceProvider == "Microsoft.Cache"
| where MetricName == "usedmemorypercentage"
| summarize avg(Maximum) by bin(TimeGenerated, 5m), ResourceId
EOF

print_status "Creating Azure Monitor workbooks..."

# Create workbook for detailed analytics
az monitor workbook create \
    --resource-group $RESOURCE_GROUP \
    --name "Supply Chain Analytics" \
    --definition log-queries.kql \
    --location $LOCATION \
    --display-name "Supply Chain Platform Analytics"

print_status "Setting up Azure Security Center..."

# Enable Azure Security Center (Free tier)
az security setting create \
    --name "MCAS" \
    --tier "Free"

# Enable Azure Defender for servers (Free trial)
az security setting update \
    --name "WDATP" \
    --tier "Free"

print_status "Configuring Azure cost monitoring..."

# Create detailed cost management
az consumption budget create \
    --amount 25 \
    --name "AKSBudget" \
    --resource-group $RESOURCE_GROUP \
    --category Cost \
    --time-grain Monthly \
    --time-period 2025-01-01T00:00:00Z 2025-12-31T23:59:59Z \
    --notification action-group="supplychain-cost-alerts" threshold=50 operator=GreaterThan \
    --notification action-group="supplychain-cost-alerts" threshold=75 operator=GreaterThan \
    --notification action-group="supplychain-cost-alerts" threshold=90 operator=GreaterThan

# Create resource-specific budgets
az consumption budget create \
    --amount 10 \
    --name "DatabaseBudget" \
    --resource-group $RESOURCE_GROUP \
    --category Cost \
    --time-grain Monthly \
    --filter "ResourceId eq $(az postgres server show --resource-group $RESOURCE_GROUP --name $POSTGRES_NAME --query id -o tsv)" \
    --notification action-group="supplychain-cost-alerts" threshold=80 operator=GreaterThan

print_status "Setting up Azure DevOps monitoring..."

# Create Azure DevOps dashboard (if using Azure DevOps)
if command -v az devops &> /dev/null; then
    az devops dashboard create \
        --name "Supply Chain Platform" \
        --project "supplychain-finance-platform" \
        --definition dashboard-widgets.json
fi

print_status "Creating monitoring validation script..."

cat > validate-monitoring.sh << EOF
#!/bin/bash
echo "🔍 Validating Azure monitoring setup..."

# Check Application Insights
APP_INSIGHTS_STATUS=$(az monitor app-insights component show \
    --resource-group $RESOURCE_GROUP \
    --app supplychain-app-insights \
    --query provisioningState -o tsv)

if [ "$APP_INSIGHTS_STATUS" != "Succeeded" ]; then
    echo "❌ Application Insights not ready"
    exit 1
fi

# Check Log Analytics
LOG_STATUS=$(az monitor log-analytics workspace show \
    --resource-group $RESOURCE_GROUP \
    --workspace-name supplychain-log-analytics \
    --query provisioningState -o tsv)

if [ "$LOG_STATUS" != "Succeeded" ]; then
    echo "❌ Log Analytics workspace not ready"
    exit 1
fi

# Check monitoring addon
MONITORING_STATUS=$(az aks addon show \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_CLUSTER_NAME \
    --addon monitoring \
    --query provisioningState -o tsv)

if [ "$MONITORING_STATUS" != "Succeeded" ]; then
    echo "❌ AKS monitoring not enabled"
    exit 1
fi

# Test metrics collection
echo "Testing metrics collection..."
kubectl top nodes || exit 1
kubectl top pods -n supplychain || exit 1

echo "✅ All monitoring components are working!"
EOF

chmod +x validate-monitoring.sh

print_status "Creating cost monitoring dashboard..."

# Create cost management dashboard
az portal dashboard create \
    --resource-group $RESOURCE_GROUP \
    --name "Cost Management Dashboard" \
    --input-path cost-dashboard.json \
    --location $LOCATION

print_status "Setting up automated reports..."

# Create automated cost report
az monitor scheduled-query create \
    --resource-group $RESOURCE_GROUP \
    --name "DailyCostReport" \
    --scopes $(az group show --name $RESOURCE_GROUP --query id -o tsv) \
    --query "AzureActivity | where Level != 'Informational' | where ResourceProvider != '' | summarize count() by ResourceProvider, bin(TimeGenerated, 1d)" \
    --frequency 1d \
    --time-window 1d \
    --action supplychain-cost-alerts

print_success "=== AZURE MONITORING SETUP COMPLETED ==="
print_success "Application Insights: Configured for all services"
print_success "Log Analytics: Collecting logs and metrics"
print_success "Custom Dashboards: Created in Azure Portal"
print_success "Alert Rules: Configured for key metrics"
print_success "Cost Monitoring: Budgets and alerts set up"
print_success "Security Center: Enabled with free tier"

print_status "Next steps:"
print_status "1. Run: ./validate-monitoring.sh"
print_status "2. Access Azure Portal dashboard: Supply Chain Platform Dashboard"
print_status "3. Monitor costs at: Azure Cost Management"

print_status "🎉 Azure monitoring setup completed successfully!"
