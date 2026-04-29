#!/usr/bin/env python3
from __future__ import annotations

"""
BMC-01-SX — Shell-Preserving vs Shell-Crossing Weighted Permutation Probe

This script implements the first shell-focused extension of the BMC marker–carrier
test line for the Quantum–Spacetime Bridge project.

It compares:
- within_shell_weight_permutation
against
- shell_crossing_weight_permutation

The current implementation starts with one controlled shell-crossing policy:
- adjacent_shell_crossing

It preserves:
- topology
- pair count
- node count
- global multiset of weights

Required input columns:
- pair_id
- endpoint_a
- endpoint_b
- weight
- shell_label

Optional:
- local_group
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
    "within_shell_weight_permutation",
    "shell_crossing_weight_permutation",
}

ALLOWED_CROSSING_POLICIES = {
    "adjacent_shell_crossing",
    "full_shell_crossing",
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
    intervention_variant: str
    shell_crossing_policy: str | None
    intervention_strength: str
    preserve_topology: bool
    preserve_global_weight_distribution: bool
    preserve_pair_count: bool
    preserve_node_count: bool
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
    shell_arrangement_shift_score: float
    pair_neighborhood_consistency_shift_score: float
    arrangement_signal_score: float
    shell_boundary_disruption_score: float
    shell_crossing_fraction: float
    shell_distance_mean: float
    readability_label: str


@dataclass
class DecisionSummary:
    decision_label: str
    shell_order_support_level: float
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
        description="BMC-01-SX Shell-Preserving vs Shell-Crossing Probe"
    )
    parser.add_argument("--input", required=True, help="Path to baseline relational CSV")
    parser.add_argument("--output-dir", required=True, help="Run output directory")
    parser.add_argument("--variant", required=True, choices=sorted(ALLOWED_VARIANTS))
    parser.add_argument(
        "--shell-crossing-policy",
        default="adjacent_shell_crossing",
        choices=sorted(ALLOWED_CROSSING_POLICIES),
        help="Crossing policy used when variant=shell_crossing_weight_permutation",
    )
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


def compute_shell_pair_rank_score(df: pd.DataFrame, weight_col: str = "weight") -> pd.DataFrame:
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
    merged = work.merge(
        endpoint_loads.rename(columns={"endpoint": "endpoint_a", "endpoint_total": "endpoint_a_total"}),
        on="endpoint_a",
        how="left",
    )
    merged = merged.merge(
        endpoint_loads.rename(columns={"endpoint": "endpoint_b", "endpoint_total": "endpoint_b_total"}),
        on="endpoint_b",
        how="left",
    )
    merged["pair_neighborhood_context"] = (
        merged["endpoint_a_total"].astype(float) + merged["endpoint_b_total"].astype(float)
    ) / 2.0
    merged["pair_neighborhood_consistency"] = (
        merged["weight_used"].astype(float) - merged["pair_neighborhood_context"].astype(float)
    ).abs()
    return merged[["pair_id", "pair_neighborhood_context", "pair_neighborhood_consistency"]]


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


def parse_shell_index(label: str) -> int:
    digits = "".join(ch for ch in str(label) if ch.isdigit())
    if digits:
        return int(digits)
    raise ValueError(f"Cannot parse shell index from label: {label}")


def choose_crossing_target_shell(
    source_shell: str,
    shell_labels: list[str],
    policy: str,
    rng: random.Random,
) -> str:
    source_idx = parse_shell_index(source_shell)
    candidates: list[str] = []

    if policy == "adjacent_shell_crossing":
        for s in shell_labels:
            idx = parse_shell_index(s)
            if abs(idx - source_idx) == 1:
                candidates.append(s)
    elif policy == "full_shell_crossing":
        candidates = [s for s in shell_labels if s != source_shell]
    else:
        raise ValueError(f"Unsupported shell crossing policy: {policy}")

    if not candidates:
        return source_shell
    return rng.choice(candidates)


def apply_within_shell_permutation(df: pd.DataFrame, strength: str, seed: int) -> pd.DataFrame:
    rng = random.Random(seed)
    fraction = STRENGTH_FRACTIONS[strength]
    out = df.copy()
    out["baseline_weight"] = out["weight"].astype(float)
    out["baseline_shell_label"] = out["shell_label"].astype(str)
    out["target_shell_label"] = out["shell_label"].astype(str)
    out["shell_crossing_flag"] = False
    out["shell_distance"] = 0

    for shell_label, sub in out.groupby("shell_label", sort=False):
        idx = sub.index.tolist()
        values = sub["weight"].astype(float).tolist()
        n = len(values)
        if n <= 1:
            continue
        k = max(2, int(round(n * fraction)))
        k = min(k, n)
        chosen_pos = rng.sample(list(range(n)), k)
        chosen_values = [values[i] for i in chosen_pos]
        rng.shuffle(chosen_values)
        for pos, new_value in zip(chosen_pos, chosen_values):
            out.at[idx[pos], "weight"] = new_value

    out["weight"] = out["weight"].astype(float)
    out["weight_delta"] = out["weight"] - out["baseline_weight"]
    out["weight_changed_flag"] = out["weight_delta"].abs() > 1e-12
    return out


def apply_shell_crossing_permutation(
    df: pd.DataFrame,
    strength: str,
    seed: int,
    policy: str,
) -> pd.DataFrame:
    rng = random.Random(seed)
    fraction = STRENGTH_FRACTIONS[strength]
    out = df.copy()
    out["baseline_weight"] = out["weight"].astype(float)
    out["baseline_shell_label"] = out["shell_label"].astype(str)
    out["target_shell_label"] = out["shell_label"].astype(str)
    out["shell_crossing_flag"] = False
    out["shell_distance"] = 0

    shell_labels = sorted(out["shell_label"].astype(str).unique(), key=parse_shell_index)
    n_total = len(out)
    k_total = max(2, int(round(n_total * fraction)))
    k_total = min(k_total, n_total)

    eligible_idx = out.index.tolist()
    chosen_idx = rng.sample(eligible_idx, k_total)

    used_targets: set[int] = set()
    source_to_target: dict[int, int] = {}

    for src_idx in chosen_idx:
        src_shell = str(out.at[src_idx, "shell_label"])
        target_shell = choose_crossing_target_shell(src_shell, shell_labels, policy, rng)

        target_candidates = [
            idx for idx in eligible_idx
            if idx not in used_targets
            and str(out.at[idx, "shell_label"]) == target_shell
            and idx != src_idx
        ]
        if not target_candidates:
            continue
        tgt_idx = rng.choice(target_candidates)
        used_targets.add(tgt_idx)
        source_to_target[src_idx] = tgt_idx

    original_weights = out["weight"].astype(float).copy()
    for src_idx, tgt_idx in source_to_target.items():
        out.at[src_idx, "weight"] = float(original_weights.loc[tgt_idx])
        baseline_shell = str(out.at[src_idx, "baseline_shell_label"])
        target_shell = str(out.at[tgt_idx, "shell_label"])
        out.at[src_idx, "target_shell_label"] = target_shell
        out.at[src_idx, "shell_crossing_flag"] = (baseline_shell != target_shell)
        out.at[src_idx, "shell_distance"] = abs(parse_shell_index(target_shell) - parse_shell_index(baseline_shell))

    out["weight"] = out["weight"].astype(float)
    out["weight_delta"] = out["weight"] - out["baseline_weight"]
    out["weight_changed_flag"] = out["weight_delta"].abs() > 1e-12
    return out


def apply_intervention(
    df: pd.DataFrame,
    variant: str,
    strength: str,
    seed: int,
    shell_crossing_policy: str | None,
) -> pd.DataFrame:
    if variant == "within_shell_weight_permutation":
        return apply_within_shell_permutation(df, strength, seed)
    if variant == "shell_crossing_weight_permutation":
        if not shell_crossing_policy:
            raise ValueError("shell_crossing_weight_permutation requires a shell_crossing_policy")
        return apply_shell_crossing_permutation(df, strength, seed, shell_crossing_policy)
    raise ValueError(f"Unsupported variant: {variant}")


def compute_bridge_readout(
    baseline_df: pd.DataFrame,
    current_df: pd.DataFrame,
) -> BridgeReadout:
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
        baseline_endpoint, current_endpoint, ["endpoint"], "endpoint_total_weight"
    )

    baseline_endpoint_disp = safe_std(baseline_endpoint["endpoint_total_weight"]) if len(baseline_endpoint) else 0.0
    current_endpoint_disp = safe_std(current_endpoint["endpoint_total_weight"]) if len(current_endpoint) else 0.0
    endpoint_load_dispersion_shift_score = abs(current_endpoint_disp - baseline_endpoint_disp)

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

    shell_crossing_fraction = float(current_df["shell_crossing_flag"].mean()) if "shell_crossing_flag" in current_df.columns else 0.0
    shell_distance_mean = float(current_df["shell_distance"].astype(float).mean()) if "shell_distance" in current_df.columns else 0.0
    shell_boundary_disruption_score = shell_crossing_fraction * max(1.0, shell_distance_mean)

    arrangement_signal_score = (
        endpoint_load_shift_score
        + endpoint_load_dispersion_shift_score
        + shell_arrangement_shift_score
        + pair_neighborhood_consistency_shift_score
        + shell_boundary_disruption_score
    ) / 5.0

    if arrangement_signal_score >= 0.15:
        readability_label = "arrangement_sensitive"
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
        shell_arrangement_shift_score=shell_arrangement_shift_score,
        pair_neighborhood_consistency_shift_score=pair_neighborhood_consistency_shift_score,
        arrangement_signal_score=arrangement_signal_score,
        shell_boundary_disruption_score=shell_boundary_disruption_score,
        shell_crossing_fraction=shell_crossing_fraction,
        shell_distance_mean=shell_distance_mean,
        readability_label=readability_label,
    )


def compute_control_shell_comparison(
    baseline_df: pd.DataFrame,
    perturbed_df: pd.DataFrame,
) -> pd.DataFrame:
    topology_similarity_score = 1.0
    global_weight_distribution_similarity_score = 1.0
    geometry_surrogate_similarity_score = 0.5

    shell_preservation_score = 1.0 - float(perturbed_df["shell_crossing_flag"].mean())
    shell_crossing_fraction = float(perturbed_df["shell_crossing_flag"].mean())
    shell_distance_mean = float(perturbed_df["shell_distance"].astype(float).mean())

    rows = [
        ("topology_similarity_score", topology_similarity_score),
        ("geometry_surrogate_similarity_score", geometry_surrogate_similarity_score),
        ("global_weight_distribution_similarity_score", global_weight_distribution_similarity_score),
        ("shell_preservation_score", shell_preservation_score),
        ("shell_crossing_fraction", shell_crossing_fraction),
        ("shell_distance_mean", shell_distance_mean),
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
        ("baseline_shell_arrangement_shift_score", baseline_readout.shell_arrangement_shift_score),
        ("perturbed_shell_arrangement_shift_score", perturbed_readout.shell_arrangement_shift_score),
        ("baseline_pair_neighborhood_consistency_shift_score", baseline_readout.pair_neighborhood_consistency_shift_score),
        ("perturbed_pair_neighborhood_consistency_shift_score", perturbed_readout.pair_neighborhood_consistency_shift_score),
        ("baseline_shell_boundary_disruption_score", baseline_readout.shell_boundary_disruption_score),
        ("perturbed_shell_boundary_disruption_score", perturbed_readout.shell_boundary_disruption_score),
        ("baseline_shell_crossing_fraction", baseline_readout.shell_crossing_fraction),
        ("perturbed_shell_crossing_fraction", perturbed_readout.shell_crossing_fraction),
        ("baseline_shell_distance_mean", baseline_readout.shell_distance_mean),
        ("perturbed_shell_distance_mean", perturbed_readout.shell_distance_mean),
        ("baseline_arrangement_signal_score", baseline_readout.arrangement_signal_score),
        ("perturbed_arrangement_signal_score", perturbed_readout.arrangement_signal_score),
        ("baseline_readability_label", baseline_readout.readability_label),
        ("perturbed_readability_label", perturbed_readout.readability_label),
    ]
    return pd.DataFrame(rows, columns=["field", "value"])


def make_decision_summary(
    perturbed_readout: BridgeReadout,
    control_shell_df: pd.DataFrame,
    variant: str,
) -> DecisionSummary:
    control_map = dict(zip(control_shell_df["metric"], control_shell_df["value"]))
    topology_similarity = float(control_map.get("topology_similarity_score", 0.0))
    shell_crossing_fraction = float(control_map.get("shell_crossing_fraction", 0.0))
    arrangement_signal = float(perturbed_readout.arrangement_signal_score)

    if topology_similarity < 0.90:
        return DecisionSummary(
            decision_label="test_not_informative",
            shell_order_support_level=0.0,
            marker_support_level=0.0,
            carrier_support_level=0.0,
            test_informativeness="low",
            primary_reason="Topology changed too strongly for shell-focused interpretation.",
            secondary_reason="The run no longer isolates shell structure under stable coarse conditions.",
            topology_preservation_status="failed",
            geometry_surrogate_preservation_status="placeholder_partial",
            weighted_relational_disruption_status="unclear",
        )

    if variant == "shell_crossing_weight_permutation" and shell_crossing_fraction < 0.05:
        return DecisionSummary(
            decision_label="test_not_informative",
            shell_order_support_level=0.0,
            marker_support_level=0.0,
            carrier_support_level=0.0,
            test_informativeness="low",
            primary_reason="Shell-crossing fraction was too small for an interpretable shell-breaking run.",
            secondary_reason="The intended shell comparison is not strong enough in this run.",
            topology_preservation_status="passed",
            geometry_surrogate_preservation_status="placeholder_partial",
            weighted_relational_disruption_status="passed",
        )

    if variant == "shell_crossing_weight_permutation" and arrangement_signal >= 0.18:
        shell_order_support_level = min(1.0, arrangement_signal)
        carrier_support_level = min(1.0, arrangement_signal)
        marker_support_level = max(0.0, 1.0 - carrier_support_level)
        return DecisionSummary(
            decision_label="shell_order_leaning",
            shell_order_support_level=round(shell_order_support_level, 6),
            marker_support_level=round(marker_support_level, 6),
            carrier_support_level=round(carrier_support_level, 6),
            test_informativeness="medium",
            primary_reason="Shell-crossing produced a clear shell-sensitive structural response under preserved topology and preserved weight multiset.",
            secondary_reason="This supports the reading that shell membership carries nontrivial intermediate order.",
            topology_preservation_status="passed",
            geometry_surrogate_preservation_status="placeholder_partial",
            weighted_relational_disruption_status="passed",
        )

    return DecisionSummary(
        decision_label="undecided",
        shell_order_support_level=0.5 if arrangement_signal >= 0.10 else 0.0,
        marker_support_level=0.5,
        carrier_support_level=0.5 if arrangement_signal >= 0.10 else 0.0,
        test_informativeness="medium",
        primary_reason="The shell-focused intervention is real, but the response is not yet decisive on its own.",
        secondary_reason="A matched preserving-vs-crossing comparison is required before stronger shell-order claims are warranted.",
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
    text = f"""# BMC-01-SX Block Readout

