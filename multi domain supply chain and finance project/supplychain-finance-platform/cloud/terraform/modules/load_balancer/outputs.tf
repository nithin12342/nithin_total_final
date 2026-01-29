# Outputs for Load Balancer module

output "dns_name" {
  description = "Load balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "zone_id" {
  description = "Load balancer zone ID"
  value       = aws_lb.main.zone_id
}

output "arn" {
  description = "Load balancer ARN"
  value       = aws_lb.main.arn
}