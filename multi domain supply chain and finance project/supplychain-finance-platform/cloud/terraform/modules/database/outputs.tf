# Outputs for Database module

output "endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "username" {
  description = "Database username"
  value       = aws_db_instance.main.username
}

output "port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}

output "arn" {
  description = "Database ARN"
  value       = aws_db_instance.main.arn
}