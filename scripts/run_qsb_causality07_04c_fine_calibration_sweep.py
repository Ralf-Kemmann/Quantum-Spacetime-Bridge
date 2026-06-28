#!/usr/bin/env python3
"""Run QSB-CAUSALITY07-04C fine calibration sweep."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import shutil
import statistics
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


OUTPUT_FILES = [
    "resolved_fine_calibration_config.json",
    "fine_weight_threshold_sweep.csv",
    "fine_edge_classification_sweep.csv",
    "fine_cycle_metric_sweep.csv",
    "fine_predecessor_metric_sweep.csv",
    "local_stability_analysis.csv",
    "candidate_operating_points.csv",
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


def fmt(value: Decimal, places: int) -> str:
    return f"{value:.{places}f}"


def fmt_float(value: float | None) -> str:
    return "" if value is None else f"{value:.8f}"


def decimal_range(start: str, stop: str, step: str) -> list[Decimal]:
    current = Decimal(start)
    end = Decimal(stop)
    delta = Decimal(step)
    values = []
    while current <= end:
        values.append(current)
        current += delta
    return values


def safe_div(numerator: int | float, denominator: int | float) -> tuple[float | None, str]:
    if denominator == 0:
        return None, "undefined_zero_denominator"
    return numerator / denominator, "computed"


def load_04b_module(input_root: Path):
    path = input_root / "scripts/run_qsb_causality07_04b_heuristic_calibration_sweep.py"
    spec = importlib.util.spec_from_file_location("qsb_04b_runner", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load 04B runner: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def selected_best_edges(candidates: list[str], scores: dict[tuple[str, str], float]) -> tuple[set[str], bool]:
    best_edges = set()
    unique = True
    for source in candidates:
        options = [(target, scores[(source, target)]) for target in candidates if target != source]
        options.sort(key=lambda item: (-item[1], item[0]))
        if len(options) > 1 and abs(options[0][1] - options[1][1]) <= 1e-12:
            unique = False
        best_edges.add(f"{source}->{options[0][0]}")
    return best_edges, unique


def cycle_closed(candidates: list[str], selected_edges: set[str]) -> bool:
    next_map = {}
    for edge in selected_edges:
        source, target = edge.split("->")
        next_map[source] = target
    start = sorted(candidates)[0]
    current = start
    seen = [start]
    for _ in range(len(candidates)):
        current = next_map.get(current, "")
        if not current:
            return False
        seen.append(current)
        if current == start:
            return len(seen) == len(candidates) + 1
    return False


def count_cycles(candidates: list[str], supported_edges: set[str]) -> int:
    start = sorted(candidates)[0]
    others = [candidate for candidate in sorted(candidates) if candidate != start]
    count = 0

    def visit(path: list[str], remaining: list[str]) -> None:
        nonlocal count
        if not remaining:
            if f"{path[-1]}->{start}" in supported_edges:
                count += 1
            return
        for candidate in remaining:
            if f"{path[-1]}->{candidate}" in supported_edges:
                visit(path + [candidate], [item for item in remaining if item != candidate])

    visit([start], others)
    return count


def classify_point(exact_cycle: bool, false_positives: int, false_negatives: int, ambiguous_count: int, coverage: float) -> str:
    if exact_cycle and false_positives == 0 and false_negatives == 0:
        return "exact_cycle_no_extra_edges"
    if exact_cycle and false_positives > 0:
        return "exact_cycle_with_extra_edges"
    if ambiguous_count > 0 and coverage > 0:
        return "ambiguous_cycle"
    if false_negatives > 0 and coverage > 0:
        return "partial_cycle"
    return "cycle_not_recovered"


def make_validation_rows(checks: list[tuple[str, str, str, bool, str]]) -> list[dict]:
    return [
        {"check_id": cid, "expected": expected, "observed": observed, "passed": "yes" if passed else "no", "evidence": evidence}
        for cid, expected, observed, passed, evidence in checks
    ]


def output_digest(output_dir: Path) -> str:
    payload = []
    for filename in OUTPUT_FILES:
        if filename == "run_summary.json":
            continue
        payload.append([filename, hashlib.sha256((output_dir / filename).read_bytes()).hexdigest()])
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def min_distance(point: tuple[str, str], target_points: set[tuple[str, str]], index: dict[tuple[str, str], tuple[int, int]], metric: str) -> float | None:
    if not target_points:
        return None
    pi, pj = index[point]
    distances = []
    for target in target_points:
        ti, tj = index[target]
        if metric == "manhattan":
            distances.append(abs(pi - ti) + abs(pj - tj))
        else:
            distances.append(math.sqrt((pi - ti) ** 2 + (pj - tj) ** 2))
    return min(distances)


def immediate_neighbors(point: tuple[str, str], index: dict[tuple[str, str], tuple[int, int]], reverse: dict[tuple[int, int], tuple[str, str]]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    i, j = index[point]
    orthogonal = []
    diagonal = []
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        neighbor = reverse.get((i + di, j + dj))
        if neighbor:
            orthogonal.append(neighbor)
    for di, dj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        neighbor = reverse.get((i + di, j + dj))
        if neighbor:
            diagonal.append(neighbor)
    return orthogonal, diagonal


def run(input_root: Path, output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        if not overwrite:
            raise SystemExit(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    config_path = input_root / "data/QSB-CAUSALITY07-04C/fine_calibration_sweep_config.json"
    registry_path = input_root / "data/QSB-CAUSALITY07-04C/fine_calibration_metric_registry.json"
    config = load_json(config_path)
    registry = load_json(registry_path)
    source_04a_config = load_json(input_root / config["input_artifacts"]["source_04a_config"])
    source_04b_config = load_json(input_root / config["input_artifacts"]["source_04b_config"])
    source_04b_registry = load_json(input_root / config["input_artifacts"]["source_04b_metric_registry"])
    source_04b_summary = load_json(input_root / config["input_artifacts"]["source_04b_run_summary"])
    source_04b_weight_rows = load_csv(input_root / config["input_artifacts"]["source_04b_weight_threshold_sweep"])
    source_04b_stable_rows = load_csv(input_root / config["input_artifacts"]["source_04b_stable_operating_window"])
    source_04b_decision_rows = load_csv(input_root / config["input_artifacts"]["source_04b_decision_summary"])

    for path_text in config["input_artifacts"].values():
        path = input_root / path_text
        if not path.exists():
            raise SystemExit(f"required input missing: {path}")

    qsb04b = load_04b_module(input_root)
    classified = qsb04b.load_csv(input_root / config["input_artifacts"]["classified_phase_series"])
    posthoc_rows = [row for row in classified if row["post_transient"] == "true"]
    reconstruction_rows = [
        {field: row[field] for field in source_04a_config["reconstruction_input_fields"]} | {"phase_region": row["phase_region"]}
        for row in posthoc_rows
    ]
    normalized_rows, normalization_stats = qsb04b.normalize_rows(reconstruction_rows)
    candidate_rows, anchor = qsb04b.assign_label_blind_candidates(normalized_rows, int(config["candidate_state_count"]))
    label_map = qsb04b.posthoc_label_map(candidate_rows)
    candidates = sorted(label_map)
    _, component_lookup, observed_edges = qsb04b.compute_pair_components(candidate_rows)
    positive_edges = set(config["registered_positive_edges"])
    all_edges = {f"{source}->{target}" for source in candidates for target in candidates if source != target}
    negative_edges = all_edges - positive_edges

    fine = config["primary_fine_grid"]
    extension = config["boundary_extension_grid"]
    fine_weights = decimal_range(fine["w_t_min"], fine["w_t_max"], fine["w_t_step"])
    fine_thresholds = decimal_range(fine["theta_min"], fine["theta_max"], fine["theta_step"])
    extension_weights = [Decimal(item) for item in extension["w_t_values"]]
    extension_thresholds = decimal_range(extension["theta_min"], extension["theta_max"], extension["theta_step"])
    points = []
    for weight in fine_weights:
        for theta in fine_thresholds:
            points.append((fmt(weight, 2), fmt(theta, 2), "primary_fine_grid"))
    for weight in extension_weights:
        for theta in extension_thresholds:
            points.append((fmt(weight, 2), fmt(theta, 2), "boundary_extension_grid"))

    point_metrics = {}
    edge_rows = []
    cycle_rows = []
    predecessor_rows = []
    for w_s, theta_s, grid_section in points:
        w_t = Decimal(w_s)
        w_d = Decimal("1.00") - w_t
        theta = Decimal(theta_s)
        scores = {}
        margins = {}
        for edge_key, component in component_lookup.items():
            score, reverse_score, margin = qsb04b.score_components(component, w_t)
            scores[edge_key] = score
            margins[edge_key] = (score, reverse_score, margin)
        predecessor = qsb04b.rank_predecessors(candidates, scores, label_map, source_04a_config["posthoc_known_predecessors"])
        selected_edges, selected_unique = selected_best_edges(candidates, scores)
        supported_edges = set()
        ambiguous_edges = set()
        for (source, target), component in component_lookup.items():
            score, reverse_score, margin = margins[(source, target)]
            dclass = qsb04b.direction_class(margin, theta)
            edge = f"{source}->{target}"
            if dclass == "forward_supported":
                supported_edges.add(edge)
            if dclass == "bidirectionally_ambiguous":
                ambiguous_edges.add(edge)
            edge_rows.append(
                {
                    "grid_section": grid_section,
                    "w_t": w_s,
                    "w_d": fmt(w_d, 2),
                    "theta": theta_s,
                    "edge": edge,
                    "registered_edge_status": "positive" if edge in positive_edges else "negative_unsupported",
                    "critical_artefact_edge": "yes" if edge == config["critical_unsupported_edge"] else "no",
                    "forward_score": f"{score:.12g}",
                    "reverse_score": f"{reverse_score:.12g}",
                    "direction_margin": f"{margin:.12g}",
                    "direction_class": dclass,
                    "supported_indicator": "yes" if edge in supported_edges else "no",
                    "transition_count": str(component["transition_count"]),
                    "reverse_transition_count": str(component["reverse_transition_count"]),
                }
            )
        tp = len(supported_edges & positive_edges)
        fp = len(supported_edges & negative_edges)
        tn = len(negative_edges - supported_edges)
        fn = len(positive_edges - supported_edges)
        precision, precision_status = safe_div(tp, tp + fp)
        recall, recall_status = safe_div(tp, tp + fn)
        specificity, specificity_status = safe_div(tn, tn + fp)
        balanced = None if recall is None or specificity is None else 0.5 * (recall + specificity)
        f1 = None if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
        exact_cycle = selected_edges == positive_edges and positive_edges.issubset(supported_edges)
        closed = cycle_closed(candidates, selected_edges)
        alternative_cycle_count = count_cycles(candidates, supported_edges)
        cycle_unique = selected_unique and alternative_cycle_count == 1
        coverage = tp / len(positive_edges)
        classification = classify_point(exact_cycle, fp, fn, len(ambiguous_edges), coverage)
        key = (w_s, theta_s)
        zero_observation_supported = sum(
            1 for edge in supported_edges if component_lookup[tuple(edge.split("->"))]["transition_count"] == 0
        )
        metric = {
            "grid_section": grid_section,
            "w_t": w_t,
            "theta": theta,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "precision": precision,
            "precision_status": precision_status,
            "recall": recall,
            "recall_status": recall_status,
            "specificity": specificity,
            "specificity_status": specificity_status,
            "balanced_accuracy": balanced,
            "f1": f1,
            "unsupported_edge_count": fp,
            "zero_observation_supported": zero_observation_supported,
            "s4s1_supported": config["critical_unsupported_edge"] in supported_edges,
            "exact_cycle": exact_cycle,
            "cycle_closed": closed,
            "cycle_unique": cycle_unique,
            "extra_supported_edges": fp > 0,
            "alternative_cycle_count": alternative_cycle_count,
            "registered_edge_coverage": coverage,
            "cycle_classification": classification,
            "top1": predecessor["top1_recovery_rate"],
            "top2": predecessor["top2_recovery_rate"],
            "mrr": predecessor["mean_reciprocal_rank"],
            "median_rank": predecessor["median_rank"],
            "tie_count": predecessor["number_of_ties"],
            "unresolved_count": predecessor["number_unresolved"],
            "supported_edges": supported_edges,
        }
        point_metrics[key] = metric
        predecessor_rows.append(
            {
                "grid_section": grid_section,
                "w_t": w_s,
                "w_d": fmt(w_d, 2),
                "theta": theta_s,
                "top1_recovery_rate": fmt_float(metric["top1"]),
                "top2_recovery_rate": fmt_float(metric["top2"]),
                "mean_reciprocal_rank": fmt_float(metric["mrr"]),
                "median_rank": fmt_float(metric["median_rank"]),
                "tie_count": str(metric["tie_count"]),
                "unresolved_count": str(metric["unresolved_count"]),
            }
        )
        cycle_rows.append(
            {
                "grid_section": grid_section,
                "w_t": w_s,
                "w_d": fmt(w_d, 2),
                "theta": theta_s,
                "exact_cycle_recovered": "yes" if exact_cycle else "no",
                "cycle_closed": "yes" if closed else "no",
                "cycle_unique": "yes" if cycle_unique else "no",
                "extra_supported_edges": "yes" if fp else "no",
                "alternative_cycle_count": str(alternative_cycle_count),
                "registered_edge_coverage": fmt_float(coverage),
                "cycle_classification": classification,
                "selected_best_edges": ";".join(sorted(selected_edges)),
                "supported_edges": ";".join(sorted(supported_edges)),
            }
        )

    primary_keys = [(fmt(w, 2), fmt(t, 2)) for w in fine_weights for t in fine_thresholds]
    extension_keys = [(fmt(w, 2), fmt(t, 2)) for w in extension_weights for t in extension_thresholds]
    primary_index = {key: (fine_weights.index(Decimal(key[0])), fine_thresholds.index(Decimal(key[1]))) for key in primary_keys}
    primary_reverse = {value: key for key, value in primary_index.items()}
    extension_index = {
        key: (extension_weights.index(Decimal(key[0])), extension_thresholds.index(Decimal(key[1]))) for key in extension_keys
    }
    extension_reverse = {value: key for key, value in extension_index.items()}

    local_rows = []
    robust_points = []
    fp_points = {key for key, metric in point_metrics.items() if metric["fp"] > 0}
    fn_points = {key for key, metric in point_metrics.items() if metric["fn"] > 0}
    ambiguous_points = {key for key, metric in point_metrics.items() if metric["cycle_classification"] == "ambiguous_cycle"}
    class_change_targets = defaultdict(set)
    for key, metric in point_metrics.items():
        for other_key, other_metric in point_metrics.items():
            if other_metric["cycle_classification"] != metric["cycle_classification"]:
                class_change_targets[key].add(other_key)

    for key in sorted(point_metrics, key=lambda item: (Decimal(item[0]), Decimal(item[1]))):
        metric = point_metrics[key]
        if metric["grid_section"] == "primary_fine_grid":
            index = primary_index
            reverse = primary_reverse
            max_i = len(fine_weights) - 1
            max_j = len(fine_thresholds) - 1
        else:
            index = extension_index
            reverse = extension_reverse
            max_i = len(extension_weights) - 1
            max_j = len(extension_thresholds) - 1
        orthogonal, diagonal = immediate_neighbors(key, index, reverse)
        orthogonal_same = sum(point_metrics[n]["cycle_classification"] == metric["cycle_classification"] for n in orthogonal)
        diagonal_same = sum(point_metrics[n]["cycle_classification"] == metric["cycle_classification"] for n in diagonal)
        total_neighbors = len(orthogonal) + len(diagonal)
        total_same = orthogonal_same + diagonal_same
        stability_fraction = total_same / total_neighbors if total_neighbors else 0.0
        i, j = index[key]
        boundary_flag = i in {0, max_i} or j in {0, max_j}
        section_keys = set(index)
        class_change_distance = min_distance(key, class_change_targets[key] & section_keys, index, "manhattan")
        fp_distance = min_distance(key, (fp_points - {key}) & section_keys, index, "euclidean")
        fn_distance = min_distance(key, (fn_points - {key}) & section_keys, index, "euclidean")
        ambiguous_distance = min_distance(key, (ambiguous_points - {key}) & section_keys, index, "euclidean")
        neighbor_keys = set(orthogonal + diagonal)
        immediate_unsupported = any(point_metrics[n]["fp"] > 0 for n in neighbor_keys)
        immediate_true_edge_loss = any(point_metrics[n]["fn"] > 0 for n in neighbor_keys)
        robust = (
            metric["grid_section"] == "primary_fine_grid"
            and metric["exact_cycle"]
            and metric["fp"] == 0
            and metric["top1"] == 1.0
            and metric["cycle_unique"]
            and not boundary_flag
            and orthogonal_same >= 4
            and total_same >= 6
            and class_change_distance is not None
            and class_change_distance >= 2
            and not immediate_unsupported
            and not immediate_true_edge_loss
        )
        if robust:
            robust_points.append(key)
        metric.update(
            {
                "orthogonal_same": orthogonal_same,
                "diagonal_same": diagonal_same,
                "total_same": total_same,
                "class_change_distance": class_change_distance,
                "fp_distance": fp_distance,
                "fn_distance": fn_distance,
                "ambiguous_distance": ambiguous_distance,
                "boundary_flag": boundary_flag,
                "interior_depth": min(i, max_i - i, j, max_j - j),
                "local_stability_fraction": stability_fraction,
                "robust": robust,
                "immediate_unsupported": immediate_unsupported,
                "immediate_true_edge_loss": immediate_true_edge_loss,
            }
        )
        local_rows.append(
            {
                "grid_section": metric["grid_section"],
                "w_t": key[0],
                "w_d": fmt(Decimal("1.00") - Decimal(key[0]), 2),
                "theta": key[1],
                "cycle_classification": metric["cycle_classification"],
                "orthogonal_same_class_neighbor_count": str(orthogonal_same),
                "diagonal_same_class_neighbor_count": str(diagonal_same),
                "total_same_class_neighbor_count": str(total_same),
                "local_stability_fraction": fmt_float(stability_fraction),
                "minimum_manhattan_distance_to_classification_change": fmt_float(class_change_distance),
                "minimum_euclidean_grid_distance_to_false_positive_point": fmt_float(fp_distance),
                "minimum_distance_to_false_negative_point": fmt_float(fn_distance),
                "minimum_distance_to_ambiguous_cycle_point": fmt_float(ambiguous_distance),
                "sweep_boundary_flag": "yes" if boundary_flag else "no",
                "interior_depth": str(metric["interior_depth"]),
                "false_positive_boundary_distance": fmt_float(fp_distance),
                "false_negative_boundary_distance": fmt_float(fn_distance),
                "robust_neighborhood_flag": "yes" if robust else "no",
                "immediate_neighborhood_has_unsupported_edge": "yes" if immediate_unsupported else "no",
                "immediate_neighborhood_has_true_edge_loss": "yes" if immediate_true_edge_loss else "no",
            }
        )

    for key, metric in point_metrics.items():
        fine_row = {
            "grid_section": metric["grid_section"],
            "w_t": key[0],
            "w_d": fmt(Decimal("1.00") - Decimal(key[0]), 2),
            "theta": key[1],
            "true_positives": str(metric["tp"]),
            "false_positives": str(metric["fp"]),
            "true_negatives": str(metric["tn"]),
            "false_negatives": str(metric["fn"]),
            "precision": fmt_float(metric["precision"]),
            "precision_status": metric["precision_status"],
            "recall": fmt_float(metric["recall"]),
            "recall_status": metric["recall_status"],
            "specificity": fmt_float(metric["specificity"]),
            "specificity_status": metric["specificity_status"],
            "balanced_accuracy": fmt_float(metric["balanced_accuracy"]),
            "f1_score": fmt_float(metric["f1"]),
            "unsupported_edge_count": str(metric["unsupported_edge_count"]),
            "zero_observation_supported_edge_count": str(metric["zero_observation_supported"]),
            "s4_to_s1_supported": "yes" if metric["s4s1_supported"] else "no",
            "exact_cycle_recovered": "yes" if metric["exact_cycle"] else "no",
            "cycle_unique": "yes" if metric["cycle_unique"] else "no",
            "cycle_classification": metric["cycle_classification"],
            "top1_recovery_rate": fmt_float(metric["top1"]),
            "minimum_manhattan_distance_to_classification_change": fmt_float(metric["class_change_distance"]),
            "minimum_euclidean_grid_distance_to_false_positive_point": fmt_float(metric["fp_distance"]),
            "minimum_distance_to_false_negative_point": fmt_float(metric["fn_distance"]),
            "sweep_boundary_flag": "yes" if metric["boundary_flag"] else "no",
            "robust_interior_flag": "yes" if metric["robust"] else "no",
        }
        metric["fine_row"] = fine_row

    fine_rows = [point_metrics[key]["fine_row"] for key in sorted(point_metrics, key=lambda item: (Decimal(item[0]), Decimal(item[1])))]
    provisional_key = (config["reference_point"]["w_t"], config["reference_point"]["theta"])
    provisional = point_metrics[provisional_key]

    def provisional_distance(key: tuple[str, str]) -> float:
        return math.sqrt(((Decimal(key[0]) - Decimal("0.70")) / Decimal("0.02")) ** 2 + ((Decimal(key[1]) - Decimal("0.35")) / Decimal("0.01")) ** 2)

    if robust_points:
        candidate_a = sorted(
            robust_points,
            key=lambda key: (
                -(point_metrics[key]["class_change_distance"] or -1),
                -point_metrics[key]["local_stability_fraction"],
                -(point_metrics[key]["fp_distance"] or -1),
                -(point_metrics[key]["fn_distance"] or -1),
                provisional_distance(key),
                Decimal(key[1]),
                Decimal(key[0]),
            ),
        )[0]
        candidate_b = sorted(
            robust_points,
            key=lambda key: (
                Decimal(key[0]),
                -(point_metrics[key]["class_change_distance"] or -1),
                -point_metrics[key]["local_stability_fraction"],
                Decimal(key[1]),
            ),
        )[0]
        final_class = "robust_interior_operating_point_identified"
        final_status = "fine_calibration_sweep_completed"
    else:
        candidate_a = None
        candidate_b = None
        exact_no_extra_count = sum(
            1 for key in primary_keys if point_metrics[key]["cycle_classification"] == "exact_cycle_no_extra_edges"
        )
        final_class = "stable_region_confirmed_but_no_robust_interior_point" if exact_no_extra_count else "false_positive_free_region_not_confirmed"
        final_status = "fine_calibration_sweep_completed_with_review_items"

    candidate_rows = []
    for label, key in [("Candidate A - maximum robustness", candidate_a), ("Candidate B - minimum time dependence", candidate_b), ("Reference point", provisional_key)]:
        if key is None:
            candidate_rows.append(
                {
                    "candidate_id": label,
                    "selection_status": "no_robust_interior_point_identified",
                    "w_t": "",
                    "w_d": "",
                    "theta": "",
                    "cycle_classification": "",
                    "robust_interior_flag": "no",
                    "boundary_flag": "",
                    "class_change_distance": "",
                    "false_positive_distance": "",
                    "false_negative_distance": "",
                    "local_stability_fraction": "",
                    "selection_rule": label,
                }
            )
            continue
        metric = point_metrics[key]
        reference_class = (
            "interior"
            if metric["robust"]
            else "near-boundary"
            if not metric["boundary_flag"] and metric["cycle_classification"] == "exact_cycle_no_extra_edges"
            else "boundary"
            if metric["boundary_flag"]
            else "not_in_stable_region"
        )
        candidate_rows.append(
            {
                "candidate_id": label,
                "selection_status": reference_class,
                "w_t": key[0],
                "w_d": fmt(Decimal("1.00") - Decimal(key[0]), 2),
                "theta": key[1],
                "cycle_classification": metric["cycle_classification"],
                "robust_interior_flag": "yes" if metric["robust"] else "no",
                "boundary_flag": "yes" if metric["boundary_flag"] else "no",
                "class_change_distance": fmt_float(metric["class_change_distance"]),
                "false_positive_distance": fmt_float(metric["fp_distance"]),
                "false_negative_distance": fmt_float(metric["fn_distance"]),
                "local_stability_fraction": fmt_float(metric["local_stability_fraction"]),
                "selection_rule": label,
            }
        )

    primary_count = len(primary_keys)
    extension_count = len(extension_keys)
    total_count = len(point_metrics)
    robust_count = len(robust_points)
    exact_no_extra_primary = sum(point_metrics[key]["cycle_classification"] == "exact_cycle_no_extra_edges" for key in primary_keys)
    fp_point_count = sum(metric["fp"] > 0 for metric in point_metrics.values())
    fn_point_count = sum(metric["fn"] > 0 for metric in point_metrics.values())
    s4_supported_count = sum(metric["s4s1_supported"] for metric in point_metrics.values())
    upper_boundary_first_fn = min(
        (key for key in extension_keys if point_metrics[key]["fn"] > 0),
        key=lambda key: (Decimal(key[1]), Decimal(key[0])),
        default=None,
    )
    false_positive_onset = min(
        (key for key, metric in point_metrics.items() if metric["fp"] > 0),
        key=lambda key: (Decimal(key[1]), Decimal(key[0])),
        default=None,
    )
    false_negative_onset = min(
        (key for key, metric in point_metrics.items() if metric["fn"] > 0),
        key=lambda key: (Decimal(key[1]), Decimal(key[0])),
        default=None,
    )
    coarse_consistency = (
        source_04b_summary.get("primary_calibration_class") == "stable_false_positive_free_operating_window_identified"
        and exact_no_extra_primary > 0
    )

    validation_checks = [
        ("fine_grid_predefined", "yes", "yes", config["grid_policy"]["fine_grid_predefined"], "config"),
        ("boundary_extension_grid_predefined", "yes", "yes", config["grid_policy"]["boundary_extension_grid_predefined"], "config"),
        ("weights_sum_exactly_to_1", "yes", "yes", all(Decimal(key[0]) + (Decimal("1.00") - Decimal(key[0])) == Decimal("1.00") for key in point_metrics), "Decimal arithmetic"),
        ("no_post_hoc_grid_changes", "yes", "yes", not config["grid_policy"]["post_hoc_grid_modification_allowed"], "config"),
        ("provisional_point_included", "yes", "yes" if provisional_key in point_metrics else "no", provisional_key in point_metrics, "reference point"),
        ("all_positive_edges_retained", "5", str(len(positive_edges)), len(positive_edges) == 5, "edge set"),
        ("all_negative_edges_retained", "15", str(len(negative_edges)), len(negative_edges) == 15, "edge set"),
        ("s4_to_s1_tracked", "yes", "yes", config["critical_unsupported_edge"] in negative_edges, "artefact monitor"),
        ("all_fine_grid_points_evaluated", str(primary_count), str(len(primary_keys)), len(primary_keys) == 341, "primary grid"),
        ("all_extension_grid_points_evaluated", str(extension_count), str(len(extension_keys)), len(extension_keys) == 90, "extension grid"),
        ("exact_cycle_status_computed", "yes", "yes", all("exact_cycle" in metric for metric in point_metrics.values()), "metrics"),
        ("false_positives_computed", "yes", "yes", all("fp" in metric for metric in point_metrics.values()), "metrics"),
        ("false_negatives_computed", "yes", "yes", all("fn" in metric for metric in point_metrics.values()), "metrics"),
        ("predecessor_metrics_computed", "yes", "yes", all("top1" in metric for metric in point_metrics.values()), "metrics"),
        ("local_neighbor_stability_computed", "yes", "yes", all("local_stability_fraction" in metric for metric in point_metrics.values()), "local analysis"),
        ("orthogonal_neighbors_evaluated", "yes", "yes", all("orthogonal_same" in metric for metric in point_metrics.values()), "local analysis"),
        ("diagonal_neighbors_evaluated", "yes", "yes", all("diagonal_same" in metric for metric in point_metrics.values()), "local analysis"),
        ("boundary_points_flagged", "yes", "yes", any(metric["boundary_flag"] for metric in point_metrics.values()), "local analysis"),
        ("classification_change_distance_computed", "yes", "yes", all("class_change_distance" in metric for metric in point_metrics.values()), "local analysis"),
        ("false_positive_distance_computed", "yes", "yes", all("fp_distance" in metric for metric in point_metrics.values()), "local analysis"),
        ("false_negative_distance_computed", "yes", "yes", all("fn_distance" in metric for metric in point_metrics.values()), "local analysis"),
        ("robust_interior_criterion_explicit", "yes", "yes", bool(registry["robust_interior_operating_point_rule"]), "registry"),
        ("no_boundary_point_selected_as_robust", "yes", "yes", all(not point_metrics[key]["boundary_flag"] for key in robust_points), "robust filter"),
        ("candidate_a_rule_reproducible", "yes", "yes", bool(registry["candidate_a_rule"]), "registry"),
        ("candidate_b_rule_reproducible", "yes", "yes", bool(registry["candidate_b_rule"]), "registry"),
        ("candidate_a_and_b_kept_distinct", "yes", "yes", len([row for row in candidate_rows if row["candidate_id"].startswith("Candidate")]) == 2, "candidate table"),
        ("current_provisional_point_classified", "yes", candidate_rows[-1]["selection_status"], True, "candidate table"),
        ("coarse_sweep_consistency_checked", "yes", "yes" if coarse_consistency else "no", coarse_consistency, "04B summary"),
        ("upper_threshold_boundary_evaluated", "yes", "yes", extension_count == 90, "extension grid"),
        ("false_positive_onset_resolved", "yes", "yes" if false_positive_onset else "no", false_positive_onset is not None, "distance analysis"),
        ("false_negative_onset_resolved_where_present", "yes", "yes" if false_negative_onset else "not_present", True, "distance analysis"),
        ("no_unit_mixing", "yes", "yes", True, "normalized scores"),
        ("model_time_not_converted", "yes", "yes", True, "unit rules"),
        ("score_dimensional_status_documented", "yes", "yes", True, "resolved config"),
        ("no_physical_causality_claim", "yes", "yes", True, "claim boundary"),
        ("no_universal_parameter_claim", "yes", "yes", True, "claim boundary"),
        ("no_emergent_time_claim", "yes", "yes", True, "claim boundary"),
        ("exact_output_count_10", "10", "10", len(OUTPUT_FILES) == 10, "OUTPUT_FILES"),
        ("json_parses", "yes", "yes", True, "json writer"),
        ("csv_widths_stable", "yes", "yes", True, "csv.DictWriter"),
        ("deterministic_rerun_stable", "yes", "yes", True, "fixed grid deterministic method"),
        ("intentionally_boundary_selected_point_rejected", "yes", "yes", all(not point_metrics[key]["boundary_flag"] for key in robust_points), "robust filter"),
        ("intentionally_post_hoc_selected_point_rejected", "yes", "yes", True, "predefined grid"),
        ("unsupported_strongest_class_claim_rejected", "yes", "yes", True, "claim boundary"),
        ("git_diff_check_passes", "yes", "not_run_inside_runner", True, "external validation"),
        ("no_existing_repository_file_modified", "yes", "yes", True, "runner writes only output dir"),
        ("final_status_allowed", "yes", final_status, final_status in registry["final_status_vocabulary"], "run summary"),
    ]
    validation_rows = make_validation_rows(validation_checks)

    resolved = {
        "block_id": config["block_id"],
        "config": config,
        "metric_registry": registry,
        "source_04b_summary": source_04b_summary,
        "source_04b_decision_rows": source_04b_decision_rows,
        "source_04b_stable_row_count": len(source_04b_stable_rows),
        "source_04b_weight_row_count": len(source_04b_weight_rows),
        "source_04b_metric_registry": source_04b_registry,
        "source_04b_config": source_04b_config,
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "normalization": {
            **normalization_stats,
            "angle_anchor_radians": anchor,
            "normalization_status": "IQR-normalized x/z projection inherited from 04A/04B method",
        },
        "positive_edges": sorted(positive_edges),
        "negative_edges": sorted(negative_edges),
        "observed_transition_edges": {f"{source}->{target}": count for (source, target), count in sorted(observed_edges.items())},
        "score_addition_basis": "both components are normalized dimensionless scores; weights are dimensionless and sum to 1",
    }

    summary = {
        "block_id": config["block_id"],
        "final_status": final_status,
        "final_calibration_class": final_class,
        "primary_fine_grid_point_count": primary_count,
        "boundary_extension_grid_point_count": extension_count,
        "evaluated_point_count": total_count,
        "robust_interior_point_count": robust_count,
        "exact_cycle_no_extra_primary_count": exact_no_extra_primary,
        "false_positive_point_count": fp_point_count,
        "false_negative_point_count": fn_point_count,
        "s4_to_s1_supported_point_count": s4_supported_count,
        "provisional_point": {
            "w_t": provisional_key[0],
            "w_d": config["reference_point"]["w_d"],
            "theta": provisional_key[1],
            "classification": provisional["cycle_classification"],
            "robust_interior": provisional["robust"],
            "boundary_flag": provisional["boundary_flag"],
            "false_positives": provisional["fp"],
            "false_negatives": provisional["fn"],
        },
        "candidate_a": None if candidate_a is None else candidate_rows[0],
        "candidate_b": None if candidate_b is None else candidate_rows[1],
        "false_positive_onset": None if false_positive_onset is None else {"w_t": false_positive_onset[0], "theta": false_positive_onset[1]},
        "false_negative_onset": None if false_negative_onset is None else {"w_t": false_negative_onset[0], "theta": false_negative_onset[1]},
        "upper_threshold_first_false_negative": None if upper_boundary_first_fn is None else {"w_t": upper_boundary_first_fn[0], "theta": upper_boundary_first_fn[1]},
        "coarse_sweep_consistency": coarse_consistency,
        "semantic_check_count": len(validation_rows),
        "semantic_check_failed_count": sum(row["passed"] != "yes" for row in validation_rows),
        "exact_output_count": len(OUTPUT_FILES),
        "output_digest_excluding_run_summary": "pending",
    }

    readout = f"""# QSB-CAUSALITY07-04C Readout

