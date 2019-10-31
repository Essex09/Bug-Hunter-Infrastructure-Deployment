###################################################
###### Assign appropiate variables       ##########
###################################################
variable "digitalocean_api_token" {}
variable "ssh_keys" {}


###################################################
###### Create tags                       ##########
###################################################
resource "digitalocean_tag" "bughunter" {
    name = "bughunter"
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

resource "digitalocean_droplet" "bughunter_server" {
    name = "bughunter-server"
    image = "ubuntu-16-04-x64"
    size = "s-1vcpu-1gb"
    region = "sfo2"
    ipv6 = "true"
    private_networking = "false"
    monitoring = "true"
    tags = ["${digitalocean_tag.bughunter.name}"]
    ssh_keys = ["${var.ssh_keys}"]
}

###################################################
###### Create a firewall for our droplet ##########
###################################################

resource "digitalocean_firewall" "bughunter" {
    name = "bughunter-firewall"
    droplet_ids = ["${digitalocean_droplet.bughunter_server.id}"]

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
  value = "${digitalocean_droplet.bughunter_server.ipv4_address}"
}

output "Name" {
  value = "${digitalocean_droplet.bughunter_server.name}"
}
