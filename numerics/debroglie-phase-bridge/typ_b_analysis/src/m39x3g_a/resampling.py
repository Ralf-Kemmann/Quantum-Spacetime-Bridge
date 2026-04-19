from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from src.m39x3g_a.metrics import compute_comparison_metrics
from src.m39x3g_a.models import ResamplingRowModel


@dataclass(slots=True)
class TypeBRuleConfig:
    """Operational Type-B consistency rules (provisional v1)."""

    distance_to_type_D_min: float = 0.15
    distance_to_type_D_max: float = 0.45

    spacing_cv_min: float = 0.20
    spacing_cv_max: float = 0.60

    grid_deviation_score_min: float = 0.05
    grid_deviation_score_max: float = 0.30

    simple_rigidity_surrogate_min: float = 0.40

    separation_margin_min: float = 0.20
    assignment_score_min: float = 0.75

    stability_score_min: float = 0.80
    separation_margin_ci_low_min: float = 0.05


@dataclass(slots=True)
class ResamplingSummary:
    stability_score: float
    separation_margin_mean: float
    separation_margin_ci: tuple[float, float] | None
    separation_ratio_mean: float
    assignment_score_mean: float
    type_B_like_pattern_detected: bool
    rows: list[ResamplingRowModel]


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


def _mean_feature(df: pd.DataFrame, feature_name: str) -> float:
    if feature_name not in df.columns:
        raise ValueError(f"missing feature column: {feature_name}")
    return float(df[feature_name].mean())


def _quantitative_core_ok(
    *,
    distance_to_type_D: float,
    spacing_cv: float,
    separation_margin: float,
    rules: TypeBRuleConfig,
) -> bool:
    return (
        rules.distance_to_type_D_min <= distance_to_type_D <= rules.distance_to_type_D_max
        and rules.spacing_cv_min <= spacing_cv <= rules.spacing_cv_max
        and separation_margin >= rules.separation_margin_min
    )


def _structural_consistency_ok(
    *,
    grid_deviation_score: float,
    simple_rigidity_surrogate: float,
    rules: TypeBRuleConfig,
) -> bool:
    return (
        rules.grid_deviation_score_min <= grid_deviation_score <= rules.grid_deviation_score_max
        and simple_rigidity_surrogate >= rules.simple_rigidity_surrogate_min
    )


def _resample_type_b_positive(
    *,
    distance_to_type_D: float,
    spacing_cv: float,
    grid_deviation_score: float,
    simple_rigidity_surrogate: float,
    separation_margin: float,
    assignment_score: float,
    rules: TypeBRuleConfig,
) -> bool:
    return (
        _quantitative_core_ok(
            distance_to_type_D=distance_to_type_D,
            spacing_cv=spacing_cv,
            separation_margin=separation_margin,
            rules=rules,
        )
        and _structural_consistency_ok(
            grid_deviation_score=grid_deviation_score,
            simple_rigidity_surrogate=simple_rigidity_surrogate,
            rules=rules,
        )
        and assignment_score >= rules.assignment_score_min
    )


def bootstrap_comparison(
    *,
    run_id: str,
    control_family: str,
    comparison_id: str,
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    feature_columns: Sequence[str],
    n_resamples: int = 1000,
    seed: int = 1729,
    distance_metric: str = "euclidean",
    rules: TypeBRuleConfig | None = None,
) -> ResamplingSummary:
    """
    Bootstrap left/right groups and estimate stability of the separation signal.

    Per-resample positive condition:
    - quantitative_core_ok
    - structural_consistency_ok
    - assignment_score >= rules.assignment_score_min

    Global type_B_like_pattern_detected condition:
    - stability_score >= rules.stability_score_min
    - lower CI bound of separation_margin >= rules.separation_margin_ci_low_min
    - mean separation_margin >= rules.separation_margin_min
    """
    if n_resamples < 1:
        raise ValueError("n_resamples must be >= 1")

    if rules is None:
        rules = TypeBRuleConfig()

    rng = np.random.default_rng(seed)
    rows: list[ResamplingRowModel] = []

    separation_margins: list[float] = []
    separation_ratios: list[float] = []
    assignment_scores: list[float] = []
    positives = 0

    for resample_id in range(1, n_resamples + 1):
        left_sample = _bootstrap_sample(left_df, rng)
        right_sample = _bootstrap_sample(right_df, rng)

        metrics = compute_comparison_metrics(
            left_sample,
            right_sample,
            feature_columns,
            distance_metric=distance_metric,
        )

        separation_margin = float(metrics["separation_margin"])
        separation_ratio = float(metrics["separation_ratio"])
        assignment_score = float(metrics["assignment_score"])

        distance_to_type_D_mean = _mean_feature(right_sample, "distance_to_type_D")
        spacing_cv_mean = _mean_feature(right_sample, "spacing_cv")
        grid_deviation_score_mean = _mean_feature(right_sample, "grid_deviation_score")
        simple_rigidity_surrogate_mean = _mean_feature(right_sample, "simple_rigidity_surrogate")

        is_positive = _resample_type_b_positive(
            distance_to_type_D=distance_to_type_D_mean,
            spacing_cv=spacing_cv_mean,
            grid_deviation_score=grid_deviation_score_mean,
            simple_rigidity_surrogate=simple_rigidity_surrogate_mean,
            separation_margin=separation_margin,
            assignment_score=assignment_score,
            rules=rules,
        )

        if is_positive:
            positives += 1

        separation_margins.append(separation_margin)
        separation_ratios.append(separation_ratio)
        assignment_scores.append(assignment_score)

        rows.append(
            ResamplingRowModel(
                run_id=run_id,
                block_id="M.3.9x.3g.a",
                control_family=control_family,
                comparison_id=comparison_id,
                resample_id=resample_id,
                resample_scheme="bootstrap",
                seed=seed,
                n_left=int(metrics["n_left"]),
                n_right=int(metrics["n_right"]),
                mean_intra_left=float(metrics["mean_intra_left"]),
                mean_intra_right=float(metrics["mean_intra_right"]),
                pooled_intra_distance=float(metrics["pooled_intra_distance"]),
                mean_inter_distance=float(metrics["mean_inter_distance"]),
                separation_margin=separation_margin,
                separation_ratio=separation_ratio,
                assignment_score=assignment_score,
                type_B_like_pattern_detected=is_positive,
                warning_flag=False,
            )
        )

    stability_score = positives / n_resamples
    separation_margin_mean = float(np.mean(separation_margins))
    separation_margin_ci = _quantile_ci(separation_margins)
    ci_low = separation_margin_ci[0] if separation_margin_ci is not None else None

    type_B_like_pattern_detected = (
        stability_score >= rules.stability_score_min
        and ci_low is not None
        and ci_low >= rules.separation_margin_ci_low_min
        and separation_margin_mean >= rules.separation_margin_min
    )

    return ResamplingSummary(
        stability_score=float(stability_score),
        separation_margin_mean=separation_margin_mean,
        separation_margin_ci=separation_margin_ci,
        separation_ratio_mean=float(np.mean(separation_ratios)),
        assignment_score_mean=float(np.mean(assignment_scores)),
        type_B_like_pattern_detected=type_B_like_pattern_detected,
        rows=rows,
    )