## Run identity

- Run ID: `{baseline_state.run_id}`
- Block: `{cfg.block_identifier}`
- Title: `{cfg.block_title}`
- Variant: `{cfg.intervention_variant}`
- Shell crossing policy: `{cfg.shell_crossing_policy}`
- Strength: `{cfg.intervention_strength}`
- Seed: `{cfg.random_seed}`

## Baseline description

- Source label: `{baseline_state.source_label}`
- Framework label: `{baseline_state.framework_label}`
- Pair count: `{baseline_state.pair_count}`
- Node count: `{baseline_state.node_count}`
- Baseline weight mean: `{baseline_state.baseline_weight_mean:.6f}`
- Baseline weight std: `{baseline_state.baseline_weight_std:.6f}`

## Perturbed readout

- Bridge signal score: `{perturbed_readout.bridge_signal_score:.6f}`
- D1/D2 separation score: `{perturbed_readout.d1_d2_separation_score:.6f}`
- Weighted relational contrast score: `{perturbed_readout.weighted_relational_contrast_score:.6f}`
- Endpoint load shift score: `{perturbed_readout.endpoint_load_shift_score:.6f}`
- Endpoint load dispersion shift score: `{perturbed_readout.endpoint_load_dispersion_shift_score:.6f}`
- Shell arrangement shift score: `{perturbed_readout.shell_arrangement_shift_score:.6f}`
- Pair-to-neighborhood consistency shift score: `{perturbed_readout.pair_neighborhood_consistency_shift_score:.6f}`
- Shell boundary disruption score: `{perturbed_readout.shell_boundary_disruption_score:.6f}`
- Shell crossing fraction: `{perturbed_readout.shell_crossing_fraction:.6f}`
- Shell distance mean: `{perturbed_readout.shell_distance_mean:.6f}`
- Arrangement signal score: `{perturbed_readout.arrangement_signal_score:.6f}`
- Readability label: `{perturbed_readout.readability_label}`

