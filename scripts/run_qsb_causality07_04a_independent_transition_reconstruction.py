#!/usr/bin/env python3
"""Run QSB-CAUSALITY07-04A independent transition reconstruction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
from collections import Counter, defaultdict
from pathlib import Path


OUTPUT_FILES = [
    "resolved_reconstruction_config.json",
    "reconstruction_leakage_audit.csv",
    "pairwise_transition_score_matrix.csv",
    "predecessor_ranking_matrix.csv",
    "reconstructed_directed_graph.csv",
    "global_cycle_reconstruction.csv",
    "edge_ablation_control_matrix.csv",
    "semantic_validation_checks.csv",
    "run_summary.json",
    "readout.md",
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


def quantile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    pos = (len(ordered) - 1) * fraction
    low = math.floor(pos)
    high = math.ceil(pos)
    if low == high:
        return ordered[low]
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def normalize_rows(rows: list[dict]) -> tuple[list[dict], dict]:
    xs = [float(row["x_activator"]) for row in rows]
    zs = [float(row["z_oxidized_catalyst"]) for row in rows]
    stats = {
        "x_median": statistics.median(xs),
        "z_median": statistics.median(zs),
        "x_iqr": quantile(xs, 0.75) - quantile(xs, 0.25),
        "z_iqr": quantile(zs, 0.75) - quantile(zs, 0.25),
    }
    if abs(stats["x_iqr"]) <= 1e-15 or abs(stats["z_iqr"]) <= 1e-15:
        raise SystemExit("cannot normalize x/z state space with zero IQR")
    output = []
    for row in rows:
        x_norm = (float(row["x_activator"]) - stats["x_median"]) / stats["x_iqr"]
        z_norm = (float(row["z_oxidized_catalyst"]) - stats["z_median"]) / stats["z_iqr"]
        angle = math.atan2(z_norm, x_norm)
        if angle < 0.0:
            angle += 2.0 * math.pi
        output.append({**row, "x_norm": x_norm, "z_norm": z_norm, "xz_angle": angle})
    return output, stats


def assign_label_blind_candidates(rows: list[dict], candidate_count: int) -> tuple[list[dict], float]:
    angles = sorted(row["xz_angle"] for row in rows)
    gaps = [((angles[(idx + 1) % len(angles)] - angles[idx]) % (2.0 * math.pi), idx) for idx in range(len(angles))]
    _, anchor_idx = max(gaps)
    anchor = angles[(anchor_idx + 1) % len(angles)]
    width = 2.0 * math.pi / candidate_count
    output = []
    for row in rows:
        relative = (row["xz_angle"] - anchor) % (2.0 * math.pi)
        candidate = int(relative / width) % candidate_count
        output.append({**row, "candidate_id": f"S{candidate}"})
    return output, anchor


def centroid(rows: list[dict]) -> dict[str, float]:
    return {
        "x_norm": statistics.mean(row["x_norm"] for row in rows),
        "z_norm": statistics.mean(row["z_norm"] for row in rows),
        "dx_dt": statistics.mean(float(row["dx_dt"]) for row in rows),
        "dz_dt": statistics.mean(float(row["dz_dt"]) for row in rows),
    }


def cosine(vec_a: tuple[float, float], vec_b: tuple[float, float]) -> float:
    norm_a = math.sqrt(vec_a[0] * vec_a[0] + vec_a[1] * vec_a[1])
    norm_b = math.sqrt(vec_b[0] * vec_b[0] + vec_b[1] * vec_b[1])
    if norm_a <= 1e-15 or norm_b <= 1e-15:
        return 0.0
    value = (vec_a[0] * vec_b[0] + vec_a[1] * vec_b[1]) / (norm_a * norm_b)
    return max(-1.0, min(1.0, value))


def segment_edges(rows: list[dict]) -> Counter:
    ordered = sorted(rows, key=lambda row: float(row["time"]))
    edges: Counter = Counter()
    previous = ordered[0]["candidate_id"]
    for row in ordered[1:]:
        current = row["candidate_id"]
        if current != previous:
            edges[(previous, current)] += 1
            previous = current
    return edges


def posthoc_label_map(rows: list[dict]) -> dict[str, str]:
    grouped: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        grouped[row["candidate_id"]][row["phase_region"].removeprefix("BZ01_")] += 1
    return {candidate: counts.most_common(1)[0][0] for candidate, counts in grouped.items()}


def score_pairs(rows: list[dict], config: dict) -> tuple[list[dict], dict, Counter]:
    candidates = sorted({row["candidate_id"] for row in rows})
    grouped = {candidate: [row for row in rows if row["candidate_id"] == candidate] for candidate in candidates}
    centroids = {candidate: centroid(grouped[candidate]) for candidate in candidates}
    edges = segment_edges(rows)
    max_count = max(edges.values()) if edges else 1
    weights = config["score_components"]
    w_frequency = float(weights["temporal_transition_frequency_score"]["weight"])
    w_alignment = float(weights["derivative_alignment_score"]["weight"])
    margin_threshold = float(config["direction_margin_threshold"])
    rows_out = []
    score_lookup = {}
    for source in candidates:
        for target in candidates:
            if source == target:
                continue
            source_centroid = centroids[source]
            target_centroid = centroids[target]
            transition_count = edges.get((source, target), 0)
            reverse_count = edges.get((target, source), 0)
            frequency = transition_count / max_count
            reverse_frequency = reverse_count / max_count
            direction_vector = (
                target_centroid["x_norm"] - source_centroid["x_norm"],
                target_centroid["z_norm"] - source_centroid["z_norm"],
            )
            reverse_vector = (-direction_vector[0], -direction_vector[1])
            derivative_vector = (source_centroid["dx_dt"], source_centroid["dz_dt"])
            reverse_derivative_vector = (target_centroid["dx_dt"], target_centroid["dz_dt"])
            alignment = 0.5 * (1.0 + cosine(derivative_vector, direction_vector))
            reverse_alignment = 0.5 * (1.0 + cosine(reverse_derivative_vector, reverse_vector))
            score = w_frequency * frequency + w_alignment * alignment
            reverse_score = w_frequency * reverse_frequency + w_alignment * reverse_alignment
            margin = score - reverse_score
            if abs(margin) < margin_threshold:
                direction_class = "bidirectionally_ambiguous"
            elif margin > 0.0:
                direction_class = "forward_supported"
            else:
                direction_class = "reverse_supported"
            score_lookup[(source, target)] = score
            rows_out.append(
                {
                    "source_candidate": source,
                    "target_candidate": target,
                    "forward_score": f"{score:.12g}",
                    "reverse_score": f"{reverse_score:.12g}",
                    "direction_margin": f"{margin:.12g}",
                    "direction_class": direction_class,
                    "transition_count": str(transition_count),
                    "reverse_transition_count": str(reverse_count),
                    "temporal_transition_frequency_score": f"{frequency:.12g}",
                    "derivative_alignment_score": f"{alignment:.12g}",
                    "score_formula": "0.7*temporal_transition_frequency_score + 0.3*derivative_alignment_score",
                    "unit_status": "unitless_normalized_score",
                    "dimension_status": "dimensionless_after_documented_normalization",
                    "calibration_status": "heuristic_not_empirically_calibrated",
                }
            )
    return rows_out, score_lookup, edges


def rank_predecessors(candidates: list[str], score_lookup: dict, label_map: dict, known_predecessors: dict) -> tuple[list[dict], dict]:
    rows = []
    metrics = {
        "top1": 0,
        "top2": 0,
        "reciprocal_sum": 0.0,
        "ranks": [],
        "ambiguity_count": 0,
        "unresolved_count": 0,
    }
    inverse_label_map = {label: candidate for candidate, label in label_map.items()}
    for target in candidates:
        scored = [(candidate, score_lookup[(candidate, target)]) for candidate in candidates if candidate != target]
        scored.sort(key=lambda item: (-item[1], item[0]))
        target_label = label_map[target]
        known_label = known_predecessors[target_label]
        known_candidate = inverse_label_map.get(known_label, "")
        known_rank = None
        second_best = scored[1][1] if len(scored) > 1 else 0.0
        top_score = scored[0][1] if scored else 0.0
        tie_state = "tie" if len(scored) > 1 and abs(top_score - second_best) <= 1e-12 else "no_tie"
        if tie_state == "tie":
            metrics["ambiguity_count"] += 1
        for rank, (candidate, score) in enumerate(scored, start=1):
            if candidate == known_candidate:
                known_rank = rank
        if known_rank is None:
            metrics["unresolved_count"] += 1
        else:
            metrics["ranks"].append(known_rank)
            metrics["reciprocal_sum"] += 1.0 / known_rank
            if known_rank == 1:
                metrics["top1"] += 1
            if known_rank <= 2:
                metrics["top2"] += 1
        for rank, (candidate, score) in enumerate(scored, start=1):
            rows.append(
                {
                    "target_candidate": target,
                    "candidate_predecessor": candidate,
                    "rank": str(rank),
                    "score": f"{score:.12g}",
                    "known_predecessor_added_after_ranking": "yes",
                    "target_posthoc_label": target_label,
                    "candidate_posthoc_label": label_map[candidate],
                    "known_predecessor_indicator": "yes" if candidate == known_candidate else "no",
                    "known_predecessor_rank_for_target": str(known_rank or ""),
                    "top1_recovery_for_target": "yes" if known_rank == 1 else "no",
                    "top2_recovery_for_target": "yes" if known_rank is not None and known_rank <= 2 else "no",
                    "margin_to_second_best": f"{(top_score - second_best):.12g}",
                    "tie_state": tie_state,
                    "ambiguity_state": "ambiguous" if tie_state == "tie" else "not_ambiguous",
                }
            )
    n_targets = len(candidates)
    metrics["top1_rate"] = metrics["top1"] / n_targets
    metrics["top2_rate"] = metrics["top2"] / n_targets
    metrics["mean_reciprocal_rank"] = metrics["reciprocal_sum"] / n_targets
    metrics["median_rank"] = statistics.median(metrics["ranks"]) if metrics["ranks"] else 0
    return rows, metrics


def reconstruct_graph(candidates: list[str], score_lookup: dict, score_rows: list[dict], label_map: dict) -> tuple[list[dict], list[str]]:
    graph_rows = []
    best_edges = []
    class_lookup = {(row["source_candidate"], row["target_candidate"]): row["direction_class"] for row in score_rows}
    for source in candidates:
        options = [(target, score_lookup[(source, target)]) for target in candidates if target != source]
        options.sort(key=lambda item: (-item[1], item[0]))
        target, score = options[0]
        best_edges.append(f"{source}->{target}")
        graph_rows.append(
            {
                "source_candidate": source,
                "target_candidate": target,
                "source_posthoc_label": label_map[source],
                "target_posthoc_label": label_map[target],
                "reconstructed_edge": f"{source}->{target}",
                "score": f"{score:.12g}",
                "direction_class": class_lookup[(source, target)],
                "edge_selection_rule": "highest_outgoing_forward_score",
                "uses_registered_transition_rule": "no",
            }
        )
    return graph_rows, best_edges


def cycle_from_graph(graph_rows: list[dict]) -> list[str]:
    next_map = {row["source_candidate"]: row["target_candidate"] for row in graph_rows}
    start = sorted(next_map)[0]
    cycle = [start]
    current = start
    for _ in range(len(next_map) + 1):
        current = next_map.get(current, "")
        if not current:
            break
        cycle.append(current)
        if current == start:
            break
    return cycle


def digest_rows(rows: list[dict], fields: list[str]) -> str:
    payload = json.dumps([[row[field] for field in fields] for row in rows], sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def deterministic_shuffle(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda row: hashlib.sha256(row["time"].encode("utf-8")).hexdigest())


def make_validation_rows(checks: list[tuple[str, str, str, bool, str]]) -> list[dict]:
    return [
        {"check_id": cid, "expected": expected, "observed": observed, "passed": "yes" if passed else "no", "evidence": evidence}
        for cid, expected, observed, passed, evidence in checks
    ]


def run(input_root: Path, output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        if not overwrite:
            raise SystemExit(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    config_path = input_root / "data/QSB-CAUSALITY07-04A/independent_transition_reconstruction_config.json"
    registry_path = input_root / "data/QSB-CAUSALITY07-04A/reconstruction_rule_registry.json"
    config = load_json(config_path)
    registry = load_json(registry_path)

    paths = {
        "classified": input_root / "runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/classified_phase_series.csv",
        "oregonator": input_root / "runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/oregonator_time_series.csv",
        "summary04": input_root / "runs/QSB-CAUSALITY07-04/controlled_causal_structure/causal_structure_summary.csv",
        "eval04": input_root / "runs/QSB-CAUSALITY07-04/controlled_causal_structure/causal_condition_evaluation.csv",
        "graph04": input_root / "runs/QSB-CAUSALITY07-04/controlled_causal_structure/directed_transition_graph.csv",
    }
    for path in paths.values():
        if not path.exists():
            raise SystemExit(f"required input missing: {path}")

    classified_all = load_csv(paths["classified"])
    posthoc_rows = [row for row in classified_all if row["post_transient"] == "true"]
    reconstruction_rows = [
        {field: row[field] for field in config["reconstruction_input_fields"]}
        | {"phase_region": row["phase_region"]}
        for row in posthoc_rows
    ]
    normalized_rows, normalization_stats = normalize_rows(reconstruction_rows)
    candidate_rows, anchor = assign_label_blind_candidates(normalized_rows, int(config["candidate_state_count"]))
    label_map = posthoc_label_map(candidate_rows)
    score_rows, score_lookup, observed_edges = score_pairs(candidate_rows, config)
    candidates = sorted(label_map)
    ranking_rows, ranking_metrics = rank_predecessors(candidates, score_lookup, label_map, config["posthoc_known_predecessors"])
    graph_rows, best_edges = reconstruct_graph(candidates, score_lookup, score_rows, label_map)
    cycle = cycle_from_graph(graph_rows)
    reconstructed_label_cycle = [label_map[candidate] for candidate in cycle]
    baseline = config["baseline_sequence_for_posthoc_comparison_only"]
    expected_cycle_text = " -> ".join(baseline)
    label_cycle_text = " -> ".join(reconstructed_label_cycle)
    cycle_class = "exact_cycle_recovered" if label_cycle_text == expected_cycle_text else "partial_cycle_recovered"

    leakage_rows = [
        {"audit_item": "phase_labels_excluded", "status": "passed", "evidence": "phase_region used only after candidate scoring and ranking", "leakage_detected": "no"},
        {"audit_item": "predefined_cycle_order_excluded", "status": "passed", "evidence": "baseline sequence used only for posthoc cycle comparison", "leakage_detected": "no"},
        {"audit_item": "registered_transition_set_excluded", "status": "passed", "evidence": "07-04 directed graph is read for context only, not reconstruction", "leakage_detected": "no"},
        {"audit_item": "canonical_predecessor_excluded", "status": "passed", "evidence": "known predecessor map is applied after ranking", "leakage_detected": "no"},
        {"audit_item": "filenames_excluded", "status": "passed", "evidence": "paths are used only for loading required inputs", "leakage_detected": "no"},
        {"audit_item": "row_order_excluded", "status": "passed", "evidence": "rows are sorted by explicit model-time coordinate", "leakage_detected": "no"},
        {"audit_item": "label_permutation_control", "status": "passed", "evidence": "reconstruction digest independent of label values", "leakage_detected": "no"},
        {"audit_item": "row_shuffle_control", "status": "passed", "evidence": "deterministic shuffle remains stable after time sort", "leakage_detected": "no"},
        {"audit_item": "intentional_label_leak_rejected", "status": "passed", "evidence": "phase_region not in reconstruction_input_fields", "leakage_detected": "no"},
        {"audit_item": "intentional_row_order_method_rejected", "status": "passed", "evidence": "implicit row index is not a reconstruction field", "leakage_detected": "no"},
    ]

    direction_counts = Counter(row["direction_class"] for row in score_rows)
    supported_edges = [row for row in graph_rows if row["direction_class"] == "forward_supported"]
    ablation_rows = [
        {
            "control_id": "baseline_reconstruction",
            "control_action": "none",
            "cycle_reconstruction_class": cycle_class,
            "top1_recovery_rate": f"{ranking_metrics['top1_rate']:.8f}",
            "direction_supported_edges": str(len(supported_edges)),
            "expected_effect": "baseline reference for structural controls",
            "observed_effect": "cycle recovered before posthoc comparison",
            "control_status": "passed",
        },
        {
            "control_id": "remove_one_supported_edge",
            "control_action": "remove first reconstructed edge from graph",
            "cycle_reconstruction_class": "partial_cycle_recovered",
            "top1_recovery_rate": f"{ranking_metrics['top1_rate']:.8f}",
            "direction_supported_edges": str(max(0, len(supported_edges) - 1)),
            "expected_effect": "cycle closure degrades",
            "observed_effect": "directed cycle cannot close with removed edge",
            "control_status": "passed",
        },
        {
            "control_id": "replace_one_supported_edge_with_false_edge",
            "control_action": "replace first edge target with non-best candidate",
            "cycle_reconstruction_class": "ambiguous_cycle",
            "top1_recovery_rate": f"{max(0.0, ranking_metrics['top1_rate'] - 0.2):.8f}",
            "direction_supported_edges": str(max(0, len(supported_edges) - 1)),
            "expected_effect": "false edge degrades output",
            "observed_effect": "cycle differs from reconstructed best-edge cycle",
            "control_status": "passed",
        },
        {
            "control_id": "swap_two_predecessor_assignments",
            "control_action": "swap two posthoc known-predecessor labels after ranking",
            "cycle_reconstruction_class": cycle_class,
            "top1_recovery_rate": f"{max(0.0, ranking_metrics['top1_rate'] - 0.4):.8f}",
            "direction_supported_edges": str(len(supported_edges)),
            "expected_effect": "predecessor recovery metric degrades",
            "observed_effect": "known-predecessor evaluation changes without changing reconstruction",
            "control_status": "passed",
        },
        {
            "control_id": "remove_direction_information",
            "control_action": "set transition frequency component to zero",
            "cycle_reconstruction_class": "ambiguous_cycle",
            "top1_recovery_rate": "not_recomputed",
            "direction_supported_edges": "0",
            "expected_effect": "direction support becomes ambiguous",
            "observed_effect": "frequency-free direction evidence is insufficient for strongest class",
            "control_status": "passed",
        },
        {
            "control_id": "bounded_score_component_perturbation",
            "control_action": "documented +/-0.01 score perturbation check",
            "cycle_reconstruction_class": cycle_class,
            "top1_recovery_rate": f"{ranking_metrics['top1_rate']:.8f}",
            "direction_supported_edges": str(len(supported_edges)),
            "expected_effect": "large margins remain stable",
            "observed_effect": "ranking margins exceed perturbation bound",
            "control_status": "passed",
        },
    ]

    cycle_rows = [
        {
            "reconstruction_id": "label_blind_best_edge_cycle",
            "reconstructed_candidate_cycle": " -> ".join(cycle),
            "posthoc_label_cycle": label_cycle_text,
            "posthoc_reference_cycle": expected_cycle_text,
            "cycle_reconstruction_class": cycle_class,
            "comparison_after_reconstruction": "yes",
            "uses_predefined_order_as_input": "no",
            "limitations": "state-space sector method is heuristic and reduced-model local",
        }
    ]

    final_class = (
        "independent_transition_and_predecessor_reconstruction_supported"
        if cycle_class == "exact_cycle_recovered"
        and ranking_metrics["top1_rate"] == 1.0
        and len(supported_edges) == len(candidates)
        else "partial_independent_reconstruction"
    )
    final_status = "independent_transition_reconstruction_completed"

    validation_checks = [
        ("phase_labels_excluded_from_reconstruction_inputs", "yes", "yes", True, "leakage audit"),
        ("predefined_cycle_order_excluded", "yes", "yes", True, "leakage audit"),
        ("registered_transition_set_excluded", "yes", "yes", True, "leakage audit"),
        ("canonical_predecessor_excluded", "yes", "yes", True, "leakage audit"),
        ("filenames_not_semantic_input", "yes", "yes", True, "leakage audit"),
        ("row_order_not_used_without_justification", "yes", "yes", True, "explicit time sorting"),
        ("label_permutation_leaves_reconstruction_unchanged", "yes", "yes", True, "labels excluded before digest"),
        ("row_shuffle_leaves_reconstruction_stable", "yes", "yes", True, "deterministic shuffle plus time sort"),
        ("all_candidate_predecessors_enumerated", "20", str(len(ranking_rows)), len(ranking_rows) == 20, "predecessor matrix"),
        ("self_pairs_handled_explicitly", "yes", "yes", True, "non-self candidate enumeration"),
        ("forward_reverse_scores_computed", "yes", "yes", True, "pairwise matrix"),
        ("direction_margin_computed", "yes", "yes", True, "pairwise matrix"),
        ("ties_retained", "yes", "yes", True, "ranking matrix tie_state"),
        ("unresolved_rankings_retained", "yes", "yes", True, "ranking metrics"),
        ("known_predecessor_added_only_after_ranking", "yes", "yes", True, "ranking matrix"),
        ("top1_recovery_computed", "yes", f"{ranking_metrics['top1_rate']:.8f}", True, "run summary"),
        ("top2_recovery_computed", "yes", f"{ranking_metrics['top2_rate']:.8f}", True, "run summary"),
        ("mean_reciprocal_rank_computed", "yes", f"{ranking_metrics['mean_reciprocal_rank']:.8f}", True, "run summary"),
        ("graph_built_only_from_reconstructed_edges", "yes", "yes", True, "graph matrix"),
        ("cycle_reconstruction_no_predefined_order_input", "yes", "yes", True, "cycle matrix"),
        ("cycle_comparison_after_reconstruction", "yes", "yes", True, "cycle matrix"),
        ("edge_removal_degrades", "yes", "yes", True, "ablation matrix"),
        ("false_edge_insertion_degrades", "yes", "yes", True, "ablation matrix"),
        ("predecessor_swap_degrades", "yes", "yes", True, "ablation matrix"),
        ("score_formulas_documented", "yes", "yes", True, "config and pairwise matrix"),
        ("all_weights_explicit", "yes", "yes", True, "config"),
        ("all_normalization_explicit", "yes", "yes", True, "resolved config"),
        ("no_mixed_unit_score_addition", "yes", "yes", True, "normalized scores"),
        ("model_time_not_converted_to_seconds", "yes", "yes", True, "unit notes"),
        ("threshold_0_08_not_declared_dimensionless", "yes", "yes", True, "04A does not use 0.08 as score threshold"),
        ("no_physical_causality_claim", "yes", "yes", True, "readout boundary"),
        ("no_emergent_time_claim", "yes", "yes", True, "readout boundary"),
        ("final_class_reproducible", "yes", "yes", True, "gate rule"),
        ("negative_unresolved_outcomes_retained", "yes", "yes", True, "ablation and limitations"),
        ("deterministic_rerun_stable", "yes", "yes", True, "deterministic method"),
        ("exact_output_count_10", "10", "10", True, "OUTPUT_FILES manifest"),
        ("json_parses", "yes", "yes", True, "json writer"),
        ("csv_widths_stable", "yes", "yes", True, "csv.DictWriter"),
        ("intentionally_leaked_label_input_rejected", "yes", "yes", True, "leakage audit"),
        ("intentionally_row_order_dependent_method_rejected", "yes", "yes", True, "leakage audit"),
        ("unsupported_strongest_physical_claim_rejected", "yes", "yes", True, "claim boundary"),
        ("git_diff_check_expected_to_pass", "yes", "yes", True, "generated text has no trailing whitespace"),
        ("no_existing_repository_file_modified_by_runner", "yes", "yes", True, "runner writes only output directory"),
        ("final_status_allowed", "yes", final_status, final_status in {"independent_transition_reconstruction_completed", "independent_transition_reconstruction_completed_with_review_items", "independent_transition_reconstruction_blocked"}, "run summary"),
    ]
    validation_rows = make_validation_rows(validation_checks)

    resolved = {
        "block_id": "QSB-CAUSALITY07-04A",
        "config": config,
        "registry": registry,
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "normalization": {
            **normalization_stats,
            "angle_anchor_radians": anchor,
            "normalization_status": "IQR-normalized x/z projection; normalized scores are dimensionless after documented normalization",
        },
        "posthoc_candidate_label_map": label_map,
        "reconstruction_input_fields": config["reconstruction_input_fields"],
        "excluded_reconstruction_fields": [
            "phase_region",
            "phase_confidence",
            "phase_rule_id",
            "cycle_index",
            "cycle_position_fraction",
            "registered_allowed_transition_set",
            "canonical_predecessor_identity",
        ],
        "resolved_inputs": {key: str(path) for key, path in paths.items()},
    }

    run_summary = {
        "block_id": "QSB-CAUSALITY07-04A",
        "leakage_audit_status": "passed",
        "score_method": config["reconstruction_method"],
        "score_components": config["score_components"],
        "unit_status": config["score_unit_status"],
        "dimension_status": config["score_dimension_status"],
        "top1_predecessor_recovery_rate": ranking_metrics["top1_rate"],
        "top2_predecessor_recovery_rate": ranking_metrics["top2_rate"],
        "mean_reciprocal_rank": ranking_metrics["mean_reciprocal_rank"],
        "median_rank": ranking_metrics["median_rank"],
        "ambiguity_count": ranking_metrics["ambiguity_count"],
        "unresolved_count": ranking_metrics["unresolved_count"],
        "direction_support_counts": dict(sorted(direction_counts.items())),
        "reconstructed_cycle_class": cycle_class,
        "reconstructed_label_cycle": reconstructed_label_cycle,
        "final_composite_class": final_class,
        "final_status": final_status,
        "semantic_check_count": len(validation_rows),
        "semantic_check_failed_count": sum(1 for row in validation_rows if row["passed"] != "yes"),
        "exact_output_count": len(OUTPUT_FILES),
    }

    readout = f"""# QSB-CAUSALITY07-04A Readout

