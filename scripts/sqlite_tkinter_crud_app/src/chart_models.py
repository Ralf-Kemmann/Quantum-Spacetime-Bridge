"""Chart configuration and prepared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CHART_TYPES = ("bar", "line", "scatter", "pie", "histogram")
AGGREGATIONS = ("none", "count", "sum", "mean", "minimum", "maximum")


@dataclass(frozen=True)
class ChartConfig:
    source_relation: str
    chart_type: str
    x_field: str
    y_field: str = ""
    y2_field: str = ""
    group_field: str = ""
    aggregation: str = "none"
    sort_order: str = "source"
    max_rows: int = 2000
    title: str = ""
    x_label: str = ""
    y_label: str = ""
    show_legend: bool = True
    missing_values: str = "exclude"
    language: str = "de"


@dataclass(frozen=True)
class PreparedChart:
    config: ChartConfig
    rows: list[dict[str, Any]]
    x_values: list[Any]
    y_values: list[float]
    y2_values: list[float] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    excluded_null_rows: int = 0
    unit_metadata: dict[str, str] = field(default_factory=dict)
    dimension_metadata: dict[str, str] = field(default_factory=dict)
    chart_engine: str = "canvas"
