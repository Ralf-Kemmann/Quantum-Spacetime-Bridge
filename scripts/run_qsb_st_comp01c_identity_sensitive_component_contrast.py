#!/usr/bin/env python3
"""
QSB-ST-COMP01-C identity-sensitive component contrast scanner.

Synthetic diagnostic control scanner only. Psi is a diagnostic pattern object
here, not automatically a physical wavefunction. real_imag_proxy is a
diagnostic component split, not a physical derivation. Component-resolved psi
channels are diagnostic decomposition channels, not physical observables by
themselves. Identity-sensitive contrasts are diagnostic control checks, not
physical observables by themselves. Psi-overlap is a compatibility observable,
not automatically a quantum measurement probability. Tau is not physical time,
not proper time, and not a universal clock. COMP01-C does not attach D(A,B),
does not construct S_rel2, does not derive a Lorentzian metric, does not
validate a physical Bridge, and does not establish diagnostic specificity yet.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import median
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

BLOCK = "QSB-ST-COMP01C"
STATUS = "COMP01C_identity_sensitive_component_contrast_implemented_and_run_checked"
INPUT_FILE = Path(
    "runs/QSB-ST-COMP01B/component_resolved_compatibility_open/"
    "component_compatibility_pairwise.csv"
)
OUTPUT_DIR = Path("runs/QSB-ST-COMP01C/identity_sensitive_component_contrast_open")
COMPARISON_FOCUS = "structured_local_phase_response_vs_label_shuffle"
STRUCTURED_FAMILY = "structured_local_phase_response"
LABEL_SHUFFLE_FAMILY = "label_shuffle"
COMPONENT_SPLIT_MODE = "real_imag_proxy"
ETA = 1e-12
PAIR_NEAR_EQUAL_TOL = 1e-12
PAIR_COUNT_EXPECTED = 64
TOP_QUARTILE_COUNT = 16
RANK_CORRELATION_THRESHOLD = 0.5
TOP_QUARTILE_OVERLAP_THRESHOLD = 0.5
MIMIC_RANK_CORRELATION_THRESHOLD = 0.8
MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD = 0.75
SELECTED_METRICS = [
    "component_asymmetry_delta",
    "component_balance_ratio",
    "cos_cos_overlap",
    "sin_sin_overlap",
    "component_resolved_relative_phase_similarity",
    "component_resolved_local_pattern_correlation",
]
PAIRWISE_FIELDS = [
    "metric_name",
    "source_id",
    "target_id",
    "structured_value",
    "label_shuffle_value",
    "delta",
    "abs_delta",
    "signed_direction",
    "structured_rank",
    "label_shuffle_rank",
    "rank_delta",
    "structured_top_quartile",
    "label_shuffle_top_quartile",
    "pair_identity_status",
    "warning",
]
RANK_SUMMARY_FIELDS = [
    "metric_name",
    "pair_count",
    "mean_structured",
    "mean_label_shuffle",
    "mean_abs_delta",
    "median_abs_delta",
    "max_abs_delta",
    "small_delta_threshold",
    "rank_correlation",
    "top_quartile_overlap",
    "top_pair_structured",
    "top_pair_label_shuffle",
    "identity_shift_status",
    "warning",
]
CONTROL_DECISION_FIELDS = [
    "metric_name",
    "identity_sensitive_signal",
    "rank_shift_status",
    "top_quartile_status",
    "pairwise_delta_status",
    "overall_label_shuffle_status",
    "recommended_followup",
    "specificity_status",
    "warning",
]
CLAIM_BOUNDARY = (
    "synthetic identity-sensitive diagnostic contrast only; real_imag_proxy is "
    "a diagnostic component split, not a physical derivation; psi is diagnostic "
    "pattern object, not physical wavefunction; component-resolved psi channels "
    "are diagnostic decomposition channels, not physical observables by "
    "themselves; identity-sensitive contrasts are diagnostic control checks, "
    "not physical observables by themselves; psi-overlap is a compatibility "
    "observable, not automatically a quantum measurement probability; tau is "
    "not physical time, not proper time, and not a universal clock; COMP01-C "
    "does not attach D(A,B), does not construct S_rel2, does not derive a "
    "Lorentzian metric, does not validate a physical Bridge, and does not "
    "establish diagnostic specificity yet; this is synthetic diagnostic work "
    "only."
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
    label_shuffle_ranks: Sequence[float],
) -> Optional[float]:
    rank_s = np.asarray(structured_ranks, dtype=float)
    rank_l = np.asarray(label_shuffle_ranks, dtype=float)
    std_s = float(np.std(rank_s))
    std_l = float(np.std(rank_l))
    if std_s <= ETA or std_l <= ETA:
        return None
    centered_s = rank_s - float(np.mean(rank_s))
    centered_l = rank_l - float(np.mean(rank_l))
    corr = float(np.mean(centered_s * centered_l) / (std_s * std_l))
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


def signed_direction(delta: float, abs_delta: float) -> str:
    if abs_delta <= PAIR_NEAR_EQUAL_TOL:
        return "near_equal"
    if delta > 0:
        return "structured_greater"
    if delta < 0:
        return "label_shuffle_greater"
    return "undefined"


def top_pair(values: Dict[PairId, float], ranks: Dict[PairId, float]) -> str:
    top = sorted(values, key=lambda pair: (ranks[pair], pair[0], pair[1]))[0]
    return f"{top[0]}->{top[1]}"


def decide_rank_shift_status(
    identity_signal: bool,
    rank_correlation: Optional[float],
    top_quartile_overlap: float,
    mean_abs_delta: float,
    small_delta_threshold: float,
) -> str:
    if rank_correlation is None:
        return "undefined_rank_behavior"
    if identity_signal:
        return "identity_sensitive_rank_top_candidate"
    if (
        rank_correlation >= MIMIC_RANK_CORRELATION_THRESHOLD
        and top_quartile_overlap >= MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "label_shuffle_rank_top_mimic_warning"
    if (
        rank_correlation < RANK_CORRELATION_THRESHOLD
        or top_quartile_overlap <= TOP_QUARTILE_OVERLAP_THRESHOLD
    ) and mean_abs_delta <= small_delta_threshold:
        return "rank_shift_without_magnitude_warning"
    return "inconclusive_rank_top_behavior"


def decide_overall_status(
    identity_signal: bool,
    rank_correlation: Optional[float],
    top_quartile_overlap: float,
    mean_abs_delta: float,
    small_delta_threshold: float,
) -> str:
    if rank_correlation is None:
        return "undefined"
    if identity_signal:
        return "identity_sensitive_candidate"
    if (
        rank_correlation >= MIMIC_RANK_CORRELATION_THRESHOLD
        and top_quartile_overlap >= MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "label_shuffle_mimics_structured_warning"
    if (
        rank_correlation < RANK_CORRELATION_THRESHOLD
        or top_quartile_overlap <= TOP_QUARTILE_OVERLAP_THRESHOLD
    ) and mean_abs_delta <= small_delta_threshold:
        return "rank_shift_without_magnitude_warning"
    return "inconclusive_identity_signal"


def recommended_followup(overall_status: str, identity_signal: bool) -> str:
    if identity_signal:
        return "continue_with_candidate_metric_inspection"
    if overall_status == "label_shuffle_mimics_structured_warning":
        return "redesign_metric_or_add_harder_null"
    if overall_status == "inconclusive_identity_signal":
        return "inspect_metric_but_no_specificity_claim"
    return "do_not_promote_metric"


def build_outputs(
    rows: Sequence[Dict[str, str]]
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
    pairwise_rows: List[Dict[str, object]] = []
    rank_summary_rows: List[Dict[str, object]] = []
    control_decision_rows: List[Dict[str, object]] = []

    for metric in SELECTED_METRICS:
        structured, structured_warnings = collect_family_metric_values(
            rows, STRUCTURED_FAMILY, metric
        )
        label_shuffle, label_warnings = collect_family_metric_values(
            rows, LABEL_SHUFFLE_FAMILY, metric
        )
        common_pairs = sorted(set(structured) & set(label_shuffle))
        metric_warnings = structured_warnings + label_warnings
        if len(common_pairs) != PAIR_COUNT_EXPECTED:
            metric_warnings.append("missing_pair_warning")

        structured = {pair: structured[pair] for pair in common_pairs}
        label_shuffle = {pair: label_shuffle[pair] for pair in common_pairs}
        structured_ranks, structured_tie = rank_descending(structured)
        label_shuffle_ranks, label_tie = rank_descending(label_shuffle)
        if structured_tie or label_tie:
            metric_warnings.append("rank_tie_warning")

        structured_rank_values = [structured_ranks[pair] for pair in common_pairs]
        label_rank_values = [label_shuffle_ranks[pair] for pair in common_pairs]
        rank_correlation = pearson_rank_correlation(structured_rank_values, label_rank_values)
        if rank_correlation is None:
            metric_warnings.append("undefined_rank_warning")

        structured_top_pairs = {
            pair for pair in common_pairs if structured_ranks[pair] <= TOP_QUARTILE_COUNT
        }
        label_top_pairs = {
            pair for pair in common_pairs if label_shuffle_ranks[pair] <= TOP_QUARTILE_COUNT
        }
        top_overlap = len(structured_top_pairs & label_top_pairs) / float(TOP_QUARTILE_COUNT)

        deltas = [structured[pair] - label_shuffle[pair] for pair in common_pairs]
        abs_deltas = [abs(delta) for delta in deltas]
        mean_structured = float(np.mean([structured[pair] for pair in common_pairs]))
        mean_label_shuffle = float(np.mean([label_shuffle[pair] for pair in common_pairs]))
        mean_abs_delta = float(np.mean(abs_deltas))
        median_abs_delta = float(median(abs_deltas))
        max_abs_delta = float(max(abs_deltas))
        small_delta_threshold = max(
            ETA,
            0.05 * max(abs(mean_structured), abs(mean_label_shuffle), ETA),
        )

        identity_signal = (
            mean_abs_delta > small_delta_threshold
            and rank_correlation is not None
            and rank_correlation < RANK_CORRELATION_THRESHOLD
            and top_overlap <= TOP_QUARTILE_OVERLAP_THRESHOLD
        )
        identity_shift_status = decide_rank_shift_status(
            identity_signal,
            rank_correlation,
            top_overlap,
            mean_abs_delta,
            small_delta_threshold,
        )
        overall_status = decide_overall_status(
            identity_signal,
            rank_correlation,
            top_overlap,
            mean_abs_delta,
            small_delta_threshold,
        )
        rank_shift_status = (
            "rank_correlation_below_threshold"
            if rank_correlation is not None and rank_correlation < RANK_CORRELATION_THRESHOLD
            else "rank_correlation_not_below_threshold"
        )
        if rank_correlation is None:
            rank_shift_status = "rank_correlation_undefined"
        top_quartile_status = (
            "top_quartile_overlap_at_or_below_threshold"
            if top_overlap <= TOP_QUARTILE_OVERLAP_THRESHOLD
            else "top_quartile_overlap_above_threshold"
        )
        pairwise_delta_status = (
            "mean_abs_delta_above_small_delta_threshold"
            if mean_abs_delta > small_delta_threshold
            else "mean_abs_delta_at_or_below_small_delta_threshold"
        )
        warning = joined_warnings(metric_warnings)

        for pair in common_pairs:
            delta = structured[pair] - label_shuffle[pair]
            abs_delta = abs(delta)
            direction = signed_direction(delta, abs_delta)
            pair_warning = "rank_tie_warning" if (structured_tie or label_tie) else ""
            pairwise_rows.append(
                {
                    "metric_name": metric,
                    "source_id": pair[0],
                    "target_id": pair[1],
                    "structured_value": structured[pair],
                    "label_shuffle_value": label_shuffle[pair],
                    "delta": delta,
                    "abs_delta": abs_delta,
                    "signed_direction": direction,
                    "structured_rank": structured_ranks[pair],
                    "label_shuffle_rank": label_shuffle_ranks[pair],
                    "rank_delta": structured_ranks[pair] - label_shuffle_ranks[pair],
                    "structured_top_quartile": structured_ranks[pair] <= TOP_QUARTILE_COUNT,
                    "label_shuffle_top_quartile": label_shuffle_ranks[pair] <= TOP_QUARTILE_COUNT,
                    "pair_identity_status": direction,
                    "warning": pair_warning,
                }
            )

        rank_summary_rows.append(
            {
                "metric_name": metric,
                "pair_count": len(common_pairs),
                "mean_structured": mean_structured,
                "mean_label_shuffle": mean_label_shuffle,
                "mean_abs_delta": mean_abs_delta,
                "median_abs_delta": median_abs_delta,
                "max_abs_delta": max_abs_delta,
                "small_delta_threshold": small_delta_threshold,
                "rank_correlation": rank_correlation,
                "top_quartile_overlap": top_overlap,
                "top_pair_structured": top_pair(structured, structured_ranks),
                "top_pair_label_shuffle": top_pair(label_shuffle, label_shuffle_ranks),
                "identity_shift_status": identity_shift_status,
                "warning": warning,
            }
        )
        control_decision_rows.append(
            {
                "metric_name": metric,
                "identity_sensitive_signal": identity_signal,
                "rank_shift_status": rank_shift_status,
                "top_quartile_status": top_quartile_status,
                "pairwise_delta_status": pairwise_delta_status,
                "overall_label_shuffle_status": overall_status,
                "recommended_followup": recommended_followup(overall_status, identity_signal),
                "specificity_status": "specificity_not_established",
                "warning": warning,
            }
        )

    return pairwise_rows, rank_summary_rows, control_decision_rows


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
    decisions: Sequence[Dict[str, object]],
    summaries: Sequence[Dict[str, object]],
) -> None:
    identity_metrics = [
        str(row["metric_name"])
        for row in decisions
        if row["overall_label_shuffle_status"] == "identity_sensitive_candidate"
    ]
    mimic_metrics = [
        str(row["metric_name"])
        for row in decisions
        if row["overall_label_shuffle_status"] == "label_shuffle_mimics_structured_warning"
    ]
    inconclusive_metrics = [
        str(row["metric_name"])
        for row in decisions
        if row["overall_label_shuffle_status"] == "inconclusive_identity_signal"
    ]
    warning_lines = [
        f"- {row['metric_name']}: {row['warning']}"
        for row in summaries
        if row.get("warning")
    ]
    text = f"""# QSB-ST-COMP01-C Identity-Sensitive Component Contrast Readout

