from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Any, Sequence

from src.m39x3g_a.models import (
    AggregateMetricsSummary,
    ControlFamilyResultSummary,
    DecisionTraceSummary,
    DecisionThresholdsConfig,
    ResultLabel,
)


@dataclass(slots=True)
class ReferenceRuleConfig:
    original_separation_margin_min: float = 0.30
    original_stability_score_min: float = 0.80
    original_assignment_score_min: float = 0.75
    control_margin_quantile_min: float = 0.75


@dataclass(slots=True)
class DecisionResult:
    result_label: ResultLabel
    overall_interpretation: str
    decision_trace: DecisionTraceSummary


def _count_enabled_controls(
    control_results: list[ControlFamilyResultSummary],
) -> int:
    return sum(1 for row in control_results if row.enabled)


def _control_typeB_like_fraction(
    control_results: list[ControlFamilyResultSummary],
) -> float:
    enabled = [row for row in control_results if row.enabled]
    if not enabled:
        return 0.0
    positives = sum(1 for row in enabled if row.type_B_like_pattern_detected)
    return positives / len(enabled)


def _enabled_control_margins(
    control_results: list[ControlFamilyResultSummary],
) -> list[float]:
    margins: list[float] = []
    for row in control_results:
        if row.enabled and row.separation_margin_mean is not None:
            margins.append(float(row.separation_margin_mean))
    return margins


def _quantile_from_sorted(values: Sequence[float], q: float) -> float | None:
    if not values:
        return None
    if not (0.0 <= q <= 1.0):
        raise ValueError("quantile q must satisfy 0.0 <= q <= 1.0")
    vals = sorted(values)
    if len(vals) == 1:
        return float(vals[0])
    pos = q * (len(vals) - 1)
    low = int(pos)
    high = min(low + 1, len(vals) - 1)
    frac = pos - low
    return float(vals[low] * (1.0 - frac) + vals[high] * frac)


def _any_enabled_control_has_robust_typeB_like_pattern(
    control_results: list[ControlFamilyResultSummary],
    thresholds: DecisionThresholdsConfig,
) -> bool:
    for row in control_results:
        if not row.enabled:
            continue
        if not row.type_B_like_pattern_detected:
            continue

        stability_ok = (
            row.stability_score_mean is not None
            and row.stability_score_mean >= thresholds.min_stability_score_for_supported
        )
        margin_ok = (
            row.separation_margin_mean is not None
            and row.separation_margin_mean > 0.0
        )

        if stability_ok and margin_ok:
            return True
    return False


def _original_quality_ok(
    aggregate: AggregateMetricsSummary,
    reference: ReferenceRuleConfig,
) -> bool:
    return (
        aggregate.original_separation_margin is not None
        and aggregate.original_separation_margin >= reference.original_separation_margin_min
        and aggregate.original_stability_score is not None
        and aggregate.original_stability_score >= reference.original_stability_score_min
        and aggregate.original_assignment_score is not None
        and aggregate.original_assignment_score >= reference.original_assignment_score_min
    )


def _control_exclusion_ok(
    *,
    control_fraction: float,
    thresholds: DecisionThresholdsConfig,
) -> bool:
    return control_fraction <= thresholds.max_control_typeB_like_fraction_for_supported


def _relative_advantage_ok(
    *,
    aggregate: AggregateMetricsSummary,
    control_results: list[ControlFamilyResultSummary],
    reference: ReferenceRuleConfig,
    thresholds: DecisionThresholdsConfig,
) -> bool:
    if aggregate.original_separation_margin is None:
        return False

    margins = _enabled_control_margins(control_results)
    if not margins:
        return False

    control_quantile = _quantile_from_sorted(margins, reference.control_margin_quantile_min)
    if control_quantile is None:
        return False

    margin_delta_ok = (
        aggregate.original_vs_control_margin_delta is not None
        and aggregate.original_vs_control_margin_delta >= thresholds.min_original_over_control_margin_delta
    )

    quantile_ok = aggregate.original_separation_margin >= control_quantile

    return margin_delta_ok and quantile_ok


def _build_interpretation(
    label: ResultLabel,
) -> str:
    if label == "type_B_exclusion_supported":
        return (
            "Original data satisfy absolute quality criteria and remain clearly stronger "
            "than controls, while enabled controls fail to reproduce robust Type-B-like structure."
        )
    if label == "type_B_exclusion_weak":
        return (
            "Original data show partial quality and controls remain mostly negative, "
            "but the relative advantage over controls is still too weak for strong support."
        )
    if label == "type_B_exclusion_failed":
        return (
            "At least one enabled control family reproduced a substantial Type-B-like pattern, "
            "or the original signal itself failed minimum quality requirements."
        )
    return (
        "Controls do not robustly reproduce Type-B-like structure, but the original signal "
        "does not yet satisfy all absolute or relative quality criteria in a stable way."
    )


