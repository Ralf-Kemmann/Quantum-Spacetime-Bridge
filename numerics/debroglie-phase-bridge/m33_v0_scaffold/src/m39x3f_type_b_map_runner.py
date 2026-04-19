#!/usr/bin/env python3
"""
m39x3f_type_b_map_runner.py

M.3.9x.3f — Typ-B-Karte / Zwei-Pfade-Hypothese

Ziel:
- FSW- und AO-Pfad aus M39x3d kartieren
- Ergebnisse aus M39x3e und M39x3ea integrieren
- Annäherungs- und Trennzonen markieren
- die Zwei-Pfade-Hypothese als Karten-/Pfadbefund auswerten
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

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

def get_path_cfg(cfg: Dict[str, Any], path_id: str) -> Dict[str, Any]:
    for item in cfg["paths"]:
        if item["path_id"] == path_id:
            return item
    raise KeyError(f"Unknown path_id: {path_id}")


def find_segment_for_regime(seg_cfg: Dict[str, Any], regime_id: str) -> Dict[str, Any]:
    for seg in seg_cfg:
        if regime_id in seg["regime_ids"]:
            return seg
    return {
        "segment_id": "UNASSIGNED",
        "interpretation": "unassigned",
    }


def safe_bool(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def get_pair_group_status(group_df: pd.DataFrame, pair_set_id: str) -> Optional[str]:
    sub = group_df[group_df["pair_set_id"] == pair_set_id]
    if len(sub) == 0:
        return None
    return str(sub.iloc[0]["group_overlap_status"])


def get_pairset_diag(pairset_diag_df: pd.DataFrame, pair_set_id: str) -> Optional[pd.Series]:
    sub = pairset_diag_df[pairset_diag_df["pair_set_id"] == pair_set_id]
    if len(sub) == 0:
        return None
    return sub.iloc[0]


def get_transfer_focus_rows(df: pd.DataFrame, cfg: Dict[str, Any], path_id: str) -> pd.DataFrame:
    focus_key = "fsw_focus_regimes" if path_id == "FSW_PATH" else "ao_focus_regimes"
    focus_regimes = cfg["map_axes"]["transfer_map"][focus_key]
    return df[df["variant_id"].isin(focus_regimes)].copy()


def euclidean_2d(a_x: float, a_y: float, b_x: float, b_y: float) -> float:
    return float(np.sqrt((a_x - b_x) ** 2 + (a_y - b_y) ** 2))


# ---------------------------------------------------------------------
# Build point summary
# ---------------------------------------------------------------------

def build_path_point_summary(
    transition_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for path in cfg["paths"]:
        path_id = path["path_id"]
        family_id = path["family_id"]
        path_role = path["path_role"]
        regime_ids = path["regime_ids"]
        seg_cfg = cfg["path_segmentation"][path_id]

        sub = transition_df[
            (transition_df["family_id"] == family_id) &
            (transition_df["variant_id"].isin(regime_ids))
        ].copy()

        if len(sub) == 0:
            continue

        sort_col = "regime_parameter"
        ascending = True if path_id == "AO_PATH" else False
        sub = sub.sort_values(sort_col, ascending=ascending).reset_index(drop=True)

        for idx, (_, row) in enumerate(sub.iterrows(), start=1):
            seg = find_segment_for_regime(seg_cfg, str(row["variant_id"]))
            rows.append({
                "path_id": path_id,
                "path_role": path_role,
                "path_order_index": idx,
                "family_id": row["family_id"],
                "variant_id": row["variant_id"],
                "regime_parameter": float(row["regime_parameter"]),
                "segment_id": seg["segment_id"],
                "segment_interpretation": seg["interpretation"],
                "dominant_marker": row["dominant_marker"],
                "delta_p2_relative_gain_vs_type_A": float(row["delta_p2_relative_gain_vs_type_A"]),
                "distance_to_type_D": float(row["distance_to_type_D"]),
                "observed_irregularity_level": row["observed_irregularity_level"],
                "spacing_cv": float(row["spacing_cv"]),
                "grid_deviation_score": float(row["grid_deviation_score"]),
                "simple_rigidity_surrogate": float(row["simple_rigidity_surrogate"]),
                "second_difference_curvature": float(row.get("second_difference_curvature", 0.0)),
                "prediction_match_status": row.get("prediction_match_status", ""),
                "window_or_jump_membership": row.get("window_or_jump_membership", ""),
                "regime_assignment": row.get("regime_assignment", ""),
                "local_transition_flag": safe_bool(row.get("local_transition_flag", False)),
                "knee_candidate_flag": safe_bool(row.get("knee_candidate_flag", False)),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Build segment summary
# ---------------------------------------------------------------------

def build_path_segment_summary(
    point_df: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    if len(point_df) == 0:
        return pd.DataFrame()

    for (path_id, segment_id, segment_interpretation), sub in point_df.groupby(
        ["path_id", "segment_id", "segment_interpretation"], sort=False
    ):
        rows.append({
            "path_id": path_id,
            "segment_id": segment_id,
            "segment_interpretation": segment_interpretation,
            "n_points": int(len(sub)),
            "regime_ids": ",".join(sub["variant_id"].tolist()),
            "mean_delta_p2_relative_gain_vs_type_A": float(sub["delta_p2_relative_gain_vs_type_A"].mean()),
            "mean_distance_to_type_D": float(sub["distance_to_type_D"].mean()),
            "mean_spacing_cv": float(sub["spacing_cv"].mean()),
            "mean_grid_deviation_score": float(sub["grid_deviation_score"].mean()),
            "mean_simple_rigidity_surrogate": float(sub["simple_rigidity_surrogate"].mean()),
            "dominant_regime_assignment": (
                sub["regime_assignment"].mode().iloc[0] if len(sub["regime_assignment"].mode()) else ""
            ),
            "has_local_transition_flag": bool(sub["local_transition_flag"].any()),
            "has_knee_candidate_flag": bool(sub["knee_candidate_flag"].any()),
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Path relation summary
# ---------------------------------------------------------------------

def build_path_relation_summary(
    point_df: pd.DataFrame,
    pair_group_df: pd.DataFrame,
    pairset_diag_df: pd.DataFrame,
    sens_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    fsw_focus = get_transfer_focus_rows(point_df, cfg, "FSW_PATH")
    ao_focus = get_transfer_focus_rows(point_df, cfg, "AO_PATH")

    approach_thr = float(cfg["path_relation_logic"]["approach_zone"]["transfer_map_distance_threshold"])
    separation_thr = float(cfg["path_relation_logic"]["separation_zone"]["transfer_map_distance_threshold"])

    transfer_pairs = []
    for _, frow in fsw_focus.iterrows():
        for _, arow in ao_focus.iterrows():
            dist = euclidean_2d(
                float(frow["distance_to_type_D"]),
                float(frow["spacing_cv"]),
                float(arow["distance_to_type_D"]),
                float(arow["spacing_cv"]),
            )
            transfer_pairs.append({
                "relation_type": "transfer_map_pair",
                "fsw_regime_id": frow["variant_id"],
                "ao_regime_id": arow["variant_id"],
                "map_distance": dist,
                "approach_zone_flag": dist <= approach_thr,
                "separation_zone_flag": dist >= separation_thr,
                "map_relation_note": (
                    "approach_zone" if dist <= approach_thr
                    else "separation_zone" if dist >= separation_thr
                    else "intermediate_distance"
                ),
            })

    transfer_pair_df = pd.DataFrame(transfer_pairs)

    # Structural AO transition
    ao_all = point_df[point_df["path_id"] == "AO_PATH"].copy().sort_values("regime_parameter", ascending=True)
    ao_transition_visible = False
    ao_transition_regime = None
    rig_jump_min = float(cfg["path_relation_logic"]["structural_transition_flag"]["rigidity_jump_min"])
    grid_jump_min = float(cfg["path_relation_logic"]["structural_transition_flag"]["grid_deviation_jump_min"])

    prev_row = None
    for _, row in ao_all.iterrows():
        if prev_row is not None:
            rig_jump = float(row["simple_rigidity_surrogate"]) - float(prev_row["simple_rigidity_surrogate"])
            grid_jump = float(row["grid_deviation_score"]) - float(prev_row["grid_deviation_score"])
            if rig_jump >= rig_jump_min or grid_jump >= grid_jump_min:
                ao_transition_visible = True
                ao_transition_regime = str(row["variant_id"])
                rows.append({
                    "relation_type": "ao_structural_transition",
                    "fsw_regime_id": "",
                    "ao_regime_id": str(row["variant_id"]),
                    "map_distance": np.nan,
                    "approach_zone_flag": False,
                    "separation_zone_flag": False,
                    "map_relation_note": f"structural_transition_detected_at_{row['variant_id']}",
                })
                break
        prev_row = row

    # Quantitative FSW corridor
    fsw_all = point_df[point_df["path_id"] == "FSW_PATH"].copy().sort_values("regime_parameter", ascending=False)
    fsw_quant_corridor_visible = False
    fsw_corridor_note = "not_detected"
    if len(fsw_all) >= 2:
        core = fsw_all[fsw_all["segment_id"] == "FSW_CORE"]
        if len(core) >= 2:
            fsw_quant_corridor_visible = True
            fsw_corridor_note = "core_plateau_visible"

    rows.extend(transfer_pairs)
    rows.append({
        "relation_type": "fsw_quantitative_corridor",
        "fsw_regime_id": "FSW_CORE",
        "ao_regime_id": "",
        "map_distance": np.nan,
        "approach_zone_flag": False,
        "separation_zone_flag": False,
        "map_relation_note": fsw_corridor_note,
    })

    # Integrate previous diagnostics
    transfer_group_status = get_pair_group_status(pair_group_df, "FSW_CORE_VS_AO_TRANSFER")
    prejump_group_status = get_pair_group_status(pair_group_df, "FSW_CORE_VS_AO_PREJUMP")
    jump_group_status = get_pair_group_status(pair_group_df, "FSW_CORE_VS_AO_JUMP")

    transfer_diag = get_pairset_diag(pairset_diag_df, "FSW_CORE_VS_AO_TRANSFER")
    prejump_diag = get_pairset_diag(pairset_diag_df, "FSW_CORE_VS_AO_PREJUMP")
    jump_diag = get_pairset_diag(pairset_diag_df, "FSW_CORE_VS_AO_JUMP")

    distance_diagnosis_supports_related_paths = False
    if transfer_diag is not None:
        dominant_feat = str(transfer_diag["dominant_distance_feature"])
        second_feat = str(transfer_diag["second_distance_feature"])
        if dominant_feat == "distance_to_type_D" and second_feat == "spacing_cv":
            distance_diagnosis_supports_related_paths = True

    rows.append({
        "relation_type": "diagnostic_integration",
        "fsw_regime_id": "",
        "ao_regime_id": "",
        "map_distance": np.nan,
        "approach_zone_flag": bool(len(transfer_pair_df) and transfer_pair_df["approach_zone_flag"].any()),
        "separation_zone_flag": bool(len(transfer_pair_df) and transfer_pair_df["separation_zone_flag"].any()),
        "map_relation_note": json.dumps({
            "transfer_group_status": transfer_group_status,
            "prejump_group_status": prejump_group_status,
            "jump_group_status": jump_group_status,
            "transfer_pattern": transfer_diag["distribution_pattern"] if transfer_diag is not None else None,
            "prejump_pattern": prejump_diag["distribution_pattern"] if prejump_diag is not None else None,
            "jump_pattern": jump_diag["distribution_pattern"] if jump_diag is not None else None,
            "distance_diagnosis_supports_related_paths": distance_diagnosis_supports_related_paths,
            "ao_transition_visible": ao_transition_visible,
            "ao_transition_regime": ao_transition_regime,
            "fsw_quantitative_corridor_visible": fsw_quant_corridor_visible,
        }, ensure_ascii=False),
    })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Plot data
# ---------------------------------------------------------------------

def build_transfer_map_plotdata(point_df: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
    fsw_focus = cfg["map_axes"]["transfer_map"]["fsw_focus_regimes"]
    ao_focus = cfg["map_axes"]["transfer_map"]["ao_focus_regimes"]
    focus = set(fsw_focus + ao_focus)
    out = point_df[point_df["variant_id"].isin(focus)].copy()
    return out[[
        "path_id",
        "path_role",
        "variant_id",
        "segment_id",
        "regime_parameter",
        "distance_to_type_D",
        "spacing_cv",
        "delta_p2_relative_gain_vs_type_A",
        "grid_deviation_score",
        "simple_rigidity_surrogate",
    ]].reset_index(drop=True)


def build_ao_structure_map_plotdata(point_df: pd.DataFrame) -> pd.DataFrame:
    out = point_df[point_df["path_id"] == "AO_PATH"].copy().sort_values("regime_parameter", ascending=True)
    return out[[
        "path_id",
        "variant_id",
        "segment_id",
        "regime_parameter",
        "simple_rigidity_surrogate",
        "grid_deviation_score",
        "distance_to_type_D",
        "spacing_cv",
        "delta_p2_relative_gain_vs_type_A",
    ]].reset_index(drop=True)


def build_global_type_b_map_plotdata(point_df: pd.DataFrame) -> pd.DataFrame:
    out = point_df.copy()
    return out[[
        "path_id",
        "path_role",
        "variant_id",
        "segment_id",
        "regime_parameter",
        "distance_to_type_D",
        "simple_rigidity_surrogate",
        "spacing_cv",
        "grid_deviation_score",
        "delta_p2_relative_gain_vs_type_A",
    ]].reset_index(drop=True)


# ---------------------------------------------------------------------
# Global decision
# ---------------------------------------------------------------------

def build_global_summary(
    point_df: pd.DataFrame,
    relation_df: pd.DataFrame,
    pair_group_df: pd.DataFrame,
    pairset_diag_df: pd.DataFrame,
    sens_df: pd.DataFrame,
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    fsw_quantitative_corridor_visible = bool(
        len(point_df[(point_df["path_id"] == "FSW_PATH") & (point_df["segment_id"] == "FSW_CORE")]) >= 2
    )

    ao_jump = point_df[(point_df["path_id"] == "AO_PATH") & (point_df["segment_id"] == "AO_JUMP")]
    ao_transition = point_df[(point_df["path_id"] == "AO_PATH") & (point_df["segment_id"] == "AO_TRANSITION")]
    ao_structural_transition_visible = bool(len(ao_jump) >= 1 and len(ao_transition) >= 1)

    transfer_group_status = get_pair_group_status(pair_group_df, "FSW_CORE_VS_AO_TRANSFER")
    no_shared_core_overlap = transfer_group_status in {
        "no_meaningful_model_overlap",
        "weak_model_overlap_only",
    }

    transfer_pairs = relation_df[relation_df["relation_type"] == "transfer_map_pair"]
    at_least_one_transfer_map_approach_zone = bool(
        len(transfer_pairs) and transfer_pairs["approach_zone_flag"].any()
    )

    transfer_diag = get_pairset_diag(pairset_diag_df, "FSW_CORE_VS_AO_TRANSFER")
    distance_diagnosis_supports_related_paths = False
    if transfer_diag is not None:
        distance_diagnosis_supports_related_paths = (
            str(transfer_diag["dominant_distance_feature"]) == "distance_to_type_D"
            and str(transfer_diag["second_distance_feature"]) == "spacing_cv"
        )

    maps_do_not_show_consistent_relation = not (
        fsw_quantitative_corridor_visible and ao_structural_transition_visible
    )

    path_roles_remain_ambiguous = False
    if len(sens_df):
        # only a soft ambiguity flag
        path_roles_remain_ambiguous = False

    if (
        fsw_quantitative_corridor_visible
        and ao_structural_transition_visible
        and distance_diagnosis_supports_related_paths
    ):
        if no_shared_core_overlap:
            global_status = "type_B_paths_related_but_separate"
        else:
            global_status = "type_B_two_path_hypothesis_supported"
    elif no_shared_core_overlap and distance_diagnosis_supports_related_paths:
        global_status = "type_B_no_shared_core_but_structural_relation"
    elif at_least_one_transfer_map_approach_zone:
        global_status = "type_B_annäherungszone_identified"
    else:
        global_status = "type_B_paths_not_yet_coherent"

    return {
        "run_id": cfg["run"]["run_id"],
        "n_path_points": int(len(point_df)),
        "n_path_relations": int(len(relation_df)),
        "global_prediction_status": global_status,
        "FSW_quantitative_corridor_visible": fsw_quantitative_corridor_visible,
        "AO_structural_transition_visible": ao_structural_transition_visible,
        "no_shared_core_overlap": no_shared_core_overlap,
        "at_least_one_transfer_map_approach_zone": at_least_one_transfer_map_approach_zone,
        "distance_diagnosis_supports_related_paths": distance_diagnosis_supports_related_paths,
        "maps_do_not_show_consistent_relation": maps_do_not_show_consistent_relation,
        "path_roles_remain_ambiguous": path_roles_remain_ambiguous,
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config_m39x3f_type_b_map.yaml")
    args = parser.parse_args()

    cfg = load_yaml(args.config)
    outdir = ensure_dir(cfg["run"]["outdir"])

    transition_df = pd.read_csv(cfg["inputs"]["transition_mapping_csv"])
    pair_overlap_df = pd.read_csv(cfg["inputs"]["pair_overlap_summary_csv"])
    group_overlap_df = pd.read_csv(cfg["inputs"]["group_overlap_summary_csv"])
    pairset_diag_df = pd.read_csv(cfg["inputs"]["pair_set_feature_diagnosis_csv"])
    sens_df = pd.read_csv(cfg["inputs"]["sensitivity_summary_csv"])

    point_df = build_path_point_summary(transition_df, cfg)
    segment_df = build_path_segment_summary(point_df)
    relation_df = build_path_relation_summary(
        point_df,
        group_overlap_df,
        pairset_diag_df,
        sens_df,
        cfg,
    )

    transfer_map_df = build_transfer_map_plotdata(point_df, cfg)
    ao_structure_df = build_ao_structure_map_plotdata(point_df)
    global_map_df = build_global_type_b_map_plotdata(point_df)

    global_summary = build_global_summary(
        point_df,
        relation_df,
        group_overlap_df,
        pairset_diag_df,
        sens_df,
        cfg,
    )

    # outputs
    point_df.to_csv(outdir / cfg["outputs"]["path_point_summary_csv"], index=False)
    segment_df.to_csv(outdir / cfg["outputs"]["path_segment_summary_csv"], index=False)
    relation_df.to_csv(outdir / cfg["outputs"]["path_relation_summary_csv"], index=False)
    transfer_map_df.to_csv(outdir / cfg["outputs"]["transfer_map_plotdata_csv"], index=False)
    ao_structure_df.to_csv(outdir / cfg["outputs"]["ao_structure_map_plotdata_csv"], index=False)
    global_map_df.to_csv(outdir / cfg["outputs"]["global_type_b_map_plotdata_csv"], index=False)
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
        "## 3. Path point summary",
        point_df.to_markdown(index=False) if len(point_df) else "_keine Daten_",
        "",
        "## 4. Path segment summary",
        segment_df.to_markdown(index=False) if len(segment_df) else "_keine Daten_",
        "",
        "## 5. Path relation summary",
        relation_df.to_markdown(index=False) if len(relation_df) else "_keine Daten_",
        "",
    ]
    write_markdown("\n".join(report_lines), outdir / cfg["outputs"]["markdown_report"])

    source_notes = "\n".join([
        "# Source Notes",
        "",
        f"- Transition mapping source: {cfg['inputs']['transition_mapping_csv']}",
        f"- Pair overlap source: {cfg['inputs']['pair_overlap_summary_csv']}",
        f"- Group overlap source: {cfg['inputs']['group_overlap_summary_csv']}",
        f"- Distance diagnosis source: {cfg['inputs']['pair_set_feature_diagnosis_csv']}",
        f"- Sensitivity source: {cfg['inputs']['sensitivity_summary_csv']}",
        "- FSW and AO are treated as two mapped paths through Type-B space.",
        "",
    ])
    write_markdown(source_notes, outdir / cfg["outputs"]["source_notes_md"])

    print(f"[OK] Run completed: {cfg['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()