## Purpose

The COMP01-C scanner tests identity-sensitive component contrasts between structured_local_phase_response and label_shuffle using existing COMP01-B outputs. It evaluates pairwise deltas, rank correlation, and top-quartile overlap. It does not establish physical wavefunctions, physical time, Lorentz structure, D(A,B), S_rel2, or Bridge validation.

## Input basis

- Input file: {INPUT_FILE}
- Comparison focus: {COMPARISON_FOCUS}
- Pair count: {PAIR_COUNT_EXPECTED}

## Component split mode

{COMPONENT_SPLIT_MODE}

real_imag_proxy is a diagnostic component split, not a physical derivation.

## Selected metrics

{chr(10).join(f"- {metric}" for metric in SELECTED_METRICS)}

## Output files

- {OUTPUT_DIR / "identity_component_pairwise_contrast.csv"}
- {OUTPUT_DIR / "identity_component_rank_summary.csv"}
- {OUTPUT_DIR / "identity_component_control_decision.csv"}
- {OUTPUT_DIR / "summary.json"}
- {OUTPUT_DIR / "readout.md"}
- {OUTPUT_DIR / "config_resolved.json"}

## Identity-sensitive label_shuffle contrast summary

{chr(10).join(f"- {row['metric_name']}: {row['overall_label_shuffle_status']}" for row in decisions)}