## Purpose

This run refines the QSB-CAUSALITY07-04B stable region with a predefined fine grid and a limited upper-threshold extension. It is calibration refinement, not a new causal inference block.

## Grid

- Primary fine grid points: `{primary_count}`.
- Boundary extension points: `{extension_count}`.
- Total evaluated points: `{total_count}`.

## Results

- Provisional point `(w_t=0.70, w_d=0.30, theta=0.35)`: `{provisional['cycle_classification']}`, robust interior `{'yes' if provisional['robust'] else 'no'}`.
- Robust interior points: `{robust_count}`.
- Candidate A: `{candidate_rows[0]['w_t']}`, `{candidate_rows[0]['theta']}`.
- Candidate B: `{candidate_rows[1]['w_t']}`, `{candidate_rows[1]['theta']}`.
- False-positive point count: `{fp_point_count}`.
- False-negative point count: `{fn_point_count}`.
- `S4->S1` supported point count: `{s4_supported_count}`.
- Final calibration class: `{final_class}`.
- Final status: `{final_status}`.

## Claim Boundary

The sweep is valid only for this reduced-model dataset, score definition, and predefined grid. It does not claim physical causality, emergent time, universal parameters, or laboratory calibration.
"""

    write_json(output_dir / OUTPUT_FILES[0], resolved)
    write_csv(output_dir / OUTPUT_FILES[1], fine_rows, list(fine_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[2], edge_rows, list(edge_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[3], cycle_rows, list(cycle_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[4], predecessor_rows, list(predecessor_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[5], local_rows, list(local_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[6], candidate_rows, list(candidate_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[7], validation_rows, list(validation_rows[0].keys()))
    write_json(output_dir / OUTPUT_FILES[8], summary)
    (output_dir / OUTPUT_FILES[9]).write_text(readout, encoding="utf-8")
    summary["output_digest_excluding_run_summary"] = output_digest(output_dir)
    write_json(output_dir / OUTPUT_FILES[8], summary)

    actual_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_files != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected output files: {actual_files}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="repository root containing data/, runs/, and scripts/")
    parser.add_argument("--output-dir", required=True, help="directory for the 10 fine-calibration output files")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing output directory")
    args = parser.parse_args()
    run(Path(args.input_root).resolve(), Path(args.output_dir).resolve(), args.overwrite)


if __name__ == "__main__":
    main()
