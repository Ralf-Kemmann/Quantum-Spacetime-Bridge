from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd


@dataclass(slots=True)
class CalibrationSummary:
    original_margin_median: float
    original_margin_std: float
    suggested_original_separation_margin_min: float

    control_delta_quantile_q: float
    suggested_min_original_over_control_margin_delta: float

    notes: list[str]


def _as_array(values: Sequence[float], *, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        raise ValueError(f"{name} must not be empty")
    if np.isnan(arr).any():
        raise ValueError(f"{name} contains NaN values")
    return arr


def calibrate_reference_thresholds(
    *,
    original_margins: Sequence[float],
    control_deltas: Sequence[float],
    control_quantile_q: float = 0.90,
) -> CalibrationSummary:
    """
    Calibrate reference thresholds from observed original and control values.

    Rules:
    - original separation margin threshold:
        median(original_margins) + std(original_margins)
    - relative advantage threshold:
        quantile(control_deltas, control_quantile_q)
    """
    if not (0.0 <= control_quantile_q <= 1.0):
        raise ValueError("control_quantile_q must satisfy 0.0 <= q <= 1.0")

    original_arr = _as_array(original_margins, name="original_margins")
    control_arr = _as_array(control_deltas, name="control_deltas")

    original_margin_median = float(np.median(original_arr))
    original_margin_std = float(np.std(original_arr, ddof=0))
    suggested_original_separation_margin_min = original_margin_median + original_margin_std

    suggested_min_original_over_control_margin_delta = float(
        np.quantile(control_arr, control_quantile_q)
    )

    notes = [
        "Suggested original separation margin threshold = median(original_margins) + std(original_margins).",
        f"Suggested relative-advantage threshold = q{control_quantile_q:.2f}(control_deltas).",
        "These are calibration values, not final physical constants.",
    ]

    return CalibrationSummary(
        original_margin_median=original_margin_median,
        original_margin_std=original_margin_std,
        suggested_original_separation_margin_min=suggested_original_separation_margin_min,
        control_delta_quantile_q=control_quantile_q,
        suggested_min_original_over_control_margin_delta=suggested_min_original_over_control_margin_delta,
        notes=notes,
    )


def calibrate_from_dataframe(
    *,
    df: pd.DataFrame,
    original_margin_column: str,
    control_delta_column: str,
    control_quantile_q: float = 0.90,
) -> CalibrationSummary:
    if original_margin_column not in df.columns:
        raise ValueError(f"missing column: {original_margin_column}")
    if control_delta_column not in df.columns:
        raise ValueError(f"missing column: {control_delta_column}")

    return calibrate_reference_thresholds(
        original_margins=df[original_margin_column].dropna().tolist(),
        control_deltas=df[control_delta_column].dropna().tolist(),
        control_quantile_q=control_quantile_q,
    )