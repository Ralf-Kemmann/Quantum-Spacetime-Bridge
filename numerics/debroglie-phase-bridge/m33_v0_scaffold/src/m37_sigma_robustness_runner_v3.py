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
class M37Config:
    enabled: bool
    combined_pair_contributions: Path
    combined_pair_top_summary: Path
    combined_pair_class_summary: Path
    source_pair_kernel: Path
    diversity_case_table: Path
    sigma_factors: List[float]
    min_sigma_p: float
    modes: List[str]
    top_k_values: List[int]
    class_modes: List[str]
    output_root: Path


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def safe_json_value(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): safe_json_value(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [safe_json_value(v) for v in x]
    if isinstance(x, np.ndarray):
        return [safe_json_value(v) for v in x.tolist()]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
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


def load_config(path: Path) -> M37Config:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m37_sigma_robustness"]
    return M37Config(
        enabled=bool(block["enabled"]),
        combined_pair_contributions=Path(block["input"]["combined_pair_contributions"]),
        combined_pair_top_summary=Path(block["input"]["combined_pair_top_summary"]),
        combined_pair_class_summary=Path(block["input"]["combined_pair_class_summary"]),
        source_pair_kernel=Path(block["input"]["source_pair_kernel"]),
        diversity_case_table=Path(block["input"]["diversity_case_table"]),
        sigma_factors=[float(x) for x in block["sweep"]["sigma_factors"]],
        min_sigma_p=float(block["sweep"]["min_sigma_p"]),
        modes=[str(x) for x in block["sweep"]["modes"]],
        top_k_values=[int(x) for x in block["comparison"]["top_k_values"]],
        class_modes=[str(x) for x in block["comparison"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )


def infer_p_values_for_family(raw_cfg: Dict[str, Any], p_family: str) -> np.ndarray:
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


def gaussian_probabilities(p_values: np.ndarray, p0: float, sigma_p: float) -> np.ndarray:
    sigma = max(float(sigma_p), 1.0e-12)
    amp = np.exp(-((p_values - p0) ** 2) / (4.0 * sigma * sigma))
    prob = amp ** 2
    total = float(prob.sum())
    return np.full_like(prob, 1.0 / len(prob), dtype=float) if total <= 0 else prob / total


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


def class_label_from_row(row: pd.Series, class_mode: str) -> str:
    if class_mode == "delta_p":
        return f"dp={row['delta_p']:.6g}"
    if class_mode == "delta_p2":
        return f"dp2={row['delta_p2']:.6g}"
    raise ValueError(f"Unsupported class_mode: {class_mode}")


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


def pair_set(df: pd.DataFrame, top_k: int) -> Set[Tuple[int, int]]:
    sub = df.sort_values("pair_rank_primary", ascending=True).head(top_k)
    return {(int(r["pair_i"]), int(r["pair_j"])) for _, r in sub.iterrows()}


def class_set(df: pd.DataFrame, top_k: int) -> Set[str]:
    sub = df.sort_values("class_rank").head(top_k)
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


def weighted_mean_from_overlap(df: pd.DataFrame, value_col: str) -> Optional[float]:
    if df.empty:
        return None
    if "case_weight_a" not in df.columns or "case_weight_b" not in df.columns:
        return float(df[value_col].mean())
    weights = (df["case_weight_a"].astype(float) * df["case_weight_b"].astype(float)).to_numpy()
    values = df[value_col].astype(float).to_numpy()
    denom = float(weights.sum())
    if denom <= 0:
        return float(values.mean()) if len(values) else None
    return float(np.sum(weights * values) / denom)


def canonize_case_parameters(diversity_df: pd.DataFrame, top_df: pd.DataFrame, pair_df: pd.DataFrame) -> pd.DataFrame:
    out = diversity_df.copy()

    top_cols = [c for c in [
        "case_label", "run_id", "t", "p_family", "theta", "source_feature",
        "best_p0", "best_sigma_p", "best_alpha_source", "branch_label", "branch_pref_readout"
    ] if c in top_df.columns]
    top_case = top_df[top_cols].drop_duplicates("case_label").copy() if top_cols else pd.DataFrame()

    pair_cols = [c for c in [
        "case_label", "run_id", "t", "p_family", "theta", "source_feature",
        "best_p0", "best_sigma_p", "best_alpha_source", "branch_label", "branch_pref_readout"
    ] if c in pair_df.columns]
    pair_case = pair_df[pair_cols].drop_duplicates("case_label").copy() if pair_cols else pd.DataFrame()

    fallback = top_case
    if not pair_case.empty:
        fallback = fallback.merge(pair_case, on="case_label", how="outer", suffixes=("_top", "_pair")) if not fallback.empty else pair_case

    if not fallback.empty:
        for base in ["run_id", "t", "p_family", "theta", "source_feature", "best_p0", "best_sigma_p", "best_alpha_source", "branch_label", "branch_pref_readout"]:
            if base not in fallback.columns:
                cand = [f"{base}_top", f"{base}_pair"]
                existing = [c for c in cand if c in fallback.columns]
                if existing:
                    fallback[base] = None
                    for c in existing:
                        fallback[base] = fallback[base].where(fallback[base].notna(), fallback[c])
        merge_cols = [c for c in ["case_label", "run_id", "t", "p_family", "theta", "source_feature", "best_p0", "best_sigma_p", "best_alpha_source", "branch_label"] if c in fallback.columns]
        fallback = fallback[merge_cols].drop_duplicates("case_label")

        out = out.merge(fallback, on="case_label", how="left", suffixes=("", "_fb"))

        for base in ["run_id", "t", "p_family", "theta", "source_feature", "best_p0", "best_sigma_p", "best_alpha_source", "branch_label"]:
            fb = f"{base}_fb"
            if fb in out.columns:
                if base not in out.columns:
                    out[base] = out[fb]
                else:
                    out[base] = out[base].where(out[base].notna(), out[fb])

    if "branch_pref_readout" in out.columns:
        out["branch_label"] = out["branch_label"].where(out["branch_label"].notna(), out["branch_pref_readout"])

    return out


def audit_case_sigma(
    case_row: pd.Series,
    sigma_factor: float,
    pair_kernel_df: pd.DataFrame,
    raw_cfg: Dict[str, Any],
    class_modes: List[str],
    min_sigma_p: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    run_id = str(case_row["run_id"])
    case_label = str(case_row["case_label"])
    branch_label = case_row.get("branch_label")
    mode = str(case_row["selection_mode"])
    t = float(case_row["t"])
    p_family = str(case_row["p_family"])
    theta = float(case_row["theta"])
    source_feature = str(case_row["source_feature"])
    best_p0 = float(case_row["best_p0"])
    sigma_p_base = float(case_row["best_sigma_p"])
    sigma_p_test = max(float(min_sigma_p), sigma_p_base * float(sigma_factor))
    best_alpha_source = float(case_row["best_alpha_source"])
    diversity_group = case_row.get("diversity_group")
    group_weight = float(case_row.get("group_weight", 1.0))

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
    pair_weights = pair_weights_from_best_fit(pair_slice, p_values, best_p0, sigma_p_test)

    pair_rows: List[Dict[str, Any]] = []
    for prow in pair_slice.itertuples(index=False):
        key = (int(prow.pair_i), int(prow.pair_j))
        w = float(pair_weights.get(key, 0.0))
        kbar = float(prow.kbar_ij)
        p_i = float(prow.p_i)
        p_j = float(prow.p_j)
        contrib_neg, contrib_abs, contrib_signed, contrib_primary = contribution_triplet(source_feature, w, kbar)

        pair_rows.append(
            {
                "run_id": run_id,
                "case_label": case_label,
                "branch_label": branch_label,
                "mode": mode,
                "sigma_factor": float(sigma_factor),
                "sigma_p_test": sigma_p_test,
                "t": t,
                "p_family": p_family,
                "theta": theta,
                "source_feature": source_feature,
                "best_p0": best_p0,
                "sigma_p_base": sigma_p_base,
                "best_alpha_source": best_alpha_source,
                "diversity_group": diversity_group,
                "group_weight": group_weight,
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
            }
        )

    pair_df = pd.DataFrame(pair_rows).sort_values("contrib_primary", ascending=False).reset_index(drop=True)
    total = float(pair_df["contrib_primary"].sum())
    pair_df["normalized_contrib_primary"] = np.where(total > 0, pair_df["contrib_primary"] / total, 0.0)
    pair_df["pair_rank_primary"] = np.arange(1, len(pair_df) + 1)

    normed = pair_df["normalized_contrib_primary"].to_numpy(dtype=float)
    top_df = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "case_label": case_label,
                "branch_label": branch_label,
                "mode": mode,
                "sigma_factor": float(sigma_factor),
                "sigma_p_test": sigma_p_test,
                "t": t,
                "p_family": p_family,
                "theta": theta,
                "source_feature": source_feature,
                "best_p0": best_p0,
                "sigma_p_base": sigma_p_base,
                "best_alpha_source": best_alpha_source,
                "diversity_group": diversity_group,
                "group_weight": group_weight,
                "n_pairs_total": int(len(pair_df)),
                "top1_share": top_share(normed, 1),
                "top3_share": top_share(normed, 3),
                "top5_share": top_share(normed, 5),
                "effective_pair_count": effective_pair_count(normed),
                "dominance_label": dominance_label(top_share(normed, 3), effective_pair_count(normed)),
            }
        ]
    )

    class_rows: List[Dict[str, Any]] = []
    for class_mode in class_modes:
        tmp = pair_df.copy()
        tmp["class_mode"] = class_mode
        tmp["class_label"] = tmp.apply(lambda r: class_label_from_row(r, class_mode), axis=1)

        grouped = (
            tmp.groupby(["class_mode", "class_label"], dropna=False)
            .agg(sum_contrib_primary=("contrib_primary", "sum"))
            .reset_index()
            .sort_values("sum_contrib_primary", ascending=False)
            .reset_index(drop=True)
        )

        total_class = float(grouped["sum_contrib_primary"].sum())
        grouped["normalized_class_contrib"] = np.where(total_class > 0, grouped["sum_contrib_primary"] / total_class, 0.0)
        grouped["class_rank"] = np.arange(1, len(grouped) + 1)

        for grow in grouped.itertuples(index=False):
            class_rows.append(
                {
                    "run_id": run_id,
                    "case_label": case_label,
                    "branch_label": branch_label,
                    "mode": mode,
                    "sigma_factor": float(sigma_factor),
                    "sigma_p_test": sigma_p_test,
                    "t": t,
                    "p_family": p_family,
                    "theta": theta,
                    "source_feature": source_feature,
                    "best_p0": best_p0,
                    "sigma_p_base": sigma_p_base,
                    "best_alpha_source": best_alpha_source,
                    "diversity_group": diversity_group,
                    "group_weight": group_weight,
                    "class_mode": grow.class_mode,
                    "class_label": grow.class_label,
                    "class_rank": int(grow.class_rank),
                    "sum_contrib_primary": float(grow.sum_contrib_primary),
                    "normalized_class_contrib": float(grow.normalized_class_contrib),
                }
            )

    class_df = pd.DataFrame(class_rows)
    return pair_df, top_df, class_df


def build_overlap_tables(
    pair_df: pd.DataFrame,
    class_df: pd.DataFrame,
    case_weights: Dict[str, float],
    top_k_values: List[int],
    class_modes: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    pair_rows: List[Dict[str, Any]] = []
    class_rows: List[Dict[str, Any]] = []

    meta = (
        pair_df[["run_id", "case_label", "branch_label"]]
        .drop_duplicates()
        .set_index("case_label")
    )

    grouped_pairs = {case: g.copy() for case, g in pair_df.groupby("case_label", dropna=False)}
    case_labels = sorted(grouped_pairs.keys())

    for i, case_a in enumerate(case_labels):
        for case_b in case_labels[i + 1:]:
            df_a = grouped_pairs[case_a]
            df_b = grouped_pairs[case_b]
            run_id = meta.loc[case_a, "run_id"]
            branch_a = meta.loc[case_a, "branch_label"]
            branch_b = meta.loc[case_b, "branch_label"]
            rel = "within_branch" if pd.notna(branch_a) and pd.notna(branch_b) and branch_a == branch_b else "between_branch"
            w_a = float(case_weights.get(case_a, 1.0))
            w_b = float(case_weights.get(case_b, 1.0))
            for k in top_k_values:
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
                        "pair_overlap_weighted_by_case": raw_overlap * w_a * w_b,
                        "relation_type": rel,
                    }
                )

    grouped_classes = {(case, mode): g.copy() for (case, mode), g in class_df.groupby(["case_label", "class_mode"], dropna=False)}
    for mode in class_modes:
        mode_cases = sorted([case for (case, m) in grouped_classes.keys() if m == mode])
        for i, case_a in enumerate(mode_cases):
            for case_b in mode_cases[i + 1:]:
                df_a = grouped_classes[(case_a, mode)]
                df_b = grouped_classes[(case_b, mode)]
                run_id = meta.loc[case_a, "run_id"]
                branch_a = meta.loc[case_a, "branch_label"]
                branch_b = meta.loc[case_b, "branch_label"]
                rel = "within_branch" if pd.notna(branch_a) and pd.notna(branch_b) and branch_a == branch_b else "between_branch"
                w_a = float(case_weights.get(case_a, 1.0))
                w_b = float(case_weights.get(case_b, 1.0))
                for k in top_k_values:
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
                            "class_overlap_weighted_by_case": raw_overlap * w_a * w_b,
                            "relation_type": rel,
                        }
                    )

    return pd.DataFrame(pair_rows), pd.DataFrame(class_rows)


