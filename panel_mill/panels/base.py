from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.common import StackingConfig, VizLegendOptions
from grafana_foundation_sdk.builders.prometheus import Dataquery as PrometheusQuery
from grafana_foundation_sdk.builders.timeseries import Panel
from grafana_foundation_sdk.models.dashboard import DataSourceRef

from typing import Self


class Timeseries(Panel):
    def __init__(self):
        super().__init__()
        self.datasource(DataSourceRef("prometheus", "$datasource")).axis_soft_min(0)

    def with_histogram_quantile_targets(
        self,
        metric: str,
        filters: LabelFilters,
        quantiles: list[float] = [0.5, 0.95, 0.99],
    ) -> Self:
        self.fill_opacity(10)
        sum_by_le = f"sum by(le) (increase({metric}{filters}[$__rate_interval]))"
        for quantile in quantiles:
            query = f"histogram_quantile({quantile}, {sum_by_le})"
            self.with_target(
                PrometheusQuery().expr(query).legend_format(f"{quantile * 100:g} %")
            )
        return self

    def with_summary_quantile_target(self, metric: str, filters: LabelFilters):
        self.fill_opacity(10)
        query = f"avg by(quantile) (avg_over_time({metric}{filters}[$__interval]))"
        self.with_target(PrometheusQuery().expr(query).legend_format("__auto"))
        return self

    def with_utilization_target(
        self, metric: str, filters: LabelFilters, legend_format: str = "__auto"
    ):
        self.axis_soft_max(1)
        self.unit("percentunit")
        query = f"max_over_time({metric}{filters}[$__interval])"
        self.with_target(PrometheusQuery().expr(query).legend_format(legend_format))
        return self

    def with_count_target(
        self,
        metric: str,
        filters: LabelFilters,
        by: list[str] | str | None = None,
        legend_format: str = "__auto",
    ):
        self.draw_style("bars")
        self.stacking(StackingConfig().mode(("normal")))
        self.legend(VizLegendOptions().show_legend(True).calcs(["sum"]))
        if isinstance(by, list):
            query = "sum by({}) ".format(", ".join(by))
        elif isinstance(by, str):
            query = f"sum by({by}) "
        else:
            query = "sum"
        query += f"(increase({metric}{filters}[$__interval]))"
        self.with_target(PrometheusQuery().expr(query).legend_format(legend_format))
        return self
