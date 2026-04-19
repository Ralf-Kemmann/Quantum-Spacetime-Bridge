from __future__ import annotations

import argparse, json, math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass(slots=True)
class BranchDef:
    id: str
    left: float
    right: float
    center: float


@dataclass(slots=True)
class M35cConfig:
    enabled: bool
    packet_fit_best: Path
    branches: List[BranchDef]
    sigma_branch: float
    sigma_tail: float
    mode: str
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
    return 0.0 if not vals else float(-sum(f * math.log(f) for f in vals))


def load_config(path: Path) -> M35cConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    block = raw["m35c_soft_branch"]
    branches = [BranchDef(**b) for b in block["branches"]]
    return M35cConfig(
        enabled=bool(block["enabled"]),
        packet_fit_best=Path(block["input"]["packet_fit_best"]),
        branches=branches,
        sigma_branch=float(block["soft_matching"]["sigma_branch"]),
        sigma_tail=float(block["soft_matching"]["sigma_tail"]),
        mode=str(block["soft_matching"]["mode"]),
        output_root=Path(block["output"]["root"]),
    )


def nearest_branch(alpha: Optional[float], branches: List[BranchDef]) -> Tuple[Optional[str], Dict[str, Optional[float]]]:
    dists = {b.id: None for b in branches}
    if alpha is None:
        return None, dists
    for b in branches:
        dists[b.id] = abs(alpha - b.center)
    bid = min(branches, key=lambda b: dists[b.id]).id
    return bid, dists


def membership(alpha: Optional[float], branch: BranchDef, mode: str, sigma_branch: float, sigma_tail: float) -> float:
    if alpha is None:
        return 0.0
    if mode == "gaussian_center":
        s = max(sigma_branch, 1e-9)
        return float(math.exp(-((alpha - branch.center) ** 2) / (2.0 * s * s)))
    if mode == "window_tail":
        if branch.left <= alpha <= branch.right:
            return 1.0
        d = branch.left - alpha if alpha < branch.left else alpha - branch.right
        s = max(sigma_tail, 1e-9)
        return float(math.exp(-(d * d) / (2.0 * s * s)))
    raise ValueError(f"Unsupported mode: {mode}")


def best_soft_branch(mu: Dict[str, float]) -> Optional[str]:
    if not mu:
        return None
    k, v = max(mu.items(), key=lambda kv: kv[1])
    return k if v > 0 else None


