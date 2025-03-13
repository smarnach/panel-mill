from grafana_foundation_sdk.builders.prometheus import Dataquery

from typing import Self


class LabelFilters:
    def __init__(self, *filters: str):
        self.filters = list(filters)

    def __str__(self):
        return "{{{}}}".format(", ".join(self.filters))

    def __add__(self, other: str | Self):
        if isinstance(other, str):
            return LabelFilters(*self.filters, other)
        return LabelFilters(*self.filters, *other.filters)


class PrometheusQuery(Dataquery):
    def __init__(self):
        super().__init__()
        self.range_val().editor_mode("builder").legend_format("__auto")

    def histogram_quantile(
        self, metric: str, filters: LabelFilters, quantile: float
    ) -> Self:
        sum_by_le = f"sum by(le) (increase({metric}{filters}[$__rate_interval]))"
        query = f"histogram_quantile({quantile}, {sum_by_le})"
        return self.expr(query).legend_format(f"{quantile * 100:g} %")

    def summary_quantiles(self, metric: str, filters: LabelFilters) -> Self:
        return self.expr(
            f"avg by(quantile) (avg_over_time({metric}{filters}[$__interval]))"
        )

    def utilization(self, metric: str, filters: LabelFilters) -> Self:
        return self.expr(f"max_over_time({metric}{filters}[$__interval])")

    def count(
        self, metric: str, filters: LabelFilters, by: list[str] | str | None = None
    ) -> Self:
        if isinstance(by, list):
            func = "sum by({}) ".format(", ".join(by))
        elif isinstance(by, str):
            func = f"sum by({by}) "
        else:
            func = "sum"
        return self.expr(f"{func}(increase({metric}{filters}[$__interval]))")

    def gauge(self, metric: str, filters: LabelFilters) -> Self:
        return self.expr(f"avg_over_time({metric}{filters}[$__interval])")
