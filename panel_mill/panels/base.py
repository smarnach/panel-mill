from panel_mill.promql import LabelFilters
from panel_mill.queries import PrometheusQuery

from grafana_foundation_sdk.builders.timeseries import Panel
from grafana_foundation_sdk.models.dashboard import DataSourceRef

from typing import Self


class Timeseries(Panel):
    def __init__(self):
        super().__init__()
        self.datasource(DataSourceRef("prometheus", "$datasource"))

    def with_histogram_quantile_targets(
        self,
        metric: str,
        filters: LabelFilters,
        quantiles: list[float] = [0.5, 0.95, 0.99],
    ) -> Self:
        for quantile in quantiles:
            self.with_target(
                PrometheusQuery().histogram_quantile(metric, filters, quantile)
            )
        return self

    def with_summary_quantile_target(self, metric: str, filters: LabelFilters) -> Self:
        return self.with_target(PrometheusQuery().summary_quantiles(metric, filters))

    def with_utilization_target(
        self, metric: str, filters: LabelFilters, legend_format: str = "__auto"
    ) -> Self:
        return self.with_target(
            PrometheusQuery().utilization(metric, filters).legend_format(legend_format)
        )

    def with_count_target(
        self,
        metric: str,
        filters: LabelFilters,
        by: list[str] | str | None = None,
        legend_format: str = "__auto",
    ) -> Self:
        return self.with_target(
            PrometheusQuery().count(metric, filters, by).legend_format(legend_format)
        )

    def with_gauge_target(
        self, metric: str, filters: LabelFilters, legend_format: str = "__auto"
    ) -> Self:
        return self.with_target(
            PrometheusQuery().gauge(metric, filters).legend_format(legend_format)
        )