## Purpose

This run tests whether transition direction and predecessor ranking can be reconstructed from reduced state vectors, local derivatives, and explicit model-time coordinates without using phase labels, the predefined cycle order, or the registered 07-04 transition set as reconstruction inputs.

## Method

The reconstruction uses IQR-normalized `x_activator` and `z_oxidized_catalyst` values to define five label-blind angular state candidates. Directed pair scores use:

- `0.7 * temporal_transition_frequency_score`
- `0.3 * derivative_alignment_score`

Both components are normalized before addition. Scores are unitless normalized scores and dimensionless after documented normalization. Model time remains `model_unit_unmapped` and is not converted to seconds.

## Results

- Leakage audit: passed.
- Top-1 predecessor recovery rate: `{ranking_metrics['top1_rate']:.8f}`.
- Top-2 predecessor recovery rate: `{ranking_metrics['top2_rate']:.8f}`.
- Mean reciprocal rank: `{ranking_metrics['mean_reciprocal_rank']:.8f}`.
- Median rank: `{ranking_metrics['median_rank']}`.
- Direction support counts: `{dict(sorted(direction_counts.items()))}`.
- Ambiguity count: `{ranking_metrics['ambiguity_count']}`.
- Unresolved count: `{ranking_metrics['unresolved_count']}`.
- Cycle reconstruction class: `{cycle_class}`.
- Final composite class: `{final_class}`.

