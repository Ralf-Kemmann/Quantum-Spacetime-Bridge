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
class M38bConfig:
    enabled: bool
    wavepacket_case_grid: Path
    wavepacket_metrics: Path
    dispersion_pair_top_summary: Path
    dispersion_class_summary: Path
    dispersion_identity_comparison: Path
    branch_reference_summary: Path
    sigma_branch_scores: Path
    soft_branch_frequency: Path
    reference_modes: List[str]
    top_k_values: List[int]
    class_modes: List[str]
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


def load_config(path: Path) -> M38bConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m38b_branch_dispersion"]
    return M38bConfig(
        enabled=bool(block["enabled"]),
        wavepacket_case_grid=Path(block["input"]["wavepacket_case_grid"]),
        wavepacket_metrics=Path(block["input"]["wavepacket_metrics"]),
        dispersion_pair_top_summary=Path(block["input"]["dispersion_pair_top_summary"]),
        dispersion_class_summary=Path(block["input"]["dispersion_class_summary"]),
        dispersion_identity_comparison=Path(block["input"]["dispersion_identity_comparison"]),
        branch_reference_summary=Path(block["input"]["branch_reference_summary"]),
        sigma_branch_scores=Path(block["input"]["sigma_branch_scores"]),
        soft_branch_frequency=Path(block["input"]["soft_branch_frequency"]),
        reference_modes=[str(x) for x in block["matching"]["reference_modes"]],
        top_k_values=[int(x) for x in block["matching"]["top_k_values"]],
        class_modes=[str(x) for x in block["matching"]["class_modes"]],
        use_hard=bool(block["matching"]["use_hard"]),
        use_nearest=bool(block["matching"]["use_nearest"]),
        use_soft=bool(block["matching"]["use_soft"]),
        output_root=Path(block["output"]["root"]),
    )


def comparison_key_from_case_id(case_id: str) -> str:
    parts = [p for p in case_id.split("__") if not p.startswith("mode=") and not p.startswith("nu=")]
    return "__".join(parts)


def build_case_features(
    pair_top_df: pd.DataFrame,
    class_df: pd.DataFrame,
    metrics_df: pd.DataFrame,
) -> pd.DataFrame:
    pair_top = pair_top_df.copy()
    topk_dp = (
        class_df[class_df["class_mode"] == "delta_p"]
        .sort_values(["case_id", "class_rank"])
        .groupby("case_id", as_index=False)
        .head(3)
        .groupby("case_id", as_index=False)["normalized_class_contrib"]
        .sum()
        .rename(columns={"normalized_class_contrib": "delta_p_proxy"})
    )
    topk_dp2 = (
        class_df[class_df["class_mode"] == "delta_p2"]
        .sort_values(["case_id", "class_rank"])
        .groupby("case_id", as_index=False)
        .head(3)
        .groupby("case_id", as_index=False)["normalized_class_contrib"]
        .sum()
        .rename(columns={"normalized_class_contrib": "delta_p2_proxy"})
    )
    metrics_small = metrics_df[["case_id", "x_width_delta"]].copy()

    feat = pair_top.merge(topk_dp, on="case_id", how="left")
    feat = feat.merge(topk_dp2, on="case_id", how="left")
    feat = feat.merge(metrics_small, on="case_id", how="left")

    feat["comparison_key"] = feat["case_id"].map(comparison_key_from_case_id)
    feat["pair_proxy"] = feat["top3_share"].astype(float)
    feat["delta_p_proxy"] = feat["delta_p_proxy"].fillna(0.0).astype(float)
    feat["delta_p2_proxy"] = feat["delta_p2_proxy"].fillna(0.0).astype(float)
    feat["x_width_delta"] = feat["x_width_delta"].fillna(0.0).astype(float)
    return feat


