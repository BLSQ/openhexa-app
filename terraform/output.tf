output "gcp_sql_instance_connection_name" {
  value = google_sql_database_instance.sql_instance.connection_name
}
output "gcp_gke_cluster_zone" {
  value = google_container_cluster.app_cluster.zone
}
output "gcp_gke_cluster_name" {
  value = google_container_cluster.app_cluster.name
}
output "gcp_global_address" {
  value = google_compute_global_address.app_address.address
}
output "gcp_gke_default_node_pool_name" {
  value = google_container_cluster.app_cluster.node_pool.0.name
}
output "kubernetes_namespace" {
  value = kubernetes_namespace.app_namespace.metadata.0.name
}
output "aws_route53_record_name" {
  value = aws_route53_record.app_record.name
}