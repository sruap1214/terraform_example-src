resource "aws_s3_bucket" "app_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "${var.project_name}-bucket"
    Environment = "Dev"
  }
}
