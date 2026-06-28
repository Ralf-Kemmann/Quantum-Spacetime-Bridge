"""Export prepared charts and chart datasets."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

from .chart_models import PreparedChart
from .config import APP_VERSION


def chart_manifest(chart: PreparedChart, snapshot_manifest: dict, export_path: Path, displayed_labels: dict[str, str]) -> dict:
    return {
        "application_version": APP_VERSION,
        "export_timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_snapshot_path": snapshot_manifest.get("snapshot_path", ""),
        "source_snapshot_sha256": snapshot_manifest.get("snapshot_sha256", ""),
        "source_table_or_view": chart.config.source_relation,
        "active_filters": {},
        "chart_type": chart.config.chart_type,
        "canonical_x_field": chart.config.x_field,
        "canonical_y_fields": [field for field in [chart.config.y_field, chart.config.y2_field] if field],
        "displayed_field_labels": displayed_labels,
        "aggregation": chart.config.aggregation,
        "group_field": chart.config.group_field,
        "sort_order": chart.config.sort_order,
        "plotted_row_count": len(chart.rows),
        "excluded_row_count": chart.excluded_null_rows,
        "unit_metadata": chart.unit_metadata,
        "dimension_metadata": chart.dimension_metadata,
        "selected_language": chart.config.language,
        "chart_title": chart.config.title,
        "chart_engine": chart.chart_engine,
        "export_path": str(export_path),
    }


def export_plotted_csv(path: Path, chart: PreparedChart) -> Path:
    columns = list(chart.rows[0].keys()) if chart.rows else [chart.config.x_field, chart.config.y_field]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in chart.rows:
            writer.writerow({column: row.get(column, "") for column in columns})
    return path


def write_chart_manifest(path: Path, chart: PreparedChart, snapshot_manifest: dict, displayed_labels: dict[str, str]) -> Path:
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest_path.write_text(
        json.dumps(chart_manifest(chart, snapshot_manifest, path, displayed_labels), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path
