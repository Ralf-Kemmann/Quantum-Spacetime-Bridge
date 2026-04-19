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
class M38bV2Config:
    enabled: bool
    wavepacket_case_grid: Path
    wavepacket_metrics: Path
    dispersion_pair_full: Path
    dispersion_pair_topk: Path
    dispersion_pair_top_summary: Path
    dispersion_class_summary: Path
    dispersion_identity_comparison: Path
    branch_reference_summary: Path
    sigma_branch_scores: Path
    soft_branch_frequency: Path
    reference_modes: List[str]
    top_k_values: List[int]
    class_modes: List[str]
    hard_min_score: float
    hard_min_margin: float
    use_hard: bool
    use_nearest: bool
    use_soft: bool
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


def load_config(path: Path) -> M38bV2Config:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m38b_branch_dispersion_v2"]
    return M38bV2Config(
        enabled=bool(block["enabled"]),
        wavepacket_case_grid=Path(block["input"]["wavepacket_case_grid"]),
        wavepacket_metrics=Path(block["input"]["wavepacket_metrics"]),
        dispersion_pair_full=Path(block["input"]["dispersion_pair_full"]),
        dispersion_pair_topk=Path(block["input"]["dispersion_pair_topk"]),
        dispersion_pair_top_summary=Path(block["input"]["dispersion_pair_top_summary"]),
        dispersion_class_summary=Path(block["input"]["dispersion_class_summary"]),
        dispersion_identity_comparison=Path(block["input"]["dispersion_identity_comparison"]),
        branch_reference_summary=Path(block["input"]["branch_reference_summary"]),
        sigma_branch_scores=Path(block["input"]["sigma_branch_scores"]),
        soft_branch_frequency=Path(block["input"]["soft_branch_frequency"]),
        reference_modes=[str(x) for x in block["matching"]["reference_modes"]],
        top_k_values=[int(x) for x in block["matching"]["top_k_values"]],
        class_modes=[str(x) for x in block["matching"]["class_modes"]],
        hard_min_score=float(block["matching"]["hard_min_score"]),
        hard_min_margin=float(block["matching"]["hard_min_margin"]),
        use_hard=bool(block["matching"]["use_hard"]),
        use_nearest=bool(block["matching"]["use_nearest"]),
        use_soft=bool(block["matching"]["use_soft"]),
        output_root=Path(block["output"]["root"]),
    )


def comparison_key_from_case_id(case_id: str) -> str:
    parts = [p for p in str(case_id).split("__") if not p.startswith("mode=") and not p.startswith("nu=")]
    return "__".join(parts)


def top_class_proxy(class_df: pd.DataFrame, class_mode: str, top_k: int = 3) -> pd.DataFrame:
    sub = class_df[class_df["class_mode"] == class_mode].copy()
    sub = sub.sort_values(["case_id", "class_rank"]).groupby("case_id", as_index=False).head(top_k)
    out = (
        sub.groupby("case_id", as_index=False)["normalized_class_contrib"]
        .sum()
        .rename(columns={"normalized_class_contrib": f"{class_mode}_proxy"})
    )
    return out


def build_case_features(
    pair_top_summary: pd.DataFrame,
    class_summary: pd.DataFrame,
    metrics_df: pd.DataFrame,
) -> pd.DataFrame:
    feat = pair_top_summary.copy()
    feat["comparison_key"] = feat["case_id"].map(comparison_key_from_case_id)

    dp = top_class_proxy(class_summary, "delta_p", top_k=3)
    dp2 = top_class_proxy(class_summary, "delta_p2", top_k=3)
    m = metrics_df[["case_id", "x_width_delta"]].copy()

    feat = feat.merge(dp, on="case_id", how="left")
    feat = feat.merge(dp2, on="case_id", how="left")
    feat = feat.merge(m, on="case_id", how="left")

    feat["pair_proxy"] = feat["top3_share"].astype(float)
    feat["delta_p_proxy"] = feat["delta_p_proxy"].fillna(0.0).astype(float)
    feat["delta_p2_proxy"] = feat["delta_p2_proxy"].fillna(0.0).astype(float)
    feat["x_width_delta"] = feat["x_width_delta"].fillna(0.0).astype(float)
    return feat


def standardize_within(df: pd.DataFrame, cols: List[str], group_col: str) -> pd.DataFrame:
    out_frames = []
    for group_value, sub in df.groupby(group_col, dropna=False):
        s = sub.copy()
        for col in cols:
            mu = float(s[col].mean())
            sd = float(s[col].std(ddof=0))
            s[f"{col}_z"] = 0.0 if sd <= 1.0e-12 else (s[col] - mu) / sd
        out_frames.append(s)
    return pd.concat(out_frames, ignore_index=True) if out_frames else df.copy()