## Candidate movement

- Metriken mit identity_sensitive_signal = true: {identity_metrics}
- Metriken mit label_shuffle_mimics_structured_warning: {mimic_metrics}
- Metriken mit inconclusive_identity_signal: {inconclusive_metrics}

## Warnings

{chr(10).join(warning_lines) if warning_lines else "- none"}

## Claim Boundary

{CLAIM_BOUNDARY}
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    rows = read_input_rows(INPUT_FILE)
    component_split_mode = require_component_split_mode(rows)
    pairwise_rows, rank_summary_rows, control_decision_rows = build_outputs(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        OUTPUT_DIR / "identity_component_pairwise_contrast.csv",
        PAIRWISE_FIELDS,
        pairwise_rows,
    )
    write_csv(
        OUTPUT_DIR / "identity_component_rank_summary.csv",
        RANK_SUMMARY_FIELDS,
        rank_summary_rows,
    )
    write_csv(
        OUTPUT_DIR / "identity_component_control_decision.csv",
        CONTROL_DECISION_FIELDS,
        control_decision_rows,
    )

    identity_candidate_metrics = [
        str(row["metric_name"])
        for row in control_decision_rows
        if row["overall_label_shuffle_status"] == "identity_sensitive_candidate"
    ]
    mimic_warning_metrics = [
        str(row["metric_name"])
        for row in control_decision_rows
        if row["overall_label_shuffle_status"] == "label_shuffle_mimics_structured_warning"
    ]
    inconclusive_metrics = [
        str(row["metric_name"])
        for row in control_decision_rows
        if row["overall_label_shuffle_status"] == "inconclusive_identity_signal"
    ]
    summary = {
        "block": BLOCK,
        "status": STATUS,
        "input_file": str(INPUT_FILE),
        "output_dir": str(OUTPUT_DIR),
        "comparison_focus": COMPARISON_FOCUS,
        "component_split_mode": component_split_mode,
        "pair_count": PAIR_COUNT_EXPECTED,
        "selected_metric_count": len(SELECTED_METRICS),
        "pairwise_contrast_row_count": len(pairwise_rows),
        "rank_summary_row_count": len(rank_summary_rows),
        "control_decision_row_count": len(control_decision_rows),
        "selected_metrics": SELECTED_METRICS,
        "identity_sensitive_candidate_metrics": identity_candidate_metrics,
        "label_shuffle_mimic_warning_metrics": mimic_warning_metrics,
        "inconclusive_metrics": inconclusive_metrics,
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
        "component_split_mode": component_split_mode,
        "selected_metrics": SELECTED_METRICS,
        "pair_count_expected": PAIR_COUNT_EXPECTED,
        "top_quartile_count": TOP_QUARTILE_COUNT,
        "rank_correlation_method": "pearson_on_descending_value_ranks",
        "small_delta_threshold_rule": (
            "max(1e-12, 0.05 * max(abs(mean_structured), "
            "abs(mean_label_shuffle), 1e-12))"
        ),
        "rank_correlation_threshold": RANK_CORRELATION_THRESHOLD,
        "top_quartile_overlap_threshold": TOP_QUARTILE_OVERLAP_THRESHOLD,
        "specificity_default": False,
    }
    write_json(OUTPUT_DIR / "config_resolved.json", config)
    write_readout(OUTPUT_DIR / "readout.md", control_decision_rows, rank_summary_rows)

    print(STATUS)
    print(f"input_file: {INPUT_FILE}")
    print(f"output_dir: {OUTPUT_DIR}")
    print(f"pairwise_contrast_row_count: {len(pairwise_rows)}")
    print(f"rank_summary_row_count: {len(rank_summary_rows)}")
    print(f"control_decision_row_count: {len(control_decision_rows)}")
    print(f"identity_sensitive_candidate_metrics: {identity_candidate_metrics}")
    print(f"label_shuffle_mimic_warning_metrics: {mimic_warning_metrics}")
    print(f"inconclusive_metrics: {inconclusive_metrics}")
    print("specificity_established: False")


if __name__ == "__main__":
    main()
