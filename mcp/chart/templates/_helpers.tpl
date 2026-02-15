{{/*
Expand the name of the chart.
*/}}
{{- define "sheerwater-mcp.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "sheerwater-mcp.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sheerwater-mcp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sheerwater-mcp.labels" -}}
helm.sh/chart: {{ include "sheerwater-mcp.chart" . }}
{{ include "sheerwater-mcp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "sheerwater-mcp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sheerwater-mcp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
