"""Chart data preparation and scientific safeguards."""

from __future__ import annotations

import importlib.util
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .chart_models import AGGREGATIONS, CHART_TYPES, ChartConfig, PreparedChart
from .qsb_database import QSBMetadataDatabase


class ChartError(Exception):
    """Raised when chart configuration or data violate safeguards."""


def chart_engine_info() -> dict[str, str | bool]:
    spec = importlib.util.find_spec("matplotlib")
    if spec is None:
        return {
            "matplotlib_available": False,
            "matplotlib_version": "",
            "selected_chart_engine": "tkinter_canvas",
            "png_export_available": False,
            "svg_export_available": True,
        }
    os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="qsb_mpl_"))
    try:
        import matplotlib  # type: ignore

        version = matplotlib.__version__
    except Exception:
        return {
            "matplotlib_available": False,
            "matplotlib_version": "",
            "selected_chart_engine": "tkinter_canvas",
            "png_export_available": False,
            "svg_export_available": True,
        }
    return {
        "matplotlib_available": True,
        "matplotlib_version": version,
        "selected_chart_engine": "matplotlib",
        "png_export_available": True,
        "svg_export_available": True,
    }


def is_numeric(value: Any) -> bool:
    if value is None or value == "":
        return False
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def detect_numeric_fields(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    result = []
    for column in columns:
        values = [row.get(column) for row in rows if row.get(column) not in (None, "")]
        if values and all(is_numeric(value) for value in values[:100]):
            result.append(column)
    return result


def detect_categorical_fields(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    numeric = set(detect_numeric_fields(rows, columns))
    return [column for column in columns if column not in numeric]


def is_ordered_axis(field_name: str, rows: list[dict[str, Any]]) -> bool:
    lower = field_name.casefold()
    if any(token in lower for token in ("time", "index", "sequence", "order", "cycle", "phase", "created_at", "updated_at")):
        return True
    values = [row.get(field_name) for row in rows if row.get(field_name) is not None]
    return bool(values) and all(is_numeric(value) for value in values[:100])


def unit_metadata_for(database: QSBMetadataDatabase, fields: list[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    try:
        if "meta_field" not in database.list_tables():
            return metadata
        for field in fields:
            rows = database.execute_read_only(
                """
                SELECT canonical_field_name, unit_status, dimension_status, dimension_vector
                FROM meta_field
                WHERE canonical_field_name = ?
                LIMIT 1
                """,
                (field,),
            )
            if rows:
                row = rows[0]
                status = row["unit_status"] or "unresolved"
                metadata[field] = status if status != "unresolved" else "Unit unresolved"
    except Exception:
        return metadata
    return metadata


def dimension_metadata_for(database: QSBMetadataDatabase, fields: list[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    try:
        if "meta_field" not in database.list_tables():
            return metadata
        for field in fields:
            rows = database.execute_read_only(
                """
                SELECT canonical_field_name, dimension_status, dimension_vector
                FROM meta_field
                WHERE canonical_field_name = ?
                LIMIT 1
                """,
                (field,),
            )
            if rows:
                row = rows[0]
                metadata[field] = row["dimension_vector"] or row["dimension_status"] or "dimension unresolved"
    except Exception:
        return metadata
    return metadata


class ChartService:
    def __init__(self, database: QSBMetadataDatabase) -> None:
        self.database = database
        info = chart_engine_info()
        self.engine = str(info["selected_chart_engine"])

    def prepare(self, config: ChartConfig, quick_filter: str = "", filter_column: str = "", filter_value: str = "") -> PreparedChart:
        self._validate_config(config)
        page = self.database.load_relation_page(
            config.source_relation,
            offset=0,
            limit=min(config.max_rows, 10_000),
            quick_filter=quick_filter,
            filter_column=filter_column or None,
            filter_value=filter_value,
            include_tables=True,
        )
        if page.total_count > config.max_rows:
            warnings = [f"Row limit applied: {config.max_rows} of {page.total_count} rows used."]
        else:
            warnings = []
        rows, excluded = self._exclude_null_rows(page.rows, config)
        self._validate_scientific_safeguards(config, rows)
        x_values, y_values, categories = self._series(config, rows)
        y2_values: list[float] = []
        if config.y2_field:
            dims = dimension_metadata_for(self.database, [config.y_field, config.y2_field])
            if dims.get(config.y_field) != dims.get(config.y2_field):
                raise ChartError("Second y-series has incompatible or unresolved dimension metadata.")
            y2_values = [float(row[config.y2_field]) for row in rows if is_numeric(row.get(config.y2_field))]
        units = unit_metadata_for(self.database, [config.x_field, config.y_field, config.y2_field])
        dims = dimension_metadata_for(self.database, [config.x_field, config.y_field, config.y2_field])
        if any("unresolved" in value.casefold() for value in units.values()):
            warnings.append("Unit unresolved for at least one selected field.")
        return PreparedChart(
            config=config,
            rows=rows,
            x_values=x_values,
            y_values=y_values,
            y2_values=y2_values,
            categories=categories,
            warnings=warnings,
            excluded_null_rows=excluded,
            unit_metadata=units,
            dimension_metadata=dims,
            chart_engine=self.engine,
        )

    @staticmethod
    def _validate_config(config: ChartConfig) -> None:
        if config.chart_type not in CHART_TYPES:
            raise ChartError("Unsupported chart type.")
        if config.aggregation not in AGGREGATIONS:
            raise ChartError("Unsupported aggregation.")
        if config.max_rows > 10_000:
            raise ChartError("Plotting more than 10,000 rows requires an explicit smaller limit in this release.")

    @staticmethod
    def _exclude_null_rows(rows: list[dict[str, Any]], config: ChartConfig) -> tuple[list[dict[str, Any]], int]:
        fields = [config.x_field]
        if config.y_field:
            fields.append(config.y_field)
        if config.y2_field:
            fields.append(config.y2_field)
        kept = [row for row in rows if all(row.get(field) not in (None, "") for field in fields)]
        return kept, len(rows) - len(kept)

    def _validate_scientific_safeguards(self, config: ChartConfig, rows: list[dict[str, Any]]) -> None:
        if config.chart_type == "scatter":
            if not rows or not all(is_numeric(row.get(config.x_field)) and is_numeric(row.get(config.y_field)) for row in rows):
                raise ChartError("Scatter plot requires numeric x and y fields.")
        if config.chart_type == "histogram":
            if not rows or not all(is_numeric(row.get(config.x_field)) for row in rows):
                raise ChartError("Histogram requires one numeric field.")
        if config.chart_type == "pie":
            if config.y_field and any(float(row[config.y_field]) < 0 for row in rows if is_numeric(row.get(config.y_field))):
                raise ChartError("Pie chart values must be non-negative.")
            categories = {row.get(config.x_field) for row in rows}
            if len(categories) > 10:
                raise ChartError("Pie chart category count exceeds the default maximum of 10.")
        if config.chart_type == "line" and not is_ordered_axis(config.x_field, rows):
            raise ChartError("Line chart requires a meaningfully ordered x-axis.")

    def _series(self, config: ChartConfig, rows: list[dict[str, Any]]) -> tuple[list[Any], list[float], list[str]]:
        if config.aggregation == "none":
            x_values = [row.get(config.x_field) for row in rows]
            if config.chart_type == "histogram":
                y_values = [float(row[config.x_field]) for row in rows]
            elif config.y_field:
                y_values = [float(row[config.y_field]) for row in rows if is_numeric(row.get(config.y_field))]
            else:
                y_values = [1.0 for _row in rows]
            return x_values, y_values, [str(value) for value in x_values]
        grouped: dict[Any, list[float]] = defaultdict(list)
        for row in rows:
            key = row.get(config.group_field or config.x_field)
            if config.aggregation == "count":
                grouped[key].append(1.0)
            elif config.y_field and is_numeric(row.get(config.y_field)):
                grouped[key].append(float(row[config.y_field]))
        x_values = list(grouped)
        y_values = [aggregate(values, config.aggregation) for values in grouped.values()]
        return x_values, y_values, [str(value) for value in x_values]


def aggregate(values: list[float], mode: str) -> float:
    if mode == "count":
        return float(sum(values))
    if not values:
        return 0.0
    if mode == "sum":
        return float(sum(values))
    if mode == "mean":
        return float(sum(values) / len(values))
    if mode == "minimum":
        return float(min(values))
    if mode == "maximum":
        return float(max(values))
    return float(values[0])


def chart_presets(columns: list[str]) -> list[dict[str, str]]:
    colset = set(columns)
    presets = []
    candidates = [
        ("validation_by_status", "status", "count", "Validation results by status"),
        ("evidence_by_relation", "relation_type", "count", "Evidence relations by relation type"),
        ("fields_by_unit_status", "unit_status", "count", "Fields by unit status"),
        ("fields_by_dimension_status", "dimension_status", "count", "Fields by dimension status"),
        ("objects_by_work_package", "work_package_code", "count", "Objects by work package"),
        ("lineage_by_derivation", "derivation_class", "count", "Lineage edges by derivation class"),
        ("control_cycle_counts", "control_id", "detected_complete_cycle_count", "CAUSALITY07 control-cycle counts"),
        ("cycle_progression", "cycle_index", "cycle_duration", "CAUSALITY07 cycle progression"),
    ]
    for preset_id, x_field, y_field, title in candidates:
        if x_field in colset and (y_field == "count" or y_field in colset):
            presets.append({"id": preset_id, "x_field": x_field, "y_field": "" if y_field == "count" else y_field, "aggregation": "count" if y_field == "count" else "none", "title": title})
    return presets
