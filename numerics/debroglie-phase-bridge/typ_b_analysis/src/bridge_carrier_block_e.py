from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml


@dataclass
class BootstrapConfig:
    enabled: bool
    n_bootstrap: int
    sample_fraction: float


@dataclass
class ThresholdConfig:
    assignment_min: float
    stability_min: float


@dataclass
class H2Config:
    use_internal_controls_as_fallback: bool
    substitute_rigidity_proxy: bool
    rigidity_proxy_column: str
    rigidity_proxy_flag_column: str


@dataclass
class EvaluationConfig:
    bootstrap: BootstrapConfig
    thresholds: ThresholdConfig
    h2: H2Config


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
    internal_original_csv: Path
    internal_control_csv: Path
    h2_features_csv: Path
    results_dir: Path
    columns: Dict[str, Dict[str, str]]
    core_features: List[str]
    variants: List[VariantConfig]
    evaluation: EvaluationConfig
    outputs: Dict[str, Any]


def load_config(path: str | Path) -> Config:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    bootstrap = BootstrapConfig(**raw["evaluation"]["bootstrap"])
    thresholds = ThresholdConfig(**raw["evaluation"]["thresholds"])
    h2 = H2Config(**raw["evaluation"]["h2"])
    evaluation = EvaluationConfig(bootstrap=bootstrap, thresholds=thresholds, h2=h2)
    variants = [VariantConfig(**v) for v in raw["variants"]]

    return Config(
        run_id=raw["run_id"],
        source_run_id=raw["source_run_id"],
        mode=raw["mode"],
        random_seed=raw.get("random_seed", 42),
        internal_original_csv=Path(raw["data"]["internal_original_csv"]),
        internal_control_csv=Path(raw["data"]["internal_control_csv"]),
        h2_features_csv=Path(raw["data"]["h2_features_csv"]),
        results_dir=Path(raw["data"]["results_dir"]),
        columns=raw["columns"],
        core_features=raw["core_features"],
        variants=variants,
        evaluation=evaluation,
        outputs=raw["outputs"],
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_float(value: Any) -> Optional[float]:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def mean_or_none(series: pd.Series) -> Optional[float]:
    if series.empty:
        return None
    return safe_float(series.mean())


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


def prepare_internal_original(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    out = df.rename(columns={
        cfg.columns["internal_original"]["sample_id"]: "sample_id",
        cfg.columns["internal_original"]["group_label"]: "group_label",
    }).copy()
    out["dataset_role"] = "original"
    out["source_family"] = out["group_label"]
    out["split_label"] = "inherited_eval"
    return out


def prepare_internal_control(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    out = df.rename(columns={
        cfg.columns["internal_control"]["sample_id"]: "sample_id",
        cfg.columns["internal_control"]["group_label"]: "group_label",
    }).copy()
    out["dataset_role"] = "control"
    out["source_family"] = out["group_label"]
    out["split_label"] = "inherited_eval"
    return out


def prepare_h2(df: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    out = df.rename(columns={
        cfg.columns["h2"]["sample_id"]: "sample_id",
        cfg.columns["h2"]["group_label"]: "group_label",
    }).copy()
    out["dataset_role"] = "h2"
    out["source_family"] = out.get("family_id", "H2")
    out["split_label"] = out.get("mapping_mode", "h2")
    return out


def apply_h2_proxy_substitution(h2_df: pd.DataFrame, active_features: List[str], cfg: Config) -> pd.DataFrame:
    out = h2_df.copy()
    if (
        "simple_rigidity_surrogate" in active_features
        and cfg.evaluation.h2.substitute_rigidity_proxy
        and cfg.evaluation.h2.rigidity_proxy_column in out.columns
        and cfg.evaluation.h2.rigidity_proxy_flag_column in out.columns
    ):
        target_missing = out["simple_rigidity_surrogate"].isna() if "simple_rigidity_surrogate" in out.columns else pd.Series([True] * len(out), index=out.index)
        proxy_allowed = out[cfg.evaluation.h2.rigidity_proxy_flag_column].fillna(False).astype(bool)
        proxy_available = out[cfg.evaluation.h2.rigidity_proxy_column].notna()
        use_proxy = target_missing & proxy_allowed & proxy_available
        if "simple_rigidity_surrogate" not in out.columns:
            out["simple_rigidity_surrogate"] = pd.NA
        out.loc[use_proxy, "simple_rigidity_surrogate"] = out.loc[use_proxy, cfg.evaluation.h2.rigidity_proxy_column]
        out["proxy_rigidity_substituted"] = use_proxy.astype(int)
    else:
        out["proxy_rigidity_substituted"] = 0
    return out


def compute_feature_stats(reference_df: pd.DataFrame, active_features: List[str]) -> Dict[str, Dict[str, float]]:
    feature_stats: Dict[str, Dict[str, float]] = {}
    for feat in active_features:
        col = pd.to_numeric(reference_df[feat], errors="coerce")
        col = col.dropna()
        if col.empty:
            feature_stats[feat] = {"q50": 0.0, "iqr": 1.0}
            continue
        q25 = col.quantile(0.25)
        q50 = col.quantile(0.50)
        q75 = col.quantile(0.75)
        iqr = q75 - q25
        if pd.isna(iqr) or iqr == 0:
            iqr = max(col.std(ddof=0), 1e-9)
        feature_stats[feat] = {"q50": float(q50), "iqr": float(iqr)}
    return feature_stats


def corridor_distance(row: pd.Series, active_features: List[str], feature_stats: Dict[str, Dict[str, float]]) -> float:
    distances = []
    for feat in active_features:
        x = pd.to_numeric(pd.Series([row.get(feat)]), errors="coerce").iloc[0]
        if pd.isna(x):
            return float("nan")
        center = feature_stats[feat]["q50"]
        scale = feature_stats[feat]["iqr"] if feature_stats[feat]["iqr"] != 0 else 1e-9
        distances.append(abs(float(x) - center) / scale)
    return float(sum(distances) / len(distances)) if distances else 0.0


def evaluate_two_group(
    reference_original: pd.DataFrame,
    target_group: pd.DataFrame,
    control_group: pd.DataFrame,
    active_features: List[str],
    cfg: Config,
) -> Dict[str, Any]:
    ref = reference_original.copy()
    tgt = target_group.copy()
    ctl = control_group.copy()

    for feat in active_features:
        if feat not in ref.columns or feat not in tgt.columns or feat not in ctl.columns:
            return {
                "overall_pass": False,
                "result_label": "failed",
                "separation_margin_mean": None,
                "assignment_score": 0.0,
                "original_stability_score": 0.0,
            }

    feature_stats = compute_feature_stats(ref, active_features)

    tgt = tgt.copy()
    ctl = ctl.copy()
    tgt["_corridor_distance"] = tgt.apply(lambda r: corridor_distance(r, active_features, feature_stats), axis=1)
    ctl["_corridor_distance"] = ctl.apply(lambda r: corridor_distance(r, active_features, feature_stats), axis=1)
    tgt = tgt.dropna(subset=["_corridor_distance"])
    ctl = ctl.dropna(subset=["_corridor_distance"])

    if tgt.empty or ctl.empty:
        return {
            "overall_pass": False,
            "result_label": "failed",
            "separation_margin_mean": None,
            "assignment_score": 0.0,
            "original_stability_score": 0.0,
        }

    tgt["_bridge_score"] = -tgt["_corridor_distance"]
    ctl["_bridge_score"] = -ctl["_corridor_distance"]

    target_scores = tgt["_bridge_score"]
    control_scores = ctl["_bridge_score"]
    target_mean = mean_or_none(target_scores)
    control_mean = mean_or_none(control_scores)
    separation_margin_mean = None if target_mean is None or control_mean is None else target_mean - control_mean

    control_threshold = float(control_scores.median())
    target_hit_rate = float((target_scores > control_threshold).mean())
    target_threshold = float(target_scores.median())
    control_reject_rate = float((control_scores < target_threshold).mean())
    assignment_score = 0.5 * (target_hit_rate + control_reject_rate)

    fractions = []
    if cfg.evaluation.bootstrap.enabled:
        n = cfg.evaluation.bootstrap.n_bootstrap
        frac = cfg.evaluation.bootstrap.sample_fraction
        for i in range(n):
            boot_tgt = tgt.sample(frac=frac, replace=True, random_state=cfg.random_seed + i)
            boot_ctl = ctl.sample(frac=frac, replace=True, random_state=cfg.random_seed + 10000 + i)
            if boot_tgt.empty or boot_ctl.empty:
                continue
            boot_margin = float(boot_tgt["_bridge_score"].mean() - boot_ctl["_bridge_score"].mean())
            boot_control_threshold = float(boot_ctl["_bridge_score"].median())
            boot_target_hit_rate = float((boot_tgt["_bridge_score"] > boot_control_threshold).mean())
            boot_target_threshold = float(boot_tgt["_bridge_score"].median())
            boot_control_reject_rate = float((boot_ctl["_bridge_score"] < boot_target_threshold).mean())
            boot_assignment = 0.5 * (boot_target_hit_rate + boot_control_reject_rate)
            fractions.append(float(
                boot_margin > 0 and boot_assignment >= cfg.evaluation.thresholds.assignment_min
            ))

    stability = safe_float(sum(fractions) / len(fractions)) if fractions else 0.0
    overall_pass = bool(
        separation_margin_mean is not None
        and separation_margin_mean > 0
        and assignment_score >= cfg.evaluation.thresholds.assignment_min
        and stability >= cfg.evaluation.thresholds.stability_min
    )
    result_label = "supported" if overall_pass else ("weak" if (separation_margin_mean is not None and separation_margin_mean > 0 and assignment_score > 0) else "failed")

    return {
        "overall_pass": overall_pass,
        "result_label": result_label,
        "separation_margin_mean": separation_margin_mean,
        "assignment_score": assignment_score,
        "original_stability_score": stability,
    }


def classify_transfer_signal(row: Dict[str, Any]) -> str:
    internal_pass = bool(row["internal_overall_pass"])
    h2_pass = bool(row["h2_overall_pass"])
    h2_assignment = safe_float(row["h2_assignment_score"]) or 0.0
    if internal_pass and h2_pass:
        return "candidate_transfer_core"
    if internal_pass and h2_assignment > 0:
        return "candidate_transfer_partial"
    if internal_pass and not h2_pass:
        return "internal_only_core"
    return "insufficient_under_current_logic"


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_serializable(payload), f, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def write_markdown(path: Path, rows: List[Dict[str, Any]]) -> None:
    lines = [
        "# BRIDGE_CARRIER_BLOCK_E_RESULTS — H2 discrimination",
        "",
        "## Purpose",
        "Test whether `distance_to_type_D` behaves like a genuine reduced-H2 transfer stabilizer or only as a mirror artifact under proxy-rigidity conditions.",
        "",
        "## Summary table",
        "",
        "| variant | active_features | internal_pass | internal_assignment | h2_pass | h2_assignment | h2_stability | transfer_signal |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['variant']} | {', '.join(r['active_features'])} | {r['internal_overall_pass']} | {r['internal_assignment_score']} | {r['h2_overall_pass']} | {r['h2_assignment_score']} | {r['h2_original_stability_score']} | {r['transfer_signal']} |"
        )
    lines += [
        "",
        "## Reading rule",
        "- proxy_rigidity_plus_distance > proxy_rigidity_only supports the transfer-stabilizer hypothesis.",
        "- proxy_rigidity_plus_distance > proxy_rigidity_plus_spacing argues against a generic reduced-feature artifact reading.",
        "- proxy_rigidity_plus_grid_plus_distance > proxy_rigidity_plus_grid supports distance as a transport anchor in the richer reduced core.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Bridge carrier block E")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_dir(cfg.results_dir)

    internal_original = prepare_internal_original(pd.read_csv(cfg.internal_original_csv), cfg)
    internal_control = prepare_internal_control(pd.read_csv(cfg.internal_control_csv), cfg)
    h2 = prepare_h2(pd.read_csv(cfg.h2_features_csv), cfg)

    rows: List[Dict[str, Any]] = []
    full_h2_assignment: Optional[float] = None

    for variant in cfg.variants:
        active_features = variant.active_features
        h2_variant = apply_h2_proxy_substitution(h2, active_features, cfg)
        internal_metrics = evaluate_two_group(internal_original, internal_original, internal_control, active_features, cfg)
        h2_metrics = evaluate_two_group(internal_original, h2_variant, internal_control, active_features, cfg)

        row = {
            "variant": variant.name,
            "feature_count": len(active_features),
            "active_features": active_features,
            "internal_overall_pass": internal_metrics["overall_pass"],
            "internal_result_label": internal_metrics["result_label"],
            "internal_separation_margin_mean": internal_metrics["separation_margin_mean"],
            "internal_assignment_score": internal_metrics["assignment_score"],
            "internal_original_stability_score": internal_metrics["original_stability_score"],
            "h2_overall_pass": h2_metrics["overall_pass"],
            "h2_result_label": h2_metrics["result_label"],
            "h2_separation_margin_mean": h2_metrics["separation_margin_mean"],
            "h2_assignment_score": h2_metrics["assignment_score"],
            "h2_original_stability_score": h2_metrics["original_stability_score"],
            "h2_proxy_rigidity_rows": int(h2_variant.get("proxy_rigidity_substituted", pd.Series([0])).sum()),
        }
        if variant.name == "full_reference":
            full_h2_assignment = safe_float(row["h2_assignment_score"])
        rows.append(row)

    baseline = next(r for r in rows if r["variant"] == "full_reference")
    baseline_h2_assignment = safe_float(baseline["h2_assignment_score"]) or 0.0
    for row in rows:
        row["transfer_signal"] = classify_transfer_signal(row)
        row["delta_internal_assignment_vs_full"] = (safe_float(row["internal_assignment_score"]) or 0.0) - (safe_float(baseline["internal_assignment_score"]) or 0.0)
        row["delta_h2_assignment_vs_full"] = (safe_float(row["h2_assignment_score"]) or 0.0) - baseline_h2_assignment

    summary = {
        "run_id": cfg.run_id,
        "source_run_id": cfg.source_run_id,
        "mode": cfg.mode,
        "base_variant": "full_reference",
        "variants_tested": len(cfg.variants),
        "core_features": cfg.core_features,
        "results": rows,
        "interpretation_rule": {
            "distance_stabilizer_supported": "proxy_rigidity_plus_distance improves H2 over proxy_rigidity_only and over proxy_rigidity_plus_spacing",
            "distance_stabilizer_partial": "distance helps only in the richer reduced core",
            "mirror_artifact_suspected": "distance effect vanishes or behaves like generic reduced-set noise",
        },
    }

    if cfg.outputs.get("write_variant_json", False):
        variant_dir = cfg.results_dir / "variant_reports"
        ensure_dir(variant_dir)
        for row in rows:
            write_json(variant_dir / f"{row['variant']}.json", row)
    if cfg.outputs.get("write_csv", False):
        write_csv(cfg.results_dir / "bridge_carrier_block_e.csv", rows)
    if cfg.outputs.get("write_json", False):
        write_json(cfg.results_dir / "summary.json", summary)
    if cfg.outputs.get("write_markdown", False):
        write_markdown(cfg.results_dir / "BRIDGE_CARRIER_BLOCK_E_RESULTS.md", rows)

    print(json.dumps(to_serializable(summary), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
