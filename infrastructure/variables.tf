variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "The EC2 instance type."
  type        = string
  default     = "t2.micro"
}

variable "ami_id" {
  description = "The AMI ID for the EC2 instance. Default is Amazon Linux 2."
  type        = string
  default     = "ami-0c55b159cbfafe1f0" # Example: Amazon Linux 2 AMI (HVM), SSD Volume Type in us-east-1
}

variable "bucket_name" {
  description = "The name of the S3 bucket."
  type        = string
}

variable "microservice_port" {
  description = "The port the microservice will listen on."
  type        = number
  default     = 8080
}

variable "project_name" {
  description = "A name prefix for resources."
  type        = string
  default     = "microservice-app"
}
