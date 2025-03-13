from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters, PrometheusQuery

from grafana_foundation_sdk.builders.dashboard import Row

from typing import Self


class GCLBMixin(Dashboard):
    def _gclb_request_rate_by_status_code(
        self, filters: LabelFilters, title: str
    ) -> Timeseries:
        metric = "loadbalancing_googleapis_com:https_request_count"
        query = f"sum by(response_code) (rate({metric}{filters}[$__rate_interval]))"
        query_total = f"sum(rate({metric}{filters}[$__rate_interval]))"
        return (
            self.timeseries_panel()
            .title(title)
            .unit("reqps")
            .with_target(PrometheusQuery().expr(query))
            .with_target(PrometheusQuery().expr(query_total).legend_format("total"))
        )

    def gclb_request_rate_by_status_code(self, filters: LabelFilters) -> Timeseries:
        return self._gclb_request_rate_by_status_code(
            filters + 'backend_type!="FRONTEND_5XX"',
            "KEYPANEL: Request rate by status code",
        )

    def gclb_request_rate_lb_5xx(self, filters: LabelFilters) -> Timeseries:
        return self._gclb_request_rate_by_status_code(
            filters + 'backend_type="FRONTEND_5XX"', "Load balancer 500s"
        ).description(
            "These are 500s emitted by the load balancer without sending the "
            "request to any backend. Some of these are outside of our control."
        )

    def gclb_request_rate_all_5xx(self, filters: LabelFilters) -> Timeseries:
        return self._gclb_request_rate_by_status_code(
            filters + 'response_code_class="500"',
            "All 500s (load balancer and backend)",
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
            .with_panel(self.gclb_request_rate_all_5xx(filters))
            .with_panel(self.gclb_backend_latency(filters))
        )
