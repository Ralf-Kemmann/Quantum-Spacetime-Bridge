from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Sequence

import pandas as pd

from src.m39x3g_a.original_reference import bootstrap_original_reference


@dataclass(slots=True)
class OriginalPairCandidate:
    pair_id: str
    fsw_labels: list[str]
    ao_labels: list[str]
    notes: str = ""


@dataclass(slots=True)
class OriginalPairEvaluation:
    pair_id: str
    fsw_labels: list[str]
    ao_labels: list[str]

    fsw_n_rows: int
    ao_n_rows: int

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

    notes: str = ""


def default_original_pair_candidates() -> list[OriginalPairCandidate]:
    """
    Provisional predeclared candidate set for O1/O2/O3.
    """
    return [
        OriginalPairCandidate(
            pair_id="O1",
            fsw_labels=["FSW_D05", "FSW_D06"],
            ao_labels=["AO_A03", "AO_A04", "AO_A05"],
            notes="Primary baseline original pair.",
        ),
        OriginalPairCandidate(
            pair_id="O2",
            fsw_labels=["FSW_D05", "FSW_D06"],
            ao_labels=["AO_A04", "AO_A05", "AO_A06"],
            notes="Shifted AO window for robustness check.",
        ),
        OriginalPairCandidate(
            pair_id="O3",
            fsw_labels=["FSW_D05", "FSW_D06"],
            ao_labels=["AO_A04", "AO_A05"],
            notes="Tighter AO core candidate.",
        ),
    ]


def evaluate_original_pair_candidates(
    *,
    original_df: pd.DataFrame,
    candidates: Sequence[OriginalPairCandidate],
    feature_columns: Sequence[str],
    n_resamples: int = 100,
    seed: int = 1729,
    distance_metric: str = "euclidean",
    min_margin_threshold: float = 0.21,
    min_stability_threshold: float = 0.80,
    min_assignment_threshold: float = 0.75,
) -> list[OriginalPairEvaluation]:
    """
    Evaluate all original pair candidates with the same bootstrap protocol.
    """
    evaluations: list[OriginalPairEvaluation] = []

    for candidate in candidates:
        result = bootstrap_original_reference(
            original_df=original_df,
            fsw_labels=candidate.fsw_labels,
            ao_labels=candidate.ao_labels,
            feature_columns=feature_columns,
            n_resamples=n_resamples,
            seed=seed,
            distance_metric=distance_metric,
            min_assignment_for_positive=min_assignment_threshold,
            min_margin_for_positive=0.05,
        )

        ci_low = result.separation_margin_ci[0] if result.separation_margin_ci is not None else None
        ci_high = result.separation_margin_ci[1] if result.separation_margin_ci is not None else None

        passes_margin_threshold = result.separation_margin_mean >= min_margin_threshold
        passes_stability_threshold = result.stability_score >= min_stability_threshold
        passes_assignment_threshold = result.assignment_score_mean >= min_assignment_threshold

        overall_pass = (
            passes_margin_threshold
            and passes_stability_threshold
            and passes_assignment_threshold
        )

        evaluations.append(
            OriginalPairEvaluation(
                pair_id=candidate.pair_id,
                fsw_labels=list(candidate.fsw_labels),
                ao_labels=list(candidate.ao_labels),
                fsw_n_rows=result.fsw_n_rows,
                ao_n_rows=result.ao_n_rows,
                separation_margin_mean=result.separation_margin_mean,
                separation_margin_ci_low=ci_low,
                separation_margin_ci_high=ci_high,
                separation_ratio_mean=result.separation_ratio_mean,
                assignment_score_mean=result.assignment_score_mean,
                stability_score=result.stability_score,
                passes_margin_threshold=passes_margin_threshold,
                passes_stability_threshold=passes_stability_threshold,
                passes_assignment_threshold=passes_assignment_threshold,
                overall_pass=overall_pass,
                notes=candidate.notes,
            )
        )

    return evaluations


def rank_original_pair_evaluations(
    evaluations: Sequence[OriginalPairEvaluation],
) -> list[OriginalPairEvaluation]:
    """
    Defensive ranking protocol:
    1. overall_pass
    2. passes_margin_threshold
    3. passes_stability_threshold
    4. passes_assignment_threshold
    5. separation_margin_mean
    6. assignment_score_mean
    """
    return sorted(
        evaluations,
        key=lambda x: (
            x.overall_pass,
            x.passes_margin_threshold,
            x.passes_stability_threshold,
            x.passes_assignment_threshold,
            x.separation_margin_mean,
            x.assignment_score_mean,
        ),
        reverse=True,
    )


def evaluations_to_dataframe(
    evaluations: Sequence[OriginalPairEvaluation],
) -> pd.DataFrame:
    return pd.DataFrame([asdict(e) for e in evaluations])


def evaluate_and_rank_default_candidates(
    *,
    original_df: pd.DataFrame,
    feature_columns: Sequence[str],
    n_resamples: int = 100,
    seed: int = 1729,
    distance_metric: str = "euclidean",
    min_margin_threshold: float = 0.21,
    min_stability_threshold: float = 0.80,
    min_assignment_threshold: float = 0.75,
) -> pd.DataFrame:
    candidates = default_original_pair_candidates()
    evaluations = evaluate_original_pair_candidates(
        original_df=original_df,
        candidates=candidates,
        feature_columns=feature_columns,
        n_resamples=n_resamples,
        seed=seed,
        distance_metric=distance_metric,
        min_margin_threshold=min_margin_threshold,
        min_stability_threshold=min_stability_threshold,
        min_assignment_threshold=min_assignment_threshold,
    )
    ranked = rank_original_pair_evaluations(evaluations)
    return evaluations_to_dataframe(ranked)