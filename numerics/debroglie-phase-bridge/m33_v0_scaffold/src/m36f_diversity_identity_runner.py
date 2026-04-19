from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass(slots=True)
class M36fConfig:
    enabled: bool
    combined_pair_contributions: Path
    combined_pair_top_summary: Path
    combined_pair_class_summary: Path
    grouping_columns: List[str]
    ranking_primary: str
    ranking_secondary: str
    run_pruned: bool
    run_weighted: bool
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


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def case_label_from_row(row: pd.Series) -> str:
    return f"t={row.get('t')}__pf={row.get('p_family')}__th={row.get('theta')}"


def attach_case_label(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "case_label" not in out.columns:
        out["case_label"] = out.apply(case_label_from_row, axis=1)
    return out


def load_config(path: Path) -> M36fConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m36f_diversity_identity"]
    return M36fConfig(
        enabled=bool(block["enabled"]),
        combined_pair_contributions=Path(block["input"]["combined_pair_contributions"]),
        combined_pair_top_summary=Path(block["input"]["combined_pair_top_summary"]),
        combined_pair_class_summary=Path(block["input"]["combined_pair_class_summary"]),
        grouping_columns=[str(x) for x in block["diversity"]["grouping_columns"]],
        ranking_primary=str(block["diversity"]["ranking_primary"]),
        ranking_secondary=str(block["diversity"]["ranking_secondary"]),
        run_pruned=bool(block["diversity"]["run_pruned"]),
        run_weighted=bool(block["diversity"]["run_weighted"]),
        top_k_values=[int(x) for x in block["comparison"]["top_k_values"]],
        class_modes=[str(x) for x in block["comparison"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )


def mean_or_none(s: pd.Series) -> Optional[float]:
    return None if s.empty else float(s.mean())


def pair_set(df: pd.DataFrame, top_k: int) -> Set[Tuple[int, int]]:
    sub = df.sort_values("pair_rank_primary", ascending=True).head(top_k)
    return {(int(r["pair_i"]), int(r["pair_j"])) for _, r in sub.iterrows()}


def class_set(df: pd.DataFrame, top_k: int) -> Set[str]:
    sub = df.sort_values("class_rank", ascending=True).head(top_k)
    return {str(x) for x in sub["class_label"].tolist()}


def weighted_pair_overlap(df_a: pd.DataFrame, df_b: pd.DataFrame, top_k: int) -> float:
    a = df_a.sort_values("pair_rank_primary").head(top_k).copy()
    b = df_b.sort_values("pair_rank_primary").head(top_k).copy()
    if a.empty or b.empty:
        return 0.0
    a = a.set_index(["pair_i", "pair_j"])
    b = b.set_index(["pair_i", "pair_j"])
    overlap = set(a.index).intersection(set(b.index))
    total = 0.0
    for key in overlap:
        total += min(float(a.loc[key, "normalized_contrib_primary"]), float(b.loc[key, "normalized_contrib_primary"]))
    return total


def weighted_class_overlap(df_a: pd.DataFrame, df_b: pd.DataFrame, top_k: int) -> float:
    a = df_a.sort_values("class_rank").head(top_k).copy()
    b = df_b.sort_values("class_rank").head(top_k).copy()
    if a.empty or b.empty:
        return 0.0
    a = a.set_index("class_label")
    b = b.set_index("class_label")
    overlap = set(a.index).intersection(set(b.index))
    total = 0.0
    for key in overlap:
        total += min(float(a.loc[key, "normalized_class_contrib"]), float(b.loc[key, "normalized_class_contrib"]))
    return total


def compute_meta_table(pair_df: pd.DataFrame, top_df: pd.DataFrame, class_df: pd.DataFrame) -> pd.DataFrame:
    meta_cols = ["case_label", "run_id", "branch_label", "t", "p_family", "theta", "source_feature", "best_alpha_source", "best_sigma_p", "top3_share", "effective_pair_count"]
    pieces = []
    for df in (top_df, pair_df, class_df):
        cols = [c for c in meta_cols if c in df.columns]
        if cols:
            pieces.append(df[cols].copy())
    meta = pd.concat(pieces, ignore_index=True).drop_duplicates()
    meta = (
        meta.groupby("case_label", dropna=False)
        .agg(
            run_id=("run_id", "first"),
            branch_label=("branch_label", lambda s: next((x for x in s if pd.notna(x)), None)),
            t=("t", "first"),
            p_family=("p_family", "first"),
            theta=("theta", "first"),
            source_feature=("source_feature", "first"),
            best_alpha_source=("best_alpha_source", "first") if "best_alpha_source" in meta.columns else ("t", "first"),
            best_sigma_p=("best_sigma_p", "first") if "best_sigma_p" in meta.columns else ("t", "first"),
            top3_share=("top3_share", "first") if "top3_share" in meta.columns else ("t", "first"),
            effective_pair_count=("effective_pair_count", "first") if "effective_pair_count" in meta.columns else ("t", "first"),
        )
        .reset_index()
    )
    return meta


def assign_diversity_groups(meta_df: pd.DataFrame, cfg: M36fConfig) -> pd.DataFrame:
    df = meta_df.copy()
    missing = [c for c in cfg.grouping_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing grouping columns in meta table: {missing}")
    df["diversity_group"] = df[cfg.grouping_columns].astype(str).agg("|".join, axis=1)

    if cfg.ranking_primary not in df.columns:
        raise ValueError(f"ranking_primary not found: {cfg.ranking_primary}")
    if cfg.ranking_secondary not in df.columns:
        raise ValueError(f"ranking_secondary not found: {cfg.ranking_secondary}")

    df = df.sort_values(
        by=["diversity_group", cfg.ranking_primary, cfg.ranking_secondary],
        ascending=[True, False, True],
        na_position="last",
    ).copy()
    df["group_rank"] = df.groupby("diversity_group").cumcount() + 1
    df["group_size"] = df.groupby("diversity_group")["case_label"].transform("count")
    df["group_weight"] = 1.0 / df["group_size"].astype(float)
    df["is_group_representative"] = (df["group_rank"] == 1).astype(int)
    return df


def apply_normalization(pair_df: pd.DataFrame, class_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = pair_df.copy()
    c = class_df.copy()

    if "normalized_contrib_primary" not in p.columns:
        totals = p.groupby("case_label")["contrib_primary"].transform("sum")
        p["normalized_contrib_primary"] = np.where(totals > 0, p["contrib_primary"] / totals, 0.0)

    if "normalized_class_contrib" not in c.columns:
        totals = c.groupby(["case_label", "class_mode"])["sum_contrib_primary"].transform("sum")
        c["normalized_class_contrib"] = np.where(totals > 0, c["sum_contrib_primary"] / totals, 0.0)

    return p, c


def filtered_case_labels(diversity_df: pd.DataFrame, mode: str) -> List[str]:
    if mode == "pruned":
        return diversity_df.loc[diversity_df["is_group_representative"] == 1, "case_label"].tolist()
    return diversity_df["case_label"].tolist()


def build_overlap_tables(
    pair_df: pd.DataFrame,
    class_df: pd.DataFrame,
    meta_index: pd.DataFrame,
    cfg: M36fConfig,
    case_weights: Optional[Dict[str, float]] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pair_rows: List[Dict[str, Any]] = []
    class_rows: List[Dict[str, Any]] = []

    grouped_pairs = {case: g.copy() for case, g in pair_df.groupby("case_label", dropna=False)}
    case_labels = sorted(grouped_pairs.keys())

    for i, case_a in enumerate(case_labels):
        for case_b in case_labels[i + 1:]:
            df_a = grouped_pairs[case_a]
            df_b = grouped_pairs[case_b]
            branch_a = meta_index.loc[case_a, "branch_label"] if case_a in meta_index.index else None
            branch_b = meta_index.loc[case_b, "branch_label"] if case_b in meta_index.index else None
            run_id = meta_index.loc[case_a, "run_id"] if case_a in meta_index.index else None
            rel = "within_branch" if pd.notna(branch_a) and pd.notna(branch_b) and branch_a == branch_b else "between_branch"
            w_a = 1.0 if case_weights is None else float(case_weights.get(case_a, 1.0))
            w_b = 1.0 if case_weights is None else float(case_weights.get(case_b, 1.0))
            pair_case_weight = w_a * w_b

            for k in cfg.top_k_values:
                sa = pair_set(df_a, k)
                sb = pair_set(df_b, k)
                overlap = len(sa.intersection(sb))
                frac_a = overlap / max(1, len(sa))
                frac_b = overlap / max(1, len(sb))
                raw_overlap = weighted_pair_overlap(df_a, df_b, k)
                pair_rows.append(
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
                        "weighted_pair_overlap": raw_overlap,
                        "case_weight_a": w_a,
                        "case_weight_b": w_b,
                        "pair_overlap_weighted_by_case": raw_overlap * pair_case_weight,
                        "relation_type": rel,
                    }
                )

    grouped_classes = {(case, mode): g.copy() for (case, mode), g in class_df.groupby(["case_label", "class_mode"], dropna=False)}
    for mode in cfg.class_modes:
        mode_cases = sorted([case for (case, m) in grouped_classes.keys() if m == mode])
        for i, case_a in enumerate(mode_cases):
            for case_b in mode_cases[i + 1:]:
                df_a = grouped_classes[(case_a, mode)]
                df_b = grouped_classes[(case_b, mode)]
                branch_a = meta_index.loc[case_a, "branch_label"] if case_a in meta_index.index else None
                branch_b = meta_index.loc[case_b, "branch_label"] if case_b in meta_index.index else None
                run_id = meta_index.loc[case_a, "run_id"] if case_a in meta_index.index else None
                rel = "within_branch" if pd.notna(branch_a) and pd.notna(branch_b) and branch_a == branch_b else "between_branch"
                w_a = 1.0 if case_weights is None else float(case_weights.get(case_a, 1.0))
                w_b = 1.0 if case_weights is None else float(case_weights.get(case_b, 1.0))
                class_case_weight = w_a * w_b

                for k in cfg.top_k_values:
                    sa = class_set(df_a, k)
                    sb = class_set(df_b, k)
                    overlap = len(sa.intersection(sb))
                    frac_a = overlap / max(1, len(sa))
                    frac_b = overlap / max(1, len(sb))
                    raw_overlap = weighted_class_overlap(df_a, df_b, k)
                    class_rows.append(
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
                            "weighted_class_overlap": raw_overlap,
                            "case_weight_a": w_a,
                            "case_weight_b": w_b,
                            "class_overlap_weighted_by_case": raw_overlap * class_case_weight,
                            "relation_type": rel,
                        }
                    )

    return pd.DataFrame(pair_rows), pd.DataFrame(class_rows)


def weighted_mean_by_case(df: pd.DataFrame, value_col: str) -> Optional[float]:
    if df.empty:
        return None
    weight_col = None
    if value_col == "weighted_pair_overlap" and "pair_overlap_weighted_by_case" in df.columns:
        weight_col = "pair_overlap_weighted_by_case"
    elif value_col == "weighted_class_overlap" and "class_overlap_weighted_by_case" in df.columns:
        weight_col = "class_overlap_weighted_by_case"

    if weight_col is None or "case_weight_a" not in df.columns or "case_weight_b" not in df.columns:
        return float(df[value_col].mean())

    weights = (df["case_weight_a"].astype(float) * df["case_weight_b"].astype(float)).to_numpy()
    vals = df[value_col].astype(float).to_numpy()
    denom = weights.sum()
    if denom <= 0:
        return float(vals.mean()) if len(vals) else None
    return float((vals * weights).sum() / denom)


def branch_summary_for_mode(
    mode: str,
    meta_df: pd.DataFrame,
    pair_overlap_df: pd.DataFrame,
    class_overlap_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    branches = sorted([b for b in meta_df["branch_label"].dropna().unique().tolist()])

    for branch in branches:
        n_raw = int((meta_df["branch_label"] == branch).sum())
        n_eff = float(meta_df.loc[meta_df["branch_label"] == branch, "group_weight"].sum()) if "group_weight" in meta_df.columns else float(n_raw)

        pair_within_df = pair_overlap_df[
            (pair_overlap_df["relation_type"] == "within_branch")
            & (pair_overlap_df["branch_a"] == branch)
            & (pair_overlap_df["top_k"] == 3)
        ]
        pair_between_df = pair_overlap_df[
            (pair_overlap_df["relation_type"] == "between_branch")
            & ((pair_overlap_df["branch_a"] == branch) | (pair_overlap_df["branch_b"] == branch))
            & (pair_overlap_df["top_k"] == 3)
        ]

        dp_within_df = class_overlap_df[
            (class_overlap_df["relation_type"] == "within_branch")
            & (class_overlap_df["branch_a"] == branch)
            & (class_overlap_df["class_mode"] == "delta_p")
            & (class_overlap_df["top_k"] == 3)
        ]
        dp_between_df = class_overlap_df[
            (class_overlap_df["relation_type"] == "between_branch")
            & ((class_overlap_df["branch_a"] == branch) | (class_overlap_df["branch_b"] == branch))
            & (class_overlap_df["class_mode"] == "delta_p")
            & (class_overlap_df["top_k"] == 3)
        ]

        dp2_within_df = class_overlap_df[
            (class_overlap_df["relation_type"] == "within_branch")
            & (class_overlap_df["branch_a"] == branch)
            & (class_overlap_df["class_mode"] == "delta_p2")
            & (class_overlap_df["top_k"] == 3)
        ]
        dp2_between_df = class_overlap_df[
            (class_overlap_df["relation_type"] == "between_branch")
            & ((class_overlap_df["branch_a"] == branch) | (class_overlap_df["branch_b"] == branch))
            & (class_overlap_df["class_mode"] == "delta_p2")
            & (class_overlap_df["top_k"] == 3)
        ]

        pair_within = weighted_mean_by_case(pair_within_df, "weighted_pair_overlap")
        pair_between = weighted_mean_by_case(pair_between_df, "weighted_pair_overlap")
        dp_within = weighted_mean_by_case(dp_within_df, "weighted_class_overlap")
        dp_between = weighted_mean_by_case(dp_between_df, "weighted_class_overlap")
        dp2_within = weighted_mean_by_case(dp2_within_df, "weighted_class_overlap")
        dp2_between = weighted_mean_by_case(dp2_between_df, "weighted_class_overlap")

        pair_sep = None if pair_within is None or pair_between is None else pair_within - pair_between
        dp_sep = None if dp_within is None or dp_between is None else dp_within - dp_between
        dp2_sep = None if dp2_within is None or dp2_between is None else dp2_within - dp2_between

        if pair_sep is not None and pair_sep > 0.2:
            sig = "pair_specific"
        elif (dp_sep is not None and dp_sep > 0.05) or (dp2_sep is not None and dp2_sep > 0.05):
            sig = "class_specific"
        elif n_raw <= 1:
            sig = "single_case"
        else:
            sig = "weak_or_none"

        rows.append(
            {
                "run_id": meta_df["run_id"].iloc[0] if not meta_df.empty else None,
                "mode": mode,
                "branch_label": branch,
                "n_cases_raw": n_raw,
                "n_cases_effective": n_eff,
                "mean_within_pair_overlap_top3": pair_within,
                "mean_between_pair_overlap_top3": pair_between,
                "mean_within_class_overlap_top3_delta_p": dp_within,
                "mean_between_class_overlap_top3_delta_p": dp_between,
                "mean_within_class_overlap_top3_delta_p2": dp2_within,
                "mean_between_class_overlap_top3_delta_p2": dp2_between,
                "pair_separability_score": pair_sep,
                "delta_p_separability_score": dp_sep,
                "delta_p2_separability_score": dp2_sep,
                "signature_label": sig,
            }
        )
    return pd.DataFrame(rows)


def global_scores(mode: str, meta_df: pd.DataFrame, pair_overlap_df: pd.DataFrame, class_overlap_df: pd.DataFrame) -> Dict[str, Any]:
    pair_within_df = pair_overlap_df[
        (pair_overlap_df["relation_type"] == "within_branch") & (pair_overlap_df["top_k"] == 3)
    ]
    pair_between_df = pair_overlap_df[
        (pair_overlap_df["relation_type"] == "between_branch") & (pair_overlap_df["top_k"] == 3)
    ]
    dp_within_df = class_overlap_df[
        (class_overlap_df["relation_type"] == "within_branch") & (class_overlap_df["class_mode"] == "delta_p") & (class_overlap_df["top_k"] == 3)
    ]
    dp_between_df = class_overlap_df[
        (class_overlap_df["relation_type"] == "between_branch") & (class_overlap_df["class_mode"] == "delta_p") & (class_overlap_df["top_k"] == 3)
    ]
    dp2_within_df = class_overlap_df[
        (class_overlap_df["relation_type"] == "within_branch") & (class_overlap_df["class_mode"] == "delta_p2") & (class_overlap_df["top_k"] == 3)
    ]
    dp2_between_df = class_overlap_df[
        (class_overlap_df["relation_type"] == "between_branch") & (class_overlap_df["class_mode"] == "delta_p2") & (class_overlap_df["top_k"] == 3)
    ]

    pair_within = weighted_mean_by_case(pair_within_df, "weighted_pair_overlap")
    pair_between = weighted_mean_by_case(pair_between_df, "weighted_pair_overlap")
    dp_within = weighted_mean_by_case(dp_within_df, "weighted_class_overlap")
    dp_between = weighted_mean_by_case(dp_between_df, "weighted_class_overlap")
    dp2_within = weighted_mean_by_case(dp2_within_df, "weighted_class_overlap")
    dp2_between = weighted_mean_by_case(dp2_between_df, "weighted_class_overlap")

    pair_sep = None if pair_within is None or pair_between is None else pair_within - pair_between
    dp_sep = None if dp_within is None or dp_between is None else dp_within - dp_between
    dp2_sep = None if dp2_within is None or dp2_between is None else dp2_within - dp2_between

    sep_scores = {
        "pair": pair_sep if pair_sep is not None else -np.inf,
        "delta_p_class": dp_sep if dp_sep is not None else -np.inf,
        "delta_p2_class": dp2_sep if dp2_sep is not None else -np.inf,
    }
    dominant = max(sep_scores, key=sep_scores.get)
    if sep_scores[dominant] == -np.inf:
        dominant = None

    return {
        "mode": mode,
        "n_cases_raw": int(meta_df["case_label"].nunique()) if not meta_df.empty else 0,
        "n_cases_effective": float(meta_df["group_weight"].sum()) if "group_weight" in meta_df.columns else float(meta_df["case_label"].nunique()),
        "pair_within_overlap_top3": pair_within,
        "pair_between_overlap_top3": pair_between,
        "delta_p_within_overlap_top3": dp_within,
        "delta_p_between_overlap_top3": dp_between,
        "delta_p2_within_overlap_top3": dp2_within,
        "delta_p2_between_overlap_top3": dp2_between,
        "pair_separability_score": pair_sep,
        "delta_p_separability_score": dp_sep,
        "delta_p2_separability_score": dp2_sep,
        "dominant_identity_level": dominant,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.6f diversity-aware combined identity audit")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.6f disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    pair_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_contributions)))
    top_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_top_summary)))
    class_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_class_summary)))

    for df in (pair_df, top_df, class_df):
        if "branch_label" not in df.columns:
            df["branch_label"] = None
        if "branch_pref_readout" in df.columns:
            df["branch_label"] = df["branch_label"].where(df["branch_label"].notna(), df["branch_pref_readout"])

    pair_df, class_df = apply_normalization(pair_df, class_df)

    meta_df = compute_meta_table(pair_df, top_df, class_df)
    diversity_df = assign_diversity_groups(meta_df, cfg)

    diversity_case_rows = []
    for _, row in diversity_df.iterrows():
        diversity_case_rows.append(
            {
                "run_id": row.get("run_id"),
                "case_label": row["case_label"],
                "branch_label": row.get("branch_label"),
                "t": row.get("t"),
                "p_family": row.get("p_family"),
                "theta": row.get("theta"),
                "source_feature": row.get("source_feature"),
                "best_alpha_source": row.get("best_alpha_source"),
                "best_sigma_p": row.get("best_sigma_p"),
                "diversity_group": row["diversity_group"],
                "group_rank": row["group_rank"],
                "group_weight": row["group_weight"],
                "is_group_representative": row["is_group_representative"],
                "selection_mode": "full",
            }
        )
        if cfg.run_pruned and int(row["is_group_representative"]) == 1:
            d = row.to_dict()
            d["selection_mode"] = "pruned"
            diversity_case_rows.append(d)
        if cfg.run_weighted:
            d = row.to_dict()
            d["selection_mode"] = "weighted"
            diversity_case_rows.append(d)

    diversity_case_table = pd.DataFrame(diversity_case_rows)

    summary_frames = []
    global_summaries = {}

    # Pruned mode
    if cfg.run_pruned:
        pruned_cases = filtered_case_labels(diversity_df, "pruned")
        pair_pruned = pair_df[pair_df["case_label"].isin(pruned_cases)].copy()
        class_pruned = class_df[class_df["case_label"].isin(pruned_cases)].copy()
        meta_pruned = diversity_df[diversity_df["case_label"].isin(pruned_cases)].copy().reset_index(drop=True)
        meta_pruned_index = meta_pruned.set_index("case_label")

        pruned_pair_overlap, pruned_class_overlap = build_overlap_tables(pair_pruned, class_pruned, meta_pruned_index, cfg, case_weights=None)
        pruned_pair_overlap.to_csv(out_root / "pruned_pair_overlap.csv", index=False)
        pruned_class_overlap.to_csv(out_root / "pruned_class_overlap.csv", index=False)

        pruned_branch_summary = branch_summary_for_mode("pruned", meta_pruned, pruned_pair_overlap, pruned_class_overlap)
        summary_frames.append(pruned_branch_summary)
        global_summaries["pruned"] = global_scores("pruned", meta_pruned, pruned_pair_overlap, pruned_class_overlap)

    # Weighted mode
    if cfg.run_weighted:
        weights = dict(zip(diversity_df["case_label"], diversity_df["group_weight"]))
        meta_weighted = diversity_df.copy().reset_index(drop=True)
        meta_weighted_index = meta_weighted.set_index("case_label")
        weighted_pair_overlap, weighted_class_overlap = build_overlap_tables(pair_df, class_df, meta_weighted_index, cfg, case_weights=weights)
        weighted_pair_overlap.to_csv(out_root / "weighted_pair_overlap.csv", index=False)
        weighted_class_overlap.to_csv(out_root / "weighted_class_overlap.csv", index=False)

        weighted_branch_summary = branch_summary_for_mode("weighted", meta_weighted, weighted_pair_overlap, weighted_class_overlap)
        summary_frames.append(weighted_branch_summary)
        global_summaries["weighted"] = global_scores("weighted", meta_weighted, weighted_pair_overlap, weighted_class_overlap)

    diversity_branch_summary = pd.concat(summary_frames, ignore_index=True) if summary_frames else pd.DataFrame()
    diversity_case_table.to_csv(out_root / "diversity_case_table.csv", index=False)
    diversity_branch_summary.to_csv(out_root / "diversity_branch_summary.csv", index=False)

    raw_n_cases = int(meta_df["case_label"].nunique()) if not meta_df.empty else 0
    pruned_n_cases = int(diversity_df["is_group_representative"].sum()) if not diversity_df.empty else 0
    weighted_eff = float(diversity_df["group_weight"].sum()) if not diversity_df.empty else 0.0

    pair_sep_pruned = global_summaries.get("pruned", {}).get("pair_separability_score")
    dp_sep_pruned = global_summaries.get("pruned", {}).get("delta_p_separability_score")
    dp2_sep_pruned = global_summaries.get("pruned", {}).get("delta_p2_separability_score")

    pair_sep_weighted = global_summaries.get("weighted", {}).get("pair_separability_score")
    dp_sep_weighted = global_summaries.get("weighted", {}).get("delta_p_separability_score")
    dp2_sep_weighted = global_summaries.get("weighted", {}).get("delta_p2_separability_score")

    raw_proxy = None
    if cfg.run_weighted and cfg.run_pruned:
        # use max of pruned/weighted as a cheap robustness proxy against collapse
        raw_proxy = max(
            x for x in [
                pair_sep_pruned if pair_sep_pruned is not None else -np.inf,
                pair_sep_weighted if pair_sep_weighted is not None else -np.inf,
                dp_sep_pruned if dp_sep_pruned is not None else -np.inf,
                dp_sep_weighted if dp_sep_weighted is not None else -np.inf,
                dp2_sep_pruned if dp2_sep_pruned is not None else -np.inf,
                dp2_sep_weighted if dp2_sep_weighted is not None else -np.inf,
            ]
        )

    # sensitivity flag: 1 if weighted/pruned drop sharply or disappear
    replicate_sensitivity_flag = 0
    if pair_sep_pruned is not None and pair_sep_weighted is not None:
        if max(pair_sep_pruned, pair_sep_weighted) < 0.05 and raw_n_cases > pruned_n_cases:
            replicate_sensitivity_flag = 1
    if dp2_sep_pruned is not None and dp2_sep_weighted is not None:
        if max(dp2_sep_pruned, dp2_sep_weighted) < 0.05 and raw_n_cases > pruned_n_cases:
            replicate_sensitivity_flag = 1

    best_pruned = global_summaries.get("pruned", {}).get("dominant_identity_level")
    best_weighted = global_summaries.get("weighted", {}).get("dominant_identity_level")

    robust_class = ((dp_sep_pruned or 0) > 0.05 or (dp2_sep_pruned or 0) > 0.05 or (dp_sep_weighted or 0) > 0.05 or (dp2_sep_weighted or 0) > 0.05)
    robust_pair = ((pair_sep_pruned or 0) > 0.2 or (pair_sep_weighted or 0) > 0.2)

    if robust_pair and robust_class and replicate_sensitivity_flag == 0:
        final_label = "F3"
    elif robust_class and replicate_sensitivity_flag == 0:
        final_label = "F2"
    elif robust_class or robust_pair:
        final_label = "F1"
    else:
        final_label = "F0"

    diversity_global_summary = {
        "n_cases_raw": raw_n_cases,
        "n_cases_pruned": pruned_n_cases,
        "n_cases_effective_weighted": weighted_eff,
        "pair_separability_pruned": pair_sep_pruned,
        "delta_p_separability_pruned": dp_sep_pruned,
        "delta_p2_separability_pruned": dp2_sep_pruned,
        "pair_separability_weighted": pair_sep_weighted,
        "delta_p_separability_weighted": dp_sep_weighted,
        "delta_p2_separability_weighted": dp2_sep_weighted,
        "dominant_identity_level_pruned": best_pruned,
        "dominant_identity_level_weighted": best_weighted,
        "replicate_sensitivity_flag": replicate_sensitivity_flag,
        "final_label": final_label,
    }

    write_json(out_root / "diversity_global_summary.json", diversity_global_summary)

    report_lines = [
        "# M.3.6f Diversity-aware Combined Identity Audit",
        "",
        f"- n_cases_raw: {safe_json_value(diversity_global_summary['n_cases_raw'])}",
        f"- n_cases_pruned: {safe_json_value(diversity_global_summary['n_cases_pruned'])}",
        f"- n_cases_effective_weighted: {safe_json_value(diversity_global_summary['n_cases_effective_weighted'])}",
        f"- pair_separability_pruned: {safe_json_value(diversity_global_summary['pair_separability_pruned'])}",
        f"- delta_p_separability_pruned: {safe_json_value(diversity_global_summary['delta_p_separability_pruned'])}",
        f"- delta_p2_separability_pruned: {safe_json_value(diversity_global_summary['delta_p2_separability_pruned'])}",
        f"- pair_separability_weighted: {safe_json_value(diversity_global_summary['pair_separability_weighted'])}",
        f"- delta_p_separability_weighted: {safe_json_value(diversity_global_summary['delta_p_separability_weighted'])}",
        f"- delta_p2_separability_weighted: {safe_json_value(diversity_global_summary['delta_p2_separability_weighted'])}",
        f"- dominant_identity_level_pruned: {safe_json_value(diversity_global_summary['dominant_identity_level_pruned'])}",
        f"- dominant_identity_level_weighted: {safe_json_value(diversity_global_summary['dominant_identity_level_weighted'])}",
        f"- replicate_sensitivity_flag: {safe_json_value(diversity_global_summary['replicate_sensitivity_flag'])}",
        f"- final_label: {safe_json_value(diversity_global_summary['final_label'])}",
    ]
    (out_root / "diversity_global_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.6f completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
