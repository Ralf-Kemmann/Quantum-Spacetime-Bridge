from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Sequence, Any
import json

import pandas as pd
import yaml

from src.m39x3g_a.metrics import build_diagnostic_row
from src.m39x3g_a.resampling import bootstrap_comparison, TypeBRuleConfig
from src.m39x3g_a.decision import (
    build_aggregate_metrics,
    evaluate_type_b_exclusion,
    ReferenceRuleConfig,
)
from src.m39x3g_a.models import (
    ControlFamilyResultSummary,
    OriginalReferenceSummary,
    ReproducibilitySummary,
    SummaryModel,
)
from src.m39x3g_a.io import write_summary_json


def _to_ns(obj: Any) -> Any:
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: _to_ns(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_to_ns(x) for x in obj]
    return obj


def _load_yaml_config(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return _to_ns(raw)


def _require_columns(df: pd.DataFrame, columns: Sequence[str], *, df_name: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def _load_feature_tables(holdout_path: str, control_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    holdout_df = pd.read_csv(holdout_path)
    control_df = pd.read_csv(control_path)
    return holdout_df, control_df


def _build_type_b_rules_from_config(config) -> TypeBRuleConfig:
    return TypeBRuleConfig(
        distance_to_type_D_min=config.type_b_rules.distance_to_type_D.min,
        distance_to_type_D_max=config.type_b_rules.distance_to_type_D.max,
        spacing_cv_min=config.type_b_rules.spacing_cv.min,
        spacing_cv_max=config.type_b_rules.spacing_cv.max,
        grid_deviation_score_min=config.type_b_rules.grid_deviation_score.min,
        grid_deviation_score_max=config.type_b_rules.grid_deviation_score.max,
        simple_rigidity_surrogate_min=config.type_b_rules.simple_rigidity_surrogate.min,
        separation_margin_min=config.type_b_rules.separation_margin.min,
        assignment_score_min=config.type_b_rules.assignment_score.min,
        stability_score_min=config.type_b_rules.stability_score.min,
        separation_margin_ci_low_min=config.type_b_rules.separation_margin_ci_low.min,
    )


def _build_reference_rules_from_config(config) -> ReferenceRuleConfig:
    return ReferenceRuleConfig(
        original_separation_margin_min=config.fixed_thresholds.original_separation_margin_min,
        original_stability_score_min=config.fixed_thresholds.original_stability_score_min,
        original_assignment_score_min=config.fixed_thresholds.original_assignment_score_min,
        control_margin_quantile_min=config.fixed_thresholds.control_margin_quantile_min,
    )


def _build_original_reference_summary(
    holdout_df: pd.DataFrame,
    *,
    scaling_method: str,
    distance_metric: str,
) -> OriginalReferenceSummary:
    dataset_count = (
        holdout_df["dataset_id"].nunique()
        if "dataset_id" in holdout_df.columns
        else len(holdout_df)
    )
    group_labels = (
        sorted(holdout_df["group_target"].dropna().unique().tolist())
        if "group_target" in holdout_df.columns
        else ["FSW", "AO"]
    )

    return OriginalReferenceSummary(
        dataset_count=int(dataset_count),
        group_labels=group_labels,
        n_rows=int(len(holdout_df)),
        scaling_method=scaling_method,
        distance_metric=distance_metric,
    )


def _control_result_from_resampling(
    *,
    diagnostic_row,
    selected_control_df: pd.DataFrame,
    resampling,
) -> ControlFamilyResultSummary:
    n_instances = (
        int(selected_control_df["dataset_id"].nunique())
        if "dataset_id" in selected_control_df.columns
        else int(len(selected_control_df))
    )

    return ControlFamilyResultSummary(
        control_family=diagnostic_row.control_family,
        enabled=True,
        n_instances=n_instances,
        n_rows=int(len(selected_control_df)),
        mean_intra_distance=diagnostic_row.mean_intra_right,
        mean_inter_distance=diagnostic_row.mean_inter_distance,
        pooled_intra_distance=diagnostic_row.pooled_intra_distance,
        separation_margin_mean=resampling.separation_margin_mean,
        separation_margin_ci=resampling.separation_margin_ci,
        separation_ratio_mean=resampling.separation_ratio_mean,
        stability_score_mean=resampling.stability_score,
        stability_score_ci=None,
        assignment_score_mean=resampling.assignment_score_mean,
        type_B_like_pattern_detected=resampling.type_B_like_pattern_detected,
        interpretation=diagnostic_row.interpretation,
        warnings=[],
    )


def _prepare_holdout_df(holdout_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    out = holdout_df.copy()

    direct_features_present = {
        "distance_to_type_D": "distance_to_type_D" in out.columns and out["distance_to_type_D"].notna().all(),
        "spacing_cv": "spacing_cv" in out.columns and out["spacing_cv"].notna().all(),
        "simple_rigidity_surrogate": "simple_rigidity_surrogate" in out.columns and out["simple_rigidity_surrogate"].notna().all(),
        "grid_deviation_score": "grid_deviation_score" in out.columns and out["grid_deviation_score"].notna().all(),
    }

    proxy_rigidity_used = False
    proxy_feature_count = 0
    if "simple_rigidity_surrogate" in out.columns:
        proxy_col = "rigidity_proxy_second_difference_curvature"
        if proxy_col in out.columns:
            missing_mask = out["simple_rigidity_surrogate"].isna() | (out["simple_rigidity_surrogate"].astype(str) == "")
            if missing_mask.any():
                out.loc[missing_mask, "simple_rigidity_surrogate"] = out.loc[missing_mask, proxy_col]
                proxy_rigidity_used = True
                proxy_feature_count = 1

    direct_feature_count = int(sum(direct_features_present.values()))
    reduced_mapping_mode = proxy_rigidity_used or direct_feature_count < 4

    metadata = {
        "reduced_mapping_mode": reduced_mapping_mode,
        "proxy_rigidity_used": proxy_rigidity_used,
        "direct_feature_count": direct_feature_count,
        "proxy_feature_count": proxy_feature_count,
        "missing_direct_features_before_proxy_fill": [
            k for k, v in direct_features_present.items() if not v
        ],
    }
    return out, metadata


def _compute_control_margin_diagnostics(control_results: list[ControlFamilyResultSummary], original_margin: float) -> dict:
    margins = [float(r.separation_margin_mean) for r in control_results if r.separation_margin_mean is not None]
    if not margins:
        return {
            "control_margin_mean": None,
            "control_margin_median": None,
            "control_margin_max": None,
            "original_minus_control_mean": None,
            "original_minus_control_median": None,
            "original_minus_control_max": None,
            "original_rank_among_controls": None,
            "n_control_margins": 0,
        }

    sorted_margins = sorted(margins)
    n = len(sorted_margins)
    if n % 2 == 1:
        median = sorted_margins[n // 2]
    else:
        median = (sorted_margins[n // 2 - 1] + sorted_margins[n // 2]) / 2.0

    mean_val = sum(sorted_margins) / n
    max_val = max(sorted_margins)
    rank = 1 + sum(original_margin < m for m in sorted_margins)

    return {
        "control_margin_mean": mean_val,
        "control_margin_median": median,
        "control_margin_max": max_val,
        "original_minus_control_mean": original_margin - mean_val,
        "original_minus_control_median": original_margin - median,
        "original_minus_control_max": original_margin - max_val,
        "original_rank_among_controls": rank,
        "n_control_margins": n,
    }


def _build_stability_trace_payload(
    *,
    holdout_df: pd.DataFrame,
    control_results: list[ControlFamilyResultSummary],
    holdout_margin: float,
    holdout_assignment: float,
    holdout_stability: float,
    config,
    h2_mapping_meta: dict,
) -> dict:
    per_control = []
    any_type_b_like = False
    any_ci_low_pass = False
    all_assignment_pass = True
    all_margin_pass = True
    all_ci_low_pass = True

    for r in control_results:
        ci_low = None
        if r.separation_margin_ci is not None and len(r.separation_margin_ci) >= 1:
            ci_low = float(r.separation_margin_ci[0])

        margin_pass = (
            r.separation_margin_mean is not None
            and float(r.separation_margin_mean) >= config.type_b_rules.separation_margin.min
        )
        assignment_pass = (
            r.assignment_score_mean is not None
            and float(r.assignment_score_mean) >= config.type_b_rules.assignment_score.min
        )
        ci_low_pass = (
            ci_low is not None
            and ci_low >= config.type_b_rules.separation_margin_ci_low.min
        )

        any_type_b_like = any_type_b_like or bool(r.type_B_like_pattern_detected)
        any_ci_low_pass = any_ci_low_pass or ci_low_pass
        all_assignment_pass = all_assignment_pass and assignment_pass
        all_margin_pass = all_margin_pass and margin_pass
        all_ci_low_pass = all_ci_low_pass and ci_low_pass

        per_control.append(
            {
                "control_family": r.control_family,
                "stability_score_mean": r.stability_score_mean,
                "type_B_like_pattern_detected": r.type_B_like_pattern_detected,
                "assignment_score_mean": r.assignment_score_mean,
                "separation_margin_mean": r.separation_margin_mean,
                "separation_margin_ci_low": ci_low,
                "margin_pass_under_type_b_rules": margin_pass,
                "assignment_pass_under_type_b_rules": assignment_pass,
                "ci_low_pass_under_type_b_rules": ci_low_pass,
            }
        )

    zeroing_candidates = []
    if h2_mapping_meta.get("reduced_mapping_mode"):
        zeroing_candidates.append("reduced_mapping_mode_active")
    if h2_mapping_meta.get("proxy_rigidity_used"):
        zeroing_candidates.append("proxy_rigidity_used")
    if holdout_df["group_target"].nunique() < 2:
        zeroing_candidates.append("single_group_holdout_reference")
    if holdout_df["dataset_id"].nunique() <= 3:
        zeroing_candidates.append("very_small_holdout_reference")
    if not any_type_b_like:
        zeroing_candidates.append("no_type_B_like_pattern_detected_in_resampling_outputs")
    if not any_ci_low_pass:
        zeroing_candidates.append("no_ci_low_pass_detected_under_type_b_rules")

    raw_signal_summary = {
        "holdout_margin_passes_type_b_min": holdout_margin >= config.type_b_rules.separation_margin.min,
        "holdout_assignment_passes_type_b_min": holdout_assignment >= config.type_b_rules.assignment_score.min,
        "holdout_stability_passes_type_b_min": holdout_stability >= config.type_b_rules.stability_score.min,
    }

    return {
        "holdout_reference_n_rows": int(len(holdout_df)),
        "holdout_reference_dataset_count": int(holdout_df["dataset_id"].nunique()) if "dataset_id" in holdout_df.columns else int(len(holdout_df)),
        "holdout_reference_group_count": int(holdout_df["group_target"].nunique()) if "group_target" in holdout_df.columns else None,
        "proxy_rigidity_used": h2_mapping_meta.get("proxy_rigidity_used"),
        "reduced_mapping_mode": h2_mapping_meta.get("reduced_mapping_mode"),
        "raw_signal_summary": raw_signal_summary,
        "per_control_trace": per_control,
        "aggregate_trace_flags": {
            "any_type_B_like_pattern_detected": any_type_b_like,
            "any_ci_low_pass_under_type_b_rules": any_ci_low_pass,
            "all_assignment_pass_under_type_b_rules": all_assignment_pass,
            "all_margin_pass_under_type_b_rules": all_margin_pass,
            "all_ci_low_pass_under_type_b_rules": all_ci_low_pass,
        },
        "likely_zeroing_candidates": zeroing_candidates,
        "note": "Diagnostic trace only; localizes plausible causes of stability collapse in reduced H2 mode."
    }


def _compute_reduced_h2_stability_score(stability_trace: dict) -> dict:
    per_control = stability_trace.get("per_control_trace", [])
    if not per_control:
        return {
            "reduced_h2_stability_score": None,
            "component_mean_margin_pass": None,
            "component_mean_assignment_pass": None,
            "component_mean_ci_low_pass": None,
            "n_controls_used": 0,
            "note": "No control trace rows available."
        }

    margin_vals = [1.0 if row.get("margin_pass_under_type_b_rules") else 0.0 for row in per_control]
    assignment_vals = [1.0 if row.get("assignment_pass_under_type_b_rules") else 0.0 for row in per_control]
    ci_vals = [1.0 if row.get("ci_low_pass_under_type_b_rules") else 0.0 for row in per_control]

    mean_margin = sum(margin_vals) / len(margin_vals)
    mean_assignment = sum(assignment_vals) / len(assignment_vals)
    mean_ci = sum(ci_vals) / len(ci_vals)

    reduced_score = (mean_margin + mean_assignment + mean_ci) / 3.0

    return {
        "reduced_h2_stability_score": reduced_score,
        "component_mean_margin_pass": mean_margin,
        "component_mean_assignment_pass": mean_assignment,
        "component_mean_ci_low_pass": mean_ci,
        "n_controls_used": len(per_control),
        "note": "Diagnostic reduced-H2 stability score based on margin/assignment/CI pass rates only; excludes type_B_like_pattern_detected gating."
    }


def run_holdout_eval(config_path: str = "data/config_holdout.yaml") -> tuple[SummaryModel, str]:
    config = _load_yaml_config(config_path)

    holdout_df, control_df = _load_feature_tables(
        config.data.holdout_original_features_path,
        config.data.control_features_path,
    )

    holdout_df, h2_mapping_meta = _prepare_holdout_df(holdout_df)

    feature_columns = list(config.feature_space.feature_columns)
    required_holdout_cols = ["dataset_id", "label_internal", "group_target"] + feature_columns
    required_control_cols = ["dataset_id", "label_internal", "control_family"] + feature_columns

    _require_columns(holdout_df, required_holdout_cols, df_name="holdout_original_features")
    _require_columns(control_df, required_control_cols, df_name="control_features")

    if holdout_df[feature_columns].isna().any().any():
        missing_cols = holdout_df[feature_columns].columns[holdout_df[feature_columns].isna().any()].tolist()
        raise ValueError(
            "holdout_original_features still contains missing values in required feature columns after proxy fill: "
            f"{missing_cols}"
        )

    type_b_rules = _build_type_b_rules_from_config(config)
    reference_rules = _build_reference_rules_from_config(config)

    n_resamples = min(config.resampling.n_resamples, 1000)
    control_results: list[ControlFamilyResultSummary] = []

    for cf in config.control_families:
        if not cf.enabled:
            continue

        selected_control_df = control_df.loc[control_df["control_family"] == cf.id].copy()
        if len(selected_control_df) == 0:
            raise ValueError(f"No control rows found for control family '{cf.id}'")

        comparison_id = f"holdout_vs_{cf.id}"

        resampling = bootstrap_comparison(
            run_id=config.run_id,
            control_family=cf.id,
            comparison_id=comparison_id,
            left_df=holdout_df,
            right_df=selected_control_df,
            feature_columns=feature_columns,
            n_resamples=n_resamples,
            seed=config.reproducibility.random_seed,
            distance_metric=config.distance.distance_metric,
            rules=type_b_rules,
        )

        diagnostic_row = build_diagnostic_row(
            run_id=config.run_id,
            feature_space_version=config.feature_space.feature_space_version,
            decision_rule_version=config.decision_rules.version,
            control_family=cf.id,
            comparison_id=comparison_id,
            left_df=holdout_df,
            right_df=selected_control_df,
            feature_columns=feature_columns,
            stability_score=resampling.stability_score,
            type_B_like_pattern_detected=resampling.type_B_like_pattern_detected,
            interpretation="Holdout evaluation diagnostic.",
            distance_metric=config.distance.distance_metric,
            warning_flag=False,
            notes="Generated by holdout_eval.py (reduced H2 stability patch)",
        )

        control_results.append(
            _control_result_from_resampling(
                diagnostic_row=diagnostic_row,
                selected_control_df=selected_control_df,
                resampling=resampling,
            )
        )

    holdout_margin = max(
        [r.separation_margin_mean for r in control_results if r.separation_margin_mean is not None],
        default=config.fixed_thresholds.original_separation_margin_min,
    )
    holdout_stability = max(
        [r.stability_score_mean for r in control_results if r.stability_score_mean is not None],
        default=0.0,
    )
    holdout_assignment = max(
        [r.assignment_score_mean for r in control_results if r.assignment_score_mean is not None],
        default=0.0,
    )

    aggregate_metrics = build_aggregate_metrics(
        original_separation_margin=holdout_margin,
        original_stability_score=holdout_stability,
        original_assignment_score=holdout_assignment,
        control_results=control_results,
    )

    margin_diag = _compute_control_margin_diagnostics(control_results, holdout_margin)
    stability_trace = _build_stability_trace_payload(
        holdout_df=holdout_df,
        control_results=control_results,
        holdout_margin=holdout_margin,
        holdout_assignment=holdout_assignment,
        holdout_stability=holdout_stability,
        config=config,
        h2_mapping_meta=h2_mapping_meta,
    )
    reduced_h2_stability_diag = _compute_reduced_h2_stability_score(stability_trace)

    class _Thresholds:
        min_stability_score_for_supported = config.decision_rules.thresholds.min_stability_score_for_supported
        min_original_over_control_margin_delta = config.fixed_thresholds.min_original_over_control_margin_delta
        max_control_typeB_like_fraction_for_supported = config.decision_rules.thresholds.max_control_typeB_like_fraction_for_supported
        max_control_typeB_like_fraction_for_weak = config.decision_rules.thresholds.max_control_typeB_like_fraction_for_weak

    decision = evaluate_type_b_exclusion(
        aggregate_metrics=aggregate_metrics,
        control_results=control_results,
        thresholds=_Thresholds(),
        reference_rules=reference_rules,
    )

    summary = SummaryModel(
        block_id="M.3.9x.3g.a",
        block_title=config.block_title,
        run_id=config.run_id,
        run_status="completed",
        feature_space_version=config.feature_space.feature_space_version,
        decision_rule_version=config.decision_rules.version,
        result_label=decision.result_label,
        overall_interpretation=decision.overall_interpretation,
        original_reference=_build_original_reference_summary(
            holdout_df,
            scaling_method=config.preprocessing.scaling_method,
            distance_metric=config.distance.distance_metric,
        ),
        control_family_results=control_results,
        aggregate_metrics=aggregate_metrics,
        decision_trace=decision.decision_trace,
        warnings=[],
        errors=[],
        reproducibility=ReproducibilitySummary(
            random_seed=config.reproducibility.random_seed,
            seed_list=config.reproducibility.seed_list,
            n_resamples=n_resamples,
            software_env={
                "python_version": config.reproducibility.software_env.python_version,
                "numpy_version": config.reproducibility.software_env.numpy_version,
                "pandas_version": config.reproducibility.software_env.pandas_version,
                "sklearn_version": config.reproducibility.software_env.sklearn_version,
            },
        ),
    )

    summary_out = str(Path(config.outputs.base_dir) / config.paths.summary_path)
    write_summary_json(summary, summary_out)

    diagnostics_out = Path(config.outputs.base_dir) / "holdout_additional_diagnostics.json"
    diagnostics_payload = {
        "run_id": config.run_id,
        "h2_mapping_diagnostics": h2_mapping_meta,
        "margin_diagnostics": margin_diag,
        "stability_diagnostics": {
            "original_stability_score": holdout_stability,
            "reference_original_stability_score_min": config.fixed_thresholds.original_stability_score_min,
            "stability_gap": holdout_stability - config.fixed_thresholds.original_stability_score_min,
            "note": "Current holdout stability is derived from inherited full-protocol logic and may be too strict for reduced H2 mode."
        },
        "relative_advantage_diagnostics": {
            "original_vs_control_margin_delta": aggregate_metrics.original_vs_control_margin_delta,
            "reference_min_original_over_control_margin_delta": config.fixed_thresholds.min_original_over_control_margin_delta,
            "delta_gap": aggregate_metrics.original_vs_control_margin_delta - config.fixed_thresholds.min_original_over_control_margin_delta,
            "note": "Current relative-advantage threshold is inherited from the hardened internal protocol."
        },
        "stability_trace": stability_trace,
        "reduced_h2_stability_diagnostics": reduced_h2_stability_diag,
    }
    diagnostics_out.parent.mkdir(parents=True, exist_ok=True)
    with open(diagnostics_out, "w", encoding="utf-8") as f:
        json.dump(diagnostics_payload, f, indent=2)

    return summary, summary_out


if __name__ == "__main__":
    summary, summary_out = run_holdout_eval()
    print("run_id:", summary.run_id)
    print("result_label:", summary.result_label)
    print("summary_out:", summary_out)
    print("extra_diagnostics_out:", str(Path(summary_out).with_name("holdout_additional_diagnostics.json")))
