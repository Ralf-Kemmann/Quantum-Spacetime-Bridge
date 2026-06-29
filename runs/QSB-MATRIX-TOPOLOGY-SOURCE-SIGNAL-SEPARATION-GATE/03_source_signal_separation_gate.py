#!/usr/bin/env python3
"""Create a source-signal separation gate for the EXTRACT03 matrix topology chain."""

from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE"
RUN_DIR = Path("runs") / RUN_ID
SOURCE_CHAIN_LATEST_COMMIT = "8defdba"

EXTRACT_DIR = Path("runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum")
PRIMARY_EDGE_FILE = EXTRACT_DIR / "16_edge_candidate_result.csv"
STRUCTURE_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json")
SEMANTICS_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json")
STRENGTH_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json")
NULLMODEL_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT/04_nullmodel_summary.json")
ORIGIN_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/04_structure_origin_summary.json")
NEGATIVE_CONTROL_RECOMMENDATIONS = Path("runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/12_negative_control_recommendations.md")
DETECTOR_GENERALIZATION_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-DETECTOR-GENERALIZATION/04_detector_generalization_summary.json")
DETECTOR_CLASSIFICATION_SCHEMA = Path("runs/QSB-MATRIX-TOPOLOGY-DETECTOR-GENERALIZATION/07_pattern_origin_classification_schema.csv")
DETECTOR_NEXT_GATE = Path("runs/QSB-MATRIX-TOPOLOGY-DETECTOR-GENERALIZATION/13_next_problem_selection_gate.md")

CLAIM_BOUNDARY = "methodological_source_signal_separation_gate_no_physics_claim"
ROW_CLAIM_BOUNDARY = "source_signal_gate_no_physics_claim"


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    data["missing"] = False
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def parse_pair(pair_id: str) -> tuple[int, int]:
    left, right = pair_id.split("|")
    return int(left), int(right)


def pair_sort_key(pair_id: str) -> tuple[int, int]:
    return parse_pair(pair_id)


def bool_text(value: bool) -> str:
    return str(value).lower()


def format_float(value: float | None) -> str:
    if value is None:
        return ""
    return repr(float(value))


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "median": None, "mean": None, "max": None}
    return {
        "min": min(values),
        "median": median(values),
        "mean": mean(values),
        "max": max(values),
    }


def csv_shape(path: Path) -> tuple[int | str, int | str, list[str]]:
    if not path.exists() or path.suffix.lower() != ".csv":
        return "", "", []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return 0, 0, []
        row_count = sum(1 for _ in reader)
    return row_count, len(header), header


def classify_artifact_role(path: Path) -> tuple[str, str, str]:
    name = path.name.lower()
    if path == PRIMARY_EDGE_FILE:
        return "primary_edge_candidate_file", "no", "primary candidate artifact; contains rule/threshold outputs"
    if "strength_matrix" in name:
        return "pre_candidate_relation_strength_matrix", "unclear", "pre-candidate strength matrix; provenance appears pipeline-native, not independently source-native"
    if "distance_cost" in name:
        return "distance_cost_matrix", "unclear", "pre-candidate distance/cost matrix; needs upstream rule trace before source-native claim"
    if "shortest_path" in name:
        return "shortest_path_matrix", "unclear", "pre-candidate shortest-path matrix; needs upstream rule trace before source-native claim"
    if "k_candidate" in name:
        return "k_candidate_matrix", "unclear", "candidate matrix upstream of edge table; source-native status unresolved"
    if "manifest" in name:
        return "source_manifest", "no", "manifest/provenance context"
    if "lineage" in name or "hash" in name:
        return "lineage_file", "no", "lineage/provenance context"
    if "config" in name:
        return "config_file", "no", "config context"
    if "detector_generalization" in str(path):
        return "detector_generalization_context", "no", "methodology context"
    if "origin" in str(path):
        return "origin_audit_context", "no", "origin-audit context"
    if "negative_control" in name:
        return "negative_control_recommendations", "no", "control recommendation context"
    return "unknown_relevant_artifact", "unclear", "relevant by filename search terms; source-native status unresolved"


