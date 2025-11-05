variable "dashboard_export_enabled" {
  description = "Enable dashboard export to local files"
  type = bool
  default = false
}

variable "dashboard_export_dir" {
  description = "Directory to export dashboards to (absolute path)"
  type = string
  default = "/tmp/exported-dashboards"
}

variable "dashboards_base_path" {
  description = "The base path of the dashboards to upload to Grafana (absolute path, leave empty to use default)"
  type = string
  default = ""
}