def frequency_table(df: pd.DataFrame, col: str, mode: str) -> pd.DataFrame:
    rows = []
    if df.empty:
        return pd.DataFrame(columns=[
            "run_id","aggregation_level","aggregation_key","n_total",
            "n_S1","n_S2","n_S3","frac_S1","frac_S2","frac_S3",
            "dominant_branch","branch_entropy","mode"
        ])
    run_id = str(df["run_id"].iloc[0])

    def build(level: str, key: str, g: pd.DataFrame) -> Dict[str, Any]:
        n_total = len(g)
        counts = {bid: int((g[col] == bid).sum()) for bid in ("S1","S2","S3")}
        fracs = {bid: (counts[bid] / n_total if n_total else 0.0) for bid in counts}
        dom = None
        best = max(fracs, key=fracs.get)
        if fracs[best] >= 0.45:
            dom = best
        return {
            "run_id": run_id,
            "aggregation_level": level,
            "aggregation_key": key,
            "n_total": n_total,
            "n_S1": counts["S1"],
            "n_S2": counts["S2"],
            "n_S3": counts["S3"],
            "frac_S1": fracs["S1"],
            "frac_S2": fracs["S2"],
            "frac_S3": fracs["S3"],
            "dominant_branch": dom,
            "branch_entropy": entropy_from_fracs(fracs.values()),
            "mode": mode,
        }

    rows.append(build("global","global",df))
    for t, g in df.groupby("t"):
        rows.append(build("by_t", str(t), g))
    for pf, g in df.groupby("p_family"):
        rows.append(build("by_p_family", str(pf), g))
    for th, g in df.groupby("theta"):
        rows.append(build("by_theta", str(th), g))
    return pd.DataFrame(rows)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.5c soft / nearest branch analysis")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    cfg = load_config(Path(args.config).resolve())
    if not cfg.enabled:
        print("M.3.5c disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    best_df = pd.read_csv(resolve_path(project_root, cfg.packet_fit_best))

    nearest_rows = []
    soft_rows = []
    summary_rows = []

    for _, row in best_df.iterrows():
        alpha_s = safe_float(row.get("best_alpha_source"))
        alpha_r = safe_float(row.get("alpha_pref_readout"))
        hard_s = row.get("best_branch_source")
        hard_r = row.get("branch_pref_readout")

        nbs, ds = nearest_branch(alpha_s, cfg.branches)
        nbr, dr = nearest_branch(alpha_r, cfg.branches)

        nearest_rows.append({
            "run_id": row["run_id"],
            "t": row["t"],
            "p_family": row["p_family"],
            "theta": row["theta"],
            "source_feature": row["source_feature"],
            "best_alpha_source": alpha_s,
            "hard_branch_source": hard_s,
            "hard_branch_readout": hard_r,
            "nearest_branch_source": nbs,
            "nearest_branch_readout": nbr,
            "dist_to_S1": ds.get("S1"),
            "dist_to_S2": ds.get("S2"),
            "dist_to_S3": ds.get("S3"),
            "nearest_branch_match_flag": int(nbs is not None and nbs == nbr),
            "hard_to_nearest_upgrade_flag": int((hard_s != hard_r) and (nbs == nbr)),
        })

        mu_s = {b.id: membership(alpha_s, b, cfg.mode, cfg.sigma_branch, cfg.sigma_tail) for b in cfg.branches}
        mu_r = {b.id: membership(alpha_r, b, cfg.mode, cfg.sigma_branch, cfg.sigma_tail) for b in cfg.branches}
        overlap = sum(mu_s[b.id] * mu_r[b.id] for b in cfg.branches)
        sbs = best_soft_branch(mu_s)
        sbr = best_soft_branch(mu_r)

        soft_rows.append({
            "run_id": row["run_id"],
            "t": row["t"],
            "p_family": row["p_family"],
            "theta": row["theta"],
            "source_feature": row["source_feature"],
            "best_alpha_source": alpha_s,
            "alpha_pref_readout": alpha_r,
            "mu_S1_source": mu_s.get("S1", 0.0),
            "mu_S2_source": mu_s.get("S2", 0.0),
            "mu_S3_source": mu_s.get("S3", 0.0),
            "mu_S1_readout": mu_r.get("S1", 0.0),
            "mu_S2_readout": mu_r.get("S2", 0.0),
            "mu_S3_readout": mu_r.get("S3", 0.0),
            "soft_overlap_score": overlap,
            "soft_best_branch_source": sbs,
            "soft_best_branch_readout": sbr,
            "soft_branch_match_flag": int(sbs is not None and sbs == sbr),
        })

        hard_match = int(row.get("branch_match_flag", 0))
        nearest_match = int(nbs is not None and nbs == nbr)
        soft_match = int(sbs is not None and sbs == sbr)
        hard_delta = abs(alpha_s - alpha_r) if alpha_s is not None and alpha_r is not None else None
        centers = {b.id: b.center for b in cfg.branches}
        nearest_delta_center = abs(alpha_s - centers[nbs]) if alpha_s is not None and nbs in centers else None

        if hard_match == 0 and nearest_match == 1 and soft_match == 1:
            upgrade = "hard_to_both"
        elif hard_match == 0 and nearest_match == 1:
            upgrade = "hard_to_nearest"
        elif hard_match == 0 and soft_match == 1:
            upgrade = "hard_to_soft"
        else:
            upgrade = "none"

        summary_rows.append({
            "run_id": row["run_id"],
            "t": row["t"],
            "p_family": row["p_family"],
            "theta": row["theta"],
            "source_feature": row["source_feature"],
            "hard_branch_match_flag": hard_match,
            "nearest_branch_match_flag": nearest_match,
            "soft_branch_match_flag": soft_match,
            "hard_delta_alpha": hard_delta,
            "nearest_delta_center": nearest_delta_center,
            "soft_overlap_score": overlap,
            "upgrade_label": upgrade,
        })

    nearest_df = pd.DataFrame(nearest_rows)
    soft_df = pd.DataFrame(soft_rows)
    summary_df = pd.DataFrame(summary_rows)

    hard_freq_df = frequency_table(best_df.rename(columns={"best_branch_source":"branch_col"}), "branch_col", "hard")
    nearest_freq_df = frequency_table(nearest_df.rename(columns={"nearest_branch_source":"branch_col"}), "branch_col", "nearest")
    soft_freq_df = frequency_table(soft_df.rename(columns={"soft_best_branch_source":"branch_col"}), "branch_col", "soft_best")
    freq_df = pd.concat([hard_freq_df, nearest_freq_df, soft_freq_df], ignore_index=True)

    hard_match_frac = float(best_df["branch_match_flag"].mean()) if not best_df.empty else 0.0
    nearest_match_frac = float(nearest_df["nearest_branch_match_flag"].mean()) if not nearest_df.empty else 0.0
    soft_match_frac = float(soft_df["soft_branch_match_flag"].mean()) if not soft_df.empty else 0.0
    soft_overlap_mean = float(soft_df["soft_overlap_score"].mean()) if not soft_df.empty else 0.0

    hard_misses = summary_df[summary_df["hard_branch_match_flag"] == 0]
    upgrade_rate = float(hard_misses["nearest_branch_match_flag"].mean()) if not hard_misses.empty else 0.0

    if nearest_match_frac - hard_match_frac >= 0.15 and soft_overlap_mean >= 0.6:
        final_label = "C3"
    elif nearest_match_frac - hard_match_frac >= 0.15:
        final_label = "C2"
    elif nearest_match_frac > hard_match_frac or soft_match_frac > hard_match_frac:
        final_label = "C1"
    else:
        final_label = "C0"

    nearest_df.to_csv(out_root / "nearest_branch_assignment.csv", index=False)
    soft_df.to_csv(out_root / "soft_branch_scores.csv", index=False)
    summary_df.to_csv(out_root / "soft_branch_summary.csv", index=False)
    freq_df.to_csv(out_root / "soft_branch_frequency_table.csv", index=False)

    write_json(out_root / "soft_branch_summary.json", {
        "final_label": final_label,
        "n_best_rows": len(best_df),
        "hard_branch_match_frac": hard_match_frac,
        "nearest_branch_match_frac": nearest_match_frac,
        "soft_branch_match_frac": soft_match_frac,
        "soft_overlap_mean": soft_overlap_mean,
        "upgrade_rate": upgrade_rate,
    })

    (out_root / "soft_branch_report.md").write_text(
        "\n".join([
            "# M.3.5c Soft / Nearest Branch Report",
            "",
            f"- final_label: {final_label}",
            f"- n_best_rows: {len(best_df)}",
            f"- hard_branch_match_frac: {hard_match_frac}",
            f"- nearest_branch_match_frac: {nearest_match_frac}",
            f"- soft_branch_match_frac: {soft_match_frac}",
            f"- soft_overlap_mean: {soft_overlap_mean}",
            f"- upgrade_rate: {upgrade_rate}",
        ]) + "\n",
        encoding="utf-8",
    )

    print(f"M.3.5c completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
