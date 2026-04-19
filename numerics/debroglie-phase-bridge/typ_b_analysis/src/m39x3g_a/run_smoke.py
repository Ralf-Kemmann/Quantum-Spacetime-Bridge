from __future__ import annotations

from pathlib import Path
import argparse

import pandas as pd

from src.m39x3g_a.io import (
    load_config_and_manifest,
    write_summary_json,
)
from src.m39x3g_a.metrics import build_diagnostic_row
from src.m39x3g_a.decision import (
    build_aggregate_metrics,
    evaluate_type_b_exclusion,
    ReferenceRuleConfig,
)
from src.m39x3g_a.resampling import bootstrap_comparison, TypeBRuleConfig
from src.m39x3g_a.original_reference import bootstrap_original_reference
from src.m39x3g_a.models import (
    ControlFamilyResultSummary,
    OriginalReferenceSummary,
    ReproducibilitySummary,
    SummaryModel,
)


def _require_columns(df: pd.DataFrame, columns: list[str], *, df_name: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"{df_name} is missing required columns: {missing}")


def _load_feature_tables(original_path: str, control_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    original_df = pd.read_csv(original_path)
    control_df = pd.read_csv(control_path)
    return original_df, control_df


def _filter_original_groups(
    original_df: pd.DataFrame,
    *,
    fsw_labels: list[str],
    ao_labels: list[str],
) -> pd.DataFrame:
    allowed = set(fsw_labels + ao_labels)
    return original_df.loc[original_df["label_internal"].isin(allowed)].copy()


def _build_original_reference_metadata(
    original_df: pd.DataFrame,
    *,
    scaling_method: str,
    distance_metric: str,
) -> OriginalReferenceSummary:
    dataset_count = (
        original_df["dataset_id"].nunique()
        if "dataset_id" in original_df.columns
        else len(original_df)
    )
    group_labels = (
        sorted(original_df["group_target"].dropna().unique().tolist())
        if "group_target" in original_df.columns
        else ["FSW", "AO"]
    )

    return OriginalReferenceSummary(
        dataset_count=int(dataset_count),
        group_labels=group_labels,
        n_rows=int(len(original_df)),
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
        original_separation_margin_min=config.reference_rules.original_separation_margin.min,
        original_stability_score_min=config.reference_rules.original_stability_score.min,
        original_assignment_score_min=config.reference_rules.original_assignment_score.min,
        control_margin_quantile_min=config.reference_rules.control_margin_quantile.min,
    )


def _compute_original_reference_pair(
    *,
    original_subset: pd.DataFrame,
    fsw_labels: list[str],
    ao_labels: list[str],
    feature_columns: list[str],
    n_resamples: int,
    seed: int,
    distance_metric: str,
):
    return bootstrap_original_reference(
        original_df=original_subset,
        fsw_labels=fsw_labels,
        ao_labels=ao_labels,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for M.3.9x.3g.a")
    parser.add_argument(
        "--config",
        default="data/config.yaml",
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--control-family",
        default=None,
        help=(
            "Optional single control family id to test. "
            "If omitted, all enabled control families are evaluated."
        ),
    )
    parser.add_argument(
        "--summary-out",
        default=None,
        help="Optional path for summary.json. Defaults to config outputs location.",
    )
    parser.add_argument(
        "--n-resamples",
        type=int,
        default=None,
        help="Optional override for smoke-test bootstrap count.",
    )
    args = parser.parse_args()

    config, manifest_rows = load_config_and_manifest(args.config)

    original_df, control_df = _load_feature_tables(
        config.data.original_features_path,
        config.data.control_features_path,
    )

    required_id_cols = [
        "dataset_id",
        "label_internal",
    ]
    required_original_cols = required_id_cols + ["group_target"]
    required_control_cols = required_id_cols + ["control_family"]
    feature_columns = list(config.feature_space.feature_columns)

    _require_columns(
        original_df,
        required_original_cols + feature_columns,
        df_name="original_features",
    )
    _require_columns(
        control_df,
        required_control_cols + feature_columns,
        df_name="control_features",
    )

    fsw_labels = list(config.grouping.original_group_mapping["FSW"])
    ao_labels_all = list(config.grouping.original_group_mapping["AO"])

    # O2 = Hauptreferenz, O3 = Robustheitsvariante
    ao_labels_o2 = ["AO_A04", "AO_A05", "AO_A06"]
    ao_labels_o3 = ["AO_A04", "AO_A05"]

    original_subset = _filter_original_groups(
        original_df,
        fsw_labels=fsw_labels,
        ao_labels=sorted(set(ao_labels_all + ao_labels_o2 + ao_labels_o3)),
    )

    if len(original_subset) == 0:
        raise ValueError("No original rows matched configured FSW/AO labels")

    enabled_controls = config.enabled_control_families
    if not enabled_controls:
        raise ValueError("No enabled control families found in config")

    if args.control_family is not None:
        selected_control_ids = [args.control_family]
    else:
        selected_control_ids = [cf.id for cf in enabled_controls]

    if args.n_resamples is not None:
        n_resamples = args.n_resamples
    else:
        n_resamples = min(config.resampling.n_resamples, 100)

    type_b_rules = _build_type_b_rules_from_config(config)
    reference_rules = _build_reference_rules_from_config(config)

    # O2 = primary reference
    original_reference = _compute_original_reference_pair(
        original_subset=original_subset,
        fsw_labels=fsw_labels,
        ao_labels=ao_labels_o2,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=config.reproducibility.random_seed,
        distance_metric=config.distance.distance_metric,
    )

    # O3 = robustness reference
    original_reference_o3 = _compute_original_reference_pair(
        original_subset=original_subset,
        fsw_labels=fsw_labels,
        ao_labels=ao_labels_o3,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=config.reproducibility.random_seed,
        distance_metric=config.distance.distance_metric,
    )

    control_results: list[ControlFamilyResultSummary] = []
    diagnostic_rows = []

    for control_family_id in selected_control_ids:
        selected_control_df = control_df.loc[
            control_df["control_family"] == control_family_id
        ].copy()

        if len(selected_control_df) == 0:
            raise ValueError(
                f"No control rows found for control family '{control_family_id}'"
            )

        comparison_id = f"original_vs_{control_family_id}"

        resampling = bootstrap_comparison(
            run_id=config.run_id,
            control_family=control_family_id,
            comparison_id=comparison_id,
            left_df=original_subset,
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
            control_family=control_family_id,
            comparison_id=comparison_id,
            left_df=original_subset,
            right_df=selected_control_df,
            feature_columns=feature_columns,
            stability_score=resampling.stability_score,
            type_B_like_pattern_detected=resampling.type_B_like_pattern_detected,
            interpretation="Bootstrap-based smoke-test interpretation.",
            distance_metric=config.distance.distance_metric,
            warning_flag=False,
            notes="Generated by run_smoke.py with bootstrap resampling",
        )

        diagnostic_rows.append(diagnostic_row)
        control_results.append(
            _control_result_from_resampling(
                diagnostic_row=diagnostic_row,
                selected_control_df=selected_control_df,
                resampling=resampling,
            )
        )

    aggregate_metrics = build_aggregate_metrics(
        original_separation_margin=original_reference.separation_margin_mean,
        original_stability_score=original_reference.stability_score,
        original_assignment_score=original_reference.assignment_score_mean,
        control_results=control_results,
    )

    decision = evaluate_type_b_exclusion(
        aggregate_metrics=aggregate_metrics,
        control_results=control_results,
        thresholds=config.decision_rules.thresholds,
        reference_rules=reference_rules,
    )

    summary = SummaryModel(
        block_id=config.block_id,
        block_title=config.block_title,
        run_id=config.run_id,
        run_status="completed",
        feature_space_version=config.feature_space.feature_space_version,
        decision_rule_version=config.decision_rules.version,
        result_label=decision.result_label,
        overall_interpretation=decision.overall_interpretation,
        original_reference=_build_original_reference_metadata(
            original_subset,
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

    summary_out = args.summary_out
    if summary_out is None:
        summary_out = str(Path(config.outputs.base_dir) / config.paths.summary_path)

    write_summary_json(summary, summary_out)

    print("run_id:", config.run_id)
    print("control_families:", ",".join(selected_control_ids))
    print("n_resamples:", n_resamples)
    print("primary_reference: O2")
    print("primary_reference_margin:", original_reference.separation_margin_mean)
    print("primary_reference_stability:", original_reference.stability_score)
    print("robustness_reference: O3")
    print("robustness_reference_margin:", original_reference_o3.separation_margin_mean)
    print("robustness_reference_stability:", original_reference_o3.stability_score)
    print("summary_out:", summary_out)
    print("result_label:", summary.result_label)
    print("overall_interpretation:", summary.overall_interpretation)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
