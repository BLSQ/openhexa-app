terraform {
  backend "gcs" {
    prefix = "releases/demo/app"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.71.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.3.1"
    }
  }
}

# Providers configuration
provider "google" {}
data "google_client_config" "config" {}
data "google_container_cluster" "aldebaran" {
  name = "hexa-aldebaran"
}
provider "kubernetes" {
  host  = "https://${data.google_container_cluster.aldebaran.endpoint}"
  token = data.google_client_config.config.access_token
  cluster_ca_certificate = base64decode(
    data.google_container_cluster.aldebaran.master_auth[0].cluster_ca_certificate,
  )
}

# Release
module "release" {
  source      = "../modules/release"
  environment = "demo"
  domain      = "app.demo.openhexa.org"
  image_tag   = "0.6.9"
}
