provider "google" {
  project = var.gcp_project_id
}

provider "aws" {
  region    = "eu-central-1"
} 
# Create a Cloud SQL for PostgreSQL instance
resource "google_sql_database_instance" "hexa" {
  name             = var.gcp_sql_instance_name
  database_version = "POSTGRES_12"
  region           = var.gcp_sql_instance_region
  settings {
    tier = var.gcp_sql_machine_type_tier
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "any"
        value = var.gcp_sql_hub_instance_access_cidr
      }
    }
  }
}

# Create a Cloud SQL database and user with access permissions in Cloud SQL database
resource "google_sql_database" "hexa" {
  name     = var.gcp_sql_database_name
  instance = google_sql_database_instance.hexa.name

}

resource "random_password" "user_password" {
  length  = 48
  special = false
}

resource "google_sql_user" "hexa" {
  name     = var.gcp_sql_user_name
  instance = google_sql_database_instance.hexa.name
  password = random_password.user_password.result
  provisioner "local-exec" {
    command = <<EOT
      psql postgresql://${google_sql_user.hexa.name}:${google_sql_user.hexa.password}@${google_sql_database_instance.hexa.public_ip_address}:5432/${google_sql_database.hexa.name} <<EOT
      GRANT ALL PRIVILEGES ON DATABASE hexa TO "${google_sql_user.hexa.name}";
      GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "${google_sql_user.hexa.name}";
    EOT
  }
}

# Create a service account
resource "google_service_account" "hexa" {
  account_id   = var.account_id
  display_name = var.display_name
  project      = var.gcp_project_id
  description  = "Used to allow pods to access Cloud SQL" 
}

resource "google_service_account_key" "hexa" {
  service_account_id = google_service_account.hexa.name
}
resource "google_project_iam_binding" "hexa" {
  project = var.gcp_project_id
  role    = "roles/cloudsql.client"

  members = [
    "serviceAccount:${google_service_account.hexa.email}",
  ]
}

# Create a GKE cluster
resource "google_container_cluster" "hexa" {
  name = var.gcp_gke_cluster_name
  location = var.gcp_gke_cluster_zone
  node_pool {
    name = var.gcp_gke_default_pool_name
    node_count = 1
    autoscaling {
      max_node_count = 3
      min_node_count = 1
                }
    node_config {
      machine_type = var.gcp_gke_default_machine_type  
      metadata  = {
         disable-legacy-endpoints = true
                }    
    }
  }
   lifecycle {
    ignore_changes = [ ip_allocation_policy ]
  }
}

# Create a global IP address 
resource "google_compute_global_address" "hexa" {
  name = var.gcp_global_address_name
  address_type  = "EXTERNAL" 
  ip_version    = "IPV4" 


}

# AWS ROUTE53 Record
data "aws_route53_zone" "blsq" {
  name = "bluesquare.org"
  private_zone = false
}
resource "aws_route53_record" "www" {
  zone_id = data.aws_route53_zone.blsq.zone_id
  name = "openhexa.${data.aws_route53_zone.blsq.name}"
  type = "A"
  ttl = "300"
  records = [
    google_compute_global_address.hexa.address
  ]
} 
