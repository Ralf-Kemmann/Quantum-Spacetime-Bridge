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

from columns_m35b_packet import (
    PACKET_FIT_BEST_COLUMNS,
    PACKET_FIT_GRID_COLUMNS,
    PACKET_FREQUENCY_TABLE_COLUMNS,
    SOURCE_CANDIDATE_GRID_COLUMNS,
    SOURCE_CURVE_GRID_COLUMNS,
)


@dataclass(slots=True)
class BranchDef:
    id: str
    left: float
    right: float
    center: float


@dataclass(slots=True)
class M35bConfig:
    enabled: bool
    source_pair_kernel: Path
    readout_summary: Path
    branch_assignment: Path
    exclude_t0: bool
    allowed_readout_labels: List[str]
    source_features: List[str]
    packet_family: str
    p0_grid: List[float]
    sigma_p_grid: List[float]
    pair_weight_mode: str
    band_min: float
    band_max: float
    source_branches: List[BranchDef]
    alpha_tolerance: float
    branch_match_weight: float
    alpha_match_weight: float
    source_score_weight: float
    readout_score_weight: float
    output_root: Path


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def safe_float(x: Any) -> Optional[float]:
    try:
        v = float(x)
        return v if np.isfinite(v) else None
    except Exception:
        return None


def safe_json_value(x: Any) -> Any:
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if pd.isna(x):
        return None
    return x


def entropy_from_fracs(fracs: Iterable[float]) -> float:
    vals = [f for f in fracs if f > 0]
    if not vals:
        return 0.0
    return float(-sum(f * math.log(f) for f in vals))


def load_config(path: Path) -> M35bConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m35b_packet_kernel"]
    branches = [BranchDef(**b) for b in block["source_branches"]]

    return M35bConfig(
        enabled=bool(block["enabled"]),
        source_pair_kernel=Path(block["input"]["source_pair_kernel"]),
        readout_summary=Path(block["input"]["readout_summary"]),
        branch_assignment=Path(block["input"]["branch_assignment"]),
        exclude_t0=bool(block["selection"]["exclude_t0"]),
        allowed_readout_labels=list(block["selection"]["allowed_readout_labels"]),
        source_features=list(block["selection"]["source_features"]),
        packet_family=str(block["packet_model"]["family"]),
        p0_grid=[float(x) for x in block["packet_model"]["p0_grid"]],
        sigma_p_grid=[float(x) for x in block["packet_model"]["sigma_p_grid"]],
        pair_weight_mode=str(block["packet_model"]["pair_weight_mode"]),
        band_min=float(block["alpha"]["band_min"]),
        band_max=float(block["alpha"]["band_max"]),
        source_branches=branches,
        alpha_tolerance=float(block["coupling"]["alpha_tolerance"]),
        branch_match_weight=float(block["coupling"]["branch_match_weight"]),
        alpha_match_weight=float(block["coupling"]["alpha_match_weight"]),
        source_score_weight=float(block["coupling"]["source_score_weight"]),
        readout_score_weight=float(block["coupling"]["readout_score_weight"]),
        output_root=Path(block["output"]["root"]),
    )


def infer_p_values_for_family(p_family: str, config_raw: Dict[str, Any]) -> np.ndarray:
    fam = config_raw["p_sets"]["families"][p_family]
    return np.asarray(fam["p_values"], dtype=float)


def gaussian_packet_probabilities(p_values: np.ndarray, p0: float, sigma_p: float) -> np.ndarray:
    sigma = max(float(sigma_p), 1.0e-9)
    amp = np.exp(-((p_values - p0) ** 2) / (4.0 * sigma * sigma))
    prob = amp ** 2
    s = prob.sum()
    if s <= 0:
        return np.full_like(prob, 1.0 / len(prob))
    return prob / s


