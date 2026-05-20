#!/usr/bin/env python3
"""
QSB-ST-COMP01-C2 candidate metric inspection scanner.

Synthetic diagnostic scanner only. Psi is a diagnostic pattern object here,
not automatically a physical wavefunction. real_imag_proxy is a diagnostic
component split, not a physical derivation. Component-resolved psi channels
are diagnostic decomposition channels, not physical observables by themselves.
Identity-sensitive contrasts are diagnostic control checks, not physical
observables by themselves. Multi-seed value-permutation label_shuffle controls
are diagnostic harder-control approximations, not physical control families.
Psi-overlap is a compatibility observable, not automatically a quantum
measurement probability. Tau is not physical time, not proper time, and not a
universal clock. COMP01-C2 does not attach D(A,B), does not construct S_rel2,
does not derive a Lorentzian metric, does not validate a physical Bridge, and
does not establish diagnostic specificity yet.
"""
from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

BLOCK = "QSB-ST-COMP01C2"
STATUS = "COMP01C2_candidate_metric_inspection_implemented_and_run_checked"
INPUT_FILE = Path(
    "runs/QSB-ST-COMP01B/component_resolved_compatibility_open/"
    "component_compatibility_pairwise.csv"
)
OUTPUT_DIR = Path("runs/QSB-ST-COMP01C2/candidate_metric_harder_label_shuffle_open")
COMPARISON_FOCUS = "structured_local_phase_response_vs_multi_seed_label_shuffle_value_permutation"
CONTROL_MODE = "multi_seed_label_shuffle_value_permutation"
STRUCTURED_FAMILY = "structured_local_phase_response"
LABEL_SHUFFLE_FAMILY = "label_shuffle"
COMPONENT_SPLIT_MODE = "real_imag_proxy"
ETA = 1e-12
PAIR_NEAR_EQUAL_TOL = 1e-12
PAIR_COUNT_EXPECTED = 64
TOP_QUARTILE_COUNT = 16
SHUFFLE_SEEDS = list(range(1000, 1020))
RANK_CORRELATION_CANDIDATE_THRESHOLD = 0.5
TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD = 0.5
STRONG_RANK_CORRELATION_THRESHOLD = 0.3
STRONG_TOP_QUARTILE_OVERLAP_THRESHOLD = 0.35
MIMIC_RANK_CORRELATION_THRESHOLD = 0.8
MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD = 0.75
PRIMARY_CANDIDATE_METRICS = [
    "sin_sin_overlap",
    "component_resolved_relative_phase_similarity",
]
SECONDARY_CONTEXT_METRICS = [
    "cos_cos_overlap",
    "component_resolved_local_pattern_correlation",
    "component_asymmetry_delta",
]
INSPECTED_METRICS = PRIMARY_CANDIDATE_METRICS + SECONDARY_CONTEXT_METRICS
INSPECTION_FIELDS = [
    "metric_name",
    "metric_role",
    "control_mode",
    "pair_count",
    "seed_count",
    "mean_structured",
    "mean_control",
    "mean_delta",
    "mean_abs_delta",
    "median_abs_delta",
    "max_abs_delta",
    "structured_greater_count_mean",
    "control_greater_count_mean",
    "near_equal_count_mean",
    "rank_correlation_mean",
    "rank_correlation_std",
    "top_quartile_overlap_mean",
    "top_quartile_overlap_std",
    "top_pair_structured_mode",
    "top_pair_control_mode",
    "inspection_status",
    "warning",
]
SEED_FIELDS = [
    "metric_name",
    "metric_role",
    "control_mode",
    "shuffle_seed",
    "pair_count",
    "mean_structured",
    "mean_control",
    "mean_abs_delta",
    "small_delta_threshold",
    "rank_correlation",
    "top_quartile_overlap",
    "identity_sensitive_signal",
    "top_pair_structured",
    "top_pair_control",
    "candidate_signal_status",
    "warning",
]
DECISION_FIELDS = [
    "metric_name",
    "candidate_signal_count",
    "seed_count",
    "candidate_signal_fraction",
    "mean_rank_correlation",
    "std_rank_correlation",
    "mean_top_quartile_overlap",
    "std_top_quartile_overlap",
    "mean_abs_delta_mean",
    "decision_status",
    "recommended_followup",
    "specificity_status",
    "warning",
]
CLAIM_BOUNDARY = (
    "synthetic candidate metric inspection only; multi-seed value-permutation "
    "label_shuffle controls preserve existing control value distributions while "
    "breaking pair identity; multi-seed value-permutation label_shuffle controls "
    "are diagnostic harder-control approximations, not physical control "
    "families; real_imag_proxy is a diagnostic component split, not a physical "
    "derivation; psi is diagnostic pattern object, not physical wavefunction; "
    "component-resolved psi channels are diagnostic decomposition channels, not "
    "physical observables by themselves; identity-sensitive contrasts are "
    "diagnostic control checks, not physical observables by themselves; "
    "psi-overlap is a compatibility observable, not automatically a quantum "
    "measurement probability; tau is not physical time, not proper time, and "
    "not a universal clock; COMP01-C2 does not attach D(A,B), does not "
    "construct S_rel2, does not derive a Lorentzian metric, does not validate "
    "a physical Bridge, and does not establish diagnostic specificity yet; "
    "this is synthetic diagnostic work only."
)