def source_artifact_inventory() -> list[dict[str, object]]:
    paths: list[Path] = [
        PRIMARY_EDGE_FILE,
        EXTRACT_DIR / "11_K_candidate_matrix.csv",
        EXTRACT_DIR / "13_distance_cost_matrix.csv",
        EXTRACT_DIR / "14_shortest_path_D_matrix.csv",
        EXTRACT_DIR / "15_strength_matrix.csv",
        EXTRACT_DIR / "01_extract03a_r1_run_manifest.json",
        EXTRACT_DIR / "02_upstream_inventory_and_hashes.csv",
        EXTRACT_DIR / "23_lineage_and_hash_audit.csv",
        NEGATIVE_CONTROL_RECOMMENDATIONS,
        DETECTOR_GENERALIZATION_SUMMARY,
        DETECTOR_CLASSIFICATION_SCHEMA,
        DETECTOR_NEXT_GATE,
        ORIGIN_SUMMARY,
    ]
    terms = [
        "relation_strength",
        "K_candidate",
        "distance_cost",
        "shortest_path_D",
        "pair_pair",
        "matrix",
        "graph",
        "source_feature",
        "source",
        "raw",
        "edge",
        "candidate",
        "theta",
        "threshold",
        "lineage",
        "provenance",
        "manifest",
        "config",
    ]
    if EXTRACT_DIR.exists():
        for path in sorted(EXTRACT_DIR.iterdir(), key=lambda item: item.name):
            if path.is_file() and any(term.lower() in path.name.lower() for term in terms):
                paths.append(path)
    unique_paths = sorted(set(paths), key=lambda item: str(item))
    rows: list[dict[str, object]] = []
    for path in unique_paths:
        role, source_native, notes = classify_artifact_role(path)
        row_count, column_count, header = csv_shape(path)
        rows.append(
            {
                "artifact_role": role,
                "path": str(path),
                "exists": bool_text(path.exists()),
                "file_type": path.suffix.lower().lstrip("."),
                "row_count": row_count,
                "column_count": column_count,
                "key_columns": ";".join(header[:8]),
                "source_native_candidate": source_native,
                "notes": notes,
                "claim_boundary": ROW_CLAIM_BOUNDARY,
            }
        )
    return rows


def edge_enrichment() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    source_feature_columns = []
    for row in read_csv_rows(PRIMARY_EDGE_FILE):
        pair_a = row["pair_a"]
        pair_b = row["pair_b"]
        i_a, j_a = parse_pair(pair_a)
        i_b, j_b = parse_pair(pair_b)
        delta_a = j_a - i_a
        delta_b = j_b - i_b
        abs_delta_a = abs(delta_a)
        abs_delta_b = abs(delta_b)
        orientation_a = "forward" if delta_a > 0 else "backward" if delta_a < 0 else "diagonal"
        orientation_b = "forward" if delta_b > 0 else "backward" if delta_b < 0 else "diagonal"
        strength = float(row.get("strength", row.get("relation_strength", "")))
        theta_edge = float(row["theta_edge"]) if row.get("theta_edge", "") != "" else None
        edge_candidate_flag = int(row["edge_candidate_flag"])
        source_features_present = any(column.startswith("source_feature_") for column in row)
        if source_features_present:
            source_feature_columns.extend(column for column in row if column.startswith("source_feature_"))
        rows.append(
            {
                "pair_a": pair_a,
                "pair_b": pair_b,
                "i_a": i_a,
                "j_a": j_a,
                "i_b": i_b,
                "j_b": j_b,
                "delta_a": delta_a,
                "delta_b": delta_b,
                "abs_delta_a": abs_delta_a,
                "abs_delta_b": abs_delta_b,
                "same_abs_delta": bool_text(abs_delta_a == abs_delta_b),
                "edge_candidate_flag": edge_candidate_flag,
                "strength": format_float(strength),
                "theta_edge": format_float(theta_edge),
                "strength_margin": format_float(strength - theta_edge if theta_edge is not None else None),
                "abs_delta_gap": abs(abs_delta_a - abs_delta_b),
                "same_orientation": bool_text(orientation_a == orientation_b),
                "shares_left_index": bool_text(i_a == i_b),
                "shares_right_index": bool_text(j_a == j_b),
                "shares_any_index": bool_text(bool({i_a, j_a} & {i_b, j_b})),
                "pair_index_sum_gap": abs((i_a + j_a) - (i_b + j_b)),
                "source_native_features_present": bool_text(source_features_present),
                "source_feature_columns": ";".join(sorted(set(source_feature_columns))),
            }
        )
    rows.sort(
        key=lambda item: (
            int(item["abs_delta_a"]),
            int(item["abs_delta_b"]),
            pair_sort_key(str(item["pair_a"])),
            pair_sort_key(str(item["pair_b"])),
        )
    )
    return rows


