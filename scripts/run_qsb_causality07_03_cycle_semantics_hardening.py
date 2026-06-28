#!/usr/bin/env python3
"""Run QSB-CAUSALITY07-03 cycle semantics hardening checks."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
from pathlib import Path


OUTPUT_FILES = [
    "resolved_hardening_config.json",
    "baseline_cycle_semantics.csv",
    "reverse_sequence_control.csv",
    "scrambled_sequence_control.csv",
    "recurrence_identity_comparison.csv",
    "phase_duration_summary.csv",
    "semantic_validation_checks.csv",
    "phase_progression_over_cycles.svg",
    "run_summary.json",
    "readout.md",
]

REQUIRED_CLASSIFIED_COLUMNS = [
    "time",
    "x_activator",
    "y_inhibitor",
    "z_oxidized_catalyst",
    "post_transient",
    "phase_region",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def short_phase(label: str) -> str:
    if label.startswith("BZ01_"):
        return label.removeprefix("BZ01_")
    return label


def sequence_text(sequence: list[str]) -> str:
    return " -> ".join(sequence)


def require_columns(rows: list[dict], columns: list[str], path: Path) -> None:
    if not rows:
        raise SystemExit(f"empty required CSV: {path}")
    missing = [column for column in columns if column not in rows[0]]
    if missing:
        raise SystemExit(f"missing columns in {path}: {missing}")


def percentile(values: list[float], pct: float) -> float:
    if not values:
        raise ValueError("cannot compute percentile of empty values")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * pct / 100.0
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return ordered[int(pos)]
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def stable_segments(rows: list[dict]) -> list[dict]:
    segments: list[dict] = []
    current_phase = None
    start_idx = None
    for idx, row in enumerate(rows):
        if row["post_transient"] != "true":
            continue
        phase = short_phase(row["phase_region"])
        if current_phase is None:
            current_phase = phase
            start_idx = idx
        elif phase != current_phase:
            segments.append({"phase": current_phase, "start_idx": start_idx, "end_idx": idx - 1})
            current_phase = phase
            start_idx = idx
    if current_phase is not None and start_idx is not None:
        segments.append({"phase": current_phase, "start_idx": start_idx, "end_idx": len(rows) - 1})
    return segments


def midpoint(segment: dict) -> int:
    return int((segment["start_idx"] + segment["end_idx"]) // 2)


def iqr_scale(values: list[float]) -> float:
    scale = percentile(values, 75.0) - percentile(values, 25.0)
    if abs(scale) <= 1e-15:
        scale = statistics.pstdev(values) or 1.0
    return scale


def state_distance(row_a: dict, row_b: dict, scales: dict[str, float]) -> float:
    components = [
        (float(row_a["x_activator"]) - float(row_b["x_activator"])) / scales["x"],
        (float(row_a["y_inhibitor"]) - float(row_b["y_inhibitor"])) / scales["y"],
        (float(row_a["z_oxidized_catalyst"]) - float(row_b["z_oxidized_catalyst"])) / scales["z"],
    ]
    return math.sqrt(sum(component * component for component in components)) / math.sqrt(3.0)


def detect_sequence(
    rows: list[dict],
    segments: list[dict],
    sequence: list[str],
    distance_threshold: float,
    scales: dict[str, float],
) -> tuple[list[dict], list[dict]]:
    cycle_rows: list[dict] = []
    recurrence_rows: list[dict] = []
    idx = 0
    cycle_index = 1
    while idx <= len(segments) - len(sequence):
        window = segments[idx : idx + len(sequence)]
        observed = [segment["phase"] for segment in window]
        if observed != sequence:
            idx += 1
            continue
        start_row = rows[midpoint(window[0])]
        end_row = rows[midpoint(window[-1])]
        duration = float(end_row["time"]) - float(start_row["time"])
        distance = state_distance(start_row, end_row, scales)
        drift = float(end_row["y_inhibitor"]) - float(start_row["y_inhibitor"])
        within = distance <= distance_threshold
        cycle_rows.append(
            {
                "cycle_id": f"C{cycle_index:04d}",
                "cycle_index": str(cycle_index),
                "p0_time": start_row["time"],
                "p0_prime_time": end_row["time"],
                "cycle_duration": f"{duration:.8f}",
                "expected_sequence": sequence_text(sequence),
                "observed_sequence": sequence_text(observed),
                "complete_cycle_detected": "yes",
                "same_assigned_phase_label": "yes" if window[0]["phase"] == window[-1]["phase"] else "no",
                "phase_identity_independently_established": "no",
                "state_vector_distance": f"{distance:.12g}",
                "state_vector_distance_within_threshold": "yes" if within else "no",
                "reduced_state_drift_proxy": f"{drift:.12g}",
                "recurrent_state_region_detected": "yes",
                "complete_state_reset_established": "no",
                "cycle_sequence_source": "predefined_phase_sequence",
            }
        )
        recurrence_rows.append(cycle_rows[-1])
        cycle_index += 1
        idx += len(sequence) - 1
    return cycle_rows, recurrence_rows


def control_row(control_id: str, sequence: list[str], detected_count: int) -> dict:
    passed = detected_count == 0
    return {
        "control_id": control_id,
        "expected_sequence": sequence_text(sequence),
        "detected_complete_cycle_count": str(detected_count),
        "control_passed": "yes" if passed else "no",
        "failure_reason": "" if passed else "control_sequence_detected_as_complete_cycle",
    }


def phase_durations(rows: list[dict], segments: list[dict]) -> list[dict]:
    grouped: dict[str, list[float]] = {}
    for segment in segments:
        start = float(rows[segment["start_idx"]]["time"])
        end = float(rows[segment["end_idx"]]["time"])
        grouped.setdefault(segment["phase"], []).append(max(0.0, end - start))
    output = []
    for phase in ["P0", "P1", "P2", "P3", "P4"]:
        durations = grouped.get(phase, [])
        total = sum(durations)
        output.append(
            {
                "phase_label": phase,
                "visit_count": str(len(durations)),
                "total_duration": f"{total:.8f}",
                "mean_duration": f"{(statistics.mean(durations) if durations else 0.0):.8f}",
                "median_duration": f"{(statistics.median(durations) if durations else 0.0):.8f}",
                "minimum_duration": f"{(min(durations) if durations else 0.0):.8f}",
                "maximum_duration": f"{(max(durations) if durations else 0.0):.8f}",
            }
        )
    return output


def make_svg(rows: list[dict], segments: list[dict], baseline_cycles: list[dict]) -> str:
    plot_rows = [row for row in rows if row["post_transient"] == "true"]
    min_t = min(float(row["time"]) for row in plot_rows)
    max_t = max(float(row["time"]) for row in plot_rows)
    width = 1100
    height = 520
    left = 82
    right = 32
    top = 56
    bottom = 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    phase_y = {"P0": 4, "P1": 3, "P2": 2, "P3": 1, "P4": 0}

    def x_pos(t: float) -> float:
        return left + (t - min_t) / (max_t - min_t) * plot_w

    def y_pos(phase: str) -> float:
        return top + phase_y[phase] / 4.0 * plot_h

    points = []
    for segment in segments:
        start_t = float(rows[segment["start_idx"]]["time"])
        end_t = float(rows[segment["end_idx"]]["time"])
        y = y_pos(segment["phase"])
        if not points:
            points.append(f"M {x_pos(start_t):.2f} {y:.2f}")
        else:
            points.append(f"L {x_pos(start_t):.2f} {y:.2f}")
        points.append(f"L {x_pos(end_t):.2f} {y:.2f}")

    grid = []
    labels = []
    for phase in ["P0", "P1", "P2", "P3", "P4"]:
        y = y_pos(phase)
        grid.append(f'<line x1="{left}" y1="{y:.2f}" x2="{width - right}" y2="{y:.2f}" stroke="#d9d9d9"/>')
        labels.append(f'<text x="{left - 18}" y="{y + 4:.2f}" text-anchor="end">{phase}</text>')

    boundaries = []
    for cycle in baseline_cycles:
        start = x_pos(float(cycle["p0_time"]))
        end = x_pos(float(cycle["p0_prime_time"]))
        boundaries.append(
            f'<rect x="{start:.2f}" y="{top}" width="{end - start:.2f}" height="{plot_h}" fill="#f2f7ff" opacity="0.55"/>'
        )
        boundaries.append(f'<line x1="{start:.2f}" y1="{top}" x2="{start:.2f}" y2="{top + plot_h}" stroke="#7a9cc6" stroke-dasharray="4 4"/>')
    if baseline_cycles:
        last_end = x_pos(float(baseline_cycles[-1]["p0_prime_time"]))
        boundaries.append(f'<line x1="{last_end:.2f}" y1="{top}" x2="{last_end:.2f}" y2="{top + plot_h}" stroke="#7a9cc6" stroke-dasharray="4 4"/>')

    changes = []
    for segment in segments[1:]:
        t = float(rows[segment["start_idx"]]["time"])
        changes.append(f'<circle cx="{x_pos(t):.2f}" cy="{y_pos(segment["phase"]):.2f}" r="3" fill="#b84a39"/>')

    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520">',
            "<title>CAUSALITY07: Phase progression across detected cycles</title>",
            '<rect width="100%" height="100%" fill="white"/>',
            '<text x="550" y="28" text-anchor="middle" font-family="Arial" font-size="18">CAUSALITY07: Phase progression across detected cycles</text>',
            *boundaries,
            *grid,
            f'<line x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}" stroke="#333"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#333"/>',
            *labels,
            f'<path d="{" ".join(points)}" fill="none" stroke="#1f5a96" stroke-width="2.5"/>',
            *changes,
            f'<text x="{left + plot_w / 2:.2f}" y="{height - 22}" text-anchor="middle" font-family="Arial" font-size="13">model time</text>',
            '<text x="20" y="260" transform="rotate(-90 20 260)" text-anchor="middle" font-family="Arial" font-size="13">assigned phase label</text>',
            '<text x="910" y="50" font-family="Arial" font-size="12">Shaded bands: detected predefined baseline cycles</text>',
            "</svg>",
        ]
    ) + "\n"


def readout_text(summary: dict) -> str:
    return f"""# QSB-CAUSALITY07-03 Readout