PairId = Tuple[str, str]


def read_input_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing input file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def require_component_split_mode(rows: Sequence[Dict[str, str]]) -> str:
    modes = sorted({row.get("component_split_mode", "") for row in rows})
    if modes != [COMPONENT_SPLIT_MODE]:
        raise SystemExit(
            "component_split_mode must be real_imag_proxy; "
            f"found: {modes}"
        )
    return COMPONENT_SPLIT_MODE


def parse_float(value: str) -> Optional[float]:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def collect_family_metric_values(
    rows: Sequence[Dict[str, str]],
    family: str,
    metric: str,
) -> Tuple[Dict[PairId, float], List[str]]:
    values: Dict[PairId, float] = {}
    warnings: List[str] = []
    for row in rows:
        if row.get("family") != family:
            continue
        pair = (row.get("source_id", ""), row.get("target_id", ""))
        parsed = parse_float(row.get(metric, ""))
        if parsed is None:
            warnings.append("value_parse_warning")
            continue
        values[pair] = parsed
    return values, warnings


def rank_descending(values: Dict[PairId, float]) -> Tuple[Dict[PairId, float], bool]:
    sorted_items = sorted(values.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    ranks: Dict[PairId, float] = {}
    tie_found = False
    idx = 0
    while idx < len(sorted_items):
        jdx = idx + 1
        while jdx < len(sorted_items) and sorted_items[jdx][1] == sorted_items[idx][1]:
            jdx += 1
        if jdx - idx > 1:
            tie_found = True
        rank_value = (idx + 1 + jdx) / 2.0
        for pair, _value in sorted_items[idx:jdx]:
            ranks[pair] = rank_value
        idx = jdx
    return ranks, tie_found


def pearson_rank_correlation(
    structured_ranks: Sequence[float],
    control_ranks: Sequence[float],
) -> Optional[float]:
    rank_s = np.asarray(structured_ranks, dtype=float)
    rank_c = np.asarray(control_ranks, dtype=float)
    std_s = float(np.std(rank_s))
    std_c = float(np.std(rank_c))
    if std_s <= ETA or std_c <= ETA:
        return None
    centered_s = rank_s - float(np.mean(rank_s))
    centered_c = rank_c - float(np.mean(rank_c))
    corr = float(np.mean(centered_s * centered_c) / (std_s * std_c))
    if not math.isfinite(corr):
        return None
    return corr


def format_float(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.12g}"


def joined_warnings(parts: Iterable[str]) -> str:
    clean = [part for part in parts if part]
    return ";".join(dict.fromkeys(clean))


def metric_role(metric: str) -> str:
    if metric in PRIMARY_CANDIDATE_METRICS:
        return "primary_candidate"
    return "secondary_context"


def top_pair(values: Dict[PairId, float], ranks: Dict[PairId, float]) -> str:
    top = sorted(values, key=lambda pair: (ranks[pair], pair[0], pair[1]))[0]
    return f"{top[0]}->{top[1]}"


def mode_text(values: Sequence[str]) -> str:
    counts = Counter(values)
    if not counts:
        return ""
    max_count = max(counts.values())
    return sorted(value for value, count in counts.items() if count == max_count)[0]


def decide_seed_status(
    identity_signal: bool,
    rank_correlation: Optional[float],
    top_quartile_overlap: float,
    mean_abs_delta: float,
    small_delta_threshold: float,
) -> str:
    if rank_correlation is None:
        return "undefined_seed"
    if identity_signal:
        return "identity_sensitive_candidate_seed"
    if (
        rank_correlation >= MIMIC_RANK_CORRELATION_THRESHOLD
        and top_quartile_overlap >= MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "label_shuffle_mimic_warning_seed"
    if (
        rank_correlation < RANK_CORRELATION_CANDIDATE_THRESHOLD
        or top_quartile_overlap <= TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD
    ) and mean_abs_delta <= small_delta_threshold:
        return "rank_shift_without_magnitude_warning_seed"
    return "inconclusive_seed"


def decision_status(
    candidate_signal_fraction: float,
    mean_rank_correlation: Optional[float],
    mean_top_quartile_overlap: float,
) -> str:
    if mean_rank_correlation is None:
        return "inconclusive_candidate"
    if (
        candidate_signal_fraction >= 0.8
        and mean_rank_correlation < STRONG_RANK_CORRELATION_THRESHOLD
        and mean_top_quartile_overlap <= STRONG_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "strong_identity_sensitive_candidate_for_followup"
    if (
        candidate_signal_fraction >= 0.6
        and mean_rank_correlation < RANK_CORRELATION_CANDIDATE_THRESHOLD
        and mean_top_quartile_overlap <= TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD
    ):
        return "identity_sensitive_candidate_for_followup"
    if (
        mean_rank_correlation >= MIMIC_RANK_CORRELATION_THRESHOLD
        and mean_top_quartile_overlap >= MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "label_shuffle_mimic_warning"
    return "inconclusive_candidate"


def recommended_followup(status: str) -> str:
    if status == "strong_identity_sensitive_candidate_for_followup":
        return "inspect_with_real_kernel_resimulation_and_harder_nulls"
    if status == "identity_sensitive_candidate_for_followup":
        return "continue_with_harder_nulls_and_candidate_inspection"
    if status == "label_shuffle_mimic_warning":
        return "redesign_or_deprioritize_metric"
    return "inspect_but_do_not_promote_metric"


def inspection_status_for_metric(role: str, decision: Optional[str]) -> str:
    if role == "secondary_context":
        return "context_only"
    if decision in {
        "strong_identity_sensitive_candidate_for_followup",
        "identity_sensitive_candidate_for_followup",
    }:
        return "candidate_stable"
    if decision == "label_shuffle_mimic_warning":
        return "label_shuffle_mimic_warning"
    if decision == "inconclusive_candidate":
        return "candidate_unstable"
    return "inconclusive"


def build_permuted_control(
    pairs: Sequence[PairId],
    label_values: Dict[PairId, float],
    seed: int,
) -> Dict[PairId, float]:
    values = np.asarray([label_values[pair] for pair in pairs], dtype=float)
    rng = np.random.default_rng(seed)
    permuted = rng.permutation(values)
    return {pair: float(value) for pair, value in zip(pairs, permuted)}


def compute_seed_row(
    metric: str,
    seed: int,
    pairs: Sequence[PairId],
    structured: Dict[PairId, float],
    control: Dict[PairId, float],
    structured_ranks: Dict[PairId, float],
    structured_tie: bool,
) -> Dict[str, object]:
    control_ranks, control_tie = rank_descending(control)
    rank_correlation = pearson_rank_correlation(
        [structured_ranks[pair] for pair in pairs],
        [control_ranks[pair] for pair in pairs],
    )
    structured_top_pairs = {
        pair for pair in pairs if structured_ranks[pair] <= TOP_QUARTILE_COUNT
    }
    control_top_pairs = {
        pair for pair in pairs if control_ranks[pair] <= TOP_QUARTILE_COUNT
    }
    top_overlap = len(structured_top_pairs & control_top_pairs) / float(TOP_QUARTILE_COUNT)

    deltas = [structured[pair] - control[pair] for pair in pairs]
    abs_deltas = [abs(delta) for delta in deltas]
    mean_structured = float(np.mean([structured[pair] for pair in pairs]))
    mean_control = float(np.mean([control[pair] for pair in pairs]))
    mean_abs_delta = float(np.mean(abs_deltas))
    small_delta_threshold = max(
        ETA,
        0.05 * max(abs(mean_structured), abs(mean_control), ETA),
    )
    identity_signal = (
        mean_abs_delta > small_delta_threshold
        and rank_correlation is not None
        and rank_correlation < RANK_CORRELATION_CANDIDATE_THRESHOLD
        and top_overlap <= TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD
    )
    status = decide_seed_status(
        identity_signal,
        rank_correlation,
        top_overlap,
        mean_abs_delta,
        small_delta_threshold,
    )
    warnings: List[str] = []
    if structured_tie or control_tie:
        warnings.append("rank_tie_warning")
    if rank_correlation is None:
        warnings.append("undefined_rank_warning")
    return {
        "metric_name": metric,
        "metric_role": metric_role(metric),
        "control_mode": CONTROL_MODE,
        "shuffle_seed": seed,
        "pair_count": len(pairs),
        "mean_structured": mean_structured,
        "mean_control": mean_control,
        "mean_abs_delta": mean_abs_delta,
        "small_delta_threshold": small_delta_threshold,
        "rank_correlation": rank_correlation,
        "top_quartile_overlap": top_overlap,
        "identity_sensitive_signal": identity_signal,
        "top_pair_structured": top_pair(structured, structured_ranks),
        "top_pair_control": top_pair(control, control_ranks),
        "candidate_signal_status": status,
        "warning": joined_warnings(warnings),
        "_mean_delta": float(np.mean(deltas)),
        "_median_abs_delta": float(median(abs_deltas)),
        "_max_abs_delta": float(max(abs_deltas)),
        "_structured_greater_count": sum(1 for delta in deltas if delta > PAIR_NEAR_EQUAL_TOL),
        "_control_greater_count": sum(1 for delta in deltas if delta < -PAIR_NEAR_EQUAL_TOL),
        "_near_equal_count": sum(1 for delta in deltas if abs(delta) <= PAIR_NEAR_EQUAL_TOL),
    }


def mean_optional(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return float(np.mean(clean))


def std_optional(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return float(np.std(clean))


def build_outputs(
    rows: Sequence[Dict[str, str]]
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    seed_rows: List[Dict[str, object]] = []
    inspection_rows: List[Dict[str, object]] = []
    decision_rows: List[Dict[str, object]] = []
    decisions_by_metric: Dict[str, str] = {}

    metric_seed_rows: Dict[str, List[Dict[str, object]]] = {}
    structured_by_metric: Dict[str, Dict[PairId, float]] = {}

    for metric in INSPECTED_METRICS:
        structured, structured_warnings = collect_family_metric_values(
            rows, STRUCTURED_FAMILY, metric
        )
        label_shuffle, label_warnings = collect_family_metric_values(
            rows, LABEL_SHUFFLE_FAMILY, metric
        )
        pairs = sorted(set(structured) & set(label_shuffle))
        warnings = list(structured_warnings) + list(label_warnings)
        if len(pairs) != PAIR_COUNT_EXPECTED:
            warnings.append("missing_pair_warning")
        structured = {pair: structured[pair] for pair in pairs}
        label_shuffle = {pair: label_shuffle[pair] for pair in pairs}
        structured_ranks, structured_tie = rank_descending(structured)
        if structured_tie:
            warnings.append("rank_tie_warning")
        structured_by_metric[metric] = structured

        rows_for_metric: List[Dict[str, object]] = []
        for seed in SHUFFLE_SEEDS:
            control = build_permuted_control(pairs, label_shuffle, seed)
            seed_row = compute_seed_row(
                metric, seed, pairs, structured, control, structured_ranks, structured_tie
            )
            if warnings:
                seed_row["warning"] = joined_warnings(
                    [str(seed_row["warning"])] + warnings
                )
            rows_for_metric.append(seed_row)
            seed_rows.append(seed_row)
        metric_seed_rows[metric] = rows_for_metric

    for metric in PRIMARY_CANDIDATE_METRICS:
        rows_for_metric = metric_seed_rows[metric]
        candidate_count = sum(
            1
            for row in rows_for_metric
            if row["candidate_signal_status"] == "identity_sensitive_candidate_seed"
        )
        seed_count = len(rows_for_metric)
        candidate_fraction = candidate_count / float(seed_count)
        rank_corrs = [row["rank_correlation"] for row in rows_for_metric]
        top_overlaps = [float(row["top_quartile_overlap"]) for row in rows_for_metric]
        mean_abs_deltas = [float(row["mean_abs_delta"]) for row in rows_for_metric]
        mean_rank_corr = mean_optional(rank_corrs)  # type: ignore[arg-type]
        mean_top_overlap = float(np.mean(top_overlaps))
        status = decision_status(candidate_fraction, mean_rank_corr, mean_top_overlap)
        decisions_by_metric[metric] = status
        decision_rows.append(
            {
                "metric_name": metric,
                "candidate_signal_count": candidate_count,
                "seed_count": seed_count,
                "candidate_signal_fraction": candidate_fraction,
                "mean_rank_correlation": mean_rank_corr,
                "std_rank_correlation": std_optional(rank_corrs),  # type: ignore[arg-type]
                "mean_top_quartile_overlap": mean_top_overlap,
                "std_top_quartile_overlap": float(np.std(top_overlaps)),
                "mean_abs_delta_mean": float(np.mean(mean_abs_deltas)),
                "decision_status": status,
                "recommended_followup": recommended_followup(status),
                "specificity_status": "specificity_not_established",
                "warning": joined_warnings(str(row["warning"]) for row in rows_for_metric),
            }
        )

    for metric in INSPECTED_METRICS:
        rows_for_metric = metric_seed_rows[metric]
        role = metric_role(metric)
        structured = structured_by_metric[metric]
        mean_structured = float(np.mean(list(structured.values())))
        rank_corrs = [row["rank_correlation"] for row in rows_for_metric]
        top_overlaps = [float(row["top_quartile_overlap"]) for row in rows_for_metric]
        inspection_rows.append(
            {
                "metric_name": metric,
                "metric_role": role,
                "control_mode": CONTROL_MODE,
                "pair_count": PAIR_COUNT_EXPECTED,
                "seed_count": len(SHUFFLE_SEEDS),
                "mean_structured": mean_structured,
                "mean_control": float(np.mean([float(row["mean_control"]) for row in rows_for_metric])),
                "mean_delta": float(np.mean([float(row["_mean_delta"]) for row in rows_for_metric])),
                "mean_abs_delta": float(np.mean([float(row["mean_abs_delta"]) for row in rows_for_metric])),
                "median_abs_delta": float(np.mean([float(row["_median_abs_delta"]) for row in rows_for_metric])),
                "max_abs_delta": float(max(float(row["_max_abs_delta"]) for row in rows_for_metric)),
                "structured_greater_count_mean": float(
                    np.mean([float(row["_structured_greater_count"]) for row in rows_for_metric])
                ),
                "control_greater_count_mean": float(
                    np.mean([float(row["_control_greater_count"]) for row in rows_for_metric])
                ),
                "near_equal_count_mean": float(
                    np.mean([float(row["_near_equal_count"]) for row in rows_for_metric])
                ),
                "rank_correlation_mean": mean_optional(rank_corrs),  # type: ignore[arg-type]
                "rank_correlation_std": std_optional(rank_corrs),  # type: ignore[arg-type]
                "top_quartile_overlap_mean": float(np.mean(top_overlaps)),
                "top_quartile_overlap_std": float(np.std(top_overlaps)),
                "top_pair_structured_mode": mode_text(
                    [str(row["top_pair_structured"]) for row in rows_for_metric]
                ),
                "top_pair_control_mode": mode_text(
                    [str(row["top_pair_control"]) for row in rows_for_metric]
                ),
                "inspection_status": inspection_status_for_metric(
                    role, decisions_by_metric.get(metric)
                ),
                "warning": joined_warnings(str(row["warning"]) for row in rows_for_metric),
            }
        )

    for row in seed_rows:
        for key in list(row):
            if key.startswith("_"):
                del row[key]

    return inspection_rows, seed_rows, decision_rows


def write_csv(path: Path, fields: Sequence[str], rows: Sequence[Dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            formatted = {
                key: format_float(value) if isinstance(value, float) else value
                for key, value in row.items()
            }
            writer.writerow(formatted)


def write_json(path: Path, payload: Dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_readout(
    path: Path,
    inspection_rows: Sequence[Dict[str, object]],
    decision_rows: Sequence[Dict[str, object]],
    stable_metrics: Sequence[str],
    unstable_metrics: Sequence[str],
    mimic_metrics: Sequence[str],
) -> None:
    decision_lines = [
        f"- {row['metric_name']}: {row['decision_status']}, "
        f"candidate_signal_fraction={row['candidate_signal_fraction']}"
        for row in decision_rows
    ]
    warning_lines = [
        f"- {row['metric_name']}: {row['warning']}"
        for row in inspection_rows
        if row.get("warning")
    ]
    text = f"""# QSB-ST-COMP01-C2 Candidate Metric Inspection Readout

## Purpose

The COMP01-C2 scanner tests whether the two COMP01-C candidate metrics remain stable under deterministic multi-seed value-permutation label_shuffle controls. This preserves the existing label_shuffle value distribution while breaking pair identity. It is a synthetic harder-control approximation, not a newly simulated physical control family. It does not establish physical wavefunctions, physical time, Lorentz structure, D(A,B), S_rel2, or Bridge validation.

## Input basis

- Input file: {INPUT_FILE}
- Comparison focus: {COMPARISON_FOCUS}
- Pair count: {PAIR_COUNT_EXPECTED}
- Shuffle seeds: {SHUFFLE_SEEDS}

## Control mode

{CONTROL_MODE}

COMP01-C2 smoke mode uses deterministic value-permutation label_shuffle controls over existing COMP01-B label_shuffle values. This preserves the control value distribution while breaking pair identity. It is a diagnostic harder-control approximation, not a newly simulated physical control family.

## Component split mode

{COMPONENT_SPLIT_MODE}

real_imag_proxy is a diagnostic component split, not a physical derivation.

## Candidate metrics

- Primary: {PRIMARY_CANDIDATE_METRICS}
- Secondary context: {SECONDARY_CONTEXT_METRICS}

## Output files

- {OUTPUT_DIR / "candidate_metric_inspection_summary.csv"}
- {OUTPUT_DIR / "harder_label_shuffle_seed_summary.csv"}
- {OUTPUT_DIR / "candidate_metric_decision.csv"}
- {OUTPUT_DIR / "summary.json"}
- {OUTPUT_DIR / "readout.md"}
- {OUTPUT_DIR / "config_resolved.json"}

## Multi-seed label_shuffle stability summary

{chr(10).join(decision_lines)}

## Candidate movement

- stable_candidate_metrics: {list(stable_metrics)}
- unstable_or_inconclusive_metrics: {list(unstable_metrics)}
- label_shuffle_mimic_warning_metrics: {list(mimic_metrics)}

## Warnings

{chr(10).join(warning_lines) if warning_lines else "- none"}

## Claim Boundary

{CLAIM_BOUNDARY}
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    rows = read_input_rows(INPUT_FILE)
    component_split_mode = require_component_split_mode(rows)
    inspection_rows, seed_rows, decision_rows = build_outputs(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUTPUT_DIR / "candidate_metric_inspection_summary.csv",
        INSPECTION_FIELDS,
        inspection_rows,
    )
    write_csv(
        OUTPUT_DIR / "harder_label_shuffle_seed_summary.csv",
        SEED_FIELDS,
        seed_rows,
    )
    write_csv(
        OUTPUT_DIR / "candidate_metric_decision.csv",
        DECISION_FIELDS,
        decision_rows,
    )

    stable_metrics = [
        str(row["metric_name"])
        for row in decision_rows
        if row["decision_status"]
        in {
            "strong_identity_sensitive_candidate_for_followup",
            "identity_sensitive_candidate_for_followup",
        }
    ]
    mimic_metrics = [
        str(row["metric_name"])
        for row in decision_rows
        if row["decision_status"] == "label_shuffle_mimic_warning"
    ]
    unstable_metrics = [
        str(row["metric_name"])
        for row in decision_rows
        if row["metric_name"] not in stable_metrics and row["metric_name"] not in mimic_metrics
    ]

    summary = {
        "block": BLOCK,
        "status": STATUS,
        "input_file": str(INPUT_FILE),
        "output_dir": str(OUTPUT_DIR),
        "comparison_focus": COMPARISON_FOCUS,
        "control_mode": CONTROL_MODE,
        "component_split_mode": component_split_mode,
        "seed_count": len(SHUFFLE_SEEDS),
        "shuffle_seeds": SHUFFLE_SEEDS,
        "pair_count": PAIR_COUNT_EXPECTED,
        "inspected_metric_count": len(INSPECTED_METRICS),
        "primary_metric_count": len(PRIMARY_CANDIDATE_METRICS),
        "candidate_metric_inspection_summary_row_count": len(inspection_rows),
        "harder_label_shuffle_seed_summary_row_count": len(seed_rows),
        "candidate_metric_decision_row_count": len(decision_rows),
        "primary_candidate_metrics": PRIMARY_CANDIDATE_METRICS,
        "secondary_context_metrics": SECONDARY_CONTEXT_METRICS,
        "stable_candidate_metrics": stable_metrics,
        "unstable_or_inconclusive_metrics": unstable_metrics,
        "label_shuffle_mimic_warning_metrics": mimic_metrics,
        "specificity_established": False,
        "tau_model_constructed": False,
        "D_AB_attached": False,
        "S_rel2_constructed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(OUTPUT_DIR / "summary.json", summary)

    config = {
        "block": BLOCK,
        "input_file": str(INPUT_FILE),
        "output_dir": str(OUTPUT_DIR),
        "comparison_focus": COMPARISON_FOCUS,
        "control_mode": CONTROL_MODE,
        "component_split_mode": component_split_mode,
        "primary_candidate_metrics": PRIMARY_CANDIDATE_METRICS,
        "secondary_context_metrics": SECONDARY_CONTEXT_METRICS,
        "seed_count": len(SHUFFLE_SEEDS),
        "shuffle_seeds": SHUFFLE_SEEDS,
        "pair_count_expected": PAIR_COUNT_EXPECTED,
        "top_quartile_count": TOP_QUARTILE_COUNT,
        "rank_correlation_method": "pearson_on_descending_value_ranks",
        "ranking_method": "descending_value_average_rank_with_pair_id_tiebreak_sort",
        "small_delta_threshold_rule": (
            "max(1e-12, 0.05 * max(abs(mean_structured), "
            "abs(mean_control), 1e-12))"
        ),
        "rank_correlation_candidate_threshold": RANK_CORRELATION_CANDIDATE_THRESHOLD,
        "top_quartile_overlap_candidate_threshold": TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD,
        "strong_rank_correlation_threshold": STRONG_RANK_CORRELATION_THRESHOLD,
        "strong_top_quartile_overlap_threshold": STRONG_TOP_QUARTILE_OVERLAP_THRESHOLD,
        "specificity_default": False,
    }
    write_json(OUTPUT_DIR / "config_resolved.json", config)
    write_readout(
        OUTPUT_DIR / "readout.md",
        inspection_rows,
        decision_rows,
        stable_metrics,
        unstable_metrics,
        mimic_metrics,
    )

    print(STATUS)
    print(f"input_file: {INPUT_FILE}")
    print(f"output_dir: {OUTPUT_DIR}")
    print(f"control_mode: {CONTROL_MODE}")
    print(f"seed_count: {len(SHUFFLE_SEEDS)}")
    print(f"candidate_metric_inspection_summary_row_count: {len(inspection_rows)}")
    print(f"harder_label_shuffle_seed_summary_row_count: {len(seed_rows)}")
    print(f"candidate_metric_decision_row_count: {len(decision_rows)}")
    print(f"stable_candidate_metrics: {stable_metrics}")
    print(f"unstable_or_inconclusive_metrics: {unstable_metrics}")
    print(f"label_shuffle_mimic_warning_metrics: {mimic_metrics}")
    print("specificity_established: False")


if __name__ == "__main__":
    main()
