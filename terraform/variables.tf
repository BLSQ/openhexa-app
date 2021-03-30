# Project ID
variable "gcp_project_id" {
  default = "blsq-dip-test"
}
# Cloud SQL instance
variable "gcp_sql_instance_name" {
  default = "hexa-app"
}
variable "gcp_sql_instance_region" {
  default     = "europe-west1"
  description = "The region for the Cloud SQL instances"
}
variable "gcp_sql_hub_instance_access_cidr" {
  default     = "0.0.0.0/0"
  description = "The IPv4 CIDR to provide access the database instance"
}
variable "gcp_sql_machine_type_tier" {
  default = "db-custom-2-7680"
}
variable "gcp_sql_database_name" {
  default = "hexa-app"
}
variable "gcp_sql_user_name" {
  default = "hexa-app"
}

#Service account for the Cloud SQL proxy
variable "account_id" {
  default = "cloud-sql-proxy"
}
variable "display_name" {
  default = "cloud-sql-proxy"
}

#GKE cluster
variable "gcp_gke_cluster_zone" {
  default = "europe-west1-b"
  description = "The zone for the GKE cluster"
}
variable "gcp_gke_cluster_name" {
  default = "hexa-main"
  description = "name of cluster"
}
variable "gcp_gke_default_machine_type" {
  default = "n2-standard-2"
  description = " GCP machine type"
}
variable "gcp_gke_default_pool_name" {
  default = "default-pool-n2s2"
}
variable "gcp_gke_default_node_pool_labels" {
  default = {
    "hub.jupyter.org/node-purpose" = "default"
  }
}
variable "gcp_gke_default_node_pool_taint_effect" {
  default = "NO_SCHEDULE"
}
variable "gcp_gke_default_node_pool_taint_key" {
  default = "hub.jupyter.org_dedicated"
}
variable "gcp_gke_default_node_pool_taint_value" {
  default = "default"
}

# Global IP address
variable "gcp_global_address_name" {
  default = "openhexa-test"
}

# Bucket
variable "gcp_bucket_name" {
  default = "hexa-app"
  description = "Bucket name"
}
variable "gcp_bucket_location" {
  default = "EU"
  description = "Bucket location"
}

