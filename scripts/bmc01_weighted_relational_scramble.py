#!/usr/bin/env python3
from __future__ import annotations

"""
BMC-01 — Weighted Relational Scramble Probe

Upgraded scaffold with arrangement-sensitive readouts.

This version keeps the original transparent structure but extends the readout
layer beyond pure weight-distribution summaries. It now includes:

- endpoint-load arrangement metrics
- local-group arrangement metrics
- shell-placement arrangement metrics
- pair-to-neighborhood consistency metrics

It also downgrades the decision logic so that intervention-positive but
readout-blind runs are not over-read as "marker_supported".

Expected minimal input table columns:
- pair_id
- endpoint_a
- endpoint_b
- weight

Optional grouping/control columns:
- local_group
- shell_label
"""

import argparse
import csv
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


ALLOWED_VARIANTS = {
    "global_weight_permutation",
    "within_shell_weight_permutation",
    "within_local_group_weight_permutation",
}

ALLOWED_STRENGTHS = {"low", "medium", "high"}

STRENGTH_FRACTIONS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 1.00,
}


@dataclass
class RunConfig:
    block_identifier: str
    block_title: str
    intervention_family: str
    intervention_variant: str
    intervention_strength: str
    preserve_topology: bool
    preserve_shell_membership: bool
    preserve_global_weight_distribution: bool
    random_seed: int
    replicate_count: int


@dataclass
class BaselineState:
    run_id: str
    source_label: str
    framework_label: str
    pair_count: int
    node_count: int
    baseline_weight_mean: float
    baseline_weight_std: float
    baseline_weight_min: float
    baseline_weight_max: float


@dataclass
class BridgeReadout:
    bridge_signal_score: float
    d1_d2_separation_score: float
    weighted_relational_contrast_score: float
    endpoint_load_shift_score: float
    endpoint_load_dispersion_shift_score: float
    local_group_arrangement_shift_score: float
    shell_arrangement_shift_score: float
    pair_neighborhood_consistency_shift_score: float
    arrangement_signal_score: float
    readability_label: str


@dataclass
class DecisionSummary:
    decision_label: str
    marker_support_level: float
    carrier_support_level: float
    test_informativeness: str
    primary_reason: str
    secondary_reason: str
    topology_preservation_status: str
    geometry_surrogate_preservation_status: str
    weighted_relational_disruption_status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BMC-01 Weighted Relational Scramble Probe"
    )
    parser.add_argument("--input", required=True, help="Path to baseline_relational_table.csv")
    parser.add_argument("--output-dir", required=True, help="Run output directory")
    parser.add_argument("--variant", required=True, choices=sorted(ALLOWED_VARIANTS))
    parser.add_argument("--strength", required=True, choices=sorted(ALLOWED_STRENGTHS))
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--source-label", default="unspecified_source")
    parser.add_argument("--framework-label", default="pair_based_h3")
    parser.add_argument("--replicate-count", type=int, default=1)
    return parser.parse_args()


def ensure_required_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def safe_std(series: pd.Series) -> float:
    if len(series) <= 1:
        return 0.0
    value = float(series.std(ddof=0))
    if math.isnan(value):
        return 0.0
    return value


def compute_baseline_state(
    df: pd.DataFrame,
    run_id: str,
    source_label: str,
    framework_label: str,
) -> BaselineState:
    weights = df["weight"].astype(float)
    nodes = set(df["endpoint_a"].astype(str)).union(set(df["endpoint_b"].astype(str)))
    return BaselineState(
        run_id=run_id,
        source_label=source_label,
        framework_label=framework_label,
        pair_count=int(len(df)),
        node_count=int(len(nodes)),
        baseline_weight_mean=float(weights.mean()) if len(weights) else 0.0,
        baseline_weight_std=safe_std(weights),
        baseline_weight_min=float(weights.min()) if len(weights) else 0.0,
        baseline_weight_max=float(weights.max()) if len(weights) else 0.0,
    )


