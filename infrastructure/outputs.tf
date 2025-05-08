output "instance_public_ip" {
  description = "Public IP address of the EC2 instance."
  value       = aws_instance.app_server[*].public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance."
  value       = aws_instance.app_server[*].public_dns
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket created."
  value       = aws_s3_bucket.app_bucket.id
}

# output "load_balancer_dns_name" {
#   description = "The DNS name of the load balancer"
#   value       = aws_lb.tulia_lb.dns_name
# }
