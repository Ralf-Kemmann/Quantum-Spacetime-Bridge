from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

from columns_m34_branch import (
    BRANCH_ASSIGNMENT_COLUMNS,
    BRANCH_DRIFT_TABLE_COLUMNS,
    BRANCH_FREQUENCY_TABLE_COLUMNS,
    BRANCH_SOURCE_COUPLING_COLUMNS,
    BRANCH_SUMMARY_BY_CONDITION_COLUMNS,
    BRANCH_TRANSITION_TABLE_COLUMNS,
)


@dataclass(slots=True)
class BranchDef:
    id: str
    left: float
    right: float
    center: float


@dataclass(slots=True)
class M34Config:
    enabled: bool
    readout_summary: Path
    readout_candidates: Path
    source_summary: Path
    source_kernel: Path
    exclude_t0: bool
    candidate_scope: str
    allowed_readout_labels: List[str]
    band_min: float
    band_max: float
    min_coherence_score: Optional[float]
    branches: List[BranchDef]
    source_link_enabled: bool
    source_alpha_tolerance: float
    dominant_branch_min_fraction: float
    source_link_min_fraction: float
    output_root: Path


def safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        x = float(value)
        if not np.isfinite(x):
            return None
        return x
    except Exception:
        return None


def safe_json_value(value: Any) -> Any:
    if isinstance(value, (np.floating, float)):
        if not np.isfinite(value):
            return None
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if pd.isna(value):
        return None
    return value


def entropy_from_fracs(fracs: Iterable[float]) -> float:
    vals = [f for f in fracs if f > 0]
    if not vals:
        return 0.0
    return float(-sum(f * math.log(f) for f in vals))


def load_m34_config(config_path: Path) -> M34Config:
    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m34_branch_analysis"]
    branches = [BranchDef(**b) for b in block["branches"]]

    return M34Config(
        enabled=bool(block["enabled"]),
        readout_summary=Path(block["input"]["readout_summary"]),
        readout_candidates=Path(block["input"]["readout_candidates"]),
        source_summary=Path(block["input"]["source_summary"]),
        source_kernel=Path(block["input"]["source_kernel"]),
        exclude_t0=bool(block["selection"]["exclude_t0"]),
        candidate_scope=str(block["selection"]["candidate_scope"]),
        allowed_readout_labels=list(block["selection"]["allowed_readout_labels"]),
        band_min=float(block["selection"]["band_min"]),
        band_max=float(block["selection"]["band_max"]),
        min_coherence_score=block["selection"].get("min_coherence_score", None),
        branches=branches,
        source_link_enabled=bool(block["source_link"]["enabled"]),
        source_alpha_tolerance=float(block["source_link"]["alpha_tolerance"]),
        dominant_branch_min_fraction=float(block["thresholds"]["dominant_branch_min_fraction"]),
        source_link_min_fraction=float(block["thresholds"]["source_link_min_fraction"]),
        output_root=Path(block["output"]["root"]),
    )


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def assign_branch(alpha: Optional[float], branches: List[BranchDef]) -> Tuple[Optional[str], Optional[float], Optional[float], Optional[float], Optional[float], int]:
    if alpha is None:
        return None, None, None, None, None, 0

    for b in branches:
        if b.left <= alpha <= b.right:
            return b.id, b.center, b.left, b.right, abs(alpha - b.center), 1

    return None, None, None, None, None, 0


def pick_preferred_alpha(row: pd.Series, scope_mode: str) -> Tuple[Optional[str], Optional[float], Optional[float], str]:
    if scope_mode == "preferred":
        scope = row.get("preferred_scope", None)
        alpha = safe_float(row.get("preferred_alpha_coherent"))
        score = safe_float(row.get("preferred_coherence_score"))
        return scope, alpha, score, "preferred"

    if scope_mode == "band_only":
        alpha = safe_float(row.get("alpha_coherent_band"))
        score = safe_float(row.get("coherence_score_band"))
        return "band", alpha, score, "band_only"

    alpha = safe_float(row.get("preferred_alpha_coherent"))
    score = safe_float(row.get("preferred_coherence_score"))
    return row.get("preferred_scope", None), alpha, score, "fallback"


