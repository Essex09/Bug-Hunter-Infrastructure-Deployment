provider "aws" {
  region   = "us-west-2"
  shared_credentials_file = "~/.aws/credentials"
  profile	    = "terraform"
}

resource "aws_lightsail_instance" "bughunter" {
  name              = "bughunter"
  availability_zone = "us-west-2a"
  blueprint_id      = "debian_9_5"
  bundle_id         = "micro_2_0"
  key_pair_name     = "CHANGETHIS"
}

resource "aws_security_group" "bughunter" {
  name        = "bughunter"

  # SSH access from anywhere
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP access from anywhere
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS access from anywhere
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "Public_IP" {
  value = "${aws_lightsail_instance.bughunter.public_ip_address}"
}

output "Name" {
  value = "${aws_lightsail_instance.bughunter.name}"
}
