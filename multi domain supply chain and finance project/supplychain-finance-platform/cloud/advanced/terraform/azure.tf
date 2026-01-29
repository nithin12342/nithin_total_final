# Azure Provider Configuration and Resources

provider "azurerm" {
  features {}
  
  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
}

# Azure Locals
locals {
  azure_name_prefix = "${var.project_name}-${var.environment}-azure"
  azure_common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Provider    = "Azure"
  }
}

# Azure Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.azure_resource_group_name
  location = var.azure_region

  tags = local.azure_common_tags
}

# Azure Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${local.azure_name_prefix}-vnet"
  address_space       = ["10.1.0.0/16"]
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  tags = local.azure_common_tags
}

# Azure Subnets
resource "azurerm_subnet" "public" {
  name                 = "${local.azure_name_prefix}-public-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.1.1.0/24"]
}

resource "azurerm_subnet" "private" {
  name                 = "${local.azure_name_prefix}-private-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.1.2.0/24"]
}

# Azure Network Security Groups
resource "azurerm_network_security_group" "web" {
  name                = "${local.azure_name_prefix}-web-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "HTTP"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "HTTPS"
    priority                   = 101
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = local.azure_common_tags
}

resource "azurerm_network_security_group" "app" {
  name                = "${local.azure_name_prefix}-app-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "AppPort"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = local.azure_common_tags
}

resource "azurerm_network_security_group" "db" {
  name                = "${local.azure_name_prefix}-db-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "PostgreSQL"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "5432"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = local.azure_common_tags
}

# Azure Network Security Group Associations
resource "azurerm_subnet_network_security_group_association" "public" {
  subnet_id                 = azurerm_subnet.public.id
  network_security_group_id = azurerm_network_security_group.web.id
}

resource "azurerm_subnet_network_security_group_association" "private" {
  subnet_id                 = azurerm_subnet.private.id
  network_security_group_id = azurerm_network_security_group.app.id
}

# Azure AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${local.azure_name_prefix}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${local.azure_name_prefix}-aks"

  default_node_pool {
    name       = "default"
    node_count = var.node_count[var.environment]
    vm_size    = var.instance_types[var.environment]
  }

  identity {
    type = "SystemAssigned"
  }

  tags = local.azure_common_tags
}

# Azure PostgreSQL Database
resource "azurerm_postgresql_server" "main" {
  name                = "${local.azure_name_prefix}-postgres"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  sku_name = var.environment == "prod" ? "GP_Gen5_4" : "B_Gen5_1"

  storage_mb                   = var.environment == "prod" ? 102400 : 5120
  backup_retention_days        = 7
  geo_redundant_backup_enabled = false
  auto_grow_enabled            = true

  administrator_login          = "postgres"
  administrator_login_password = random_password.db_password.result
  version                      = "11"
  ssl_enforcement_enabled      = true

  tags = local.azure_common_tags
}

resource "azurerm_postgresql_database" "main" {
  name                = "supplychain"
  resource_group_name = azurerm_resource_group.main.name
  server_name         = azurerm_postgresql_server.main.name
  charset             = "UTF8"
  collation           = "English_United States.1252"
}

# Azure Redis Cache
resource "azurerm_redis_cache" "main" {
  name                = "${local.azure_name_prefix}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name

  capacity = var.environment == "prod" ? 2 : 0
  family   = "C"
  sku_name = var.environment == "prod" ? "Standard" : "Basic"
  enable_non_ssl_port = false

  redis_configuration {
    maxmemory_reserved = 2
    maxmemory_delta    = 2
    maxmemory_policy   = "allkeys-lru"
  }

  tags = local.azure_common_tags
}

# Azure Load Balancer
resource "azurerm_public_ip" "main" {
  name                = "${local.azure_name_prefix}-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"

  tags = local.azure_common_tags
}

resource "azurerm_lb" "main" {
  name                = "${local.azure_name_prefix}-lb"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.main.id
  }

  tags = local.azure_common_tags
}

resource "azurerm_lb_backend_address_pool" "main" {
  resource_group_name = azurerm_resource_group.main.name
  loadbalancer_id     = azurerm_lb.main.id
  name                = "${local.azure_name_prefix}-backend"
}

resource "azurerm_lb_probe" "main" {
  resource_group_name = azurerm_resource_group.main.name
  loadbalancer_id     = azurerm_lb.main.id
  name                = "${local.azure_name_prefix}-probe"
  port                = 8080
}

resource "azurerm_lb_rule" "main" {
  resource_group_name            = azurerm_resource_group.main.name
  loadbalancer_id                = azurerm_lb.main.id
  name                           = "${local.azure_name_prefix}-rule"
  protocol                       = "Tcp"
  frontend_port                  = 80
  backend_port                   = 8080
  frontend_ip_configuration_name = "PublicIPAddress"
  backend_address_pool_id        = azurerm_lb_backend_address_pool.main.id
  probe_id                       = azurerm_lb_probe.main.id
}