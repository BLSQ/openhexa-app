variable "app_domain" {
  description = "The fully-qualified domain name of the app component"
}
variable "cookie_domain" {
  description = "The domain name to use for cross-component cookies (.something.com for example)"
}
variable "notebooks_url" {
  description = "The full URL of the notebooks component"
}
variable "app_image_name" {
  description = "The Docker image to use for the app component"
  default     = "blsq/openhexa-app"
}
variable "app_image_tag" {
  description = "The tag of the Docker image for the app component"
  default     = "latest"
}

# GCP
variable "gcp_project_id" {
  description = "The ID of your Google Cloud Platform project"
}
variable "gcp_region" {
  description = "The name of the region to use for GCP resources"
}
variable "gcp_zone" {
  description = "The name of the zone to use for GCP resources"
}

# Global IP address
variable "gcp_global_address_name" {
  description = "The name of the GCP global address to use for the app component"
}

# Cloud SQL instance
variable "gcp_sql_instance_name" {
  description = "The name of the GCP Cloud SQL instance"
  default     = "hexa-prime"
}
variable "gcp_sql_instance_tier" {
  description = "The tier to use for the Cloud SQL instance"
}
variable "gcp_sql_database_name" {
  description = "The name of the app component database"
  default     = "hexa-app"
}
variable "gcp_sql_user_name" {
  description = "The username for the app component database"
  default     = "hexa-app"
}
# Service account for the Cloud SQL proxy
variable "gcp_iam_service_account_id" {
  description = "The ID of the service account use for the Cloud SQL proxy"
  default     = "hexa-cloud-sql-proxy"
}
variable "gcp_iam_service_account_display_name" {
  description = "The display name of the service account use for the Cloud SQL proxy"
  default     = "hexa-cloud-sql-proxy"
}

# GKE cluster
variable "gcp_gke_cluster_name" {
  description = "The name of the Kubernetes cluster in GKE"
  default     = "hexa-prime"
}
variable "gcp_gke_default_pool_name" {
  default = "default-pool"
}
variable "gcp_gke_default_pool_max_node_count" {
  description = "The max number of nodes in the default GKE pool"
  default     = 3
}
variable "gcp_gke_default_pool_machine_type" {
  description = "The machine type to use for nodes in the default GKE pool"
  default     = "e2-standard-2"
}

# KUBERNETES
variable "kubernetes_namespace" {
  description = "The Kubernetes namespace in which to deploy the resources of the app component"
  default     = "hexa-app"
}

# AWS
variable "aws_region" {
  description = "The name of the region to use for AWS resources"
}
# Route53
variable "aws_route53_zone_name" {
  description = "The name of the Route53 hosted zone"
}
variable "aws_route53_record_name" {
  description = "The record to add in the hosted zone"
}
