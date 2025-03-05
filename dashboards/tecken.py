from panel_mill.dashboard import Dashboard
from panel_mill.panels.gclb import GCLBMixin
from panel_mill.panels.kubernetes import KubernetesMixin


class TeckenDashboard(GCLBMixin, KubernetesMixin, Dashboard):
    def __init__(self):
        super().__init__("Test dashboard: Tecken GCP")
        (
            self.uid("sven-tecken-gcp-test")
            .time("now-1d", "now")
            .default_variables("symbols")
            .gclb_panels(
                project_id="moz-fx-webservices-low-$env",
                forwarding_rule_regex=".*symbols-${env:text}-tecken.*",
            )
            .kubernetes_panels(
                job="tecken",
                pod_name_regex="tecken-[^-]+-[^-]+",
                volume_names=["uploads"],
                container="tecken",
            )
        )
