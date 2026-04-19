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


@dataclass(slots=True)
class AuditCase:
    t: float
    p_family: str
    theta: float


@dataclass(slots=True)
class M36aConfig:
    enabled: bool
    packet_fit_best: Path
    source_pair_kernel: Path
    audit_cases: List[AuditCase]
    class_modes: List[str]
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


def load_config(path: Path) -> M36aConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m36a_pair_audit"]
    cases = [
        AuditCase(
            t=float(c["t"]),
            p_family=str(c["p_family"]),
            theta=float(c["theta"]),
        )
        for c in block["selection"]["audit_cases"]
    ]
    return M36aConfig(
        enabled=bool(block["enabled"]),
        packet_fit_best=Path(block["input"]["packet_fit_best"]),
        source_pair_kernel=Path(block["input"]["source_pair_kernel"]),
        audit_cases=cases,
        class_modes=list(block["grouping"]["class_modes"]),
        output_root=Path(block["output"]["root"]),
    )


def load_full_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def gaussian_probabilities(p_values: np.ndarray, p0: float, sigma_p: float) -> np.ndarray:
    sigma = max(float(sigma_p), 1.0e-12)
    amp = np.exp(-((p_values - p0) ** 2) / (4.0 * sigma * sigma))
    prob = amp ** 2
    s = prob.sum()
    if s <= 0:
        return np.full_like(prob, 1.0 / len(prob))
    return prob / s


def infer_p_values_for_family(p_family: str, raw_cfg: Dict[str, Any]) -> np.ndarray:
    fam = raw_cfg["p_sets"]["families"][p_family]
    return np.asarray(fam["p_values"], dtype=float)


def infer_pair_index_base(pair_df: pd.DataFrame, n_modes: int) -> int:
    vals = pd.concat([pair_df["pair_i"], pair_df["pair_j"]], ignore_index=True).dropna().astype(int)
    if vals.empty:
        return 0
    mn = int(vals.min())
    mx = int(vals.max())
    if mn >= 1 and mx <= n_modes:
        return 1
    return 0


def pair_weights_from_best_fit(
    pair_df: pd.DataFrame,
    p_values: np.ndarray,
    p0: float,
    sigma_p: float,
) -> Dict[Tuple[int, int], float]:
    prob = gaussian_probabilities(p_values, p0, sigma_p)
    idx_base = infer_pair_index_base(pair_df, len(p_values))
    weights: Dict[Tuple[int, int], float] = {}

    pairs = (
        pair_df[["pair_i", "pair_j"]]
        .drop_duplicates()
        .dropna()
        .astype(int)
        .itertuples(index=False, name=None)
    )
    for pair_i, pair_j in pairs:
        i = int(pair_i) - idx_base
        j = int(pair_j) - idx_base
        if 0 <= i < len(prob) and 0 <= j < len(prob):
            weights[(int(pair_i), int(pair_j))] = float(prob[i] * prob[j])

    norm = sum(weights.values())
    if norm > 0:
        weights = {k: v / norm for k, v in weights.items()}
    return weights


def contribution_triplet(source_feature: str, weight: float, kbar: float) -> Tuple[float, float, float, float]:
    contrib_neg = weight * max(-kbar, 0.0)
    contrib_abs = weight * abs(kbar)
    contrib_signed = weight * kbar

    if source_feature == "neg":
        contrib_primary = contrib_neg
    elif source_feature == "abs":
        contrib_primary = contrib_abs
    else:
        # fallback for future feature variants
        contrib_primary = contrib_abs
    return contrib_neg, contrib_abs, contrib_signed, contrib_primary


def top_share(normed: np.ndarray, n: int) -> float:
    if normed.size == 0:
        return 0.0
    return float(normed[: min(n, normed.size)].sum())


def effective_pair_count(normed: np.ndarray) -> float:
    if normed.size == 0:
        return 0.0
    denom = float(np.sum(normed ** 2))
    if denom <= 0:
        return 0.0
    return 1.0 / denom


def dominance_label(top3_share_value: float, n_eff_value: float) -> str:
    if top3_share_value > 0.7:
        return "pair_dominated"
    if n_eff_value >= 6:
        return "collective"
    return "mixed"


