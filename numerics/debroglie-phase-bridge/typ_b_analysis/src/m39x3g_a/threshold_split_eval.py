from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Sequence

import pandas as pd

from src.m39x3g_a.calibration import calibrate_reference_thresholds
from src.m39x3g_a.original_reference import bootstrap_original_reference
from src.m39x3g_a.models import ControlFamilyResultSummary
from src.m39x3g_a.decision import build_aggregate_metrics, evaluate_type_b_exclusion, ReferenceRuleConfig


@dataclass(slots=True)
class PairEvalSummary:
    pair_id: str
    fsw_labels: list[str]
    ao_labels: list[str]
    separation_margin_mean: float
    separation_margin_ci_low: float | None
    separation_margin_ci_high: float | None
    separation_ratio_mean: float
    assignment_score_mean: float
    stability_score: float
    passes_margin_threshold: bool
    passes_stability_threshold: bool
    passes_assignment_threshold: bool
    overall_pass: bool


def _evaluate_pair(
    *,
    original_df: pd.DataFrame,
    pair_id: str,
    fsw_labels: Sequence[str],
    ao_labels: Sequence[str],
    feature_columns: Sequence[str],
    n_resamples: int,
    seed: int,
    distance_metric: str,
    min_margin_threshold: float,
    min_stability_threshold: float,
    min_assignment_threshold: float,
) -> PairEvalSummary:
    result = bootstrap_original_reference(
        original_df=original_df,
        fsw_labels=fsw_labels,
        ao_labels=ao_labels,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
        min_assignment_for_positive=min_assignment_threshold,
        min_margin_for_positive=0.05,
    )

    ci_low = result.separation_margin_ci[0] if result.separation_margin_ci is not None else None
    ci_high = result.separation_margin_ci[1] if result.separation_margin_ci is not None else None

    passes_margin = result.separation_margin_mean >= min_margin_threshold
    passes_stability = result.stability_score >= min_stability_threshold
    passes_assignment = result.assignment_score_mean >= min_assignment_threshold

    return PairEvalSummary(
        pair_id=pair_id,
        fsw_labels=list(fsw_labels),
        ao_labels=list(ao_labels),
        separation_margin_mean=result.separation_margin_mean,
        separation_margin_ci_low=ci_low,
        separation_margin_ci_high=ci_high,
        separation_ratio_mean=result.separation_ratio_mean,
        assignment_score_mean=result.assignment_score_mean,
        stability_score=result.stability_score,
        passes_margin_threshold=passes_margin,
        passes_stability_threshold=passes_stability,
        passes_assignment_threshold=passes_assignment,
        overall_pass=(passes_margin and passes_stability and passes_assignment),
    )


