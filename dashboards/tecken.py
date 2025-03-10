from panel_mill.dashboard import Dashboard
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
            .app_metrics()
            .postgres_panels("symbols")
        )

    def app_metrics(self) -> Self:
        filters = LabelFilters('namespace="$namespace"')
        return (
            self.with_row(Row("Upload metrics"))
            .with_panel(
                self.histogram_timeseries_panel()
                .title("KEYPANEL: Upload request times")
                .unit("s")
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
                .unit("s")
                .with_summary_quantile_target("tecken_upload_file_upload", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Time to Upload by Download URL")
                .unit("s")
                .with_summary_quantile_target("tecken_upload_download_by_url", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Dump and extract zip file to disk")
                .unit("s")
                .with_summary_quantile_target("tecken_upload_dump_and_extract", filters)
            )

            .with_row(Row("Download metrics"))
            .with_panel(
                self.histogram_timeseries_panel()
                .title("KEYPANEL: Download requests times")
                .unit("s")
                .with_summary_quantile_target("tecken_download_symbol", filters)
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Download API code id lookup (count)")
                .with_count_target("tecken_download_symbol_code_id_lookup", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Age of downloaded files – regular storage")
                .unit("d")
                .with_summary_quantile_target(
                    "tecken_symboldownloader_file_age_days",
                    filters + 'storage="regular"',
                )
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Age of downloaded files – try storage")
                .unit("d")
                .with_summary_quantile_target(
                    "tecken_symboldownloader_file_age_days",
                    filters + 'storage="try"',
                )
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("SymbolDownloader timings")
                .unit("s")
                .with_summary_quantile_target("tecken_symboldownloader_exists", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Time to find out a symbol file size in object storage")
                .unit("s")
                .with_summary_quantile_target("tecken_upload_file_exists", filters)
            )

            .with_row(Row("Other application metrics"))
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Requests by operation")
                .with_count_target(
                    "tecken_download_symbol_count", filters, legend_format="downloads"
                )
                .with_count_target(
                    "tecken_upload_archive_count", filters, legend_format="uploads"
                )
                .with_count_target("tecken_api_count", filters, legend_format="API")
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Total time by operation")
                .unit("s")
                .with_count_target(
                    "tecken_download_symbol_sum", filters, legend_format="downloads"
                )
                .with_count_target(
                    "tecken_upload_archive_sum", filters, legend_format="uploads"
                )
                .with_count_target("tecken_api_sum", filters, legend_format="API")
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Total time by operation and pod")
                .unit("s")
                .with_count_target(
                    "tecken_download_symbol_sum",
                    filters,
                    legend_format="downloads",
                    by="pod",
                )
                .with_count_target(
                    "tecken_upload_archive_sum",
                    filters,
                    legend_format="uploads",
                    by="pod",
                )
                .with_count_target(
                    "tecken_api_sum", filters, legend_format="API", by="pod"
                )
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Time to compute upload stats")
                .unit("s")
                .with_summary_quantile_target("tecken_api_stats", filters)
            )
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("Orphaned files")
                .with_count_target("tecken_remove_orphaned_files_delete_file", filters)
            )
            .with_panel(
                self.histogram_timeseries_panel()
                .title("Time to remove orphaned files")
                .unit("s")
                .with_summary_quantile_target(
                    "tecken_remove_orphaned_files_timing", filters
                )
            )
            .with_panel(
                self.timeseries_panel()
                .title("Syminfo cache hits/misses")
                .with_count_target("tecken_syminfo_lookup_cached", filters, by="result")
                .override_by_name("false", [DynamicConfigValue("displayName", "miss")])
                .override_by_name("true", [DynamicConfigValue("displayName", "hit")])
            )

            .with_row(Row("Sentry"))
            .with_panel(
                self.stacked_count_timeseries_panel()
                .title("KEYPANEL: Sentry Scrub Errors")
                .with_count_target("tecken_sentry_scrub_error", filters)
            )
        )