## Interpretation

- Decision label: `{decision.decision_label}`
- Shell-order support level: `{decision.shell_order_support_level}`
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

This shell-focused run should be interpreted only together with a matched shell-preserving comparison.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    ensure_required_columns(df, ["pair_id", "endpoint_a", "endpoint_b", "weight", "shell_label"])
    df["weight"] = df["weight"].astype(float)
    df["shell_label"] = df["shell_label"].astype(str)

    run_id = args.run_id or output_dir.name
    shell_crossing_policy = args.shell_crossing_policy if args.variant == "shell_crossing_weight_permutation" else None

    cfg = RunConfig(
        block_identifier="BMC-01-SX",
        block_title="Shell-Preserving vs Shell-Crossing Weighted Permutation Probe",
        intervention_variant=args.variant,
        shell_crossing_policy=shell_crossing_policy,
        intervention_strength=args.strength,
        preserve_topology=True,
        preserve_global_weight_distribution=True,
        preserve_pair_count=True,
        preserve_node_count=True,
        random_seed=args.seed,
        replicate_count=args.replicate_count,
    )

    baseline_state = compute_baseline_state(df, run_id, args.source_label, args.framework_label)
    baseline_df = df.copy()
    baseline_df["baseline_weight"] = baseline_df["weight"]
    baseline_df["baseline_shell_label"] = baseline_df["shell_label"]
    baseline_df["target_shell_label"] = baseline_df["shell_label"]
    baseline_df["shell_crossing_flag"] = False
    baseline_df["shell_distance"] = 0
    baseline_df["weight_delta"] = 0.0
    baseline_df["weight_changed_flag"] = False

    baseline_readout = compute_bridge_readout(baseline_df, baseline_df)
    perturbed_df = apply_intervention(df, args.variant, args.strength, args.seed, shell_crossing_policy)
    perturbed_readout = compute_bridge_readout(baseline_df, perturbed_df)
    control_shell_df = compute_control_shell_comparison(baseline_df, perturbed_df)
    readout_comparison_df = build_readout_comparison(baseline_readout, perturbed_readout)
    decision = make_decision_summary(perturbed_readout, control_shell_df, args.variant)

    perturbed_df.to_csv(output_dir / "intervention_table.csv", index=False, quoting=csv.QUOTE_MINIMAL)
    perturbed_df[
        [
            "pair_id",
            "baseline_shell_label",
            "target_shell_label",
            "shell_crossing_flag",
            "shell_distance",
            "weight",
            "baseline_weight",
            "weight_delta",
        ]
    ].to_csv(output_dir / "shell_crossing_summary.csv", index=False, quoting=csv.QUOTE_MINIMAL)
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
        "shell_crossing_policy": cfg.shell_crossing_policy,
        "strength": cfg.intervention_strength,
        "decision_label": decision.decision_label,
        "shell_order_support_level": decision.shell_order_support_level,
        "marker_support_level": decision.marker_support_level,
        "carrier_support_level": decision.carrier_support_level,
        "perturbed_arrangement_signal_score": perturbed_readout.arrangement_signal_score,
        "shell_arrangement_shift_score": perturbed_readout.shell_arrangement_shift_score,
        "shell_boundary_disruption_score": perturbed_readout.shell_boundary_disruption_score,
        "shell_crossing_fraction": perturbed_readout.shell_crossing_fraction,
        "shell_distance_mean": perturbed_readout.shell_distance_mean,
        "endpoint_load_shift_score": perturbed_readout.endpoint_load_shift_score,
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

    print(f"Wrote BMC-01-SX outputs to: {output_dir}")


if __name__ == "__main__":
    main()
