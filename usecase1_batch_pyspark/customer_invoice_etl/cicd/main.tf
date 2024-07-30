provider "aws" {
  region = var.region  # Use the variable, define instance features
}

data "aws_ami" "ubuntu" {
  most_recent = true

  dynamic "filter" {
    for_each = var.ami_filters
    content {
      name   = filter.value.name
      values = filter.value.values
    }
  }

  owners = var.ami_owners
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = "aws_remote_key"  

  connection {
    type        = "ssh"
    user        = "ubuntu"  # default user for Ubuntu, this could be company username
    private_key = file("${path.module}/your-private-key.pem")  # use private key for connection
    host        = self.public_ip
  }

  provisioner "remote-exec" {
    # commands to execute on instance,  this will run test + ETL run
    inline = [
      "sudo apt-get update",
      "sudo docker build -t customer-invoice-etl . && docker run -t --rm -v ./:/etl_app customer-invoice-etl"
    ]
  }

  tags = {
    Name = "Run scheduled ETL job"
  }
}
