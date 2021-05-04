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
resource "google_compute_global_address" "app" {
  name         = var.gcp_global_address_name
  address_type = "EXTERNAL"
  ip_version   = "IPV4"
}

# GCP Cloud SQL
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
# GCP GCE managed certificate
# (See https://github.com/hashicorp/terraform-provider-kubernetes/issues/446)
resource "google_compute_managed_ssl_certificate" "app" {
  name = "app-certificate-${var.app_domain}"

  managed {
    domains = [var.app_domain]
  }
}

# KUBERNETES
data "google_client_config" "terraform" {}
provider "kubernetes" {
  load_config_file = false
  host             = "https://${google_container_cluster.app_cluster.endpoint}"
  token            = data.google_client_config.terraform.access_token
  cluster_ca_certificate = base64decode(
    google_container_cluster.app_cluster.master_auth[0].cluster_ca_certificate,
  )
}
# Namespace
resource "kubernetes_namespace" "app" {
  metadata {
    name = var.kubernetes_namespace
  }
}
# Config map
resource "kubernetes_config_map" "app" {
  metadata {
    name = "app-config"
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
    name = "app-deployment"
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
          "cloud.google.com/gke-nodepool" = google_container_cluster.app_cluster.node_pool[0].name
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
            secret_name = "hexa-cloudsql-oauth-credentials"
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
# SQL Proxy secret
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
# App secret
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
# Service
resource "kubernetes_service" "app" {
  metadata {
    name = "app-service"
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
    name = "app-ingress"
    labels = {
      component = "app"
    }
    annotations = {
      "kubernetes.io/ingress.global-static-ip-name" = var.gcp_global_address_name
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
