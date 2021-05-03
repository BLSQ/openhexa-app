output "gcp_sql_instance_connection_name" {
  value = google_sql_database_instance.hexa.connection_name
}
output "gcp_sql_database_name" {
  value = google_sql_database.hexa.name
}
output "gcp_sql_database_user" {
  value = google_sql_user.hexa.name
}
output "gcp_sql_database_password" {
  value = google_sql_user.hexa.password
}

output "gcp_gke_cluster_zone" {
  value = google_container_cluster.hexa.location
}
output "gcp_gke_cluster_name" {
  value = google_container_cluster.hexa.name
}
output "gcp_global_address_name" {
  value = google_compute_global_address.hexa.name
}
output "gcp_global_address" {
  value = google_compute_global_address.hexa.address
}
output "hexa_domain" {
  value = aws_route53_record.www.name
}
output "NODE_POOL_SELECTOR" {
  value = google_container_cluster.hexa.node_pool.0.name
}

output "kubernetes_namespace" {
  value = kubernetes_namespace.hexa.metadata.0.name
}