def infer_pair_index_base(pair_df: pd.DataFrame, n_modes: int) -> int:
    vals = pd.concat([pair_df["pair_i"], pair_df["pair_j"]], ignore_index=True).dropna().astype(int)
    if vals.empty:
        return 0
    mn, mx = int(vals.min()), int(vals.max())
    if mn >= 1 and mx <= n_modes:
        return 1
    return 0


def pair_weights_from_probabilities(
    p_values: np.ndarray,
    p0: float,
    sigma_p: float,
    pair_df: pd.DataFrame,
) -> Dict[Tuple[int, int], float]:
    prob = gaussian_packet_probabilities(p_values, p0, sigma_p)
    idx_base = infer_pair_index_base(pair_df, len(p_values))
    weights: Dict[Tuple[int, int], float] = {}

    unique_pairs = (
        pair_df[["pair_i", "pair_j"]]
        .drop_duplicates()
        .dropna()
        .astype(int)
        .itertuples(index=False, name=None)
    )

    for pair_i, pair_j in unique_pairs:
        i = int(pair_i) - idx_base
        j = int(pair_j) - idx_base
        if 0 <= i < len(prob) and 0 <= j < len(prob) and i < j:
            weights[(int(pair_i), int(pair_j))] = float(prob[i] * prob[j])

    norm = sum(weights.values())
    if norm > 0:
        weights = {k: v / norm for k, v in weights.items()}
    return weights


def assign_branch(alpha: Optional[float], branches: List[BranchDef]) -> Tuple[Optional[str], Optional[float]]:
    if alpha is None:
        return None, None
    for b in branches:
        if b.left <= alpha <= b.right:
            return b.id, abs(alpha - b.center)
    return None, None


def compute_source_curve_for_feature(
    pair_df: pd.DataFrame,
    pair_weights: Dict[Tuple[int, int], float],
    feature: str,
) -> pd.Series:
    def agg_group(g: pd.DataFrame) -> float:
        num = 0.0
        den = 0.0
        for row in g.itertuples(index=False):
            key = (int(row.pair_i), int(row.pair_j))
            w = pair_weights.get(key, 0.0)
            if w <= 0:
                continue
            kbar = float(row.kbar_ij)
            if feature == "neg":
                val = max(-kbar, 0.0)
            elif feature == "abs":
                val = abs(kbar)
            elif feature == "imb":
                val = float(np.sign(kbar))
            else:
                raise ValueError(f"Unsupported source feature: {feature}")
            num += w * val
            den += w
        return np.nan if den <= 0 else num / den

    return pair_df.groupby("alpha", dropna=False).apply(agg_group, include_groups=False)