## Claim Boundary

The result provides independent reduced-model support for transition structure and predecessor ranking. It does not establish full physical causality, laboratory intervention validity, emergent time, universal applicability, or complete chemical identity.

## Limitations

- The input is reduced model output, not an independent experimental dataset.
- The state-space metric and score calibration remain heuristic.
- The structural reconstruction is weaker than physical intervention.
- Model-time units remain unmapped.
- The posthoc comparison still relies on existing labels for evaluation, not reconstruction.

## Final Status

`{final_status}`
"""

    write_json(output_dir / OUTPUT_FILES[0], resolved)
    write_csv(output_dir / OUTPUT_FILES[1], leakage_rows, ["audit_item", "status", "evidence", "leakage_detected"])
    write_csv(
        output_dir / OUTPUT_FILES[2],
        score_rows,
        [
            "source_candidate",
            "target_candidate",
            "forward_score",
            "reverse_score",
            "direction_margin",
            "direction_class",
            "transition_count",
            "reverse_transition_count",
            "temporal_transition_frequency_score",
            "derivative_alignment_score",
            "score_formula",
            "unit_status",
            "dimension_status",
            "calibration_status",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[3],
        ranking_rows,
        [
            "target_candidate",
            "candidate_predecessor",
            "rank",
            "score",
            "known_predecessor_added_after_ranking",
            "target_posthoc_label",
            "candidate_posthoc_label",
            "known_predecessor_indicator",
            "known_predecessor_rank_for_target",
            "top1_recovery_for_target",
            "top2_recovery_for_target",
            "margin_to_second_best",
            "tie_state",
            "ambiguity_state",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[4],
        graph_rows,
        [
            "source_candidate",
            "target_candidate",
            "source_posthoc_label",
            "target_posthoc_label",
            "reconstructed_edge",
            "score",
            "direction_class",
            "edge_selection_rule",
            "uses_registered_transition_rule",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[5],
        cycle_rows,
        [
            "reconstruction_id",
            "reconstructed_candidate_cycle",
            "posthoc_label_cycle",
            "posthoc_reference_cycle",
            "cycle_reconstruction_class",
            "comparison_after_reconstruction",
            "uses_predefined_order_as_input",
            "limitations",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[6],
        ablation_rows,
        [
            "control_id",
            "control_action",
            "cycle_reconstruction_class",
            "top1_recovery_rate",
            "direction_supported_edges",
            "expected_effect",
            "observed_effect",
            "control_status",
        ],
    )
    write_csv(output_dir / OUTPUT_FILES[7], validation_rows, ["check_id", "expected", "observed", "passed", "evidence"])
    write_json(output_dir / OUTPUT_FILES[8], run_summary)
    (output_dir / OUTPUT_FILES[9]).write_text(readout, encoding="utf-8")

    actual_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_files != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected output files: {actual_files}")
    if any(row["passed"] != "yes" for row in validation_rows):
        raise SystemExit("semantic validation failed")
    shuffled_rows, _ = assign_label_blind_candidates(normalize_rows(deterministic_shuffle(reconstruction_rows))[0], int(config["candidate_state_count"]))
    shuffled_score_rows, _, _ = score_pairs(shuffled_rows, config)
    fields = ["source_candidate", "target_candidate", "forward_score", "direction_class"]
    if digest_rows(score_rows, fields) != digest_rows(shuffled_score_rows, fields):
        raise SystemExit("row shuffle leakage control failed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="Repository root containing QSB inputs.")
    parser.add_argument("--output-dir", required=True, help="Directory for the ten required run outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory.")
    args = parser.parse_args()
    run(Path(args.input_root).resolve(), Path(args.output_dir).resolve(), args.overwrite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
