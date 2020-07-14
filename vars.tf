# Variables that need to be updated with the path to
# YOUR own custom keys
variable "public_key_path" {
  description = "Public key path to use with Terraform"
  default = "~/.ssh/labs-key.pub"
}

variable "private_key_path" {
  description = "Private key path to use with Terraform"
  default = "~/.ssh/labs-key.pem"
}

# Vars to have less redundacy
variable "cidr_vpc" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "cidr_subnet" {
  description = "CIDR block for the subnet"
  default     = "10.0.0.0/24"
}

variable "instance_type" {
  description = "type (aka free) AWS EC2 instance"
  default     = "t2.micro"
}

# Unused
variable "environment_tag" {
  description = "Environment tag"
  default     = "Production"
}