def build_branch_prototypes(
    branch_ref_df: pd.DataFrame,
    sigma_branch_df: pd.DataFrame,
    reference_modes: List[str],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for ref_mode in reference_modes:
        sdf = sigma_branch_df[sigma_branch_df["mode"] == ref_mode].copy()
        if not sdf.empty:
            proto = (
                sdf.groupby("branch_label", as_index=False)
                .agg(
                    pair_proxy=("pair_separability_score", "median"),
                    delta_p_proxy=("delta_p_separability_score", "median"),
                    delta_p2_proxy=("delta_p2_separability_score", "median"),
                )
            )
            for row in proto.itertuples(index=False):
                rows.append(
                    {
                        "reference_mode": ref_mode,
                        "branch_label": str(row.branch_label),
                        "pair_proxy": float(row.pair_proxy) if pd.notna(row.pair_proxy) else 0.0,
                        "delta_p_proxy": float(row.delta_p_proxy) if pd.notna(row.delta_p_proxy) else 0.0,
                        "delta_p2_proxy": float(row.delta_p2_proxy) if pd.notna(row.delta_p2_proxy) else 0.0,
                    }
                )

    proto_df = pd.DataFrame(rows)

    if proto_df.empty and not branch_ref_df.empty:
        br = branch_ref_df.copy()
        if "mode" not in br.columns:
            br["mode"] = "pruned"
        fallback_rows: List[Dict[str, Any]] = []
        for ref_mode in reference_modes:
            sdf = br[br["mode"] == ref_mode].copy()
            for row in sdf.itertuples(index=False):
                fallback_rows.append(
                    {
                        "reference_mode": ref_mode,
                        "branch_label": str(row.branch_label),
                        "pair_proxy": float(getattr(row, "pair_separability_score", getattr(row, "mean_within_pair_overlap_top3", 0.0)) or 0.0),
                        "delta_p_proxy": float(getattr(row, "delta_p_separability_score", getattr(row, "mean_within_class_overlap_top3_delta_p", 0.0)) or 0.0),
                        "delta_p2_proxy": float(getattr(row, "delta_p2_separability_score", getattr(row, "mean_within_class_overlap_top3_delta_p2", 0.0)) or 0.0),
                    }
                )
        proto_df = pd.DataFrame(fallback_rows)

    if proto_df.empty:
        raise ValueError("Could not build branch prototypes from sigma_branch_scores or diversity_branch_summary.")

    return standardize_within(proto_df, ["pair_proxy", "delta_p_proxy", "delta_p2_proxy"], "reference_mode")


def dist3(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return float(np.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))))


def soft_scores_from_distances(dist_map: Dict[str, float]) -> Dict[str, float]:
    eps = 1.0e-9
    inv = {k: 1.0 / (eps + max(v, 0.0)) for k, v in dist_map.items()}
    total = float(sum(inv.values()))
    return {k: (v / total if total > 0 else 0.0) for k, v in inv.items()}


def assign_branch_row(
    row: pd.Series,
    proto_df_mode: pd.DataFrame,
    hard_min_score: float,
    hard_min_margin: float,
) -> Dict[str, Any]:
    feat = (float(row["pair_proxy_z"]), float(row["delta_p_proxy_z"]), float(row["delta_p2_proxy_z"]))
    dist_map: Dict[str, float] = {}
    for prow in proto_df_mode.itertuples(index=False):
        pfeat = (float(prow.pair_proxy_z), float(prow.delta_p_proxy_z), float(prow.delta_p2_proxy_z))
        dist_map[str(prow.branch_label)] = dist3(feat, pfeat)

    score_map = soft_scores_from_distances(dist_map)
    ranked = sorted(score_map.items(), key=lambda kv: kv[1], reverse=True)
    best_branch, best_score = ranked[0]
    second_branch, second_score = ranked[1] if len(ranked) > 1 else ("NONE", 0.0)
    margin = float(best_score - second_score)
    nearest_branch = min(dist_map, key=dist_map.get)
    soft_branch = best_branch

    hard_assignment_flag = int(best_score >= hard_min_score and margin >= hard_min_margin)
    hard_branch = best_branch if hard_assignment_flag == 1 else "NONE"

    return {
        "dist_to_S1": float(dist_map.get("S1", np.nan)),
        "dist_to_S2": float(dist_map.get("S2", np.nan)),
        "dist_to_S3": float(dist_map.get("S3", np.nan)),
        "score_S1": float(score_map.get("S1", 0.0)),
        "score_S2": float(score_map.get("S2", 0.0)),
        "score_S3": float(score_map.get("S3", 0.0)),
        "best_branch": best_branch,
        "second_branch": second_branch,
        "best_score": float(best_score),
        "second_score": float(second_score),
        "score_margin": margin,
        "hard_assignment_flag": hard_assignment_flag,
        "hard_branch": hard_branch,
        "nearest_branch": nearest_branch,
        "soft_branch": soft_branch,
    }


def get_case_id(p_family: str, k0: float, sigma_k: float, t: float, mode: str, nu: float) -> str:
    return f"{p_family}__k0={k0:.6g}__sk={sigma_k:.6g}__t={t:.6g}__mode={mode}__nu={nu:.6g}"


def pair_table_for_case(pair_full_df: pd.DataFrame, case_id: str) -> pd.DataFrame:
    return pair_full_df[pair_full_df["case_id"] == case_id].copy()


