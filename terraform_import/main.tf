terraform {
  backend "s3" {
    encrypt = true
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.66.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.1.0"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "3.38.0"
    }
  }
}

# GCP
provider "google" {
  project = var.gcp_project_id
}
# Cloud SQL
resource "google_sql_database_instance" "app" {
  database_version = "POSTGRES_12"
  name             = var.gcp_sql_instance_name
  region           = var.gcp_region
  settings {
    tier = var.gcp_sql_instance_tier
    ip_configuration {
      ipv4_enabled = true
      # TODO: find a safer way to access Cloud SQL instance
      authorized_networks {
        name  = "external-access"
        value = "0.0.0.0/0"
      }
    }
  }
}
