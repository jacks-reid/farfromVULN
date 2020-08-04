# Vars to have less redundacy
variable "private_key_path" {
  description = "Absolute path to the private key"
}

variable "public_key_path" {
  description = "Absolute path to the public key"
}

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

