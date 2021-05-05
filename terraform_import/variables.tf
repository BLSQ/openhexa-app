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
