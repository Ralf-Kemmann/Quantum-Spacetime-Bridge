#!/usr/bin/env python3
"""
m39x3e_model_overlap_test_runner.py

M.3.9x.3e — Modell-Überlappungstest FSW ↔ AO

Ziel:
- Transition-Mapping-Ergebnisse aus M39x3d laden
- ausgewählte FSW- und AO-Regime in einem gemeinsamen Merkmalsraum vergleichen
- paarweise Überlappungsscores berechnen
- Gruppenurteile und globales Modell-Überlappungsurteil ableiten
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

def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    s = str(value).strip().lower()
    return s in {"true", "1", "yes", "y"}


def get_threshold(cfg: Dict[str, Any], name: str) -> float:
    return float(cfg["overlap_distance_logic"]["pair_overlap_thresholds"][name])


def feature_judgement(norm_diff: float, cfg: Dict[str, Any]) -> str:
    thr = cfg["overlap_distance_logic"]["feature_overlap_thresholds"]
    near_max = float(thr["near_max"])
    moderate_max = float(thr["moderate_max"])

    if norm_diff <= near_max:
        return "near"
    if norm_diff <= moderate_max:
        return "moderate"
    return "far"


def pair_overlap_status(score: float, cfg: Dict[str, Any]) -> str:
    thr = cfg["overlap_distance_logic"]["pair_overlap_thresholds"]
    strong_max = float(thr["strong_overlap_max"])
    partial_max = float(thr["partial_overlap_max"])
    weak_max = float(thr["weak_overlap_max"])

    if score <= strong_max:
        return "strong_overlap"
    if score <= partial_max:
        return "partial_overlap"
    if score <= weak_max:
        return "weak_overlap"
    return "no_meaningful_overlap"


def pair_overlap_note(
    status: str,
    dominant_match: bool,
    irr_match: bool,
) -> str:
    if status == "strong_overlap":
        return "Strong shared Type-B overlap."
    if status == "partial_overlap":
        if dominant_match:
            return "Partial overlap with compatible dominant marker."
        return "Partial overlap despite some categorical mismatch."
    if status == "weak_overlap":
        if irr_match:
            return "Weak overlap with limited structural compatibility."
        return "Weak overlap only."
    return "No meaningful overlap in the shared feature space."


def group_overlap_status(
    mean_score: float,
    pair_set_id: str,
    strong_count: int,
    partial_count: int,
    cfg: Dict[str, Any],
) -> str:
    strong_max = get_threshold(cfg, "strong_overlap_max")
    partial_max = get_threshold(cfg, "partial_overlap_max")
    weak_max = get_threshold(cfg, "weak_overlap_max")

    if pair_set_id == "FSW_CORE_VS_AO_TRANSFER":
        if mean_score <= strong_max and strong_count >= 2:
            return "shared_type_B_overlap_supported"
        if mean_score <= partial_max and partial_count >= 2:
            return "shared_quantitative_type_B_overlap_supported"
        if mean_score <= weak_max:
            return "weak_model_overlap_only"
        return "no_meaningful_model_overlap"

    if pair_set_id == "FSW_CORE_VS_AO_PREJUMP":
        if mean_score <= partial_max:
            return "boundary_or_partial_overlap"
        if mean_score <= weak_max:
            return "weak_model_overlap_only"
        return "no_meaningful_model_overlap"

    if pair_set_id == "FSW_CORE_VS_AO_JUMP":
        if mean_score > partial_max:
            return "ao_qualitative_extension_beyond_shared_overlap"
        if mean_score <= weak_max:
            return "weak_model_overlap_only"
        return "no_meaningful_model_overlap"

    if mean_score <= partial_max:
        return "shared_quantitative_type_B_overlap_supported"
    if mean_score <= weak_max:
        return "weak_model_overlap_only"
    return "no_meaningful_model_overlap"


def group_overlap_note(status: str) -> str:
    notes = {
        "shared_type_B_overlap_supported": "Robust shared overlap between FSW core and AO transfer regimes.",
        "shared_quantitative_type_B_overlap_supported": "Shared quantitative Type-B overlap is supported.",
        "ao_qualitative_extension_beyond_shared_overlap": "AO jump core extends beyond the shared FSW/AO overlap.",
        "boundary_or_partial_overlap": "Boundary region with partial overlap only.",
        "weak_model_overlap_only": "Only weak overlap is visible.",
        "no_meaningful_model_overlap": "No meaningful overlap in the tested pair set.",
    }
    return notes.get(status, status)


# ---------------------------------------------------------------------
# Core loading / extraction
# ---------------------------------------------------------------------

def load_transition_summary(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = [
        "family_id",
        "variant_id",
        "dominant_marker",
        "delta_p2_relative_gain_vs_type_A",
        "distance_to_type_D",
        "observed_irregularity_level",
        "spacing_cv",
        "grid_deviation_score",
        "simple_rigidity_surrogate",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Transition summary missing columns: {missing}")
    return df


def load_selected_regimes(families_cfg: Dict[str, Any]) -> Dict[str, Dict[str, Dict[str, Any]]]:
    out: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for fam in families_cfg.get("families", []):
        family_id = fam["family_id"]
        out[family_id] = {}
        for reg in fam.get("selected_overlap_regimes", []):
            out[family_id][reg["regime_id"]] = reg

    return out


def build_feature_ranges(
    source_df: pd.DataFrame,
    numeric_features: List[str],
    epsilon: float,
) -> Dict[str, Tuple[float, float]]:
    ranges: Dict[str, Tuple[float, float]] = {}
    for feat in numeric_features:
        mn = float(source_df[feat].min())
        mx = float(source_df[feat].max())
        if np.isclose(mx - mn, 0.0):
            mx = mn + epsilon
        ranges[feat] = (mn, mx)
    return ranges


def normalize_difference(
    feat: str,
    a: float,
    b: float,
    ranges: Dict[str, Tuple[float, float]],
) -> float:
    mn, mx = ranges[feat]
    denom = mx - mn
    if np.isclose(denom, 0.0):
        return 0.0
    return abs(a - b) / denom


# ---------------------------------------------------------------------
# Pairwise comparison
# ---------------------------------------------------------------------

def build_group_rows(
    source_df: pd.DataFrame,
    family_id: str,
    regime_ids: List[str],
) -> pd.DataFrame:
    sub = source_df[
        (source_df["family_id"] == family_id) &
        (source_df["variant_id"].isin(regime_ids))
    ].copy()
    return sub.reset_index(drop=True)


def compare_pair(
    fsw_row: pd.Series,
    ao_row: pd.Series,
    pair_set_id: str,
    cfg: Dict[str, Any],
    ranges: Dict[str, Tuple[float, float]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    logic = cfg["overlap_distance_logic"]
    num_features = cfg["model_overlap_test"]["comparison_space"]["numeric_features"]
    num_weights = logic["numeric_feature_weights"]
    cat_pen = logic["categorical_penalties"]

    feature_rows: List[Dict[str, Any]] = []
    weighted_diffs: List[float] = []
    norm_diffs: List[float] = []

    for feat in num_features:
        fsw_val = float(fsw_row[feat])
        ao_val = float(ao_row[feat])
        raw_diff = ao_val - fsw_val
        abs_diff = abs(raw_diff)
        norm_diff = normalize_difference(feat, fsw_val, ao_val, ranges)
        weight = float(num_weights[feat])
        weighted_diff = norm_diff * weight
        weighted_diffs.append(weighted_diff)
        norm_diffs.append(norm_diff)

        feature_rows.append({
            "pair_set_id": pair_set_id,
            "fsw_regime_id": fsw_row["variant_id"],
            "ao_regime_id": ao_row["variant_id"],
            "feature_name": feat,
            "fsw_value": fsw_val,
            "ao_value": ao_val,
            "raw_difference": raw_diff,
            "abs_difference": abs_diff,
            "normalized_difference": norm_diff,
            "feature_weight": weight,
            "weighted_difference": weighted_diff,
            "feature_overlap_judgement": feature_judgement(norm_diff, cfg),
        })

    dom_match = str(fsw_row["dominant_marker"]) == str(ao_row["dominant_marker"])
    irr_match = str(fsw_row["observed_irregularity_level"]) == str(ao_row["observed_irregularity_level"])

    categorical_penalty = 0.0
    if not dom_match:
        categorical_penalty += float(cat_pen["dominant_marker_mismatch"])
    if not irr_match:
        categorical_penalty += float(cat_pen["irregularity_level_mismatch"])

    mean_norm = float(np.mean(norm_diffs)) if norm_diffs else 0.0
    weighted_score = float(np.sum(weighted_diffs) + categorical_penalty)
    status = pair_overlap_status(weighted_score, cfg)

    pair_row = {
        "pair_set_id": pair_set_id,
        "fsw_regime_id": fsw_row["variant_id"],
        "ao_regime_id": ao_row["variant_id"],
        "dominant_marker_fsw": fsw_row["dominant_marker"],
        "dominant_marker_ao": ao_row["dominant_marker"],
        "dominant_marker_match_flag": dom_match,
        "irregularity_level_fsw": fsw_row["observed_irregularity_level"],
        "irregularity_level_ao": ao_row["observed_irregularity_level"],
        "irregularity_level_match_flag": irr_match,
        "mean_normalized_difference": mean_norm,
        "weighted_overlap_distance_score": weighted_score,
        "overlap_status": status,
        "overlap_note": pair_overlap_note(status, dom_match, irr_match),
    }

    return feature_rows, pair_row


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config_m39x3e_model_overlap_test.yaml")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    families_cfg = load_yaml(cfg["inputs"]["family_definitions_yaml"])

    outdir = ensure_dir(cfg["run"]["outdir"])

    source_csv = cfg["inputs"]["source_transition_summary_csv"]
    source_df = load_transition_summary(source_csv)

    selected = load_selected_regimes(families_cfg)
    numeric_features = cfg["model_overlap_test"]["comparison_space"]["numeric_features"]
    epsilon = float(cfg["overlap_distance_logic"]["normalization"].get("epsilon", 1.0e-12))
    ranges = build_feature_ranges(source_df, numeric_features, epsilon)

    pair_feature_rows: List[Dict[str, Any]] = []
    pair_summary_rows: List[Dict[str, Any]] = []
    group_summary_rows: List[Dict[str, Any]] = []

    ref_groups = cfg["model_overlap_test"]["reference_groups"]
    pair_sets = cfg["model_overlap_test"]["pair_sets"]

    for pair_set in pair_sets:
        pair_set_id = pair_set["pair_set_id"]

        fsw_group_name = pair_set["fsw_group"]
        ao_group_name = pair_set["ao_group"]

        fsw_group_cfg = ref_groups[fsw_group_name]
        ao_group_cfg = ref_groups[ao_group_name]

        fsw_family_id = fsw_group_cfg["family_id"]
        ao_family_id = ao_group_cfg["family_id"]

        fsw_regimes = fsw_group_cfg["regime_ids"]
        ao_regimes = ao_group_cfg["regime_ids"]

        fsw_df = build_group_rows(source_df, fsw_family_id, fsw_regimes)
        ao_df = build_group_rows(source_df, ao_family_id, ao_regimes)

        if len(fsw_df) == 0:
            raise ValueError(f"No source rows found for FSW group {fsw_group_name}: {fsw_regimes}")
        if len(ao_df) == 0:
            raise ValueError(f"No source rows found for AO group {ao_group_name}: {ao_regimes}")

        local_pair_rows: List[Dict[str, Any]] = []

        for _, fsw_row in fsw_df.iterrows():
            for _, ao_row in ao_df.iterrows():
                feat_rows, pair_row = compare_pair(fsw_row, ao_row, pair_set_id, cfg, ranges)
                pair_feature_rows.extend(feat_rows)
                pair_summary_rows.append(pair_row)
                local_pair_rows.append(pair_row)

        local_df = pd.DataFrame(local_pair_rows)

        mean_overlap_distance = float(local_df["weighted_overlap_distance_score"].mean())
        min_overlap_distance = float(local_df["weighted_overlap_distance_score"].min())
        max_overlap_distance = float(local_df["weighted_overlap_distance_score"].max())

        strong_count = int((local_df["overlap_status"] == "strong_overlap").sum())
        partial_count = int((local_df["overlap_status"] == "partial_overlap").sum())
        weak_count = int((local_df["overlap_status"] == "weak_overlap").sum())
        no_overlap_count = int((local_df["overlap_status"] == "no_meaningful_overlap").sum())

        group_status = group_overlap_status(
            mean_overlap_distance,
            pair_set_id,
            strong_count,
            partial_count,
            cfg,
        )

        group_summary_rows.append({
            "pair_set_id": pair_set_id,
            "n_pairs": int(len(local_df)),
            "mean_overlap_distance": mean_overlap_distance,
            "min_overlap_distance": min_overlap_distance,
            "max_overlap_distance": max_overlap_distance,
            "strong_overlap_count": strong_count,
            "partial_overlap_count": partial_count,
            "weak_overlap_count": weak_count,
            "no_overlap_count": no_overlap_count,
            "group_overlap_status": group_status,
            "group_overlap_note": group_overlap_note(group_status),
        })

    pair_feature_df = pd.DataFrame(pair_feature_rows)
    pair_summary_df = pd.DataFrame(pair_summary_rows)
    group_summary_df = pd.DataFrame(group_summary_rows)

    # -----------------------------------------------------------------
    # Global decision
    # -----------------------------------------------------------------
    group_map = {
        row["pair_set_id"]: row
        for _, row in group_summary_df.iterrows()
    }

    transfer_group = group_map.get("FSW_CORE_VS_AO_TRANSFER")
    prejump_group = group_map.get("FSW_CORE_VS_AO_PREJUMP")
    jump_group = group_map.get("FSW_CORE_VS_AO_JUMP")

    strong_max = get_threshold(cfg, "strong_overlap_max")
    partial_max = get_threshold(cfg, "partial_overlap_max")
    weak_max = get_threshold(cfg, "weak_overlap_max")

    if (
        transfer_group is not None
        and float(transfer_group["mean_overlap_distance"]) <= strong_max
        and int(transfer_group["strong_overlap_count"]) >= 2
    ):
        global_status = "shared_type_B_overlap_supported"
    elif (
        transfer_group is not None
        and float(transfer_group["mean_overlap_distance"]) <= partial_max
        and int(transfer_group["partial_overlap_count"]) >= 2
    ):
        if jump_group is not None and float(jump_group["mean_overlap_distance"]) > partial_max:
            global_status = "ao_qualitative_extension_beyond_shared_overlap"
        else:
            global_status = "shared_quantitative_type_B_overlap_supported"
    elif (
        transfer_group is not None
        and float(transfer_group["mean_overlap_distance"]) <= weak_max
    ):
        global_status = "weak_model_overlap_only"
    else:
        global_status = "no_meaningful_model_overlap"

    all_weak_or_worse = bool(
        len(group_summary_df) > 0 and
        all(
            s in {"weak_model_overlap_only", "no_meaningful_model_overlap", "boundary_or_partial_overlap"}
            for s in group_summary_df["group_overlap_status"].tolist()
        )
    )

    global_summary = {
        "run_id": cfg["run"]["run_id"],
        "source_run_id": cfg["inputs"]["source_run_id"],
        "n_pair_feature_rows": int(len(pair_feature_df)),
        "n_pair_rows": int(len(pair_summary_df)),
        "n_group_rows": int(len(group_summary_df)),
        "global_overlap_status": global_status,
        "transfer_mean_overlap_distance": float(transfer_group["mean_overlap_distance"]) if transfer_group is not None else None,
        "prejump_mean_overlap_distance": float(prejump_group["mean_overlap_distance"]) if prejump_group is not None else None,
        "jump_mean_overlap_distance": float(jump_group["mean_overlap_distance"]) if jump_group is not None else None,
        "all_pair_sets_have_only_weak_or_worse_overlap": all_weak_or_worse,
    }

    # -----------------------------------------------------------------
    # Outputs
    # -----------------------------------------------------------------
    pair_feature_df.to_csv(outdir / cfg["outputs"]["pair_feature_comparison_csv"], index=False)
    pair_summary_df.to_csv(outdir / cfg["outputs"]["pair_overlap_summary_csv"], index=False)
    group_summary_df.to_csv(outdir / cfg["outputs"]["group_overlap_summary_csv"], index=False)
    write_json(global_summary, outdir / cfg["outputs"]["global_summary_json"])

    report_lines = [
        f"# {cfg['run']['run_id']}",
        "",
        "## 1. Zweck",
        cfg["run"]["description"],
        "",
        "## 2. Globales Urteil",
        "```json",
        json.dumps(global_summary, indent=2, ensure_ascii=False),
        "```",
        "",
        "## 3. Gruppenübersicht",
        group_summary_df.to_markdown(index=False) if len(group_summary_df) else "_keine Daten_",
        "",
        "## 4. Paarübersicht",
        pair_summary_df.to_markdown(index=False) if len(pair_summary_df) else "_keine Daten_",
        "",
    ]
    write_markdown("\n".join(report_lines), outdir / cfg["outputs"]["markdown_report"])

    source_notes = "\n".join([
        "# Source Notes",
        "",
        f"- Source run: {cfg['inputs']['source_run_id']}",
        f"- Source transition summary: {cfg['inputs']['source_transition_summary_csv']}",
        "- Comparison is performed in a shared Type-B feature space.",
        "- Numeric distances are range-normalized from the source run.",
        "- Categorical mismatches contribute additive penalties.",
        "",
    ])
    write_markdown(source_notes, outdir / cfg["outputs"]["source_notes_md"])

    print(f"[OK] Run completed: {cfg['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()