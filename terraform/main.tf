terraform {
  backend "s3" {
    encrypt = true
  }
}

# GCP
provider "google" {
  project = var.gcp_project_id
}
# Global IP address
resource "google_compute_global_address" "app_address" {
  name         = var.gcp_global_address_name
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
}

# GCP Cloud SQL
resource "google_sql_database_instance" "sql_instance" {
  database_version = "POSTGRES_12"
  name             = var.gcp_sql_instance_name
  region           = var.gcp_region
  settings {
    tier = var.gcp_sql_instance_tier
    ip_configuration {
      ipv4_enabled = true
      # TODO: find a safer way to access Cloud SQL instance
      authorized_networks {
        name = "external-access"
        value = "0.0.0.0/0"
      }
    }
  }
}
resource "google_sql_database" "app_database" {
  name     = var.gcp_sql_database_name
  instance = google_sql_database_instance.sql_instance.name
}
resource "random_password" "app_database_password" {
  length  = 20
  special = false
  lifecycle {
    ignore_changes = all
  }
}
resource "google_sql_user" "app_database_user" {
  name     = var.gcp_sql_user_name
  instance = google_sql_database_instance.sql_instance.name
  password = random_password.app_database_password.result
  provisioner "local-exec" {
    command = <<EOT
      psql postgresql://${google_sql_user.app_database_user.name}:${google_sql_user.app_database_user.password}@${google_sql_database_instance.sql_instance.public_ip_address}:5432/${google_sql_database.app_database.name} <<EOT
      GRANT ALL PRIVILEGES ON DATABASE ${google_sql_database.app_database.name} TO "${google_sql_user.app_database_user.name}";
      GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "${google_sql_user.app_database_user.name}";
    EOT
  }
}

# GCP IAM (Cloud SQL proxy)
resource "google_service_account" "cloud_sql_proxy" {
  account_id   = var.gcp_iam_service_account_id
  display_name = var.gcp_iam_service_account_display_name
  project      = var.gcp_project_id
  description  = "Used to allow pods to access Cloud SQL"
}
resource "google_service_account_key" "cloud_sql_proxy" {
  service_account_id = google_service_account.cloud_sql_proxy.name

  keepers = {
    # Keep the key alive as long as the service account ID stays the same
    service_account_id = google_service_account.cloud_sql_proxy.name
  }
}
resource "google_project_iam_binding" "hexa" {
  project = var.gcp_project_id
  role    = "roles/cloudsql.client"
  members = [
    "serviceAccount:${google_service_account.cloud_sql_proxy.email}",
  ]
}

# GCP GKE cluster
resource "google_container_cluster" "app_cluster" {
  name     = var.gcp_gke_cluster_name
  location = var.gcp_zone
  node_pool {
    name       = var.gcp_gke_default_pool_name
    node_count = 1
    autoscaling {
      min_node_count = 1
      max_node_count = var.gcp_gke_default_pool_max_node_count
    }
    node_config {
      machine_type = var.gcp_gke_default_pool_machine_type
      metadata = {
        disable-legacy-endpoints = true
      }
    }
  }
}

# KUBERNETES
data "google_client_config" "terraform" {}
provider "kubernetes" {
  host  = "https://${google_container_cluster.app_cluster.endpoint}"
  token = data.google_client_config.terraform.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.app_cluster.master_auth[0].cluster_ca_certificate,
  )
}
# Namespace
resource "kubernetes_namespace" "app_namespace" {
  metadata {
    name = var.kubernetes_namespace
  }
}
# Create a secret for the Cloud SQL proxy
resource "kubernetes_secret" "sql_proxy" {
  metadata {
    name      = "hexa-cloudsql-oauth-credentials"
    namespace = var.kubernetes_namespace
  }
  # TODO: Use workload identity, see # https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity
  data = {
    "credentials.json" = base64decode(google_service_account_key.cloud_sql_proxy.private_key)
  }
}
# Generate a secret key for the Django app
resource "random_password" "django_secret_key" {
  length  = 50
  special = true
  lifecycle {
    ignore_changes = all
  }
}
# Create a secret for the Django environment variables
resource "kubernetes_secret" "django" {
  metadata {
    name      = "app-secret"
    namespace = var.kubernetes_namespace
  }
  data = {
    DATABASE_USER     = google_sql_user.app_database_user.name
    DATABASE_PASSWORD = random_password.app_database_password.result
    DATABASE_NAME     = google_sql_database.app_database.name
    DATABASE_PORT     = 5432
    SECRET_KEY        = random_password.django_secret_key.result
  }
}

# AWS
provider "aws" {
  region = var.aws_region
}
# Route53 Record
data "aws_route53_zone" "zone" {
  name         = var.aws_route53_zone_name
  private_zone = false
}
resource "aws_route53_record" "app_record" {
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = "${var.aws_route53_record_name}.${data.aws_route53_zone.zone.name}"
  type    = "A"
  ttl     = "300"
  records = [
    google_compute_global_address.app_address.address
  ]
}