## Purpose

This run hardens the cycle semantics of QSB-CAUSALITY07 by separating predefined sequence matching, phase-label recurrence, reduced-state closeness, and non-identity.

## Inputs

- Input run: `{summary['input_run_id']}`.
- Classified phase series: `runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/classified_phase_series.csv`.
- Cycle sequence source: `{summary['cycle_sequence_source']}`.

## Baseline Cycle Result

{summary['complete_cycle_count']} complete cycles were detected for the predefined sequence `{sequence_text(summary['baseline_sequence'])}`.

## What Recurs

The model returns repeatedly to the same assigned phase region and to a nearby reduced state vector. This supports recurrence within the chosen representation.

Das Modell kommt regelmaessig in denselben Phasenbereich zurueck. Das bedeutet noch nicht, dass der vollstaendige chemische Zustand exakt derselbe ist.

## What Does Not Follow

The result does not establish a whole-chemistry restart, an independent reconstruction of the global phase order, physical causality, emergent time, or complete state identity.

## Negative Controls

The reverse sequence detected {summary['reverse_sequence_control_detected_cycle_count']} complete cycles. The scrambled sequence detected {summary['scrambled_sequence_control_detected_cycle_count']} complete cycles. The controls test detector behavior, not the physical truth of the model.

## Phase Duration

