# Outputs for Monitoring module

output "prometheus_endpoint" {
  description = "Prometheus endpoint"
  value       = aws_prometheus_workspace.main.prometheus_endpoint
}

output "grafana_endpoint" {
  description = "Grafana endpoint"
  value       = aws_grafana_workspace.main.endpoint
}