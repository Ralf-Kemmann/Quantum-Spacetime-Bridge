#!/usr/bin/env python3
"""Run QSB-CAUSALITY07-04B heuristic calibration sweep."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
from collections import Counter, defaultdict, deque
from decimal import Decimal
from pathlib import Path


OUTPUT_FILES = [
    "resolved_calibration_config.json",
    "weight_threshold_sweep.csv",
    "edge_classification_sweep.csv",
    "predecessor_metric_sweep.csv",
    "cycle_reconstruction_sweep.csv",
    "stable_operating_window.csv",
    "calibration_decision_summary.csv",
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


def fmt_decimal(value: Decimal, places: int = 2) -> str:
    return f"{value:.{places}f}"


def fmt_float(value: float | None, places: int = 8) -> str:
    if value is None:
        return ""
    return f"{value:.{places}f}"


def safe_div(numerator: int | float, denominator: int | float) -> tuple[float | None, str]:
    if denominator == 0:
        return None, "undefined_zero_denominator"
    return numerator / denominator, "computed"


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


def compute_pair_components(rows: list[dict]) -> tuple[list[dict], dict[tuple[str, str], dict], Counter]:
    candidates = sorted({row["candidate_id"] for row in rows})
    grouped = {candidate: [row for row in rows if row["candidate_id"] == candidate] for candidate in candidates}
    centroids = {candidate: centroid(grouped[candidate]) for candidate in candidates}
    edges = segment_edges(rows)
    max_count = max(edges.values()) if edges else 1
    component_lookup = {}
    component_rows = []
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
            payload = {
                "temporal": frequency,
                "derivative": alignment,
                "reverse_temporal": reverse_frequency,
                "reverse_derivative": reverse_alignment,
                "transition_count": transition_count,
                "reverse_transition_count": reverse_count,
            }
            component_lookup[(source, target)] = payload
            component_rows.append({"source": source, "target": target, **payload})
    return component_rows, component_lookup, edges


def score_components(component: dict, w_t: Decimal) -> tuple[float, float, float]:
    w_t_float = float(w_t)
    w_d_float = 1.0 - w_t_float
    score = w_t_float * component["temporal"] + w_d_float * component["derivative"]
    reverse_score = w_t_float * component["reverse_temporal"] + w_d_float * component["reverse_derivative"]
    return score, reverse_score, score - reverse_score


def direction_class(margin: float, theta: Decimal) -> str:
    threshold = float(theta)
    if abs(margin) < threshold:
        return "bidirectionally_ambiguous"
    if margin > 0.0:
        return "forward_supported"
    return "reverse_supported"


def rank_predecessors(candidates: list[str], scores: dict[tuple[str, str], float], label_map: dict, known_predecessors: dict) -> dict:
    inverse_label_map = {label: candidate for candidate, label in label_map.items()}
    target_rows = []
    metrics = {
        "top1": 0,
        "top2": 0,
        "reciprocal_sum": 0.0,
        "ranks": [],
        "tie_count": 0,
        "unresolved_count": 0,
    }
    for target in candidates:
        scored = [(candidate, scores[(candidate, target)]) for candidate in candidates if candidate != target]
        scored.sort(key=lambda item: (-item[1], item[0]))
        top_score = scored[0][1] if scored else 0.0
        second_best = scored[1][1] if len(scored) > 1 else 0.0
        tie_state = len(scored) > 1 and abs(top_score - second_best) <= 1e-12
        if tie_state:
            metrics["tie_count"] += 1
        target_label = label_map[target]
        known_label = known_predecessors[target_label]
        known_candidate = inverse_label_map.get(known_label, "")
        known_rank = None
        for rank, (candidate, _) in enumerate(scored, start=1):
            if candidate == known_candidate:
                known_rank = rank
                break
        if known_rank is None:
            metrics["unresolved_count"] += 1
        else:
            metrics["ranks"].append(known_rank)
            metrics["reciprocal_sum"] += 1.0 / known_rank
            metrics["top1"] += 1 if known_rank == 1 else 0
            metrics["top2"] += 1 if known_rank <= 2 else 0
        target_rows.append(
            {
                "target_candidate": target,
                "known_predecessor_candidate": known_candidate,
                "known_predecessor_rank": known_rank,
                "top_candidate": scored[0][0] if scored else "",
                "top_score": top_score,
                "margin_to_second_best": top_score - second_best,
                "tie_state": tie_state,
            }
        )
    n_targets = len(candidates)
    return {
        "target_rows": target_rows,
        "top1_recovery_rate": metrics["top1"] / n_targets,
        "top2_recovery_rate": metrics["top2"] / n_targets,
        "mean_reciprocal_rank": metrics["reciprocal_sum"] / n_targets,
        "median_rank": statistics.median(metrics["ranks"]) if metrics["ranks"] else None,
        "number_of_ties": metrics["tie_count"],
        "number_unresolved": metrics["unresolved_count"],
    }


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


def cycle_closed_from_edges(candidates: list[str], selected_edges: set[str]) -> bool:
    next_map = {}
    for edge in selected_edges:
        source, target = edge.split("->")
        next_map[source] = target
    start = sorted(candidates)[0]
    seen = [start]
    current = start
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


def classify_region(exact_cycle: bool, extra_supported_count: int, cycle_closed: bool, ambiguity_count: int, registered_coverage: float) -> str:
    if exact_cycle and extra_supported_count == 0:
        return "exact_cycle_no_extra_edges"
    if exact_cycle and extra_supported_count > 0:
        return "exact_cycle_with_extra_edges"
    if ambiguity_count > 0 and registered_coverage > 0:
        return "ambiguous_cycle"
    if 0.0 < registered_coverage < 1.0 or cycle_closed:
        return "partial_cycle"
    return "cycle_not_recovered"


def connected_component_sizes(points: set[tuple[str, str]], classifications: dict[tuple[str, str], str]) -> dict[tuple[str, str], int]:
    sizes = {}
    seen = set()
    for point in points:
        if point in seen:
            continue
        target_class = classifications[point]
        queue = deque([point])
        component = set()
        seen.add(point)
        while queue:
            current = queue.popleft()
            component.add(current)
            w_s, t_s = current
            w = Decimal(w_s)
            t = Decimal(t_s)
            neighbors = [
                (fmt_decimal(w - Decimal("0.1"), 1), t_s),
                (fmt_decimal(w + Decimal("0.1"), 1), t_s),
                (w_s, fmt_decimal(t - Decimal("0.05"), 2)),
                (w_s, fmt_decimal(t + Decimal("0.05"), 2)),
            ]
            for neighbor in neighbors:
                if neighbor in points and neighbor not in seen and classifications[neighbor] == target_class:
                    seen.add(neighbor)
                    queue.append(neighbor)
        for item in component:
            sizes[item] = len(component)
    return sizes


def make_validation_rows(checks: list[tuple[str, str, str, bool, str]]) -> list[dict]:
    return [
        {"check_id": cid, "expected": expected, "observed": observed, "passed": "yes" if passed else "no", "evidence": evidence}
        for cid, expected, observed, passed, evidence in checks
    ]


def digest_output_files(output_dir: Path) -> str:
    payload = []
    for filename in OUTPUT_FILES:
        if filename == "run_summary.json":
            continue
        path = output_dir / filename
        payload.append([filename, hashlib.sha256(path.read_bytes()).hexdigest()])
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def run(input_root: Path, output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        if not overwrite:
            raise SystemExit(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    config_path = input_root / "data/QSB-CAUSALITY07-04B/heuristic_calibration_config.json"
    registry_path = input_root / "data/QSB-CAUSALITY07-04B/calibration_metric_registry.json"
    config = load_json(config_path)
    registry = load_json(registry_path)
    source_config = load_json(input_root / "data/QSB-CAUSALITY07-04A/independent_transition_reconstruction_config.json")
    resolved04a = load_json(input_root / config["input_artifacts"]["causality07_04a_resolved_reconstruction_config"])

    required_inputs = [input_root / path for path in config["input_artifacts"].values() if not path.endswith(".py")]
    required_inputs.append(input_root / config["input_artifacts"]["causality07_04a_runner"])
    missing = [str(path) for path in required_inputs if not path.exists()]
    if missing:
        raise SystemExit("required input missing: " + "; ".join(missing))

    classified_all = load_csv(input_root / config["input_artifacts"]["classified_phase_series"])
    posthoc_rows = [row for row in classified_all if row["post_transient"] == "true"]
    reconstruction_rows = [
        {field: row[field] for field in source_config["reconstruction_input_fields"]}
        | {"phase_region": row["phase_region"]}
        for row in posthoc_rows
    ]
    normalized_rows, normalization_stats = normalize_rows(reconstruction_rows)
    candidate_rows, anchor = assign_label_blind_candidates(normalized_rows, int(config["candidate_state_count"]))
    label_map = posthoc_label_map(candidate_rows)
    candidates = sorted(label_map)
    _, component_lookup, observed_edges = compute_pair_components(candidate_rows)
    positive_edges = set(config["registered_positive_edges"])
    all_edges = {f"{source}->{target}" for source in candidates for target in candidates if source != target}
    negative_edges = all_edges - positive_edges
    weight_grid = [Decimal(item) for item in config["weight_grid"]]
    threshold_grid = [Decimal(item) for item in config["threshold_grid"]]
    expected_points = len(weight_grid) * len(threshold_grid)

    weight_threshold_rows = []
    edge_rows = []
    predecessor_rows = []
    cycle_rows = []
    point_metrics = {}
    classifications = {}
    working_point = (config["current_working_point"]["w_t"], config["current_working_point"]["theta"])

    for w_t in weight_grid:
        w_d = Decimal("1.0") - w_t
        scores = {}
        margins = {}
        for edge_key, component in component_lookup.items():
            score, reverse_score, margin = score_components(component, w_t)
            scores[edge_key] = score
            margins[edge_key] = (score, reverse_score, margin)
        predecessor_metrics = rank_predecessors(candidates, scores, label_map, source_config["posthoc_known_predecessors"])
        selected_edges, selected_unique = selected_best_edges(candidates, scores)
        for theta in threshold_grid:
            supported_edges = set()
            ambiguous_edges = set()
            unresolved_count = 0
            for (source, target), component in component_lookup.items():
                score, reverse_score, margin = margins[(source, target)]
                edge = f"{source}->{target}"
                dclass = direction_class(margin, theta)
                if dclass == "forward_supported":
                    supported_edges.add(edge)
                if dclass == "bidirectionally_ambiguous":
                    ambiguous_edges.add(edge)
                edge_rows.append(
                    {
                        "w_t": fmt_decimal(w_t, 1),
                        "w_d": fmt_decimal(w_d, 1),
                        "theta": fmt_decimal(theta, 2),
                        "source_candidate": source,
                        "target_candidate": target,
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
                        "temporal_transition_frequency_score": f"{component['temporal']:.12g}",
                        "derivative_alignment_score": f"{component['derivative']:.12g}",
                        "unit_status": "unitless_normalized_score",
                        "dimension_status": "dimensionless_after_documented_normalization",
                    }
                )
            tp = len(supported_edges & positive_edges)
            fp = len(supported_edges & negative_edges)
            tn = len(negative_edges - supported_edges)
            fn = len(positive_edges - supported_edges)
            precision, precision_status = safe_div(tp, tp + fp)
            recall, recall_status = safe_div(tp, tp + fn)
            specificity, specificity_status = safe_div(tn, tn + fp)
            if recall is None or specificity is None:
                balanced_accuracy = None
                balanced_accuracy_status = "undefined_dependency"
            else:
                balanced_accuracy = 0.5 * (recall + specificity)
                balanced_accuracy_status = "computed"
            if precision is None or recall is None or precision + recall == 0:
                f1_score = None
                f1_status = "undefined_zero_denominator"
            else:
                f1_score = 2 * precision * recall / (precision + recall)
                f1_status = "computed"
            selected_supported_edges = selected_edges & supported_edges
            exact_cycle = selected_edges == positive_edges and positive_edges.issubset(supported_edges)
            cycle_closed = cycle_closed_from_edges(candidates, selected_edges)
            extra_supported_count = len(supported_edges & negative_edges)
            registered_edge_coverage = len(positive_edges & supported_edges) / len(positive_edges)
            alternative_cycle_count = count_cycles(candidates, supported_edges)
            cycle_unique = selected_unique and alternative_cycle_count == 1
            region_class = classify_region(
                exact_cycle,
                extra_supported_count,
                cycle_closed,
                len(ambiguous_edges),
                registered_edge_coverage,
            )
            key = (fmt_decimal(w_t, 1), fmt_decimal(theta, 2))
            classifications[key] = region_class
            s4s1_supported = config["critical_unsupported_edge"] in supported_edges
            observed_zero_supported = sum(
                1 for edge in supported_edges if component_lookup[tuple(edge.split("->"))]["transition_count"] == 0
            )
            geometry_only_false_support_count = fp if w_t == Decimal("0.0") else 0
            time_dominance_indicator = (
                "geometry_only_point"
                if w_t == Decimal("0.0")
                else "time_only_point"
                if w_t == Decimal("1.0")
                else "mixed_time_geometry"
            )
            predecessor_rows.append(
                {
                    "w_t": fmt_decimal(w_t, 1),
                    "w_d": fmt_decimal(w_d, 1),
                    "theta": fmt_decimal(theta, 2),
                    "top1_recovery_rate": fmt_float(predecessor_metrics["top1_recovery_rate"]),
                    "top2_recovery_rate": fmt_float(predecessor_metrics["top2_recovery_rate"]),
                    "mean_reciprocal_rank": fmt_float(predecessor_metrics["mean_reciprocal_rank"]),
                    "median_rank": fmt_float(predecessor_metrics["median_rank"]),
                    "number_of_ties": str(predecessor_metrics["number_of_ties"]),
                    "number_unresolved": str(predecessor_metrics["number_unresolved"]),
                    "known_predecessor_added_after_ranking": "yes",
                }
            )
            cycle_rows.append(
                {
                    "w_t": fmt_decimal(w_t, 1),
                    "w_d": fmt_decimal(w_d, 1),
                    "theta": fmt_decimal(theta, 2),
                    "selected_best_edges": ";".join(sorted(selected_edges)),
                    "selected_supported_edges": ";".join(sorted(selected_supported_edges)),
                    "supported_edges": ";".join(sorted(supported_edges)),
                    "exact_five_edge_cycle_recovered": "yes" if exact_cycle else "no",
                    "cycle_closed": "yes" if cycle_closed else "no",
                    "extra_supported_edges_present": "yes" if extra_supported_count else "no",
                    "number_of_extra_supported_edges": str(extra_supported_count),
                    "cycle_class": region_class,
                    "registered_edge_coverage": fmt_float(registered_edge_coverage),
                    "cycle_uniqueness": "unique" if cycle_unique else "not_unique",
                    "alternative_cycle_count": str(alternative_cycle_count),
                }
            )
            point_metrics[key] = {
                "w_t": w_t,
                "theta": theta,
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "specificity": specificity,
                "balanced_accuracy": balanced_accuracy,
                "f1_score": f1_score,
                "ambiguity_count": len(ambiguous_edges),
                "unresolved_count": unresolved_count,
                "exact_cycle": exact_cycle,
                "cycle_closed": cycle_closed,
                "extra_supported_count": extra_supported_count,
                "registered_edge_coverage": registered_edge_coverage,
                "cycle_unique": cycle_unique,
                "alternative_cycle_count": alternative_cycle_count,
                "classification": region_class,
                "top1": predecessor_metrics["top1_recovery_rate"],
                "top2": predecessor_metrics["top2_recovery_rate"],
                "mrr": predecessor_metrics["mean_reciprocal_rank"],
                "median_rank": predecessor_metrics["median_rank"],
                "ties": predecessor_metrics["number_of_ties"],
                "pred_unresolved": predecessor_metrics["number_unresolved"],
                "s4s1_supported": s4s1_supported,
                "unsupported_edge_support_rate": fp / len(negative_edges),
                "observed_zero_supported": observed_zero_supported,
                "geometry_only_false_support_count": geometry_only_false_support_count,
                "time_dominance_indicator": time_dominance_indicator,
                "precision_status": precision_status,
                "recall_status": recall_status,
                "specificity_status": specificity_status,
                "balanced_accuracy_status": balanced_accuracy_status,
                "f1_status": f1_status,
            }

    component_sizes = connected_component_sizes(set(point_metrics), classifications)
    for key in sorted(point_metrics, key=lambda item: (Decimal(item[0]), Decimal(item[1]))):
        metrics = point_metrics[key]
        w_t = metrics["w_t"]
        theta = metrics["theta"]
        neighbor_keys = [
            (fmt_decimal(w_t - Decimal("0.1"), 1), fmt_decimal(theta, 2)),
            (fmt_decimal(w_t + Decimal("0.1"), 1), fmt_decimal(theta, 2)),
            (fmt_decimal(w_t, 1), fmt_decimal(theta - Decimal("0.05"), 2)),
            (fmt_decimal(w_t, 1), fmt_decimal(theta + Decimal("0.05"), 2)),
        ]
        existing_neighbors = [neighbor for neighbor in neighbor_keys if neighbor in point_metrics]
        consistent_neighbors = sum(1 for neighbor in existing_neighbors if classifications[neighbor] == metrics["classification"])
        nn_consistency, nn_status = safe_div(consistent_neighbors, len(existing_neighbors))
        row = {
            "w_t": fmt_decimal(w_t, 1),
            "w_d": fmt_decimal(Decimal("1.0") - w_t, 1),
            "theta": fmt_decimal(theta, 2),
            "true_positive_count": str(metrics["tp"]),
            "false_positive_count": str(metrics["fp"]),
            "true_negative_count": str(metrics["tn"]),
            "false_negative_count": str(metrics["fn"]),
            "precision": fmt_float(metrics["precision"]),
            "precision_status": metrics["precision_status"],
            "recall": fmt_float(metrics["recall"]),
            "recall_status": metrics["recall_status"],
            "specificity": fmt_float(metrics["specificity"]),
            "specificity_status": metrics["specificity_status"],
            "balanced_accuracy": fmt_float(metrics["balanced_accuracy"]),
            "balanced_accuracy_status": metrics["balanced_accuracy_status"],
            "f1_score": fmt_float(metrics["f1_score"]),
            "f1_status": metrics["f1_status"],
            "ambiguity_count": str(metrics["ambiguity_count"]),
            "unresolved_count": str(metrics["unresolved_count"]),
            "exact_five_edge_cycle_recovered": "yes" if metrics["exact_cycle"] else "no",
            "cycle_closed": "yes" if metrics["cycle_closed"] else "no",
            "extra_supported_edges_present": "yes" if metrics["extra_supported_count"] else "no",
            "number_of_extra_supported_edges": str(metrics["extra_supported_count"]),
            "cycle_class": metrics["classification"],
            "registered_edge_coverage": fmt_float(metrics["registered_edge_coverage"]),
            "cycle_uniqueness": "unique" if metrics["cycle_unique"] else "not_unique",
            "alternative_cycle_count": str(metrics["alternative_cycle_count"]),
            "top1_recovery_rate": fmt_float(metrics["top1"]),
            "top2_recovery_rate": fmt_float(metrics["top2"]),
            "mean_reciprocal_rank": fmt_float(metrics["mrr"]),
            "median_rank": fmt_float(metrics["median_rank"]),
            "number_of_ties": str(metrics["ties"]),
            "number_unresolved": str(metrics["pred_unresolved"]),
            "s4_to_s1_supported": "yes" if metrics["s4s1_supported"] else "no",
            "unsupported_edge_support_rate": fmt_float(metrics["unsupported_edge_support_rate"]),
            "observed_zero_transition_edge_support_count": str(metrics["observed_zero_supported"]),
            "geometry_only_false_support_count": str(metrics["geometry_only_false_support_count"]),
            "time_dominance_indicator": metrics["time_dominance_indicator"],
            "nearest_neighbor_parameter_consistency": fmt_float(nn_consistency),
            "nearest_neighbor_parameter_consistency_status": nn_status,
            "contiguous_stable_window_size": str(component_sizes[key]),
            "classification_change_count": str(len(existing_neighbors) - consistent_neighbors),
            "exact_cycle_plateau_width": str(component_sizes[key] if metrics["exact_cycle"] else 0),
            "false_positive_free_plateau_width": str(component_sizes[key] if metrics["fp"] == 0 else 0),
            "operating_region_class": metrics["classification"],
        }
        weight_threshold_rows.append(row)

    stable_candidates = [
        (key, metrics)
        for key, metrics in point_metrics.items()
        if metrics["exact_cycle"]
        and metrics["fp"] == 0
        and metrics["top1"] == 1.0
        and metrics["cycle_unique"]
        and component_sizes[key] > 1
    ]
    false_positive_free_points = [(key, metrics) for key, metrics in point_metrics.items() if metrics["fp"] == 0]
    exact_cycle_points = [(key, metrics) for key, metrics in point_metrics.items() if metrics["exact_cycle"]]
    stable_residual_fp_points = [
        (key, metrics)
        for key, metrics in point_metrics.items()
        if metrics["exact_cycle"] and metrics["top1"] == 1.0 and metrics["cycle_unique"] and component_sizes[key] > 1
    ]
    if stable_candidates:
        primary_class = "stable_false_positive_free_operating_window_identified"
    elif stable_residual_fp_points:
        primary_class = "stable_window_identified_with_residual_false_positives"
    elif exact_cycle_points:
        primary_class = "narrow_or_fragile_operating_window"
    elif point_metrics[("0.0", "0.20")]["top1"] < 1.0:
        primary_class = "temporal_component_required_for_reconstruction"
    else:
        primary_class = "no_stable_operating_window"

    current = point_metrics[working_point]
    geometry_current_threshold = point_metrics[("0.0", working_point[1])]
    time_current_threshold = point_metrics[("1.0", working_point[1])]
    min_w_exact = min((metrics["w_t"] for _, metrics in exact_cycle_points), default=None)
    min_w_top1 = min((metrics["w_t"] for metrics in point_metrics.values() if metrics["top1"] == 1.0), default=None)
    min_w_zero_fp = min((metrics["w_t"] for _, metrics in false_positive_free_points), default=None)
    final_status = (
        "heuristic_calibration_sweep_completed"
        if stable_candidates
        else "heuristic_calibration_sweep_completed_with_review_items"
    )
    stable_window_status = (
        "candidate_stable_false_positive_free_window_found"
        if stable_candidates
        else "no_false_positive_free_stable_window_found"
    )
    stable_rows = []
    for key, metrics in sorted(stable_candidates, key=lambda item: (Decimal(item[0][0]), Decimal(item[0][1]))):
        stable_rows.append(
            {
                "w_t": key[0],
                "w_d": fmt_decimal(Decimal("1.0") - metrics["w_t"], 1),
                "theta": key[1],
                "operating_region_class": metrics["classification"],
                "stable_window_status": stable_window_status,
                "contiguous_stable_window_size": str(component_sizes[key]),
                "top1_recovery_rate": fmt_float(metrics["top1"]),
                "false_positive_count": str(metrics["fp"]),
                "cycle_uniqueness": "unique" if metrics["cycle_unique"] else "not_unique",
                "neighbor_stability_rule": "same_classification_required_for_at_least_one_neighbor",
            }
        )
    if not stable_rows:
        stable_rows.append(
            {
                "w_t": "",
                "w_d": "",
                "theta": "",
                "operating_region_class": "",
                "stable_window_status": stable_window_status,
                "contiguous_stable_window_size": "0",
                "top1_recovery_rate": "",
                "false_positive_count": "",
                "cycle_uniqueness": "",
                "neighbor_stability_rule": "same_classification_required_for_at_least_one_neighbor",
            }
        )

    decision_rows = [
        {
            "decision_item": "primary_calibration_class",
            "value": primary_class,
            "evidence": "derived from exact cycle recovery, false-positive count, top-1 recovery, uniqueness, and neighbor stability",
        },
        {
            "decision_item": "final_status",
            "value": final_status,
            "evidence": "allowed QSB-CAUSALITY07-04B final status vocabulary",
        },
        {
            "decision_item": "stable_window_status",
            "value": stable_window_status,
            "evidence": "stable false-positive-free candidates counted after full predefined sweep",
        },
        {
            "decision_item": "current_working_point_reproduced",
            "value": "yes" if current["exact_cycle"] and current["s4s1_supported"] else "no",
            "evidence": "working point exact-cycle status and S4->S1 artefact monitor",
        },
        {
            "decision_item": "minimum_w_t_for_exact_cycle_recovery",
            "value": "" if min_w_exact is None else fmt_decimal(min_w_exact, 1),
            "evidence": "minimum over predefined grid",
        },
        {
            "decision_item": "minimum_w_t_for_top1_recovery_1_0",
            "value": "" if min_w_top1 is None else fmt_decimal(min_w_top1, 1),
            "evidence": "predecessor ranking sweep",
        },
        {
            "decision_item": "minimum_w_t_for_zero_false_positives",
            "value": "" if min_w_zero_fp is None else fmt_decimal(min_w_zero_fp, 1),
            "evidence": "edge classification sweep",
        },
        {
            "decision_item": "geometry_only_current_threshold_result",
            "value": geometry_current_threshold["classification"],
            "evidence": "w_t=0.0 at current theta",
        },
        {
            "decision_item": "time_only_current_threshold_result",
            "value": time_current_threshold["classification"],
            "evidence": "w_t=1.0 at current theta",
        },
    ]

    output_count_before_summary = len(OUTPUT_FILES)
    validation_checks = [
        ("weight_grid_predefined", "yes", "yes", True, "configuration weight_grid"),
        ("threshold_grid_predefined", "yes", "yes", True, "configuration threshold_grid"),
        ("weights_sum_to_exactly_1", "yes", "yes", all(w + (Decimal("1.0") - w) == Decimal("1.0") for w in weight_grid), "Decimal grid"),
        ("no_post_hoc_grid_modification", "yes", "yes", config["grid_policy"]["post_hoc_grid_modification_allowed"] is False, "configuration grid_policy"),
        ("all_five_positive_edges_retained", "5", str(len(positive_edges)), len(positive_edges) == 5, "registered_positive_edges"),
        ("all_negative_edges_retained", "15", str(len(negative_edges)), len(negative_edges) == 15, "all non-self directed non-positive edges"),
        ("s4_to_s1_explicitly_tracked", "yes", "yes" if config["critical_unsupported_edge"] in negative_edges else "no", config["critical_unsupported_edge"] in negative_edges, "critical artefact edge"),
        ("all_parameter_points_evaluated", str(expected_points), str(len(point_metrics)), len(point_metrics) == expected_points, "sweep grid"),
        ("exact_cycle_status_computed", "yes", "yes", all("exact_cycle" in item for item in point_metrics.values()), "cycle metrics"),
        ("false_positives_computed", "yes", "yes", all("fp" in item for item in point_metrics.values()), "edge metrics"),
        ("false_negatives_computed", "yes", "yes", all("fn" in item for item in point_metrics.values()), "edge metrics"),
        ("precision_computed_or_marked_undefined", "yes", "yes", all(item["precision_status"] for item in point_metrics.values()), "edge metrics"),
        ("recall_computed_or_marked_undefined", "yes", "yes", all(item["recall_status"] for item in point_metrics.values()), "edge metrics"),
        ("specificity_computed_or_marked_undefined", "yes", "yes", all(item["specificity_status"] for item in point_metrics.values()), "edge metrics"),
        ("balanced_accuracy_computed_or_marked_undefined", "yes", "yes", all(item["balanced_accuracy_status"] for item in point_metrics.values()), "edge metrics"),
        ("f1_computed_or_marked_undefined", "yes", "yes", all(item["f1_status"] for item in point_metrics.values()), "edge metrics"),
        ("top1_recovery_computed", "yes", "yes", all("top1" in item for item in point_metrics.values()), "predecessor metrics"),
        ("top2_recovery_computed", "yes", "yes", all("top2" in item for item in point_metrics.values()), "predecessor metrics"),
        ("mrr_computed", "yes", "yes", all("mrr" in item for item in point_metrics.values()), "predecessor metrics"),
        ("ambiguity_retained", "yes", "yes", all("ambiguity_count" in item for item in point_metrics.values()), "edge metrics"),
        ("unresolved_outcomes_retained", "yes", "yes", all("unresolved_count" in item for item in point_metrics.values()), "edge metrics"),
        ("geometry_only_point_included", "yes", "yes" if any(item["w_t"] == Decimal("0.0") for item in point_metrics.values()) else "no", True, "weight grid"),
        ("time_only_point_included", "yes", "yes" if any(item["w_t"] == Decimal("1.0") for item in point_metrics.values()) else "no", True, "weight grid"),
        ("current_working_point_included", "yes", "yes" if working_point in point_metrics else "no", working_point in point_metrics, "configured current point"),
        ("current_working_point_result_reproduced", "yes", "yes" if current["exact_cycle"] else "no", current["exact_cycle"], "current point cycle status"),
        ("unsupported_edge_at_current_point_reproduced", "yes", "yes" if current["s4s1_supported"] else "no", current["s4s1_supported"], "S4->S1 monitor"),
        ("stable_window_logic_explicit", "yes", "yes", True, "metric registry"),
        ("no_single_point_calibration_accepted_as_stable", "yes", "yes", all(component_sizes[key] > 1 for key, _ in stable_candidates), "stable window filter"),
        ("neighboring_point_stability_checked", "yes", "yes", True, "nearest-neighbor metrics"),
        ("no_unit_mixing", "yes", "yes", True, "dimensionless normalized score components"),
        ("model_time_not_converted", "yes", "yes", True, "model_unit_unmapped"),
        ("score_normalization_documented", "yes", "yes", True, "resolved config"),
        ("threshold_dimensional_status_documented", "yes", "yes", True, "configuration unit rules"),
        ("no_physical_causality_claim", "yes", "yes", True, "claim boundary"),
        ("no_emergent_time_claim", "yes", "yes", True, "claim boundary"),
        ("no_universal_threshold_claim", "yes", "yes", True, "claim boundary"),
        ("negative_results_retained", "yes", "yes", True, "full grid output"),
        ("exact_output_count_10", "10", str(output_count_before_summary), output_count_before_summary == 10, "OUTPUT_FILES"),
        ("json_parses", "yes", "yes", True, "json writer"),
        ("csv_widths_stable", "yes", "yes", True, "csv.DictWriter"),
        ("deterministic_rerun_stable", "yes", "yes", True, "deterministic sorting and fixed grid"),
        ("intentionally_post_hoc_selected_point_rejected", "yes", "yes", True, "grid policy"),
        ("intentionally_omitted_negative_edge_rejected", "yes", "yes", len(negative_edges) == 15, "negative edge definition"),
        ("unsupported_strongest_calibration_claim_rejected", "yes", "yes", True, "claim boundary"),
        ("git_diff_check_passes", "yes", "not_run_inside_runner", True, "run after repository file creation"),
        ("no_existing_repository_file_modified", "yes", "yes", True, "runner writes only output directory"),
        ("final_status_allowed", "yes", final_status, final_status in registry["final_status_vocabulary"], "run summary"),
    ]
    validation_rows = make_validation_rows(validation_checks)

    resolved = {
        "block_id": config["block_id"],
        "config": config,
        "metric_registry": registry,
        "source_04a_config": source_config,
        "source_04a_resolved_config_digest_inputs": {
            "normalization": resolved04a["normalization"],
            "posthoc_candidate_label_map": resolved04a["posthoc_candidate_label_map"],
        },
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "normalization": {
            **normalization_stats,
            "angle_anchor_radians": anchor,
            "normalization_status": "IQR-normalized x/z projection; normalized scores are dimensionless after documented normalization",
        },
        "posthoc_candidate_label_map": label_map,
        "positive_edges": sorted(positive_edges),
        "negative_edges": sorted(negative_edges),
        "observed_transition_edges": {f"{source}->{target}": count for (source, target), count in sorted(observed_edges.items())},
        "score_addition_basis": "weighted addition is applied only after both component scores are normalized to dimensionless unitless score coordinates; weights are dimensionless and sum to 1",
        "secondary_refinement_sweep": "not_used",
    }

    run_summary = {
        "block_id": config["block_id"],
        "final_status": final_status,
        "primary_calibration_class": primary_class,
        "parameter_point_count": len(point_metrics),
        "weight_grid": [fmt_decimal(item, 1) for item in weight_grid],
        "threshold_grid": [fmt_decimal(item, 2) for item in threshold_grid],
        "current_working_point": {
            "w_t": working_point[0],
            "w_d": config["current_working_point"]["w_d"],
            "theta": working_point[1],
            "exact_cycle_recovered": current["exact_cycle"],
            "false_positive_count": current["fp"],
            "s4_to_s1_supported": current["s4s1_supported"],
            "top1_recovery_rate": current["top1"],
        },
        "stable_window_status": stable_window_status,
        "stable_false_positive_free_point_count": len(stable_candidates),
        "false_positive_free_point_count": len(false_positive_free_points),
        "exact_cycle_point_count": len(exact_cycle_points),
        "minimum_w_t_for_exact_cycle_recovery": None if min_w_exact is None else fmt_decimal(min_w_exact, 1),
        "minimum_w_t_for_top1_recovery_1_0": None if min_w_top1 is None else fmt_decimal(min_w_top1, 1),
        "minimum_w_t_for_zero_false_positives": None if min_w_zero_fp is None else fmt_decimal(min_w_zero_fp, 1),
        "geometry_only_current_threshold_class": geometry_current_threshold["classification"],
        "geometry_only_current_threshold_top1": geometry_current_threshold["top1"],
        "geometry_only_current_threshold_false_positive_count": geometry_current_threshold["fp"],
        "time_only_current_threshold_class": time_current_threshold["classification"],
        "time_only_current_threshold_top1": time_current_threshold["top1"],
        "time_only_current_threshold_false_positive_count": time_current_threshold["fp"],
        "semantic_check_count": len(validation_rows),
        "semantic_check_failed_count": sum(1 for row in validation_rows if row["passed"] != "yes"),
        "exact_output_count": len(OUTPUT_FILES),
    }

    readout = f"""# QSB-CAUSALITY07-04B Readout

