from panel_mill.dashboard import Dashboard
from panel_mill.panels.base import Timeseries
from panel_mill.panels.cloud_sql import PostgresMixin
from panel_mill.panels.gclb import GCLBMixin
from panel_mill.panels.kubernetes import KubernetesMixin
from panel_mill.promql import LabelFilters

from grafana_foundation_sdk.builders.dashboard import Row
from grafana_foundation_sdk.models.dashboard import DynamicConfigValue

from typing import Self


class TeckenDashboard(GCLBMixin, KubernetesMixin, PostgresMixin, Dashboard):
    def __init__(self):
        super().__init__("Test dashboard: Tecken GCP")
        (
            self.uid("sven-tecken-gcp-test")
            .time("now-1d", "now")
            .default_variables("symbols")
            .gclb_panels(
                project_id="moz-fx-webservices-low-$env",
                forwarding_rule_regex=".*symbols-${env:text}-tecken.*",
            )
            .k8s_panels(
                job="tecken",
                pod_name_regex="tecken-[^-]+-[^-]+",
                volume_names=["uploads"],
                container="tecken",
            )
            .upload_metrics()
            .postgres_panels("symbols")
        )

    def upload_metrics(self) -> Self:
        filters = LabelFilters('namespace="$namespace"')
        return (
            self.with_row(Row("Upload metrics"))
            .with_panel(
                self.histogram_timeseries_panel()
                .title("KEYPANEL: Upload request times")
                .with_summary_quantile_target("tecken_upload_archive", filters)
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Count of uploads")
                .with_count_target("tecken_upload_uploads", filters, by="try")
                .override_by_name(
                    "False", [DynamicConfigValue("displayName", "regular")]
                )
                .override_by_name("True", [DynamicConfigValue("displayName", "try")])
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("File uploads and skips")
                .with_count_target(
                    "tecken_upload_file_upload_upload", filters, legend_format="uploads"
                )
                .with_count_target(
                    "tecken_upload_file_upload_skip", filters, legend_format="skips"
                )
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Skip uploads early counts")
                .with_count_target(
                    "tecken_upload_skip_early_compressed",
                    filters,
                    legend_format="compressed",
                )
                .with_count_target(
                    "tecken_upload_skip_early_uncompressed",
                    filters,
                    legend_format="uncompressed",
                )
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Time to  upload individual symbols file to GCS")
                .with_summary_quantile_target("tecken_upload_file_upload", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Time to Upload by Download URL")
                .with_summary_quantile_target("tecken_upload_download_by_url", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Dump and extract zip file to disk")
                .with_summary_quantile_target("tecken_upload_dump_and_extract", filters)
            )
        )
