from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from src.m39x3g_a.metrics import compute_comparison_metrics


@dataclass(slots=True)
class OriginalReferenceSummary:
    fsw_n_rows: int
    ao_n_rows: int
    separation_margin_mean: float
    separation_margin_ci: tuple[float, float] | None
    separation_ratio_mean: float
    assignment_score_mean: float
    stability_score: float


def _bootstrap_sample(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if len(df) == 0:
        raise ValueError("cannot resample empty dataframe")
    idx = rng.integers(0, len(df), size=len(df))
    return df.iloc[idx].reset_index(drop=True)


def _quantile_ci(values: list[float], alpha: float = 0.95) -> tuple[float, float] | None:
    if not values:
        return None
    lower_q = (1.0 - alpha) / 2.0
    upper_q = 1.0 - lower_q
    arr = np.asarray(values, dtype=float)
    return (float(np.quantile(arr, lower_q)), float(np.quantile(arr, upper_q)))


def _filter_by_labels(df: pd.DataFrame, labels: Sequence[str]) -> pd.DataFrame:
    if "label_internal" not in df.columns:
        raise ValueError("original dataframe is missing column 'label_internal'")
    out = df.loc[df["label_internal"].isin(labels)].copy()
    if len(out) == 0:
        raise ValueError(f"no rows matched labels: {list(labels)}")
    return out


def bootstrap_original_reference(
    *,
    original_df: pd.DataFrame,
    fsw_labels: Sequence[str],
    ao_labels: Sequence[str],
    feature_columns: Sequence[str],
    n_resamples: int = 1000,
    seed: int = 1729,
    distance_metric: str = "euclidean",
    min_assignment_for_positive: float = 0.75,
    min_margin_for_positive: float = 0.05,
) -> OriginalReferenceSummary:
    """
    Bootstrap the original FSW-vs-AO reference comparison.

    stability_score:
        fraction of resamples with
        separation_margin >= min_margin_for_positive
        and assignment_score >= min_assignment_for_positive
    """
    if n_resamples < 1:
        raise ValueError("n_resamples must be >= 1")

    fsw_df = _filter_by_labels(original_df, fsw_labels)
    ao_df = _filter_by_labels(original_df, ao_labels)

    rng = np.random.default_rng(seed)

    separation_margins: list[float] = []
    separation_ratios: list[float] = []
    assignment_scores: list[float] = []
    positives = 0

    for _ in range(n_resamples):
        fsw_sample = _bootstrap_sample(fsw_df, rng)
        ao_sample = _bootstrap_sample(ao_df, rng)

        metrics = compute_comparison_metrics(
            fsw_sample,
            ao_sample,
            feature_columns,
            distance_metric=distance_metric,
        )

        separation_margin = float(metrics["separation_margin"])
        separation_ratio = float(metrics["separation_ratio"])
        assignment_score = float(metrics["assignment_score"])

        if (
            separation_margin >= min_margin_for_positive
            and assignment_score >= min_assignment_for_positive
        ):
            positives += 1

        separation_margins.append(separation_margin)
        separation_ratios.append(separation_ratio)
        assignment_scores.append(assignment_score)

    return OriginalReferenceSummary(
        fsw_n_rows=int(len(fsw_df)),
        ao_n_rows=int(len(ao_df)),
        separation_margin_mean=float(np.mean(separation_margins)),
        separation_margin_ci=_quantile_ci(separation_margins),
        separation_ratio_mean=float(np.mean(separation_ratios)),
        assignment_score_mean=float(np.mean(assignment_scores)),
        stability_score=float(positives / n_resamples),
    )