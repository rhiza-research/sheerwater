output "grafana_url" {
  value = local.grafana_url
  description = "The url of the Grafana instance"
}

output "dashboards_base_path" {
  value = var.dashboards_base_path
  description = "The base path of the dashboards directory"
}