# Sample Vulnhub machine file
resource "aws_instance" "sample" {
  ami                    = ""
  instance_type          = var.instance_type
  key_name               = "primary"
  subnet_id              = aws_subnet.my_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_vuln.id]

  tags = {
    Name = "Sample"
  }
}

output "Vulnhub_Sample" {
  value = aws_instance.sample.private_ip
}
