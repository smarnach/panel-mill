from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.promql import LabelFilters
from panel_mill.queries import PrometheusQuery

from grafana_foundation_sdk.builders.dashboard import CustomVariable, Row
from grafana_foundation_sdk.models.dashboard import VariableHide

from typing import Self


class ClousSQLMixin(Dashboard):
    def cloud_sql_utilization(self, filters: LabelFilters, resource: str) -> Timeseries:
        metric = f"cloudsql_googleapis_com:database_{resource.lower()}_utilization"
        return (
            self.utilization_timeseries_panel()
            .title(f"{resource} utilization")
            .with_utilization_target(metric, filters, legend_format="{{database_id}}")
        )

    def cloud_sql_disk_iops(self, filters: LabelFilters, mode: str) -> Timeseries:
        metric = f"cloudsql_googleapis_com:database_disk_{mode}_ops_count"
        query = f"rate({metric}{filters}[$__rate_interval])"
        return (
            self.timeseries_panel()
            .title(f"Disk {mode} IO")
            .unit("iops")
            .with_target(PrometheusQuery().expr(query).legend_format("{{database_id}}"))
        )

    def cloud_sql_network_bytes(
        self, filters: LabelFilters, direction: str
    ) -> Timeseries:
        metric = f"cloudsql_googleapis_com:database_network_{direction}_bytes_count"
        query = f"rate({metric}{filters}[$__rate_interval])"
        return (
            self.timeseries_panel()
            .title(f"Network {direction} bytes")
            .unit("Bps")
            .with_target(PrometheusQuery().expr(query).legend_format("{{database_id}}"))
        )

    def cloud_sql_instance_variable(
        self,
        database_id: str = "$project_id:$tenant-$env-${env:text}-v1",
        variable: str = "database_id",
    ) -> Self:
        return self.with_variable(
            CustomVariable(variable)
            .values(database_id)
            .hide(VariableHide.HIDE_VARIABLE)
        )

    def cloud_sql_panels(self, filters: LabelFilters) -> Self:
        return (
            self.with_panel(self.cloud_sql_utilization(filters, "CPU"))
            .with_panel(self.cloud_sql_utilization(filters, "Memory"))
            .with_panel(self.cloud_sql_disk_iops(filters, "read"))
            .with_panel(self.cloud_sql_disk_iops(filters, "write"))
            .with_panel(self.cloud_sql_network_bytes(filters, "received"))
            .with_panel(self.cloud_sql_network_bytes(filters, "sent"))
            .with_panel(self.cloud_sql_utilization(filters, "Disk"))
        )


class PostgresMixin(ClousSQLMixin):
    def postgres_active_connections(self, filters: LabelFilters) -> Timeseries:
        metric = "cloudsql_googleapis_com:database_postgresql_num_backends"
        query = f"sum by(database_id) (max_over_time({metric}{filters}[$__interval]))"
        return (
            self.timeseries_panel()
            .title("Active connections")
            .with_target(PrometheusQuery().expr(query).legend_format("{{database_id}}"))
        )

    def postgres_panels(self, database_id: str = "$database_id") -> Self:
        filters = LabelFilters(f'database_id="{database_id}"')
        return (
            self.with_row(Row("Cloud SQL (Postgres)"))
            .cloud_sql_panels(filters)
            .with_panel(self.postgres_active_connections(filters))
        )
