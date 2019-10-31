###################################################
###### Assign appropiate variables       ##########
###################################################
variable "digitalocean_api_token" {}
variable "ssh_keys" {}


###################################################
###### Create tags                       ##########
###################################################
resource "digitalocean_tag" "nginx" {
    name = "nginx"
}

###################################################
###### Assign your API token             ##########
###################################################

provider "digitalocean" {
    token = "${var.digitalocean_api_token}"
}

###################################################
###### Droplet Settings                  ##########
###################################################

resource "digitalocean_droplet" "nginx_server" {
    name = "nginx-server"
    image = "ubuntu-16-04-x64"
    size = "512mb"
    region = "sfo2"
    ipv6 = "true"
    private_networking = "false"
    monitoring = "true"
    tags = ["${digitalocean_tag.nginx.name}"]
    ssh_keys = ["${var.ssh_keys}"]
}

###################################################
###### Create a firewall for our droplet ##########
###################################################

resource "digitalocean_firewall" "webserver" {
    name = "webserver-firewall"
    droplet_ids = ["${digitalocean_droplet.nginx_server.id}"]

    inbound_rule {
        protocol = "tcp"
        port_range = "22"
        source_addresses = ["47.152.61.20"]
    }

    inbound_rule {
        protocol = "tcp"
        port_range = "80"
        source_addresses = ["0.0.0.0/0", "::/0"]
    }

    inbound_rule {
        protocol = "tcp"
        port_range = "443"
        source_addresses = ["0.0.0.0/0", "::/0"]
    }

    inbound_rule {
        protocol = "icmp"
        source_addresses = ["0.0.0.0/0", "::/0"]
    }

    outbound_rule {
        protocol = "tcp"
        port_range = "53"
        destination_addresses = ["0.0.0.0/0", "::/0"]
    }

    outbound_rule {
        protocol = "udp"
        port_range = "53"
        destination_addresses = ["0.0.0.0/0", "::/0"]
    }

    outbound_rule {
       protocol = "icmp"
       destination_addresses = ["0.0.0.0/0", "::/0"]
  }

   outbound_rule {
        protocol = "tcp"
        port_range = "80"
        destination_addresses = ["0.0.0.0/0", "::/0"]
    }

    outbound_rule {
       protocol = "tcp"
       port_range = "443"
       destination_addresses = ["0.0.0.0/0", "::/0"]
  }


}

output "Public_IP" {
  value = "${digitalocean_droplet.nginx_server.ipv4_address}"
}

output "Name" {
  value = "${digitalocean_droplet.nginx_server.name}"
}