def evaluate_type_b_exclusion(
    *,
    aggregate_metrics: AggregateMetricsSummary,
    control_results: list[ControlFamilyResultSummary],
    thresholds: DecisionThresholdsConfig,
    reference_rules: ReferenceRuleConfig | None = None,
) -> DecisionResult:
    """
    Evaluate the exclusion-test outcome for M.3.9x.3g.a.

    Decision order:
    1. failed
    2. supported
    3. weak
    4. ambiguous
    """
    if reference_rules is None:
        reference_rules = ReferenceRuleConfig()

    enabled_count = _count_enabled_controls(control_results)
    control_fraction = _control_typeB_like_fraction(control_results)

    original_quality_ok = _original_quality_ok(aggregate_metrics, reference_rules)
    control_exclusion_ok = _control_exclusion_ok(
        control_fraction=control_fraction,
        thresholds=thresholds,
    )
    relative_advantage_ok = _relative_advantage_ok(
        aggregate=aggregate_metrics,
        control_results=control_results,
        reference=reference_rules,
        thresholds=thresholds,
    )

    failed_conditions_met = False
    supported_conditions_met = False
    weak_conditions_met = False
    ambiguous_conditions_met = False

    robust_control_pattern = _any_enabled_control_has_robust_typeB_like_pattern(
        control_results, thresholds
    )

    if robust_control_pattern:
        failed_conditions_met = True

    if (
        aggregate_metrics.control_typeB_like_fraction is not None
        and aggregate_metrics.control_typeB_like_fraction
        > thresholds.max_control_typeB_like_fraction_for_weak
    ):
        failed_conditions_met = True

    if not original_quality_ok and control_fraction > 0.0:
        failed_conditions_met = True

    if not failed_conditions_met:
        enough_controls = enabled_count >= 2
        supported_conditions_met = (
            original_quality_ok
            and control_exclusion_ok
            and relative_advantage_ok
            and enough_controls
        )

    if not failed_conditions_met and not supported_conditions_met:
        enough_controls = enabled_count >= 2
        weak_conditions_met = (
            enough_controls
            and control_fraction <= thresholds.max_control_typeB_like_fraction_for_weak
            and (
                original_quality_ok
                or (
                    aggregate_metrics.original_stability_score is not None
                    and aggregate_metrics.original_stability_score >= thresholds.min_stability_score_for_supported
                )
                or control_exclusion_ok
            )
        )

    if not failed_conditions_met and not supported_conditions_met and not weak_conditions_met:
        ambiguous_conditions_met = True

    if failed_conditions_met:
        label: ResultLabel = "type_B_exclusion_failed"
    elif supported_conditions_met:
        label = "type_B_exclusion_supported"
    elif weak_conditions_met:
        label = "type_B_exclusion_weak"
    else:
        label = "type_B_exclusion_ambiguous"

    interpretation = _build_interpretation(label)

    trace = DecisionTraceSummary(
        thresholds_used={
            "min_stability_score_for_supported": thresholds.min_stability_score_for_supported,
            "min_original_over_control_margin_delta": thresholds.min_original_over_control_margin_delta,
            "max_control_typeB_like_fraction_for_supported": thresholds.max_control_typeB_like_fraction_for_supported,
            "max_control_typeB_like_fraction_for_weak": thresholds.max_control_typeB_like_fraction_for_weak,
            "enabled_control_count": enabled_count,
            "derived_control_typeB_like_fraction": control_fraction,
            "reference_original_separation_margin_min": reference_rules.original_separation_margin_min,
            "reference_original_stability_score_min": reference_rules.original_stability_score_min,
            "reference_original_assignment_score_min": reference_rules.original_assignment_score_min,
            "reference_control_margin_quantile_min": reference_rules.control_margin_quantile_min,
            "original_quality_ok": original_quality_ok,
            "control_exclusion_ok": control_exclusion_ok,
            "relative_advantage_ok": relative_advantage_ok,
        },
        supported_conditions_met=supported_conditions_met,
        weak_conditions_met=weak_conditions_met,
        ambiguous_conditions_met=ambiguous_conditions_met,
        failed_conditions_met=failed_conditions_met,
    )

    return DecisionResult(
        result_label=label,
        overall_interpretation=interpretation,
        decision_trace=trace,
    )


def build_aggregate_metrics(
    *,
    original_separation_margin: float | None,
    original_stability_score: float | None,
    original_assignment_score: float | None,
    control_results: list[ControlFamilyResultSummary],
) -> AggregateMetricsSummary:
    """
    Convenience helper to derive aggregate metrics from control-family summaries.

    original_vs_control_margin_delta is computed against the median control separation margin
    across enabled control families with non-null margin values.
    """
    enabled_controls = [row for row in control_results if row.enabled]

    control_margins = [
        row.separation_margin_mean
        for row in enabled_controls
        if row.separation_margin_mean is not None
    ]

    if control_margins:
        control_margin_reference = float(median(control_margins))
    else:
        control_margin_reference = None

    if (
        original_separation_margin is not None
        and control_margin_reference is not None
    ):
        original_vs_control_margin_delta = original_separation_margin - control_margin_reference
    else:
        original_vs_control_margin_delta = None

    control_fraction = _control_typeB_like_fraction(control_results)

    return AggregateMetricsSummary(
        original_separation_margin=original_separation_margin,
        original_stability_score=original_stability_score,
        original_assignment_score=original_assignment_score,
        control_typeB_like_fraction=control_fraction,
        original_vs_control_margin_delta=original_vs_control_margin_delta,
    )