def run_threshold_split_eval(
    *,
    original_df: pd.DataFrame,
    control_results: list[ControlFamilyResultSummary],
    feature_columns: Sequence[str],
    n_resamples: int = 100,
    seed: int = 1729,
    distance_metric: str = "euclidean",
    min_stability_threshold: float = 0.80,
    min_assignment_threshold: float = 0.75,
    control_delta_quantile_q: float = 0.90,
) -> dict:
    """
    Minimal de-circularized evaluation:

    Calibration side:
      - O1 original pair margin
      - control deltas reconstructed from O1 against current control summaries

    Evaluation side:
      - O2 primary evaluation
      - O3 replication evaluation

    This is still not a full out-of-sample protocol, but it separates threshold
    calibration from the O2/O3 evaluation target.
    """

    fsw = ["FSW_D05", "FSW_D06"]
    o1_ao = ["AO_A03", "AO_A04", "AO_A05"]
    o2_ao = ["AO_A04", "AO_A05", "AO_A06"]
    o3_ao = ["AO_A04", "AO_A05"]

    o1 = _evaluate_pair(
        original_df=original_df,
        pair_id="O1",
        fsw_labels=fsw,
        ao_labels=o1_ao,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
        min_margin_threshold=0.0,
        min_stability_threshold=min_stability_threshold,
        min_assignment_threshold=min_assignment_threshold,
    )

    control_deltas = []
    for row in control_results:
        if row.enabled and row.separation_margin_mean is not None:
            control_deltas.append(o1.separation_margin_mean - float(row.separation_margin_mean))

    cal = calibrate_reference_thresholds(
        original_margins=[o1.separation_margin_mean],
        control_deltas=control_deltas,
        control_quantile_q=control_delta_quantile_q,
    )

    calibrated_margin_threshold = max(
        cal.suggested_original_separation_margin_min,
        o1.separation_margin_mean,
    )
    calibrated_delta_threshold = cal.suggested_min_original_over_control_margin_delta

    o2 = _evaluate_pair(
        original_df=original_df,
        pair_id="O2",
        fsw_labels=fsw,
        ao_labels=o2_ao,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
        min_margin_threshold=calibrated_margin_threshold,
        min_stability_threshold=min_stability_threshold,
        min_assignment_threshold=min_assignment_threshold,
    )

    o3 = _evaluate_pair(
        original_df=original_df,
        pair_id="O3",
        fsw_labels=fsw,
        ao_labels=o3_ao,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
        min_margin_threshold=calibrated_margin_threshold,
        min_stability_threshold=min_stability_threshold,
        min_assignment_threshold=min_assignment_threshold,
    )

    reference_rules = ReferenceRuleConfig(
        original_separation_margin_min=calibrated_margin_threshold,
        original_stability_score_min=min_stability_threshold,
        original_assignment_score_min=min_assignment_threshold,
        control_margin_quantile_min=0.75,
    )

    aggregate_metrics_o2 = build_aggregate_metrics(
        original_separation_margin=o2.separation_margin_mean,
        original_stability_score=o2.stability_score,
        original_assignment_score=o2.assignment_score_mean,
        control_results=control_results,
    )

    class _Thresholds:
        min_stability_score_for_supported = 0.70
        min_original_over_control_margin_delta = calibrated_delta_threshold
        max_control_typeB_like_fraction_for_supported = 0.10
        max_control_typeB_like_fraction_for_weak = 0.30

    decision_o2 = evaluate_type_b_exclusion(
        aggregate_metrics=aggregate_metrics_o2,
        control_results=control_results,
        thresholds=_Thresholds(),
        reference_rules=reference_rules,
    )

    aggregate_metrics_o3 = build_aggregate_metrics(
        original_separation_margin=o3.separation_margin_mean,
        original_stability_score=o3.stability_score,
        original_assignment_score=o3.assignment_score_mean,
        control_results=control_results,
    )

    decision_o3 = evaluate_type_b_exclusion(
        aggregate_metrics=aggregate_metrics_o3,
        control_results=control_results,
        thresholds=_Thresholds(),
        reference_rules=reference_rules,
    )

    return {
        "protocol": {
            "name": "threshold_split_eval_v1",
            "description": "O1-based calibration; O2 primary evaluation; O3 replication evaluation",
            "distance_metric": distance_metric,
            "n_resamples": n_resamples,
            "seed": seed,
        },
        "calibration": {
            "source_pair": "O1",
            "source_margin": o1.separation_margin_mean,
            "control_delta_quantile_q": control_delta_quantile_q,
            "suggested_original_separation_margin_min_raw": cal.suggested_original_separation_margin_min,
            "suggested_original_separation_margin_min_used": calibrated_margin_threshold,
            "suggested_min_original_over_control_margin_delta": calibrated_delta_threshold,
            "notes": cal.notes + [
                "Because calibration used only O1 as original margin input, the used margin threshold is max(raw_suggestion, O1 margin).",
            ],
        },
        "pairs": {
            "O1": asdict(o1),
            "O2": asdict(o2),
            "O3": asdict(o3),
        },
        "decisions": {
            "O2": {
                "result_label": decision_o2.result_label,
                "overall_interpretation": decision_o2.overall_interpretation,
                "decision_trace": decision_o2.decision_trace.model_dump(),
                "aggregate_metrics": aggregate_metrics_o2.model_dump(),
            },
            "O3": {
                "result_label": decision_o3.result_label,
                "overall_interpretation": decision_o3.overall_interpretation,
                "decision_trace": decision_o3.decision_trace.model_dump(),
                "aggregate_metrics": aggregate_metrics_o3.model_dump(),
            },
        },
    }
