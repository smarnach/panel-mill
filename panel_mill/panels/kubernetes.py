from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.dashboard import Row
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery

from typing import Self


class KubernetesMixin(Dashboard):
    def k8s_pod_count(self, job: str, container: str) -> Timeseries:
        filters_count = LabelFilters('namespace="$namespace"', f'job="{job}"')
        query = f"count(avg_over_time(up{filters_count}[$__interval]))"
        filters_restart = LabelFilters(
            'namespace_name="$namespace"', f'container_name="{container}"'
        )
        return (
            self.timeseries_panel()
            .title("Application pods")
            .with_target(PrometheusQuery().expr(query).legend_format("count"))
            .with_count_target(
                "kubernetes_io:container_restart_count",
                filters_restart,
                legend_format="restarts",
            )
        )

    def k8s_volume_utilization(
        self, volume_name: str, pod_name_regex: str
    ) -> Timeseries:
        filters = LabelFilters(
            'namespace_name="$namespace"',
            f'pod_name=~"{pod_name_regex}"',
            f'volume_name="{volume_name}"',
        )
        metric = "kubernetes_io:pod_volume_utilization"
        return (
            self.utilization_timeseries_panel()
            .title(f"Disk utilization: {volume_name}")
            .with_utilization_target(metric, filters, legend_format="{{pod_name}}")
        )

    def k8s_cpu_request_utilization(self, container: str) -> Timeseries:
        filters = LabelFilters(
            'namespace_name="$namespace"',
            f'container_name="{container}"',
        )
        metric = "kubernetes_io:container_cpu_request_utilization"
        return (
            self.utilization_timeseries_panel()
            .title("CPU request utilization")
            .description(
                "May be above 100 percent, since the limit we can use "
                "is higher than the amount we request."
            )
            .with_utilization_target(metric, filters, legend_format="{{pod_name}}")
        )

    def k8s_memory_request_utilization(self, container: str) -> Timeseries:
        filters = LabelFilters(
            'namespace_name="$namespace"',
            f'container_name="{container}"',
            'memory_type="non-evictable"',
        )
        metric = "kubernetes_io:container_memory_request_utilization"
        return (
            self.utilization_timeseries_panel()
            .title("Memory request utilization")
            .description(
                "May be above 100 percent, since the limit we can use "
                "is higher than the amount we request."
            )
            .with_utilization_target(metric, filters, legend_format="{{pod_name}}")
        )

    def k8s_cpu_limit_utilization(self, container: str) -> Timeseries:
        filters = LabelFilters(
            'namespace_name="$namespace"',
            f'container_name="{container}"',
        )
        metric = "kubernetes_io:container_cpu_limit_utilization"
        return (
            self.utilization_timeseries_panel()
            .title("CPU limit utilization")
            .with_utilization_target(metric, filters, legend_format="{{pod_name}}")
        )

    def k8s_memory_limit_utilization(self, container: str) -> Timeseries:
        filters = LabelFilters(
            'namespace_name="$namespace"',
            f'container_name="{container}"',
            'memory_type="non-evictable"',
        )
        metric = "kubernetes_io:container_memory_limit_utilization"
        return (
            self.utilization_timeseries_panel()
            .title("Memory limit utilization")
            .with_utilization_target(metric, filters, legend_format="{{pod_name}}")
        )

    def k8s_panels(
        self,
        job: str,
        pod_name_regex: str,
        volume_names: list[str],
        container: str,
    ) -> Self:
        self.with_row(Row("Kubernetes"))
        self.with_panel(self.k8s_pod_count(job, container))
        for volume_name in volume_names:
            self.with_panel(self.k8s_volume_utilization(volume_name, pod_name_regex))
        self.with_panel(self.k8s_cpu_request_utilization(container))
        self.with_panel(self.k8s_cpu_limit_utilization(container))
        self.with_panel(self.k8s_memory_request_utilization(container))
        self.with_panel(self.k8s_memory_limit_utilization(container))
        return self
