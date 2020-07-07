# First Vulnhub machine on the network
resource "aws_instance" "mrrobot" {
  ami                    = "ami-0123ff4726fe8aff9" # Custom AMI, uploaded using https://docs.amazonaws.cn/en_us/vm-import/latest/userguide/vm-import-ug.pdf
  instance_type          = var.instance_type
  key_name               = "primary"
  subnet_id              = aws_subnet.my_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_vuln.id]

  tags = {
    Name = "Mr Robot"
  }
}
