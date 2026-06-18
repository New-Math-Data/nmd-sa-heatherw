output "alb_dns_name" {
  description = "ALB DNS name — use this to access the deployed API"
  value       = module.alb.alb_dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing container images"
  value       = var.ecr_repository_url
}
