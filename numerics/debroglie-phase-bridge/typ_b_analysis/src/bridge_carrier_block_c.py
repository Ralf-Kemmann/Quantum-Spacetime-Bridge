from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml


@dataclass
class BootstrapConfig:
    enabled: bool
    n_bootstrap: int
    sample_fraction: float


@dataclass
class ThresholdConfig:
    assignment_pass_min: float
    stability_pass_min: float
    near_sufficient_margin_ratio: float
    near_sufficient_assignment_ratio: float
    near_sufficient_stability_ratio: float


@dataclass
class EvaluationConfig:
    bootstrap: BootstrapConfig
    thresholds: ThresholdConfig


@dataclass
class VariantConfig:
    name: str
    active_features: List[str]


@dataclass
class Config:
    run_id: str
    source_run_id: str
    mode: str
    random_seed: int
    input_csv: Path
    results_dir: Path
    columns: Dict[str, str]
    core_features: List[str]
    variants: List[VariantConfig]
    evaluation: EvaluationConfig
    outputs: Dict[str, Any]


def load_config(path: str | Path) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    bootstrap = BootstrapConfig(**raw["evaluation"]["bootstrap"])
    thresholds = ThresholdConfig(**raw["evaluation"]["thresholds"])
    evaluation = EvaluationConfig(bootstrap=bootstrap, thresholds=thresholds)
    variants = [VariantConfig(**v) for v in raw["variants"]]
    return Config(
        run_id=raw["run_id"],
        source_run_id=raw["source_run_id"],
        mode=raw["mode"],
        random_seed=raw.get("random_seed", 42),
        input_csv=Path(raw["data"]["input_csv"]),
        results_dir=Path(raw["data"]["results_dir"]),
        columns=raw["columns"],
        core_features=raw["core_features"],
        variants=variants,
        evaluation=evaluation,
        outputs=raw["outputs"],
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_float(value: Any):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def mean_or_none(series: pd.Series):
    if series.empty:
        return None
    return safe_float(series.mean())


def validate_dataset(df: pd.DataFrame, cfg: Config) -> None:
    required_cols = [
        cfg.columns["sample_id"],
        cfg.columns["group_label"],
        cfg.columns["dataset_role"],
        cfg.columns["source_family"],
        cfg.columns["split_label"],
        *cfg.core_features,
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if df.empty:
        raise ValueError("Input dataset is empty.")


def run_current_bridge_evaluation(dataset: pd.DataFrame, active_features: List[str], cfg: Config) -> Dict[str, Any]:
    working = dataset.copy()
    dataset_role_col = cfg.columns["dataset_role"]

    original_mask = working[dataset_role_col].astype(str).str.lower().eq("original")
    control_mask = working[dataset_role_col].astype(str).str.lower().eq("control")

    original_df = working.loc[original_mask].copy()
    control_df = working.loc[control_mask].copy()

    if original_df.empty or control_df.empty or not active_features:
        return {
            "overall_pass": False,
            "result_label": "failed",
            "separation_margin_mean": None,
            "assignment_score": None,
            "original_stability_score": None,
            "original_vs_control_margin_delta": None,
            "type_B_like_pattern_detected": False,
            "positive_bootstrap_fraction": None,
            "n_active_features": len(active_features),
            "active_features": active_features,
        }

    feature_stats = {}
    for feat in active_features:
        col = pd.to_numeric(original_df[feat], errors="coerce")
        q25 = col.quantile(0.25)
        q50 = col.quantile(0.50)
        q75 = col.quantile(0.75)
        iqr = q75 - q25
        if pd.isna(iqr) or iqr == 0:
            iqr = max(col.std(ddof=0), 1e-9)
        feature_stats[feat] = {"q50": float(q50), "iqr": float(iqr)}

    def corridor_distance(row: pd.Series) -> float:
        distances = []
        for feat in active_features:
            x = pd.to_numeric(pd.Series([row[feat]]), errors="coerce").iloc[0]
            center = feature_stats[feat]["q50"]
            scale = feature_stats[feat]["iqr"] if feature_stats[feat]["iqr"] != 0 else 1e-9
            distances.append(abs(float(x) - center) / scale)
        return float(sum(distances) / len(distances)) if distances else 0.0

    working["_corridor_distance"] = working.apply(corridor_distance, axis=1)
    working["_bridge_score"] = -working["_corridor_distance"]

    original_scores = working.loc[original_mask, "_bridge_score"]
    control_scores = working.loc[control_mask, "_bridge_score"]

    original_mean = mean_or_none(original_scores)
    control_mean = mean_or_none(control_scores)
    separation_margin_mean = None if original_mean is None or control_mean is None else original_mean - control_mean

    assignment_score = None
    if len(original_scores) > 0 and len(control_scores) > 0:
        control_threshold = float(control_scores.median())
        original_hit_rate = float((original_scores > control_threshold).mean())
        original_threshold = float(original_scores.median())
        control_reject_rate = float((control_scores < original_threshold).mean())
        assignment_score = 0.5 * (original_hit_rate + control_reject_rate)

    original_vs_control_margin_delta = separation_margin_mean
    type_B_like_pattern_detected = bool(
        separation_margin_mean is not None and assignment_score is not None
        and separation_margin_mean > 0 and assignment_score >= cfg.evaluation.thresholds.assignment_pass_min
    )

    original_stability_score = None
    positive_bootstrap_fraction = None
    if cfg.evaluation.bootstrap.enabled:
        fractions = []
        n = cfg.evaluation.bootstrap.n_bootstrap
        frac = cfg.evaluation.bootstrap.sample_fraction
        for i in range(n):
            boot_orig = original_df.sample(frac=frac, replace=True, random_state=cfg.random_seed + i)
            boot_ctrl = control_df.sample(frac=frac, replace=True, random_state=cfg.random_seed + 10000 + i)
            boot = pd.concat([boot_orig, boot_ctrl], ignore_index=True)
            boot_original_mask = boot[dataset_role_col].astype(str).str.lower().eq("original")
            boot_control_mask = boot[dataset_role_col].astype(str).str.lower().eq("control")

            boot_feature_stats = {}
            for feat in active_features:
                col = pd.to_numeric(boot.loc[boot_original_mask, feat], errors="coerce")
                q25 = col.quantile(0.25)
                q50 = col.quantile(0.50)
                q75 = col.quantile(0.75)
                iqr = q75 - q25
                if pd.isna(iqr) or iqr == 0:
                    iqr = max(col.std(ddof=0), 1e-9)
                boot_feature_stats[feat] = {"q50": float(q50), "iqr": float(iqr)}

            def boot_distance(row: pd.Series) -> float:
                distances = []
                for feat in active_features:
                    x = pd.to_numeric(pd.Series([row[feat]]), errors="coerce").iloc[0]
                    center = boot_feature_stats[feat]["q50"]
                    scale = boot_feature_stats[feat]["iqr"] if boot_feature_stats[feat]["iqr"] != 0 else 1e-9
                    distances.append(abs(float(x) - center) / scale)
                return float(sum(distances) / len(distances)) if distances else 0.0

            boot["_corridor_distance"] = boot.apply(boot_distance, axis=1)
            boot["_bridge_score"] = -boot["_corridor_distance"]
            boot_original_scores = boot.loc[boot_original_mask, "_bridge_score"]
            boot_control_scores = boot.loc[boot_control_mask, "_bridge_score"]
            if len(boot_original_scores) == 0 or len(boot_control_scores) == 0:
                continue
            boot_margin = float(boot_original_scores.mean() - boot_control_scores.mean())
            boot_control_threshold = float(boot_control_scores.median())
            boot_original_hit_rate = float((boot_original_scores > boot_control_threshold).mean())
            boot_original_threshold = float(boot_original_scores.median())
            boot_control_reject_rate = float((boot_control_scores < boot_original_threshold).mean())
            boot_assignment = 0.5 * (boot_original_hit_rate + boot_control_reject_rate)
            fractions.append(float(boot_margin > 0 and boot_assignment >= cfg.evaluation.thresholds.assignment_pass_min))
        if fractions:
            positive_bootstrap_fraction = safe_float(sum(fractions) / len(fractions))
            original_stability_score = positive_bootstrap_fraction

    overall_pass = bool(
        separation_margin_mean is not None and assignment_score is not None and original_stability_score is not None
        and separation_margin_mean > 0
        and assignment_score >= cfg.evaluation.thresholds.assignment_pass_min
        and original_stability_score >= cfg.evaluation.thresholds.stability_pass_min
    )
    if overall_pass:
        result_label = "supported"
    elif type_B_like_pattern_detected:
        result_label = "weak"
    else:
        result_label = "failed"

    return {
        "overall_pass": overall_pass,
        "result_label": result_label,
        "separation_margin_mean": separation_margin_mean,
        "assignment_score": assignment_score,
        "original_stability_score": original_stability_score,
        "original_vs_control_margin_delta": original_vs_control_margin_delta,
        "type_B_like_pattern_detected": type_B_like_pattern_detected,
        "positive_bootstrap_fraction": positive_bootstrap_fraction,
        "n_active_features": len(active_features),
        "active_features": active_features,
    }


def compute_degradation(current: Dict[str, Any], full: Dict[str, Any]) -> Dict[str, Any]:
    def diff(key: str):
        cur = safe_float(current.get(key))
        ref = safe_float(full.get(key))
        if cur is None or ref is None:
            return None
        return cur - ref
    return {
        "delta_separation_margin_mean": diff("separation_margin_mean"),
        "delta_assignment_score": diff("assignment_score"),
        "delta_original_stability_score": diff("original_stability_score"),
        "pass_changed": current.get("overall_pass") != full.get("overall_pass"),
        "label_changed": current.get("result_label") != full.get("result_label"),
    }


def classify_set_signal(metrics: Dict[str, Any], full_metrics: Dict[str, Any], cfg: Config) -> str:
    if metrics.get("active_features") == full_metrics.get("active_features"):
        return "baseline"
    if metrics.get("overall_pass"):
        if len(metrics.get("active_features", [])) == 1:
            return "candidate_single_anchor"
        margin = safe_float(metrics.get("separation_margin_mean"))
        assign = safe_float(metrics.get("assignment_score"))
        stab = safe_float(metrics.get("original_stability_score"))
        full_margin = safe_float(full_metrics.get("separation_margin_mean"))
        full_assign = safe_float(full_metrics.get("assignment_score"))
        full_stab = safe_float(full_metrics.get("original_stability_score"))
        if all(v is not None for v in [margin, assign, stab, full_margin, full_assign, full_stab]):
            if (
                margin >= cfg.evaluation.thresholds.near_sufficient_margin_ratio * full_margin
                and assign >= cfg.evaluation.thresholds.near_sufficient_assignment_ratio * full_assign
                and stab >= cfg.evaluation.thresholds.near_sufficient_stability_ratio * full_stab
            ):
                return "candidate_near_full_core"
        return "candidate_sufficient_reduced_set"
    if metrics.get("type_B_like_pattern_detected"):
        return "weak_or_partial_set"
    return "insufficient_under_current_logic"


def to_serializable(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def write_variant_json(results_dir: Path, variant_name: str, payload: Dict[str, Any]) -> None:
    out_dir = results_dir / "variant_reports"
    ensure_dir(out_dir)
    with open(out_dir / f"{variant_name}.json", "w", encoding="utf-8") as f:
        json.dump(to_serializable(payload), f, indent=2, ensure_ascii=False)


def write_results_csv(results_dir: Path, rows: List[Dict[str, Any]]) -> None:
    pd.DataFrame(rows).to_csv(results_dir / "bridge_carrier_block_c.csv", index=False)


def write_summary_json(results_dir: Path, summary: Dict[str, Any]) -> None:
    with open(results_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(to_serializable(summary), f, indent=2, ensure_ascii=False)


def write_markdown_summary(results_dir: Path, rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# BRIDGE_CARRIER_BLOCK_C_RESULTS — singles and triples",
        "",
        "## Purpose",
        "Test singleton anchors and triple sets after block B minimal-pair findings.",
        "",
        "## Summary table",
        "",
        "| variant | feature_count | overall_pass | result_label | separation_margin_mean | assignment_score | original_stability_score | provisional_set_signal |",
        "|---|---:|---:|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant']} | {row['feature_count']} | {row['overall_pass']} | {row['result_label']} | {row['separation_margin_mean']} | {row['assignment_score']} | {row['original_stability_score']} | {row['provisional_set_signal']} |"
        )
    with open(results_dir / "BRIDGE_CARRIER_BLOCK_C_RESULTS.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_block_c(cfg: Config) -> Dict[str, Any]:
    ensure_dir(cfg.results_dir)
    df = pd.read_csv(cfg.input_csv)
    validate_dataset(df, cfg)
    results = []
    for variant in cfg.variants:
        metrics = run_current_bridge_evaluation(df, variant.active_features, cfg)
        row = {
            "variant": variant.name,
            "feature_count": len(variant.active_features),
            **metrics,
        }
        results.append(row)
        if cfg.outputs.get("write_variant_json", False):
            write_variant_json(cfg.results_dir, variant.name, row)
    full_row = next((r for r in results if r["variant"] == "full"), None)
    if full_row is None:
        raise RuntimeError("No 'full' variant found.")
    summary_rows = []
    for row in results:
        summary_row = {
            **row,
            **compute_degradation(row, full_row),
            "provisional_set_signal": classify_set_signal(row, full_row, cfg),
        }
        summary_rows.append(summary_row)
    if cfg.outputs.get("write_csv", False):
        write_results_csv(cfg.results_dir, summary_rows)
    summary = {
        "run_id": cfg.run_id,
        "source_run_id": cfg.source_run_id,
        "mode": cfg.mode,
        "base_variant": "full",
        "variants_tested": len(cfg.variants),
        "core_features": cfg.core_features,
        "results": summary_rows,
        "interpretation_rule": {
            "candidate_single_anchor": "single feature still passes",
            "candidate_near_full_core": "reduced set remains close to full",
            "candidate_sufficient_reduced_set": "reduced set still passes",
            "weak_or_partial_set": "reduced set retains only partial signal",
            "insufficient_under_current_logic": "reduced set fails to preserve current bridge logic",
        },
    }
    if cfg.outputs.get("write_json", False):
        write_summary_json(cfg.results_dir, summary)
    if cfg.outputs.get("write_markdown", False):
        write_markdown_summary(cfg.results_dir, summary_rows)
    return summary


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Bridge carrier block C runner")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    summary = run_block_c(cfg)
    print(json.dumps(to_serializable(summary), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
