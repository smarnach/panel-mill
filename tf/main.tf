provider "grafana" {
  url = "https://yardstick.mozilla.org/"
}

terraform {
  required_version = ">= 1.0"
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 3.20"
    }
  }
}

data "grafana_folder" "sven" {
  title = "sven"
}

resource "grafana_dashboard" "default" {
  for_each = fileset(path.module, "../build/*.json")

  folder      = data.grafana_folder.sven.id
  config_json = file(each.value)
}
