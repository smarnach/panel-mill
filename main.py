from grafana_foundation_sdk.cog.encoder import JSONEncoder

from importlib import import_module
from pathlib import Path

ALL_DASHBOARDS = {
    "dashboards.tecken.TeckenDashboard": "tecken-gcp.json",
    "dashboards.eliot.EliotDashboard": "eliot.json",
}

def main():
    encoder = JSONEncoder(sort_keys=True, indent=2)
    build_path = Path("build")
    for dashboard_class, file_name in ALL_DASHBOARDS.items():
        module_path, class_name = dashboard_class.rsplit(".", 1)
        module = import_module(module_path)
        dashboard = getattr(module, class_name)().build()
        with (build_path / file_name).open("w") as f:
            f.write(encoder.encode(dashboard))


if __name__ == "__main__":
    main()
