from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.dashboard import Row
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery

from typing import Self


class GCLBMixin(Dashboard):
    def _gclb_request_rate_by_status_code(
        self, filters: LabelFilters, title: str, operator: str
    ) -> Timeseries:
        metric = "loadbalancing_googleapis_com:https_request_count"
        filters = filters + f'backend_type{operator}"FRONTEND_5XX"'
        query = f"sum by(response_code) (rate({metric}{filters}[$__rate_interval]))"
        return (
            self.stacked_rps_timeseries_panel()
            .title(title)
            .with_target(PrometheusQuery().expr(query).legend_format("__auto"))
        )

    def gclb_request_rate_by_status_code(self, filters: LabelFilters) -> Timeseries:
        return self._gclb_request_rate_by_status_code(
            filters, "KEYPANEL: Request rate by status code", "!="
        )

    def gclb_request_rate_lb_5xx(self, filters: LabelFilters) -> Timeseries:
        return self._gclb_request_rate_by_status_code(
            filters, "Load balancer 500s", "="
        )

    def gclb_backend_latency(self, filters: LabelFilters) -> Timeseries:
        return (
            self.histogram_timeseries_panel()
            .title("KEYPANEL: Backend latency")
            .unit("ms")
            .with_histogram_quantile_targets(
                "loadbalancing_googleapis_com:https_backend_latencies_bucket",
                filters,
            )
        )

    def gclb_panels(self, forwarding_rule_regex: str) -> Self:
        filters = LabelFilters(
            'project_id="$k8s_project_id"',
            f'forwarding_rule_name=~"{forwarding_rule_regex}"',
        )
        return (
            self.with_row(Row("GCLB"))
            .with_panel(self.gclb_request_rate_by_status_code(filters))
            .with_panel(self.gclb_request_rate_lb_5xx(filters))
            .with_panel(self.gclb_backend_latency(filters))
        )
