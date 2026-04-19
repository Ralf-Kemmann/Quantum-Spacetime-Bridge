#!/usr/bin/env python3
"""
m39x3ea_feature_distance_diagnosis_runner.py

M.3.9x.3e.a — Feature-wise Distanzdiagnose

Ziel:
- den negativen Modell-Überlappungsbefund aus M39x3e zerlegen
- Distanzbeiträge pro Feature sichtbar machen
- pro Pair Set diagnostizieren, ob wenige oder viele Features treiben
- Sensitivität unter Ablation, Reweighting und alternativer Normierung prüfen
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import yaml


# ---------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------

def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(obj: Dict[str, Any], path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def write_markdown(text: str, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def parse_weighted_difference_source(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "pair_set_id",
        "fsw_regime_id",
        "ao_regime_id",
        "feature_name",
        "fsw_value",
        "ao_value",
        "raw_difference",
        "abs_difference",
        "normalized_difference",
        "feature_weight",
        "weighted_difference",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"pair_feature_comparison_csv missing columns: {sorted(missing)}")
    return df.copy()


def parse_pair_summary_source(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "pair_set_id",
        "fsw_regime_id",
        "ao_regime_id",
        "dominant_marker_match_flag",
        "irregularity_level_match_flag",
        "weighted_overlap_distance_score",
        "overlap_status",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"pair_overlap_summary_csv missing columns: {sorted(missing)}")
    return df.copy()


def parse_group_summary_source(df: pd.DataFrame) -> pd.DataFrame:
    required = {
        "pair_set_id",
        "mean_overlap_distance",
        "group_overlap_status",
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"group_overlap_summary_csv missing columns: {sorted(missing)}")
    return df.copy()


def pair_status_from_score(score: float, cfg: Dict[str, Any]) -> str:
    thr = cfg["pair_overlap_thresholds"]
    if score <= float(thr["strong_overlap_max"]):
        return "strong_overlap"
    if score <= float(thr["partial_overlap_max"]):
        return "partial_overlap"
    if score <= float(thr["weak_overlap_max"]):
        return "weak_overlap"
    return "no_meaningful_overlap"


def feature_contribution_judgement(rel_share: float) -> str:
    if rel_share >= 0.50:
        return "dominant"
    if rel_share >= 0.25:
        return "strong"
    if rel_share >= 0.10:
        return "moderate"
    return "minor"


def group_pattern_from_shares(top1: float, top2sum: float, cfg: Dict[str, Any]) -> str:
    logic = cfg["contribution_pattern_logic"]
    if top1 >= 0.50:
        return "single_feature_dominates_distance"
    if top2sum >= 0.70:
        return "two_feature_cluster_dominates_distance"
    if top1 < 0.40 and top2sum < 0.70:
        return "distance_broadly_distributed"
    return "mixed_distribution"


def safe_bool(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def normalize_column(series: pd.Series, method: str, group_key: pd.Series | None = None, eps: float = 1e-12) -> pd.Series:
    s = series.astype(float)

    if method == "from_source_run":
        # already normalized in source
        return s

    if method == "zscore_from_source_run":
        mu = float(s.mean())
        sigma = float(s.std())
        if np.isclose(sigma, 0.0):
            return pd.Series(np.zeros(len(s)), index=s.index, dtype=float)
        z = (s - mu) / sigma
        # squash to positive scale via abs(z)
        return z.abs()

    if method == "local_pairset_range":
        if group_key is None:
            raise ValueError("local_pairset_range requires group_key")
        out = pd.Series(index=s.index, dtype=float)
        for g, idx in group_key.groupby(group_key).groups.items():
            sub = s.loc[idx]
            mn = float(sub.min())
            mx = float(sub.max())
            rng = mx - mn
            if np.isclose(rng, 0.0):
                out.loc[idx] = 0.0
            else:
                out.loc[idx] = (sub - mn).abs() / max(rng, eps)
        return out

    raise ValueError(f"Unsupported normalization method: {method}")


def pair_note_from_status(status: str) -> str:
    notes = {
        "strong_overlap": "Strong overlap under this sensitivity setting.",
        "partial_overlap": "Partial overlap under this sensitivity setting.",
        "weak_overlap": "Weak overlap under this sensitivity setting.",
        "no_meaningful_overlap": "No meaningful overlap under this sensitivity setting.",
    }
    return notes.get(status, status)


def best_group_status_from_mean(mean_score: float, cfg: Dict[str, Any]) -> str:
    thr = cfg["pair_overlap_thresholds"]
    if mean_score <= float(thr["strong_overlap_max"]):
        return "shared_type_B_overlap_supported"
    if mean_score <= float(thr["partial_overlap_max"]):
        return "shared_quantitative_type_B_overlap_supported"
    if mean_score <= float(thr["weak_overlap_max"]):
        return "weak_model_overlap_only"
    return "no_meaningful_model_overlap"


# ---------------------------------------------------------------------
# Baseline contribution analysis
# ---------------------------------------------------------------------

def build_pair_feature_contribution(
    pair_feature_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> pd.DataFrame:
    eps = float(cfg["contribution_metrics"].get("epsilon", 1.0e-12))
    rows: List[Dict[str, Any]] = []

    group_cols = ["pair_set_id", "fsw_regime_id", "ao_regime_id"]
    for keys, sub in pair_feature_df.groupby(group_cols, sort=False):
        total = float(sub["weighted_difference"].sum())
        total = max(total, eps)

        for _, row in sub.iterrows():
            rel_share = float(row["weighted_difference"]) / total
            rows.append({
                "pair_set_id": row["pair_set_id"],
                "fsw_regime_id": row["fsw_regime_id"],
                "ao_regime_id": row["ao_regime_id"],
                "feature_name": row["feature_name"],
                "fsw_value": float(row["fsw_value"]),
                "ao_value": float(row["ao_value"]),
                "raw_difference": float(row["raw_difference"]),
                "abs_difference": float(row["abs_difference"]),
                "normalized_difference": float(row["normalized_difference"]),
                "feature_weight": float(row["feature_weight"]),
                "weighted_difference": float(row["weighted_difference"]),
                "relative_contribution": rel_share,
                "contribution_judgement": feature_contribution_judgement(rel_share),
            })

    return pd.DataFrame(rows)


def build_pair_set_feature_diagnosis(
    contribution_df: pd.DataFrame,
    target_pair_sets: List[str],
    cfg: Dict[str, Any],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for pair_set_id in target_pair_sets:
        sub = contribution_df[contribution_df["pair_set_id"] == pair_set_id].copy()
        if len(sub) == 0:
            continue

        feat_agg = (
            sub.groupby("feature_name", as_index=False)
            .agg(
                mean_weighted_difference=("weighted_difference", "mean"),
                mean_relative_contribution=("relative_contribution", "mean"),
                median_relative_contribution=("relative_contribution", "median"),
                max_relative_contribution=("relative_contribution", "max"),
            )
            .sort_values("mean_relative_contribution", ascending=False)
            .reset_index(drop=True)
        )

        top1 = float(feat_agg.iloc[0]["mean_relative_contribution"])
        top_feature = str(feat_agg.iloc[0]["feature_name"])
        if len(feat_agg) >= 2:
            top2_feature = str(feat_agg.iloc[1]["feature_name"])
            top2sum = float(feat_agg.iloc[0]["mean_relative_contribution"] + feat_agg.iloc[1]["mean_relative_contribution"])
        else:
            top2_feature = ""
            top2sum = top1

        distribution_pattern = group_pattern_from_shares(top1, top2sum, cfg)

        rows.append({
            "pair_set_id": pair_set_id,
            "dominant_distance_feature": top_feature,
            "second_distance_feature": top2_feature,
            "top_feature_relative_contribution": top1,
            "top_2_features_relative_contribution_sum": top2sum,
            "distribution_pattern": distribution_pattern,
            "mean_pair_distance": float(
                sub.groupby(["pair_set_id", "fsw_regime_id", "ao_regime_id"])["weighted_difference"].sum().mean()
            ),
            "n_pairs": int(sub.groupby(["pair_set_id", "fsw_regime_id", "ao_regime_id"]).ngroups),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Sensitivity recomputation
# ---------------------------------------------------------------------

def recompute_sensitivity(
    baseline_feature_df: pd.DataFrame,
    pair_summary_df: pd.DataFrame,
    group_summary_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> pd.DataFrame:
    tests = cfg["sensitivity_tests"]
    rows: List[Dict[str, Any]] = []
    baseline_group_map = {
        row["pair_set_id"]: row["group_overlap_status"]
        for _, row in group_summary_df.iterrows()
    }

    numeric_features_all = cfg["diagnostic_features"]

    for test in tests:
        test_id = test["test_id"]
        normalization = test.get("normalization", "from_source_run")
        weights_spec = test.get("weights", "from_source_run")
        keep_features = test.get("keep_features")
        drop_features = test.get("drop_features", [])

        if keep_features is None:
            keep_features = [f for f in numeric_features_all if f not in drop_features]
        keep_features = list(keep_features)

        sub = baseline_feature_df[baseline_feature_df["feature_name"].isin(keep_features)].copy()

        if len(sub) == 0:
            continue

        # weights
        if weights_spec == "from_source_run":
            sub["effective_weight"] = sub["feature_weight"].astype(float)
        else:
            sub["effective_weight"] = sub["feature_name"].map(weights_spec).astype(float)

        # normalization
        if normalization == "from_source_run":
            sub["effective_norm_diff"] = sub["normalized_difference"].astype(float)
        elif normalization == "zscore_from_source_run":
            # feature-wise z-score on absolute raw differences
            tmp = []
            for feat, feat_sub in sub.groupby("feature_name", sort=False):
                normed = normalize_column(feat_sub["abs_difference"], "zscore_from_source_run")
                feat_sub = feat_sub.copy()
                feat_sub["effective_norm_diff"] = normed.values
                tmp.append(feat_sub)
            sub = pd.concat(tmp, ignore_index=True)
        elif normalization == "local_pairset_range":
            tmp = []
            for feat, feat_sub in sub.groupby("feature_name", sort=False):
                normed = normalize_column(
                    feat_sub["abs_difference"],
                    "local_pairset_range",
                    group_key=feat_sub["pair_set_id"],
                )
                feat_sub = feat_sub.copy()
                feat_sub["effective_norm_diff"] = normed.values
                tmp.append(feat_sub)
            sub = pd.concat(tmp, ignore_index=True)
        else:
            raise ValueError(f"Unsupported normalization in test {test_id}: {normalization}")

        sub["effective_weighted_difference"] = sub["effective_norm_diff"] * sub["effective_weight"]

        # pair-level recompute
        pair_rows = []
        for (pair_set_id, fsw_regime_id, ao_regime_id), psub in sub.groupby(
            ["pair_set_id", "fsw_regime_id", "ao_regime_id"], sort=False
        ):
            base_pair = pair_summary_df[
                (pair_summary_df["pair_set_id"] == pair_set_id)
                & (pair_summary_df["fsw_regime_id"] == fsw_regime_id)
                & (pair_summary_df["ao_regime_id"] == ao_regime_id)
            ]
            if len(base_pair) != 1:
                continue
            base_pair = base_pair.iloc[0]

            penalty = 0.0
            # baseline pair score = sum(weighted diffs) + cat penalties
            # so recover cat penalty from baseline
            baseline_feature_sum = float(
                baseline_feature_df[
                    (baseline_feature_df["pair_set_id"] == pair_set_id)
                    & (baseline_feature_df["fsw_regime_id"] == fsw_regime_id)
                    & (baseline_feature_df["ao_regime_id"] == ao_regime_id)
                ]["weighted_difference"].sum()
            )
            baseline_pair_score = float(base_pair["weighted_overlap_distance_score"])
            penalty = max(0.0, baseline_pair_score - baseline_feature_sum)

            new_score = float(psub["effective_weighted_difference"].sum() + penalty)
            new_status = pair_status_from_score(new_score, cfg)

            pair_rows.append({
                "test_id": test_id,
                "pair_set_id": pair_set_id,
                "fsw_regime_id": fsw_regime_id,
                "ao_regime_id": ao_regime_id,
                "recomputed_score": new_score,
                "recomputed_status": new_status,
            })

        pair_re_df = pd.DataFrame(pair_rows)

        # group-level summary for this test
        for pair_set_id, gsub in pair_re_df.groupby("pair_set_id", sort=False):
            mean_score = float(gsub["recomputed_score"].mean())
            strong_count = int((gsub["recomputed_status"] == "strong_overlap").sum())
            partial_count = int((gsub["recomputed_status"] == "partial_overlap").sum())
            weak_count = int((gsub["recomputed_status"] == "weak_overlap").sum())
            no_count = int((gsub["recomputed_status"] == "no_meaningful_overlap").sum())

            recomputed_group_status = best_group_status_from_mean(mean_score, cfg)
            baseline_status = baseline_group_map.get(pair_set_id, "unknown")
            improved = baseline_status != recomputed_group_status and (
                baseline_status == "no_meaningful_model_overlap"
                and recomputed_group_status in {
                    "weak_model_overlap_only",
                    "shared_quantitative_type_B_overlap_supported",
                    "shared_type_B_overlap_supported",
                }
            )

            rows.append({
                "test_id": test_id,
                "test_label": test.get("label", test_id),
                "pair_set_id": pair_set_id,
                "features_used": ",".join(keep_features),
                "normalization": normalization,
                "weights_mode": "from_source_run" if weights_spec == "from_source_run" else "custom",
                "mean_overlap_distance": mean_score,
                "strong_overlap_count": strong_count,
                "partial_overlap_count": partial_count,
                "weak_overlap_count": weak_count,
                "no_overlap_count": no_count,
                "baseline_group_status": baseline_status,
                "recomputed_group_status": recomputed_group_status,
                "improved_vs_baseline": improved,
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Global diagnosis
# ---------------------------------------------------------------------

def build_global_diagnosis(
    pair_set_diag_df: pd.DataFrame,
    sens_df: pd.DataFrame,
    group_summary_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    baseline_global_status = "no_meaningful_model_overlap"
    if len(group_summary_df):
        if any(group_summary_df["group_overlap_status"] == "shared_type_B_overlap_supported"):
            baseline_global_status = "shared_type_B_overlap_supported"
        elif any(group_summary_df["group_overlap_status"] == "shared_quantitative_type_B_overlap_supported"):
            baseline_global_status = "shared_quantitative_type_B_overlap_supported"
        elif all(group_summary_df["group_overlap_status"] == "no_meaningful_model_overlap"):
            baseline_global_status = "no_meaningful_model_overlap"
        else:
            baseline_global_status = "mixed_overlap_baseline"

    # contribution pattern baseline
    patterns = pair_set_diag_df["distribution_pattern"].tolist() if len(pair_set_diag_df) else []
    has_single = "single_feature_dominates_distance" in patterns
    has_two = "two_feature_cluster_dominates_distance" in patterns
    has_broad = "distance_broadly_distributed" in patterns

    # sensitivity
    def test_improves(test_id: str) -> bool:
        sub = sens_df[sens_df["test_id"] == test_id]
        return bool(len(sub) and sub["improved_vs_baseline"].any())

    equal_weights_improves = test_improves("equal_weights")
    zscore_improves = test_improves("zscore_like_rescale")
    local_range_improves = test_improves("local_range_norm")

    def keeps_no_meaningful(test_id: str) -> bool:
        sub = sens_df[sens_df["test_id"] == test_id]
        if len(sub) == 0:
            return False
        return all(sub["recomputed_group_status"] == "no_meaningful_model_overlap")

    no_rigidity_keeps = keeps_no_meaningful("no_rigidity")
    no_grid_keeps = keeps_no_meaningful("no_grid_deviation")
    no_both_keeps = keeps_no_meaningful("no_rigidity_no_grid")

    any_alt_partial_or_better = bool(
        len(sens_df) and sens_df["recomputed_group_status"].isin(
            {"shared_quantitative_type_B_overlap_supported", "shared_type_B_overlap_supported"}
        ).any()
    )

    no_alt_partial_or_better = not any_alt_partial_or_better

    weighting_and_normalization_tests_disagree = bool(
        (equal_weights_improves and not (zscore_improves or local_range_improves))
        or ((zscore_improves or local_range_improves) and not equal_weights_improves)
    )

    overlap_stable_under_ablation = (
        baseline_global_status == "no_meaningful_model_overlap"
        and no_rigidity_keeps
        and no_grid_keeps
        and no_both_keeps
    )

    no_overlap_remains_robust = (
        baseline_global_status == "no_meaningful_model_overlap"
        and overlap_stable_under_ablation
        and no_alt_partial_or_better
    )

    # choose dominant diagnostic status
    if no_overlap_remains_robust:
        global_status = "no_overlap_remains_robust"
    elif equal_weights_improves:
        global_status = "overlap_sensitive_to_weighting"
    elif zscore_improves or local_range_improves:
        global_status = "overlap_sensitive_to_normalization"
    elif overlap_stable_under_ablation:
        global_status = "overlap_stable_under_ablation"
    elif has_single:
        global_status = "single_feature_dominates_distance"
    elif has_two:
        global_status = "two_feature_cluster_dominates_distance"
    elif has_broad:
        global_status = "distance_broadly_distributed"
    else:
        global_status = "mixed_diagnostic_result"

    return {
        "run_id": cfg["run"]["run_id"],
        "source_run_id": cfg["inputs"]["source_run_id"],
        "baseline_global_status": baseline_global_status,
        "n_pair_set_rows": int(len(pair_set_diag_df)),
        "n_sensitivity_rows": int(len(sens_df)),
        "global_diagnostic_status": global_status,
        "has_single_feature_dominance": has_single,
        "has_two_feature_cluster_dominance": has_two,
        "has_broad_distribution": has_broad,
        "equal_weights_improves_overlap_status": equal_weights_improves,
        "zscore_like_rescale_improves_overlap_status": zscore_improves,
        "local_range_norm_improves_overlap_status": local_range_improves,
        "no_rigidity_keeps_no_meaningful_model_overlap": no_rigidity_keeps,
        "no_grid_deviation_keeps_no_meaningful_model_overlap": no_grid_keeps,
        "no_rigidity_no_grid_keeps_no_meaningful_model_overlap": no_both_keeps,
        "overlap_stable_under_ablation": overlap_stable_under_ablation,
        "no_alternative_test_reaches_partial_or_better": no_alt_partial_or_better,
        "weighting_and_normalization_tests_disagree": weighting_and_normalization_tests_disagree,
        "no_overlap_remains_robust": no_overlap_remains_robust,
    }


# ---------------------------------------------------------------------
# Plot data helpers
# ---------------------------------------------------------------------

def build_plotdata_feature_contribution(contribution_df: pd.DataFrame) -> pd.DataFrame:
    return (
        contribution_df.groupby(["pair_set_id", "feature_name"], as_index=False)
        .agg(
            mean_relative_contribution=("relative_contribution", "mean"),
            mean_weighted_difference=("weighted_difference", "mean"),
        )
        .sort_values(["pair_set_id", "mean_relative_contribution"], ascending=[True, False])
        .reset_index(drop=True)
    )


def build_plotdata_heatmap(contribution_df: pd.DataFrame) -> pd.DataFrame:
    return (
        contribution_df.groupby(
            ["pair_set_id", "fsw_regime_id", "ao_regime_id", "feature_name"],
            as_index=False,
        )
        .agg(
            relative_contribution=("relative_contribution", "mean"),
            weighted_difference=("weighted_difference", "mean"),
        )
        .reset_index(drop=True)
    )


def build_plotdata_sensitivity(sens_df: pd.DataFrame) -> pd.DataFrame:
    return sens_df.copy()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config_m39x3ea_feature_distance_diagnosis.yaml")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    outdir = ensure_dir(cfg["run"]["outdir"])

    pair_feature_src = pd.read_csv(cfg["inputs"]["pair_feature_comparison_csv"])
    pair_summary_src = pd.read_csv(cfg["inputs"]["pair_overlap_summary_csv"])
    group_summary_src = pd.read_csv(cfg["inputs"]["group_overlap_summary_csv"])

    pair_feature_src = parse_weighted_difference_source(pair_feature_src)
    pair_summary_src = parse_pair_summary_source(pair_summary_src)
    group_summary_src = parse_group_summary_source(group_summary_src)

    target_pair_sets = cfg["feature_distance_diagnosis"]["target_pair_sets"]

    # limit to target pair sets
    pair_feature_src = pair_feature_src[pair_feature_src["pair_set_id"].isin(target_pair_sets)].copy()
    pair_summary_src = pair_summary_src[pair_summary_src["pair_set_id"].isin(target_pair_sets)].copy()
    group_summary_src = group_summary_src[group_summary_src["pair_set_id"].isin(target_pair_sets)].copy()

    # baseline contribution analysis
    contribution_df = build_pair_feature_contribution(pair_feature_src, cfg)

    # pair-set feature diagnosis
    pair_set_diag_df = build_pair_set_feature_diagnosis(contribution_df, target_pair_sets, cfg)

    # sensitivity recomputation
    sens_df = recompute_sensitivity(pair_feature_src, pair_summary_src, group_summary_src, cfg)

    # global diagnosis
    global_summary = build_global_diagnosis(pair_set_diag_df, sens_df, group_summary_src, cfg)

    # plotdata
    feature_plot_df = build_plotdata_feature_contribution(contribution_df)
    heatmap_plot_df = build_plotdata_heatmap(contribution_df)
    sens_plot_df = build_plotdata_sensitivity(sens_df)

    # outputs
    contribution_df.to_csv(outdir / cfg["outputs"]["pair_feature_contribution_csv"], index=False)
    pair_set_diag_df.to_csv(outdir / cfg["outputs"]["pair_set_feature_diagnosis_csv"], index=False)
    sens_df.to_csv(outdir / cfg["outputs"]["sensitivity_summary_csv"], index=False)
    feature_plot_df.to_csv(outdir / cfg["outputs"]["feature_contribution_plotdata_csv"], index=False)
    heatmap_plot_df.to_csv(outdir / cfg["outputs"]["pairset_heatmap_plotdata_csv"], index=False)
    sens_plot_df.to_csv(outdir / cfg["outputs"]["sensitivity_plotdata_csv"], index=False)
    write_json(global_summary, outdir / cfg["outputs"]["global_summary_json"])

    report_lines = [
        f"# {cfg['run']['run_id']}",
        "",
        "## 1. Zweck",
        cfg["run"]["description"],
        "",
        "## 2. Globales Diagnoseurteil",
        "```json",
        json.dumps(global_summary, indent=2, ensure_ascii=False),
        "```",
        "",
        "## 3. Pair-Set-Feature-Diagnose",
        pair_set_diag_df.to_markdown(index=False) if len(pair_set_diag_df) else "_keine Daten_",
        "",
        "## 4. Sensitivität",
        sens_df.to_markdown(index=False) if len(sens_df) else "_keine Daten_",
        "",
    ]
    write_markdown("\n".join(report_lines), outdir / cfg["outputs"]["markdown_report"])

    source_notes = "\n".join([
        "# Source Notes",
        "",
        f"- Source run: {cfg['inputs']['source_run_id']}",
        f"- Pair feature source: {cfg['inputs']['pair_feature_comparison_csv']}",
        f"- Pair summary source: {cfg['inputs']['pair_overlap_summary_csv']}",
        f"- Group summary source: {cfg['inputs']['group_overlap_summary_csv']}",
        "- Baseline contribution uses weighted feature distances from M39x3e.",
        "- Sensitivity tests recompute overlap distances under ablation, reweighting, and alternative normalization.",
        "",
    ])
    write_markdown(source_notes, outdir / cfg["outputs"]["source_notes_md"])

    print(f"[OK] Run completed: {cfg['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()