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
class M36bConfig:
    enabled: bool
    pair_contributions: Path
    pair_top_summary: Path
    pair_class_summary: Path
    top_k_values: List[int]
    branch_source_column: str
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


def load_config(path: Path) -> M36bConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m36b_pair_identity"]
    return M36bConfig(
        enabled=bool(block["enabled"]),
        pair_contributions=Path(block["input"]["pair_contributions"]),
        pair_top_summary=Path(block["input"]["pair_top_summary"]),
        pair_class_summary=Path(block["input"]["pair_class_summary"]),
        top_k_values=[int(x) for x in block["selection"]["top_k_values"]],
        branch_source_column=str(block["selection"]["branch_source_column"]),
        class_modes=[str(x) for x in block["comparison"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )


def case_label_from_row(row: pd.Series) -> str:
    return f"t={row.get('t')}__pf={row.get('p_family')}__th={row.get('theta')}"


def attach_case_and_branch(df: pd.DataFrame, branch_source_column: str) -> pd.DataFrame:
    out = df.copy()
    out["case_label"] = out.apply(case_label_from_row, axis=1)

    if "branch_pref_readout" in out.columns:
        out["branch_label"] = out["branch_pref_readout"]
    elif branch_source_column in out.columns:
        out["branch_label"] = out[branch_source_column]
    elif "best_branch_source" in out.columns:
        out["branch_label"] = out["best_branch_source"]
    else:
        out["branch_label"] = None
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


def identity_relation(frac_a: float, frac_b: float) -> str:
    m = min(frac_a, frac_b)
    if m >= 0.8:
        return "same"
    if m >= 0.3:
        return "partial_overlap"
    return "distinct"


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.6b pair/class identity comparison v2")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.6b disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    pair_contrib_df = attach_case_and_branch(
        pd.read_csv(resolve_path(project_root, cfg.pair_contributions)),
        cfg.branch_source_column,
    )
    pair_top_df = attach_case_and_branch(
        pd.read_csv(resolve_path(project_root, cfg.pair_top_summary)),
        cfg.branch_source_column,
    )
    pair_class_df = attach_case_and_branch(
        pd.read_csv(resolve_path(project_root, cfg.pair_class_summary)),
        cfg.branch_source_column,
    )

    pair_identity_rows: List[Dict[str, Any]] = []
    grouped_pairs: Dict[str, pd.DataFrame] = {}

    for case_label, g in pair_contrib_df.groupby("case_label", dropna=False):
        g2 = g.copy()
        g2["normalized_contrib_primary"] = normalized_contrib(g2, "contrib_primary")
        g2["is_top1_pair"] = (g2["pair_rank_primary"] <= 1).astype(int)
        g2["is_top3_pair"] = (g2["pair_rank_primary"] <= 3).astype(int)
        g2["is_top5_pair"] = (g2["pair_rank_primary"] <= 5).astype(int)
        grouped_pairs[str(case_label)] = g2

        for _, row in g2.iterrows():
            pair_identity_rows.append(
                {
                    "run_id": row["run_id"],
                    "case_label": case_label,
                    "t": row["t"],
                    "p_family": row["p_family"],
                    "theta": row["theta"],
                    "source_feature": row["source_feature"],
                    "branch_label": row["branch_label"],
                    "pair_i": row["pair_i"],
                    "pair_j": row["pair_j"],
                    "p_i": row["p_i"],
                    "p_j": row["p_j"],
                    "delta_p": row["delta_p"],
                    "delta_p2": row["delta_p2"],
                    "pair_rank_primary": row["pair_rank_primary"],
                    "contrib_primary": row["contrib_primary"],
                    "normalized_contrib_primary": row["normalized_contrib_primary"],
                    "is_top1_pair": row["is_top1_pair"],
                    "is_top3_pair": row["is_top3_pair"],
                    "is_top5_pair": row["is_top5_pair"],
                }
            )

    pair_identity_df = pd.DataFrame(pair_identity_rows)

    class_identity_rows: List[Dict[str, Any]] = []
    grouped_classes: Dict[Tuple[str, str], pd.DataFrame] = {}

    for (case_label, class_mode), g in pair_class_df.groupby(["case_label", "class_mode"], dropna=False):
        g2 = g.copy()
        total = float(g2["sum_contrib_primary"].sum())
        g2["normalized_class_contrib"] = 0.0 if total <= 0 else g2["sum_contrib_primary"] / total
        g2["is_top1_class"] = (g2["class_rank"] <= 1).astype(int)
        g2["is_top3_class"] = (g2["class_rank"] <= 3).astype(int)
        g2["is_top5_class"] = (g2["class_rank"] <= 5).astype(int)
        grouped_classes[(str(case_label), str(class_mode))] = g2

        for _, row in g2.iterrows():
            class_identity_rows.append(
                {
                    "run_id": row["run_id"],
                    "case_label": case_label,
                    "t": row["t"],
                    "p_family": row["p_family"],
                    "theta": row["theta"],
                    "source_feature": row["source_feature"],
                    "branch_label": row["branch_label"],
                    "class_mode": row["class_mode"],
                    "class_label": row["class_label"],
                    "class_rank": row["class_rank"],
                    "sum_contrib_primary": row["sum_contrib_primary"],
                    "normalized_class_contrib": row["normalized_class_contrib"],
                    "is_top1_class": row["is_top1_class"],
                    "is_top3_class": row["is_top3_class"],
                    "is_top5_class": row["is_top5_class"],
                }
            )

    class_identity_df = pd.DataFrame(class_identity_rows)

    # Build robust case metadata from all three inputs.
    meta_cols = ["case_label", "run_id", "branch_label"]
    meta_df = pd.concat(
        [
            pair_top_df[meta_cols],
            pair_contrib_df[meta_cols],
            pair_class_df[meta_cols],
        ],
        ignore_index=True,
    ).drop_duplicates()

    case_meta = (
        meta_df.groupby("case_label", dropna=False)
        .agg(
            run_id=("run_id", "first"),
            branch_label=("branch_label", lambda s: next((x for x in s if pd.notna(x)), None)),
        )
    )

    pair_overlap_rows: List[Dict[str, Any]] = []
    case_labels = sorted(grouped_pairs.keys())

    for i, case_a in enumerate(case_labels):
        for case_b in case_labels[i + 1:]:
            df_a = grouped_pairs[case_a]
            df_b = grouped_pairs[case_b]
            branch_a = case_meta.loc[case_a, "branch_label"] if case_a in case_meta.index else None
            branch_b = case_meta.loc[case_b, "branch_label"] if case_b in case_meta.index else None
            run_id = case_meta.loc[case_a, "run_id"] if case_a in case_meta.index else None

            for k in cfg.top_k_values:
                sa = pair_set(df_a, k)
                sb = pair_set(df_b, k)
                overlap = len(sa.intersection(sb))
                frac_a = overlap / max(1, len(sa))
                frac_b = overlap / max(1, len(sb))
                w_overlap = weighted_pair_overlap(df_a, df_b, k)
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
                        "weighted_pair_overlap": w_overlap,
                        "identity_relation": identity_relation(frac_a, frac_b),
                    }
                )

    pair_overlap_df = pd.DataFrame(pair_overlap_rows)

    class_overlap_rows: List[Dict[str, Any]] = []
    for class_mode in cfg.class_modes:
        mode_cases = sorted([case for (case, mode) in grouped_classes.keys() if mode == class_mode])
        for i, case_a in enumerate(mode_cases):
            for case_b in mode_cases[i + 1:]:
                df_a = grouped_classes[(case_a, class_mode)]
                df_b = grouped_classes[(case_b, class_mode)]
                branch_a = case_meta.loc[case_a, "branch_label"] if case_a in case_meta.index else None
                branch_b = case_meta.loc[case_b, "branch_label"] if case_b in case_meta.index else None
                run_id = case_meta.loc[case_a, "run_id"] if case_a in case_meta.index else None

                for k in cfg.top_k_values:
                    sa = class_set(df_a, k)
                    sb = class_set(df_b, k)
                    overlap = len(sa.intersection(sb))
                    frac_a = overlap / max(1, len(sa))
                    frac_b = overlap / max(1, len(sb))
                    w_overlap = weighted_class_overlap(df_a, df_b, k)
                    class_overlap_rows.append(
                        {
                            "run_id": run_id,
                            "case_label_a": case_a,
                            "case_label_b": case_b,
                            "branch_a": branch_a,
                            "branch_b": branch_b,
                            "class_mode": class_mode,
                            "top_k": k,
                            "class_overlap_count": overlap,
                            "class_overlap_fraction_a": frac_a,
                            "class_overlap_fraction_b": frac_b,
                            "weighted_class_overlap": w_overlap,
                            "identity_relation": identity_relation(frac_a, frac_b),
                        }
                    )

    class_overlap_df = pd.DataFrame(class_overlap_rows)

    branch_rows: List[Dict[str, Any]] = []
    branches = sorted([x for x in pair_top_df["branch_label"].dropna().unique().tolist()])

    for branch in branches:
        cases_in_branch = pair_top_df.loc[pair_top_df["branch_label"] == branch, "case_label"].tolist()
        if not cases_in_branch:
            continue

        within_pair = pair_overlap_df[
            (pair_overlap_df["branch_a"] == branch)
            & (pair_overlap_df["branch_b"] == branch)
            & (pair_overlap_df["top_k"] == 3)
        ]
        between_pair = pair_overlap_df[
            (
                ((pair_overlap_df["branch_a"] == branch) & (pair_overlap_df["branch_b"] != branch))
                | ((pair_overlap_df["branch_b"] == branch) & (pair_overlap_df["branch_a"] != branch))
            )
            & (pair_overlap_df["top_k"] == 3)
        ]

        top1_pairs = (
            pair_identity_df[
                (pair_identity_df["branch_label"] == branch)
                & (pair_identity_df["is_top1_pair"] == 1)
            ]
            .groupby(["pair_i", "pair_j"], dropna=False)
            .size()
            .sort_values(ascending=False)
        )

        consensus_top1_pair = None
        consensus_top1_dp = None
        consensus_top1_dp2 = None
        if not top1_pairs.empty:
            pi, pj = top1_pairs.index[0]
            consensus_top1_pair = f"({int(pi)},{int(pj)})"
            top1_row = pair_identity_df[
                (pair_identity_df["branch_label"] == branch)
                & (pair_identity_df["pair_i"] == pi)
                & (pair_identity_df["pair_j"] == pj)
            ].iloc[0]
            consensus_top1_dp = float(top1_row["delta_p"])
            consensus_top1_dp2 = float(top1_row["delta_p2"])

        class_mode_scores = (
            class_identity_df[class_identity_df["branch_label"] == branch]
            .groupby("class_mode")["normalized_class_contrib"]
            .sum()
            .sort_values(ascending=False)
        )
        dominant_class_mode = class_mode_scores.index[0] if not class_mode_scores.empty else None

        consensus_top3_classes = None
        if dominant_class_mode is not None:
            sub = class_identity_df[
                (class_identity_df["branch_label"] == branch)
                & (class_identity_df["class_mode"] == dominant_class_mode)
                & (class_identity_df["is_top3_class"] == 1)
            ]
            cls = (
                sub.groupby("class_label")["normalized_class_contrib"]
                .sum()
                .sort_values(ascending=False)
                .head(3)
                .index
                .tolist()
            )
            consensus_top3_classes = ";".join(cls)

        within_overlap = float(within_pair["weighted_pair_overlap"].mean()) if not within_pair.empty else None
        between_overlap = float(between_pair["weighted_pair_overlap"].mean()) if not between_pair.empty else None

        if within_overlap is None:
            signature_label = "single_case"
        elif between_overlap is None or within_overlap > between_overlap + 0.2:
            signature_label = "branch_specific"
        elif within_overlap > between_overlap:
            signature_label = "weakly_branch_specific"
        else:
            signature_label = "non_specific"

        branch_rows.append(
            {
                "run_id": pair_top_df["run_id"].iloc[0] if not pair_top_df.empty else None,
                "branch_label": branch,
                "n_cases": len(cases_in_branch),
                "dominant_pair_mode": "top_pair",
                "dominant_class_mode": dominant_class_mode,
                "consensus_top1_pair": consensus_top1_pair,
                "consensus_top1_delta_p": consensus_top1_dp,
                "consensus_top1_delta_p2": consensus_top1_dp2,
                "consensus_top3_classes": consensus_top3_classes,
                "within_branch_overlap": within_overlap,
                "between_branch_overlap": between_overlap,
                "signature_label": signature_label,
            }
        )

    branch_signature_df = pd.DataFrame(branch_rows)

    if not pair_overlap_df.empty:
        within_all = pair_overlap_df[
            (pair_overlap_df["branch_a"] == pair_overlap_df["branch_b"])
            & (pair_overlap_df["top_k"] == 3)
        ]
        between_all = pair_overlap_df[
            (pair_overlap_df["branch_a"] != pair_overlap_df["branch_b"])
            & (pair_overlap_df["top_k"] == 3)
        ]
        mean_within_pair_overlap = float(within_all["weighted_pair_overlap"].mean()) if not within_all.empty else None
        mean_between_pair_overlap = float(between_all["weighted_pair_overlap"].mean()) if not between_all.empty else None
    else:
        mean_within_pair_overlap = None
        mean_between_pair_overlap = None

    if not class_overlap_df.empty:
        class_mode_pref = (
            class_overlap_df.groupby("class_mode")["weighted_class_overlap"]
            .mean()
            .sort_values(ascending=False)
        )
        strongest_class_mode = class_mode_pref.index[0] if not class_mode_pref.empty else None
    else:
        strongest_class_mode = None

    if mean_within_pair_overlap is None:
        final_label = "B0"
    elif mean_between_pair_overlap is None or mean_within_pair_overlap > (mean_between_pair_overlap + 0.2):
        final_label = "B3"
    elif strongest_class_mode is not None:
        final_label = "B2"
    else:
        final_label = "B1"

    summary = {
        "n_cases": int(pair_top_df["case_label"].nunique()) if not pair_top_df.empty else 0,
        "mean_within_pair_overlap_top3": mean_within_pair_overlap,
        "mean_between_pair_overlap_top3": mean_between_pair_overlap,
        "strongest_class_mode": strongest_class_mode,
        "final_label": final_label,
    }

    pair_identity_df.to_csv(out_root / "pair_identity_comparison.csv", index=False)
    pair_overlap_df.to_csv(out_root / "pair_overlap_summary.csv", index=False)
    class_identity_df.to_csv(out_root / "class_identity_comparison.csv", index=False)
    class_overlap_df.to_csv(out_root / "class_overlap_summary.csv", index=False)
    branch_signature_df.to_csv(out_root / "branch_identity_signature.csv", index=False)
    write_json(out_root / "pair_identity_summary.json", summary)

    report_lines = [
        "# M.3.6b Pair Identity Report",
        "",
        f"- n_cases: {safe_json_value(summary['n_cases'])}",
        f"- mean_within_pair_overlap_top3: {safe_json_value(summary['mean_within_pair_overlap_top3'])}",
        f"- mean_between_pair_overlap_top3: {safe_json_value(summary['mean_between_pair_overlap_top3'])}",
        f"- strongest_class_mode: {safe_json_value(summary['strongest_class_mode'])}",
        f"- final_label: {safe_json_value(summary['final_label'])}",
    ]
    (out_root / "pair_identity_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.6b completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