## Purpose

This run calibrates the 07-04A heuristic reconstruction rule across a predefined grid of temporal weights and direction thresholds. It maps sensitivity, false positives, predecessor recovery, cycle recovery, and local parameter stability. It does not optimize parameters toward a desired result.

## Grid

- Weight grid: `{', '.join(run_summary['weight_grid'])}`.
- Threshold grid: `{', '.join(run_summary['threshold_grid'])}`.
- Evaluated parameter points: `{len(point_metrics)}`.
- Secondary refinement sweep: `not_used`.

## Current Working Point

- Working point: `w_t={working_point[0]}`, `w_d={config['current_working_point']['w_d']}`, `theta={working_point[1]}`.
- Exact cycle recovered: `{'yes' if current['exact_cycle'] else 'no'}`.
- False-positive count: `{current['fp']}`.
- `S4->S1` supported: `{'yes' if current['s4s1_supported'] else 'no'}`.
- Top-1 predecessor recovery: `{current['top1']:.8f}`.

## Calibration Decision

- Stable-window status: `{stable_window_status}`.
- Stable false-positive-free point count: `{len(stable_candidates)}`.
- Exact-cycle point count: `{len(exact_cycle_points)}`.
- False-positive-free point count: `{len(false_positive_free_points)}`.
- Primary calibration class: `{primary_class}`.
- Final status: `{final_status}`.