def predictability_audit(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    tests: list[dict[str, object]] = []

    def add_test(test_id: str, target: str, predictor_set: str, correct: int, total: int, interpretation: str) -> None:
        incorrect = total - correct
        tests.append(
            {
                "test_id": test_id,
                "target": target,
                "predictor_set": predictor_set,
                "rows_tested": total,
                "correct_count": correct,
                "incorrect_count": incorrect,
                "accuracy": correct / total if total else "",
                "perfect_prediction": bool_text(total > 0 and incorrect == 0),
                "interpretation": interpretation,
            }
        )

    add_test(
        "P01",
        "edge_candidate_flag",
        "same_abs_delta",
        sum(1 for row in rows if int(row["edge_candidate_flag"]) == (1 if row["same_abs_delta"] == "true" else 0)),
        len(rows),
        "Candidate flag is tested against same Pair-ID abs_delta.",
    )
    add_test(
        "P02",
        "edge_candidate_flag",
        "strength >= theta_edge",
        sum(1 for row in rows if int(row["edge_candidate_flag"]) == (1 if float(row["strength"]) >= float(row["theta_edge"]) else 0)),
        len(rows),
        "Candidate flag is tested against thresholded strength.",
    )
    add_test(
        "P03",
        "strength == 1.0",
        "same_abs_delta",
        sum(1 for row in rows if (float(row["strength"]) == 1.0) == (row["same_abs_delta"] == "true")),
        len(rows),
        "Unit strength is tested against same Pair-ID abs_delta.",
    )
    by_gap: dict[int, set[str]] = defaultdict(set)
    for row in rows:
        by_gap[int(row["abs_delta_gap"])].add(row["strength"])
    deterministic_by_gap = all(len(values) == 1 for values in by_gap.values())
    add_test(
        "P04",
        "strength group",
        "abs_delta_gap",
        len(rows) if deterministic_by_gap else 0,
        len(rows),
        "Checks whether abs_delta_gap alone determines strength exactly.",
    )
    by_pair: dict[tuple[int, int], set[str]] = defaultdict(set)
    for row in rows:
        key = tuple(sorted((int(row["abs_delta_a"]), int(row["abs_delta_b"]))))
        by_pair[key].add(row["strength"])
    deterministic_by_pair = all(len(values) == 1 for values in by_pair.values())
    add_test(
        "P05",
        "cross-block strength summarized by abs_delta pair",
        "unordered abs_delta_a,abs_delta_b",
        len(rows) if deterministic_by_pair else 0,
        len(rows),
        "Checks whether unordered abs_delta pair determines strength exactly in the current artifact.",
    )
    return tests


def residual_profile(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    def group_and_profile(model: str, key_fn) -> list[dict[str, object]]:
        grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in rows:
            grouped[key_fn(row)].append(row)
        output: list[dict[str, object]] = []
        for key in sorted(grouped):
            group_rows = grouped[key]
            strengths = [float(row["strength"]) for row in group_rows]
            group_mean = statistics.fmean(strengths)
            residuals = [value - group_mean for value in strengths]
            strength_stats = stats(strengths)
            residual_stats = stats(residuals)
            output.append(
                {
                    "residual_model": model,
                    "group_key": key,
                    "edge_rows": len(group_rows),
                    "strength_min": format_float(strength_stats["min"]),
                    "strength_median": format_float(strength_stats["median"]),
                    "strength_mean": format_float(strength_stats["mean"]),
                    "strength_max": format_float(strength_stats["max"]),
                    "residual_min": format_float(residual_stats["min"]),
                    "residual_median": format_float(residual_stats["median"]),
                    "residual_mean": format_float(residual_stats["mean"]),
                    "residual_max": format_float(residual_stats["max"]),
                    "residual_abs_mean": format_float(statistics.fmean(abs(value) for value in residuals) if residuals else None),
                    "residual_nonzero_count": sum(1 for value in residuals if abs(value) > 1e-12),
                }
            )
        return output

    coarse = group_and_profile("coarse_same_abs_delta", lambda row: f"same_abs_delta={row['same_abs_delta']}")
    abs_pair = group_and_profile(
        "abs_delta_pair",
        lambda row: f"abs_delta_pair={min(int(row['abs_delta_a']), int(row['abs_delta_b']))},{max(int(row['abs_delta_a']), int(row['abs_delta_b']))}",
    )
    fine = group_and_profile(
        "fine_label_features",
        lambda row: (
            f"abs_delta_pair={min(int(row['abs_delta_a']), int(row['abs_delta_b']))},"
            f"{max(int(row['abs_delta_a']), int(row['abs_delta_b']))}|"
            f"same_orientation={row['same_orientation']}|shares_any_index={row['shares_any_index']}"
        ),
    )
    return coarse + abs_pair + fine


def graph_metrics_for_threshold(rows: list[dict[str, object]], theta: float) -> dict[str, object]:
    nodes = sorted({str(row["pair_a"]) for row in rows} | {str(row["pair_b"]) for row in rows}, key=pair_sort_key)
    index = {node: pos for pos, node in enumerate(nodes)}
    adj = [set() for _ in nodes]
    selected = []
    within = 0
    cross = 0
    for row in rows:
        if float(row["strength"]) >= theta:
            a = index[str(row["pair_a"])]
            b = index[str(row["pair_b"])]
            adj[a].add(b)
            adj[b].add(a)
            selected.append((a, b, row))
            if row["same_abs_delta"] == "true":
                within += 1
            else:
                cross += 1
    seen = set()
    component_sizes = []
    component_edges = []
    for start in range(len(nodes)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in adj[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        component_sizes.append(len(component))
        component_set = set(component)
        component_edges.append(sum(1 for a, b, _row in selected if a in component_set and b in component_set))
    component_count = len(component_sizes)
    largest = max(component_sizes) if component_sizes else 0
    complete_disjoint = bool(selected) and all(
        edge_count == size * (size - 1) // 2
        for size, edge_count in zip(component_sizes, component_edges)
    )
    return {
        "candidate_edge_count": len(selected),
        "within_same_abs_delta_candidate_count": within,
        "cross_abs_delta_candidate_count": cross,
        "component_count": component_count,
        "largest_component_size": largest,
        "complete_disjoint_clique_blocks": complete_disjoint,
    }


def threshold_sweep(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for step in range(0, 21):
        theta = step * 0.05
        metrics = graph_metrics_for_threshold(rows, theta)
        notes = "observed_theta" if abs(theta - 0.5) < 1e-12 else "simulated_from_existing_strength"
        output.append(
            {
                "theta": format_float(theta),
                "candidate_edge_count": metrics["candidate_edge_count"],
                "within_same_abs_delta_candidate_count": metrics["within_same_abs_delta_candidate_count"],
                "cross_abs_delta_candidate_count": metrics["cross_abs_delta_candidate_count"],
                "component_count": metrics["component_count"],
                "largest_component_size": metrics["largest_component_size"],
                "complete_disjoint_clique_blocks": bool_text(bool(metrics["complete_disjoint_clique_blocks"])),
                "notes": notes,
            }
        )
    return output


def source_signal_tests(
    inventory: list[dict[str, object]],
    edge_rows: list[dict[str, object]],
    predictability_rows: list[dict[str, object]],
    residual_rows: list[dict[str, object]],
    origin: dict,
) -> list[dict[str, object]]:
    source_native_yes = [row for row in inventory if row["source_native_candidate"] == "yes"]
    source_native_unclear = [row for row in inventory if row["source_native_candidate"] == "unclear"]
    source_features_primary = any(row["source_native_features_present"] == "true" for row in edge_rows)
    same_abs_delta_perfect = next(row for row in predictability_rows if row["test_id"] == "P01")["perfect_prediction"] == "true"
    threshold_perfect = next(row for row in predictability_rows if row["test_id"] == "P02")["perfect_prediction"] == "true"
    abs_pair_perfect = next(row for row in predictability_rows if row["test_id"] == "P05")["perfect_prediction"] == "true"
    cross_variation = any(
        row["residual_model"] == "coarse_same_abs_delta"
        and row["group_key"] == "same_abs_delta=false"
        and int(row["residual_nonzero_count"]) > 0
        for row in residual_rows
    )
    return [
        {
            "test_id": "T01",
            "test_name": "source_native_features_present",
            "result": "pass" if source_native_yes or source_features_primary else "partial" if source_native_unclear else "fail",
            "evidence": f"yes_artifacts={len(source_native_yes)};unclear_artifacts={len(source_native_unclear)};primary_source_feature_columns={source_features_primary}",
            "blocking_issue": "source-native status is unresolved for pre-candidate matrices" if source_native_unclear and not source_native_yes else "",
            "next_action": "resolve upstream generator and source-feature provenance",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T02",
            "test_name": "edge_strength_not_fully_explained_by_same_abs_delta",
            "result": "fail" if same_abs_delta_perfect else "pass",
            "evidence": f"same_abs_delta_perfectly_predicts_candidate_flag={same_abs_delta_perfect}",
            "blocking_issue": "candidate topology is already explained by same_abs_delta",
            "next_action": "test residual strength variation only after separating label features",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T03",
            "test_name": "cross_block_strength_has_nontrivial_variation",
            "result": "pass" if cross_variation else "fail",
            "evidence": f"cross_block_coarse_residual_nonzero={cross_variation}",
            "blocking_issue": "",
            "next_action": "check whether variation is label-feature explained",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T04",
            "test_name": "cross_block_strength_variation_explained_by_label_features",
            "result": "pass" if abs_pair_perfect else "partial",
            "evidence": f"unordered_abs_delta_pair_perfectly_determines_strength={abs_pair_perfect}",
            "blocking_issue": "" if abs_pair_perfect else "some residual variation remains after abs_delta-pair grouping",
            "next_action": "perform source-feature comparison only if independent features are available",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T05",
            "test_name": "source_artifact_lineage_resolved",
            "result": "unresolved",
            "evidence": f"origin_upstream_trace_status={origin.get('upstream_trace_status', 'missing')}",
            "blocking_issue": "upstream generator trace is not resolved",
            "next_action": "run upstream generator trace resolution",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T06",
            "test_name": "source_feature_supports_same_blocks_independently",
            "result": "unresolved",
            "evidence": "no independent source-feature test is available in the current artifact set",
            "blocking_issue": "source-native features are not certified independent of rule/label construction",
            "next_action": "identify or construct independent source-feature matrix",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T07",
            "test_name": "label_permuted_recomputation_possible",
            "result": "unresolved",
            "evidence": "post-hoc label permutation exists; upstream recomputation path is unresolved",
            "blocking_issue": "upstream generator/config path needs trace resolution",
            "next_action": "resolve generator and rerun after label permutation",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T08",
            "test_name": "threshold_sweep_possible",
            "result": "pass",
            "evidence": "strength and theta_edge columns are present in the primary edge artifact",
            "blocking_issue": "",
            "next_action": "use current strength values for artifact-level threshold sweep; upstream sweep still requires generator",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T09",
            "test_name": "negative_control_available",
            "result": "partial",
            "evidence": f"negative_control_recommendations_present={NEGATIVE_CONTROL_RECOMMENDATIONS.exists()}",
            "blocking_issue": "recommendations exist, but execution requires upstream trace/recompute setup",
            "next_action": "convert recommendations into executable controls",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
        {
            "test_id": "T10",
            "test_name": "source_signal_remaining_after_rule_label_threshold_controls",
            "result": "unresolved",
            "evidence": "candidate topology is rule/label/threshold explained; source-native independent support is not resolved",
            "blocking_issue": "current artifacts do not certify a source-driven residual",
            "next_action": "run upstream generator trace resolution before source-signal claim",
            "claim_boundary": ROW_CLAIM_BOUNDARY,
        },
    ]


def feasibility_rows() -> list[dict[str, object]]:
    return [
        {
            "control_id": "C01",
            "control_name": "posthoc_pair_label_permutation",
            "requires_source_generator": "false",
            "requires_source_features": "false",
            "requires_config": "false",
            "available_now": "true",
            "feasible_without_upstream_generator": "true",
            "expected_diagnostic_value": "tests label binding of current artifact only",
            "blocking_issue": "",
            "next_action": "use as sanity check, not source-signal proof",
        },
        {
            "control_id": "C02",
            "control_name": "recompute_after_pair_label_permutation",
            "requires_source_generator": "true",
            "requires_source_features": "true",
            "requires_config": "true",
            "available_now": "false",
            "feasible_without_upstream_generator": "false",
            "expected_diagnostic_value": "tests whether source values or labels drive the structure",
            "blocking_issue": "upstream generator trace unresolved",
            "next_action": "resolve generator path and config",
        },
        {
            "control_id": "C03",
            "control_name": "recompute_after_abs_delta_masking",
            "requires_source_generator": "true",
            "requires_source_features": "true",
            "requires_config": "true",
            "available_now": "false",
            "feasible_without_upstream_generator": "false",
            "expected_diagnostic_value": "tests whether abs_delta term is necessary",
            "blocking_issue": "rule location unresolved",
            "next_action": "trace rule implementation",
        },
        {
            "control_id": "C04",
            "control_name": "recompute_with_random_pair_ids_same_source_values",
            "requires_source_generator": "true",
            "requires_source_features": "true",
            "requires_config": "true",
            "available_now": "false",
            "feasible_without_upstream_generator": "false",
            "expected_diagnostic_value": "separates labels from source values",
            "blocking_issue": "source-native values not independently certified",
            "next_action": "identify source-native matrix and generator",
        },
        {
            "control_id": "C05",
            "control_name": "recompute_with_threshold_sweep",
            "requires_source_generator": "false",
            "requires_source_features": "false",
            "requires_config": "false",
            "available_now": "true",
            "feasible_without_upstream_generator": "true",
            "expected_diagnostic_value": "artifact-level candidate sensitivity from existing strength",
            "blocking_issue": "does not test upstream strength recomputation",
            "next_action": "run artifact-level sweep now; upstream sweep after generator trace",
        },
        {
            "control_id": "C06",
            "control_name": "recompute_with_rule_ablation_no_abs_delta",
            "requires_source_generator": "true",
            "requires_source_features": "true",
            "requires_config": "true",
            "available_now": "false",
            "feasible_without_upstream_generator": "false",
            "expected_diagnostic_value": "direct test of rule-induced origin",
            "blocking_issue": "upstream rule/generator unresolved",
            "next_action": "run upstream generator trace resolution",
        },
    ]


def classification_rows() -> list[dict[str, object]]:
    return [
        {
            "classification_id": "rule_induced_structure",
            "applies": "true",
            "evidence": "origin audit found edge_candidate_flag equivalent to same_abs_delta with mismatch_count=0",
            "allowed_claim": "artifact-level rule-structured relational pattern",
            "forbidden_claim": "independent source-driven signal",
            "next_gate": "rule ablation recompute",
        },
        {
            "classification_id": "label_induced_structure",
            "applies": "true",
            "evidence": "same_abs_delta is derived from Pair-ID labels and explains candidate topology",
            "allowed_claim": "label-derived structure in current artifact",
            "forbidden_claim": "label-invariant source structure",
            "next_gate": "label-permuted recomputation",
        },
        {
            "classification_id": "threshold_induced_structure",
            "applies": "true",
            "evidence": "edge_candidate_flag equivalent to strength >= theta_edge",
            "allowed_claim": "threshold-selected candidate structure",
            "forbidden_claim": "threshold-independent candidate structure",
            "next_gate": "threshold sweep",
        },
        {
            "classification_id": "source_supported_structure",
            "applies": "unresolved",
            "evidence": "no independent source-native support certified under current artifacts",
            "allowed_claim": "unresolved source support",
            "forbidden_claim": "source-supported structure",
            "next_gate": "source-feature provenance resolution",
        },
        {
            "classification_id": "source_driven_structure",
            "applies": "false",
            "evidence": "candidate topology is already fully explained by rule/label/threshold features",
            "allowed_claim": "not established",
            "forbidden_claim": "source-driven structure",
            "next_gate": "upstream recomputation controls",
        },
        {
            "classification_id": "mixed_origin_structure",
            "applies": "unresolved",
            "evidence": "cross-block strength variation exists but is label-feature grouped; source component not certified",
            "allowed_claim": "mixed origin unresolved",
            "forbidden_claim": "mixed source-rule claim",
            "next_gate": "source residual audit after provenance resolution",
        },
        {
            "classification_id": "unresolved_source_signal",
            "applies": "true",
            "evidence": "current artifacts do not support or exclude independent source signal after recompute controls",
            "allowed_claim": "source signal unresolved under current artifacts",
            "forbidden_claim": "source signal supported or absent as final conclusion",
            "next_gate": "upstream generator trace resolution",
        },
        {
            "classification_id": "source_signal_absent_after_controls",
            "applies": "false",
            "evidence": "controls are not executable enough to exclude source signal fully",
            "allowed_claim": "not established",
            "forbidden_claim": "source signal absent after all controls",
            "next_gate": "execute recomputation controls",
        },
        {
            "classification_id": "source_signal_candidate_pending_recompute",
            "applies": "false",
            "evidence": "source-native independent features are not certified; recompute pending",
            "allowed_claim": "candidate not opened from current artifacts",
            "forbidden_claim": "source-signal candidate",
            "next_gate": "identify independent source features",
        },
    ]


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    structure = read_json(STRUCTURE_SUMMARY)
    semantics = read_json(SEMANTICS_SUMMARY)
    strength = read_json(STRENGTH_SUMMARY)
    nullmodel = read_json(NULLMODEL_SUMMARY)
    origin = read_json(ORIGIN_SUMMARY)
    _detector = read_json(DETECTOR_GENERALIZATION_SUMMARY) if DETECTOR_GENERALIZATION_SUMMARY.exists() else {"missing": True}

    inventory = source_artifact_inventory()
    edge_rows = edge_enrichment()
    predictability = predictability_audit(edge_rows)
    residuals = residual_profile(edge_rows)
    tests = source_signal_tests(inventory, edge_rows, predictability, residuals, origin)
    feasibility = feasibility_rows()
    thresholds = threshold_sweep(edge_rows)
    classifications = classification_rows()

    write_csv(
        RUN_DIR / "05_source_artifact_inventory.csv",
        ["artifact_role", "path", "exists", "file_type", "row_count", "column_count", "key_columns", "source_native_candidate", "notes", "claim_boundary"],
        inventory,
    )
    write_csv(
        RUN_DIR / "06_edge_enriched_rule_source_features.csv",
        [
            "pair_a", "pair_b", "i_a", "j_a", "i_b", "j_b", "delta_a", "delta_b",
            "abs_delta_a", "abs_delta_b", "same_abs_delta", "edge_candidate_flag",
            "strength", "theta_edge", "strength_margin", "abs_delta_gap", "same_orientation",
            "shares_left_index", "shares_right_index", "shares_any_index", "pair_index_sum_gap",
            "source_native_features_present", "source_feature_columns",
        ],
        edge_rows,
    )
    write_csv(
        RUN_DIR / "07_rule_label_threshold_predictability_audit.csv",
        ["test_id", "target", "predictor_set", "rows_tested", "correct_count", "incorrect_count", "accuracy", "perfect_prediction", "interpretation"],
        predictability,
    )
    write_csv(
        RUN_DIR / "08_source_residual_profile.csv",
        [
            "residual_model", "group_key", "edge_rows", "strength_min", "strength_median",
            "strength_mean", "strength_max", "residual_min", "residual_median",
            "residual_mean", "residual_max", "residual_abs_mean", "residual_nonzero_count",
        ],
        residuals,
    )
    write_csv(
        RUN_DIR / "09_source_signal_candidate_tests.csv",
        ["test_id", "test_name", "result", "evidence", "blocking_issue", "next_action", "claim_boundary"],
        tests,
    )
    write_csv(
        RUN_DIR / "10_label_permuted_recomputation_feasibility.csv",
        ["control_id", "control_name", "requires_source_generator", "requires_source_features", "requires_config", "available_now", "feasible_without_upstream_generator", "expected_diagnostic_value", "blocking_issue", "next_action"],
        feasibility,
    )
    write_csv(
        RUN_DIR / "11_threshold_sweep_feasibility.csv",
        ["theta", "candidate_edge_count", "within_same_abs_delta_candidate_count", "cross_abs_delta_candidate_count", "component_count", "largest_component_size", "complete_disjoint_clique_blocks", "notes"],
        thresholds,
    )
    write_csv(
        RUN_DIR / "12_source_signal_classification.csv",
        ["classification_id", "applies", "evidence", "allowed_claim", "forbidden_claim", "next_gate"],
        classifications,
    )

    source_native_count = sum(1 for row in inventory if row["source_native_candidate"] == "yes")
    source_features_primary = any(row["source_native_features_present"] == "true" for row in edge_rows)
    strength_detected = all(row["strength"] != "" for row in edge_rows)
    theta_detected = all(row["theta_edge"] != "" for row in edge_rows)
    upstream_resolved = origin.get("upstream_trace_status") == "upstream_rule_trace_found"
    test_counts = {result: sum(1 for row in tests if row["result"] == result) for result in ["pass", "fail", "partial", "unresolved"]}
    same_abs_count = sum(1 for row in edge_rows if row["same_abs_delta"] == "true")
    cross_abs_count = len(edge_rows) - same_abs_count
    candidate_count = sum(1 for row in edge_rows if int(row["edge_candidate_flag"]) == 1)
    non_candidate_count = len(edge_rows) - candidate_count

    if source_native_count == 0 and not source_features_primary:
        current_source_signal_status = "source_signal_not_testable_from_current_artifacts"
    elif upstream_resolved and source_features_primary:
        current_source_signal_status = "source_signal_supported_under_current_artifacts"
    else:
        current_source_signal_status = "source_signal_unresolved_pending_upstream_recompute"
    current_pattern_origin_classification = "rule_induced_artifact_structure_source_signal_unresolved"
    recommended_next_run_id = "QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION"
    status = "source_signal_separation_gate_completed_with_blockers"

    summary = {
        "run_id": RUN_ID,
        "source_chain_latest_commit": SOURCE_CHAIN_LATEST_COMMIT,
        "primary_edge_file": str(PRIMARY_EDGE_FILE),
        "edge_rows_total": len(edge_rows),
        "candidate_edge_count": candidate_count,
        "non_candidate_edge_count": non_candidate_count,
        "same_abs_delta_edge_count": same_abs_count,
        "cross_abs_delta_edge_count": cross_abs_count,
        "rule_equivalence_confirmed_from_origin_audit": bool(origin.get("edge_candidate_equivalent_to_same_abs_delta") and origin.get("edge_candidate_equivalent_to_strength_threshold")),
        "source_artifact_count": len(inventory),
        "source_native_candidate_artifact_count": source_native_count,
        "source_native_features_present_in_primary_edge_file": source_features_primary,
        "strength_column_detected": strength_detected,
        "theta_edge_detected": theta_detected,
        "threshold_sweep_feasible_from_existing_strength": strength_detected and theta_detected,
        "label_permuted_recompute_feasible_now": False,
        "rule_ablation_recompute_feasible_now": False,
        "upstream_generator_trace_resolved": upstream_resolved,
        "source_signal_tests_pass": test_counts["pass"],
        "source_signal_tests_fail": test_counts["fail"],
        "source_signal_tests_partial": test_counts["partial"],
        "source_signal_tests_unresolved": test_counts["unresolved"],
        "current_source_signal_status": current_source_signal_status,
        "current_pattern_origin_classification": current_pattern_origin_classification,
        "recommended_next_run_id": recommended_next_run_id,
        "status": status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_source_signal_separation_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    write_text(
        RUN_DIR / "13_negative_control_execution_plan.md",
        """# Negative Control Execution Plan

## 1. Upstream generator trace resolution

Purpose: identify the exact script/config path that produced strength and candidate flags.
Needed inputs: generator scripts, configs, manifests, lineage hashes.
Expected if rule-induced: generator exposes rule/label/threshold construction.
Expected if source-signal present: generator exposes independent source features not reducible to labels.
Review boundary: trace resolution is methodological only.

## 2. Label-permuted recomputation

Purpose: test whether structure follows Pair-ID labels during generation.
Needed inputs: upstream generator, source features, config.
Expected if rule-induced: structure follows permuted labels or changes predictably.
Expected if source-signal present: structure remains aligned with source features, not labels.
Review boundary: post-hoc permutation is insufficient.

## 3. Abs-delta masking / rule ablation

Purpose: remove or mask abs_delta information in the generator.
Needed inputs: editable generator or configurable rule.
Expected if rule-induced: block topology collapses or changes.
Expected if source-signal present: residual structure remains.
Review boundary: ablation must not introduce unrelated algorithm changes.

## 4. Threshold sweep from continuous strength

Purpose: test candidate sensitivity to theta.
Needed inputs: continuous strength values and threshold rule.
Expected if rule-induced: block topology appears only in predictable threshold ranges.
Expected if source-signal present: source-aligned structure remains across meaningful ranges.
Review boundary: artifact-level sweep does not replace upstream recompute.

## 5. Independent source-feature matrix test

Purpose: compare detected structure against independent source-native features.
Needed inputs: source feature matrix not derived from Pair-ID label distance.
Expected if rule-induced: no independent support after controls.
Expected if source-signal present: source features align with residual structure.
Review boundary: source-feature independence must be documented.

## 6. Negative source control

Purpose: run detector on source data where no structure is expected.
Needed inputs: negative control matrix or synthetic source.
Expected if rule-induced: detector may reproduce rule patterns if labels remain.
Expected if source-signal present: no target-specific alignment should appear in control.
Review boundary: failed negative control blocks source claims.

## 7. Positive synthetic calibration control

Purpose: verify detector can recover known injected source structure.
Needed inputs: synthetic matrix with known injected pattern.
Expected if rule-induced: rule-only detector should not overclaim source origin.
Expected if source-signal present: injected source structure is recovered and classified correctly.
Review boundary: calibration proves detector behavior, not EXTRACT03 physics.
""",
    )

    write_text(
        RUN_DIR / "14_source_signal_separation_review_note.md",
        f"""# QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE

## Purpose

This gate separates the detector's ability to reveal structure from the stronger question of whether the structure is source-driven.

## Source basis

The gate reads the EXTRACT03 edge-candidate artifact and prior structure, semantics, strength, nullmodel, origin, and detector-generalization context where available.

## Rule/label/threshold controls

The prior origin audit confirms artifact-level equivalence between candidate edges and shared Pair-ID `abs_delta`, and between candidate flags and thresholded strength. This run reuses that boundary and profiles rule/label/threshold predictability.

## Available source-native artifacts

The EXTRACT03A-R1 folder contains pre-candidate matrices and lineage files. Their source-native status is not certified here; they are inventoried as available or unclear, not as independent source evidence.

## Residual signal after rule/label grouping

Residual profiles are produced after grouping by same-abs-delta and label-derived abs-delta pairs. Cross-block strength variation exists at coarse grouping, but current artifacts do not certify it as source-native residual signal.

## Threshold sweep feasibility

Threshold sweep is feasible from existing `strength` and `theta_edge` columns at artifact level. It does not replace upstream recomputation.

## Label-permuted recomputation feasibility

Post-hoc label permutation is feasible, but true recomputation after label permutation is not feasible now because the upstream generator trace is unresolved.

## Source-signal classification

Current source-signal status: `{summary["current_source_signal_status"]}`.
Current pattern-origin classification: `{summary["current_pattern_origin_classification"]}`.

## Interpretation

This gate separates the detector's ability to reveal structure from the stronger question of whether the structure is source-driven. For EXTRACT03, the candidate topology is already explained at artifact level by rule/label/threshold features; any source-signal claim requires upstream recomputation or independent source-native features.

## Claim boundary

This is a methodological source-signal separation gate. It makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence claim.

## Next-step gate

Recommended next run: `{summary["recommended_next_run_id"]}`.
""",
    )

    write_csv(
        RUN_DIR / "15_source_feature_correlation_inventory.csv",
        ["feature_source", "path", "feature_columns", "independent_source_native_status", "correlation_test_possible_now", "blocking_issue", "claim_boundary"],
        [
            {
                "feature_source": "primary_edge_file",
                "path": str(PRIMARY_EDGE_FILE),
                "feature_columns": "",
                "independent_source_native_status": "absent",
                "correlation_test_possible_now": "false",
                "blocking_issue": "no source_feature_* columns in primary edge artifact",
                "claim_boundary": ROW_CLAIM_BOUNDARY,
            },
            {
                "feature_source": "pre_candidate_matrices",
                "path": str(EXTRACT_DIR),
                "feature_columns": "K_candidate;d_cost_candidate;D_shortest_path_candidate;relation_strength",
                "independent_source_native_status": "unclear",
                "correlation_test_possible_now": "partial",
                "blocking_issue": "pre-candidate matrices need upstream provenance before source-native interpretation",
                "claim_boundary": ROW_CLAIM_BOUNDARY,
            },
        ],
    )
    write_text(
        RUN_DIR / "16_next_run_prompt_recommendation.md",
        """# Next Run Prompt Recommendation

Recommended run ID:

`QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION`

Goal:

Resolve the exact upstream generator and config path that produces `15_strength_matrix.csv` and `16_edge_candidate_result.csv`, then determine whether `relation_strength`, `theta_edge`, and `edge_candidate_flag` are generated from Pair-ID label distance, source-native features, or a mixed rule.

Required outputs should include a generator trace inventory, rule reconstruction table, source-native feature inventory, and a recomputation feasibility decision.
""",
    )

    if structure.get("candidate_edge_count") != candidate_count:
        raise ValueError("Candidate count differs from block-structure summary")
    if strength.get("candidate_edge_count") != candidate_count:
        raise ValueError("Candidate count differs from strength summary")
    if nullmodel.get("observed_edge_count") != candidate_count:
        raise ValueError("Candidate count differs from nullmodel summary")
    if semantics.get("node_count") != len({row["pair_a"] for row in edge_rows} | {row["pair_b"] for row in edge_rows}):
        raise ValueError("Node count differs from semantics summary")


if __name__ == "__main__":
    main()
