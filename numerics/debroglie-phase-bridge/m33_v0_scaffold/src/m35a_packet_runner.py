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

from columns_m35a_packet import (
    PACKET_BRANCH_ALIGNMENT_COLUMNS,
    PACKET_FIT_BEST_COLUMNS,
    PACKET_FIT_GRID_COLUMNS,
    PACKET_FREQUENCY_TABLE_COLUMNS,
)


@dataclass(slots=True)
class BranchDef:
    id: str
    left: float
    right: float
    center: float


@dataclass(slots=True)
class M35aConfig:
    enabled: bool
    source_kernel: Path
    readout_summary: Path
    branch_assignment: Path
    exclude_t0: bool
    allowed_readout_labels: List[str]
    source_features: List[str]
    candidate_scope: str
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
    dominant_source_branch_min_fraction: float
    output_root: Path


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def safe_float(x: Any) -> Optional[float]:
    try:
        val = float(x)
        if not np.isfinite(val):
            return None
        return val
    except Exception:
        return None


def safe_json_value(x: Any) -> Any:
    if isinstance(x, (np.floating, float)):
        if not np.isfinite(x):
            return None
        return float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if pd.isna(x):
        return None
    return x


def load_config(path: Path) -> M35aConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m35a_packet_model"]
    branches = [BranchDef(**b) for b in block["source_branches"]]

    return M35aConfig(
        enabled=bool(block["enabled"]),
        source_kernel=Path(block["input"]["source_kernel"]),
        readout_summary=Path(block["input"]["readout_summary"]),
        branch_assignment=Path(block["input"]["branch_assignment"]),
        exclude_t0=bool(block["selection"]["exclude_t0"]),
        allowed_readout_labels=list(block["selection"]["allowed_readout_labels"]),
        source_features=list(block["selection"]["source_features"]),
        candidate_scope=str(block["selection"]["candidate_scope"]),
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
        dominant_source_branch_min_fraction=float(block["thresholds"]["dominant_source_branch_min_fraction"]),
        output_root=Path(block["output"]["root"]),
    )


def gaussian_packet_weights(p_values: np.ndarray, p0: float, sigma_p: float) -> np.ndarray:
    sigma = max(float(sigma_p), 1.0e-9)
    amp = np.exp(-((p_values - p0) ** 2) / (4.0 * sigma * sigma))
    prob = amp ** 2
    s = prob.sum()
    if s <= 0:
        return np.full_like(prob, 1.0 / len(prob))
    return prob / s


def pair_weights_from_prob(prob: np.ndarray) -> Dict[Tuple[int, int], float]:
    out: Dict[Tuple[int, int], float] = {}
    n = len(prob)
    for i in range(n):
        for j in range(i + 1, n):
            out[(i, j)] = float(prob[i] * prob[j])
    norm = sum(out.values())
    if norm > 0:
        out = {k: v / norm for k, v in out.items()}
    return out


def assign_branch(alpha: Optional[float], branches: List[BranchDef]) -> Optional[str]:
    if alpha is None:
        return None
    for b in branches:
        if b.left <= alpha <= b.right:
            return b.id
    return None


def infer_p_values_for_family(p_family: str, config_raw: Dict[str, Any]) -> np.ndarray:
    fam = config_raw["p_sets"]["families"][p_family]
    return np.asarray(fam["p_values"], dtype=float)


def build_pair_feature_table(source_kernel_df: pd.DataFrame, p_values: np.ndarray, t: float, p_family: str) -> pd.DataFrame:
    # Minimaler Skeleton:
    # Wir haben aktuell keine explizite alpha-resolved pair table aus kernel_sign_stats.csv.
    # Deshalb nutzen wir vorläufig nur alpha-resolved readout-side targeting und
    # erzeugen ein einfaches modelliertes Source-Surrogat über branch-aligned alpha reference.
    #
    # Sobald eine alpha-resolved source pair matrix vorliegt, wird diese Funktion ersetzt.
    return pd.DataFrame({
        "pair_i": [],
        "pair_j": [],
        "alpha": [],
        "kbar_ij": [],
    })


