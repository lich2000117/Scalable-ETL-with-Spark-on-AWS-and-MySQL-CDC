variable "region" {
  description = "AWS region to create resources in, this would be best setup according to costs"
  default     = "au-east-1"
}

variable "instance_type" {
  description = "Demo instance, no need to be large"
  default     = "t3.micro"
}

variable "ami_filters" {
  description = "Filters used to select a specific AMI"
  type = map(object({
    name   = string
    values = list(string)
  }))
  default = {
    name = {
      name   = "name"
      values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
    },
    type = {
      name   = "virtualization-type"
      values = ["hvm"]
    }
  }
}

variable "ami_owners" {
  description = "List of owners for the AMI"
  default     = ["099720109477"]  # Canonical's Ubuntu owner ID
}