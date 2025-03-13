from panel_mill.dashboard import Dashboard
from panel_mill.panels.gclb import GCLBMixin
from panel_mill.panels.kubernetes import KubernetesMixin
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.dashboard import Row

from typing import Self


class EliotDashboard(GCLBMixin, KubernetesMixin, Dashboard):
    def __init__(self):
        super().__init__("Test dashboard: Eliot")
        (
            self.uid("sven-eliot-test")
            .time("now-1d", "now")
            .default_variables(
                tenant="symbols", function="webservices", risk_level="low"
            )
            .gclb_panels(
                forwarding_rule_regex=".*symbols-${env:text}-eliot.*",
            )
            .k8s_panels(
                job="eliot",
                pod_name_regex="eliot-[^-]+-[^-]+",
                volume_names=["scratch"],
                container="eliot",
            )
            .app_metrics()
        )

    def app_metrics(self) -> Self:
        filters = LabelFilters('namespace="$namespace"')
        return (
            self.with_row(Row("Aplication metrics"))
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Symbolication API requests by version")
                .with_count_target("eliot_symbolicate_api_count", filters, by="version")
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Request errors")
                .description("No data means no errors.")
                .with_count_target(
                    "eliot_symbolicate_request_error", filters, by="reason"
                )
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Symbolication API timings")
                .unit("s")
                .with_summary_quantile_target("eliot_symbolicate_api", filters)
            )
            .with_panel(
                self.timeseries_panel()
                .title("Disk cache usage by pod")
                .unit("decbytes")
                .with_gauge_target(
                    "eliot_diskcache_usage", filters, legend_format="{{pod}}"
                )
            )
            .with_panel(
                self.timeseries_panel()
                .title("Disk cache churn (set vs. evict)")
                .with_count_target(
                    "eliot_diskcache_set_count", filters, legend_format="set"
                )
                .with_count_target(
                    "eliot_diskcache_evict_count", filters, legend_format="evict"
                )
            )
            .with_panel(
                self.timeseries_panel()
                .title("Disk cache hits/misses")
                .with_count_target("eliot_diskcache_get_count", filters, by="result")
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("SYM parse timings")
                .unit("s")
                .with_summary_quantile_target(
                    "eliot_symbolicate_parse_sym_file_parse", filters
                )
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("SYM download timings")
                .unit("ms")
                .with_summary_quantile_target("eliot_downloader_download", filters)
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("SYM parse error count")
                .description("No data means no errors.")
                .with_count_target("eliot_symbolicate_parse_sym_file_error", filters)
            )
            .with_row(Row("Sentry"))
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("KEYPANEL: Sentry scrub errors")
                .description("No data means no errors.")
                .with_count_target("eliot_sentry_scrub_error", filters)
            )
        )