def pair_topk_table_for_case(pair_topk_df: pd.DataFrame, case_id: str, top_k: int) -> pd.DataFrame:
    return pair_topk_df[(pair_topk_df["case_id"] == case_id) & (pair_topk_df["top_k"] == top_k)].copy()


def pair_key_set(df: pd.DataFrame) -> set[tuple[int, int]]:
    return {(int(r.pair_i), int(r.pair_j)) for r in df.itertuples(index=False)}


def weight_map(df: pd.DataFrame, weight_col: str) -> Dict[tuple[int, int], float]:
    return {(int(r.pair_i), int(r.pair_j)): float(getattr(r, weight_col)) for r in df.itertuples(index=False)}


def rank_map(df: pd.DataFrame) -> Dict[tuple[int, int], int]:
    return {(int(r.pair_i), int(r.pair_j)): int(r.pair_rank_primary) for r in df.itertuples(index=False)}


def pair_overlap_metrics(top_none: pd.DataFrame, top_quad: pd.DataFrame, full_none: pd.DataFrame, full_quad: pd.DataFrame) -> Dict[str, Any]:
    set_none = pair_key_set(top_none)
    set_quad = pair_key_set(top_quad)
    inter = set_none.intersection(set_quad)

    overlap_frac = float(len(inter) / max(1, min(len(set_none), len(set_quad))))
    w_none = weight_map(top_none, "normalized_contrib_primary")
    w_quad = weight_map(top_quad, "normalized_contrib_primary")
    weighted_overlap = float(sum(min(w_none[k], w_quad[k]) for k in inter))

    entering = sorted(set_quad - set_none)
    leaving = sorted(set_none - set_quad)
    rank_none_full = rank_map(full_none)
    rank_quad_full = rank_map(full_quad)

    shared_rank_shifts = []
    detail_rows = []
    shared_all = set(rank_none_full.keys()).intersection(set(rank_quad_full.keys()))
    top_union = set_none.union(set_quad)
    relevant_keys = shared_all.intersection(top_union).union(set(entering)).union(set(leaving))

    full_w_none = weight_map(full_none, "normalized_contrib_primary")
    full_w_quad = weight_map(full_quad, "normalized_contrib_primary")

    for key in sorted(relevant_keys):
        present_none = int(key in full_w_none)
        present_quad = int(key in full_w_quad)
        rn = rank_none_full.get(key)
        rq = rank_quad_full.get(key)
        wn = full_w_none.get(key, 0.0)
        wq = full_w_quad.get(key, 0.0)
        if present_none and present_quad:
            migration_type = "shared"
            shared_rank_shifts.append(abs((rq or 0) - (rn or 0)))
        elif present_quad and not present_none:
            migration_type = "entering"
        else:
            migration_type = "leaving"

        detail_rows.append(
            {
                "pair_i": int(key[0]),
                "pair_j": int(key[1]),
                "present_in_none": present_none,
                "present_in_quadratic": present_quad,
                "rank_none": rn,
                "rank_quadratic": rq,
                "weight_none": wn,
                "weight_quadratic": wq,
                "rank_shift": None if (rn is None or rq is None) else int(rq - rn),
                "weight_shift": float(wq - wn),
                "migration_type": migration_type,
            }
        )

    mean_rank_shift_shared = float(np.mean(shared_rank_shifts)) if shared_rank_shifts else 0.0
    dominant_pair_preserved_flag = int(len(set_none.intersection(set_quad)) > 0 and min(rank_none_full.get(next(iter(inter), (-1, -1)), 999), 999) >= 1)

    if overlap_frac >= 0.8 and weighted_overlap < 0.9:
        migration_label = "stable_reweighting"
    elif overlap_frac >= 0.4:
        migration_label = "partial_migration"
    else:
        migration_label = "major_migration"

    return {
        "pair_overlap_none_vs_quadratic": overlap_frac,
        "weighted_pair_overlap": weighted_overlap,
        "n_entering_pairs": int(len(entering)),
        "n_leaving_pairs": int(len(leaving)),
        "mean_rank_shift_shared_pairs": mean_rank_shift_shared,
        "dominant_pair_preserved_flag": dominant_pair_preserved_flag,
        "pair_migration_label": migration_label,
        "detail_rows": detail_rows,
    }


def class_topk_overlap(class_none: pd.DataFrame, class_quad: pd.DataFrame, class_mode: str, top_k: int) -> float:
    a = class_none[class_none["class_mode"] == class_mode].sort_values("class_rank").head(top_k)
    b = class_quad[class_quad["class_mode"] == class_mode].sort_values("class_rank").head(top_k)
    sa = set(a["class_label"].astype(str).tolist())
    sb = set(b["class_label"].astype(str).tolist())
    return 0.0 if min(len(sa), len(sb)) == 0 else float(len(sa.intersection(sb)) / min(len(sa), len(sb)))


def stable_branch_for_summary(row: pd.Series) -> str:
    if str(row["branch_label_none_hard"]) != "NONE":
        return str(row["branch_label_none_hard"])
    return str(row["branch_label_none_nearest"])