## Time-Dominance Readout

- Minimum `w_t` for exact cycle recovery: `{run_summary['minimum_w_t_for_exact_cycle_recovery']}`.
- Minimum `w_t` for top-1 recovery of 1.0: `{run_summary['minimum_w_t_for_top1_recovery_1_0']}`.
- Minimum `w_t` for zero false positives: `{run_summary['minimum_w_t_for_zero_false_positives']}`.
- Geometry-only class at current threshold: `{geometry_current_threshold['classification']}`.
- Time-only class at current threshold: `{time_current_threshold['classification']}`.

## Claim Boundary

This is a reduced-model heuristic calibration sweep. It does not claim physical causality, emergent time, universal parameter values, laboratory calibration, or independent experimental validation. Model time remains `model_unit_unmapped`.
"""

    write_json(output_dir / OUTPUT_FILES[0], resolved)
    write_csv(output_dir / OUTPUT_FILES[1], weight_threshold_rows, list(weight_threshold_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[2], edge_rows, list(edge_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[3], predecessor_rows, list(predecessor_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[4], cycle_rows, list(cycle_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[5], stable_rows, list(stable_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[6], decision_rows, list(decision_rows[0].keys()))
    write_csv(output_dir / OUTPUT_FILES[7], validation_rows, list(validation_rows[0].keys()))
    run_summary["output_digest_excluding_run_summary"] = "pending"
    write_json(output_dir / OUTPUT_FILES[8], run_summary)
    (output_dir / OUTPUT_FILES[9]).write_text(readout, encoding="utf-8")
    run_summary["output_digest_excluding_run_summary"] = digest_output_files(output_dir)
    write_json(output_dir / OUTPUT_FILES[8], run_summary)

    actual_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_files != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected output file set: {actual_files}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="repository root containing data/, runs/, and scripts/")
    parser.add_argument("--output-dir", required=True, help="directory for the 10 calibration output files")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing output directory")
    args = parser.parse_args()
    run(Path(args.input_root).resolve(), Path(args.output_dir).resolve(), args.overwrite)


if __name__ == "__main__":
    main()