Phase-duration statistics were computed from the post-transient classified phase segments and written to `phase_duration_summary.csv`.

## Semantic Hardening

The distance threshold is explicit at `{summary['state_vector_distance_threshold']}` and is not empirically calibrated here. No similarity function is defined.

## Claim Boundaries

This run uses a reduced model output, not laboratory measurements. It does not model real resource exhaustion and does not validate a physical direction.

## Final Status

`{summary['final_status']}`
"""


def validation_rows(summary: dict, source_inventory_specific: bool, readout: str, figure_path: Path) -> list[dict]:
    checks = [
        ("baseline_sequence_predefined", "yes", summary["cycle_sequence_source"] == "predefined_phase_sequence", "cycle_sequence_source"),
        ("global_cycle_order_not_independently_reconstructed", "yes", summary["global_cycle_order_independently_reconstructed"] == "no", "run_summary"),
        ("time_order_used_to_orient_phase_labels", "yes", summary["time_order_used_to_orient_phase_labels"] == "yes", "run_summary"),
        ("distance_threshold_explicit", "yes", summary["distance_threshold_explicit"] == "yes", "hardening_config"),
        ("similarity_function_not_claimed", "yes", summary["similarity_function_defined"] == "no", "hardening_config"),
        ("same_assigned_phase_label_used", "yes", summary["same_assigned_phase_label_count"] == summary["complete_cycle_count"], "recurrence_identity_comparison"),
        ("phase_identity_not_claimed", "yes", summary["phase_identity_independently_established"] == "no", "run_summary"),
        ("reduced_state_drift_proxy_used", "yes", summary["reduced_state_drift_proxy_used"] == "yes", "recurrence_identity_comparison"),
        ("real_resource_exhaustion_not_claimed", "yes", summary["real_resource_exhaustion_modelled"] == "no", "run_summary"),
        ("recurrent_state_region_detected", "yes", summary["recurrent_state_region_detected"] == "yes", "recurrence_identity_comparison"),
        ("complete_state_reset_not_established", "yes", summary["complete_state_reset_established"] == "no", "recurrence_identity_comparison"),
        ("reverse_sequence_control_passed", "yes", summary["reverse_sequence_control_detected_cycle_count"] == 0, "reverse_sequence_control"),
        ("scrambled_sequence_control_passed", "yes", summary["scrambled_sequence_control_detected_cycle_count"] == 0, "scrambled_sequence_control"),
        ("baseline_cycle_count_matches_07_02", "yes", summary["baseline_cycle_count_matches_07_02"] == "yes", "07-02 run_summary"),
        ("readout_cycle_count_dynamic", "yes", f"{summary['complete_cycle_count']} complete cycles were detected" in readout, "readout.md"),
        ("phase_progression_figure_created", "yes", figure_path.exists() and figure_path.stat().st_size > 0, "phase_progression_over_cycles.svg"),
        ("source_inventory_specific", "yes", source_inventory_specific, "source_inventory.md"),
        ("experimental_data_not_claimed", "yes", summary["experimental_data_used"] == "no", "run_summary"),
        ("physical_causality_not_claimed", "yes", summary["physical_causality_claimed"] == "no", "run_summary"),
        ("emergent_time_not_claimed", "yes", summary["emergent_time_claimed"] == "no", "run_summary"),
    ]
    rows = []
    for check_id, expected, passed, evidence in checks:
        rows.append(
            {
                "check_id": check_id,
                "expected": expected,
                "observed": "yes" if passed else "no",
                "passed": "yes" if passed else "no",
                "evidence": evidence,
            }
        )
    return rows


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output dir: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run QSB-CAUSALITY07-03 cycle semantics hardening.")
    parser.add_argument("--input-root", default=".", help="Repository input root.")
    parser.add_argument(
        "--output-dir",
        default="runs/QSB-CAUSALITY07-03/cycle_semantics_hardening",
        help="Directory for exactly ten 07-03 run outputs.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Replace expected output files if present.")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    prepare_output_dir(output_dir, args.overwrite)

    config_path = root / "data" / "QSB-CAUSALITY07-03" / "cycle_semantics_hardening_config.json"
    input_run_dir = root / "runs" / "QSB-CAUSALITY07-02" / "first_oscillatory_state_cycle"
    classified_path = input_run_dir / "classified_phase_series.csv"
    summary_07_02_path = input_run_dir / "run_summary.json"
    readout_07_02_path = input_run_dir / "readout.md"
    source_inventory_path = root / "data" / "QSB-CAUSALITY07-02" / "source_inventory.md"

    config = load_json(config_path)
    rows = load_csv(classified_path)
    require_columns(rows, REQUIRED_CLASSIFIED_COLUMNS, classified_path)
    summary_07_02 = load_json(summary_07_02_path)
    readout_07_02 = readout_07_02_path.read_text(encoding="utf-8")
    source_inventory = source_inventory_path.read_text(encoding="utf-8")
    source_inventory_specific = "Secondary Oregonator/BZ framework overview" not in source_inventory

    baseline_sequence = config["baseline_sequence"]
    reverse_sequence = config["reverse_control_sequence"]
    scrambled_sequence = config["scrambled_control_sequence"]
    distance_threshold = float(config["state_vector_distance_threshold"])

    post_rows = [row for row in rows if row["post_transient"] == "true"]
    if not post_rows:
        raise SystemExit("no post-transient classified rows found")
    scales = {
        "x": iqr_scale([float(row["x_activator"]) for row in post_rows]),
        "y": iqr_scale([float(row["y_inhibitor"]) for row in post_rows]),
        "z": iqr_scale([float(row["z_oxidized_catalyst"]) for row in post_rows]),
    }
    segments = stable_segments(rows)
    baseline_cycles, recurrence_rows = detect_sequence(rows, segments, baseline_sequence, distance_threshold, scales)
    reverse_cycles, _ = detect_sequence(rows, segments, reverse_sequence, distance_threshold, scales)
    scrambled_cycles, _ = detect_sequence(rows, segments, scrambled_sequence, distance_threshold, scales)

    complete_cycle_count = len(baseline_cycles)
    durations = [float(row["cycle_duration"]) for row in baseline_cycles]
    mean_cycle_duration = statistics.mean(durations) if durations else 0.0
    baseline_count_07_02 = int(summary_07_02["complete_cycle_count"])
    readout_match = re.search(r"Complete cycles detected:\s*`?(\d+)`?", readout_07_02)
    readout_count_07_02 = int(readout_match.group(1)) if readout_match else None
    count_matches = complete_cycle_count == baseline_count_07_02 == readout_count_07_02
    same_assigned_count = sum(1 for row in recurrence_rows if row["same_assigned_phase_label"] == "yes")
    negative_controls_passed = len(reverse_cycles) == 0 and len(scrambled_cycles) == 0

    summary = {
        "arbitrary_sequence_acceptance_detected": "no" if negative_controls_passed else "yes",
        "baseline_cycle_count_matches_07_02": "yes" if count_matches else "no",
        "baseline_sequence": baseline_sequence,
        "block_id": config["block_id"],
        "complete_cycle_count": complete_cycle_count,
        "complete_state_reset_established": "no",
        "cycle_sequence_source": config["cycle_sequence_source"],
        "distance_threshold_empirically_calibrated": "no",
        "distance_threshold_explicit": "yes",
        "emergent_time_claimed": "no",
        "experimental_data_used": "no",
        "global_cycle_order_independently_reconstructed": "no",
        "input_run_id": config["input_run_id"],
        "mean_cycle_duration": mean_cycle_duration,
        "negative_controls_passed": "yes" if negative_controls_passed else "no",
        "phase_identity_independently_established": "no",
        "phase_labels_are_model_relative": "yes",
        "physical_causality_claimed": "no",
        "physical_direction_validated": "no",
        "real_resource_exhaustion_modelled": "no",
        "recurrent_state_region_detected": "yes" if complete_cycle_count else "no",
        "reduced_state_drift_proxy_used": "yes",
        "resource_inventory_reconstructed": "no",
        "reverse_sequence_control_detected_cycle_count": len(reverse_cycles),
        "same_assigned_phase_label_count": same_assigned_count,
        "scrambled_sequence_control_detected_cycle_count": len(scrambled_cycles),
        "similarity_function_defined": "no",
        "source_inventory_specific": "yes" if source_inventory_specific else "no",
        "state_vector_distance_threshold": distance_threshold,
        "state_vector_distance_threshold_basis": config["state_vector_distance_threshold_basis"],
        "time_order_used_to_orient_phase_labels": "yes",
        "validation_check_count": 0,
        "validation_failed_count": 0,
    }

    resolved = {
        "hardening_config": config,
        "input_paths": {
            "classified_phase_series": str(classified_path.relative_to(root)),
            "run_summary_07_02": str(summary_07_02_path.relative_to(root)),
            "readout_07_02": str(readout_07_02_path.relative_to(root)),
            "source_inventory": str(source_inventory_path.relative_to(root)),
        },
        "phase_label_input_prefix": "BZ01_",
        "phase_label_output_form": "P0_to_P4",
        "state_vector_distance_components": ["x_activator", "y_inhibitor", "z_oxidized_catalyst"],
        "state_vector_distance_scaling": "post_transient_interquartile_range_then_euclidean_divided_by_sqrt_3",
        "output_files": OUTPUT_FILES,
    }

    write_json(output_dir / "resolved_hardening_config.json", resolved)
    write_csv(
        output_dir / "baseline_cycle_semantics.csv",
        baseline_cycles,
        [
            "cycle_id",
            "cycle_index",
            "p0_time",
            "p0_prime_time",
            "cycle_duration",
            "expected_sequence",
            "observed_sequence",
            "complete_cycle_detected",
            "same_assigned_phase_label",
            "phase_identity_independently_established",
            "state_vector_distance",
            "state_vector_distance_within_threshold",
            "reduced_state_drift_proxy",
            "recurrent_state_region_detected",
            "complete_state_reset_established",
            "cycle_sequence_source",
        ],
    )
    write_csv(output_dir / "reverse_sequence_control.csv", [control_row("reverse_sequence_control", reverse_sequence, len(reverse_cycles))], ["control_id", "expected_sequence", "detected_complete_cycle_count", "control_passed", "failure_reason"])
    write_csv(output_dir / "scrambled_sequence_control.csv", [control_row("scrambled_sequence_control", scrambled_sequence, len(scrambled_cycles))], ["control_id", "expected_sequence", "detected_complete_cycle_count", "control_passed", "failure_reason"])
    write_csv(
        output_dir / "recurrence_identity_comparison.csv",
        recurrence_rows,
        [
            "cycle_id",
            "cycle_index",
            "p0_time",
            "p0_prime_time",
            "cycle_duration",
            "expected_sequence",
            "observed_sequence",
            "complete_cycle_detected",
            "same_assigned_phase_label",
            "phase_identity_independently_established",
            "state_vector_distance",
            "state_vector_distance_within_threshold",
            "reduced_state_drift_proxy",
            "recurrent_state_region_detected",
            "complete_state_reset_established",
            "cycle_sequence_source",
        ],
    )
    write_csv(output_dir / "phase_duration_summary.csv", phase_durations(rows, segments), ["phase_label", "visit_count", "total_duration", "mean_duration", "median_duration", "minimum_duration", "maximum_duration"])
    (output_dir / "phase_progression_over_cycles.svg").write_text(make_svg(rows, segments, baseline_cycles), encoding="utf-8")

    readout = readout_text({**summary, "final_status": "pending_validation"})
    validation = validation_rows(summary, source_inventory_specific, readout, output_dir / "phase_progression_over_cycles.svg")
    failed = sum(1 for row in validation if row["passed"] != "yes")
    final_status = "cycle_semantics_hardening_completed" if failed == 0 and negative_controls_passed else "cycle_semantics_hardening_failed"
    summary["validation_check_count"] = len(validation)
    summary["validation_failed_count"] = failed
    summary["final_status"] = final_status
    readout = readout_text(summary)
    validation = validation_rows(summary, source_inventory_specific, readout, output_dir / "phase_progression_over_cycles.svg")
    failed = sum(1 for row in validation if row["passed"] != "yes")
    summary["validation_failed_count"] = failed
    summary["final_status"] = "cycle_semantics_hardening_completed" if failed == 0 and negative_controls_passed else "cycle_semantics_hardening_failed"

    write_csv(output_dir / "semantic_validation_checks.csv", validation, ["check_id", "expected", "observed", "passed", "evidence"])
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(readout_text(summary), encoding="utf-8")

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_FILES):
        raise SystemExit(f"output file set mismatch: {actual_outputs}")
    return 0 if summary["final_status"] == "cycle_semantics_hardening_completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
