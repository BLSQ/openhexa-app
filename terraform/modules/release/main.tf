# Fetch namespace and networking resources
data "kubernetes_namespace" "app" {
  metadata {
    name = "hexa-app-${var.environment}"
  }
}
data "google_compute_global_address" "app" {
  name = "hexa-app-${var.environment}"
}
data "google_compute_ssl_certificate" "app" {
  name = "hexa-app-${var.environment}"
}

# Deployment
resource "kubernetes_deployment" "app" {
  timeouts {
    create = "5m"
  }
  metadata {
    name      = "app-deployment"
    namespace = data.kubernetes_namespace.app.metadata[0].name
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
        container {
          name  = "app-container"
          image = "blsq/openhexa-app:${var.image_tag}"
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
          # TODO stop using entrypoint
          command = ["/code/docker-entrypoint.sh"]
          args    = ["start"]
          readiness_probe {
            http_get {
              path = "/ready"
              port = "8000"
              http_header {
                name  = "Host"
                value = var.domain
              }
            }
          }
        }
        container {
          name  = "cloudsql-proxy"
          image = "gcr.io/cloudsql-docker/gce-proxy:1.21.0"
          command = [
            "/cloud_sql_proxy",
            "--dir=/cloudsql",
            "-credential_file=/secrets/cloudsql/credentials.json"
          ]
          env {
            name = "INSTANCES"
            value_from {
              secret_key_ref {
                name = "csp-secret"
                key  = "INSTANCES"
              }
            }
          }
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
            secret_name = "csp-secret"
            items {
              key  = "credentials.json"
              path = "credentials.json"
            }
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

# Migration job
resource "kubernetes_job" "app" {
  depends_on = [kubernetes_deployment.app]
  metadata {
    name      = "app-migration-job"
    namespace = data.kubernetes_namespace.app.metadata[0].name
  }
  spec {
    template {
      metadata {}
      spec {
        share_process_namespace = true
        container {
          name    = "app-container"
          image   = "blsq/openhexa-app:${var.image_tag}"
          command = ["sh"]
          # TODO stop using entrypoint
          args = ["-c", "/code/docker-entrypoint.sh migrate;pkill cloud_sql_proxy"]
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
        }
        container {
          name  = "cloudsql-proxy"
          image = "gcr.io/cloudsql-docker/gce-proxy:1.21.0"
          command = [
            "/cloud_sql_proxy",
            "--dir=/cloudsql",
            "-credential_file=/secrets/cloudsql/credentials.json"
          ]
          env {
            name = "INSTANCES"
            value_from {
              secret_key_ref {
                name = "csp-secret"
                key  = "INSTANCES"
              }
            }
          }
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
            secret_name = "csp-secret"
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
    namespace = data.kubernetes_namespace.app.metadata[0].name
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
    namespace = data.kubernetes_namespace.app.metadata[0].name
    labels = {
      component = "app"
    }
    annotations = {
      "kubernetes.io/ingress.global-static-ip-name" = data.google_compute_global_address.app.name
      # https://github.com/hashicorp/terraform-provider-google/issues/6637
      "ingress.gcp.kubernetes.io/pre-shared-cert" = data.google_compute_ssl_certificate.app.name
    }
  }
  spec {
    backend {
      service_name = "app-service"
      service_port = "8000"
    }
  }
}