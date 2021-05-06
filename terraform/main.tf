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
# Global IP address
resource "google_compute_global_address" "app" {
  name = var.gcp_global_address_name
}

# Cloud SQL
resource "google_sql_database_instance" "app" {
  database_version = "POSTGRES_12"
  name             = var.gcp_sql_instance_name
  region           = var.gcp_region
  lifecycle {
    prevent_destroy = true
  }
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
resource "google_sql_database" "app" {
  name     = var.gcp_sql_database_name
  instance = google_sql_database_instance.app.name
}
resource "random_password" "app_database" {
  length  = 20
  special = false
  lifecycle {
    ignore_changes = all
  }
}
resource "google_sql_user" "app" {
  name     = var.gcp_sql_user_name
  instance = google_sql_database_instance.app.name
  password = random_password.app_database.result
  provisioner "local-exec" {
    command = <<EOT
      psql postgresql://${google_sql_user.app.name}:${google_sql_user.app.password}@${google_sql_database_instance.app.public_ip_address}:5432/${google_sql_database.app.name} <<EOT
      GRANT ALL PRIVILEGES ON DATABASE ${google_sql_database.app.name} TO "${google_sql_user.app.name}";
      GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "${google_sql_user.app.name}";
    EOT
  }
}

# IAM (Cloud SQL proxy)
resource "google_service_account" "app_cloud_sql_proxy" {
  account_id   = var.gcp_iam_cloud_sql_proxy_service_account_id
  display_name = var.gcp_iam_cloud_sql_proxy_service_account_id
  project      = var.gcp_project_id
  description  = "Cloud SQL Proxy"
}
resource "google_service_account_key" "app_cloud_sql_proxy" {
  service_account_id = google_service_account.app_cloud_sql_proxy.name

  keepers = {
    # Keep the key alive as long as the service account ID stays the same
    service_account_id = google_service_account.app_cloud_sql_proxy.account_id
  }
}
resource "google_project_iam_binding" "app_cloud_sql_proxy" {
  project = var.gcp_project_id
  role    = "roles/cloudsql.client"
  members = [
    "serviceAccount:${google_service_account.app_cloud_sql_proxy.email}",
  ]
}
# GKE cluster
resource "google_container_cluster" "cluster" {
  name                     = var.gcp_gke_cluster_name
  location                 = var.gcp_zone
  initial_node_count       = 1
  remove_default_node_pool = true
}
resource "google_container_node_pool" "default_pool" {
  cluster    = google_container_cluster.cluster.name
  name       = var.gcp_gke_default_pool_name
  location   = var.gcp_zone
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
# GCE managed certificate
# (See https://github.com/hashicorp/terraform-provider-kubernetes/issues/446)
resource "google_compute_managed_ssl_certificate" "app" {
  name = var.kubernetes_namespace

  managed {
    domains = [var.app_domain]
  }
}

# KUBERNETES
data "google_client_config" "terraform" {}
provider "kubernetes" {
  host  = "https://${google_container_cluster.cluster.endpoint}"
  token = data.google_client_config.terraform.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.cluster.master_auth[0].cluster_ca_certificate,
  )
}
# Namespace
resource "kubernetes_namespace" "app" {
  metadata {
    name = var.kubernetes_namespace
  }
}
# Secrets
resource "random_password" "django_secret_key" {
  length  = 50
  special = true
  lifecycle {
    ignore_changes = all
  }
}
resource "kubernetes_secret" "app" {
  metadata {
    name      = "app-secret"
    namespace = var.kubernetes_namespace
  }
  data = {
    DATABASE_USER     = google_sql_user.app.name
    DATABASE_PASSWORD = random_password.app_database.result
    DATABASE_NAME     = google_sql_database.app.name
    DATABASE_PORT     = 5432
    SECRET_KEY        = random_password.django_secret_key.result
  }
}

resource "kubernetes_secret" "cloud_sql_proxy" {
  metadata {
    name      = "cloud-sql-proxy-secret"
    namespace = var.kubernetes_namespace
  }
  # TODO: Use workload identity, see # https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity
  data = {
    "credentials.json" = base64decode(google_service_account_key.app_cloud_sql_proxy.private_key)
  }
}
# Config map
resource "kubernetes_config_map" "app" {
  metadata {
    name      = "app-config"
    namespace = var.kubernetes_namespace
    labels = {
      component = "app"
    }
  }
  data = {
    DEBUG                 = "false"
    ALLOWED_HOSTS         = var.app_domain
    DATABASE_HOST         = "127.0.0.1"
    DATABASE_PORT         = "5432"
    NOTEBOOKS_URL         = var.notebooks_url
    SESSION_COOKIE_DOMAIN = var.cookie_domain
  }
}
# Deployment
resource "kubernetes_deployment" "app" {
  metadata {
    name      = "app-deployment"
    namespace = var.kubernetes_namespace
    labels = {
      component = "app"
    }
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        component = "app"
      }
    }
    template {
      metadata {
        labels = {
          component = "app"
        }
      }
      spec {
        node_selector = {
          "cloud.google.com/gke-nodepool" = google_container_node_pool.default_pool.name
        }
        container {
          name  = "app-container"
          image = "${var.app_image_name}:${var.app_image_tag}"
          port {
            container_port = 8000
          }
          env_from {
            secret_ref {
              name = "app-secret"
            }
          }
          env_from {
            config_map_ref {
              name = "app-config"
            }
          }
          command = ["/code/docker-entrypoint.sh"]
          args    = ["start"]
          readiness_probe {
            http_get {
              path = "/ready"
              port = "8000"
              http_header {
                name  = "Host"
                value = var.app_domain
              }
            }
          }
        }
        container {
          name  = "cloudsql-proxy"
          image = "gcr.io/cloudsql-docker/gce-proxy:1.21.0"
          command = ["/cloud_sql_proxy", "--dir=/cloudsql",
            "-instances=${google_sql_database_instance.app.connection_name}=tcp:5432",
          "-credential_file=/secrets/cloudsql/credentials.json"]
          volume_mount {
            name       = "cloudsql-oauth-credentials"
            mount_path = "/secrets/cloudsql"
            read_only  = true
          }
          volume_mount {
            name       = "ssl-certs"
            mount_path = "/etc/ssl/certs"
          }
          volume_mount {
            name       = "cloudsql"
            mount_path = "/cloudsql"
          }
        }
        volume {
          name = "cloudsql-oauth-credentials"
          secret {
            secret_name = kubernetes_secret.cloud_sql_proxy.metadata[0].name
          }
        }
        volume {
          name = "ssl-certs"
          host_path {
            path = "/etc/ssl/certs"
          }
        }
        volume {
          name = "cloudsql"
          empty_dir {}
        }
      }
    }
  }
}
# Service
resource "kubernetes_service" "app" {
  metadata {
    name      = "app-service"
    namespace = var.kubernetes_namespace
    labels = {
      component = "app"
    }
  }
  spec {
    type = "NodePort"
    port {
      port        = "8000"
      target_port = "8000"
    }
    selector = {
      component = "app"
    }
  }
}
# Ingress
resource "kubernetes_ingress" "app" {
  metadata {
    name      = "app-ingress"
    namespace = var.kubernetes_namespace
    labels = {
      component = "app"
    }
    annotations = {
      "kubernetes.io/ingress.global-static-ip-name" = google_compute_global_address.app.name
      "ingress.gcp.kubernetes.io/pre-shared-cert"   = google_compute_managed_ssl_certificate.app.name
    }
  }
  spec {
    backend {
      service_name = "app-service"
      service_port = "8000"
    }
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
resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.zone.zone_id
  name    = "${var.aws_route53_record_name}.${data.aws_route53_zone.zone.name}"
  type    = "A"
  ttl     = "300"
  records = [
    google_compute_global_address.app.address
  ]
}