def permute_subset(values: list[float], rng: random.Random, fraction: float) -> list[float]:
    n = len(values)
    if n <= 1:
        return values.copy()
    k = max(2, int(round(n * fraction)))
    k = min(k, n)
    idx = list(range(n))
    chosen = rng.sample(idx, k)
    chosen_values = [values[i] for i in chosen]
    rng.shuffle(chosen_values)

    out = values.copy()
    for original_idx, new_value in zip(chosen, chosen_values):
        out[original_idx] = new_value
    return out


def apply_intervention(df: pd.DataFrame, variant: str, strength: str, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    fraction = STRENGTH_FRACTIONS[strength]
    out = df.copy()
    out["baseline_weight"] = out["weight"].astype(float)

    if variant == "global_weight_permutation":
        permuted = permute_subset(out["weight"].astype(float).tolist(), rng, fraction)
        out["weight"] = permuted
        out["intervention_group"] = "global"

    elif variant == "within_shell_weight_permutation":
        if "shell_label" not in out.columns:
            raise ValueError("Variant within_shell_weight_permutation requires column shell_label")
        out["intervention_group"] = out["shell_label"].astype(str)
        idx_and_weights: list[tuple[int, float]] = []
        for _, sub in out.groupby("intervention_group", sort=False):
            permuted = permute_subset(sub["weight"].astype(float).tolist(), rng, fraction)
            idx_and_weights.extend(zip(sub.index.tolist(), permuted))
        for idx, w in idx_and_weights:
            out.at[idx, "weight"] = w

    elif variant == "within_local_group_weight_permutation":
        if "local_group" not in out.columns:
            raise ValueError("Variant within_local_group_weight_permutation requires column local_group")
        out["intervention_group"] = out["local_group"].astype(str)
        idx_and_weights = []
        for _, sub in out.groupby("intervention_group", sort=False):
            permuted = permute_subset(sub["weight"].astype(float).tolist(), rng, fraction)
            idx_and_weights.extend(zip(sub.index.tolist(), permuted))
        for idx, w in idx_and_weights:
            out.at[idx, "weight"] = w

    else:
        raise ValueError(f"Unsupported variant: {variant}")

    out["weight"] = out["weight"].astype(float)
    out["weight_delta"] = out["weight"] - out["baseline_weight"].astype(float)
    out["weight_changed_flag"] = out["weight_delta"].abs() > 1e-12
    return out


def similarity_preserved_fraction(before: pd.Series, after: pd.Series) -> float:
    if len(before) == 0:
        return 1.0
    unchanged = (
        before.astype(str).reset_index(drop=True)
        == after.astype(str).reset_index(drop=True)
    ).sum()
    return float(unchanged / len(before))


def compute_endpoint_loads(df: pd.DataFrame, weight_col: str = "weight") -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        w = float(row[weight_col])
        rows.append((str(row["endpoint_a"]), w))
        rows.append((str(row["endpoint_b"]), w))
    endpoint_df = pd.DataFrame(rows, columns=["endpoint", "weight"])
    summary = endpoint_df.groupby("endpoint", as_index=False)["weight"].sum()
    summary.rename(columns={"weight": "endpoint_total_weight"}, inplace=True)
    return summary


def compute_local_group_means(df: pd.DataFrame, weight_col: str = "weight") -> pd.DataFrame:
    if "local_group" not in df.columns:
        return pd.DataFrame(columns=["local_group", "group_mean_weight", "group_weight_std"])
    grouped = (
        df.groupby("local_group", as_index=False)[weight_col]
        .agg(group_mean_weight="mean", group_weight_std=lambda s: safe_std(pd.Series(s)))
    )
    grouped["local_group"] = grouped["local_group"].astype(str)
    return grouped


def compute_shell_pair_rank_score(df: pd.DataFrame, weight_col: str = "weight") -> pd.DataFrame:
    if "shell_label" not in df.columns:
        return pd.DataFrame(columns=["pair_id", "shell_label", "shell_weight_rank"])
    tmp = df[["pair_id", "shell_label", weight_col]].copy()
    tmp["pair_id"] = tmp["pair_id"].astype(str)
    tmp["shell_label"] = tmp["shell_label"].astype(str)
    tmp["shell_weight_rank"] = (
        tmp.groupby("shell_label")[weight_col]
        .rank(method="average", ascending=False)
        .astype(float)
    )
    return tmp[["pair_id", "shell_label", "shell_weight_rank"]]


def compute_pair_neighborhood_consistency(df: pd.DataFrame, weight_col: str = "weight") -> pd.DataFrame:
    work = df.copy()
    work["weight_used"] = work[weight_col].astype(float)
    endpoint_loads = compute_endpoint_loads(work, "weight_used").rename(
        columns={"endpoint_total_weight": "endpoint_total"}
    )

    merged_a = work.merge(
        endpoint_loads.rename(columns={"endpoint": "endpoint_a", "endpoint_total": "endpoint_a_total"}),
        on="endpoint_a",
        how="left",
    )
    merged_ab = merged_a.merge(
        endpoint_loads.rename(columns={"endpoint": "endpoint_b", "endpoint_total": "endpoint_b_total"}),
        on="endpoint_b",
        how="left",
    )
    merged_ab["pair_neighborhood_context"] = (
        merged_ab["endpoint_a_total"].astype(float) + merged_ab["endpoint_b_total"].astype(float)
    ) / 2.0
    merged_ab["pair_neighborhood_consistency"] = (
        merged_ab["weight_used"].astype(float) - merged_ab["pair_neighborhood_context"].astype(float)
    ).abs()
    return merged_ab[["pair_id", "pair_neighborhood_context", "pair_neighborhood_consistency"]]


def compute_arrangement_features(df: pd.DataFrame, weight_col: str = "weight") -> dict[str, float]:
    endpoint_loads = compute_endpoint_loads(df, weight_col)
    endpoint_load_mean = float(endpoint_loads["endpoint_total_weight"].mean()) if len(endpoint_loads) else 0.0
    endpoint_load_dispersion = safe_std(endpoint_loads["endpoint_total_weight"]) if len(endpoint_loads) else 0.0

    local_group_df = compute_local_group_means(df, weight_col)
    local_group_mean_dispersion = safe_std(local_group_df["group_mean_weight"]) if len(local_group_df) else 0.0

    shell_rank_df = compute_shell_pair_rank_score(df, weight_col)
    shell_rank_mean = float(shell_rank_df["shell_weight_rank"].mean()) if len(shell_rank_df) else 0.0

    pair_consistency_df = compute_pair_neighborhood_consistency(df, weight_col)
    pair_neighborhood_consistency_mean = (
        float(pair_consistency_df["pair_neighborhood_consistency"].mean()) if len(pair_consistency_df) else 0.0
    )

    return {
        "endpoint_load_mean": endpoint_load_mean,
        "endpoint_load_dispersion": endpoint_load_dispersion,
        "local_group_mean_dispersion": local_group_mean_dispersion,
        "shell_rank_mean": shell_rank_mean,
        "pair_neighborhood_consistency_mean": pair_neighborhood_consistency_mean,
    }


def arrangement_delta_score(
    baseline_df: pd.DataFrame,
    perturbed_df: pd.DataFrame,
    key_cols: list[str],
    value_col: str,
) -> float:
    if len(baseline_df) == 0 or len(perturbed_df) == 0:
        return 0.0
    merged = baseline_df.merge(
        perturbed_df,
        on=key_cols,
        suffixes=("_baseline", "_perturbed"),
        how="inner",
    )
    if len(merged) == 0:
        return 0.0
    delta = (
        merged[f"{value_col}_perturbed"].astype(float)
        - merged[f"{value_col}_baseline"].astype(float)
    ).abs()
    return float(delta.mean())


def compute_bridge_readout(
    baseline_df: pd.DataFrame,
    current_df: pd.DataFrame,
) -> BridgeReadout:
    """
    Readout now combines:
    - value-distribution summaries
    - arrangement-sensitive summaries
    """
    weights = current_df["weight"].astype(float)
    mean_w = float(weights.mean()) if len(weights) else 0.0
    std_w = safe_std(weights)

    if abs(mean_w) > 1e-12:
        bridge_signal_score = abs(std_w / mean_w)
    else:
        bridge_signal_score = std_w

    q10 = float(weights.quantile(0.10)) if len(weights) else 0.0
    q90 = float(weights.quantile(0.90)) if len(weights) else 0.0
    d1_d2_separation_score = q90 - q10

    weighted_relational_contrast_score = float((weights - mean_w).abs().mean()) if len(weights) else 0.0

    baseline_endpoint = compute_endpoint_loads(baseline_df, "weight")
    current_endpoint = compute_endpoint_loads(current_df, "weight")
    endpoint_load_shift_score = arrangement_delta_score(
        baseline_endpoint,
        current_endpoint,
        ["endpoint"],
        "endpoint_total_weight",
    )

    baseline_endpoint_disp = safe_std(baseline_endpoint["endpoint_total_weight"]) if len(baseline_endpoint) else 0.0
    current_endpoint_disp = safe_std(current_endpoint["endpoint_total_weight"]) if len(current_endpoint) else 0.0
    endpoint_load_dispersion_shift_score = abs(current_endpoint_disp - baseline_endpoint_disp)

    baseline_local = compute_local_group_means(baseline_df, "weight")
    current_local = compute_local_group_means(current_df, "weight")
    local_group_arrangement_shift_score = arrangement_delta_score(
        baseline_local,
        current_local,
        ["local_group"],
        "group_mean_weight",
    )

    baseline_shell_rank = compute_shell_pair_rank_score(baseline_df, "weight")
    current_shell_rank = compute_shell_pair_rank_score(current_df, "weight")
    shell_arrangement_shift_score = arrangement_delta_score(
        baseline_shell_rank,
        current_shell_rank,
        ["pair_id", "shell_label"],
        "shell_weight_rank",
    )

    baseline_pair_consistency = compute_pair_neighborhood_consistency(baseline_df, "weight")
    current_pair_consistency = compute_pair_neighborhood_consistency(current_df, "weight")
    pair_neighborhood_consistency_shift_score = arrangement_delta_score(
        baseline_pair_consistency,
        current_pair_consistency,
        ["pair_id"],
        "pair_neighborhood_consistency",
    )

    arrangement_signal_score = (
        endpoint_load_shift_score
        + endpoint_load_dispersion_shift_score
        + local_group_arrangement_shift_score
        + shell_arrangement_shift_score
        + pair_neighborhood_consistency_shift_score
    ) / 5.0

    if arrangement_signal_score >= 0.15:
        readability_label = "arrangement_sensitive"
    elif bridge_signal_score >= 0.50 and d1_d2_separation_score > 0:
        readability_label = "readable"
    elif bridge_signal_score >= 0.20:
        readability_label = "weakly_readable"
    else:
        readability_label = "blurred"

    return BridgeReadout(
        bridge_signal_score=bridge_signal_score,
        d1_d2_separation_score=d1_d2_separation_score,
        weighted_relational_contrast_score=weighted_relational_contrast_score,
        endpoint_load_shift_score=endpoint_load_shift_score,
        endpoint_load_dispersion_shift_score=endpoint_load_dispersion_shift_score,
        local_group_arrangement_shift_score=local_group_arrangement_shift_score,
        shell_arrangement_shift_score=shell_arrangement_shift_score,
        pair_neighborhood_consistency_shift_score=pair_neighborhood_consistency_shift_score,
        arrangement_signal_score=arrangement_signal_score,
        readability_label=readability_label,
    )


def compute_control_shell_comparison(
    baseline_df: pd.DataFrame,
    perturbed_df: pd.DataFrame,
    variant: str,
) -> pd.DataFrame:
    topology_similarity_score = 1.0
    global_weight_distribution_similarity_score = 1.0

    if "shell_label" in baseline_df.columns and "shell_label" in perturbed_df.columns:
        shell_preservation_score = similarity_preserved_fraction(
            baseline_df["shell_label"],
            perturbed_df["shell_label"],
        )
    else:
        shell_preservation_score = 1.0

    if "local_group" in baseline_df.columns and "local_group" in perturbed_df.columns:
        local_group_preservation_score = similarity_preserved_fraction(
            baseline_df["local_group"],
            perturbed_df["local_group"],
        )
    else:
        local_group_preservation_score = 1.0

    geometry_surrogate_similarity_score = 0.5

    rows = [
        ("topology_similarity_score", topology_similarity_score),
        ("geometry_surrogate_similarity_score", geometry_surrogate_similarity_score),
        ("global_weight_distribution_similarity_score", global_weight_distribution_similarity_score),
        ("local_group_preservation_score", local_group_preservation_score),
        ("shell_preservation_score", shell_preservation_score),
        ("variant", variant),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def build_readout_comparison(
    baseline_readout: BridgeReadout,
    perturbed_readout: BridgeReadout,
) -> pd.DataFrame:
    rows = [
        ("baseline_bridge_signal_score", baseline_readout.bridge_signal_score),
        ("perturbed_bridge_signal_score", perturbed_readout.bridge_signal_score),
        ("delta_bridge_signal_score", perturbed_readout.bridge_signal_score - baseline_readout.bridge_signal_score),
        ("baseline_d1_d2_separation_score", baseline_readout.d1_d2_separation_score),
        ("perturbed_d1_d2_separation_score", perturbed_readout.d1_d2_separation_score),
        ("delta_d1_d2_separation_score", perturbed_readout.d1_d2_separation_score - baseline_readout.d1_d2_separation_score),
        ("baseline_weighted_relational_contrast_score", baseline_readout.weighted_relational_contrast_score),
        ("perturbed_weighted_relational_contrast_score", perturbed_readout.weighted_relational_contrast_score),
        ("delta_weighted_relational_contrast_score", perturbed_readout.weighted_relational_contrast_score - baseline_readout.weighted_relational_contrast_score),
        ("baseline_endpoint_load_shift_score", baseline_readout.endpoint_load_shift_score),
        ("perturbed_endpoint_load_shift_score", perturbed_readout.endpoint_load_shift_score),
        ("delta_endpoint_load_shift_score", perturbed_readout.endpoint_load_shift_score - baseline_readout.endpoint_load_shift_score),
        ("baseline_endpoint_load_dispersion_shift_score", baseline_readout.endpoint_load_dispersion_shift_score),
        ("perturbed_endpoint_load_dispersion_shift_score", perturbed_readout.endpoint_load_dispersion_shift_score),
        ("delta_endpoint_load_dispersion_shift_score", perturbed_readout.endpoint_load_dispersion_shift_score - baseline_readout.endpoint_load_dispersion_shift_score),
        ("baseline_local_group_arrangement_shift_score", baseline_readout.local_group_arrangement_shift_score),
        ("perturbed_local_group_arrangement_shift_score", perturbed_readout.local_group_arrangement_shift_score),
        ("delta_local_group_arrangement_shift_score", perturbed_readout.local_group_arrangement_shift_score - baseline_readout.local_group_arrangement_shift_score),
        ("baseline_shell_arrangement_shift_score", baseline_readout.shell_arrangement_shift_score),
        ("perturbed_shell_arrangement_shift_score", perturbed_readout.shell_arrangement_shift_score),
        ("delta_shell_arrangement_shift_score", perturbed_readout.shell_arrangement_shift_score - baseline_readout.shell_arrangement_shift_score),
        ("baseline_pair_neighborhood_consistency_shift_score", baseline_readout.pair_neighborhood_consistency_shift_score),
        ("perturbed_pair_neighborhood_consistency_shift_score", perturbed_readout.pair_neighborhood_consistency_shift_score),
        ("delta_pair_neighborhood_consistency_shift_score", perturbed_readout.pair_neighborhood_consistency_shift_score - baseline_readout.pair_neighborhood_consistency_shift_score),
        ("baseline_arrangement_signal_score", baseline_readout.arrangement_signal_score),
        ("perturbed_arrangement_signal_score", perturbed_readout.arrangement_signal_score),
        ("delta_arrangement_signal_score", perturbed_readout.arrangement_signal_score - baseline_readout.arrangement_signal_score),
        ("baseline_readability_label", baseline_readout.readability_label),
        ("perturbed_readability_label", perturbed_readout.readability_label),
    ]
    return pd.DataFrame(rows, columns=["field", "value"])


def make_decision_summary(
    perturbed_df: pd.DataFrame,
    perturbed_readout: BridgeReadout,
    control_shell_df: pd.DataFrame,
) -> DecisionSummary:
    control_map = dict(zip(control_shell_df["metric"], control_shell_df["value"]))
    topology_similarity = float(control_map.get("topology_similarity_score", 0.0))
    geometry_similarity = float(control_map.get("geometry_surrogate_similarity_score", 0.0))

    changed_fraction = float(perturbed_df["weight_changed_flag"].mean()) if len(perturbed_df) else 0.0
    arrangement_signal = float(perturbed_readout.arrangement_signal_score)

    if topology_similarity < 0.90:
        return DecisionSummary(
            decision_label="test_not_informative",
            marker_support_level=0.0,
            carrier_support_level=0.0,
            test_informativeness="low",
            primary_reason="Topology changed too strongly for BMC-01 interpretation.",
            secondary_reason="Intervention no longer isolates weighted-relational role sufficiently.",
            topology_preservation_status="failed",
            geometry_surrogate_preservation_status="unclear",
            weighted_relational_disruption_status="unclear",
        )

    if changed_fraction >= 0.25 and arrangement_signal < 1e-9:
        return DecisionSummary(
            decision_label="test_not_informative",
            marker_support_level=0.0,
            carrier_support_level=0.0,
            test_informativeness="low",
            primary_reason="Intervention changed pair-level weight placement, but the readout layer remained arrangement-blind.",
            secondary_reason="This run cannot distinguish marker from carrier because the readout did not register the structural reassignment.",
            topology_preservation_status="passed",
            geometry_surrogate_preservation_status="placeholder_partial",
            weighted_relational_disruption_status="passed",
        )

    if arrangement_signal >= 0.15 and geometry_similarity >= 0.40:
        carrier_support = min(1.0, arrangement_signal)
        marker_support = max(0.0, 1.0 - carrier_support)
        return DecisionSummary(
            decision_label="carrier_leaning",
            marker_support_level=round(marker_support, 6),
            carrier_support_level=round(carrier_support, 6),
            test_informativeness="medium",
            primary_reason="Arrangement-sensitive readouts changed under weighted-relational intervention while the coarse shell remained broadly stable.",
            secondary_reason="This pattern is more compatible with carrier-leaning behavior than with a purely diagnostic marker reading.",
            topology_preservation_status="passed",
            geometry_surrogate_preservation_status="placeholder_partial",
            weighted_relational_disruption_status="passed",
        )

    return DecisionSummary(
        decision_label="undecided",
        marker_support_level=0.5,
        carrier_support_level=0.5,
        test_informativeness="medium",
        primary_reason="The intervention was real, but the arrangement-sensitive response is not yet decisive.",
        secondary_reason="Additional readouts or intervention families are needed before stronger marker–carrier conclusions are warranted.",
        topology_preservation_status="passed",
        geometry_surrogate_preservation_status="placeholder_partial",
        weighted_relational_disruption_status="passed",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_markdown_readout(
    path: Path,
    cfg: RunConfig,
    baseline_state: BaselineState,
    baseline_readout: BridgeReadout,
    perturbed_readout: BridgeReadout,
    decision: DecisionSummary,
) -> None:
    text = f"""# BMC-01 Block Readout

## Run identity

- Run ID: `{baseline_state.run_id}`
- Block: `{cfg.block_identifier}`
- Title: `{cfg.block_title}`
- Variant: `{cfg.intervention_variant}`
- Strength: `{cfg.intervention_strength}`
- Seed: `{cfg.random_seed}`

## Baseline description

- Source label: `{baseline_state.source_label}`
- Framework label: `{baseline_state.framework_label}`
- Pair count: `{baseline_state.pair_count}`
- Node count: `{baseline_state.node_count}`
- Baseline weight mean: `{baseline_state.baseline_weight_mean:.6f}`
- Baseline weight std: `{baseline_state.baseline_weight_std:.6f}`

## Baseline readout

- Bridge signal score: `{baseline_readout.bridge_signal_score:.6f}`
- D1/D2 separation score: `{baseline_readout.d1_d2_separation_score:.6f}`
- Weighted relational contrast score: `{baseline_readout.weighted_relational_contrast_score:.6f}`
- Endpoint load shift score: `{baseline_readout.endpoint_load_shift_score:.6f}`
- Endpoint load dispersion shift score: `{baseline_readout.endpoint_load_dispersion_shift_score:.6f}`
- Local group arrangement shift score: `{baseline_readout.local_group_arrangement_shift_score:.6f}`
- Shell arrangement shift score: `{baseline_readout.shell_arrangement_shift_score:.6f}`
- Pair-to-neighborhood consistency shift score: `{baseline_readout.pair_neighborhood_consistency_shift_score:.6f}`
- Arrangement signal score: `{baseline_readout.arrangement_signal_score:.6f}`
- Readability label: `{baseline_readout.readability_label}`

## Perturbed readout

- Bridge signal score: `{perturbed_readout.bridge_signal_score:.6f}`
- D1/D2 separation score: `{perturbed_readout.d1_d2_separation_score:.6f}`
- Weighted relational contrast score: `{perturbed_readout.weighted_relational_contrast_score:.6f}`
- Endpoint load shift score: `{perturbed_readout.endpoint_load_shift_score:.6f}`
- Endpoint load dispersion shift score: `{perturbed_readout.endpoint_load_dispersion_shift_score:.6f}`
- Local group arrangement shift score: `{perturbed_readout.local_group_arrangement_shift_score:.6f}`
- Shell arrangement shift score: `{perturbed_readout.shell_arrangement_shift_score:.6f}`
- Pair-to-neighborhood consistency shift score: `{perturbed_readout.pair_neighborhood_consistency_shift_score:.6f}`
- Arrangement signal score: `{perturbed_readout.arrangement_signal_score:.6f}`
- Readability label: `{perturbed_readout.readability_label}`

## Marker–carrier interpretation

- Decision label: `{decision.decision_label}`
- Marker support level: `{decision.marker_support_level}`
- Carrier support level: `{decision.carrier_support_level}`
- Informativeness: `{decision.test_informativeness}`

### Primary reason
{decision.primary_reason}

### Secondary reason
{decision.secondary_reason}

## Preservation status

- Topology preservation: `{decision.topology_preservation_status}`
- Geometry surrogate preservation: `{decision.geometry_surrogate_preservation_status}`
- Weighted relational disruption: `{decision.weighted_relational_disruption_status}`

## Next-step note

This BMC-01 block should be treated as a discriminative probe scaffold, not as a final bridge decision.
If arrangement-sensitive metrics remain weak or ambiguous, further readout upgrades or additional intervention families are required.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    ensure_required_columns(df, ["pair_id", "endpoint_a", "endpoint_b", "weight"])

    run_id = args.run_id or output_dir.name

    cfg = RunConfig(
        block_identifier="BMC-01",
        block_title="Weighted Relational Scramble Probe",
        intervention_family="weighted_relational_scramble",
        intervention_variant=args.variant,
        intervention_strength=args.strength,
        preserve_topology=True,
        preserve_shell_membership=("shell" in args.variant),
        preserve_global_weight_distribution=True,
        random_seed=args.seed,
        replicate_count=args.replicate_count,
    )

    baseline_state = compute_baseline_state(
        df=df,
        run_id=run_id,
        source_label=args.source_label,
        framework_label=args.framework_label,
    )
    baseline_readout = compute_bridge_readout(df, df)

    perturbed_df = apply_intervention(df, args.variant, args.strength, args.seed)
    perturbed_readout = compute_bridge_readout(df, perturbed_df)
    control_shell_df = compute_control_shell_comparison(df, perturbed_df, args.variant)
    readout_comparison_df = build_readout_comparison(baseline_readout, perturbed_readout)
    decision = make_decision_summary(perturbed_df, perturbed_readout, control_shell_df)

    perturbed_df.to_csv(output_dir / "intervention_table.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    readout_comparison_df.to_csv(output_dir / "readout_comparison.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    control_shell_df.to_csv(output_dir / "control_shell_comparison.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    write_json(output_dir / "run_config.json", asdict(cfg))
    write_json(output_dir / "run_metadata.json", {
        "run_id": run_id,
        "input_path": str(input_path),
        "output_dir": str(output_dir),
        "source_label": args.source_label,
        "framework_label": args.framework_label,
        "seed": args.seed,
    })
    write_json(output_dir / "baseline_state.json", asdict(baseline_state))
    write_json(output_dir / "baseline_readout.json", asdict(baseline_readout))
    write_json(output_dir / "decision_summary.json", asdict(decision))
    write_json(output_dir / "summary.json", {
        "block_identifier": cfg.block_identifier,
        "run_id": run_id,
        "variant": cfg.intervention_variant,
        "strength": cfg.intervention_strength,
        "decision_label": decision.decision_label,
        "marker_support_level": decision.marker_support_level,
        "carrier_support_level": decision.carrier_support_level,
        "baseline_bridge_signal_score": baseline_readout.bridge_signal_score,
        "perturbed_bridge_signal_score": perturbed_readout.bridge_signal_score,
        "baseline_d1_d2_separation_score": baseline_readout.d1_d2_separation_score,
        "perturbed_d1_d2_separation_score": perturbed_readout.d1_d2_separation_score,
        "baseline_weighted_relational_contrast_score": baseline_readout.weighted_relational_contrast_score,
        "perturbed_weighted_relational_contrast_score": perturbed_readout.weighted_relational_contrast_score,
        "perturbed_arrangement_signal_score": perturbed_readout.arrangement_signal_score,
        "endpoint_load_shift_score": perturbed_readout.endpoint_load_shift_score,
        "local_group_arrangement_shift_score": perturbed_readout.local_group_arrangement_shift_score,
        "shell_arrangement_shift_score": perturbed_readout.shell_arrangement_shift_score,
        "pair_neighborhood_consistency_shift_score": perturbed_readout.pair_neighborhood_consistency_shift_score,
    })

    write_markdown_readout(
        output_dir / "block_readout.md",
        cfg,
        baseline_state,
        baseline_readout,
        perturbed_readout,
        decision,
    )

    print(f"Wrote BMC-01 outputs to: {output_dir}")


if __name__ == "__main__":
    main()