def build_branch_assignment(
    readout_summary_df: pd.DataFrame,
    source_summary_df: pd.DataFrame,
    cfg: M34Config,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    source_lookup = source_summary_df.set_index(["t", "p_family"]) if not source_summary_df.empty else None

    for _, row in readout_summary_df.iterrows():
        scope, alpha, score, _ = pick_preferred_alpha(row, cfg.candidate_scope)

        branch_id, center, left, right, dist, in_branch_flag = assign_branch(alpha, cfg.branches)

        source_alpha = None
        source_feature = None
        source_label = None
        if source_lookup is not None:
            key = (row["t"], row["p_family"])
            if key in source_lookup.index:
                src = source_lookup.loc[key]
                if isinstance(src, pd.DataFrame):
                    src = src.iloc[0]
                source_alpha = safe_float(src.get("alpha_star_source"))
                source_feature = src.get("source_feature")
                source_label = src.get("source_label")

        delta_source_branch = None
        source_link_flag = 0
        if cfg.source_link_enabled and alpha is not None and source_alpha is not None:
            delta_source_branch = abs(alpha - source_alpha)
            source_link_flag = int(delta_source_branch <= cfg.source_alpha_tolerance)

        rows.append(
            {
                "run_id": row["run_id"],
                "t": row["t"],
                "p_family": row["p_family"],
                "theta": row["theta"],
                "preferred_scope": scope,
                "preferred_alpha_coherent": alpha,
                "preferred_coherence_score": score,
                "readout_label": row["readout_label"],
                "branch_id": branch_id,
                "branch_center": center,
                "branch_left": left,
                "branch_right": right,
                "distance_to_branch_center": dist,
                "in_branch_flag": in_branch_flag,
                "source_alpha_reference": source_alpha,
                "delta_source_branch": delta_source_branch,
                "source_link_flag": source_link_flag,
            }
        )

    return pd.DataFrame(rows, columns=BRANCH_ASSIGNMENT_COLUMNS)


def build_branch_summary_by_condition(branch_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for (run_id, t, p_family, theta), group in branch_df.groupby(["run_id", "t", "p_family", "theta"], dropna=False):
        branch_counts = group["branch_id"].value_counts(dropna=True)
        preferred_branch = branch_counts.index[0] if not branch_counts.empty else None

        preferred_row = group.sort_values("preferred_coherence_score", ascending=False, na_position="last").iloc[0]

        rows.append(
            {
                "run_id": run_id,
                "t": t,
                "p_family": p_family,
                "theta": theta,
                "n_candidates": int(len(group)),
                "preferred_branch": preferred_branch,
                "preferred_alpha": safe_float(preferred_row.get("preferred_alpha_coherent")),
                "preferred_score": safe_float(preferred_row.get("preferred_coherence_score")),
                "branch_B1_flag": int((group["branch_id"] == "B1").any()),
                "branch_B2_flag": int((group["branch_id"] == "B2").any()),
                "branch_B3_flag": int((group["branch_id"] == "B3").any()),
                "source_link_flag": int((group["source_link_flag"] == 1).any()),
                "branch_label": "B0" if branch_counts.empty else "B1",
            }
        )

    return pd.DataFrame(rows, columns=BRANCH_SUMMARY_BY_CONDITION_COLUMNS)


def frequency_row(run_id: str, aggregation_level: str, aggregation_key: str, group: pd.DataFrame, dominant_branch_min_fraction: float) -> Dict[str, Any]:
    n_total = len(group)
    counts = {bid: int((group["branch_id"] == bid).sum()) for bid in ("B1", "B2", "B3")}
    fracs = {bid: (counts[bid] / n_total if n_total > 0 else 0.0) for bid in counts}

    dominant_branch = None
    if n_total > 0:
        best_bid = max(fracs, key=fracs.get)
        if fracs[best_bid] >= dominant_branch_min_fraction:
            dominant_branch = best_bid

    return {
        "run_id": run_id,
        "aggregation_level": aggregation_level,
        "aggregation_key": aggregation_key,
        "n_total": n_total,
        "n_B1": counts["B1"],
        "n_B2": counts["B2"],
        "n_B3": counts["B3"],
        "frac_B1": fracs["B1"],
        "frac_B2": fracs["B2"],
        "frac_B3": fracs["B3"],
        "dominant_branch": dominant_branch,
        "branch_entropy": entropy_from_fracs(fracs.values()),
    }


def build_branch_frequency_table(branch_df: pd.DataFrame, dominant_branch_min_fraction: float) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    if branch_df.empty:
        return pd.DataFrame(columns=BRANCH_FREQUENCY_TABLE_COLUMNS)

    run_id = str(branch_df["run_id"].iloc[0])

    rows.append(frequency_row(run_id, "global", "global", branch_df, dominant_branch_min_fraction))

    for t, group in branch_df.groupby("t", dropna=False):
        rows.append(frequency_row(run_id, "by_t", str(t), group, dominant_branch_min_fraction))

    for p_family, group in branch_df.groupby("p_family", dropna=False):
        rows.append(frequency_row(run_id, "by_p_family", str(p_family), group, dominant_branch_min_fraction))

    for theta, group in branch_df.groupby("theta", dropna=False):
        rows.append(frequency_row(run_id, "by_theta", str(theta), group, dominant_branch_min_fraction))

    return pd.DataFrame(rows, columns=BRANCH_FREQUENCY_TABLE_COLUMNS)


def build_branch_drift_table(branch_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for (branch_id, p_family, theta), group in branch_df.dropna(subset=["branch_id"]).groupby(["branch_id", "p_family", "theta"], dropna=False):
        g = group.sort_values("t")
        if g.empty or g["t"].nunique() < 2:
            continue

        first = g.iloc[0]
        last = g.iloc[-1]
        alpha_first = safe_float(first["preferred_alpha_coherent"])
        alpha_last = safe_float(last["preferred_alpha_coherent"])
        delta_alpha = None if alpha_first is None or alpha_last is None else alpha_last - alpha_first

        diffs = g["preferred_alpha_coherent"].astype(float).diff().dropna()
        monotonicity_flag = int((diffs >= 0).all() or (diffs <= 0).all()) if not diffs.empty else 0

        rows.append(
            {
                "run_id": first["run_id"],
                "branch_id": branch_id,
                "p_family": p_family,
                "theta": theta,
                "t_min": first["t"],
                "t_max": last["t"],
                "alpha_at_t_min": alpha_first,
                "alpha_at_t_max": alpha_last,
                "delta_alpha": delta_alpha,
                "monotonicity_flag": monotonicity_flag,
                "drift_label": "stable" if monotonicity_flag else "mixed",
            }
        )

    return pd.DataFrame(rows, columns=BRANCH_DRIFT_TABLE_COLUMNS)


def transition_name(a: Optional[str], b: Optional[str]) -> str:
    if a == b:
        return "stay"
    if a is None and b is not None:
        return "reemerge"
    if a is not None and b is None:
        return "dropout"
    return f"{a}_to_{b}"


def build_branch_transition_table(branch_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for (p_family, theta), group in branch_df.sort_values("t").groupby(["p_family", "theta"], dropna=False):
        g = group.sort_values("t").reset_index(drop=True)
        for i in range(len(g) - 1):
            r1 = g.iloc[i]
            r2 = g.iloc[i + 1]

            a1 = safe_float(r1["preferred_alpha_coherent"])
            a2 = safe_float(r2["preferred_alpha_coherent"])
            delta_alpha = None if a1 is None or a2 is None else a2 - a1

            rows.append(
                {
                    "run_id": r1["run_id"],
                    "scan_axis": "t",
                    "group_id": f"{p_family}__{theta}",
                    "step_from": r1["t"],
                    "step_to": r2["t"],
                    "branch_from": r1["branch_id"],
                    "branch_to": r2["branch_id"],
                    "transition_type": transition_name(r1["branch_id"], r2["branch_id"]),
                    "delta_alpha": delta_alpha,
                    "score_from": safe_float(r1["preferred_coherence_score"]),
                    "score_to": safe_float(r2["preferred_coherence_score"]),
                }
            )

    return pd.DataFrame(rows, columns=BRANCH_TRANSITION_TABLE_COLUMNS)


def build_branch_source_coupling(branch_df: pd.DataFrame, source_summary_df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    source_lookup = source_summary_df.set_index(["t", "p_family"]) if not source_summary_df.empty else None

    for _, row in branch_df.iterrows():
        source_feature = None
        source_label = None
        if source_lookup is not None:
            key = (row["t"], row["p_family"])
            if key in source_lookup.index:
                src = source_lookup.loc[key]
                if isinstance(src, pd.DataFrame):
                    src = src.iloc[0]
                source_feature = src.get("source_feature")
                source_label = src.get("source_label")

        rows.append(
            {
                "run_id": row["run_id"],
                "t": row["t"],
                "p_family": row["p_family"],
                "theta": row["theta"],
                "preferred_branch": row["branch_id"],
                "preferred_alpha": row["preferred_alpha_coherent"],
                "source_alpha_reference": row["source_alpha_reference"],
                "delta_source_branch": row["delta_source_branch"],
                "source_feature": source_feature,
                "source_label": source_label,
                "source_link_flag": row["source_link_flag"],
            }
        )

    return pd.DataFrame(rows, columns=BRANCH_SOURCE_COUPLING_COLUMNS)


def decide_branch_label(
    freq_df: pd.DataFrame,
    transition_df: pd.DataFrame,
    coupling_df: pd.DataFrame,
    cfg: M34Config,
) -> Tuple[str, Dict[str, Any]]:
    if freq_df.empty:
        return "B0", {"reason": "no branch assignments"}

    global_row = freq_df[freq_df["aggregation_level"] == "global"].iloc[0]
    n_present = sum(int(global_row[f"n_{bid}"] > 0) for bid in ("B1", "B2", "B3"))
    if n_present < 2:
        return "B0", {"reason": "fewer than two branches populated"}

    nonlocal_jumps = int(
        ((transition_df["transition_type"] == "B1_to_B3") | (transition_df["transition_type"] == "B3_to_B1")).sum()
    ) if not transition_df.empty else 0

    adjacent_jumps = int(
        transition_df["transition_type"].isin(["B1_to_B2", "B2_to_B1", "B2_to_B3", "B3_to_B2"]).sum()
    ) if not transition_df.empty else 0

    source_link_frac = float(coupling_df["source_link_flag"].mean()) if not coupling_df.empty else 0.0

    label = "B1"
    if adjacent_jumps >= nonlocal_jumps:
        label = "B2"
    if label == "B2" and source_link_frac >= cfg.source_link_min_fraction:
        label = "B3"

    diagnostics = {
        "dominant_branch": global_row["dominant_branch"],
        "frac_B1": safe_json_value(global_row["frac_B1"]),
        "frac_B2": safe_json_value(global_row["frac_B2"]),
        "frac_B3": safe_json_value(global_row["frac_B3"]),
        "branch_entropy": safe_json_value(global_row["branch_entropy"]),
        "adjacent_jumps": adjacent_jumps,
        "nonlocal_jumps": nonlocal_jumps,
        "source_link_frac": source_link_frac,
    }
    return label, diagnostics


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    safe_payload = {k: safe_json_value(v) for k, v in payload.items()}
    with path.open("w", encoding="utf-8") as f:
        json.dump(safe_payload, f, indent=2, ensure_ascii=False)


def write_report(path: Path, final_label: str, diagnostics: Dict[str, Any]) -> None:
    lines = [
        "# M.3.4 Branch Analysis Report",
        "",
        f"## Final label",
        f"{final_label}",
        "",
        "## Diagnostics",
    ]
    for k, v in diagnostics.items():
        lines.append(f"- {k}: {safe_json_value(v)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.4 branch analysis postprocessing")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    cfg = load_m34_config(Path(args.config).resolve())

    if not cfg.enabled:
        print("M.3.4 disabled in config. Exiting.")
        return

    output_root = resolve_path(project_root, cfg.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    readout_summary_path = resolve_path(project_root, cfg.readout_summary)
    source_summary_path = resolve_path(project_root, cfg.source_summary)

    readout_summary_df = pd.read_csv(readout_summary_path)
    source_summary_df = pd.read_csv(source_summary_path) if source_summary_path.exists() else pd.DataFrame()

    # Auswahl
    if cfg.exclude_t0:
        readout_summary_df = readout_summary_df[readout_summary_df["t"] > 0].copy()

    readout_summary_df = readout_summary_df[
        readout_summary_df["readout_label"].isin(cfg.allowed_readout_labels)
    ].copy()

    readout_summary_df = readout_summary_df[
        readout_summary_df["preferred_scope"].fillna("none") != "none"
    ].copy()

    if cfg.min_coherence_score is not None:
        readout_summary_df = readout_summary_df[
            readout_summary_df["preferred_coherence_score"].astype(float) >= cfg.min_coherence_score
        ].copy()

    branch_df = build_branch_assignment(readout_summary_df, source_summary_df, cfg)
    summary_df = build_branch_summary_by_condition(branch_df)
    freq_df = build_branch_frequency_table(branch_df, cfg.dominant_branch_min_fraction)
    drift_df = build_branch_drift_table(branch_df)
    transition_df = build_branch_transition_table(branch_df)
    coupling_df = build_branch_source_coupling(branch_df, source_summary_df)

    final_label, diagnostics = decide_branch_label(freq_df, transition_df, coupling_df, cfg)

    branch_df.to_csv(output_root / "branch_assignment.csv", index=False)
    summary_df.to_csv(output_root / "branch_summary_by_condition.csv", index=False)
    freq_df.to_csv(output_root / "branch_frequency_table.csv", index=False)
    drift_df.to_csv(output_root / "branch_drift_table.csv", index=False)
    transition_df.to_csv(output_root / "branch_transition_table.csv", index=False)
    coupling_df.to_csv(output_root / "branch_source_coupling.csv", index=False)

    write_json(
        output_root / "branch_summary.json",
        {
            "final_label": final_label,
            **diagnostics,
        },
    )
    write_report(output_root / "branch_report.md", final_label, diagnostics)

    print(f"M.3.4 completed. Output written to: {output_root}")


if __name__ == "__main__":
    main()