def build_model_source_curve(
    alpha_grid: np.ndarray,
    p_values: np.ndarray,
    p0: float,
    sigma_p: float,
    feature_mode: str,
) -> pd.DataFrame:
    # Minimales heuristisches Source-Surrogat:
    # packet weights erzeugen ein effektives Zentrum/Spread im Paarraum.
    # Das ist bewusst noch ein Skeleton, aber strukturell korrekt.
    prob = gaussian_packet_weights(p_values, p0, sigma_p)
    pair_w = pair_weights_from_prob(prob)

    pair_scale = 0.0
    for (i, j), w in pair_w.items():
        pair_scale += w * abs((p_values[i] ** 2) - (p_values[j] ** 2))

    pair_scale = max(pair_scale, 1.0e-9)

    if feature_mode == "neg":
        values = np.exp(-((alpha_grid - (1.35 + 0.10 * pair_scale)) ** 2) / (2.0 * (0.10 + 0.05 * sigma_p) ** 2))
    else:
        values = np.exp(-((alpha_grid - (1.55 + 0.05 * pair_scale)) ** 2) / (2.0 * (0.12 + 0.04 * sigma_p) ** 2))

    return pd.DataFrame({
        "alpha": alpha_grid,
        "source_value": values,
    })


def find_local_max_in_band(curve_df: pd.DataFrame, band_min: float, band_max: float) -> Tuple[Optional[float], Optional[float]]:
    sub = curve_df[(curve_df["alpha"] >= band_min) & (curve_df["alpha"] <= band_max)].copy()
    if sub.empty:
        return None, None

    sub = sub.sort_values("alpha").reset_index(drop=True)
    vals = sub["source_value"].to_numpy(dtype=float)
    alphas = sub["alpha"].to_numpy(dtype=float)

    candidates: List[Tuple[float, float]] = []
    for i in range(1, len(sub) - 1):
        if vals[i] > vals[i - 1] and vals[i] > vals[i + 1]:
            prom = vals[i] - 0.5 * (vals[i - 1] + vals[i + 1])
            candidates.append((alphas[i], prom))

    if not candidates:
        idx = int(np.argmax(vals))
        return float(alphas[idx]), 0.0

    best = max(candidates, key=lambda x: x[1])
    return float(best[0]), float(best[1])


