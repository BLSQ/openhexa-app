# GCP
variable "gcp_project_id" {
  description = "The ID of your Google Cloud Platform project"
}
variable "gcp_region" {
  description = "The name of the region to use for GCP resources"
}
# Cloud SQL instance
variable "gcp_sql_instance_name" {
  description = "The name of the GCP Cloud SQL instance"
  default     = "hexa-prime"
}
variable "gcp_sql_instance_tier" {
  description = "The tier to use for the Cloud SQL instance"
  default     = "db-custom-1-3840"
}
variable "gcp_sql_instance_availability_type" {
  description = "The availability type for the master instance.This is only used to set up high availability for the PostgreSQL instance. Can be either `ZONAL` or `REGIONAL`."
  default     = "ZONAL"
}