def compute_scores_for_mode_sigma(
    mode: str,
    sigma_factor: float,
    pair_df: pd.DataFrame,
    class_df: pd.DataFrame,
    case_weights: Dict[str, float],
    top_k_values: List[int],
    class_modes: List[str],
) -> Tuple[Dict[str, Any], pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pair_overlap_df, class_overlap_df = build_overlap_tables(
        pair_df=pair_df,
        class_df=class_df,
        case_weights=case_weights,
        top_k_values=top_k_values,
        class_modes=class_modes,
    )

    pair_within = weighted_mean_from_overlap(
        pair_overlap_df[(pair_overlap_df["relation_type"] == "within_branch") & (pair_overlap_df["top_k"] == 3)],
        "weighted_pair_overlap",
    )
    pair_between = weighted_mean_from_overlap(
        pair_overlap_df[(pair_overlap_df["relation_type"] == "between_branch") & (pair_overlap_df["top_k"] == 3)],
        "weighted_pair_overlap",
    )
    dp_within = weighted_mean_from_overlap(
        class_overlap_df[(class_overlap_df["relation_type"] == "within_branch") & (class_overlap_df["class_mode"] == "delta_p") & (class_overlap_df["top_k"] == 3)],
        "weighted_class_overlap",
    )
    dp_between = weighted_mean_from_overlap(
        class_overlap_df[(class_overlap_df["relation_type"] == "between_branch") & (class_overlap_df["class_mode"] == "delta_p") & (class_overlap_df["top_k"] == 3)],
        "weighted_class_overlap",
    )
    dp2_within = weighted_mean_from_overlap(
        class_overlap_df[(class_overlap_df["relation_type"] == "within_branch") & (class_overlap_df["class_mode"] == "delta_p2") & (class_overlap_df["top_k"] == 3)],
        "weighted_class_overlap",
    )
    dp2_between = weighted_mean_from_overlap(
        class_overlap_df[(class_overlap_df["relation_type"] == "between_branch") & (class_overlap_df["class_mode"] == "delta_p2") & (class_overlap_df["top_k"] == 3)],
        "weighted_class_overlap",
    )

    pair_sep = None if pair_within is None or pair_between is None else pair_within - pair_between
    dp_sep = None if dp_within is None or dp_between is None else dp_within - dp_between
    dp2_sep = None if dp2_within is None or dp2_between is None else dp2_within - dp2_between

    score_map = {
        "pair": pair_sep if pair_sep is not None else -np.inf,
        "delta_p_class": dp_sep if dp_sep is not None else -np.inf,
        "delta_p2_class": dp2_sep if dp2_sep is not None else -np.inf,
    }
    dominant = max(score_map, key=score_map.get)
    if score_map[dominant] == -np.inf:
        dominant = None

    if (dp2_sep or 0.0) > 0.1:
        robust_label = "delta_p2_robust"
    elif (dp_sep or 0.0) > 0.1:
        robust_label = "delta_p_robust"
    elif (pair_sep or 0.0) > 0.1:
        robust_label = "pair_only"
    else:
        robust_label = "weak"

    global_row = {
        "run_id": pair_df["run_id"].iloc[0] if not pair_df.empty else None,
        "mode": mode,
        "sigma_factor": sigma_factor,
        "n_cases_effective": float(sum(case_weights.values())),
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
        "robust_identity_label": robust_label,
    }

    branch_rows: List[Dict[str, Any]] = []
    for branch in sorted(pair_df["branch_label"].dropna().unique().tolist()):
        case_labels = pair_df.loc[pair_df["branch_label"] == branch, "case_label"].drop_duplicates().tolist()
        n_eff = float(sum(case_weights.get(c, 1.0) for c in case_labels))

        b_pair_within = weighted_mean_from_overlap(
            pair_overlap_df[(pair_overlap_df["relation_type"] == "within_branch") & (pair_overlap_df["branch_a"] == branch) & (pair_overlap_df["top_k"] == 3)],
            "weighted_pair_overlap",
        )
        b_pair_between = weighted_mean_from_overlap(
            pair_overlap_df[(pair_overlap_df["relation_type"] == "between_branch") & ((pair_overlap_df["branch_a"] == branch) | (pair_overlap_df["branch_b"] == branch)) & (pair_overlap_df["top_k"] == 3)],
            "weighted_pair_overlap",
        )
        b_dp_within = weighted_mean_from_overlap(
            class_overlap_df[(class_overlap_df["relation_type"] == "within_branch") & (class_overlap_df["branch_a"] == branch) & (class_overlap_df["class_mode"] == "delta_p") & (class_overlap_df["top_k"] == 3)],
            "weighted_class_overlap",
        )
        b_dp_between = weighted_mean_from_overlap(
            class_overlap_df[(class_overlap_df["relation_type"] == "between_branch") & ((class_overlap_df["branch_a"] == branch) | (class_overlap_df["branch_b"] == branch)) & (class_overlap_df["class_mode"] == "delta_p") & (class_overlap_df["top_k"] == 3)],
            "weighted_class_overlap",
        )
        b_dp2_within = weighted_mean_from_overlap(
            class_overlap_df[(class_overlap_df["relation_type"] == "within_branch") & (class_overlap_df["branch_a"] == branch) & (class_overlap_df["class_mode"] == "delta_p2") & (class_overlap_df["top_k"] == 3)],
            "weighted_class_overlap",
        )
        b_dp2_between = weighted_mean_from_overlap(
            class_overlap_df[(class_overlap_df["relation_type"] == "between_branch") & ((class_overlap_df["branch_a"] == branch) | (class_overlap_df["branch_b"] == branch)) & (class_overlap_df["class_mode"] == "delta_p2") & (class_overlap_df["top_k"] == 3)],
            "weighted_class_overlap",
        )

        b_pair_sep = None if b_pair_within is None or b_pair_between is None else b_pair_within - b_pair_between
        b_dp_sep = None if b_dp_within is None or b_dp_between is None else b_dp_within - b_dp_between
        b_dp2_sep = None if b_dp2_within is None or b_dp2_between is None else b_dp2_within - b_dp2_between

        if (b_pair_sep or 0.0) > 0.2:
            sig = "pair_specific"
        elif ((b_dp_sep or 0.0) > 0.05) or ((b_dp2_sep or 0.0) > 0.05):
            sig = "class_specific"
        else:
            sig = "weak_or_none"

        branch_rows.append(
            {
                "run_id": global_row["run_id"],
                "mode": mode,
                "branch_label": branch,
                "sigma_factor": sigma_factor,
                "n_cases_effective": n_eff,
                "pair_separability_score": b_pair_sep,
                "delta_p_separability_score": b_dp_sep,
                "delta_p2_separability_score": b_dp2_sep,
                "signature_label": sig,
            }
        )

    return global_row, pd.DataFrame(branch_rows), pair_overlap_df, class_overlap_df


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.7 sigma_p robustness sweep v3")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.7 disabled in config. Exiting.")
        return

    with config_path.open("r", encoding="utf-8") as f:
        raw_cfg = yaml.safe_load(f)

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    pair_in = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_contributions)))
    top_in = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_top_summary)))
    class_in = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_class_summary)))
    pair_kernel_df = pd.read_csv(resolve_path(project_root, cfg.source_pair_kernel))
    diversity_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.diversity_case_table)))

    diversity_df = canonize_case_parameters(diversity_df, top_in, pair_in)

    keep_cols = [
        "run_id", "case_label", "branch_label", "selection_mode", "t", "p_family", "theta",
        "source_feature", "best_alpha_source", "best_sigma_p", "best_p0",
        "diversity_group", "group_weight", "is_group_representative"
    ]
    available_cols = [c for c in keep_cols if c in diversity_df.columns]
    cases_df = diversity_df[available_cols].drop_duplicates().copy()

    required = ["run_id", "case_label", "branch_label", "selection_mode", "t", "p_family", "theta", "source_feature", "best_alpha_source", "best_sigma_p", "best_p0"]
    missing_required = [c for c in required if c not in cases_df.columns]
    if missing_required:
        raise ValueError(f"Missing required columns after fallback merge: {missing_required}")

    sigma_case_rows: List[Dict[str, Any]] = []
    pair_top_frames: List[pd.DataFrame] = []
    class_frames: List[pd.DataFrame] = []
    global_rows: List[Dict[str, Any]] = []
    branch_score_frames: List[pd.DataFrame] = []
    pair_overlap_frames: List[pd.DataFrame] = []
    class_overlap_frames: List[pd.DataFrame] = []

    for mode in cfg.modes:
        mode_cases = cases_df[cases_df["selection_mode"] == mode].copy()
        if mode_cases.empty:
            continue
        if mode == "pruned":
            mode_cases = mode_cases[mode_cases["is_group_representative"].fillna(0).astype(int) == 1].copy()

        for sigma_factor in cfg.sigma_factors:
            pair_case_frames: List[pd.DataFrame] = []
            top_case_frames: List[pd.DataFrame] = []
            class_case_frames: List[pd.DataFrame] = []
            case_weights: Dict[str, float] = {}

            for _, case_row in mode_cases.iterrows():
                sigma_case_rows.append(
                    {
                        "run_id": case_row["run_id"],
                        "case_label": case_row["case_label"],
                        "branch_label": case_row["branch_label"],
                        "mode": mode,
                        "t": case_row["t"],
                        "p_family": case_row["p_family"],
                        "theta": case_row["theta"],
                        "source_feature": case_row["source_feature"],
                        "best_p0": case_row["best_p0"],
                        "sigma_p_base": case_row["best_sigma_p"],
                        "sigma_factor": float(sigma_factor),
                        "sigma_p_test": max(cfg.min_sigma_p, float(case_row["best_sigma_p"]) * float(sigma_factor)),
                        "best_alpha_source": case_row["best_alpha_source"],
                        "diversity_group": case_row.get("diversity_group"),
                        "group_weight": case_row.get("group_weight", 1.0),
                    }
                )

                pair_df, top_df, class_df = audit_case_sigma(
                    case_row=case_row,
                    sigma_factor=float(sigma_factor),
                    pair_kernel_df=pair_kernel_df,
                    raw_cfg=raw_cfg,
                    class_modes=cfg.class_modes,
                    min_sigma_p=cfg.min_sigma_p,
                )

                if not pair_df.empty:
                    pair_case_frames.append(pair_df)
                    case_weights[str(case_row["case_label"])] = float(case_row.get("group_weight", 1.0) if mode == "weighted" else 1.0)
                if not top_df.empty:
                    top_case_frames.append(top_df)
                if not class_df.empty:
                    class_case_frames.append(class_df)

            pair_sigma_df = pd.concat(pair_case_frames, ignore_index=True) if pair_case_frames else pd.DataFrame()
            top_sigma_df = pd.concat(top_case_frames, ignore_index=True) if top_case_frames else pd.DataFrame()
            class_sigma_df = pd.concat(class_case_frames, ignore_index=True) if class_case_frames else pd.DataFrame()

            if not top_sigma_df.empty:
                pair_top_frames.append(top_sigma_df)
            if not class_sigma_df.empty:
                class_frames.append(class_sigma_df)

            if not pair_sigma_df.empty and not class_sigma_df.empty:
                global_row, branch_df, pair_overlap_df, class_overlap_df = compute_scores_for_mode_sigma(
                    mode=mode,
                    sigma_factor=float(sigma_factor),
                    pair_df=pair_sigma_df,
                    class_df=class_sigma_df,
                    case_weights=case_weights,
                    top_k_values=cfg.top_k_values,
                    class_modes=cfg.class_modes,
                )
                global_rows.append(global_row)
                if not branch_df.empty:
                    branch_score_frames.append(branch_df)
                if not pair_overlap_df.empty:
                    pair_overlap_df["mode"] = mode
                    pair_overlap_df["sigma_factor"] = float(sigma_factor)
                    pair_overlap_frames.append(pair_overlap_df)
                if not class_overlap_df.empty:
                    class_overlap_df["mode"] = mode
                    class_overlap_df["sigma_factor"] = float(sigma_factor)
                    class_overlap_frames.append(class_overlap_df)

    sigma_case_grid_df = pd.DataFrame(sigma_case_rows)
    sigma_pair_top_summary_df = pd.concat(pair_top_frames, ignore_index=True) if pair_top_frames else pd.DataFrame()
    sigma_class_summary_df = pd.concat(class_frames, ignore_index=True) if class_frames else pd.DataFrame()
    sigma_global_scores_df = pd.DataFrame(global_rows)
    sigma_branch_scores_df = pd.concat(branch_score_frames, ignore_index=True) if branch_score_frames else pd.DataFrame()
    sigma_pair_overlap_df = pd.concat(pair_overlap_frames, ignore_index=True) if pair_overlap_frames else pd.DataFrame()
    sigma_class_overlap_df = pd.concat(class_overlap_frames, ignore_index=True) if class_overlap_frames else pd.DataFrame()

    sigma_case_grid_df.to_csv(out_root / "sigma_case_grid.csv", index=False)
    sigma_pair_top_summary_df.to_csv(out_root / "sigma_pair_top_summary.csv", index=False)
    sigma_class_summary_df.to_csv(out_root / "sigma_class_summary.csv", index=False)
    sigma_global_scores_df.to_csv(out_root / "sigma_global_scores.csv", index=False)
    sigma_branch_scores_df.to_csv(out_root / "sigma_branch_scores.csv", index=False)
    sigma_pair_overlap_df.to_csv(out_root / "sigma_pair_overlap.csv", index=False)
    sigma_class_overlap_df.to_csv(out_root / "sigma_class_overlap.csv", index=False)

    dp2_pos_frac = float((sigma_global_scores_df["delta_p2_separability_score"] > 0).mean()) if not sigma_global_scores_df.empty else 0.0
    dp_pos_frac = float((sigma_global_scores_df["delta_p_separability_score"] > 0).mean()) if not sigma_global_scores_df.empty else 0.0
    pair_pos_frac = float((sigma_global_scores_df["pair_separability_score"] > 0).mean()) if not sigma_global_scores_df.empty else 0.0

    sigma_band_dp2 = sigma_global_scores_df.loc[
        sigma_global_scores_df["delta_p2_separability_score"].fillna(-np.inf) > 0.1,
        "sigma_factor"
    ].tolist()

    sigma_collapse_pair = None
    neg_pair = sigma_global_scores_df.loc[
        sigma_global_scores_df["pair_separability_score"].fillna(np.inf) <= 0,
        "sigma_factor"
    ]
    if not neg_pair.empty:
        sigma_collapse_pair = float(neg_pair.min())

    dominant_counts = sigma_global_scores_df["dominant_identity_level"].value_counts(dropna=True) if not sigma_global_scores_df.empty else pd.Series(dtype=int)
    best_identity_level = str(dominant_counts.idxmax()) if not dominant_counts.empty else None

    replicate_sensitive_flag = 0
    if not sigma_global_scores_df.empty and set(["pruned", "weighted"]).issubset(set(sigma_global_scores_df["mode"].unique())):
        merged = sigma_global_scores_df.pivot_table(index="sigma_factor", columns="mode", values="delta_p2_separability_score", aggfunc="first")
        if {"pruned", "weighted"}.issubset(set(merged.columns)):
            diff = (merged["weighted"] - merged["pruned"]).abs().dropna()
            if not diff.empty and float(diff.max()) > 0.25:
                replicate_sensitive_flag = 1

    if dp2_pos_frac >= 0.7 and pair_pos_frac >= 0.4 and replicate_sensitive_flag == 0:
        final_label = "G3"
    elif dp2_pos_frac >= 0.7 and replicate_sensitive_flag == 0:
        final_label = "G2"
    elif dp2_pos_frac > 0 or dp_pos_frac > 0:
        final_label = "G1"
    else:
        final_label = "G0"

    summary = {
        "best_identity_level": best_identity_level,
        "delta_p2_positive_fraction": dp2_pos_frac,
        "delta_p_positive_fraction": dp_pos_frac,
        "pair_positive_fraction": pair_pos_frac,
        "sigma_robust_band_delta_p2": sigma_band_dp2,
        "sigma_collapse_threshold_pair": sigma_collapse_pair,
        "replicate_sensitive_flag": replicate_sensitive_flag,
        "final_label": final_label,
    }
    write_json(out_root / "sigma_robustness_summary.json", summary)

    report_lines = [
        "# M.3.7 Sigma Robustness Sweep",
        "",
        f"- best_identity_level: {safe_json_value(summary['best_identity_level'])}",
        f"- delta_p2_positive_fraction: {safe_json_value(summary['delta_p2_positive_fraction'])}",
        f"- delta_p_positive_fraction: {safe_json_value(summary['delta_p_positive_fraction'])}",
        f"- pair_positive_fraction: {safe_json_value(summary['pair_positive_fraction'])}",
        f"- sigma_robust_band_delta_p2: {safe_json_value(summary['sigma_robust_band_delta_p2'])}",
        f"- sigma_collapse_threshold_pair: {safe_json_value(summary['sigma_collapse_threshold_pair'])}",
        f"- replicate_sensitive_flag: {safe_json_value(summary['replicate_sensitive_flag'])}",
        f"- final_label: {safe_json_value(summary['final_label'])}",
    ]
    (out_root / "sigma_robustness_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.7 completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
