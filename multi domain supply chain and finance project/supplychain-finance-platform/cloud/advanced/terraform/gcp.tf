# GCP Provider Configuration and Resources

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# GCP Locals
locals {
  gcp_name_prefix = "${var.project_name}-${var.environment}-gcp"
  gcp_common_labels = {
    project     = var.project_name
    environment = var.environment
    managed-by  = "Terraform"
    provider    = "GCP"
  }
}

# GCP VPC Network
resource "google_compute_network" "main" {
  name                    = "${local.gcp_name_prefix}-network"
  auto_create_subnetworks = false

  labels = local.gcp_common_labels
}

# GCP Subnets
resource "google_compute_subnetwork" "public" {
  name          = "${local.gcp_name_prefix}-public-subnet"
  ip_cidr_range = "10.2.1.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  labels = local.gcp_common_labels
}

resource "google_compute_subnetwork" "private" {
  name          = "${local.gcp_name_prefix}-private-subnet"
  ip_cidr_range = "10.2.2.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id

  labels = local.gcp_common_labels
}

# GCP Firewall Rules
resource "google_compute_firewall" "web" {
  name    = "${local.gcp_name_prefix}-web-firewall"
  network = google_compute_network.main.id

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]

  labels = local.gcp_common_labels
}

resource "google_compute_firewall" "app" {
  name    = "${local.gcp_name_prefix}-app-firewall"
  network = google_compute_network.main.id

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = ["10.2.0.0/16"]
  target_tags   = ["app-server"]

  labels = local.gcp_common_labels
}

resource "google_compute_firewall" "db" {
  name    = "${local.gcp_name_prefix}-db-firewall"
  network = google_compute_network.main.id

  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }

  source_ranges = ["10.2.0.0/16"]
  target_tags   = ["db-server"]

  labels = local.gcp_common_labels
}

# GCP GKE Cluster
resource "google_container_cluster" "main" {
  name     = "${local.gcp_name_prefix}-gke"
  location = var.gcp_region

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  labels = local.gcp_common_labels
}

resource "google_container_node_pool" "main" {
  name       = "${local.gcp_name_prefix}-node-pool"
  location   = var.gcp_region
  cluster    = google_container_cluster.main.name
  node_count = var.node_count[var.environment]

  node_config {
    preemptible  = false
    machine_type = var.instance_types[var.environment]

    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    labels = local.gcp_common_labels
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# GCP Cloud SQL Database
resource "google_sql_database_instance" "main" {
  name             = "${local.gcp_name_prefix}-postgres"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier = var.environment == "prod" ? "db-n1-standard-2" : "db-f1-micro"

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }

    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
  }

  deletion_protection = var.environment == "prod"

  labels = local.gcp_common_labels
}

resource "google_sql_database" "main" {
  name     = "supplychain"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = "postgres"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

# GCP Memorystore Redis
resource "google_redis_instance" "main" {
  name           = "${local.gcp_name_prefix}-redis"
  tier           = var.environment == "prod" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.environment == "prod" ? 2 : 1

  location_id             = var.gcp_region
  alternative_location_id = var.environment == "prod" ? "us-west2-a" : ""

  authorized_network = google_compute_network.main.id

  redis_version = "REDIS_7_0"
  display_name  = "Supply Chain Redis Instance"

  labels = local.gcp_common_labels
}

# GCP Load Balancer
resource "google_compute_global_address" "main" {
  name = "${local.gcp_name_prefix}-external-address"

  labels = local.gcp_common_labels
}

resource "google_compute_health_check" "main" {
  name = "${local.gcp_name_prefix}-health-check"

  http_health_check {
    port = 8080
    request_path = "/health"
  }

  labels = local.gcp_common_labels
}

resource "google_compute_backend_service" "main" {
  name          = "${local.gcp_name_prefix}-backend-service"
  health_checks = [google_compute_health_check.main.id]

  backend {
    group = google_container_node_pool.main.instance_group_urls[0]
  }

  labels = local.gcp_common_labels
}

resource "google_compute_url_map" "main" {
  name            = "${local.gcp_name_prefix}-url-map"
  default_service = google_compute_backend_service.main.id

  labels = local.gcp_common_labels
}

resource "google_compute_target_http_proxy" "main" {
  name    = "${local.gcp_name_prefix}-http-proxy"
  url_map = google_compute_url_map.main.id

  labels = local.gcp_common_labels
}

resource "google_compute_global_forwarding_rule" "main" {
  name       = "${local.gcp_name_prefix}-forwarding-rule"
  target     = google_compute_target_http_proxy.main.id
  port_range = "80"
  ip_address = google_compute_global_address.main.address

  labels = local.gcp_common_labels
}