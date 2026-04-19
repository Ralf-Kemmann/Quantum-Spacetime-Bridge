from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass(slots=True)
class M36cConfig:
    enabled: bool
    nearest_branch_assignment: Path
    soft_branch_scores: Path
    soft_branch_summary: Path
    pair_contributions: Path
    pair_top_summary: Path
    pair_class_summary: Path
    branch_basis: str
    n_cases_per_branch: int
    require_nearest_match: bool
    require_soft_match: bool
    ranking_metric: str
    audit_mode: str
    top_k_values: List[int]
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


def load_config(path: Path) -> M36cConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m36c_branch_expanded"]
    return M36cConfig(
        enabled=bool(block["enabled"]),
        nearest_branch_assignment=Path(block["input"]["nearest_branch_assignment"]),
        soft_branch_scores=Path(block["input"]["soft_branch_scores"]),
        soft_branch_summary=Path(block["input"]["soft_branch_summary"]),
        pair_contributions=Path(block["input"]["pair_contributions"]),
        pair_top_summary=Path(block["input"]["pair_top_summary"]),
        pair_class_summary=Path(block["input"]["pair_class_summary"]),
        branch_basis=str(block["selection"]["branch_basis"]),
        n_cases_per_branch=int(block["selection"]["n_cases_per_branch"]),
        require_nearest_match=bool(block["selection"]["require_nearest_match"]),
        require_soft_match=bool(block["selection"]["require_soft_match"]),
        ranking_metric=str(block["selection"]["ranking_metric"]),
        audit_mode=str(block["selection"]["audit_mode"]),
        top_k_values=[int(x) for x in block["comparison"]["top_k_values"]],
        class_modes=[str(x) for x in block["comparison"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )


def case_label_from_row(row: pd.Series) -> str:
    return f"t={row.get('t')}__pf={row.get('p_family')}__th={row.get('theta')}"


def attach_case_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["case_label"] = out.apply(case_label_from_row, axis=1)
    return out


def normalized_contrib(df: pd.DataFrame, value_col: str) -> pd.Series:
    s = df[value_col].astype(float)
    total = float(s.sum())
    if total <= 0:
        return pd.Series(np.zeros(len(df)), index=df.index)
    return s / total


def pair_set(df: pd.DataFrame, top_k: int) -> Set[Tuple[int, int]]:
    sub = df.sort_values("pair_rank_primary", ascending=True).head(top_k)
    return {(int(r["pair_i"]), int(r["pair_j"])) for _, r in sub.iterrows()}


def class_set(df: pd.DataFrame, top_k: int) -> Set[str]:
    sub = df.sort_values("class_rank", ascending=True).head(top_k)
    return {str(x) for x in sub["class_label"].tolist()}


def weighted_pair_overlap(df_a: pd.DataFrame, df_b: pd.DataFrame, top_k: int) -> float:
    a = df_a.sort_values("pair_rank_primary").head(top_k).copy()
    b = df_b.sort_values("pair_rank_primary").head(top_k).copy()
    a = a.set_index(["pair_i", "pair_j"])
    b = b.set_index(["pair_i", "pair_j"])
    overlap = set(a.index).intersection(set(b.index))
    total = 0.0
    for key in overlap:
        total += min(float(a.loc[key, "normalized_contrib_primary"]), float(b.loc[key, "normalized_contrib_primary"]))
    return total


def weighted_class_overlap(df_a: pd.DataFrame, df_b: pd.DataFrame, top_k: int) -> float:
    a = df_a.sort_values("class_rank").head(top_k).copy().set_index("class_label")
    b = df_b.sort_values("class_rank").head(top_k).copy().set_index("class_label")
    overlap = set(a.index).intersection(set(b.index))
    total = 0.0
    for key in overlap:
        total += min(float(a.loc[key, "normalized_class_contrib"]), float(b.loc[key, "normalized_class_contrib"]))
    return total


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.6c branch-conditioned expanded audit")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.6c disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    nearest_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.nearest_branch_assignment)))
    soft_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.soft_branch_scores)))
    soft_summary_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.soft_branch_summary)))
    pair_contrib_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.pair_contributions)))
    pair_top_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.pair_top_summary)))
    pair_class_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.pair_class_summary)))

    select_df = nearest_df.merge(
        soft_df[
            [
                "run_id", "t", "p_family", "theta", "source_feature", "case_label",
                "soft_best_branch_source", "soft_best_branch_readout",
                "soft_branch_match_flag", "soft_overlap_score",
            ]
        ],
        on=["run_id", "t", "p_family", "theta", "source_feature", "case_label"],
        how="left",
    ).merge(
        soft_summary_df[
            [
                "run_id", "t", "p_family", "theta", "source_feature", "case_label",
                "hard_delta_alpha", "nearest_branch_match_flag", "soft_branch_match_flag",
            ]
        ],
        on=["run_id", "t", "p_family", "theta", "source_feature", "case_label"],
        how="left",
        suffixes=("", "_summary"),
    )

    if cfg.branch_basis not in select_df.columns:
        raise ValueError(f"branch_basis column not found: {cfg.branch_basis}")

    if cfg.require_nearest_match and "nearest_branch_match_flag" in select_df.columns:
        select_df = select_df[select_df["nearest_branch_match_flag"].fillna(0).astype(int) == 1].copy()

    if cfg.require_soft_match and "soft_branch_match_flag" in select_df.columns:
        select_df = select_df[select_df["soft_branch_match_flag"].fillna(0).astype(int) == 1].copy()

    reusable_cases = set(pair_top_df["case_label"].unique().tolist())
    if cfg.audit_mode == "strict_reuse":
        select_df = select_df[select_df["case_label"].isin(reusable_cases)].copy()
    elif cfg.audit_mode != "auto_extend":
        raise ValueError(f"Unsupported audit_mode: {cfg.audit_mode}")

    if cfg.ranking_metric not in select_df.columns:
        raise ValueError(f"ranking_metric column not found: {cfg.ranking_metric}")

    selected_rows: List[Dict[str, Any]] = []
    for branch_label in ["S1", "S2", "S3"]:
        sub = select_df[select_df[cfg.branch_basis] == branch_label].copy()
        if sub.empty:
            continue
        sub = sub.sort_values(cfg.ranking_metric, ascending=False, na_position="last").head(cfg.n_cases_per_branch)
        for rank, (_, row) in enumerate(sub.iterrows(), start=1):
            selected_rows.append(
                {
                    "run_id": row["run_id"],
                    "t": row["t"],
                    "p_family": row["p_family"],
                    "theta": row["theta"],
                    "selection_mode": cfg.audit_mode,
                    "branch_basis": cfg.branch_basis,
                    "branch_label": row[cfg.branch_basis],
                    "selection_rank": rank,
                    "nearest_branch_match_flag": row.get("nearest_branch_match_flag"),
                    "soft_branch_match_flag": row.get("soft_branch_match_flag"),
                    "soft_overlap_score": row.get("soft_overlap_score"),
                    "hard_delta_alpha": row.get("hard_delta_alpha"),
                    "source_feature": row.get("source_feature"),
                    "best_p0": row.get("best_p0"),
                    "best_sigma_p": row.get("best_sigma_p"),
                    "best_alpha_source": row.get("best_alpha_source"),
                    "alpha_pref_readout": row.get("alpha_pref_readout"),
                    "case_label": row["case_label"],
                }
            )

    selected_df = pd.DataFrame(selected_rows)
    selected_cases = set(selected_df["case_label"].tolist()) if not selected_df.empty else set()

    branch_pair_df = pair_contrib_df[pair_contrib_df["case_label"].isin(selected_cases)].copy()
    if not branch_pair_df.empty:
        branch_pair_df["normalized_contrib_primary"] = (
            branch_pair_df.groupby("case_label", group_keys=False)
            .apply(lambda g: normalized_contrib(g, "contrib_primary"))
            .reset_index(level=0, drop=True)
        )
        branch_pair_df["is_top1_pair"] = (branch_pair_df["pair_rank_primary"] <= 1).astype(int)
        branch_pair_df["is_top3_pair"] = (branch_pair_df["pair_rank_primary"] <= 3).astype(int)
        branch_pair_df["is_top5_pair"] = (branch_pair_df["pair_rank_primary"] <= 5).astype(int)
        branch_pair_df["branch_basis"] = cfg.branch_basis
        branch_pair_df = branch_pair_df.merge(
            selected_df[["case_label", "branch_label"]].drop_duplicates(),
            on="case_label",
            how="left",
            suffixes=("", "_selected"),
        )
        if "branch_label_selected" in branch_pair_df.columns:
            branch_pair_df["branch_label"] = branch_pair_df["branch_label_selected"]
            branch_pair_df = branch_pair_df.drop(columns=["branch_label_selected"])

    branch_class_df = pair_class_df[pair_class_df["case_label"].isin(selected_cases)].copy()
    if not branch_class_df.empty:
        branch_class_df["normalized_class_contrib"] = (
            branch_class_df.groupby(["case_label", "class_mode"], group_keys=False)
            .apply(lambda g: normalized_contrib(g, "sum_contrib_primary"))
            .reset_index(level=[0, 1], drop=True)
        )
        branch_class_df["is_top1_class"] = (branch_class_df["class_rank"] <= 1).astype(int)
        branch_class_df["is_top3_class"] = (branch_class_df["class_rank"] <= 3).astype(int)
        branch_class_df["is_top5_class"] = (branch_class_df["class_rank"] <= 5).astype(int)
        branch_class_df["branch_basis"] = cfg.branch_basis
        branch_class_df = branch_class_df.merge(
            selected_df[["case_label", "branch_label"]].drop_duplicates(),
            on="case_label",
            how="left",
            suffixes=("", "_selected"),
        )
        if "branch_label_selected" in branch_class_df.columns:
            branch_class_df["branch_label"] = branch_class_df["branch_label_selected"]
            branch_class_df = branch_class_df.drop(columns=["branch_label_selected"])

    meta_df = selected_df[["case_label", "run_id", "branch_label"]].drop_duplicates().set_index("case_label")

    pair_overlap_rows: List[Dict[str, Any]] = []
    grouped_pairs = {case: g.copy() for case, g in branch_pair_df.groupby("case_label", dropna=False)}
    case_labels = sorted(grouped_pairs.keys())
    for i, case_a in enumerate(case_labels):
        for case_b in case_labels[i + 1:]:
            df_a = grouped_pairs[case_a]
            df_b = grouped_pairs[case_b]
            branch_a = meta_df.loc[case_a, "branch_label"]
            branch_b = meta_df.loc[case_b, "branch_label"]
            rel = "within_branch" if branch_a == branch_b else "between_branch"
            run_id = meta_df.loc[case_a, "run_id"]
            for k in cfg.top_k_values:
                sa = pair_set(df_a, k)
                sb = pair_set(df_b, k)
                overlap = len(sa.intersection(sb))
                frac_a = overlap / max(1, len(sa))
                frac_b = overlap / max(1, len(sb))
                pair_overlap_rows.append(
                    {
                        "run_id": run_id,
                        "case_label_a": case_a,
                        "case_label_b": case_b,
                        "branch_a": branch_a,
                        "branch_b": branch_b,
                        "top_k": k,
                        "pair_overlap_count": overlap,
                        "pair_overlap_fraction_a": frac_a,
                        "pair_overlap_fraction_b": frac_b,
                        "weighted_pair_overlap": weighted_pair_overlap(df_a, df_b, k),
                        "relation_type": rel,
                    }
                )
    branch_pair_overlap_df = pd.DataFrame(pair_overlap_rows)

    class_overlap_rows: List[Dict[str, Any]] = []
    grouped_classes = {(case, mode): g.copy() for (case, mode), g in branch_class_df.groupby(["case_label", "class_mode"], dropna=False)}
    for mode in cfg.class_modes:
        mode_cases = sorted([case for (case, m) in grouped_classes.keys() if m == mode])
        for i, case_a in enumerate(mode_cases):
            for case_b in mode_cases[i + 1:]:
                df_a = grouped_classes[(case_a, mode)]
                df_b = grouped_classes[(case_b, mode)]
                branch_a = meta_df.loc[case_a, "branch_label"]
                branch_b = meta_df.loc[case_b, "branch_label"]
                rel = "within_branch" if branch_a == branch_b else "between_branch"
                run_id = meta_df.loc[case_a, "run_id"]
                for k in cfg.top_k_values:
                    sa = class_set(df_a, k)
                    sb = class_set(df_b, k)
                    overlap = len(sa.intersection(sb))
                    frac_a = overlap / max(1, len(sa))
                    frac_b = overlap / max(1, len(sb))
                    class_overlap_rows.append(
                        {
                            "run_id": run_id,
                            "case_label_a": case_a,
                            "case_label_b": case_b,
                            "branch_a": branch_a,
                            "branch_b": branch_b,
                            "class_mode": mode,
                            "top_k": k,
                            "class_overlap_count": overlap,
                            "class_overlap_fraction_a": frac_a,
                            "class_overlap_fraction_b": frac_b,
                            "weighted_class_overlap": weighted_class_overlap(df_a, df_b, k),
                            "relation_type": rel,
                        }
                    )
    branch_class_overlap_df = pd.DataFrame(class_overlap_rows)

    summary_rows: List[Dict[str, Any]] = []
    for branch in ["S1", "S2", "S3"]:
        branch_cases = selected_df[selected_df["branch_label"] == branch]["case_label"].tolist()
        if not branch_cases:
            continue

        pair_within = branch_pair_overlap_df[
            (branch_pair_overlap_df["relation_type"] == "within_branch")
            & (branch_pair_overlap_df["branch_a"] == branch)
            & (branch_pair_overlap_df["top_k"] == 3)
        ]
        dp_within = branch_class_overlap_df[
            (branch_class_overlap_df["relation_type"] == "within_branch")
            & (branch_class_overlap_df["branch_a"] == branch)
            & (branch_class_overlap_df["class_mode"] == "delta_p")
            & (branch_class_overlap_df["top_k"] == 3)
        ]
        dp2_within = branch_class_overlap_df[
            (branch_class_overlap_df["relation_type"] == "within_branch")
            & (branch_class_overlap_df["branch_a"] == branch)
            & (branch_class_overlap_df["class_mode"] == "delta_p2")
            & (branch_class_overlap_df["top_k"] == 3)
        ]

        sub_pairs = branch_pair_df[branch_pair_df["case_label"].isin(branch_cases)]
        consensus_pair = None
        consensus_dp = None
        consensus_dp2 = None
        if not sub_pairs.empty:
            top1_pairs = (
                sub_pairs[sub_pairs["is_top1_pair"] == 1]
                .groupby(["pair_i", "pair_j"], dropna=False)
                .size()
                .sort_values(ascending=False)
            )
            if not top1_pairs.empty:
                pi, pj = top1_pairs.index[0]
                consensus_pair = f"({int(pi)},{int(pj)})"
                prow = sub_pairs[(sub_pairs["pair_i"] == pi) & (sub_pairs["pair_j"] == pj)].iloc[0]
                consensus_dp = float(prow["delta_p"])
                consensus_dp2 = float(prow["delta_p2"])

        def consensus_classes(mode: str):
            sub = branch_class_df[
                (branch_class_df["case_label"].isin(branch_cases))
                & (branch_class_df["class_mode"] == mode)
                & (branch_class_df["is_top3_class"] == 1)
            ]
            if sub.empty:
                return None
            vals = (
                sub.groupby("class_label")["normalized_class_contrib"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
                .index
                .tolist()
            )
            return ";".join(vals)

        within_pair_mean = float(pair_within["weighted_pair_overlap"].mean()) if not pair_within.empty else None
        within_dp_mean = float(dp_within["weighted_class_overlap"].mean()) if not dp_within.empty else None
        within_dp2_mean = float(dp2_within["weighted_class_overlap"].mean()) if not dp2_within.empty else None

        if within_pair_mean is not None and within_pair_mean > 0.3:
            sig = "pair_specific"
        elif ((within_dp_mean or 0.0) > 0.1) or ((within_dp2_mean or 0.0) > 0.1):
            sig = "class_specific"
        elif len(branch_cases) == 1:
            sig = "single_case"
        else:
            sig = "weak_or_none"

        summary_rows.append(
            {
                "run_id": selected_df["run_id"].iloc[0] if not selected_df.empty else None,
                "branch_basis": cfg.branch_basis,
                "branch_label": branch,
                "n_cases": len(branch_cases),
                "mean_within_pair_overlap_top3": within_pair_mean,
                "mean_within_class_overlap_top3_delta_p": within_dp_mean,
                "mean_within_class_overlap_top3_delta_p2": within_dp2_mean,
                "consensus_top1_pair": consensus_pair,
                "consensus_top1_delta_p": consensus_dp,
                "consensus_top1_delta_p2": consensus_dp2,
                "consensus_top3_classes_delta_p": consensus_classes("delta_p"),
                "consensus_top3_classes_delta_p2": consensus_classes("delta_p2"),
                "signature_label": sig,
            }
        )
    branch_identity_summary_df = pd.DataFrame(summary_rows)

    pair_within = branch_pair_overlap_df[
        (branch_pair_overlap_df["relation_type"] == "within_branch")
        & (branch_pair_overlap_df["top_k"] == 3)
    ]
    pair_between = branch_pair_overlap_df[
        (branch_pair_overlap_df["relation_type"] == "between_branch")
        & (branch_pair_overlap_df["top_k"] == 3)
    ]
    dp_within = branch_class_overlap_df[
        (branch_class_overlap_df["relation_type"] == "within_branch")
        & (branch_class_overlap_df["class_mode"] == "delta_p")
        & (branch_class_overlap_df["top_k"] == 3)
    ]
    dp_between = branch_class_overlap_df[
        (branch_class_overlap_df["relation_type"] == "between_branch")
        & (branch_class_overlap_df["class_mode"] == "delta_p")
        & (branch_class_overlap_df["top_k"] == 3)
    ]
    dp2_within = branch_class_overlap_df[
        (branch_class_overlap_df["relation_type"] == "within_branch")
        & (branch_class_overlap_df["class_mode"] == "delta_p2")
        & (branch_class_overlap_df["top_k"] == 3)
    ]
    dp2_between = branch_class_overlap_df[
        (branch_class_overlap_df["relation_type"] == "between_branch")
        & (branch_class_overlap_df["class_mode"] == "delta_p2")
        & (branch_class_overlap_df["top_k"] == 3)
    ]

    pair_within_mean = float(pair_within["weighted_pair_overlap"].mean()) if not pair_within.empty else None
    pair_between_mean = float(pair_between["weighted_pair_overlap"].mean()) if not pair_between.empty else None
    dp_within_mean = float(dp_within["weighted_class_overlap"].mean()) if not dp_within.empty else None
    dp_between_mean = float(dp_between["weighted_class_overlap"].mean()) if not dp_between.empty else None
    dp2_within_mean = float(dp2_within["weighted_class_overlap"].mean()) if not dp2_within.empty else None
    dp2_between_mean = float(dp2_between["weighted_class_overlap"].mean()) if not dp2_between.empty else None

    score_pair = None if pair_within_mean is None or pair_between_mean is None else pair_within_mean - pair_between_mean
    score_dp = None if dp_within_mean is None or dp_between_mean is None else dp_within_mean - dp_between_mean
    score_dp2 = None if dp2_within_mean is None or dp2_between_mean is None else dp2_within_mean - dp2_between_mean

    if score_pair is not None and score_pair > 0.2:
        final_label = "C3"
    elif (score_dp is not None and score_dp > 0.05) or (score_dp2 is not None and score_dp2 > 0.05):
        final_label = "C2"
    elif selected_df["branch_label"].nunique() >= 3 if not selected_df.empty else False:
        final_label = "C1"
    else:
        final_label = "C0"

    global_summary = {
        "n_selected_cases": int(len(selected_df)),
        "n_selected_branches": int(selected_df["branch_label"].nunique()) if not selected_df.empty else 0,
        "pair_within_overlap_top3": pair_within_mean,
        "pair_between_overlap_top3": pair_between_mean,
        "delta_p_within_overlap_top3": dp_within_mean,
        "delta_p_between_overlap_top3": dp_between_mean,
        "delta_p2_within_overlap_top3": dp2_within_mean,
        "delta_p2_between_overlap_top3": dp2_between_mean,
        "pair_separability_score": score_pair,
        "delta_p_separability_score": score_dp,
        "delta_p2_separability_score": score_dp2,
        "final_label": final_label,
    }

    selected_df.to_csv(out_root / "selected_branch_cases.csv", index=False)
    branch_pair_df.to_csv(out_root / "branch_pair_identity.csv", index=False)
    branch_pair_overlap_df.to_csv(out_root / "branch_pair_overlap.csv", index=False)
    branch_class_df.to_csv(out_root / "branch_class_identity.csv", index=False)
    branch_class_overlap_df.to_csv(out_root / "branch_class_overlap.csv", index=False)
    branch_identity_summary_df.to_csv(out_root / "branch_identity_summary.csv", index=False)
    write_json(out_root / "global_identity_summary.json", global_summary)

    report_lines = [
        "# M.3.6c Branch-conditioned Expanded Audit",
        "",
        f"- n_selected_cases: {safe_json_value(global_summary['n_selected_cases'])}",
        f"- n_selected_branches: {safe_json_value(global_summary['n_selected_branches'])}",
        f"- pair_within_overlap_top3: {safe_json_value(global_summary['pair_within_overlap_top3'])}",
        f"- pair_between_overlap_top3: {safe_json_value(global_summary['pair_between_overlap_top3'])}",
        f"- delta_p_within_overlap_top3: {safe_json_value(global_summary['delta_p_within_overlap_top3'])}",
        f"- delta_p_between_overlap_top3: {safe_json_value(global_summary['delta_p_between_overlap_top3'])}",
        f"- delta_p2_within_overlap_top3: {safe_json_value(global_summary['delta_p2_within_overlap_top3'])}",
        f"- delta_p2_between_overlap_top3: {safe_json_value(global_summary['delta_p2_between_overlap_top3'])}",
        f"- final_label: {safe_json_value(global_summary['final_label'])}",
    ]
    (out_root / "global_identity_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.6c completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
