from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.common import StackingConfig
from grafana_foundation_sdk.builders.dashboard import (
    Row,
)
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.models.common import StackingMode

from typing import Self


def _base_filters(project_id: str, forwarding_rule_regex: str):
    return LabelFilters(
        f'project_id="{project_id}"',
        f'forwarding_rule_name=~"{forwarding_rule_regex}"',
    )


def _request_rate_internal(
    base_filters: LabelFilters, title: str, operator: str
) -> Timeseries:
    metric = "loadbalancing_googleapis_com:https_request_count"
    filters = base_filters + f'backend_type{operator}"FRONTEND_5XX"'
    query = f"sum by(response_code) (rate({metric}{filters}[$__rate_interval]))"
    return (
        Timeseries()
        .title(title)
        .stacking(StackingConfig().mode((StackingMode.NORMAL)))
        .fill_opacity(10)
        .unit("reqps")
        .with_target(PrometheusQuery().expr(query).legend_format("__auto"))
    )


def request_rate(project_id: str, forwarding_rule_regex: str):
    base_filters = _base_filters(project_id, forwarding_rule_regex)
    return _request_rate_internal(
        base_filters, "KEYPANEL: Request rate by status code", "!="
    )


def request_rate_lb_5xx(project_id: str, forwarding_rule_regex: str):
    base_filters = _base_filters(project_id, forwarding_rule_regex)
    return _request_rate_internal(base_filters, "Load balancer 500s", "=")


def backend_latency(project_id: str, forwarding_rule_regex: str):
    base_filters = _base_filters(project_id, forwarding_rule_regex)
    return (
        Timeseries()
        .title("KEYPANEL: Backend latency")
        .unit("ms")
        .with_histogram_quantile_targets(
            metric="loadbalancing_googleapis_com:https_backend_latencies_bucket",
            filters=base_filters,
        )
    )


class GCLBMixin:
    def gclb_panels(
        self: Dashboard, project_id: str, forwarding_rule_regex: str
    ) -> Self:
        self.with_row(Row("GCLB"))
        self.with_panel(request_rate(project_id, forwarding_rule_regex))
        self.with_panel(request_rate_lb_5xx(project_id, forwarding_rule_regex))
        self.with_panel(backend_latency(project_id, forwarding_rule_regex))
        return self
