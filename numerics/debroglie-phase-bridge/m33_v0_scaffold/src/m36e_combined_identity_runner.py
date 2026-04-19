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
class M36eConfig:
    enabled: bool
    combined_pair_contributions: Path
    combined_pair_top_summary: Path
    combined_pair_class_summary: Path
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


def load_config(path: Path) -> M36eConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m36e_combined_identity"]
    return M36eConfig(
        enabled=bool(block["enabled"]),
        combined_pair_contributions=Path(block["input"]["combined_pair_contributions"]),
        combined_pair_top_summary=Path(block["input"]["combined_pair_top_summary"]),
        combined_pair_class_summary=Path(block["input"]["combined_pair_class_summary"]),
        top_k_values=[int(x) for x in block["comparison"]["top_k_values"]],
        class_modes=[str(x) for x in block["comparison"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )


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


def mean_or_none(s: pd.Series) -> float | None:
    return None if s.empty else float(s.mean())


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.6e combined branch identity audit")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.6e disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    pair_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_contributions)))
    top_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_top_summary)))
    class_df = attach_case_label(pd.read_csv(resolve_path(project_root, cfg.combined_pair_class_summary)))

    # Normalize / canonize branch labels
    if "branch_label" not in pair_df.columns:
        pair_df["branch_label"] = None
    if "branch_label" not in top_df.columns:
        top_df["branch_label"] = None
    if "branch_label" not in class_df.columns:
        class_df["branch_label"] = None

    # Fill missing branch_label from branch_pref_readout if needed
    for df in (pair_df, top_df, class_df):
        if "branch_pref_readout" in df.columns:
            df["branch_label"] = df["branch_label"].where(df["branch_label"].notna(), df["branch_pref_readout"])

    # Pair-level normalized contributions
    if "normalized_contrib_primary" not in pair_df.columns:
        totals = pair_df.groupby("case_label")["contrib_primary"].transform("sum")
        pair_df["normalized_contrib_primary"] = np.where(
            totals > 0,
            pair_df["contrib_primary"] / totals,
            0.0,
        )

    # Class-level normalized contributions
    if "normalized_class_contrib" not in class_df.columns:
        totals = class_df.groupby(["case_label", "class_mode"])["sum_contrib_primary"].transform("sum")
        class_df["normalized_class_contrib"] = np.where(
            totals > 0,
            class_df["sum_contrib_primary"] / totals,
            0.0,
        )

    # Basic meta table
    meta_cols = ["case_label", "run_id", "branch_label", "t", "p_family", "theta"]
    meta_df = pd.concat(
        [
            top_df[[c for c in meta_cols if c in top_df.columns]],
            pair_df[[c for c in meta_cols if c in pair_df.columns]],
            class_df[[c for c in meta_cols if c in class_df.columns]],
        ],
        ignore_index=True,
    ).drop_duplicates()

    meta_df = (
        meta_df.groupby("case_label", dropna=False)
        .agg(
            run_id=("run_id", "first"),
            branch_label=("branch_label", lambda s: next((x for x in s if pd.notna(x)), None)),
            t=("t", "first"),
            p_family=("p_family", "first"),
            theta=("theta", "first"),
        )
        .reset_index()
    )

    # Pair overlap table
    pair_overlap_rows: List[Dict[str, Any]] = []
    grouped_pairs = {case: g.copy() for case, g in pair_df.groupby("case_label", dropna=False)}
    case_labels = sorted(grouped_pairs.keys())

    meta_index = meta_df.set_index("case_label")

    for i, case_a in enumerate(case_labels):
        for case_b in case_labels[i + 1:]:
            df_a = grouped_pairs[case_a]
            df_b = grouped_pairs[case_b]
            branch_a = meta_index.loc[case_a, "branch_label"] if case_a in meta_index.index else None
            branch_b = meta_index.loc[case_b, "branch_label"] if case_b in meta_index.index else None
            rel = "within_branch" if pd.notna(branch_a) and pd.notna(branch_b) and branch_a == branch_b else "between_branch"
            run_id = meta_index.loc[case_a, "run_id"] if case_a in meta_index.index else None

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

    pair_overlap_df = pd.DataFrame(pair_overlap_rows)

    # Class overlap table
    class_overlap_rows: List[Dict[str, Any]] = []
    grouped_classes = {(case, mode): g.copy() for (case, mode), g in class_df.groupby(["case_label", "class_mode"], dropna=False)}

    for mode in cfg.class_modes:
        mode_cases = sorted([case for (case, m) in grouped_classes.keys() if m == mode])
        for i, case_a in enumerate(mode_cases):
            for case_b in mode_cases[i + 1:]:
                df_a = grouped_classes[(case_a, mode)]
                df_b = grouped_classes[(case_b, mode)]
                branch_a = meta_index.loc[case_a, "branch_label"] if case_a in meta_index.index else None
                branch_b = meta_index.loc[case_b, "branch_label"] if case_b in meta_index.index else None
                rel = "within_branch" if pd.notna(branch_a) and pd.notna(branch_b) and branch_a == branch_b else "between_branch"
                run_id = meta_index.loc[case_a, "run_id"] if case_a in meta_index.index else None

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

    class_overlap_df = pd.DataFrame(class_overlap_rows)

    # Branch identity summary
    summary_rows: List[Dict[str, Any]] = []
    branches = sorted([b for b in meta_df["branch_label"].dropna().unique().tolist()])

    def consensus_top1_pair_for_branch(branch: str) -> tuple[str | None, float | None, float | None]:
        sub = pair_df[pair_df["branch_label"] == branch].copy()
        if sub.empty:
            return None, None, None
        top1 = (
            sub[sub["pair_rank_primary"] <= 1]
            .groupby(["pair_i", "pair_j"], dropna=False)
            .size()
            .sort_values(ascending=False)
        )
        if top1.empty:
            return None, None, None
        pi, pj = top1.index[0]
        row = sub[(sub["pair_i"] == pi) & (sub["pair_j"] == pj)].iloc[0]
        return f"({int(pi)},{int(pj)})", float(row["delta_p"]), float(row["delta_p2"])

    def consensus_top3_classes_for_branch(branch: str, mode: str) -> str | None:
        sub = class_df[
            (class_df["branch_label"] == branch)
            & (class_df["class_mode"] == mode)
            & (class_df["class_rank"] <= 3)
        ].copy()
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

    for branch in branches:
        cases_in_branch = meta_df.loc[meta_df["branch_label"] == branch, "case_label"].tolist()

        pair_within = pair_overlap_df[
            (pair_overlap_df["relation_type"] == "within_branch")
            & (pair_overlap_df["branch_a"] == branch)
            & (pair_overlap_df["top_k"] == 3)
        ]["weighted_pair_overlap"]
        pair_between = pair_overlap_df[
            (pair_overlap_df["relation_type"] == "between_branch")
            & (
                (pair_overlap_df["branch_a"] == branch)
                | (pair_overlap_df["branch_b"] == branch)
            )
            & (pair_overlap_df["top_k"] == 3)
        ]["weighted_pair_overlap"]

        dp_within = class_overlap_df[
            (class_overlap_df["relation_type"] == "within_branch")
            & (class_overlap_df["branch_a"] == branch)
            & (class_overlap_df["class_mode"] == "delta_p")
            & (class_overlap_df["top_k"] == 3)
        ]["weighted_class_overlap"]
        dp_between = class_overlap_df[
            (class_overlap_df["relation_type"] == "between_branch")
            & (
                (class_overlap_df["branch_a"] == branch)
                | (class_overlap_df["branch_b"] == branch)
            )
            & (class_overlap_df["class_mode"] == "delta_p")
            & (class_overlap_df["top_k"] == 3)
        ]["weighted_class_overlap"]

        dp2_within = class_overlap_df[
            (class_overlap_df["relation_type"] == "within_branch")
            & (class_overlap_df["branch_a"] == branch)
            & (class_overlap_df["class_mode"] == "delta_p2")
            & (class_overlap_df["top_k"] == 3)
        ]["weighted_class_overlap"]
        dp2_between = class_overlap_df[
            (class_overlap_df["relation_type"] == "between_branch")
            & (
                (class_overlap_df["branch_a"] == branch)
                | (class_overlap_df["branch_b"] == branch)
            )
            & (class_overlap_df["class_mode"] == "delta_p2")
            & (class_overlap_df["top_k"] == 3)
        ]["weighted_class_overlap"]

        pair_within_mean = mean_or_none(pair_within)
        pair_between_mean = mean_or_none(pair_between)
        dp_within_mean = mean_or_none(dp_within)
        dp_between_mean = mean_or_none(dp_between)
        dp2_within_mean = mean_or_none(dp2_within)
        dp2_between_mean = mean_or_none(dp2_between)

        pair_sep = None if pair_within_mean is None or pair_between_mean is None else pair_within_mean - pair_between_mean
        dp_sep = None if dp_within_mean is None or dp_between_mean is None else dp_within_mean - dp_between_mean
        dp2_sep = None if dp2_within_mean is None or dp2_between_mean is None else dp2_within_mean - dp2_between_mean

        consensus_pair, consensus_dp, consensus_dp2 = consensus_top1_pair_for_branch(branch)
        consensus_dp_classes = consensus_top3_classes_for_branch(branch, "delta_p")
        consensus_dp2_classes = consensus_top3_classes_for_branch(branch, "delta_p2")

        if pair_sep is not None and pair_sep > 0.2:
            signature = "pair_specific"
        elif (dp_sep is not None and dp_sep > 0.05) or (dp2_sep is not None and dp2_sep > 0.05):
            signature = "class_specific"
        elif len(cases_in_branch) == 1:
            signature = "single_case"
        else:
            signature = "weak_or_none"

        summary_rows.append(
            {
                "run_id": meta_df["run_id"].iloc[0] if not meta_df.empty else None,
                "branch_label": branch,
                "n_cases": len(cases_in_branch),
                "mean_within_pair_overlap_top3": pair_within_mean,
                "mean_between_pair_overlap_top3": pair_between_mean,
                "mean_within_class_overlap_top3_delta_p": dp_within_mean,
                "mean_between_class_overlap_top3_delta_p": dp_between_mean,
                "mean_within_class_overlap_top3_delta_p2": dp2_within_mean,
                "mean_between_class_overlap_top3_delta_p2": dp2_between_mean,
                "pair_separability_score": pair_sep,
                "delta_p_separability_score": dp_sep,
                "delta_p2_separability_score": dp2_sep,
                "consensus_top1_pair": consensus_pair,
                "consensus_top1_delta_p": consensus_dp,
                "consensus_top1_delta_p2": consensus_dp2,
                "consensus_top3_classes_delta_p": consensus_dp_classes,
                "consensus_top3_classes_delta_p2": consensus_dp2_classes,
                "signature_label": signature,
            }
        )

    branch_identity_summary_df = pd.DataFrame(summary_rows)

    # Global summary
    pair_within = pair_overlap_df[
        (pair_overlap_df["relation_type"] == "within_branch")
        & (pair_overlap_df["top_k"] == 3)
    ]["weighted_pair_overlap"]
    pair_between = pair_overlap_df[
        (pair_overlap_df["relation_type"] == "between_branch")
        & (pair_overlap_df["top_k"] == 3)
    ]["weighted_pair_overlap"]

    dp_within = class_overlap_df[
        (class_overlap_df["relation_type"] == "within_branch")
        & (class_overlap_df["class_mode"] == "delta_p")
        & (class_overlap_df["top_k"] == 3)
    ]["weighted_class_overlap"]
    dp_between = class_overlap_df[
        (class_overlap_df["relation_type"] == "between_branch")
        & (class_overlap_df["class_mode"] == "delta_p")
        & (class_overlap_df["top_k"] == 3)
    ]["weighted_class_overlap"]

    dp2_within = class_overlap_df[
        (class_overlap_df["relation_type"] == "within_branch")
        & (class_overlap_df["class_mode"] == "delta_p2")
        & (class_overlap_df["top_k"] == 3)
    ]["weighted_class_overlap"]
    dp2_between = class_overlap_df[
        (class_overlap_df["relation_type"] == "between_branch")
        & (class_overlap_df["class_mode"] == "delta_p2")
        & (class_overlap_df["top_k"] == 3)
    ]["weighted_class_overlap"]

    pair_within_mean = mean_or_none(pair_within)
    pair_between_mean = mean_or_none(pair_between)
    dp_within_mean = mean_or_none(dp_within)
    dp_between_mean = mean_or_none(dp_between)
    dp2_within_mean = mean_or_none(dp2_within)
    dp2_between_mean = mean_or_none(dp2_between)

    pair_sep = None if pair_within_mean is None or pair_between_mean is None else pair_within_mean - pair_between_mean
    dp_sep = None if dp_within_mean is None or dp_between_mean is None else dp_within_mean - dp_between_mean
    dp2_sep = None if dp2_within_mean is None or dp2_between_mean is None else dp2_within_mean - dp2_between_mean

    dominant_identity_level = None
    sep_scores = {
        "pair": pair_sep if pair_sep is not None else -np.inf,
        "delta_p_class": dp_sep if dp_sep is not None else -np.inf,
        "delta_p2_class": dp2_sep if dp2_sep is not None else -np.inf,
    }
    best_key = max(sep_scores, key=sep_scores.get)
    if sep_scores[best_key] != -np.inf:
        dominant_identity_level = best_key

    if pair_sep is not None and pair_sep > 0.2:
        final_label = "E3"
    elif (dp_sep is not None and dp_sep > 0.05) or (dp2_sep is not None and dp2_sep > 0.05):
        final_label = "E2"
    elif meta_df["branch_label"].nunique() >= 3 if not meta_df.empty else False:
        final_label = "E1"
    else:
        final_label = "E0"

    global_summary = {
        "n_cases_total": int(meta_df["case_label"].nunique()) if not meta_df.empty else 0,
        "n_branches_total": int(meta_df["branch_label"].nunique()) if not meta_df.empty else 0,
        "pair_within_overlap_top3": pair_within_mean,
        "pair_between_overlap_top3": pair_between_mean,
        "delta_p_within_overlap_top3": dp_within_mean,
        "delta_p_between_overlap_top3": dp_between_mean,
        "delta_p2_within_overlap_top3": dp2_within_mean,
        "delta_p2_between_overlap_top3": dp2_between_mean,
        "pair_separability_score": pair_sep,
        "delta_p_separability_score": dp_sep,
        "delta_p2_separability_score": dp2_sep,
        "dominant_identity_level": dominant_identity_level,
        "final_label": final_label,
    }

    pair_overlap_df.to_csv(out_root / "combined_pair_overlap.csv", index=False)
    class_overlap_df.to_csv(out_root / "combined_class_overlap.csv", index=False)
    branch_identity_summary_df.to_csv(out_root / "branch_identity_summary.csv", index=False)
    write_json(out_root / "global_identity_summary.json", global_summary)

    report_lines = [
        "# M.3.6e Combined Branch Identity Audit",
        "",
        f"- n_cases_total: {safe_json_value(global_summary['n_cases_total'])}",
        f"- n_branches_total: {safe_json_value(global_summary['n_branches_total'])}",
        f"- pair_within_overlap_top3: {safe_json_value(global_summary['pair_within_overlap_top3'])}",
        f"- pair_between_overlap_top3: {safe_json_value(global_summary['pair_between_overlap_top3'])}",
        f"- delta_p_within_overlap_top3: {safe_json_value(global_summary['delta_p_within_overlap_top3'])}",
        f"- delta_p_between_overlap_top3: {safe_json_value(global_summary['delta_p_between_overlap_top3'])}",
        f"- delta_p2_within_overlap_top3: {safe_json_value(global_summary['delta_p2_within_overlap_top3'])}",
        f"- delta_p2_between_overlap_top3: {safe_json_value(global_summary['delta_p2_between_overlap_top3'])}",
        f"- dominant_identity_level: {safe_json_value(global_summary['dominant_identity_level'])}",
        f"- final_label: {safe_json_value(global_summary['final_label'])}",
    ]
    (out_root / "global_identity_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.6e completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
