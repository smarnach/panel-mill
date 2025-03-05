from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.dashboard import (
    Row,
)
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery

from typing import Self


def pod_count(job: str) -> Timeseries:
    filters = LabelFilters('namespace="$namespace"', f'job="{job}"')
    query = f"count(up{filters})"
    return (
        Timeseries()
        .title("Application pods")
        .with_target(PrometheusQuery().expr(query).legend_format("__auto"))
    )


def _utilization(title: str, filters: LabelFilters, metric: str) -> Timeseries:
    query = f"max_over_time({metric}{filters}[$__interval])"
    return (
        Timeseries()
        .title(title)
        .axis_soft_max(1)
        .unit("percentunit")
        .with_target(PrometheusQuery().expr(query).legend_format("__auto"))
    )


def volume_utilization(volume_name: str, pod_name_regex: str) -> Timeseries:
    filters = LabelFilters(
        'namespace_name="$namespace"',
        f'pod_name=~"{pod_name_regex}"',
        f'volume_name="{volume_name}"',
    )
    metric = "kubernetes_io:pod_volume_utilization"
    return _utilization(f"Disk utilization: {volume_name}", filters, metric)


def cpu_utilization(container: str) -> Timeseries:
    filters = LabelFilters(
        'namespace_name="$namespace"',
        f'container_name="{container}"',
    )
    metric = "kubernetes_io:container_cpu_request_utilization"
    return _utilization(f"CPU request utilization", filters, metric)


def memory_utilization(container: str) -> Timeseries:
    filters = LabelFilters(
        'namespace_name="$namespace"',
        f'container_name="{container}"',
        'memory_type="non-evictable"',
    )
    metric = "kubernetes_io:container_memory_request_utilization"
    return _utilization(f"Memory request utilization", filters, metric)


class KubernetesMixin:
    def kubernetes_panels(
        self: Dashboard,
        job: str,
        pod_name_regex: str,
        volume_names: list[str],
        container: str,
    ) -> Self:
        self.with_row(Row("Kubernetes"))
        self.with_panel(pod_count(job))
        for volume_name in volume_names:
            self.with_panel(volume_utilization(volume_name, pod_name_regex))
        self.with_panel(cpu_utilization(container))
        self.with_panel(memory_utilization(container))
        return self
