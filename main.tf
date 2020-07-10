# Get the most recent version of Kali AMI
data "aws_ami" "kali" {
  most_recent = true
  owners      = ["aws-marketplace"]
  filter {
    name   = "name"
    values = ["*Kali Linux*"]
  }
}

# The actual AWS EC2 instance (aka the stuff that costs money)
resource "aws_instance" "kali-machine" {
  ami                    = data.aws_ami.kali.id
  instance_type          = var.instance_type
  key_name               = "primary"
  subnet_id              = aws_subnet.my_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  provisioner "file" {
    source      = "kali_setup.sh"
    destination = "/tmp/kali_setup.sh"
    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/labs-key.pem") # CHANGE ME
      host        = self.public_ip
    }
  }

  # Run the setup script
  provisioner "remote-exec" {
    inline = ["chmod +x /tmp/kali_setup.sh && sudo /tmp/kali_setup.sh"]
    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = file("~/.ssh/labs-key.pem") # CHANGE ME
      host        = self.public_ip
    }
  }

  tags = {
    Name = "Kali"
  }
}

# Upload your own key here
resource "aws_key_pair" "primary-key" {
  key_name   = "primary"
  public_key = file("~/.ssh/labs-key.pub") # CHANGE ME
}

# Don't change the name of the output, will break Webapp :)
output "Kali" {
  value = aws_instance.primary_vpn.private_ip
}