def find_best_local_candidate_in_band(
    curve_df: pd.DataFrame,
    band_min: float,
    band_max: float,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    sub = curve_df[(curve_df["alpha"] >= band_min) & (curve_df["alpha"] <= band_max)].copy()
    if sub.empty:
        return None, None, None

    sub = sub.sort_values("alpha").reset_index(drop=True)
    vals = sub["source_curve_value"].to_numpy(dtype=float)
    alphas = sub["alpha"].to_numpy(dtype=float)

    candidates: List[Tuple[float, float, float]] = []
    for i in range(1, len(sub) - 1):
        if np.isfinite(vals[i - 1]) and np.isfinite(vals[i]) and np.isfinite(vals[i + 1]):
            if vals[i] > vals[i - 1] and vals[i] > vals[i + 1]:
                prom = vals[i] - 0.5 * (vals[i - 1] + vals[i + 1])
                candidates.append((alphas[i], vals[i], prom))

    if not candidates:
        idx = int(np.nanargmax(vals))
        return float(alphas[idx]), float(vals[idx]), 0.0

    return max(candidates, key=lambda x: x[2])


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.5b real packet-weighted kernel runner")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.5b disabled in config. Exiting.")
        return

    with config_path.open("r", encoding="utf-8") as f:
        raw_cfg = yaml.safe_load(f)

    output_root = resolve_path(project_root, cfg.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    pair_kernel_df = pd.read_csv(resolve_path(project_root, cfg.source_pair_kernel))
    readout_summary_df = pd.read_csv(resolve_path(project_root, cfg.readout_summary))
    _ = pd.read_csv(resolve_path(project_root, cfg.branch_assignment))

    required_cols = {"run_id", "t", "p_family", "alpha", "pair_i", "pair_j", "kbar_ij"}
    missing = required_cols - set(pair_kernel_df.columns)
    if missing:
        raise ValueError(f"source_pair_kernel is missing required columns: {sorted(missing)}")

    if cfg.exclude_t0:
        readout_summary_df = readout_summary_df[readout_summary_df["t"] > 0].copy()

    readout_summary_df = readout_summary_df[
        readout_summary_df["readout_label"].isin(cfg.allowed_readout_labels)
    ].copy()

    readout_summary_df = readout_summary_df[
        readout_summary_df["preferred_scope"].fillna("none") != "none"
    ].copy()

    source_curve_rows: List[Dict[str, Any]] = []
    source_candidate_rows: List[Dict[str, Any]] = []
    fit_grid_rows: List[Dict[str, Any]] = []
    best_rows: List[Dict[str, Any]] = []

    for _, rd in readout_summary_df.iterrows():
        run_id = str(rd["run_id"])
        t = float(rd["t"])
        p_family = str(rd["p_family"])
        theta = float(rd["theta"])
        alpha_rd = safe_float(rd.get("preferred_alpha_coherent"))
        branch_rd, _ = assign_branch(alpha_rd, cfg.source_branches)
        readout_score = safe_float(rd.get("preferred_coherence_score")) or 0.0

        pair_slice = pair_kernel_df[
            (pair_kernel_df["run_id"] == run_id)
            & (pair_kernel_df["t"].astype(float) == t)
            & (pair_kernel_df["p_family"] == p_family)
        ].copy()

        if pair_slice.empty:
            continue

        p_values = infer_p_values_for_family(p_family, raw_cfg)

        best_loss: Optional[float] = None
        best_row: Optional[Dict[str, Any]] = None

        for source_feature in cfg.source_features:
            for p0 in cfg.p0_grid:
                for sigma_p in cfg.sigma_p_grid:
                    pair_weights = pair_weights_from_probabilities(p_values, p0, sigma_p, pair_slice)
                    if not pair_weights:
                        continue

                    curve_series = compute_source_curve_for_feature(pair_slice, pair_weights, source_feature)
                    curve_df = curve_series.reset_index(name="source_curve_value").sort_values("alpha").reset_index(drop=True)

                    for c_row in curve_df.itertuples(index=False):
                        source_curve_rows.append(
                            {
                                "run_id": run_id,
                                "t": t,
                                "p_family": p_family,
                                "theta": theta,
                                "packet_model": cfg.packet_family,
                                "source_feature": source_feature,
                                "p0": p0,
                                "sigma_p": sigma_p,
                                "alpha": float(c_row.alpha),
                                "source_curve_value": float(c_row.source_curve_value) if np.isfinite(c_row.source_curve_value) else np.nan,
                            }
                        )

                    alpha_src, cand_val, cand_prom = find_best_local_candidate_in_band(curve_df, cfg.band_min, cfg.band_max)
                    branch_src, dist_to_center = assign_branch(alpha_src, cfg.source_branches)

                    branch_center = None
                    if branch_src is not None:
                        for b in cfg.source_branches:
                            if b.id == branch_src:
                                branch_center = b.center
                                break

                    source_candidate_rows.append(
                        {
                            "run_id": run_id,
                            "t": t,
                            "p_family": p_family,
                            "theta": theta,
                            "packet_model": cfg.packet_family,
                            "source_feature": source_feature,
                            "p0": p0,
                            "sigma_p": sigma_p,
                            "alpha_candidate": alpha_src,
                            "candidate_value": cand_val,
                            "candidate_prominence": cand_prom,
                            "source_branch_id": branch_src,
                            "source_branch_center": branch_center,
                            "delta_to_branch_center": dist_to_center,
                        }
                    )

                    delta_alpha = None if alpha_src is None or alpha_rd is None else abs(alpha_src - alpha_rd)
                    branch_match_flag = int(branch_src is not None and branch_src == branch_rd)
                    alpha_match_flag = int(delta_alpha is not None and delta_alpha <= cfg.alpha_tolerance)

                    source_score = cand_prom or 0.0
                    loss_total = 0.0
                    loss_total += (delta_alpha if delta_alpha is not None else 10.0)
                    loss_total += cfg.branch_match_weight * (0 if branch_match_flag else 1)
                    loss_total -= cfg.alpha_match_weight * alpha_match_flag
                    loss_total -= cfg.source_score_weight * source_score
                    loss_total -= cfg.readout_score_weight * readout_score

                    fit_row = {
                        "run_id": run_id,
                        "t": t,
                        "p_family": p_family,
                        "theta": theta,
                        "packet_model": cfg.packet_family,
                        "source_feature": source_feature,
                        "p0": p0,
                        "sigma_p": sigma_p,
                        "alpha_pref_source_model": alpha_src,
                        "branch_pref_source_model": branch_src,
                        "source_score_model": source_score,
                        "alpha_pref_readout": alpha_rd,
                        "branch_pref_readout": branch_rd,
                        "readout_score": readout_score,
                        "delta_alpha": delta_alpha,
                        "branch_match_flag": branch_match_flag,
                        "alpha_match_flag": alpha_match_flag,
                        "loss_total": loss_total,
                    }
                    fit_grid_rows.append(fit_row)

                    if best_loss is None or loss_total < best_loss:
                        best_loss = loss_total
                        best_row = fit_row.copy()

        if best_row is not None:
            if best_row["branch_match_flag"] and best_row["alpha_match_flag"]:
                fit_label = "K2"
            elif best_row["alpha_match_flag"] or best_row["branch_match_flag"]:
                fit_label = "K1"
            else:
                fit_label = "K0"

            best_rows.append(
                {
                    "run_id": best_row["run_id"],
                    "t": best_row["t"],
                    "p_family": best_row["p_family"],
                    "theta": best_row["theta"],
                    "packet_model": best_row["packet_model"],
                    "source_feature": best_row["source_feature"],
                    "best_p0": best_row["p0"],
                    "best_sigma_p": best_row["sigma_p"],
                    "best_alpha_source": best_row["alpha_pref_source_model"],
                    "best_branch_source": best_row["branch_pref_source_model"],
                    "alpha_pref_readout": best_row["alpha_pref_readout"],
                    "branch_pref_readout": best_row["branch_pref_readout"],
                    "delta_alpha": best_row["delta_alpha"],
                    "branch_match_flag": best_row["branch_match_flag"],
                    "alpha_match_flag": best_row["alpha_match_flag"],
                    "best_loss_total": best_row["loss_total"],
                    "fit_label": fit_label,
                }
            )

    source_curve_df = pd.DataFrame(source_curve_rows, columns=SOURCE_CURVE_GRID_COLUMNS)
    source_candidate_df = pd.DataFrame(source_candidate_rows, columns=SOURCE_CANDIDATE_GRID_COLUMNS)
    fit_grid_df = pd.DataFrame(fit_grid_rows, columns=PACKET_FIT_GRID_COLUMNS)
    best_df = pd.DataFrame(best_rows, columns=PACKET_FIT_BEST_COLUMNS)

    freq_rows: List[Dict[str, Any]] = []
    if not best_df.empty:
        run_id = str(best_df["run_id"].iloc[0])

        def build_freq(level: str, key: str, group: pd.DataFrame) -> Dict[str, Any]:
            n_total = len(group)
            n_s1 = int((group["best_branch_source"] == "S1").sum())
            n_s2 = int((group["best_branch_source"] == "S2").sum())
            n_s3 = int((group["best_branch_source"] == "S3").sum())
            fracs = {
                "S1": n_s1 / n_total if n_total else 0.0,
                "S2": n_s2 / n_total if n_total else 0.0,
                "S3": n_s3 / n_total if n_total else 0.0,
            }
            dominant = None
            best_key = max(fracs, key=fracs.get)
            if fracs[best_key] >= 0.45:
                dominant = best_key
            return {
                "run_id": run_id,
                "aggregation_level": level,
                "aggregation_key": key,
                "n_total": n_total,
                "n_S1": n_s1,
                "n_S2": n_s2,
                "n_S3": n_s3,
                "frac_S1": fracs["S1"],
                "frac_S2": fracs["S2"],
                "frac_S3": fracs["S3"],
                "dominant_source_branch": dominant,
                "source_branch_entropy": entropy_from_fracs(fracs.values()),
            }

        freq_rows.append(build_freq("global", "global", best_df))
        for t, g in best_df.groupby("t"):
            freq_rows.append(build_freq("by_t", str(t), g))
        for pf, g in best_df.groupby("p_family"):
            freq_rows.append(build_freq("by_p_family", str(pf), g))
        for th, g in best_df.groupby("theta"):
            freq_rows.append(build_freq("by_theta", str(th), g))

    freq_df = pd.DataFrame(freq_rows, columns=PACKET_FREQUENCY_TABLE_COLUMNS)

    branch_match_frac = float(best_df["branch_match_flag"].mean()) if not best_df.empty else 0.0
    alpha_match_frac = float(best_df["alpha_match_flag"].mean()) if not best_df.empty else 0.0
    mean_delta_alpha = float(best_df["delta_alpha"].dropna().mean()) if "delta_alpha" in best_df and not best_df["delta_alpha"].dropna().empty else None

    if branch_match_frac >= 0.70 and alpha_match_frac >= 0.70:
        final_label = "K3"
    elif branch_match_frac >= 0.40 or alpha_match_frac >= 0.40:
        final_label = "K2"
    elif not best_df.empty:
        final_label = "K1"
    else:
        final_label = "K0"

    source_curve_df.to_csv(output_root / "source_curve_grid.csv", index=False)
    source_candidate_df.to_csv(output_root / "source_candidate_grid.csv", index=False)
    fit_grid_df.to_csv(output_root / "packet_fit_grid.csv", index=False)
    best_df.to_csv(output_root / "packet_fit_best.csv", index=False)
    freq_df.to_csv(output_root / "packet_frequency_table.csv", index=False)

    write_json(
        output_root / "packet_summary.json",
        {
            "final_label": final_label,
            "n_source_curve_rows": len(source_curve_df),
            "n_source_candidate_rows": len(source_candidate_df),
            "n_fit_grid_rows": len(fit_grid_df),
            "n_best_rows": len(best_df),
            "branch_match_frac": branch_match_frac,
            "alpha_match_frac": alpha_match_frac,
            "mean_delta_alpha": mean_delta_alpha,
        },
    )

    (output_root / "packet_report.md").write_text(
        "\n".join(
            [
                "# M.3.5b Packet Kernel Report",
                "",
                f"- final_label: {final_label}",
                f"- n_source_curve_rows: {len(source_curve_df)}",
                f"- n_source_candidate_rows: {len(source_candidate_df)}",
                f"- n_fit_grid_rows: {len(fit_grid_df)}",
                f"- n_best_rows: {len(best_df)}",
                f"- branch_match_frac: {branch_match_frac}",
                f"- alpha_match_frac: {alpha_match_frac}",
                f"- mean_delta_alpha: {mean_delta_alpha}",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    print(f"M.3.5b completed. Output written to: {output_root}")


if __name__ == "__main__":
    main()