def mean_or_none(series: pd.Series) -> float | None:
    if series.empty:
        return None
    return float(series.mean())


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.8b-v2 hard-branch / full-pair validation")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.8b-v2 disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    wavepacket_case_grid = pd.read_csv(resolve_path(project_root, cfg.wavepacket_case_grid))
    wavepacket_metrics = pd.read_csv(resolve_path(project_root, cfg.wavepacket_metrics))
    pair_full = pd.read_csv(resolve_path(project_root, cfg.dispersion_pair_full))
    pair_topk = pd.read_csv(resolve_path(project_root, cfg.dispersion_pair_topk))
    pair_top_summary = pd.read_csv(resolve_path(project_root, cfg.dispersion_pair_top_summary))
    class_summary = pd.read_csv(resolve_path(project_root, cfg.dispersion_class_summary))
    identity_cmp = pd.read_csv(resolve_path(project_root, cfg.dispersion_identity_comparison))
    branch_ref = pd.read_csv(resolve_path(project_root, cfg.branch_reference_summary))
    sigma_branch = pd.read_csv(resolve_path(project_root, cfg.sigma_branch_scores))
    soft_branch_frequency = pd.read_csv(resolve_path(project_root, cfg.soft_branch_frequency))

    case_feat = build_case_features(pair_top_summary, class_summary, wavepacket_metrics)
    case_feat["reference_mode"] = "global"
    case_feat = standardize_within(case_feat, ["pair_proxy", "delta_p_proxy", "delta_p2_proxy"], "reference_mode")
    case_feat = case_feat.drop(columns=["reference_mode"])

    proto_df = build_branch_prototypes(branch_ref, sigma_branch, cfg.reference_modes)

    match_score_rows: List[Dict[str, Any]] = []
    assignments_by_mode: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for ref_mode in cfg.reference_modes:
        proto_mode = proto_df[proto_df["reference_mode"] == ref_mode].copy()
        per_case: Dict[str, Dict[str, Any]] = {}
        for row in case_feat.to_dict(orient="records"):
            assign = assign_branch_row(pd.Series(row), proto_mode, cfg.hard_min_score, cfg.hard_min_margin)
            case_id = str(row["case_id"])
            per_case[case_id] = assign
            match_score_rows.append(
                {
                    "run_id": row["run_id"],
                    "case_id": case_id,
                    "side": str(row["dispersion_mode"]),
                    "reference_mode": ref_mode,
                    "dist_to_S1": assign["dist_to_S1"],
                    "dist_to_S2": assign["dist_to_S2"],
                    "dist_to_S3": assign["dist_to_S3"],
                    "score_S1": assign["score_S1"],
                    "score_S2": assign["score_S2"],
                    "score_S3": assign["score_S3"],
                    "best_branch": assign["best_branch"],
                    "second_branch": assign["second_branch"],
                    "best_score": assign["best_score"],
                    "second_score": assign["second_score"],
                    "score_margin": assign["score_margin"],
                    "hard_assignment_flag": assign["hard_assignment_flag"],
                }
            )
        assignments_by_mode[ref_mode] = per_case

    branch_dispersion_match_scores = pd.DataFrame(match_score_rows)

    class_case_map = {cid: g.copy() for cid, g in class_summary.groupby("case_id", dropna=False)}

    case_rows: List[Dict[str, Any]] = []
    pair_shift_rows: List[Dict[str, Any]] = []
    pair_detail_rows: List[Dict[str, Any]] = []
    class_shift_rows: List[Dict[str, Any]] = []

    for ref_mode in cfg.reference_modes:
        per_case = assignments_by_mode[ref_mode]

        for row in identity_cmp.itertuples(index=False):
            p_family = str(row.p_family)
            k0 = float(row.k0)
            sigma_k = float(row.sigma_k)
            t = float(row.t)
            nu = float(row.nu)

            case_none = get_case_id(p_family, k0, sigma_k, t, "none", 0.0)
            case_quad = get_case_id(p_family, k0, sigma_k, t, "quadratic", nu)

            if case_none not in per_case or case_quad not in per_case:
                continue

            none_assign = per_case[case_none]
            quad_assign = per_case[case_quad]

            full_none = pair_table_for_case(pair_full, case_none)
            full_quad = pair_table_for_case(pair_full, case_quad)
            class_none = class_case_map.get(case_none, pd.DataFrame())
            class_quad = class_case_map.get(case_quad, pd.DataFrame())

            migration_labels = []
            for top_k in cfg.top_k_values:
                top_none = pair_topk_table_for_case(pair_topk, case_none, top_k)
                top_quad = pair_topk_table_for_case(pair_topk, case_quad, top_k)
                metrics = pair_overlap_metrics(top_none, top_quad, full_none, full_quad)

                pair_shift_rows.append(
                    {
                        "run_id": getattr(row, "run_id", config_path.stem),
                        "case_id": str(row.comparison_id),
                        "reference_mode": ref_mode,
                        "top_k": top_k,
                        "branch_label_none": none_assign["soft_branch"],
                        "branch_label_quadratic": quad_assign["soft_branch"],
                        "pair_overlap_none_vs_quadratic": metrics["pair_overlap_none_vs_quadratic"],
                        "weighted_pair_overlap": metrics["weighted_pair_overlap"],
                        "n_entering_pairs": metrics["n_entering_pairs"],
                        "n_leaving_pairs": metrics["n_leaving_pairs"],
                        "mean_rank_shift_shared_pairs": metrics["mean_rank_shift_shared_pairs"],
                        "dominant_pair_preserved_flag": metrics["dominant_pair_preserved_flag"],
                        "pair_migration_label": metrics["pair_migration_label"],
                        "identity_preserved_flag": int(metrics["pair_overlap_none_vs_quadratic"] > 0.0 and metrics["weighted_pair_overlap"] >= 0.6),
                    }
                )
                migration_labels.append(metrics["pair_migration_label"])

                for detail in metrics["detail_rows"]:
                    pair_detail_rows.append(
                        {
                            "run_id": getattr(row, "run_id", config_path.stem),
                            "case_id": str(row.comparison_id),
                            "reference_mode": ref_mode,
                            "top_k": top_k,
                            **detail,
                        }
                    )

            for class_mode in cfg.class_modes:
                for top_k in cfg.top_k_values:
                    overlap_frac = class_topk_overlap(class_none, class_quad, class_mode, top_k)
                    shift_col_none = "delta_p_sep_none" if class_mode == "delta_p" else "delta_p2_sep_none"
                    shift_col_quad = "delta_p_sep_quadratic" if class_mode == "delta_p" else "delta_p2_sep_quadratic"
                    weighted_shift = float(getattr(row, shift_col_quad) - getattr(row, shift_col_none))
                    class_shift_rows.append(
                        {
                            "run_id": getattr(row, "run_id", config_path.stem),
                            "case_id": str(row.comparison_id),
                            "reference_mode": ref_mode,
                            "class_mode": class_mode,
                            "top_k": top_k,
                            "branch_label_none": none_assign["soft_branch"],
                            "branch_label_quadratic": quad_assign["soft_branch"],
                            "class_overlap_none_vs_quadratic": overlap_frac,
                            "weighted_class_shift": weighted_shift,
                            "identity_preserved_flag": int(overlap_frac > 0.0 and abs(weighted_shift) <= 0.1),
                        }
                    )

            migration_mode = "major_migration" if "major_migration" in migration_labels else ("partial_migration" if "partial_migration" in migration_labels else "stable_reweighting")

            case_rows.append(
                {
                    "run_id": getattr(row, "run_id", config_path.stem),
                    "case_id": str(row.comparison_id),
                    "p_family": p_family,
                    "k0": k0,
                    "sigma_k": sigma_k,
                    "t": t,
                    "v": float(row.v),
                    "nu": nu,
                    "reference_mode": ref_mode,
                    "x_width_delta": float(row.delta_width_x),
                    "branch_label_none_hard": none_assign["hard_branch"],
                    "branch_label_quadratic_hard": quad_assign["hard_branch"],
                    "branch_label_none_nearest": none_assign["nearest_branch"],
                    "branch_label_quadratic_nearest": quad_assign["nearest_branch"],
                    "branch_label_none_soft": none_assign["soft_branch"],
                    "branch_label_quadratic_soft": quad_assign["soft_branch"],
                    "hard_branch_change_flag": int(none_assign["hard_branch"] != quad_assign["hard_branch"]),
                    "nearest_branch_change_flag": int(none_assign["nearest_branch"] != quad_assign["nearest_branch"]),
                    "soft_branch_change_flag": int(none_assign["soft_branch"] != quad_assign["soft_branch"]),
                    "hard_branch_ambiguous_flag_none": int(none_assign["hard_branch"] == "NONE"),
                    "hard_branch_ambiguous_flag_quadratic": int(quad_assign["hard_branch"] == "NONE"),
                    "dispersion_sensitive_flag": int(str(row.identity_shift_label) == "dispersion_sensitive"),
                    "pair_migration_label": migration_mode,
                }
            )

    branch_dispersion_case_table = pd.DataFrame(case_rows)
    branch_dispersion_pair_shift = pd.DataFrame(pair_shift_rows)
    branch_dispersion_pair_migration_detail = pd.DataFrame(pair_detail_rows)
    branch_dispersion_class_shift = pd.DataFrame(class_shift_rows)

    # branch summary
    summary_rows: List[Dict[str, Any]] = []
    if not branch_dispersion_case_table.empty:
        branch_dispersion_case_table["branch_label"] = branch_dispersion_case_table.apply(stable_branch_for_summary, axis=1)

        for (ref_mode, branch_label), sub in branch_dispersion_case_table.groupby(["reference_mode", "branch_label"], dropna=False):
            prs = branch_dispersion_pair_shift[
                (branch_dispersion_pair_shift["reference_mode"] == ref_mode)
                & (branch_dispersion_pair_shift["branch_label_none"] == branch_label)
            ]
            cls = branch_dispersion_class_shift[
                (branch_dispersion_class_shift["reference_mode"] == ref_mode)
                & (branch_dispersion_class_shift["branch_label_none"] == branch_label)
            ]

            hard_pres = 1.0 - float(sub["hard_branch_change_flag"].mean())
            nearest_pres = 1.0 - float(sub["nearest_branch_change_flag"].mean())
            soft_pres = 1.0 - float(sub["soft_branch_change_flag"].mean())
            hard_ambiguity_rate = float((sub["hard_branch_ambiguous_flag_none"] | sub["hard_branch_ambiguous_flag_quadratic"]).mean())

            top3 = prs[prs["top_k"] == 3]
            top5 = prs[prs["top_k"] == 5]
            mean_pair_overlap_top3 = mean_or_none(top3["pair_overlap_none_vs_quadratic"])
            mean_pair_overlap_top5 = mean_or_none(top5["pair_overlap_none_vs_quadratic"])
            mean_weighted_pair_overlap_top3 = mean_or_none(top3["weighted_pair_overlap"])
            mean_dp_shift = mean_or_none(cls[cls["class_mode"] == "delta_p"]["weighted_class_shift"])
            mean_dp2_shift = mean_or_none(cls[cls["class_mode"] == "delta_p2"]["weighted_class_shift"])
            mean_x_width_delta = mean_or_none(sub["x_width_delta"])
            dispersion_sensitivity_rate = mean_or_none(sub["dispersion_sensitive_flag"])
            stable_reweighting_rate = mean_or_none((sub["pair_migration_label"] == "stable_reweighting").astype(float))
            major_migration_rate = mean_or_none((sub["pair_migration_label"] == "major_migration").astype(float))

            if (stable_reweighting_rate or 0.0) >= 0.5 and (dispersion_sensitivity_rate or 0.0) >= 0.1:
                signature_label = "reweighting_sensitive"
            elif (mean_dp2_shift is not None and abs(mean_dp2_shift) <= 0.05 and (soft_pres or 0.0) >= 0.8):
                signature_label = "delta_p2_stable"
            elif (major_migration_rate or 0.0) >= 0.2:
                signature_label = "migration_prone"
            else:
                signature_label = "stable"

            summary_rows.append(
                {
                    "run_id": config_path.stem,
                    "reference_mode": ref_mode,
                    "branch_label": branch_label,
                    "n_cases": int(len(sub)),
                    "hard_preservation_rate": hard_pres,
                    "nearest_preservation_rate": nearest_pres,
                    "soft_preservation_rate": soft_pres,
                    "hard_ambiguity_rate": hard_ambiguity_rate,
                    "mean_pair_overlap_top3": mean_pair_overlap_top3,
                    "mean_pair_overlap_top5": mean_pair_overlap_top5,
                    "mean_weighted_pair_overlap_top3": mean_weighted_pair_overlap_top3,
                    "mean_delta_p_shift": mean_dp_shift,
                    "mean_delta_p2_shift": mean_dp2_shift,
                    "mean_x_width_delta": mean_x_width_delta,
                    "dispersion_sensitivity_rate": dispersion_sensitivity_rate,
                    "stable_reweighting_rate": stable_reweighting_rate,
                    "major_migration_rate": major_migration_rate,
                    "signature_label": signature_label,
                }
            )

    branch_dispersion_branch_summary = pd.DataFrame(summary_rows)

    # migration matrix
    matrix_rows: List[Dict[str, Any]] = []
    if not branch_dispersion_case_table.empty:
        for mode_name, from_col, to_col in [
            ("hard", "branch_label_none_hard", "branch_label_quadratic_hard"),
            ("nearest", "branch_label_none_nearest", "branch_label_quadratic_nearest"),
            ("soft", "branch_label_none_soft", "branch_label_quadratic_soft"),
        ]:
            grp = (
                branch_dispersion_case_table.groupby(["reference_mode", from_col, to_col], dropna=False)
                .size()
                .reset_index(name="n_cases")
            )
            for ref_mode in grp["reference_mode"].dropna().unique().tolist():
                sub = grp[grp["reference_mode"] == ref_mode].copy()
                total = int(sub["n_cases"].sum())
                for row in sub.itertuples(index=False):
                    matrix_rows.append(
                        {
                            "run_id": config_path.stem,
                            "reference_mode": ref_mode,
                            "branch_from": getattr(row, from_col),
                            "branch_to": getattr(row, to_col),
                            "n_cases": int(row.n_cases),
                            "fraction": float(row.n_cases / max(1, total)),
                            "mode": mode_name,
                        }
                    )

    branch_dispersion_migration_matrix = pd.DataFrame(matrix_rows)

    # S2 focus
    s2_rows: List[Dict[str, Any]] = []
    if not branch_dispersion_case_table.empty:
        branch_dispersion_case_table["branch_label"] = branch_dispersion_case_table.apply(stable_branch_for_summary, axis=1)
        for ref_mode in cfg.reference_modes:
            sub = branch_dispersion_case_table[
                (branch_dispersion_case_table["reference_mode"] == ref_mode)
                & (branch_dispersion_case_table["branch_label"] == "S2")
            ].copy()
            prs = branch_dispersion_pair_shift[
                (branch_dispersion_pair_shift["reference_mode"] == ref_mode)
                & (branch_dispersion_pair_shift["branch_label_none"] == "S2")
                & (branch_dispersion_pair_shift["top_k"] == 3)
            ]
            cls = branch_dispersion_class_shift[
                (branch_dispersion_class_shift["reference_mode"] == ref_mode)
                & (branch_dispersion_class_shift["branch_label_none"] == "S2")
            ]
            if sub.empty and prs.empty and cls.empty:
                continue

            hard_pres = 1.0 - float(sub["hard_branch_change_flag"].mean()) if not sub.empty else np.nan
            nearest_pres = 1.0 - float(sub["nearest_branch_change_flag"].mean()) if not sub.empty else np.nan
            soft_pres = 1.0 - float(sub["soft_branch_change_flag"].mean()) if not sub.empty else np.nan
            hard_amb = float((sub["hard_branch_ambiguous_flag_none"] | sub["hard_branch_ambiguous_flag_quadratic"]).mean()) if not sub.empty else np.nan
            mean_pair_overlap_top3 = mean_or_none(prs["pair_overlap_none_vs_quadratic"])
            mean_weighted_pair_overlap_top3 = mean_or_none(prs["weighted_pair_overlap"])
            mean_dp_shift = mean_or_none(cls[cls["class_mode"] == "delta_p"]["weighted_class_shift"])
            mean_dp2_shift = mean_or_none(cls[cls["class_mode"] == "delta_p2"]["weighted_class_shift"])
            mean_x_width_delta = mean_or_none(sub["x_width_delta"])
            stable_reweighting_rate = mean_or_none((sub["pair_migration_label"] == "stable_reweighting").astype(float))
            major_migration_rate = mean_or_none((sub["pair_migration_label"] == "major_migration").astype(float))

            if (stable_reweighting_rate or 0.0) >= 0.5 and (major_migration_rate or 0.0) < 0.2:
                sens_label = "stable_reweighting"
            elif (major_migration_rate or 0.0) >= 0.2:
                sens_label = "major_migration"
            elif (hard_amb or 0.0) >= 0.2:
                sens_label = "hard_ambiguity"
            else:
                sens_label = "mild"

            s2_rows.append(
                {
                    "run_id": config_path.stem,
                    "reference_mode": ref_mode,
                    "n_cases_S2": int(len(sub)),
                    "hard_preservation_rate": hard_pres,
                    "nearest_preservation_rate": nearest_pres,
                    "soft_preservation_rate": soft_pres,
                    "mean_pair_overlap_top3": mean_pair_overlap_top3,
                    "mean_weighted_pair_overlap_top3": mean_weighted_pair_overlap_top3,
                    "mean_delta_p_shift": mean_dp_shift,
                    "mean_delta_p2_shift": mean_dp2_shift,
                    "mean_x_width_delta": mean_x_width_delta,
                    "stable_reweighting_rate": stable_reweighting_rate,
                    "major_migration_rate": major_migration_rate,
                    "hard_ambiguity_rate": hard_amb,
                    "S2_sensitivity_label": sens_label,
                }
            )

    s2_focus_summary = pd.DataFrame(s2_rows)

    # global summary
    if branch_dispersion_case_table.empty:
        global_summary = {
            "n_cases_total": 0,
            "hard_branch_preservation_rate": 0.0,
            "nearest_branch_preservation_rate": 0.0,
            "soft_branch_preservation_rate": 0.0,
            "hard_branch_ambiguity_rate": 0.0,
            "delta_p_preservation_rate": 0.0,
            "delta_p2_preservation_rate": 0.0,
            "pair_preservation_rate": 0.0,
            "pair_overlap_top3_mean": 0.0,
            "weighted_pair_overlap_top3_mean": 0.0,
            "most_stable_identity_level": None,
            "most_dispersion_sensitive_branch": None,
            "S2_migration_mode": None,
            "final_label": "I3v2-0",
        }
    else:
        hard_pres = 1.0 - float(branch_dispersion_case_table["hard_branch_change_flag"].mean())
        nearest_pres = 1.0 - float(branch_dispersion_case_table["nearest_branch_change_flag"].mean())
        soft_pres = 1.0 - float(branch_dispersion_case_table["soft_branch_change_flag"].mean())
        hard_amb = float((branch_dispersion_case_table["hard_branch_ambiguous_flag_none"] | branch_dispersion_case_table["hard_branch_ambiguous_flag_quadratic"]).mean())
        dp_pres = float(branch_dispersion_class_shift[branch_dispersion_class_shift["class_mode"] == "delta_p"]["identity_preserved_flag"].mean()) if not branch_dispersion_class_shift.empty else 0.0
        dp2_pres = float(branch_dispersion_class_shift[branch_dispersion_class_shift["class_mode"] == "delta_p2"]["identity_preserved_flag"].mean()) if not branch_dispersion_class_shift.empty else 0.0
        pair_pres = float(branch_dispersion_pair_shift["identity_preserved_flag"].mean()) if not branch_dispersion_pair_shift.empty else 0.0
        pair_overlap_top3_mean = float(branch_dispersion_pair_shift[branch_dispersion_pair_shift["top_k"] == 3]["pair_overlap_none_vs_quadratic"].mean()) if not branch_dispersion_pair_shift.empty else 0.0
        weighted_pair_overlap_top3_mean = float(branch_dispersion_pair_shift[branch_dispersion_pair_shift["top_k"] == 3]["weighted_pair_overlap"].mean()) if not branch_dispersion_pair_shift.empty else 0.0

        stable_map = {"pair": pair_pres, "delta_p_class": dp_pres, "delta_p2_class": dp2_pres}
        most_stable_identity_level = max(stable_map, key=stable_map.get)

        if not branch_dispersion_branch_summary.empty:
            sens = branch_dispersion_branch_summary.groupby("branch_label", as_index=False)["dispersion_sensitivity_rate"].mean().sort_values("dispersion_sensitivity_rate", ascending=False)
            most_dispersion_sensitive_branch = str(sens.iloc[0]["branch_label"])
        else:
            most_dispersion_sensitive_branch = None

        if not s2_focus_summary.empty:
            s2_mode = str(s2_focus_summary.iloc[0]["S2_sensitivity_label"])
        else:
            s2_mode = None

        if soft_pres >= 0.9 and hard_pres >= 0.75 and most_dispersion_sensitive_branch == "S2":
            final_label = "I3v2-4" if s2_mode == "stable_reweighting" else "I3v2-3"
        elif soft_pres >= 0.8 and most_dispersion_sensitive_branch == "S2":
            final_label = "I3v2-2"
        elif soft_pres >= 0.5:
            final_label = "I3v2-1"
        else:
            final_label = "I3v2-0"

        global_summary = {
            "n_cases_total": int(len(branch_dispersion_case_table)),
            "hard_branch_preservation_rate": hard_pres,
            "nearest_branch_preservation_rate": nearest_pres,
            "soft_branch_preservation_rate": soft_pres,
            "hard_branch_ambiguity_rate": hard_amb,
            "delta_p_preservation_rate": dp_pres,
            "delta_p2_preservation_rate": dp2_pres,
            "pair_preservation_rate": pair_pres,
            "pair_overlap_top3_mean": pair_overlap_top3_mean,
            "weighted_pair_overlap_top3_mean": weighted_pair_overlap_top3_mean,
            "most_stable_identity_level": most_stable_identity_level,
            "most_dispersion_sensitive_branch": most_dispersion_sensitive_branch,
            "S2_migration_mode": s2_mode,
            "final_label": final_label,
        }

    branch_dispersion_case_table.to_csv(out_root / "branch_dispersion_case_table.csv", index=False)
    branch_dispersion_match_scores.to_csv(out_root / "branch_dispersion_match_scores.csv", index=False)
    branch_dispersion_pair_shift.to_csv(out_root / "branch_dispersion_pair_shift.csv", index=False)
    branch_dispersion_pair_migration_detail.to_csv(out_root / "branch_dispersion_pair_migration_detail.csv", index=False)
    branch_dispersion_class_shift.to_csv(out_root / "branch_dispersion_class_shift.csv", index=False)
    branch_dispersion_branch_summary.to_csv(out_root / "branch_dispersion_branch_summary.csv", index=False)
    branch_dispersion_migration_matrix.to_csv(out_root / "branch_dispersion_migration_matrix.csv", index=False)
    s2_focus_summary.to_csv(out_root / "S2_focus_summary.csv", index=False)
    write_json(out_root / "branch_dispersion_global_summary.json", global_summary)

    report_lines = [
        "# M.3.8b-v2 Hard-Branch / Full-Pair Validation",
        "",
        f"- n_cases_total: {safe_json_value(global_summary['n_cases_total'])}",
        f"- hard_branch_preservation_rate: {safe_json_value(global_summary['hard_branch_preservation_rate'])}",
        f"- nearest_branch_preservation_rate: {safe_json_value(global_summary['nearest_branch_preservation_rate'])}",
        f"- soft_branch_preservation_rate: {safe_json_value(global_summary['soft_branch_preservation_rate'])}",
        f"- hard_branch_ambiguity_rate: {safe_json_value(global_summary['hard_branch_ambiguity_rate'])}",
        f"- delta_p_preservation_rate: {safe_json_value(global_summary['delta_p_preservation_rate'])}",
        f"- delta_p2_preservation_rate: {safe_json_value(global_summary['delta_p2_preservation_rate'])}",
        f"- pair_preservation_rate: {safe_json_value(global_summary['pair_preservation_rate'])}",
        f"- pair_overlap_top3_mean: {safe_json_value(global_summary['pair_overlap_top3_mean'])}",
        f"- weighted_pair_overlap_top3_mean: {safe_json_value(global_summary['weighted_pair_overlap_top3_mean'])}",
        f"- most_stable_identity_level: {safe_json_value(global_summary['most_stable_identity_level'])}",
        f"- most_dispersion_sensitive_branch: {safe_json_value(global_summary['most_dispersion_sensitive_branch'])}",
        f"- S2_migration_mode: {safe_json_value(global_summary['S2_migration_mode'])}",
        f"- final_label: {safe_json_value(global_summary['final_label'])}",
        "",
        "This v2 uses full persisted pair tables and an independent hard-branch rule.",
    ]
    (out_root / "branch_dispersion_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.8b-v2 completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
