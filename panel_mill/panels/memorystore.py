from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.common import VizLegendOptions
from grafana_foundation_sdk.builders.dashboard import Row
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery

from typing import Self


class RedisMixin(Dashboard):
    def redis_connections(self, filters: LabelFilters) -> Timeseries:
        metric = "redis_googleapis_com:clients_connected"
        query = f"avg_over_time({metric}{filters}[$__interval])"
        return (
            self.timeseries_panel()
            .title("Connections")
            .legend(VizLegendOptions().show_legend(False))
            .with_target(PrometheusQuery().expr(query))
        )

    def redis_calls_per_second(self, filters: LabelFilters) -> Timeseries:
        metric = "redis_googleapis_com:commands_calls"
        query = f"rate({metric}{filters}[$__rate_interval])"
        return (
            self.timeseries_panel()
            .title("Calls per second")
            .with_target(PrometheusQuery().expr(query).legend_format("{{cmd}}"))
        )

    def redis_memory_utilization(self, filters: LabelFilters) -> Timeseries:
        metric = "redis_googleapis_com:stats_memory_usage_ratio"
        return (
            self.utilization_timeseries_panel()
            .title(f"Memory utilization")
            .legend(VizLegendOptions().show_legend(False))
            .with_utilization_target(metric, filters)
        )

    def redis_cpu_utilization(self, filters: LabelFilters) -> Timeseries:
        metric = "redis_googleapis_com:stats_cpu_utilization"
        query = f"sum by(space) (increase({metric}{filters}[$__rate_interval]) / 60)"
        return (
            self.utilization_timeseries_panel()
            .title(f"CPU utilization")
            .with_target(PrometheusQuery().expr(query).legend_format("{{space}}"))
        )

    def redis_cache_hit_ratio(self, filters: LabelFilters) -> Timeseries:
        metric = "redis_googleapis_com:stats_cache_hit_ratio"
        query = f"avg_over_time({metric}{filters}[$__interval])"
        return (
            self.utilization_timeseries_panel()
            .title("Cache hit ratio")
            .legend(VizLegendOptions().show_legend(False))
            .with_target(PrometheusQuery().expr(query))
        )

    def redis_cache_eviction_rate(self, filters: LabelFilters) -> Timeseries:
        metric = "redis_googleapis_com:stats_evicted_keys"
        return (
            self.utilization_timeseries_panel()
            .title("Cache eviction rate")
            .legend(VizLegendOptions().show_legend(False))
            .with_count_target(metric, filters)
        )

    def redis_panels(self) -> Self:
        instance_id = (
            "projects/$project_id/locations/us-west1/instances/$tenant-$env-${env:text}"
        )
        filters = LabelFilters(f'instance_id="{instance_id}"')
        return (
            self.with_row(Row("Memorystore (Redis)"))
            .with_panel(self.redis_connections(filters))
            .with_panel(self.redis_calls_per_second(filters))
            .with_panel(self.redis_memory_utilization(filters))
            .with_panel(self.redis_cpu_utilization(filters))
            .with_panel(self.redis_cache_hit_ratio(filters))
            .with_panel(self.redis_cache_eviction_rate(filters))
        )