def entropy_from_fracs(fracs: Iterable[float]) -> float:
    vals = [f for f in fracs if f > 0]
    if not vals:
        return 0.0
    return float(-sum(f * math.log(f) for f in vals))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.5a minimal packet model runner")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.5a disabled in config. Exiting.")
        return

    with config_path.open("r", encoding="utf-8") as f:
        raw_cfg = yaml.safe_load(f)

    output_root = resolve_path(project_root, cfg.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    source_kernel_df = pd.read_csv(resolve_path(project_root, cfg.source_kernel))
    readout_summary_df = pd.read_csv(resolve_path(project_root, cfg.readout_summary))
    branch_assignment_df = pd.read_csv(resolve_path(project_root, cfg.branch_assignment))

    if cfg.exclude_t0:
        readout_summary_df = readout_summary_df[readout_summary_df["t"] > 0].copy()

    readout_summary_df = readout_summary_df[
        readout_summary_df["readout_label"].isin(cfg.allowed_readout_labels)
    ].copy()

    alpha_grid = np.sort(readout_summary_df["preferred_alpha_coherent"].dropna().astype(float).unique())
    if alpha_grid.size == 0:
        alpha_grid = np.linspace(cfg.band_min, cfg.band_max, 31)

    grid_rows: List[Dict[str, Any]] = []
    best_rows: List[Dict[str, Any]] = []
    align_rows: List[Dict[str, Any]] = []

    for _, rd in readout_summary_df.iterrows():
        t = float(rd["t"])
        p_family = str(rd["p_family"])
        theta = float(rd["theta"])
        alpha_rd = safe_float(rd.get("preferred_alpha_coherent"))
        branch_rd = assign_branch(alpha_rd, cfg.source_branches)
        rd_score = safe_float(rd.get("preferred_coherence_score")) or 0.0

        p_values = infer_p_values_for_family(p_family, raw_cfg)

        best_loss = None
        best_row = None

        for source_feature in cfg.source_features:
            for p0 in cfg.p0_grid:
                for sigma_p in cfg.sigma_p_grid:
                    curve_df = build_model_source_curve(alpha_grid, p_values, p0, sigma_p, source_feature)
                    alpha_src, src_score = find_local_max_in_band(curve_df, cfg.band_min, cfg.band_max)
                    branch_src = assign_branch(alpha_src, cfg.source_branches)

                    delta_alpha = None if alpha_src is None or alpha_rd is None else abs(alpha_src - alpha_rd)
                    branch_match_flag = int(branch_src is not None and branch_src == branch_rd)
                    alpha_match_flag = int(delta_alpha is not None and delta_alpha <= cfg.alpha_tolerance)

                    loss_total = 0.0
                    if delta_alpha is not None:
                        loss_total += delta_alpha
                    else:
                        loss_total += 10.0

                    loss_total += cfg.branch_match_weight * (0 if branch_match_flag else 1)
                    loss_total -= cfg.source_score_weight * (src_score or 0.0)
                    loss_total -= cfg.readout_score_weight * rd_score
                    loss_total -= cfg.alpha_match_weight * alpha_match_flag

                    row = {
                        "run_id": rd["run_id"],
                        "t": t,
                        "p_family": p_family,
                        "theta": theta,
                        "packet_model": cfg.packet_family,
                        "source_feature": source_feature,
                        "p0": p0,
                        "sigma_p": sigma_p,
                        "alpha_pref_source_model": alpha_src,
                        "branch_pref_source_model": branch_src,
                        "source_score_model": src_score,
                        "alpha_pref_readout": alpha_rd,
                        "branch_pref_readout": branch_rd,
                        "readout_score": rd_score,
                        "delta_alpha": delta_alpha,
                        "branch_match_flag": branch_match_flag,
                        "alpha_match_flag": alpha_match_flag,
                        "loss_total": loss_total,
                    }
                    grid_rows.append(row)

                    if best_loss is None or loss_total < best_loss:
                        best_loss = loss_total
                        best_row = row.copy()

        if best_row is not None:
            fit_label = "P2" if best_row["branch_match_flag"] and best_row["alpha_match_flag"] else "P1"
            best_rows.append({
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
            })

            align_rows.append({
                "run_id": best_row["run_id"],
                "t": best_row["t"],
                "p_family": best_row["p_family"],
                "theta": best_row["theta"],
                "source_feature": best_row["source_feature"],
                "best_branch_source": best_row["branch_pref_source_model"],
                "branch_pref_readout": best_row["branch_pref_readout"],
                "branch_match_flag": best_row["branch_match_flag"],
                "best_alpha_source": best_row["alpha_pref_source_model"],
                "alpha_pref_readout": best_row["alpha_pref_readout"],
                "delta_alpha": best_row["delta_alpha"],
                "alpha_match_flag": best_row["alpha_match_flag"],
                "fit_label": fit_label,
            })

    grid_df = pd.DataFrame(grid_rows, columns=PACKET_FIT_GRID_COLUMNS)
    best_df = pd.DataFrame(best_rows, columns=PACKET_FIT_BEST_COLUMNS)
    align_df = pd.DataFrame(align_rows, columns=PACKET_BRANCH_ALIGNMENT_COLUMNS)

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
            if fracs[best_key] >= cfg.dominant_source_branch_min_fraction:
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

    branch_match_frac = float(align_df["branch_match_flag"].mean()) if not align_df.empty else 0.0
    alpha_match_frac = float(align_df["alpha_match_flag"].mean()) if not align_df.empty else 0.0

    final_label = "P0"
    if branch_match_frac >= 0.40 or alpha_match_frac >= 0.40:
        final_label = "P2"
    elif not best_df.empty:
        final_label = "P1"

    grid_df.to_csv(output_root / "packet_fit_grid.csv", index=False)
    best_df.to_csv(output_root / "packet_fit_best.csv", index=False)
    align_df.to_csv(output_root / "packet_branch_alignment.csv", index=False)
    freq_df.to_csv(output_root / "packet_frequency_table.csv", index=False)

    write_json(
        output_root / "packet_summary.json",
        {
            "final_label": final_label,
            "n_grid_rows": len(grid_df),
            "n_best_rows": len(best_df),
            "branch_match_frac": branch_match_frac,
            "alpha_match_frac": alpha_match_frac,
        },
    )

    (output_root / "packet_report.md").write_text(
        "\n".join(
            [
                "# M.3.5a Packet Model Report",
                "",
                f"- final_label: {final_label}",
                f"- n_grid_rows: {len(grid_df)}",
                f"- n_best_rows: {len(best_df)}",
                f"- branch_match_frac: {branch_match_frac}",
                f"- alpha_match_frac: {alpha_match_frac}",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    print(f"M.3.5a completed. Output written to: {output_root}")


if __name__ == "__main__":
    main()
