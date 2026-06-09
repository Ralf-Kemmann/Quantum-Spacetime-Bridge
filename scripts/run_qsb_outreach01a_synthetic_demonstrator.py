#!/usr/bin/env python3
"""Run the QSB-OUTREACH01A synthetic demonstrator.

The config file is JSON-compatible YAML to avoid external dependencies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_COLUMNS = [
    "case_id",
    "prompt_case_id",
    "case_role",
    "event_instance_id",
    "state_descriptor_id",
    "state_id",
    "cycle_index",
    "forcing_phase",
    "forcing_phase_role",
    "response_phase_class",
    "observable_recurrence_class",
    "full_state_equivalence_class",
    "observable_value",
    "observable_vector_json",
    "background_state_json",
    "history_representation_type",
    "history_descriptor_json",
    "history_window_start",
    "history_window_end",
    "is_observed",
    "source_sequence_index",
    "source_record_id",
    "source_type",
    "source_checksum",
    "source_checksum_algorithm",
    "random_seed",
    "transformation_version",
]

PAIR_COLUMNS = [
    "case_id",
    "model_run_id",
    "model_version",
    "state_i_id",
    "state_j_id",
    "cycle_i",
    "cycle_j",
    "lag",
    "similarity_score",
    "observable_similarity",
    "forcing_phase_similarity_reference",
    "similarity_features_used",
    "excluded_similarity_features",
    "pair_logic",
    "source_type",
    "config_hash",
]

LAG_COLUMNS = [
    "case_id",
    "lag",
    "pair_count",
    "median_similarity",
    "mean_similarity",
    "std_similarity",
    "window_count",
    "valid_window_count",
    "stable_window_count",
    "stable_window_fraction",
    "missing_observation_count",
    "robustness_status",
]

CASE_SUMMARY_COLUMNS = [
    "case_id",
    "prompt_case_id",
    "case_role",
    "expected_detection_family",
    "detected_status",
    "detection_family_match",
    "expected_control_outcome",
    "control_interpretation",
    "control_outcome_match",
    "state_record_count",
    "observed_state_count",
    "missing_observation_count",
    "observed_fraction",
    "lag1_median_similarity",
    "lag2_median_similarity",
    "lag2_minus_lag1",
    "lag2_stable_window_fraction",
    "valid_window_fraction",
    "minimum_valid_pairs_met",
    "data_quality_status",
    "method_note",
]

DETECTION_STATUSES = {
    "t_like_recurrence_supported",
    "two_t_like_recurrence_supported",
    "two_t_like_recurrence_partly_supported",
    "non_two_t_pattern",
    "data_quality_inconclusive",
    "inconclusive",
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "run_id",
        "runner_version",
        "model_run_id",
        "model_version",
        "random_seed",
        "sequence_length",
        "window_length",
        "window_overlap",
        "tested_lags",
        "noise_strength",
        "missing_observation_fraction",
        "minimum_valid_pairs",
        "minimal_lag_difference",
        "minimal_stable_window_fraction",
        "minimum_observed_fraction",
        "minimum_valid_window_fraction",
        "t_like_min_lag1_similarity",
        "t_like_max_lag_decay",
        "transformation_version",
        "source_type",
        "source_checksum_algorithm",
        "weights",
        "cases",
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Config missing required keys: {missing}")
    weights = config["weights"]
    if set(weights) != {"observable_value"}:
        raise ValueError("Hardening variant A requires weights to contain only observable_value")
    if not math.isclose(float(weights["observable_value"]), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("observable_value weight must be 1.0")
    for case in config["cases"]:
        for key in ["case_id", "case_role", "expected_detection_family", "expected_control_outcome"]:
            if key not in case:
                raise ValueError(f"Case {case.get('case_id')} missing {key}")
        if case["expected_detection_family"] not in DETECTION_STATUSES:
            raise ValueError(f"Unexpected expected_detection_family: {case['expected_detection_family']}")
    return config


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def phase_similarity(phase_a: float, phase_b: float) -> float:
    delta = abs(phase_a - phase_b) % (2.0 * math.pi)
    wrapped = min(delta, 2.0 * math.pi - delta)
    return clamp(1.0 - wrapped / math.pi)


def observable_similarity(value_a: float, value_b: float) -> float:
    return clamp(1.0 - abs(value_a - value_b))


def similarity(row_a: dict[str, Any], row_b: dict[str, Any]) -> dict[str, float]:
    obs_sim = observable_similarity(float(row_a["observable_value"]), float(row_b["observable_value"]))
    phase_sim = phase_similarity(float(row_a["forcing_phase"]), float(row_b["forcing_phase"]))
    return {
        "similarity_score": obs_sim,
        "observable_similarity": obs_sim,
        "forcing_phase_similarity_reference": phase_sim,
    }


def descriptor_for_case(case_id: str, index: int, rng: random.Random, config: dict[str, Any]) -> tuple[str, str, str, float]:
    noise = float(config["noise_strength"])
    n = int(config["sequence_length"])
    if case_id == "T_CONTROL":
        return "T", "phase_T", "T", clamp(0.5 + rng.uniform(-0.01, 0.01))
    if case_id == "T2_STABLE":
        cls = "A" if index % 2 == 0 else "B"
        return cls, f"phase_{cls}", cls, 0.25 if cls == "A" else 0.75
    if case_id == "T2_NOISY":
        cls = "A" if index % 2 == 0 else "B"
        center = 0.25 if cls == "A" else 0.75
        return cls, f"phase_{cls}", cls, clamp(center + rng.uniform(-noise, noise))
    if case_id == "DRIFT_CONTROL":
        value = clamp(0.2 + 0.6 * (index / max(n - 1, 1)))
        bucket = int(value * 5)
        return f"D{bucket}", "phase_drift", f"D{bucket}", value
    if case_id == "MISSING_OBSERVATIONS":
        cls = "A" if index % 2 == 0 else "B"
        center = 0.25 if cls == "A" else 0.75
        return cls, f"phase_{cls}", cls, clamp(center + rng.uniform(-noise, noise))
    if case_id == "FALSE_RECURRENCE_CONTROL":
        local_wave = 0.5 + 0.18 * math.sin(index * 1.7)
        value = clamp(local_wave + rng.uniform(-0.18, 0.18))
        bucket = int(value * 4)
        return f"F{bucket}", f"phase_F{bucket}", f"F{bucket}", value
    raise ValueError(f"Unsupported case_id: {case_id}")


def missing_indices_for_case(case_id: str, rng: random.Random, config: dict[str, Any]) -> set[int]:
    if case_id != "MISSING_OBSERVATIONS":
        return set()
    n = int(config["sequence_length"])
    count = max(1, round(n * float(config["missing_observation_fraction"])))
    return set(sorted(rng.sample(range(n), count)))


def build_states(config: dict[str, Any], config_hash: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base_seed = int(config["random_seed"])
    n = int(config["sequence_length"])
    for case_number, case in enumerate(config["cases"]):
        case_id = str(case["case_id"])
        rng = random.Random(base_seed + case_number * 1009)
        missing = missing_indices_for_case(case_id, rng, config)
        for index in range(n):
            desc_class, phase_class, recurrence_class, value = descriptor_for_case(case_id, index, rng, config)
            event_instance_id = f"{case_id}__E{index:04d}"
            state_descriptor_id = f"{case_id}__X_{desc_class}"
            forcing_phase = 0.0
            observable_vector = {"observable_value": round(value, 10)}
            background = {"source": "synthetic", "case_id": case_id, "config_hash": config_hash}
            history = {
                "representation": case["history_representation_type"],
                "previous_cycle_index": index - 1 if index > 0 else None,
            }
            payload_for_checksum = canonical_json(
                {
                    "case_id": case_id,
                    "event_instance_id": event_instance_id,
                    "observable_vector": observable_vector,
                    "background": background,
                    "history": history,
                }
            )
            rows.append(
                {
                    "case_id": case_id,
                    "prompt_case_id": case["prompt_case_id"],
                    "case_role": case["case_role"],
                    "event_instance_id": event_instance_id,
                    "state_descriptor_id": state_descriptor_id,
                    "state_id": event_instance_id,
                    "cycle_index": index,
                    "forcing_phase": forcing_phase,
                    "forcing_phase_role": "stroboscopic_reference_metadata_not_similarity_input",
                    "response_phase_class": phase_class,
                    "observable_recurrence_class": recurrence_class,
                    "full_state_equivalence_class": desc_class,
                    "observable_value": round(value, 10),
                    "observable_vector_json": canonical_json(observable_vector),
                    "background_state_json": canonical_json(background),
                    "history_representation_type": case["history_representation_type"],
                    "history_descriptor_json": canonical_json(history),
                    "history_window_start": -1.0,
                    "history_window_end": 0.0,
                    "is_observed": index not in missing,
                    "source_sequence_index": index,
                    "source_record_id": f"synthetic:{case_id}:{index:04d}",
                    "source_type": config["source_type"],
                    "source_checksum": sha256_text(payload_for_checksum),
                    "source_checksum_algorithm": config["source_checksum_algorithm"],
                    "random_seed": base_seed,
                    "transformation_version": config["transformation_version"],
                }
            )
    return rows


def build_pairs(states: list[dict[str, Any]], config: dict[str, Any], config_hash: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_case: dict[str, list[dict[str, Any]]] = {}
    for row in states:
        if row["is_observed"]:
            by_case.setdefault(row["case_id"], []).append(row)
    for case_id, case_rows in by_case.items():
        sorted_rows = sorted(case_rows, key=lambda row: row["event_instance_id"])
        for left_index in range(len(sorted_rows)):
            for right_index in range(left_index + 1, len(sorted_rows)):
                left = sorted_rows[left_index]
                right = sorted_rows[right_index]
                state_i_id = left["event_instance_id"]
                state_j_id = right["event_instance_id"]
                if not state_i_id < state_j_id:
                    raise AssertionError("canonical pair order violated")
                sim = similarity(left, right)
                rows.append(
                    {
                        "case_id": case_id,
                        "model_run_id": config["model_run_id"],
                        "model_version": config["model_version"],
                        "state_i_id": state_i_id,
                        "state_j_id": state_j_id,
                        "cycle_i": left["cycle_index"],
                        "cycle_j": right["cycle_index"],
                        "lag": int(right["cycle_index"]) - int(left["cycle_index"]),
                        "similarity_score": round(sim["similarity_score"], 10),
                        "observable_similarity": round(sim["observable_similarity"], 10),
                        "forcing_phase_similarity_reference": round(sim["forcing_phase_similarity_reference"], 10),
                        "similarity_features_used": "observable_value",
                        "excluded_similarity_features": "forcing_phase,response_phase_class,observable_recurrence_class,state_descriptor_id,case_role",
                        "pair_logic": "symmetric_canonical_order",
                        "source_type": config["source_type"],
                        "config_hash": config_hash,
                    }
                )
    return rows


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def mean(values: list[float]) -> float | None:
    return statistics.mean(values) if values else None


def std(values: list[float]) -> float | None:
    return statistics.pstdev(values) if len(values) > 1 else (0.0 if values else None)


def windows(config: dict[str, Any]) -> list[tuple[int, int]]:
    n = int(config["sequence_length"])
    length = int(config["window_length"])
    step = max(1, length - int(config["window_overlap"]))
    result = []
    start = 0
    while start + length <= n:
        result.append((start, start + length))
        start += step
    return result


def pair_scores_for_lag(
    pairs: list[dict[str, Any]],
    case_id: str,
    lag: int,
    start: int | None = None,
    end: int | None = None,
) -> list[float]:
    scores: list[float] = []
    for row in pairs:
        if row["case_id"] != case_id or int(row["lag"]) != lag:
            continue
        cycle_i = int(row["cycle_i"])
        cycle_j = int(row["cycle_j"])
        if start is not None and end is not None and not (start <= cycle_i and cycle_j < end):
            continue
        scores.append(float(row["similarity_score"]))
    return scores


def build_lag_profile(states: list[dict[str, Any]], pairs: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    window_ranges = windows(config)
    min_pairs = int(config["minimum_valid_pairs"])
    min_diff = float(config["minimal_lag_difference"])
    min_fraction = float(config["minimal_stable_window_fraction"])
    missing_by_case = Counter(row["case_id"] for row in states if not row["is_observed"])
    for case in config["cases"]:
        case_id = case["case_id"]
        for lag in config["tested_lags"]:
            lag = int(lag)
            scores = pair_scores_for_lag(pairs, case_id, lag)
            valid_window_count = 0
            stable_window_count = 0
            for start, end in window_ranges:
                lag_scores = pair_scores_for_lag(pairs, case_id, lag, start, end)
                if len(lag_scores) >= min_pairs:
                    valid_window_count += 1
                if lag == 2:
                    lag1_scores = pair_scores_for_lag(pairs, case_id, 1, start, end)
                    if len(lag_scores) >= min_pairs and len(lag1_scores) >= min_pairs:
                        if (statistics.median(lag_scores) - statistics.median(lag1_scores)) >= min_diff:
                            stable_window_count += 1
            fraction = stable_window_count / valid_window_count if valid_window_count else 0.0
            if not scores or len(scores) < min_pairs:
                robustness = "insufficient_pairs"
            elif lag == 2 and fraction >= min_fraction:
                robustness = "stable_lag2_over_lag1"
            elif lag == 2 and fraction > 0:
                robustness = "partial_lag2_over_lag1"
            else:
                robustness = "computed"
            rows.append(
                {
                    "case_id": case_id,
                    "lag": lag,
                    "pair_count": len(scores),
                    "median_similarity": round(median(scores), 10) if scores else "",
                    "mean_similarity": round(mean(scores), 10) if scores else "",
                    "std_similarity": round(std(scores), 10) if scores else "",
                    "window_count": len(window_ranges),
                    "valid_window_count": valid_window_count,
                    "stable_window_count": stable_window_count,
                    "stable_window_fraction": round(fraction, 10),
                    "missing_observation_count": missing_by_case[case_id],
                    "robustness_status": robustness,
                }
            )
    return rows


def lag_lookup(lag_rows: list[dict[str, Any]], case_id: str, lag: int) -> dict[str, Any]:
    for row in lag_rows:
        if row["case_id"] == case_id and int(row["lag"]) == lag:
            return row
    raise KeyError((case_id, lag))


def derived_metrics(
    case_id: str,
    states_by_case: Counter[str],
    observed_by_case: Counter[str],
    lag_rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    lag1 = lag_lookup(lag_rows, case_id, 1)
    lag2 = lag_lookup(lag_rows, case_id, 2)
    lag4 = lag_lookup(lag_rows, case_id, 4)
    total = states_by_case[case_id]
    observed = observed_by_case[case_id]
    observed_fraction = observed / total if total else 0.0
    lag1_median = float(lag1["median_similarity"]) if lag1["median_similarity"] != "" else None
    lag2_median = float(lag2["median_similarity"]) if lag2["median_similarity"] != "" else None
    lag4_median = float(lag4["median_similarity"]) if lag4["median_similarity"] != "" else None
    lag2_minus_lag1 = None if lag1_median is None or lag2_median is None else lag2_median - lag1_median
    lag4_decay_from_lag1 = None if lag1_median is None or lag4_median is None else lag1_median - lag4_median
    window_count = int(lag2["window_count"])
    valid_window_count = int(lag2["valid_window_count"])
    valid_window_fraction = valid_window_count / window_count if window_count else 0.0
    return {
        "lag1_median_similarity": lag1_median,
        "lag2_median_similarity": lag2_median,
        "lag2_minus_lag1": lag2_minus_lag1,
        "lag4_decay_from_lag1": lag4_decay_from_lag1,
        "lag2_stable_window_fraction": float(lag2["stable_window_fraction"]),
        "observed_fraction": observed_fraction,
        "valid_window_fraction": valid_window_fraction,
        "minimum_valid_pairs_met": int(lag1["pair_count"]) >= int(config["minimum_valid_pairs"])
        and int(lag2["pair_count"]) >= int(config["minimum_valid_pairs"]),
    }


def detect_status_from_metrics(metrics: dict[str, Any], config: dict[str, Any]) -> str:
    if (
        metrics["observed_fraction"] < float(config["minimum_observed_fraction"])
        or metrics["valid_window_fraction"] < float(config["minimum_valid_window_fraction"])
        or not metrics["minimum_valid_pairs_met"]
    ):
        return "data_quality_inconclusive"
    lag1 = metrics["lag1_median_similarity"]
    lag2 = metrics["lag2_median_similarity"]
    diff = metrics["lag2_minus_lag1"]
    if lag1 is None or lag2 is None or diff is None:
        return "inconclusive"
    two_t_supported = (
        diff >= float(config["minimal_lag_difference"])
        and metrics["lag2_stable_window_fraction"] >= float(config["minimal_stable_window_fraction"])
    )
    if two_t_supported:
        return "two_t_like_recurrence_supported"
    if diff >= float(config["minimal_lag_difference"]) and metrics["lag2_stable_window_fraction"] > 0.0:
        return "two_t_like_recurrence_partly_supported"
    lag4_decay = metrics.get("lag4_decay_from_lag1")
    if (
        lag1 >= float(config["t_like_min_lag1_similarity"])
        and diff < float(config["minimal_lag_difference"])
        and lag4_decay is not None
        and abs(lag4_decay) <= float(config["t_like_max_lag_decay"])
    ):
        return "t_like_recurrence_supported"
    return "non_two_t_pattern"


def detection_family_matches(expected: str, detected: str) -> bool:
    if expected == detected:
        return True
    return expected == "two_t_like_recurrence_supported" and detected == "two_t_like_recurrence_partly_supported"


def interpret_control(case_role: str, expected_family: str, detected_status: str, observed_fraction: float) -> str:
    if detected_status == "data_quality_inconclusive":
        return "control_inconclusive_due_to_data_quality"
    if case_role == "missing_observation_control" and detection_family_matches(expected_family, detected_status):
        return "control_pass_with_missing_data_warning"
    if detection_family_matches(expected_family, detected_status):
        return "control_pass"
    return "control_fail"


def build_case_summary(states: list[dict[str, Any]], lag_rows: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    states_by_case = Counter(row["case_id"] for row in states)
    observed_by_case = Counter(row["case_id"] for row in states if row["is_observed"])
    missing_by_case = Counter(row["case_id"] for row in states if not row["is_observed"])
    for case in config["cases"]:
        case_id = case["case_id"]
        metrics = derived_metrics(case_id, states_by_case, observed_by_case, lag_rows, config)
        detected_status = detect_status_from_metrics(metrics, config)
        control_interpretation = interpret_control(
            case["case_role"],
            case["expected_detection_family"],
            detected_status,
            metrics["observed_fraction"],
        )
        rows.append(
            {
                "case_id": case_id,
                "prompt_case_id": case["prompt_case_id"],
                "case_role": case["case_role"],
                "expected_detection_family": case["expected_detection_family"],
                "detected_status": detected_status,
                "detection_family_match": detection_family_matches(case["expected_detection_family"], detected_status),
                "expected_control_outcome": case["expected_control_outcome"],
                "control_interpretation": control_interpretation,
                "control_outcome_match": control_interpretation == case["expected_control_outcome"],
                "state_record_count": states_by_case[case_id],
                "observed_state_count": observed_by_case[case_id],
                "missing_observation_count": missing_by_case[case_id],
                "observed_fraction": round(metrics["observed_fraction"], 10),
                "lag1_median_similarity": "" if metrics["lag1_median_similarity"] is None else round(metrics["lag1_median_similarity"], 10),
                "lag2_median_similarity": "" if metrics["lag2_median_similarity"] is None else round(metrics["lag2_median_similarity"], 10),
                "lag2_minus_lag1": "" if metrics["lag2_minus_lag1"] is None else round(metrics["lag2_minus_lag1"], 10),
                "lag2_stable_window_fraction": round(metrics["lag2_stable_window_fraction"], 10),
                "valid_window_fraction": round(metrics["valid_window_fraction"], 10),
                "minimum_valid_pairs_met": metrics["minimum_valid_pairs_met"],
                "data_quality_status": "sufficient" if detected_status != "data_quality_inconclusive" else "insufficient",
                "method_note": "generic_detection_then_control_interpretation",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            serialised = {
                key: ("true" if value is True else "false" if value is False else value)
                for key, value in row.items()
            }
            writer.writerow(serialised)


def write_readout(path: Path, config: dict[str, Any], summary: dict[str, Any], case_rows: list[dict[str, Any]], lag_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# QSB-OUTREACH01A-06 Synthetic Demonstrator Readout",
        "",
        "## Purpose",
        "",
        "This run tests synthetic descriptor recurrence, event-instance separation, symmetric pair construction, and robust lag summaries.",
        "",
        "## Similarity Correction",
        "",
        "The runner uses stroboscopic sampling with `forcing_phase = 0.0` as reference metadata. Forcing phase is excluded from the similarity score because it is not a discriminating feature in this minimal setup.",
        "",
        "The detector receives only calculated metrics and threshold configuration. Synthetic case identifiers and control roles are evaluated only after generic detection.",
        "",
        "## Configuration",
        "",
        f"- run_id: `{summary['run_id']}`",
        f"- runner_version: `{summary['runner_version']}`",
        f"- random_seed: `{summary['random_seed']}`",
        f"- config_hash: `{summary['config_hash']}`",
        f"- similarity_features_used: `{summary['similarity_features_used']}`",
        f"- sequence_length: `{config['sequence_length']}`",
        f"- tested_lags: `{config['tested_lags']}`",
        "",
        "## Generic Detection And Control Interpretation",
        "",
    ]
    for row in case_rows:
        lines.append(
            f"- `{row['case_id']}`: detected `{row['detected_status']}`, role `{row['case_role']}`, control `{row['control_interpretation']}`"
        )
    lines.extend(["", "## Central Lag Results", ""])
    for row in lag_rows:
        if int(row["lag"]) in {1, 2}:
            lines.append(
                f"- `{row['case_id']}` lag {row['lag']}: median={row['median_similarity']}, pairs={row['pair_count']}, robustness=`{row['robustness_status']}`"
            )
    lines.extend(
        [
            "",
            "## Known Limits",
            "",
            "- Synthetic data only.",
            "- One-dimensional minimal observable.",
            "- No calibration against real laser measurements.",
            "- Thresholds are method parameters, not physical constants.",
            "- Control cases are generator families, not real experimental states.",
            "",
            "## Non-Claims",
            "",
            "- This run does not validate QSB.",
            "- This run does not establish a discrete time crystal.",
            "- This run does not make claims about fundamental time, ART, QM, gravitation, or emergent spacetime.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_outputs(
    states: list[dict[str, Any]],
    pairs: list[dict[str, Any]],
    lag_rows: list[dict[str, Any]],
    case_rows: list[dict[str, Any]],
    config: dict[str, Any],
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    expected_cases = {case["case_id"] for case in config["cases"]}
    if {row["case_id"] for row in states} != expected_cases:
        issues.append("state rows do not cover all expected cases")
    if any(float(row["forcing_phase"]) != 0.0 for row in states):
        issues.append("forcing_phase must remain stroboscopic reference 0.0")
    if len({row["event_instance_id"] for row in states}) != len(states):
        issues.append("event_instance_id values are not unique")
    for row in states:
        json.loads(row["observable_vector_json"])
        json.loads(row["background_state_json"])
        json.loads(row["history_descriptor_json"])
        if row["event_instance_id"] == row["state_descriptor_id"]:
            issues.append("event and descriptor IDs are not separated")
    pair_keys: set[tuple[str, str]] = set()
    for row in pairs:
        left = row["state_i_id"]
        right = row["state_j_id"]
        if left == right:
            issues.append("self-pair found")
        if not left < right:
            issues.append("non-canonical pair order found")
        if (left, right) in pair_keys or (right, left) in pair_keys:
            issues.append("duplicate or mirror pair found")
        pair_keys.add((left, right))
        score = float(row["similarity_score"])
        if not 0.0 <= score <= 1.0:
            issues.append("similarity outside [0,1]")
        if row["similarity_features_used"] != "observable_value":
            issues.append("unexpected similarity feature set")
    if any(row["detected_status"] == "time_crystal_confirmed" for row in case_rows):
        issues.append("forbidden physical status emitted")
    if not detector_input_independence_check(config):
        issues.append("detector input independence check failed")
    return not issues, issues


def detector_input_independence_check(config: dict[str, Any]) -> bool:
    metrics = {
        "lag1_median_similarity": 0.5,
        "lag2_median_similarity": 0.9,
        "lag2_minus_lag1": 0.4,
        "lag2_stable_window_fraction": 1.0,
        "observed_fraction": 1.0,
        "valid_window_fraction": 1.0,
        "minimum_valid_pairs_met": True,
    }
    first = detect_status_from_metrics(dict(metrics), config)
    second = detect_status_from_metrics(dict(metrics), {**config, "run_id": "detector_input_probe"})
    return first == second == "two_t_like_recurrence_supported"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    config = read_config(args.config)
    config_hash = sha256_text(canonical_json(config))
    resolved_config = dict(config)
    resolved_config["config_hash"] = config_hash
    resolved_config["persistent_migration_executed"] = False
    resolved_config["real_data_used"] = False
    resolved_config["physics_claim_gate"] = "closed"
    resolved_config["similarity_features_used"] = ["observable_value"]
    resolved_config["stroboscopic_forcing_phase_reference"] = True

    states = build_states(config, config_hash)
    pairs = build_pairs(states, config, config_hash)
    lag_rows = build_lag_profile(states, pairs, config)
    case_rows = build_case_summary(states, lag_rows, config)
    validation_passed, validation_issues = validate_outputs(states, pairs, lag_rows, case_rows, config)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "synthetic_states.csv", states, STATE_COLUMNS)
    write_csv(output_dir / "relational_pairs.csv", pairs, PAIR_COLUMNS)
    write_csv(output_dir / "lag_profile.csv", lag_rows, LAG_COLUMNS)
    write_csv(output_dir / "case_summary.csv", case_rows, CASE_SUMMARY_COLUMNS)
    detection_counts = dict(Counter(row["detected_status"] for row in case_rows))
    control_counts = dict(Counter(row["control_interpretation"] for row in case_rows))
    status_rows = [
        {"status_type": "detected_status", "status": key, "case_count": value}
        for key, value in sorted(detection_counts.items())
    ] + [
        {"status_type": "control_interpretation", "status": key, "case_count": value}
        for key, value in sorted(control_counts.items())
    ]
    write_csv(output_dir / "status_summary.csv", status_rows, ["status_type", "status", "case_count"])

    expected_status_check_passed = all(row["control_outcome_match"] for row in case_rows)
    summary = {
        "run_id": config["run_id"],
        "run_timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runner_version": config["runner_version"],
        "config_hash": config_hash,
        "random_seed": config["random_seed"],
        "case_count": len(config["cases"]),
        "state_record_count": len(states),
        "relational_pair_count": len(pairs),
        "lag_record_count": len(lag_rows),
        "detection_status_counts": detection_counts,
        "status_counts": detection_counts,
        "control_interpretation_counts": control_counts,
        "expected_status_check_passed": expected_status_check_passed,
        "validation_passed": validation_passed,
        "validation_issues": validation_issues,
        "detector_input_independence_check_passed": detector_input_independence_check(config),
        "similarity_features_used": ["observable_value"],
        "excluded_similarity_features": [
            "forcing_phase",
            "response_phase_class",
            "observable_recurrence_class",
            "state_descriptor_id",
            "case_role",
        ],
        "persistent_migration_executed": False,
        "real_data_used": False,
        "physics_claim_gate": "closed",
    }
    (output_dir / "resolved_config.json").write_text(json.dumps(resolved_config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_readout(output_dir / "readout.md", resolved_config, summary, case_rows, lag_rows)

    if not validation_passed:
        for issue in validation_issues:
            print(f"FAIL: {issue}")
        return 1
    print(f"Wrote QSB-OUTREACH01A synthetic demonstrator outputs to {output_dir}")
    print("No persistent migration was executed; no real data were used; physics_claim_gate is closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
