variable "dashboards_base_path" {
  description = "The base path of the dashboards to upload to Grafana (relative to the terraform config directory)"
  type = string
  default = "../../dashboards"
}