from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


@dataclass(slots=True)
class ControlDesignConfig:
    random_seed: int = 1729
    clip_min_zero: bool = True


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _require_columns(df: pd.DataFrame, columns: Sequence[str], *, df_name: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def _copy_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy().reset_index(drop=True)


def _clip_nonnegative(df: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = out[col].clip(lower=0.0)
    return out


def scale_feature(
    df: pd.DataFrame,
    *,
    column: str,
    factor: float,
    clip_min_zero: bool = True,
) -> pd.DataFrame:
    _require_columns(df, [column], df_name="feature dataframe")
    out = _copy_df(df)
    out[column] = out[column] * factor
    if clip_min_zero:
        out[column] = out[column].clip(lower=0.0)
    return out


def add_relative_noise(
    df: pd.DataFrame,
    *,
    column: str,
    pct: float,
    seed: int = 1729,
    clip_min_zero: bool = True,
) -> pd.DataFrame:
    """
    Add multiplicative relative noise:
        x -> x * (1 + eps), eps ~ Uniform[-pct, +pct]
    """
    _require_columns(df, [column], df_name="feature dataframe")
    if pct < 0:
        raise ValueError("pct must be >= 0")

    out = _copy_df(df)
    rng = _rng(seed)
    eps = rng.uniform(-pct, pct, size=len(out))
    out[column] = out[column] * (1.0 + eps)

    if clip_min_zero:
        out[column] = out[column].clip(lower=0.0)
    return out


def set_control_family(
    df: pd.DataFrame,
    *,
    control_family: str,
    label_prefix: str | None = None,
) -> pd.DataFrame:
    out = _copy_df(df)

    if "control_family" in out.columns:
        out["control_family"] = control_family
    else:
        out.insert(len(out.columns), "control_family", control_family)

    if "label_internal" in out.columns:
        prefix = label_prefix or control_family
        out["label_internal"] = [f"{prefix}_{i+1:03d}" for i in range(len(out))]

    if "group_target" in out.columns:
        out["group_target"] = "control"

    return out


def build_grid_disrupted_control(
    base_df: pd.DataFrame,
    *,
    control_family: str = "K1a",
    grid_scale: float = 1.30,
    grid_noise_pct: float = 0.10,
    seed: int = 1729,
) -> pd.DataFrame:
    """
    Increase grid_deviation_score while keeping the rest comparatively close.
    """
    _require_columns(base_df, ["grid_deviation_score"], df_name="base_df")
    out = scale_feature(
        base_df,
        column="grid_deviation_score",
        factor=grid_scale,
    )
    out = add_relative_noise(
        out,
        column="grid_deviation_score",
        pct=grid_noise_pct,
        seed=seed,
    )
    out = set_control_family(out, control_family=control_family, label_prefix=control_family)
    return out


def build_rigidity_disrupted_control(
    base_df: pd.DataFrame,
    *,
    control_family: str = "K2a",
    rigidity_scale: float = 0.70,
    rigidity_noise_pct: float = 0.10,
    seed: int = 1729,
) -> pd.DataFrame:
    """
    Reduce simple_rigidity_surrogate while keeping other features comparatively stable.
    """
    _require_columns(base_df, ["simple_rigidity_surrogate"], df_name="base_df")
    out = scale_feature(
        base_df,
        column="simple_rigidity_surrogate",
        factor=rigidity_scale,
    )
    out = add_relative_noise(
        out,
        column="simple_rigidity_surrogate",
        pct=rigidity_noise_pct,
        seed=seed,
    )
    out = set_control_family(out, control_family=control_family, label_prefix=control_family)
    return out


def build_coupled_structural_disruption_control(
    base_df: pd.DataFrame,
    *,
    control_family: str = "K3a",
    grid_scale: float = 1.30,
    rigidity_scale: float = 0.70,
    grid_noise_pct: float = 0.10,
    rigidity_noise_pct: float = 0.10,
    seed: int = 1729,
) -> pd.DataFrame:
    """
    Increase grid deviation and reduce rigidity simultaneously.
    """
    _require_columns(
        base_df,
        ["grid_deviation_score", "simple_rigidity_surrogate"],
        df_name="base_df",
    )
    out = scale_feature(
        base_df,
        column="grid_deviation_score",
        factor=grid_scale,
    )
    out = scale_feature(
        out,
        column="simple_rigidity_surrogate",
        factor=rigidity_scale,
    )
    out = add_relative_noise(
        out,
        column="grid_deviation_score",
        pct=grid_noise_pct,
        seed=seed,
    )
    out = add_relative_noise(
        out,
        column="simple_rigidity_surrogate",
        pct=rigidity_noise_pct,
        seed=seed + 1,
    )
    out = set_control_family(out, control_family=control_family, label_prefix=control_family)
    return out


def build_mixed_decoupling_control(
    base_df: pd.DataFrame,
    *,
    control_family: str = "K4a",
    distance_scale: float = 1.00,
    spacing_scale: float = 1.15,
    grid_scale: float = 1.25,
    rigidity_scale: float = 0.75,
    noise_pct: float = 0.10,
    seed: int = 1729,
) -> pd.DataFrame:
    """
    Keep distance_to_type_D broadly plausible while decoupling the quantitative/structural block.
    """
    _require_columns(
        base_df,
        [
            "distance_to_type_D",
            "spacing_cv",
            "grid_deviation_score",
            "simple_rigidity_surrogate",
        ],
        df_name="base_df",
    )

    out = scale_feature(
        base_df,
        column="distance_to_type_D",
        factor=distance_scale,
    )
    out = scale_feature(
        out,
        column="spacing_cv",
        factor=spacing_scale,
    )
    out = scale_feature(
        out,
        column="grid_deviation_score",
        factor=grid_scale,
    )
    out = scale_feature(
        out,
        column="simple_rigidity_surrogate",
        factor=rigidity_scale,
    )

    out = add_relative_noise(
        out,
        column="distance_to_type_D",
        pct=noise_pct,
        seed=seed,
    )
    out = add_relative_noise(
        out,
        column="spacing_cv",
        pct=noise_pct,
        seed=seed + 1,
    )
    out = add_relative_noise(
        out,
        column="grid_deviation_score",
        pct=noise_pct,
        seed=seed + 2,
    )
    out = add_relative_noise(
        out,
        column="simple_rigidity_surrogate",
        pct=noise_pct,
        seed=seed + 3,
    )

    out = set_control_family(out, control_family=control_family, label_prefix=control_family)
    return out


def stack_controls(control_dfs: Sequence[pd.DataFrame]) -> pd.DataFrame:
    if not control_dfs:
        raise ValueError("control_dfs must not be empty")
    return pd.concat(control_dfs, axis=0, ignore_index=True)


def build_adversarial_control_suite(
    base_df: pd.DataFrame,
    *,
    seed: int = 1729,
) -> pd.DataFrame:
    """
    Convenience builder for a first adversarial suite:
    K1a, K2a, K3a, K4a
    """
    k1a = build_grid_disrupted_control(base_df, control_family="K1a", seed=seed)
    k2a = build_rigidity_disrupted_control(base_df, control_family="K2a", seed=seed + 10)
    k3a = build_coupled_structural_disruption_control(base_df, control_family="K3a", seed=seed + 20)
    k4a = build_mixed_decoupling_control(base_df, control_family="K4a", seed=seed + 30)
    return stack_controls([k1a, k2a, k3a, k4a])