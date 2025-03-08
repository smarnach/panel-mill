from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.common import StackingConfig
from grafana_foundation_sdk.builders.dashboard import Row
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery

from typing import Self


def utilization(filters: LabelFilters, resource: str) -> Timeseries:
    metric = f"cloudsql_googleapis_com:database_{resource.lower()}_utilization"
    return (
        Timeseries()
        .title(f"{resource} utilization")
        .with_utilization_target(metric, filters, legend_format="{{database_id}}")
    )


def disk_iops(filters: LabelFilters, mode: str) -> Timeseries:
    metric = f"cloudsql_googleapis_com:database_disk_{mode}_ops_count"
    query = f"rate({metric}{filters}[$__rate_interval])"
    return (
        Timeseries()
        .title(f"Disk {mode} IO")
        .unit("iops")
        .with_target(PrometheusQuery().expr(query).legend_format("{{database_id}}"))
    )


def network_bytes(filters: LabelFilters, direction: str) -> Timeseries:
    metric = f"cloudsql_googleapis_com:database_network_{direction}_bytes_count"
    query = f"rate({metric}{filters}[$__rate_interval])"
    return (
        Timeseries()
        .title(f"Network {direction} bytes")
        .unit("Bps")
        .with_target(PrometheusQuery().expr(query).legend_format("{{database_id}}"))
    )


def postgres_active_connections(filters: LabelFilters) -> Timeseries:
    metric = "cloudsql_googleapis_com:database_postgresql_num_backends"
    query = f"sum by(database_id) (max_over_time({metric}{filters}[$__interval]))"
    return (
        Timeseries()
        .title("Active connections")
        .with_target(PrometheusQuery().expr(query).legend_format("{{database_id}}"))
    )


class ClousSQLMixin(Dashboard):
    def cloud_sql_panels(self, filters: LabelFilters) -> Self:
        return (
            self.with_panel(utilization(filters, "CPU"))
            .with_panel(utilization(filters, "Memory"))
            .with_panel(disk_iops(filters, "read"))
            .with_panel(disk_iops(filters, "write"))
            .with_panel(network_bytes(filters, "received"))
            .with_panel(network_bytes(filters, "sent"))
            .with_panel(utilization(filters, "Disk"))
        )


class PostgresMixin(ClousSQLMixin):
    def postgres_panels(self, tenant: str, database_id: str | None = None) -> Self:
        if not database_id:
            database_id = f"$project_id:{tenant}-$env-${{env:text}}-v1"
        filters = LabelFilters(f'database_id="{database_id}"')
        return (
            self.with_row(Row("Cloud SQL (Postgres)"))
            .cloud_sql_panels(filters)
            .with_panel(postgres_active_connections(filters))
        )
