from grafana_foundation_sdk.builders.prometheus import Dataquery


class PrometheusQuery(Dataquery):
    def __init__(self):
        super().__init__()
        self.editor_mode("builder").legend_format("__auto")
