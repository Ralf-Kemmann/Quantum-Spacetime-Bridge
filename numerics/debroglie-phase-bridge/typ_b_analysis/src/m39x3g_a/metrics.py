from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances

from src.m39x3g_a.models import DiagnosticRowModel


# ---------------------------------------------------------------------------
# Small internal helpers
# ---------------------------------------------------------------------------


def _as_float(value: float | np.floating) -> float:
    return float(value)


def _require_columns(df: pd.DataFrame, columns: Sequence[str], *, df_name: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def _numeric_feature_matrix(df: pd.DataFrame, feature_columns: Sequence[str]) -> np.ndarray:
    _require_columns(df, feature_columns, df_name="feature dataframe")
    if len(df) == 0:
        raise ValueError("feature dataframe is empty")
    x = df.loc[:, feature_columns].to_numpy(dtype=float, copy=True)
    if np.isnan(x).any():
        raise ValueError("feature matrix contains NaN values")
    return x


def _strict_upper_triangle_values(matrix: np.ndarray) -> np.ndarray:
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("matrix must be square")
    n = matrix.shape[0]
    if n < 2:
        return np.array([], dtype=float)
    idx = np.triu_indices(n, k=1)
    return matrix[idx]


def _mean_or_nan(values: np.ndarray) -> float:
    if values.size == 0:
        return float("nan")
    return _as_float(np.mean(values))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return float("inf")
    return numerator / denominator


# ---------------------------------------------------------------------------
# Metric containers
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class DistanceSummary:
    n_left: int
    n_right: int
    mean_intra_left: float
    mean_intra_right: float
    pooled_intra_distance: float
    mean_inter_distance: float
    separation_margin: float
    separation_ratio: float


@dataclass(slots=True)
class AssignmentSummary:
    assignment_score: float


# ---------------------------------------------------------------------------
# Core distance computations
# ---------------------------------------------------------------------------


def compute_intra_group_mean_distance(
    df: pd.DataFrame,
    feature_columns: Sequence[str],
    *,
    distance_metric: str = "euclidean",
) -> float:
    """
    Mean pairwise intra-group distance using the strict upper triangle.

    Returns NaN for groups with fewer than 2 rows.
    """
    x = _numeric_feature_matrix(df, feature_columns)
    d = pairwise_distances(x, metric=distance_metric)
    vals = _strict_upper_triangle_values(d)
    return _mean_or_nan(vals)


def compute_inter_group_mean_distance(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    *,
    distance_metric: str = "euclidean",
) -> float:
    """
    Mean pairwise inter-group distance across all left-right pairs.
    """
    x_left = _numeric_feature_matrix(left_df, feature_columns)
    x_right = _numeric_feature_matrix(right_df, feature_columns)
    d = pairwise_distances(x_left, x_right, metric=distance_metric)
    if d.size == 0:
        return float("nan")
    return _as_float(np.mean(d))


def compute_distance_summary(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    *,
    distance_metric: str = "euclidean",
) -> DistanceSummary:
    """
    Compute the core separation metrics used in M.3.9x.3g.a.
    """
    mean_intra_left = compute_intra_group_mean_distance(
        left_df,
        feature_columns,
        distance_metric=distance_metric,
    )
    mean_intra_right = compute_intra_group_mean_distance(
        right_df,
        feature_columns,
        distance_metric=distance_metric,
    )
    mean_inter_distance = compute_inter_group_mean_distance(
        left_df,
        right_df,
        feature_columns,
        distance_metric=distance_metric,
    )

    pooled_intra_distance = _as_float(np.nanmean([mean_intra_left, mean_intra_right]))
    separation_margin = mean_inter_distance - pooled_intra_distance
    separation_ratio = _safe_ratio(mean_inter_distance, pooled_intra_distance)

    return DistanceSummary(
        n_left=len(left_df),
        n_right=len(right_df),
        mean_intra_left=mean_intra_left,
        mean_intra_right=mean_intra_right,
        pooled_intra_distance=pooled_intra_distance,
        mean_inter_distance=mean_inter_distance,
        separation_margin=separation_margin,
        separation_ratio=separation_ratio,
    )


# ---------------------------------------------------------------------------
# Simple assignment score
# ---------------------------------------------------------------------------


def compute_nearest_centroid_assignment_score(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    *,
    distance_metric: str = "euclidean",
) -> float:
    """
    Simple diagnostic assignment score based on nearest centroid classification.

    Each row is assigned to the closer of the two group centroids.
    Returns the overall fraction of correctly assigned rows.
    """
    x_left = _numeric_feature_matrix(left_df, feature_columns)
    x_right = _numeric_feature_matrix(right_df, feature_columns)

    left_centroid = np.mean(x_left, axis=0, keepdims=True)
    right_centroid = np.mean(x_right, axis=0, keepdims=True)

    d_left_to_left = pairwise_distances(x_left, left_centroid, metric=distance_metric).ravel()
    d_left_to_right = pairwise_distances(x_left, right_centroid, metric=distance_metric).ravel()

    d_right_to_left = pairwise_distances(x_right, left_centroid, metric=distance_metric).ravel()
    d_right_to_right = pairwise_distances(x_right, right_centroid, metric=distance_metric).ravel()

    left_correct = np.sum(d_left_to_left <= d_left_to_right)
    right_correct = np.sum(d_right_to_right <= d_right_to_left)

    total = len(x_left) + len(x_right)
    if total == 0:
        raise ValueError("cannot compute assignment score for two empty groups")

    return _as_float((left_correct + right_correct) / total)


def compute_assignment_summary(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    *,
    distance_metric: str = "euclidean",
) -> AssignmentSummary:
    score = compute_nearest_centroid_assignment_score(
        left_df,
        right_df,
        feature_columns,
        distance_metric=distance_metric,
    )
    return AssignmentSummary(assignment_score=score)


# ---------------------------------------------------------------------------
# Combined helpers for diagnostics output
# ---------------------------------------------------------------------------


def compute_comparison_metrics(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    *,
    distance_metric: str = "euclidean",
) -> dict[str, float]:
    """
    Returns a plain dict with the core numeric comparison metrics.
    """
    distance_summary = compute_distance_summary(
        left_df,
        right_df,
        feature_columns,
        distance_metric=distance_metric,
    )
    assignment_summary = compute_assignment_summary(
        left_df,
        right_df,
        feature_columns,
        distance_metric=distance_metric,
    )

    return {
        "n_left": distance_summary.n_left,
        "n_right": distance_summary.n_right,
        "mean_intra_left": distance_summary.mean_intra_left,
        "mean_intra_right": distance_summary.mean_intra_right,
        "pooled_intra_distance": distance_summary.pooled_intra_distance,
        "mean_inter_distance": distance_summary.mean_inter_distance,
        "separation_margin": distance_summary.separation_margin,
        "separation_ratio": distance_summary.separation_ratio,
        "assignment_score": assignment_summary.assignment_score,
    }


def build_diagnostic_row(
    *,
    run_id: str,
    feature_space_version: str,
    decision_rule_version: str,
    control_family: str,
    comparison_id: str,
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    stability_score: float,
    type_B_like_pattern_detected: bool,
    interpretation: str,
    distance_metric: str = "euclidean",
    warning_flag: bool = False,
    notes: str = "",
) -> DiagnosticRowModel:
    """
    Build a validated DiagnosticRowModel from two dataframes.
    """
    metrics = compute_comparison_metrics(
        left_df,
        right_df,
        feature_columns,
        distance_metric=distance_metric,
    )

    return DiagnosticRowModel(
        run_id=run_id,
        block_id="M.3.9x.3g.a",
        feature_space_version=feature_space_version,
        decision_rule_version=decision_rule_version,
        source_group_left="original",
        source_group_right="control",
        control_family=control_family,
        comparison_id=comparison_id,
        n_left=int(metrics["n_left"]),
        n_right=int(metrics["n_right"]),
        mean_intra_left=float(metrics["mean_intra_left"]),
        mean_intra_right=float(metrics["mean_intra_right"]),
        pooled_intra_distance=float(metrics["pooled_intra_distance"]),
        mean_inter_distance=float(metrics["mean_inter_distance"]),
        separation_margin=float(metrics["separation_margin"]),
        separation_ratio=float(metrics["separation_ratio"]),
        stability_score=float(stability_score),
        assignment_score=float(metrics["assignment_score"]),
        type_B_like_pattern_detected=type_B_like_pattern_detected,
        interpretation=interpretation,
        warning_flag=warning_flag,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Filtering helpers
# ---------------------------------------------------------------------------


def subset_by_group_target(df: pd.DataFrame, group_target: str) -> pd.DataFrame:
    _require_columns(df, ["group_target"], df_name="manifest/features dataframe")
    return df.loc[df["group_target"] == group_target].copy()


def subset_by_control_family(df: pd.DataFrame, control_family: str) -> pd.DataFrame:
    _require_columns(df, ["control_family"], df_name="manifest/features dataframe")
    return df.loc[df["control_family"] == control_family].copy()