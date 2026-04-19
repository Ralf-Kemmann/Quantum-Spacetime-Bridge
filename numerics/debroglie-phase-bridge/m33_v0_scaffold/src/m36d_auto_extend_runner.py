from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass(slots=True)
class M36dConfig:
    enabled: bool
    nearest_branch_assignment: Path
    soft_branch_scores: Path
    soft_branch_summary: Path
    packet_fit_best: Path
    source_pair_kernel: Path
    pair_top_summary_existing: Path
    pair_contributions_existing: Path
    pair_class_summary_existing: Path
    branch_basis: str
    target_cases_per_branch: int
    require_nearest_match: bool
    require_soft_match: bool
    ranking_primary: str
    ranking_secondary: str
    class_modes: List[str]
    output_root: Path


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def safe_json_value(x: Any) -> Any:
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if pd.isna(x):
        return None
    return x


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def case_label_from_row(row: pd.Series) -> str:
    return f"t={row.get('t')}__pf={row.get('p_family')}__th={row.get('theta')}"


def attach_case_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["case_label"] = out.apply(case_label_from_row, axis=1)
    return out


def load_config(path: Path) -> M36dConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m36d_auto_extend"]
    return M36dConfig(
        enabled=bool(block["enabled"]),
        nearest_branch_assignment=Path(block["input"]["nearest_branch_assignment"]),
        soft_branch_scores=Path(block["input"]["soft_branch_scores"]),
        soft_branch_summary=Path(block["input"]["soft_branch_summary"]),
        packet_fit_best=Path(block["input"]["packet_fit_best"]),
        source_pair_kernel=Path(block["input"]["source_pair_kernel"]),
        pair_top_summary_existing=Path(block["input"]["pair_top_summary_existing"]),
        pair_contributions_existing=Path(block["input"]["pair_contributions_existing"]),
        pair_class_summary_existing=Path(block["input"]["pair_class_summary_existing"]),
        branch_basis=str(block["selection"]["branch_basis"]),
        target_cases_per_branch=int(block["selection"]["target_cases_per_branch"]),
        require_nearest_match=bool(block["selection"]["require_nearest_match"]),
        require_soft_match=bool(block["selection"]["require_soft_match"]),
        ranking_primary=str(block["selection"]["ranking_primary"]),
        ranking_secondary=str(block["selection"]["ranking_secondary"]),
        class_modes=[str(x) for x in block["grouping"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )


def infer_pair_index_base(pair_df: pd.DataFrame, n_modes: int) -> int:
    vals = pd.concat([pair_df["pair_i"], pair_df["pair_j"]], ignore_index=True).dropna().astype(int)
    if vals.empty:
        return 0
    mn = int(vals.min())
    mx = int(vals.max())
    if mn >= 1 and mx <= n_modes:
        return 1
    return 0


def infer_p_values_for_family(raw_cfg: Dict[str, Any], p_family: str) -> np.ndarray:
    fam = raw_cfg["p_sets"]["families"][p_family]
    return np.asarray(fam["p_values"], dtype=float)


def gaussian_probabilities(p_values: np.ndarray, p0: float, sigma_p: float) -> np.ndarray:
    sigma = max(float(sigma_p), 1.0e-12)
    amp = np.exp(-((p_values - p0) ** 2) / (4.0 * sigma * sigma))
    prob = amp ** 2
    s = float(prob.sum())
    return np.full_like(prob, 1.0 / len(prob), dtype=float) if s <= 0 else prob / s


def pair_weights_from_best_fit(pair_df: pd.DataFrame, p_values: np.ndarray, p0: float, sigma_p: float) -> Dict[Tuple[int, int], float]:
    prob = gaussian_probabilities(p_values, p0, sigma_p)
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
        if 0 <= i < len(prob) and 0 <= j < len(prob):
            weights[(int(pair_i), int(pair_j))] = float(prob[i] * prob[j])

    norm = float(sum(weights.values()))
    return {k: v / norm for k, v in weights.items()} if norm > 0 else weights


def contribution_triplet(source_feature: str, weight: float, kbar: float) -> Tuple[float, float, float, float]:
    contrib_neg = weight * max(-kbar, 0.0)
    contrib_abs = weight * abs(kbar)
    contrib_signed = weight * kbar
    primary = contrib_neg if source_feature == "neg" else contrib_abs
    return contrib_neg, contrib_abs, contrib_signed, primary


def top_share(normed: np.ndarray, n: int) -> float:
    return 0.0 if normed.size == 0 else float(normed[: min(n, normed.size)].sum())


def effective_pair_count(normed: np.ndarray) -> float:
    if normed.size == 0:
        return 0.0
    denom = float(np.sum(normed ** 2))
    return 0.0 if denom <= 0 else 1.0 / denom


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


def build_selection_table(nearest_df, soft_df, soft_summary_df, packet_fit_best_df, cfg: M36dConfig) -> pd.DataFrame:
    select_df = nearest_df.merge(
        soft_df[[
            "run_id", "t", "p_family", "theta", "source_feature", "case_label",
            "soft_best_branch_source", "soft_best_branch_readout",
            "soft_branch_match_flag", "soft_overlap_score",
        ]],
        on=["run_id", "t", "p_family", "theta", "source_feature", "case_label"],
        how="left",
    ).merge(
        soft_summary_df[[
            "run_id", "t", "p_family", "theta", "source_feature", "case_label",
            "hard_delta_alpha", "nearest_branch_match_flag", "soft_branch_match_flag",
        ]],
        on=["run_id", "t", "p_family", "theta", "source_feature", "case_label"],
        how="left",
        suffixes=("", "_summary"),
    ).merge(
        packet_fit_best_df[[
            "run_id", "t", "p_family", "theta", "source_feature",
            "best_p0", "best_sigma_p", "best_alpha_source",
            "best_branch_source", "alpha_pref_readout", "branch_pref_readout",
        ]],
        on=["run_id", "t", "p_family", "theta", "source_feature"],
        how="left",
    )

    if cfg.branch_basis not in select_df.columns:
        raise ValueError(f"branch_basis column not found: {cfg.branch_basis}")

    if cfg.require_nearest_match and "nearest_branch_match_flag" in select_df.columns:
        select_df = select_df[select_df["nearest_branch_match_flag"].fillna(0).astype(int) == 1].copy()

    if cfg.require_soft_match and "soft_branch_match_flag" in select_df.columns:
        select_df = select_df[select_df["soft_branch_match_flag"].fillna(0).astype(int) == 1].copy()

    return select_df


def audit_single_case(row, pair_kernel_df, raw_cfg, class_modes, branch_basis, branch_label):
    run_id = str(row["run_id"])
    t = float(row["t"])
    p_family = str(row["p_family"])
    theta = float(row["theta"])
    source_feature = str(row["source_feature"])
    best_p0 = float(row["best_p0"])
    best_sigma_p = float(row["best_sigma_p"])
    best_alpha_source = float(row["best_alpha_source"])
    best_branch_source = row.get("best_branch_source")
    alpha_pref_readout = row.get("alpha_pref_readout")
    branch_pref_readout = row.get("branch_pref_readout")
    case_label = row["case_label"]

    pair_slice = pair_kernel_df[
        (pair_kernel_df["run_id"] == run_id)
        & (pair_kernel_df["t"].astype(float) == t)
        & (pair_kernel_df["p_family"] == p_family)
        & (pair_kernel_df["alpha"].astype(float) == best_alpha_source)
    ].copy()

    if pair_slice.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    if "p_i" not in pair_slice.columns or "p_j" not in pair_slice.columns:
        raise ValueError("source_pair_kernel must contain p_i and p_j columns")

    p_values = infer_p_values_for_family(raw_cfg, p_family)
    weights = pair_weights_from_best_fit(pair_slice, p_values, best_p0, best_sigma_p)

    local_rows = []
    for prow in pair_slice.itertuples(index=False):
        key = (int(prow.pair_i), int(prow.pair_j))
        w = float(weights.get(key, 0.0))
        kbar = float(prow.kbar_ij)
        p_i = float(prow.p_i)
        p_j = float(prow.p_j)
        contrib_neg, contrib_abs, contrib_signed, contrib_primary = contribution_triplet(source_feature, w, kbar)

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
                "delta_p": p_i - p_j,
                "delta_p2": (p_i ** 2) - (p_j ** 2),
                "pair_weight": w,
                "kbar_ij": kbar,
                "kbar_abs_ij": abs(kbar),
                "kbar_sign": int(np.sign(kbar)),
                "contrib_neg": contrib_neg,
                "contrib_abs": contrib_abs,
                "contrib_signed": contrib_signed,
                "contrib_primary": contrib_primary,
                "case_label": case_label,
                "branch_basis": branch_basis,
                "branch_label": branch_label,
            }
        )

    pair_df = pd.DataFrame(local_rows).sort_values("contrib_primary", ascending=False).reset_index(drop=True)
    primary_sum = float(pair_df["contrib_primary"].sum())
    normed = (pair_df["contrib_primary"] / primary_sum).to_numpy(dtype=float) if primary_sum > 0 else np.zeros(len(pair_df), dtype=float)
    pair_df["pair_rank_primary"] = np.arange(1, len(pair_df) + 1)
    pair_df["cumulative_primary"] = np.cumsum(normed) if len(normed) else 0.0

    top_df = pd.DataFrame([{
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
        "n_pairs_total": int(len(pair_df)),
        "top1_share": top_share(normed, 1),
        "top3_share": top_share(normed, 3),
        "top5_share": top_share(normed, 5),
        "top10_share": top_share(normed, 10),
        "effective_pair_count": effective_pair_count(normed),
        "dominance_label": dominance_label(top_share(normed, 3), effective_pair_count(normed)),
        "case_label": case_label,
        "branch_basis": branch_basis,
        "branch_label": branch_label,
    }])

    class_rows = []
    for class_mode in class_modes:
        tmp = pair_df.copy()
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
        grouped["cumulative_class_contrib"] = grouped["sum_contrib_primary"].cumsum() / total_class if total_class > 0 else 0.0
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
                    "case_label": case_label,
                    "branch_basis": branch_basis,
                    "branch_label": branch_label,
                }
            )
    class_df = pd.DataFrame(class_rows)
    return pair_df, top_df, class_df


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.6d targeted auto-extend pair audit")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.6d disabled in config. Exiting.")
        return

    with config_path.open("r", encoding="utf-8") as f:
        raw_cfg = yaml.safe_load(f)

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    nearest_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.nearest_branch_assignment)))
    soft_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.soft_branch_scores)))
    soft_summary_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.soft_branch_summary)))
    packet_fit_best_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.packet_fit_best)))
    pair_kernel_df = pd.read_csv(resolve_path(project_root, cfg.source_pair_kernel))

    existing_top_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.pair_top_summary_existing)))
    existing_pair_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.pair_contributions_existing)))
    existing_class_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.pair_class_summary_existing)))

    select_df = build_selection_table(nearest_df, soft_df, soft_summary_df, packet_fit_best_df, cfg)

    existing_cases = set(existing_top_df["case_label"].tolist())
    existing_counts = {"S1": 0, "S2": 0, "S3": 0}
    branch_col_existing = "branch_pref_readout" if "branch_pref_readout" in existing_top_df.columns else ("branch_label" if "branch_label" in existing_top_df.columns else None)
    if branch_col_existing is not None:
        for branch, n in existing_top_df[branch_col_existing].value_counts(dropna=False).items():
            if branch in existing_counts:
                existing_counts[str(branch)] = int(n)

    selected_rows = []
    newly_selected_counts = {"S1": 0, "S2": 0, "S3": 0}

    for branch in ["S1", "S2", "S3"]:
        need = max(0, cfg.target_cases_per_branch - existing_counts.get(branch, 0))
        if need == 0:
            continue

        sub = select_df[select_df[cfg.branch_basis] == branch].copy()
        sub = sub[~sub["case_label"].isin(existing_cases)].copy()

        if cfg.ranking_primary not in sub.columns:
            raise ValueError(f"ranking_primary not found: {cfg.ranking_primary}")
        if cfg.ranking_secondary not in sub.columns:
            raise ValueError(f"ranking_secondary not found: {cfg.ranking_secondary}")

        sub = sub.sort_values(by=[cfg.ranking_primary, cfg.ranking_secondary], ascending=[False, True], na_position="last").head(need)
        for rank, (_, row) in enumerate(sub.iterrows(), start=1):
            selected_rows.append(
                {
                    "run_id": row["run_id"],
                    "t": row["t"],
                    "p_family": row["p_family"],
                    "theta": row["theta"],
                    "branch_basis": cfg.branch_basis,
                    "branch_label": branch,
                    "selection_rank_within_branch": rank,
                    "soft_overlap_score": row.get("soft_overlap_score"),
                    "hard_delta_alpha": row.get("hard_delta_alpha"),
                    "nearest_branch_match_flag": row.get("nearest_branch_match_flag"),
                    "soft_branch_match_flag": row.get("soft_branch_match_flag"),
                    "source_feature": row.get("source_feature"),
                    "best_p0": row.get("best_p0"),
                    "best_sigma_p": row.get("best_sigma_p"),
                    "best_alpha_source": row.get("best_alpha_source"),
                    "alpha_pref_readout": row.get("alpha_pref_readout"),
                    "extension_reason": "missing_branch_support",
                    "case_label": row["case_label"],
                }
            )
            newly_selected_counts[branch] += 1

    selected_extension_df = pd.DataFrame(selected_rows)

    extended_pair_frames = []
    extended_top_frames = []
    extended_class_frames = []

    for _, row in selected_extension_df.iterrows():
        pair_df, top_df, class_df = audit_single_case(
            row=row,
            pair_kernel_df=pair_kernel_df,
            raw_cfg=raw_cfg,
            class_modes=cfg.class_modes,
            branch_basis=cfg.branch_basis,
            branch_label=str(row["branch_label"]),
        )
        if not pair_df.empty:
            extended_pair_frames.append(pair_df)
        if not top_df.empty:
            extended_top_frames.append(top_df)
        if not class_df.empty:
            extended_class_frames.append(class_df)

    extended_pair_df = pd.concat(extended_pair_frames, ignore_index=True) if extended_pair_frames else pd.DataFrame()
    extended_top_df = pd.concat(extended_top_frames, ignore_index=True) if extended_top_frames else pd.DataFrame()
    extended_class_df = pd.concat(extended_class_frames, ignore_index=True) if extended_class_frames else pd.DataFrame()

    combined_pair_df = pd.concat([existing_pair_df, extended_pair_df], ignore_index=True)
    combined_top_df = pd.concat([existing_top_df, extended_top_df], ignore_index=True)
    combined_class_df = pd.concat([existing_class_df, extended_class_df], ignore_index=True)

    combined_counts = {"S1": 0, "S2": 0, "S3": 0}
    for col in ["branch_pref_readout", "branch_label"]:
        if col in combined_top_df.columns:
            for branch, n in combined_top_df[col].value_counts(dropna=False).items():
                if branch in combined_counts:
                    combined_counts[str(branch)] = max(combined_counts[str(branch)], int(n))

    selection_success = all(combined_counts[b] >= cfg.target_cases_per_branch for b in ["S1", "S2", "S3"])
    final_label = "D3" if selection_success else ("D1" if any(newly_selected_counts[b] > 0 for b in ["S1", "S2", "S3"]) else "D0")

    summary = {
        "target_cases_per_branch": cfg.target_cases_per_branch,
        "already_audited_counts": existing_counts,
        "newly_selected_counts": newly_selected_counts,
        "combined_counts": combined_counts,
        "n_new_cases": int(len(selected_extension_df)),
        "selection_success": bool(selection_success),
        "final_label": final_label,
    }

    selected_extension_df.to_csv(out_root / "selected_extension_cases.csv", index=False)
    extended_pair_df.to_csv(out_root / "extended_pair_contributions.csv", index=False)
    extended_top_df.to_csv(out_root / "extended_pair_top_summary.csv", index=False)
    extended_class_df.to_csv(out_root / "extended_pair_class_summary.csv", index=False)
    combined_pair_df.to_csv(out_root / "combined_pair_contributions.csv", index=False)
    combined_top_df.to_csv(out_root / "combined_pair_top_summary.csv", index=False)
    combined_class_df.to_csv(out_root / "combined_pair_class_summary.csv", index=False)
    write_json(out_root / "auto_extend_summary.json", summary)

    report_lines = [
        "# M.3.6d Targeted Auto-Extend Pair Audit",
        "",
        f"- target_cases_per_branch: {cfg.target_cases_per_branch}",
        f"- already_audited_counts: {existing_counts}",
        f"- newly_selected_counts: {newly_selected_counts}",
        f"- combined_counts: {combined_counts}",
        f"- n_new_cases: {len(selected_extension_df)}",
        f"- selection_success: {selection_success}",
        f"- final_label: {final_label}",
    ]
    (out_root / "auto_extend_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.6d completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