def class_label_from_row(row: pd.Series, class_mode: str) -> str:
    if class_mode == "delta_p":
        return f"dp={row['delta_p']:.6g}"
    if class_mode == "delta_p2":
        return f"dp2={row['delta_p2']:.6g}"
    raise ValueError(f"Unsupported class_mode: {class_mode}")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.6a pair-contribution audit")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.6a disabled in config. Exiting.")
        return

    raw_cfg = load_full_yaml(config_path)

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    best_df = pd.read_csv(resolve_path(project_root, cfg.packet_fit_best))
    pair_df = pd.read_csv(resolve_path(project_root, cfg.source_pair_kernel))

    required_pair_cols = {"run_id", "t", "p_family", "alpha", "pair_i", "pair_j", "kbar_ij"}
    missing = required_pair_cols - set(pair_df.columns)
    if missing:
        raise ValueError(f"source_pair_kernel missing required columns: {sorted(missing)}")

    if "p_i" not in pair_df.columns or "p_j" not in pair_df.columns:
        raise ValueError("source_pair_kernel must contain p_i and p_j for M.3.6a")

    pair_rows: List[Dict[str, Any]] = []
    top_rows: List[Dict[str, Any]] = []
    class_rows: List[Dict[str, Any]] = []

    n_cases = 0

    for case in cfg.audit_cases:
        sel = best_df[
            (best_df["t"].astype(float) == case.t)
            & (best_df["p_family"] == case.p_family)
            & (best_df["theta"].astype(float) == case.theta)
        ].copy()

        if sel.empty:
            continue

        # One best row per audit case
        row = sel.sort_values("best_loss_total", ascending=True, na_position="last").iloc[0]
        n_cases += 1

        run_id = str(row["run_id"])
        t = float(row["t"])
        p_family = str(row["p_family"])
        theta = float(row["theta"])
        source_feature = str(row["source_feature"])
        best_p0 = float(row["best_p0"])
        best_sigma_p = float(row["best_sigma_p"])
        best_alpha_source = float(row["best_alpha_source"])
        best_branch_source = row.get("best_branch_source")
        alpha_pref_readout = float(row["alpha_pref_readout"])
        branch_pref_readout = row.get("branch_pref_readout")

        pair_slice = pair_df[
            (pair_df["run_id"] == run_id)
            & (pair_df["t"].astype(float) == t)
            & (pair_df["p_family"] == p_family)
            & (pair_df["alpha"].astype(float) == best_alpha_source)
        ].copy()

        if pair_slice.empty:
            continue

        p_values = infer_p_values_for_family(p_family, raw_cfg)
        weights = pair_weights_from_best_fit(pair_slice, p_values, best_p0, best_sigma_p)

        local_rows: List[Dict[str, Any]] = []
        for prow in pair_slice.itertuples(index=False):
            key = (int(prow.pair_i), int(prow.pair_j))
            w = float(weights.get(key, 0.0))
            kbar = float(prow.kbar_ij)
            p_i = float(prow.p_i)
            p_j = float(prow.p_j)
            delta_p = p_i - p_j
            delta_p2 = (p_i ** 2) - (p_j ** 2)

            contrib_neg, contrib_abs, contrib_signed, contrib_primary = contribution_triplet(
                source_feature=source_feature,
                weight=w,
                kbar=kbar,
            )

            local_rows.append(
                {
                    "run_id": run_id,
                    "t": t,
                    "p_family": p_family,
                    "theta": theta,
                    "source_feature": source_feature,
                    "best_p0": best_p0,
                    "best_sigma_p": best_sigma_p,
                    "best_alpha_source": best_alpha_source,
                    "best_branch_source": best_branch_source,
                    "alpha_pref_readout": alpha_pref_readout,
                    "branch_pref_readout": branch_pref_readout,
                    "pair_i": int(prow.pair_i),
                    "pair_j": int(prow.pair_j),
                    "p_i": p_i,
                    "p_j": p_j,
                    "delta_p": delta_p,
                    "delta_p2": delta_p2,
                    "pair_weight": w,
                    "kbar_ij": kbar,
                    "kbar_abs_ij": abs(kbar),
                    "kbar_sign": int(np.sign(kbar)),
                    "contrib_neg": contrib_neg,
                    "contrib_abs": contrib_abs,
                    "contrib_signed": contrib_signed,
                    "contrib_primary": contrib_primary,
                }
            )

        local_df = pd.DataFrame(local_rows).sort_values("contrib_primary", ascending=False).reset_index(drop=True)
        primary_sum = float(local_df["contrib_primary"].sum())
        if primary_sum > 0:
            normed = (local_df["contrib_primary"] / primary_sum).to_numpy(dtype=float)
            local_df["pair_rank_primary"] = np.arange(1, len(local_df) + 1)
            local_df["cumulative_primary"] = np.cumsum(normed)
        else:
            normed = np.zeros(len(local_df), dtype=float)
            local_df["pair_rank_primary"] = np.arange(1, len(local_df) + 1)
            local_df["cumulative_primary"] = 0.0

        pair_rows.extend(local_df.to_dict(orient="records"))

        top1 = top_share(normed, 1)
        top3 = top_share(normed, 3)
        top5 = top_share(normed, 5)
        top10 = top_share(normed, 10)
        n_eff = effective_pair_count(normed)
        top_rows.append(
            {
                "run_id": run_id,
                "t": t,
                "p_family": p_family,
                "theta": theta,
                "source_feature": source_feature,
                "best_p0": best_p0,
                "best_sigma_p": best_sigma_p,
                "best_alpha_source": best_alpha_source,
                "best_branch_source": best_branch_source,
                "alpha_pref_readout": alpha_pref_readout,
                "branch_pref_readout": branch_pref_readout,
                "n_pairs_total": int(len(local_df)),
                "top1_share": top1,
                "top3_share": top3,
                "top5_share": top5,
                "top10_share": top10,
                "effective_pair_count": n_eff,
                "dominance_label": dominance_label(top3, n_eff),
            }
        )

        for class_mode in cfg.class_modes:
            tmp = local_df.copy()
            tmp["class_mode"] = class_mode
            tmp["class_label"] = tmp.apply(lambda r: class_label_from_row(r, class_mode), axis=1)

            grouped = (
                tmp.groupby(["class_mode", "class_label"], dropna=False)
                .agg(
                    n_pairs_in_class=("pair_i", "count"),
                    sum_pair_weight=("pair_weight", "sum"),
                    sum_contrib_primary=("contrib_primary", "sum"),
                    mean_contrib_primary=("contrib_primary", "mean"),
                    max_contrib_primary=("contrib_primary", "max"),
                )
                .reset_index()
                .sort_values("sum_contrib_primary", ascending=False)
                .reset_index(drop=True)
            )

            total_class = float(grouped["sum_contrib_primary"].sum())
            grouped["class_rank"] = np.arange(1, len(grouped) + 1)
            if total_class > 0:
                grouped["cumulative_class_contrib"] = grouped["sum_contrib_primary"].cumsum() / total_class
            else:
                grouped["cumulative_class_contrib"] = 0.0

            for grow in grouped.itertuples(index=False):
                class_rows.append(
                    {
                        "run_id": run_id,
                        "t": t,
                        "p_family": p_family,
                        "theta": theta,
                        "source_feature": source_feature,
                        "class_mode": grow.class_mode,
                        "class_label": grow.class_label,
                        "n_pairs_in_class": int(grow.n_pairs_in_class),
                        "sum_pair_weight": float(grow.sum_pair_weight),
                        "sum_contrib_primary": float(grow.sum_contrib_primary),
                        "mean_contrib_primary": float(grow.mean_contrib_primary),
                        "max_contrib_primary": float(grow.max_contrib_primary),
                        "class_rank": int(grow.class_rank),
                        "cumulative_class_contrib": float(grow.cumulative_class_contrib),
                    }
                )

    pair_df_out = pd.DataFrame(pair_rows)
    top_df = pd.DataFrame(top_rows)
    class_df = pd.DataFrame(class_rows)

    if not top_df.empty:
        median_top3 = float(top_df["top3_share"].median())
        median_neff = float(top_df["effective_pair_count"].median())
        dominant_mechanism = "pair_family" if median_neff >= 6 else "few_pairs"
    else:
        median_top3 = None
        median_neff = None
        dominant_mechanism = None

    if not class_df.empty:
        primary_class_mode_supported = (
            class_df.groupby("class_mode")["sum_contrib_primary"].sum().sort_values(ascending=False).index[0]
        )
    else:
        primary_class_mode_supported = None

    summary = {
        "n_audit_cases": n_cases,
        "dominant_mechanism": dominant_mechanism,
        "median_top3_share": median_top3,
        "median_effective_pair_count": median_neff,
        "primary_class_mode_supported": primary_class_mode_supported,
    }

    pair_df_out.to_csv(out_root / "pair_contributions.csv", index=False)
    top_df.to_csv(out_root / "pair_top_summary.csv", index=False)
    class_df.to_csv(out_root / "pair_class_summary.csv", index=False)
    write_json(out_root / "pair_audit_summary.json", summary)

    report_lines = [
        "# M.3.6a Pair Audit Report",
        "",
        f"- n_audit_cases: {safe_json_value(summary['n_audit_cases'])}",
        f"- dominant_mechanism: {safe_json_value(summary['dominant_mechanism'])}",
        f"- median_top3_share: {safe_json_value(summary['median_top3_share'])}",
        f"- median_effective_pair_count: {safe_json_value(summary['median_effective_pair_count'])}",
        f"- primary_class_mode_supported: {safe_json_value(summary['primary_class_mode_supported'])}",
    ]
    (out_root / "pair_audit_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.6a completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
