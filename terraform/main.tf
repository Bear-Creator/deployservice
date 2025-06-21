terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
      version = ">= 0.129.0"
    }
  }
}

provider "yandex" {
  service_account_key_file = file("service_account_key.json")
  cloud_id                = "<your-cloud-id>"
  folder_id               = "<your-folder-id>"
  zone                    = "ru-central1-a"
}

resource "yandex_vpc_network" "network" {
  name = "app-network"
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "app-subnet"
  zone           = "ru-central1-a"
  network_id     = yandex_vpc_network.network.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

resource "yandex_compute_instance" "app_vm" {
  name        = "app-vm"
  platform_id = "standard-v3"
  zone        = "ru-central1-a"

  resources {
    cores  = 2
    memory = 4
  }

  boot_disk {
    initialize_params {
      image_id = "fd8d3c0s5v8f3p6v2i1k"
      size     = 20
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat       = true # Enable public IP
  }

  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
  }
}

output "vm_public_ip" {
  value = yandex_compute_instance.app_vm.network_interface.0.nat_ip_address
}

output "vm_private_ip" {
  value = yandex_compute_instance.app_vm.network_interface.0.ip_address
}