def build_branch_prototypes(
    branch_ref_df: pd.DataFrame,
    sigma_branch_df: pd.DataFrame,
    reference_modes: List[str],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for ref_mode in reference_modes:
        sdf = sigma_branch_df[sigma_branch_df["mode"] == ref_mode].copy()
        if sdf.empty:
            continue
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
                    "branch_label": row.branch_label,
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
        for ref_mode in reference_modes:
            sdf = br[br["mode"] == ref_mode].copy()
            if sdf.empty:
                continue
            for row in sdf.itertuples(index=False):
                rows.append(
                    {
                        "reference_mode": ref_mode,
                        "branch_label": getattr(row, "branch_label"),
                        "pair_proxy": float(getattr(row, "pair_separability_score", 0.0) if pd.notna(getattr(row, "pair_separability_score", np.nan)) else 0.0),
                        "delta_p_proxy": float(getattr(row, "delta_p_separability_score", 0.0) if pd.notna(getattr(row, "delta_p_separability_score", np.nan)) else 0.0),
                        "delta_p2_proxy": float(getattr(row, "delta_p2_separability_score", 0.0) if pd.notna(getattr(row, "delta_p2_separability_score", np.nan)) else 0.0),
                    }
                )
        proto_df = pd.DataFrame(rows)

    if proto_df.empty:
        raise ValueError("Could not build branch prototypes from inputs.")

    out = []
    for ref_mode, sub in proto_df.groupby("reference_mode", dropna=False):
        s = sub.copy()
        for col in ["pair_proxy", "delta_p_proxy", "delta_p2_proxy"]:
            mu = float(s[col].mean())
            sd = float(s[col].std(ddof=0))
            s[f"{col}_z"] = 0.0 if sd <= 1e-12 else (s[col] - mu) / sd
        out.append(s)
    return pd.concat(out, ignore_index=True)


def zscore_case_features(features_df: pd.DataFrame) -> pd.DataFrame:
    out = features_df.copy()
    for col in ["pair_proxy", "delta_p_proxy", "delta_p2_proxy"]:
        mu = float(out[col].mean())
        sd = float(out[col].std(ddof=0))
        out[f"{col}_z"] = 0.0 if sd <= 1e-12 else (out[col] - mu) / sd
    return out


def dist3(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return float(np.sqrt(sum((x - y) ** 2 for x, y in zip(a, b))))


def soft_scores_from_distances(dist_map: Dict[str, float]) -> Dict[str, float]:
    eps = 1.0e-9
    inv = {k: 1.0 / (eps + max(v, 0.0)) for k, v in dist_map.items()}
    total = sum(inv.values())
    return {k: (v / total if total > 0 else 0.0) for k, v in inv.items()}


def assign_branches(
    features_df: pd.DataFrame,
    proto_df: pd.DataFrame,
    reference_mode: str,
) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
    sub_proto = proto_df[proto_df["reference_mode"] == reference_mode].copy()
    if sub_proto.empty:
        raise ValueError(f"No prototypes for reference_mode={reference_mode}")

    score_rows = []
    per_case = {}

    for row in features_df.itertuples(index=False):
        feat = (float(row.pair_proxy_z), float(row.delta_p_proxy_z), float(row.delta_p2_proxy_z))
        dist_map = {}
        for prow in sub_proto.itertuples(index=False):
            pfeat = (float(prow.pair_proxy_z), float(prow.delta_p_proxy_z), float(prow.delta_p2_proxy_z))
            dist_map[str(prow.branch_label)] = dist3(feat, pfeat)

        soft_map = soft_scores_from_distances(dist_map)
        nearest_branch = min(dist_map, key=dist_map.get)
        soft_branch = max(soft_map, key=soft_map.get)
        hard_branch = nearest_branch

        per_case[str(row.case_id)] = {
            "hard_branch": hard_branch,
            "nearest_branch": nearest_branch,
            "soft_branch": soft_branch,
            "best_branch_score": float(soft_map[soft_branch]),
            "dist_to_S1": float(dist_map.get("S1", np.nan)),
            "dist_to_S2": float(dist_map.get("S2", np.nan)),
            "dist_to_S3": float(dist_map.get("S3", np.nan)),
            "soft_overlap_S1": float(soft_map.get("S1", 0.0)),
            "soft_overlap_S2": float(soft_map.get("S2", 0.0)),
            "soft_overlap_S3": float(soft_map.get("S3", 0.0)),
        }

        for cand in ["S1", "S2", "S3"]:
            score_rows.append(
                {
                    "run_id": row.run_id,
                    "case_id": row.case_id,
                    "dispersion_mode": row.dispersion_mode,
                    "reference_mode": reference_mode,
                    "branch_candidate": cand,
                    "dist_to_S1": float(dist_map.get("S1", np.nan)),
                    "dist_to_S2": float(dist_map.get("S2", np.nan)),
                    "dist_to_S3": float(dist_map.get("S3", np.nan)),
                    "soft_overlap_S1": float(soft_map.get("S1", 0.0)),
                    "soft_overlap_S2": float(soft_map.get("S2", 0.0)),
                    "soft_overlap_S3": float(soft_map.get("S3", 0.0)),
                    "best_branch": soft_branch,
                    "best_branch_score": float(soft_map[soft_branch]),
                }
            )

    return pd.DataFrame(score_rows), per_case


def class_topk_overlap(df_a: pd.DataFrame, df_b: pd.DataFrame, class_mode: str, top_k: int) -> Tuple[int, float]:
    a = df_a[df_a["class_mode"] == class_mode].sort_values("class_rank").head(top_k)
    b = df_b[df_b["class_mode"] == class_mode].sort_values("class_rank").head(top_k)
    sa = set(a["class_label"].astype(str).tolist())
    sb = set(b["class_label"].astype(str).tolist())
    inter = sa.intersection(sb)
    frac = 0.0 if min(len(sa), len(sb)) == 0 else float(len(inter) / min(len(sa), len(sb)))
    return len(inter), frac


def mean_or_none(series: pd.Series) -> float | None:
    if series.empty:
        return None
    return float(series.mean())


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.8b branch-coupled dispersion test")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.8b disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    wavepacket_case_grid = pd.read_csv(resolve_path(project_root, cfg.wavepacket_case_grid))
    wavepacket_metrics = pd.read_csv(resolve_path(project_root, cfg.wavepacket_metrics))
    pair_top = pd.read_csv(resolve_path(project_root, cfg.dispersion_pair_top_summary))
    class_summary = pd.read_csv(resolve_path(project_root, cfg.dispersion_class_summary))
    identity_cmp = pd.read_csv(resolve_path(project_root, cfg.dispersion_identity_comparison))
    branch_ref = pd.read_csv(resolve_path(project_root, cfg.branch_reference_summary))
    sigma_branch = pd.read_csv(resolve_path(project_root, cfg.sigma_branch_scores))
    _soft_branch = pd.read_csv(resolve_path(project_root, cfg.soft_branch_frequency))

    case_feat = zscore_case_features(build_case_features(pair_top, class_summary, wavepacket_metrics))
    proto_df = build_branch_prototypes(branch_ref, sigma_branch, cfg.reference_modes)

    match_score_frames = []
    class_shift_rows = []
    pair_shift_rows = []
    case_rows = []

    class_case_map = {cid: g.copy() for cid, g in class_summary.groupby("case_id", dropna=False)}

    assigned_per_mode = {}
    for ref_mode in cfg.reference_modes:
        score_df, per_case = assign_branches(case_feat, proto_df, ref_mode)
        match_score_frames.append(score_df)
        assigned_per_mode[ref_mode] = per_case

    for ref_mode in cfg.reference_modes:
        per_case = assigned_per_mode[ref_mode]

        for row in identity_cmp.itertuples(index=False):
            p_family = str(row.p_family)
            k0 = float(row.k0)
            sigma_k = float(row.sigma_k)
            t = float(row.t)
            nu = float(row.nu)

            case_none = f"{p_family}__k0={k0:.6g}__sk={sigma_k:.6g}__t={t:.6g}__mode=none__nu=0"
            case_quad = f"{p_family}__k0={k0:.6g}__sk={sigma_k:.6g}__t={t:.6g}__mode=quadratic__nu={nu:.6g}"

            if case_none not in per_case or case_quad not in per_case:
                continue

            none_assign = per_case[case_none]
            quad_assign = per_case[case_quad]
            dispersion_sensitive_flag = int(str(row.identity_shift_label) == "dispersion_sensitive")

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
                    "dispersion_mode": "none_vs_quadratic",
                    "reference_mode": ref_mode,
                    "branch_label_none": none_assign["hard_branch"],
                    "branch_label_quadratic": quad_assign["hard_branch"],
                    "nearest_branch_none": none_assign["nearest_branch"],
                    "nearest_branch_quadratic": quad_assign["nearest_branch"],
                    "soft_branch_none": none_assign["soft_branch"],
                    "soft_branch_quadratic": quad_assign["soft_branch"],
                    "hard_branch_change_flag": int(none_assign["hard_branch"] != quad_assign["hard_branch"]),
                    "nearest_branch_change_flag": int(none_assign["nearest_branch"] != quad_assign["nearest_branch"]),
                    "soft_branch_change_flag": int(none_assign["soft_branch"] != quad_assign["soft_branch"]),
                    "x_width_delta": float(row.delta_width_x),
                    "dispersion_sensitive_flag": dispersion_sensitive_flag,
                }
            )

            if case_none in class_case_map and case_quad in class_case_map:
                cnone = class_case_map[case_none]
                cquad = class_case_map[case_quad]
                for class_mode in cfg.class_modes:
                    for top_k in cfg.top_k_values:
                        _, overlap_frac = class_topk_overlap(cnone, cquad, class_mode, top_k)
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

            for top_k in cfg.top_k_values:
                weighted_pair_shift = float(row.pair_sep_quadratic - row.pair_sep_none)
                pair_overlap_frac = 1.0 if abs(weighted_pair_shift) <= 0.02 else (0.5 if abs(weighted_pair_shift) <= 0.1 else 0.0)
                pair_shift_rows.append(
                    {
                        "run_id": getattr(row, "run_id", config_path.stem),
                        "case_id": str(row.comparison_id),
                        "reference_mode": ref_mode,
                        "top_k": top_k,
                        "branch_label_none": none_assign["soft_branch"],
                        "branch_label_quadratic": quad_assign["soft_branch"],
                        "pair_overlap_none_vs_quadratic": pair_overlap_frac,
                        "weighted_pair_shift": weighted_pair_shift,
                        "identity_preserved_flag": int(pair_overlap_frac > 0.0 and abs(weighted_pair_shift) <= 0.1),
                    }
                )

    branch_dispersion_case_table = pd.DataFrame(case_rows)
    branch_dispersion_match_scores = pd.concat(match_score_frames, ignore_index=True) if match_score_frames else pd.DataFrame()
    branch_dispersion_class_shift = pd.DataFrame(class_shift_rows)
    branch_dispersion_pair_shift = pd.DataFrame(pair_shift_rows)

    summary_rows = []
    if not branch_dispersion_case_table.empty:
        for (ref_mode, branch_label), sub in branch_dispersion_case_table.groupby(["reference_mode", "soft_branch_none"], dropna=False):
            cls = branch_dispersion_class_shift[
                (branch_dispersion_class_shift["reference_mode"] == ref_mode)
                & (branch_dispersion_class_shift["branch_label_none"] == branch_label)
            ]
            prs = branch_dispersion_pair_shift[
                (branch_dispersion_pair_shift["reference_mode"] == ref_mode)
                & (branch_dispersion_pair_shift["branch_label_none"] == branch_label)
            ]

            hard_pres = 1.0 - float(sub["hard_branch_change_flag"].mean())
            nearest_pres = 1.0 - float(sub["nearest_branch_change_flag"].mean())
            soft_pres = 1.0 - float(sub["soft_branch_change_flag"].mean())
            mean_dp_shift = mean_or_none(cls[cls["class_mode"] == "delta_p"]["weighted_class_shift"])
            mean_dp2_shift = mean_or_none(cls[cls["class_mode"] == "delta_p2"]["weighted_class_shift"])
            mean_pair_shift = mean_or_none(prs["weighted_pair_shift"])
            mean_xwd = mean_or_none(sub["x_width_delta"])
            disp_rate = mean_or_none(sub["dispersion_sensitive_flag"])

            if (mean_dp2_shift is not None and abs(mean_dp2_shift) <= 0.05 and soft_pres >= 0.8):
                sig = "delta_p2_stable"
            elif (disp_rate or 0.0) >= 0.3:
                sig = "dispersion_sensitive"
            elif soft_pres >= 0.8:
                sig = "branch_stable"
            else:
                sig = "mixed"

            summary_rows.append(
                {
                    "run_id": config_path.stem,
                    "reference_mode": ref_mode,
                    "branch_label": branch_label,
                    "n_cases": int(len(sub)),
                    "hard_preservation_rate": hard_pres,
                    "nearest_preservation_rate": nearest_pres,
                    "soft_preservation_rate": soft_pres,
                    "mean_delta_p_shift": mean_dp_shift,
                    "mean_delta_p2_shift": mean_dp2_shift,
                    "mean_pair_shift": mean_pair_shift,
                    "mean_x_width_delta": mean_xwd,
                    "dispersion_sensitivity_rate": disp_rate,
                    "signature_label": sig,
                }
            )

    branch_dispersion_branch_summary = pd.DataFrame(summary_rows)

    if branch_dispersion_case_table.empty:
        global_summary = {
            "n_cases_total": 0,
            "hard_branch_preservation_rate": 0.0,
            "nearest_branch_preservation_rate": 0.0,
            "soft_branch_preservation_rate": 0.0,
            "delta_p_preservation_rate": 0.0,
            "delta_p2_preservation_rate": 0.0,
            "pair_preservation_rate": 0.0,
            "most_stable_identity_level": None,
            "most_dispersion_sensitive_branch": None,
            "final_label": "I0",
        }
    else:
        hard_pres = 1.0 - float(branch_dispersion_case_table["hard_branch_change_flag"].mean())
        nearest_pres = 1.0 - float(branch_dispersion_case_table["nearest_branch_change_flag"].mean())
        soft_pres = 1.0 - float(branch_dispersion_case_table["soft_branch_change_flag"].mean())
        dp_pres = float(branch_dispersion_class_shift[branch_dispersion_class_shift["class_mode"] == "delta_p"]["identity_preserved_flag"].mean()) if not branch_dispersion_class_shift.empty else 0.0
        dp2_pres = float(branch_dispersion_class_shift[branch_dispersion_class_shift["class_mode"] == "delta_p2"]["identity_preserved_flag"].mean()) if not branch_dispersion_class_shift.empty else 0.0
        pair_pres = float(branch_dispersion_pair_shift["identity_preserved_flag"].mean()) if not branch_dispersion_pair_shift.empty else 0.0

        stable_map = {"pair": pair_pres, "delta_p_class": dp_pres, "delta_p2_class": dp2_pres}
        most_stable = max(stable_map, key=stable_map.get)

        if not branch_dispersion_branch_summary.empty:
            sens_by_branch = (
                branch_dispersion_branch_summary.groupby("branch_label", as_index=False)["dispersion_sensitivity_rate"]
                .mean()
                .sort_values("dispersion_sensitivity_rate", ascending=False)
            )
            most_sensitive = sens_by_branch.iloc[0]["branch_label"]
        else:
            most_sensitive = None

        if soft_pres >= 0.85 and dp2_pres >= 0.9:
            final_label = "I3"
        elif soft_pres >= 0.75 and dp2_pres >= 0.75:
            final_label = "I2"
        elif max(hard_pres, nearest_pres, soft_pres) >= 0.5:
            final_label = "I1"
        else:
            final_label = "I0"

        global_summary = {
            "n_cases_total": int(len(branch_dispersion_case_table)),
            "hard_branch_preservation_rate": hard_pres,
            "nearest_branch_preservation_rate": nearest_pres,
            "soft_branch_preservation_rate": soft_pres,
            "delta_p_preservation_rate": dp_pres,
            "delta_p2_preservation_rate": dp2_pres,
            "pair_preservation_rate": pair_pres,
            "most_stable_identity_level": most_stable,
            "most_dispersion_sensitive_branch": most_sensitive,
            "final_label": final_label,
        }

    branch_dispersion_case_table.to_csv(out_root / "branch_dispersion_case_table.csv", index=False)
    branch_dispersion_match_scores.to_csv(out_root / "branch_dispersion_match_scores.csv", index=False)
    branch_dispersion_class_shift.to_csv(out_root / "branch_dispersion_class_shift.csv", index=False)
    branch_dispersion_pair_shift.to_csv(out_root / "branch_dispersion_pair_shift.csv", index=False)
    branch_dispersion_branch_summary.to_csv(out_root / "branch_dispersion_branch_summary.csv", index=False)
    write_json(out_root / "branch_dispersion_global_summary.json", global_summary)

    report_lines = [
        "# M.3.8b Branch-Coupled Dispersion Test",
        "",
        f"- n_cases_total: {safe_json_value(global_summary['n_cases_total'])}",
        f"- hard_branch_preservation_rate: {safe_json_value(global_summary['hard_branch_preservation_rate'])}",
        f"- nearest_branch_preservation_rate: {safe_json_value(global_summary['nearest_branch_preservation_rate'])}",
        f"- soft_branch_preservation_rate: {safe_json_value(global_summary['soft_branch_preservation_rate'])}",
        f"- delta_p_preservation_rate: {safe_json_value(global_summary['delta_p_preservation_rate'])}",
        f"- delta_p2_preservation_rate: {safe_json_value(global_summary['delta_p2_preservation_rate'])}",
        f"- pair_preservation_rate: {safe_json_value(global_summary['pair_preservation_rate'])}",
        f"- most_stable_identity_level: {safe_json_value(global_summary['most_stable_identity_level'])}",
        f"- most_dispersion_sensitive_branch: {safe_json_value(global_summary['most_dispersion_sensitive_branch'])}",
        f"- final_label: {safe_json_value(global_summary['final_label'])}",
        "",
        "Note: This is a skeleton integration layer. Hard-branch scoring currently reuses nearest-branch logic,",
        "and pair-shift rows use proxy shifts because M.3.8a does not persist full pair tables.",
    ]
    (out_root / "branch_dispersion_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.8b completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
