# Create a VPC so we can eventually have a cloud full of cool stuff
resource "aws_vpc" "main" {
  cidr_block           = var.cidr_vpc
  enable_dns_support   = true
  enable_dns_hostnames = true
}

# Create a public subnet for the VPC
resource "aws_subnet" "my_subnet" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.cidr_subnet
  availability_zone       = "us-east-2a"
  map_public_ip_on_launch = "true"

  tags = {
    Name = "public subnet"
  }
}

# Internet gateway for the VPC resources to access WAN
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main_gateway"
  }
}

# Route table
resource "aws_route_table" "my_vpc_us_east_2a_public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "Public Subnet Route Table"
  }
}

# Associate route table with subnet
resource "aws_route_table_association" "my_vpc_us_east_2a_public" {
  subnet_id      = aws_subnet.my_subnet.id
  route_table_id = aws_route_table.my_vpc_us_east_2a_public.id
}


# Basically AWS by default doesn't enable ssh, so enable that
resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "allow SSH traffic on port 22"
  vpc_id      = aws_vpc.main.id


  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "All traffic from VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }  

  # Allows any kind of traffic outwards
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_ssh"
  }
}

# Security group allowing all traffic from VPC CIDR range
resource "aws_security_group" "allow_vuln" {
  name        = "allow_vuln"
  description = "allow all traffic"
  vpc_id      = aws_vpc.main.id


  ingress {
    description = "allow all traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Allows any kind of traffic outwards
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow_vuln"
  }
}


