# Monitoring module for Supply Chain Finance Platform

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/${var.project_name}/${var.environment}/logs"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-${var.environment}-log-group"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Prometheus Workspace
resource "aws_prometheus_workspace" "main" {
  alias = "${var.project_name}-${var.environment}-prometheus"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Grafana Workspace
resource "aws_grafana_workspace" "main" {
  account_access_type      = "CURRENT_ACCOUNT"
  authentication_providers = ["AWS_SSO"]
  permission_type          = "SERVICE_MANAGED"
  role_arn                 = aws_iam_role.grafana.arn

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Role for Grafana
resource "aws_iam_role" "grafana" {
  name = "${var.project_name}-${var.environment}-grafana-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "grafana.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Grafana
resource "aws_iam_policy" "grafana" {
  name = "${var.project_name}-${var.environment}-grafana-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "aps:ListWorkspaces",
          "aps:DescribeWorkspace",
          "aps:QueryMetrics",
          "aps:GetLabels",
          "aps:GetSeries",
          "aps:GetSamples",
          "aps:ListTagsForResource"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Role Policy Attachment for Grafana
resource "aws_iam_role_policy_attachment" "grafana" {
  policy_arn = aws_iam_policy.grafana.arn
  role       = aws_iam_role.grafana.name
}