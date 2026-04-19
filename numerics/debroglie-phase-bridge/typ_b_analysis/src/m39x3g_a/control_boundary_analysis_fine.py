from __future__ import annotations

from dataclasses import asdict
from typing import Sequence

import pandas as pd

from src.m39x3g_a.control_boundary_analysis import (
    scan_k2a_rigidity_boundary,
    scan_k3a_coupled_boundary,
)
from src.m39x3g_a.resampling import TypeBRuleConfig


def _default_type_b_rules() -> TypeBRuleConfig:
    return TypeBRuleConfig()


def build_fine_boundary_scan(
    *,
    original_df: pd.DataFrame,
    base_df: pd.DataFrame,
    feature_columns: Sequence[str],
    n_resamples: int = 100,
    seed: int = 1729,
    distance_metric: str = "euclidean",
    rules: TypeBRuleConfig | None = None,
) -> pd.DataFrame:
    """
    Focused follow-up scan around the currently most relevant regions:
    - K2a: finer rigidity sweep
    - K3a: finer coupled sweep around the strongest observed region
    """
    if rules is None:
        rules = _default_type_b_rules()

    df_k2 = scan_k2a_rigidity_boundary(
        original_df=original_df,
        base_df=base_df,
        feature_columns=feature_columns,
        rigidity_scales=(0.75, 0.70, 0.65, 0.60, 0.55),
        rigidity_noise_pct=0.10,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
        rules=rules,
    )

    df_k3 = scan_k3a_coupled_boundary(
        original_df=original_df,
        base_df=base_df,
        feature_columns=feature_columns,
        grid_scales=(1.25, 1.30, 1.35),
        rigidity_scales=(0.80, 0.75, 0.70),
        grid_noise_pct=0.10,
        rigidity_noise_pct=0.10,
        n_resamples=n_resamples,
        seed=seed + 100,
        distance_metric=distance_metric,
        rules=rules,
    )

    out = pd.concat([df_k2, df_k3], axis=0, ignore_index=True)
    return out.sort_values(
        by=[
            "type_B_like_pattern_detected",
            "stability_score_mean",
            "separation_margin_mean",
            "assignment_score_mean",
        ],
        ascending=[False, False, False, False],
        ignore_index=True,
    )
