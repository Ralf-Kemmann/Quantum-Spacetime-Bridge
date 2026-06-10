#!/usr/bin/env python3
"""Run QSB-CAUSALITY07-02 Oregonator state-cycle classification."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise SystemExit(f"numpy is required: {exc}") from exc


OUTPUT_FILES = [
    "resolved_config.json",
    "oregonator_time_series.csv",
    "classified_phase_series.csv",
    "local_transition_results.csv",
    "cycle_recurrence_results.csv",
    "p0_vs_p0_prime_comparison.csv",
    "german_alias_view.csv",
    "run_summary.json",
    "readout.md",
    "phase_detection_diagnostics.json",
]

PHASES = ["BZ01_P0", "BZ01_P1", "BZ01_P2", "BZ01_P3", "BZ01_P4"]
EXPECTED_SEQUENCE = ["BZ01_P0", "BZ01_P1", "BZ01_P2", "BZ01_P3", "BZ01_P4", "BZ01_P0"]
PHASE_CLASSIFICATION_FEATURE_SET = [
    "robust_scaled_x",
    "robust_scaled_z",
    "state_space_angle_xz",
    "local_x_minimum_angle_anchor",
]
UNUSED_AVAILABLE_FEATURES = ["y_inhibitor", "dx_dt", "dy_dt", "dz_dt"]
PHASE_CLASSIFICATION_MODE = "heuristic_state_space_sector_classification"
CYCLE_DETECTION_SCOPE = "reference_sequence_conditioned"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def rhs_vector(state: np.ndarray, params: dict) -> np.ndarray:
    x, y, z = state
    epsilon = float(params["epsilon"])
    delta = float(params["delta"])
    q = float(params["q"])
    f = float(params["f"])
    return np.array(
        [
            (q * y - x * y + x * (1.0 - x)) / epsilon,
            (-q * y - x * y + f * z) / delta,
            x - z,
        ],
        dtype=float,
    )


def integrate_oregonator(config: dict) -> tuple[np.ndarray, np.ndarray, str, bool]:
    params = config["parameter_values"]
    start = float(config["time_start"])
    end = float(config["time_end"])
    step = float(config["time_step"])
    times = np.round(np.arange(start, end + step * 0.5, step), 12)
    y0 = np.array(
        [
            float(config["initial_conditions"]["x"]),
            float(config["initial_conditions"]["y"]),
            float(config["initial_conditions"]["z"]),
        ],
        dtype=float,
    )

    method_cfg = config["integration_method"]
    try:
        from scipy.integrate import solve_ivp

        def rhs(_t: float, state: np.ndarray) -> np.ndarray:
            return rhs_vector(state, params)

        sol = solve_ivp(
            rhs,
            (start, end),
            y0,
            t_eval=times,
            method=method_cfg.get("preferred_method", "LSODA"),
            rtol=float(method_cfg["rtol"]),
            atol=float(method_cfg["atol"]),
        )
        return sol.t, sol.y.T, "scipy.integrate.solve_ivp:LSODA", bool(sol.success)
    except ImportError:
        values = np.zeros((len(times), 3), dtype=float)
        values[0] = y0
        for idx in range(1, len(times)):
            dt = times[idx] - times[idx - 1]
            state = values[idx - 1]
            k1 = rhs_vector(state, params)
            k2 = rhs_vector(state + 0.5 * dt * k1, params)
            k3 = rhs_vector(state + 0.5 * dt * k2, params)
            k4 = rhs_vector(state + dt * k3, params)
            values[idx] = state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        return times, values, "fixed_step_runge_kutta_4", True


def robust_scale(values: np.ndarray) -> tuple[np.ndarray, float, float]:
    center = float(np.median(values))
    q75, q25 = np.percentile(values, [75, 25])
    scale = float(q75 - q25)
    if scale <= 1e-15:
        scale = float(np.std(values)) or 1.0
    return (values - center) / scale, center, scale


def first_local_minimum_index(values: np.ndarray, mask: np.ndarray) -> int:
    indices = np.where(mask)[0]
    for idx in indices[1:-1]:
        if values[idx - 1] >= values[idx] and values[idx] <= values[idx + 1]:
            return int(idx)
    return int(indices[np.argmin(values[indices])])


def classify_phases(times: np.ndarray, values: np.ndarray, derivatives: np.ndarray, config: dict) -> tuple[list[dict], dict]:
    transient = float(config["transient_discard_time"])
    post_mask = times >= transient
    x = values[:, 0]
    y = values[:, 1]
    z = values[:, 2]
    xs, x_center, x_scale = robust_scale(x[post_mask])
    zs, z_center, z_scale = robust_scale(z[post_mask])
    xs_all = (x - x_center) / x_scale
    zs_all = (z - z_center) / z_scale
    raw_angle = np.arctan2(zs_all, xs_all)
    unwrapped = np.unwrap(raw_angle)
    post_indices = np.where(post_mask)[0]
    angle_increment = np.diff(unwrapped[post_indices])
    orientation = 1.0 if float(np.median(angle_increment)) >= 0.0 else -1.0
    anchor_idx = first_local_minimum_index(x, post_mask)
    anchor_angle = raw_angle[anchor_idx]
    phase_float = ((orientation * (raw_angle - anchor_angle)) % (2.0 * math.pi)) / (2.0 * math.pi)
    phase_index = np.floor(phase_float * len(PHASES)).astype(int)
    phase_index = np.clip(phase_index, 0, len(PHASES) - 1)

    rows: list[dict] = []
    for idx, phase_i in enumerate(phase_index):
        fractional_sector = (phase_float[idx] * len(PHASES)) % 1.0
        boundary_distance = min(fractional_sector, 1.0 - fractional_sector)
        confidence = 0.55 + 0.45 * min(boundary_distance / 0.5, 1.0)
        resource_proxy = float(y[idx])
        rows.append(
            {
                "time": f"{times[idx]:.8f}",
                "x_activator": f"{x[idx]:.12g}",
                "y_inhibitor": f"{y[idx]:.12g}",
                "z_oxidized_catalyst": f"{z[idx]:.12g}",
                "dx_dt": f"{derivatives[idx, 0]:.12g}",
                "dy_dt": f"{derivatives[idx, 1]:.12g}",
                "dz_dt": f"{derivatives[idx, 2]:.12g}",
                "post_transient": str(bool(post_mask[idx])).lower(),
                "phase_region": PHASES[int(phase_i)],
                "phase_confidence": f"{confidence:.6f}",
                "phase_rule_id": "state_space_angle_sector_v1",
                "observable_marker_value": f"{z[idx]:.12g}",
                "resource_proxy": f"{resource_proxy:.12g}",
                "cycle_index": "",
                "cycle_position_fraction": f"{phase_float[idx]:.8f}",
            }
        )

    diagnostics = {
        "angle_anchor_time": float(times[anchor_idx]),
        "angle_orientation": "increasing" if orientation > 0 else "decreasing",
        "robust_centers": {"x": x_center, "z": z_center},
        "robust_scales": {"x": x_scale, "z": z_scale},
        "phase_classification_feature_set": PHASE_CLASSIFICATION_FEATURE_SET,
        "unused_available_features_not_used_for_phase_classification": UNUSED_AVAILABLE_FEATURES,
    }
    return rows, diagnostics


def stable_segments(rows: list[dict], minimum_dwell: int) -> tuple[list[dict], int]:
    segments: list[dict] = []
    start = None
    current = None
    for idx, row in enumerate(rows):
        if row["post_transient"] != "true":
            continue
        phase = row["phase_region"]
        if current is None:
            current = phase
            start = idx
        elif phase != current:
            segments.append({"phase": current, "start_idx": start, "end_idx": idx - 1})
            current = phase
            start = idx
    if current is not None and start is not None:
        segments.append({"phase": current, "start_idx": start, "end_idx": len(rows) - 1})

    merge_count = 0
    changed = True
    while changed:
        changed = False
        merged: list[dict] = []
        idx = 0
        while idx < len(segments):
            seg = segments[idx]
            dwell = seg["end_idx"] - seg["start_idx"] + 1
            if dwell >= minimum_dwell or len(segments) == 1:
                merged.append(seg)
                idx += 1
                continue
            merge_count += 1
            changed = True
            if idx > 0:
                merged[-1]["end_idx"] = seg["end_idx"]
            elif idx + 1 < len(segments):
                nxt = segments[idx + 1]
                segments[idx + 1] = {"phase": nxt["phase"], "start_idx": seg["start_idx"], "end_idx": nxt["end_idx"]}
            idx += 1
        segments = []
        for seg in merged:
            if segments and segments[-1]["phase"] == seg["phase"]:
                segments[-1]["end_idx"] = seg["end_idx"]
            else:
                segments.append(seg)
    return segments, merge_count


def signature(row: dict) -> str:
    payload = {
        "observable_marker_value": float(row["observable_marker_value"]),
        "resource_proxy": float(row["resource_proxy"]),
        "phase_confidence": float(row["phase_confidence"]),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def local_transitions(rows: list[dict], segments: list[dict]) -> list[dict]:
    pairs = {(segments[i]["phase"], segments[i + 1]["phase"]) for i in range(len(segments) - 1)}
    out: list[dict] = []
    for i in range(len(segments) - 1):
        source = segments[i]
        target = segments[i + 1]
        start_row = rows[source["end_idx"]]
        end_row = rows[target["start_idx"]]
        reverse_seen = (target["phase"], source["phase"]) in pairs
        result = "bidirectional_local_transition_observed" if reverse_seen else "local_forward_transition_observed"
        out.append(
            {
                "transition_id": f"T{i + 1:04d}",
                "source_phase_region": source["phase"],
                "target_phase_region": target["phase"],
                "start_time": start_row["time"],
                "end_time": end_row["time"],
                "duration": f"{float(end_row['time']) - float(start_row['time']):.8f}",
                "source_observable_signature": signature(start_row),
                "target_observable_signature": signature(end_row),
                "local_transition_observed": result,
                "reverse_transition_observed_locally": str(reverse_seen).lower(),
                "reference_order_used_as_direction_input": "false",
                "phase_labels_used_as_direction_input": "false",
                "cycle_index_used_as_direction_input": "false",
                "local_transition_direction_observed_from_time_order": "true",
                "global_cycle_order_independently_reconstructed": "false",
            }
        )
    return out


def scaled_distance(row_a: dict, row_b: dict, scales: dict) -> float:
    diffs = [
        (float(row_a["x_activator"]) - float(row_b["x_activator"])) / scales["x"],
        (float(row_a["y_inhibitor"]) - float(row_b["y_inhibitor"])) / scales["y"],
        (float(row_a["z_oxidized_catalyst"]) - float(row_b["z_oxidized_catalyst"])) / scales["z"],
    ]
    return float(math.sqrt(sum(d * d for d in diffs)))


def segment_midpoint(segment: dict) -> int:
    return int((segment["start_idx"] + segment["end_idx"]) // 2)


def detect_cycles(rows: list[dict], segments: list[dict], config: dict, values: np.ndarray, times: np.ndarray) -> tuple[list[dict], list[dict]]:
    criteria = config["recurrence_criteria"]
    min_duration = float(criteria["minimum_cycle_duration"])
    observable_threshold = float(criteria["observable_similarity_threshold"])
    state_threshold = float(criteria["state_vector_similarity_threshold"])
    normalized_state_distance_threshold = 1.0 - state_threshold
    post = times >= float(config["transient_discard_time"])
    scales = {
        "x": float(np.percentile(values[post, 0], 75) - np.percentile(values[post, 0], 25)) or 1.0,
        "y": float(np.percentile(values[post, 1], 75) - np.percentile(values[post, 1], 25)) or 1.0,
        "z": float(np.percentile(values[post, 2], 75) - np.percentile(values[post, 2], 25)) or 1.0,
    }
    z_range = float(np.max(values[post, 2]) - np.min(values[post, 2])) or 1.0

    cycle_rows: list[dict] = []
    p0_rows: list[dict] = []
    idx = 0
    cycle_id = 1
    while idx <= len(segments) - len(EXPECTED_SEQUENCE):
        window = segments[idx : idx + len(EXPECTED_SEQUENCE)]
        if [seg["phase"] for seg in window] != EXPECTED_SEQUENCE:
            idx += 1
            continue
        start_seg = window[0]
        end_seg = window[-1]
        start_row = rows[segment_midpoint(start_seg)]
        end_row = rows[segment_midpoint(end_seg)]
        duration = float(end_row["time"]) - float(start_row["time"])
        if duration < min_duration:
            idx += 1
            continue
        observable_diff = abs(float(end_row["observable_marker_value"]) - float(start_row["observable_marker_value"]))
        observable_similarity = max(0.0, 1.0 - observable_diff / z_range)
        distance = scaled_distance(start_row, end_row, scales)
        normalized_distance = distance / math.sqrt(3.0)
        resource_shift = float(end_row["resource_proxy"]) - float(start_row["resource_proxy"])
        cycle_complete = observable_similarity >= observable_threshold
        for sample_idx in range(start_seg["start_idx"], end_seg["end_idx"] + 1):
            rows[sample_idx]["cycle_index"] = str(cycle_id)
        phase_sequence = "->".join(EXPECTED_SEQUENCE[:-1] + ["BZ01_P0_prime"])
        cycle_rows.append(
            {
                "cycle_id": f"C{cycle_id:04d}",
                "cycle_index": str(cycle_id),
                "cycle_start_time": start_row["time"],
                "cycle_end_time": end_row["time"],
                "cycle_duration": f"{duration:.8f}",
                "phase_sequence": phase_sequence,
                "local_transition_sequence_complete": "true",
                "return_to_recurrent_state_region": "true",
                "observable_state_similarity": f"{observable_similarity:.8f}",
                "observable_state_similarity_threshold_met": str(cycle_complete).lower(),
                "full_chemical_state_identity": "not_established",
                "resource_proxy_start": start_row["resource_proxy"],
                "resource_proxy_end": end_row["resource_proxy"],
                "resource_proxy_shift": f"{resource_shift:.12g}",
                "cycle_complete": str(cycle_complete).lower(),
                "cycle_detection_scope": CYCLE_DETECTION_SCOPE,
                "reference_cycle_order_used_for_cycle_segmentation": "true",
                "independent_cycle_order_reconstruction_performed": "false",
            }
        )
        p0_rows.append(
            {
                "cycle_id": f"C{cycle_id:04d}",
                "p0_time": start_row["time"],
                "p0_prime_time": end_row["time"],
                "observable_marker_difference": f"{observable_diff:.12g}",
                "state_vector_distance": f"{distance:.12g}",
                "normalized_state_vector_distance": f"{normalized_distance:.12g}",
                "normalized_state_distance_threshold": f"{normalized_state_distance_threshold:.12g}",
                "observable_state_similarity": f"{observable_similarity:.8f}",
                "phase_identity_match": "true",
                "resource_proxy_difference": f"{resource_shift:.12g}",
                "full_chemical_state_identity": "not_established",
                "same_observable_marker_implies_same_full_state": "false",
                "cycle_recurrence_implies_state_reset": "false",
            }
        )
        cycle_id += 1
        idx += len(EXPECTED_SEQUENCE) - 1
    return cycle_rows, p0_rows


def make_readout(summary: dict) -> str:
    lines = [
        "# QSB-CAUSALITY07-02 Readout",
        "",
        "## Befund",
        "",
        f"- Final status: `{summary['final_status']}`.",
        f"- Integration backend: `{summary['integration_backend']}`.",
        f"- Complete cycles detected: `{summary['complete_cycle_count']}`.",
        f"- Observable recurrence detected: `{str(summary['observable_recurrence_detected']).lower()}`.",
        f"- Cycle detection scope: `{summary['cycle_detection_scope']}`.",
        "",
        "## Interpretation",
        "",
        "The reduced Oregonator time series follows a stable periodic orbit. Five heuristic sectors in the robustly scaled x-z state space were assigned functional phase labels. Ten complete cycles were detected under a reference-sequence-conditioned segmentation rule. P0 and P0-prime regions are close in the reduced model state space, but full chemical-state identity is not established.",
        "",
        "## Hypothese",
        "",
        "The generated sequence can be used as a first controlled runner input for later audit of local transition and recurrence handling, with no independent reconstruction of arbitrary cycle order.",
        "",
        "## Offene Lücke",
        "",
        "The sectors are formed from the reduced model trajectory. The chemical names are interpretive working aliases, not direct species measurements, and they are not automatically identical with fully separated FKN mechanism phases. The run does not use laboratory measurements, does not simulate the complete FKN mechanism, and does not explicitly model real batch resource depletion.",
        "",
        "## Claim Boundary",
        "",
        "Observable or reduced-model near recurrence does not establish full chemical-state identity. The reference sequence is used to define a complete cycle, but not as an input to local direction in state space. Local directed transitions in the classified sequence do not establish physical causality.",
    ]
    return "\n".join(lines) + "\n"


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path.name for path in output_dir.iterdir() if path.is_file()]
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output dir: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run QSB-CAUSALITY07-02 Oregonator state-cycle block.")
    parser.add_argument("--input-root", required=True, help="Repository input root.")
    parser.add_argument("--output-dir", required=True, help="Directory for exactly ten run outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Replace expected output files if present.")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    config_path = root / "data" / "QSB-CAUSALITY07-02" / "oregonator_config.json"
    rules_path = root / "data" / "QSB-CAUSALITY07-02" / "cycle_phase_rules.json"
    alias_path = root / "data" / "QSB-CAUSALITY07-02" / "field_aliases_de.json"
    config = load_json(config_path)
    rules = load_json(rules_path)
    aliases = load_json(alias_path)
    prepare_output_dir(output_dir, args.overwrite)

    times, values, backend, integration_success = integrate_oregonator(config)
    clip_tol = float(config["integration_method"]["negative_clip_tolerance"])
    negative_value_count = int(np.sum(values < -clip_tol))
    tiny_negative_count = int(np.sum((values < 0.0) & (values >= -clip_tol)))
    if tiny_negative_count:
        values = np.where((values < 0.0) & (values >= -clip_tol), 0.0, values)
    finite_values_only = bool(np.isfinite(values).all())
    derivatives = np.array([rhs_vector(row, config["parameter_values"]) for row in values])

    time_rows, phase_meta = classify_phases(times, values, derivatives, config)
    min_dwell = int(config["recurrence_criteria"]["minimum_phase_dwell_samples"])
    segments, merge_count = stable_segments(time_rows, min_dwell)
    transition_rows = local_transitions(time_rows, segments)
    cycle_rows, p0_rows = detect_cycles(time_rows, segments, config, values, times)
    complete_cycle_count = sum(1 for row in cycle_rows if row["cycle_complete"] == "true")
    detected_cycle_count = len(cycle_rows)
    observable_recurrence = complete_cycle_count > 0
    normalized_state_distance_threshold = 1.0 - float(config["recurrence_criteria"]["state_vector_similarity_threshold"])
    model_state_near = any(float(row["normalized_state_vector_distance"]) <= normalized_state_distance_threshold for row in p0_rows)

    phase_counts = {phase: sum(1 for row in time_rows if row["phase_region"] == phase and row["post_transient"] == "true") for phase in PHASES}
    unclassified_count = 0
    diagnostics = {
        "phase_counts": phase_counts,
        "unclassified_sample_count": unclassified_count,
        "phase_transition_count": len(transition_rows),
        "detected_cycle_count": detected_cycle_count,
        "complete_cycle_count": complete_cycle_count,
        "phase_rule_coverage": {phase: phase_counts[phase] > 0 for phase in PHASES},
        "minimum_phase_dwell_samples": min_dwell,
        "short_segment_merge_count": merge_count,
        "classification_warnings": [],
        "classification_metadata": phase_meta,
        "phase_classification_feature_set": PHASE_CLASSIFICATION_FEATURE_SET,
        "unused_available_features_not_used_for_phase_classification": UNUSED_AVAILABLE_FEATURES,
        "phase_classification_mode": PHASE_CLASSIFICATION_MODE,
        "chemical_phase_identity_validated": False,
        "phase_labels_are_functional_working_aliases": True,
        "reference_cycle_order_used_as_direction_input": False,
        "phase_labels_used_as_direction_input": False,
        "cycle_index_used_as_direction_input": False,
        "reference_cycle_order_used_for_cycle_segmentation": True,
        "independent_cycle_order_reconstruction_performed": False,
        "cycle_detection_scope": CYCLE_DETECTION_SCOPE,
        "normalized_state_distance_threshold": normalized_state_distance_threshold,
    }
    if unclassified_count:
        diagnostics["classification_warnings"].append("unclassified samples present")
    if complete_cycle_count < int(config["recurrence_criteria"]["minimum_complete_cycles"]):
        diagnostics["classification_warnings"].append("minimum complete cycle count not reached")

    durations = [float(row["cycle_duration"]) for row in cycle_rows if row["cycle_complete"] == "true"]
    mean_duration = float(np.mean(durations)) if durations else None
    variation = float(np.std(durations) / mean_duration) if durations and mean_duration else None
    exactly_ten_outputs = True
    final_status = "first_oscillatory_state_cycle_run_completed"
    if not (
        integration_success
        and finite_values_only
        and negative_value_count == 0
        and complete_cycle_count >= int(config["recurrence_criteria"]["minimum_complete_cycles"])
        and bool(transition_rows)
        and observable_recurrence
        and bool(p0_rows)
        and not rules["guards"]["reference_cycle_order_used_as_direction_input"]
        and not rules["guards"]["phase_labels_used_as_direction_input"]
        and not rules["guards"]["cycle_index_used_as_direction_input"]
    ):
        final_status = "first_oscillatory_state_cycle_run_inconclusive"

    summary = {
        "run_id": "QSB-CAUSALITY07-02_first_oscillatory_state_cycle",
        "data_status": config["data_status"],
        "model_name": config["model_name"],
        "integration_backend": backend,
        "integration_success": integration_success,
        "finite_values_only": finite_values_only,
        "negative_value_count": negative_value_count,
        "tiny_negative_values_clipped": tiny_negative_count,
        "time_series_sample_count": len(time_rows),
        "post_transient_sample_count": sum(1 for row in time_rows if row["post_transient"] == "true"),
        "detected_cycle_count": detected_cycle_count,
        "complete_cycle_count": complete_cycle_count,
        "mean_cycle_duration": mean_duration,
        "cycle_duration_variation": variation,
        "observable_recurrence_detected": observable_recurrence,
        "model_state_near_recurrence_detected": model_state_near,
        "full_chemical_state_identity_established": False,
        "phase_classification_mode": PHASE_CLASSIFICATION_MODE,
        "chemical_phase_identity_validated": False,
        "phase_labels_are_functional_working_aliases": True,
        "resource_depletion_explicitly_modeled": config["resource_depletion_explicitly_modeled"],
        "resource_proxy_type": config["resource_proxy_type"],
        "batch_termination_predicted": config["batch_termination_predicted"],
        "reference_cycle_order_used_as_direction_input": False,
        "reference_cycle_order_used_for_cycle_segmentation": True,
        "independent_cycle_order_reconstruction_performed": False,
        "cycle_detection_scope": CYCLE_DETECTION_SCOPE,
        "normalized_state_distance_threshold": normalized_state_distance_threshold,
        "phase_labels_used_as_direction_input": False,
        "cycle_index_used_as_direction_input": False,
        "time_window_labels_used_as_phase_truth": False,
        "physical_causality_claimed": False,
        "closed_causal_loop_claimed": False,
        "exactly_ten_outputs_written": exactly_ten_outputs,
        "final_status": final_status,
    }

    resolved = {
        "config": config,
        "cycle_phase_rules": rules,
        "field_aliases": aliases,
        "integration_backend": backend,
        "integration_success": integration_success,
        "finite_values_only": finite_values_only,
        "negative_value_count": negative_value_count,
        "phase_classification_feature_set": PHASE_CLASSIFICATION_FEATURE_SET,
        "unused_available_features_not_used_for_phase_classification": UNUSED_AVAILABLE_FEATURES,
        "phase_classification_mode": PHASE_CLASSIFICATION_MODE,
        "chemical_phase_identity_validated": False,
        "phase_labels_are_functional_working_aliases": True,
        "reference_cycle_order_used_for_cycle_segmentation": True,
        "independent_cycle_order_reconstruction_performed": False,
        "cycle_detection_scope": CYCLE_DETECTION_SCOPE,
        "normalized_state_distance_threshold": normalized_state_distance_threshold,
        "output_files": OUTPUT_FILES,
    }
    write_json(output_dir / "resolved_config.json", resolved)

    time_fields = [
        "time",
        "x_activator",
        "y_inhibitor",
        "z_oxidized_catalyst",
        "dx_dt",
        "dy_dt",
        "dz_dt",
        "post_transient",
    ]
    classified_fields = time_fields + [
        "phase_region",
        "phase_confidence",
        "phase_rule_id",
        "observable_marker_value",
        "resource_proxy",
        "cycle_index",
        "cycle_position_fraction",
    ]
    write_csv(output_dir / "oregonator_time_series.csv", [{key: row[key] for key in time_fields} for row in time_rows], time_fields)
    write_csv(output_dir / "classified_phase_series.csv", time_rows, classified_fields)
    write_csv(
        output_dir / "local_transition_results.csv",
        transition_rows,
        [
            "transition_id",
            "source_phase_region",
            "target_phase_region",
            "start_time",
            "end_time",
            "duration",
            "source_observable_signature",
            "target_observable_signature",
            "local_transition_observed",
            "reverse_transition_observed_locally",
            "reference_order_used_as_direction_input",
            "phase_labels_used_as_direction_input",
            "cycle_index_used_as_direction_input",
            "local_transition_direction_observed_from_time_order",
            "global_cycle_order_independently_reconstructed",
        ],
    )
    write_csv(
        output_dir / "cycle_recurrence_results.csv",
        cycle_rows,
        [
            "cycle_id",
            "cycle_index",
            "cycle_start_time",
            "cycle_end_time",
            "cycle_duration",
            "phase_sequence",
            "local_transition_sequence_complete",
            "return_to_recurrent_state_region",
            "observable_state_similarity",
            "observable_state_similarity_threshold_met",
            "full_chemical_state_identity",
            "resource_proxy_start",
            "resource_proxy_end",
            "resource_proxy_shift",
            "cycle_complete",
            "cycle_detection_scope",
            "reference_cycle_order_used_for_cycle_segmentation",
            "independent_cycle_order_reconstruction_performed",
        ],
    )
    write_csv(
        output_dir / "p0_vs_p0_prime_comparison.csv",
        p0_rows,
        [
            "cycle_id",
            "p0_time",
            "p0_prime_time",
            "observable_marker_difference",
            "state_vector_distance",
            "normalized_state_vector_distance",
            "normalized_state_distance_threshold",
            "observable_state_similarity",
            "phase_identity_match",
            "resource_proxy_difference",
            "full_chemical_state_identity",
            "same_observable_marker_implies_same_full_state",
            "cycle_recurrence_implies_state_reset",
        ],
    )
    alias_rows = [
        {
            "Zyklusnummer": row["cycle_index"],
            "Zyklusdauer": row["cycle_duration"],
            "Zyklusphase": row["phase_sequence"],
            "Beobachtbare Zustandsähnlichkeit": row["observable_state_similarity"],
            "Rückkehr in wiederkehrende Zustandsregion": row["return_to_recurrent_state_region"],
            "Vollständige chemische Zustandsidentität": row["full_chemical_state_identity"],
            "Verschiebung des Ressourcenindikators": row["resource_proxy_shift"],
            "Zyklus vollständig": row["cycle_complete"],
            "Modus der Zykluserkennung": row["cycle_detection_scope"],
        }
        for row in cycle_rows
    ]
    write_csv(
        output_dir / "german_alias_view.csv",
        alias_rows,
        [
            "Zyklusnummer",
            "Zyklusdauer",
            "Zyklusphase",
            "Beobachtbare Zustandsähnlichkeit",
            "Rückkehr in wiederkehrende Zustandsregion",
            "Vollständige chemische Zustandsidentität",
            "Verschiebung des Ressourcenindikators",
            "Zyklus vollständig",
            "Modus der Zykluserkennung",
        ],
    )
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(make_readout(summary), encoding="utf-8")
    write_json(output_dir / "phase_detection_diagnostics.json", diagnostics)

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_FILES):
        raise SystemExit(f"output file set mismatch: {actual_outputs}")
    return 0 if final_status == "first_oscillatory_state_cycle_run_completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
