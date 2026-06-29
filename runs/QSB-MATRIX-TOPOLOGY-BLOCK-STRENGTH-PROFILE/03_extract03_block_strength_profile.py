#!/usr/bin/env python3
"""Profile edge strengths within and between confirmed Pair-ID distance blocks."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


RUN_ID = "QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE"
RUN_DIR = Path("runs") / RUN_ID

SOURCE_EDGE_FILE = Path(
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
CLOSURE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json")
BLOCK_STRUCTURE_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json"
)
BLOCK_SEMANTICS_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json"
)
PAIR_SEMANTICS_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/05_pair_id_semantics_by_node.csv"
)
COMPONENT_SEMANTICS_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/06_component_semantics_profile.csv"
)

CLAIM_BOUNDARY = (
    "Purely structural graph-theoretic, index-semantic, and numerically descriptive "
    "strength profile. No claim is made about physical geometry, spacetime, metric "
    "structure, gravitation, causality, dynamics, experimental validation, or physical "
    "emergence."
)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def parse_int(value: str) -> int:
    return int(value)


def pair_sort_key(pair_id: str) -> tuple[int, int]:
    left, right = pair_id.split("|")
    return int(left), int(right)


def format_float(value: float | None) -> str:
    if value is None:
        return ""
    return repr(float(value))


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def pstdev(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.pstdev(values)


def stats_dict(values: Iterable[float]) -> dict[str, float | None]:
    collected = list(values)
    return {
        "min": min(collected) if collected else None,
        "q1": quantile(collected, 0.25),
        "median": median(collected),
        "mean": mean(collected),
        "q3": quantile(collected, 0.75),
        "max": max(collected) if collected else None,
        "std": pstdev(collected),
    }


def margin_stats_dict(rows: list[dict[str, object]]) -> dict[str, float | None]:
    return stats_dict(
        float(row["margin_to_theta"])
        for row in rows
        if row["margin_to_theta"] != ""
    )


def strength_stats_dict(rows: list[dict[str, object]]) -> dict[str, float | None]:
    return stats_dict(float(row["strength"]) for row in rows)


def theta_min_max(rows: list[dict[str, object]]) -> tuple[float | None, float | None]:
    theta_values = [float(row["theta_edge"]) for row in rows if row["theta_edge"] != ""]
    if not theta_values:
        return None, None
    return min(theta_values), max(theta_values)


def candidate_counts(rows: list[dict[str, object]]) -> tuple[int, int]:
    candidate_count = sum(1 for row in rows if int(row["edge_candidate_flag"]) == 1)
    return candidate_count, len(rows) - candidate_count


def profile_row_common(rows: list[dict[str, object]]) -> dict[str, str]:
    strength_stats = strength_stats_dict(rows)
    margin_stats = margin_stats_dict(rows)
    theta_min, theta_max = theta_min_max(rows)
    return {
        "strength_min": format_float(strength_stats["min"]),
        "strength_q1": format_float(strength_stats["q1"]),
        "strength_median": format_float(strength_stats["median"]),
        "strength_mean": format_float(strength_stats["mean"]),
        "strength_q3": format_float(strength_stats["q3"]),
        "strength_max": format_float(strength_stats["max"]),
        "strength_std": format_float(strength_stats["std"]),
        "theta_edge_min": format_float(theta_min),
        "theta_edge_max": format_float(theta_max),
        "margin_min": format_float(margin_stats["min"]),
        "margin_median": format_float(margin_stats["median"]),
        "margin_mean": format_float(margin_stats["mean"]),
        "margin_max": format_float(margin_stats["max"]),
    }


def threshold_row(profile_name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    strength_stats = strength_stats_dict(rows)
    margin_stats = margin_stats_dict(rows)
    theta_min, theta_max = theta_min_max(rows)
    margin_values = [float(row["margin_to_theta"]) for row in rows if row["margin_to_theta"] != ""]
    return {
        "profile_name": profile_name,
        "edge_rows": len(rows),
        "strength_min": format_float(strength_stats["min"]),
        "strength_median": format_float(strength_stats["median"]),
        "strength_mean": format_float(strength_stats["mean"]),
        "strength_max": format_float(strength_stats["max"]),
        "theta_edge_min": format_float(theta_min),
        "theta_edge_max": format_float(theta_max),
        "margin_min": format_float(margin_stats["min"]),
        "margin_median": format_float(margin_stats["median"]),
        "margin_mean": format_float(margin_stats["mean"]),
        "margin_max": format_float(margin_stats["max"]),
        "negative_margin_count": sum(1 for value in margin_values if value < 0),
        "zero_or_positive_margin_count": sum(1 for value in margin_values if value >= 0),
    }


def load_pair_semantics() -> dict[str, dict[str, object]]:
    semantics: dict[str, dict[str, object]] = {}
    for row in read_csv_rows(PAIR_SEMANTICS_SOURCE):
        pair_id = row["pair_id"]
        semantics[pair_id] = {
            "component_id": parse_int(row["component_id"]),
            "abs_delta": parse_int(row["abs_delta"]),
            "i": parse_int(row["i"]),
            "j": parse_int(row["j"]),
        }
    return semantics


def load_component_profiles() -> dict[int, dict[str, object]]:
    profiles: dict[int, dict[str, object]] = {}
    for row in read_csv_rows(COMPONENT_SEMANTICS_SOURCE):
        component_id = parse_int(row["component_id"])
        profiles[component_id] = {
            "component_size": parse_int(row["component_size"]),
            "dominant_abs_delta": parse_int(row["dominant_abs_delta"]),
        }
    return profiles


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    closure_summary = read_json(CLOSURE_SUMMARY_SOURCE)
    block_structure_summary = read_json(BLOCK_STRUCTURE_SUMMARY_SOURCE)
    block_semantics_summary = read_json(BLOCK_SEMANTICS_SUMMARY_SOURCE)
    if block_structure_summary.get("block_structure_status") != "complete_disjoint_clique_blocks_confirmed":
        raise ValueError("Prior block-structure audit is not confirmed")
    if block_semantics_summary.get("semantic_status") != "blocks_correspond_to_directed_pair_index_distance_classes":
        raise ValueError("Prior block-semantics audit is not confirmed")

    pair_semantics = load_pair_semantics()
    component_profiles = load_component_profiles()

    enriched_rows: list[dict[str, object]] = []
    parsing_gap_count = 0
    threshold_margin_available = True

    for row in read_csv_rows(SOURCE_EDGE_FILE):
        pair_a = row["pair_a"]
        pair_b = row["pair_b"]
        if pair_a not in pair_semantics or pair_b not in pair_semantics:
            parsing_gap_count += 1
            continue
        strength = parse_float(row["strength"])
        theta_edge = parse_float(row.get("theta_edge", ""))
        if strength is None:
            parsing_gap_count += 1
            continue
        if theta_edge is None:
            threshold_margin_available = False
        margin = strength - theta_edge if theta_edge is not None else None
        component_a = int(pair_semantics[pair_a]["component_id"])
        component_b = int(pair_semantics[pair_b]["component_id"])
        abs_delta_a = int(pair_semantics[pair_a]["abs_delta"])
        abs_delta_b = int(pair_semantics[pair_b]["abs_delta"])
        same_component = component_a == component_b
        enriched_rows.append(
            {
                "pair_a": pair_a,
                "pair_b": pair_b,
                "component_a": component_a,
                "component_b": component_b,
                "abs_delta_a": abs_delta_a,
                "abs_delta_b": abs_delta_b,
                "same_component": str(same_component).lower(),
                "relation_zone": (
                    "within_confirmed_block"
                    if same_component
                    else "between_confirmed_blocks"
                ),
                "strength": strength,
                "theta_edge": theta_edge if theta_edge is not None else "",
                "margin_to_theta": margin if margin is not None else "",
                "edge_candidate_flag": parse_int(row["edge_candidate_flag"]),
            }
        )

    enriched_rows.sort(
        key=lambda row: (
            str(row["relation_zone"]),
            int(row["component_a"]),
            int(row["component_b"]),
            pair_sort_key(str(row["pair_a"])),
            pair_sort_key(str(row["pair_b"])),
        )
    )

    enriched_output_rows = []
    for row in enriched_rows:
        enriched_output_rows.append(
            {
                **row,
                "strength": format_float(float(row["strength"])),
                "theta_edge": format_float(row["theta_edge"] if row["theta_edge"] != "" else None),
                "margin_to_theta": format_float(
                    row["margin_to_theta"] if row["margin_to_theta"] != "" else None
                ),
            }
        )

    write_csv(
        RUN_DIR / "05_edge_strength_enriched.csv",
        [
            "pair_a",
            "pair_b",
            "component_a",
            "component_b",
            "abs_delta_a",
            "abs_delta_b",
            "same_component",
            "relation_zone",
            "strength",
            "theta_edge",
            "margin_to_theta",
            "edge_candidate_flag",
        ],
        enriched_output_rows,
    )

    within_rows = [row for row in enriched_rows if row["relation_zone"] == "within_confirmed_block"]
    between_rows = [row for row in enriched_rows if row["relation_zone"] == "between_confirmed_blocks"]
    candidate_rows = [row for row in enriched_rows if int(row["edge_candidate_flag"]) == 1]
    non_candidate_rows = [row for row in enriched_rows if int(row["edge_candidate_flag"]) == 0]

    internal_profile_rows: list[dict[str, object]] = []
    internal_mean_by_component: dict[int, float] = {}
    for component_id in sorted(component_profiles):
        rows = [
            row
            for row in within_rows
            if int(row["component_a"]) == component_id and int(row["component_b"]) == component_id
        ]
        candidate_count, non_candidate_count = candidate_counts(rows)
        stats = profile_row_common(rows)
        internal_mean = strength_stats_dict(rows)["mean"]
        if internal_mean is not None:
            internal_mean_by_component[component_id] = internal_mean
        internal_profile_rows.append(
            {
                "component_id": component_id,
                "abs_delta": component_profiles[component_id]["dominant_abs_delta"],
                "component_size": component_profiles[component_id]["component_size"],
                "internal_edge_rows": len(rows),
                "candidate_edge_count": candidate_count,
                "non_candidate_edge_count": non_candidate_count,
                **stats,
                "all_internal_edges_are_candidates": str(non_candidate_count == 0).lower(),
            }
        )

    write_csv(
        RUN_DIR / "06_component_internal_strength_profile.csv",
        [
            "component_id",
            "abs_delta",
            "component_size",
            "internal_edge_rows",
            "candidate_edge_count",
            "non_candidate_edge_count",
            "strength_min",
            "strength_q1",
            "strength_median",
            "strength_mean",
            "strength_q3",
            "strength_max",
            "strength_std",
            "theta_edge_min",
            "theta_edge_max",
            "margin_min",
            "margin_median",
            "margin_mean",
            "margin_max",
            "all_internal_edges_are_candidates",
        ],
        internal_profile_rows,
    )

    cross_profile_rows: list[dict[str, object]] = []
    component_ids = sorted(component_profiles)
    for index, component_a in enumerate(component_ids):
        for component_b in component_ids[index + 1 :]:
            rows = [
                row
                for row in between_rows
                if {int(row["component_a"]), int(row["component_b"])}
                == {component_a, component_b}
            ]
            candidate_count, non_candidate_count = candidate_counts(rows)
            cross_profile_rows.append(
                {
                    "component_a": component_a,
                    "component_b": component_b,
                    "abs_delta_a": component_profiles[component_a]["dominant_abs_delta"],
                    "abs_delta_b": component_profiles[component_b]["dominant_abs_delta"],
                    "cross_edge_rows": len(rows),
                    "candidate_edge_count": candidate_count,
                    "non_candidate_edge_count": non_candidate_count,
                    **profile_row_common(rows),
                    "all_cross_edges_are_non_candidates": str(candidate_count == 0).lower(),
                }
            )

    write_csv(
        RUN_DIR / "07_cross_component_strength_profile.csv",
        [
            "component_a",
            "component_b",
            "abs_delta_a",
            "abs_delta_b",
            "cross_edge_rows",
            "candidate_edge_count",
            "non_candidate_edge_count",
            "strength_min",
            "strength_q1",
            "strength_median",
            "strength_mean",
            "strength_q3",
            "strength_max",
            "strength_std",
            "theta_edge_min",
            "theta_edge_max",
            "margin_min",
            "margin_median",
            "margin_mean",
            "margin_max",
            "all_cross_edges_are_non_candidates",
        ],
        cross_profile_rows,
    )

    abs_pair_groups: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)
    for row in enriched_rows:
        abs_a = int(row["abs_delta_a"])
        abs_b = int(row["abs_delta_b"])
        abs_pair_groups[tuple(sorted((abs_a, abs_b)))].append(row)

    abs_pair_profile_rows: list[dict[str, object]] = []
    for (abs_a, abs_b), rows in sorted(abs_pair_groups.items()):
        candidate_count, non_candidate_count = candidate_counts(rows)
        profile = profile_row_common(rows)
        abs_pair_profile_rows.append(
            {
                "abs_delta_a": abs_a,
                "abs_delta_b": abs_b,
                "edge_rows": len(rows),
                "candidate_edge_count": candidate_count,
                "non_candidate_edge_count": non_candidate_count,
                "strength_min": profile["strength_min"],
                "strength_q1": profile["strength_q1"],
                "strength_median": profile["strength_median"],
                "strength_mean": profile["strength_mean"],
                "strength_q3": profile["strength_q3"],
                "strength_max": profile["strength_max"],
                "strength_std": profile["strength_std"],
                "margin_min": profile["margin_min"],
                "margin_median": profile["margin_median"],
                "margin_mean": profile["margin_mean"],
                "margin_max": profile["margin_max"],
            }
        )

    write_csv(
        RUN_DIR / "08_strength_by_abs_delta_pair_profile.csv",
        [
            "abs_delta_a",
            "abs_delta_b",
            "edge_rows",
            "candidate_edge_count",
            "non_candidate_edge_count",
            "strength_min",
            "strength_q1",
            "strength_median",
            "strength_mean",
            "strength_q3",
            "strength_max",
            "strength_std",
            "margin_min",
            "margin_median",
            "margin_mean",
            "margin_max",
        ],
        abs_pair_profile_rows,
    )

    threshold_profile_rows = [
        threshold_row("within_confirmed_block", within_rows),
        threshold_row("between_confirmed_blocks", between_rows),
        threshold_row("candidate_edges", candidate_rows),
        threshold_row("non_candidate_edges", non_candidate_rows),
        threshold_row("within_confirmed_block__candidate_edges", [row for row in within_rows if int(row["edge_candidate_flag"]) == 1]),
        threshold_row("between_confirmed_blocks__non_candidate_edges", [row for row in between_rows if int(row["edge_candidate_flag"]) == 0]),
    ]
    write_csv(
        RUN_DIR / "09_threshold_margin_profile.csv",
        [
            "profile_name",
            "edge_rows",
            "strength_min",
            "strength_median",
            "strength_mean",
            "strength_max",
            "theta_edge_min",
            "theta_edge_max",
            "margin_min",
            "margin_median",
            "margin_mean",
            "margin_max",
            "negative_margin_count",
            "zero_or_positive_margin_count",
        ],
        threshold_profile_rows,
    )

    top_internal_rows = sorted(
        within_rows,
        key=lambda row: (
            -float(row["strength"]),
            int(row["component_a"]),
            pair_sort_key(str(row["pair_a"])),
            pair_sort_key(str(row["pair_b"])),
        ),
    )[:25]
    top_internal_output = []
    for rank, row in enumerate(top_internal_rows, start=1):
        top_internal_output.append(
            {
                "rank": rank,
                "pair_a": row["pair_a"],
                "pair_b": row["pair_b"],
                "component_a": row["component_a"],
                "abs_delta_a": row["abs_delta_a"],
                "strength": format_float(float(row["strength"])),
                "theta_edge": format_float(row["theta_edge"] if row["theta_edge"] != "" else None),
                "margin_to_theta": format_float(
                    row["margin_to_theta"] if row["margin_to_theta"] != "" else None
                ),
                "edge_candidate_flag": row["edge_candidate_flag"],
            }
        )
    write_csv(
        RUN_DIR / "10_top_internal_strength_edges.csv",
        [
            "rank",
            "pair_a",
            "pair_b",
            "component_a",
            "abs_delta_a",
            "strength",
            "theta_edge",
            "margin_to_theta",
            "edge_candidate_flag",
        ],
        top_internal_output,
    )

    top_cross_rows = sorted(
        between_rows,
        key=lambda row: (
            -float(row["strength"]),
            int(row["component_a"]),
            int(row["component_b"]),
            pair_sort_key(str(row["pair_a"])),
            pair_sort_key(str(row["pair_b"])),
        ),
    )[:25]
    top_cross_output = []
    for rank, row in enumerate(top_cross_rows, start=1):
        top_cross_output.append(
            {
                "rank": rank,
                "pair_a": row["pair_a"],
                "pair_b": row["pair_b"],
                "component_a": row["component_a"],
                "component_b": row["component_b"],
                "abs_delta_a": row["abs_delta_a"],
                "abs_delta_b": row["abs_delta_b"],
                "strength": format_float(float(row["strength"])),
                "theta_edge": format_float(row["theta_edge"] if row["theta_edge"] != "" else None),
                "margin_to_theta": format_float(
                    row["margin_to_theta"] if row["margin_to_theta"] != "" else None
                ),
                "edge_candidate_flag": row["edge_candidate_flag"],
            }
        )
    write_csv(
        RUN_DIR / "11_top_cross_block_strength_edges.csv",
        [
            "rank",
            "pair_a",
            "pair_b",
            "component_a",
            "component_b",
            "abs_delta_a",
            "abs_delta_b",
            "strength",
            "theta_edge",
            "margin_to_theta",
            "edge_candidate_flag",
        ],
        top_cross_output,
    )

    matrix_rows: list[dict[str, object]] = []
    for component_a in component_ids:
        matrix_row: dict[str, object] = {"component_id": component_a}
        for component_b in component_ids:
            if component_a <= component_b:
                rows = [
                    row
                    for row in enriched_rows
                    if {int(row["component_a"]), int(row["component_b"])}
                    == {component_a, component_b}
                    and (
                        component_a != component_b
                        or (
                            int(row["component_a"]) == component_a
                            and int(row["component_b"]) == component_b
                        )
                    )
                ]
                value = strength_stats_dict(rows)["mean"]
            else:
                value = None
            matrix_row[f"component_{component_b}_mean_strength"] = format_float(value)
        matrix_rows.append(matrix_row)
    write_csv(
        RUN_DIR / "13_component_internal_strength_matrix.csv",
        ["component_id"] + [f"component_{component_id}_mean_strength" for component_id in component_ids],
        matrix_rows,
    )

    candidate_edge_count, non_candidate_edge_count = candidate_counts(enriched_rows)
    within_candidate_count, within_non_candidate_count = candidate_counts(within_rows)
    between_candidate_count, between_non_candidate_count = candidate_counts(between_rows)
    all_within_block_edges_are_candidates = within_non_candidate_count == 0
    all_between_block_edges_are_non_candidates = between_candidate_count == 0
    global_strength_stats = strength_stats_dict(enriched_rows)
    within_strength_stats = strength_stats_dict(within_rows)
    between_strength_stats = strength_stats_dict(between_rows)
    within_margin_stats = margin_stats_dict(within_rows)
    between_margin_stats = margin_stats_dict(between_rows)
    internal_order = [
        {"component_id": component_id, "strength_mean": internal_mean_by_component[component_id]}
        for component_id in sorted(internal_mean_by_component, key=lambda cid: (-internal_mean_by_component[cid], cid))
    ]
    strongest_internal_component = internal_order[0]["component_id"] if internal_order else None
    weakest_internal_component = internal_order[-1]["component_id"] if internal_order else None
    top_cross_block_strength = float(top_cross_rows[0]["strength"]) if top_cross_rows else None
    top_cross_block_margin = (
        float(top_cross_rows[0]["margin_to_theta"])
        if top_cross_rows and top_cross_rows[0]["margin_to_theta"] != ""
        else None
    )

    summary_values_available = len(enriched_rows) > 0 and parsing_gap_count == 0
    strength_profile_status = (
        "strength_profile_consistent_with_confirmed_block_structure"
        if all_within_block_edges_are_candidates
        and all_between_block_edges_are_non_candidates
        and summary_values_available
        else "strength_profile_requires_review"
    )

    summary = {
        "run_id": RUN_ID,
        "source_edge_file": str(SOURCE_EDGE_FILE),
        "closure_summary_source": str(CLOSURE_SUMMARY_SOURCE),
        "block_structure_summary_source": str(BLOCK_STRUCTURE_SUMMARY_SOURCE),
        "block_semantics_summary_source": str(BLOCK_SEMANTICS_SUMMARY_SOURCE),
        "node_count": len(pair_semantics),
        "component_count": len(component_profiles),
        "component_sizes": [
            int(component_profiles[component_id]["component_size"])
            for component_id in component_ids
        ],
        "edge_rows_total": len(enriched_rows),
        "candidate_edge_count": candidate_edge_count,
        "non_candidate_edge_count": non_candidate_edge_count,
        "within_block_edge_rows": len(within_rows),
        "between_block_edge_rows": len(between_rows),
        "within_block_candidate_edge_count": within_candidate_count,
        "within_block_non_candidate_edge_count": within_non_candidate_count,
        "between_block_candidate_edge_count": between_candidate_count,
        "between_block_non_candidate_edge_count": between_non_candidate_count,
        "all_within_block_edges_are_candidates": all_within_block_edges_are_candidates,
        "all_between_block_edges_are_non_candidates": all_between_block_edges_are_non_candidates,
        "threshold_margin_available": threshold_margin_available,
        "parsing_gap_count": parsing_gap_count,
        "strength_global_min": global_strength_stats["min"],
        "strength_global_median": global_strength_stats["median"],
        "strength_global_mean": global_strength_stats["mean"],
        "strength_global_max": global_strength_stats["max"],
        "strength_within_min": within_strength_stats["min"],
        "strength_within_median": within_strength_stats["median"],
        "strength_within_mean": within_strength_stats["mean"],
        "strength_within_max": within_strength_stats["max"],
        "strength_between_min": between_strength_stats["min"],
        "strength_between_median": between_strength_stats["median"],
        "strength_between_mean": between_strength_stats["mean"],
        "strength_between_max": between_strength_stats["max"],
        "margin_within_min": within_margin_stats["min"],
        "margin_within_median": within_margin_stats["median"],
        "margin_within_mean": within_margin_stats["mean"],
        "margin_within_max": within_margin_stats["max"],
        "margin_between_min": between_margin_stats["min"],
        "margin_between_median": between_margin_stats["median"],
        "margin_between_mean": between_margin_stats["mean"],
        "margin_between_max": between_margin_stats["max"],
        "component_internal_strength_order_by_mean": internal_order,
        "strongest_internal_component": strongest_internal_component,
        "weakest_internal_component": weakest_internal_component,
        "top_cross_block_strength": top_cross_block_strength,
        "top_cross_block_margin": top_cross_block_margin,
        "strength_profile_status": strength_profile_status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_block_strength_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    review_note = f"""# QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE

## Source basis

This run uses the EXTRACT03 edge-candidate table and the confirmed closure, block-structure, and block-semantics audit summaries listed in `02_block_strength_profile_scope.md`.

## Method

Each edge row was enriched with component and Pair-ID distance-class metadata from the semantics audit. Rows were separated into `within_confirmed_block` and `between_confirmed_blocks`, then profiled by component, component pair, abs-delta pair, threshold-margin category, and strongest observed rows.

## Results

- Edge rows total: {summary["edge_rows_total"]}
- Candidate edge count: {summary["candidate_edge_count"]}
- Non-candidate edge count: {summary["non_candidate_edge_count"]}
- Within-block rows: {summary["within_block_edge_rows"]}
- Between-block rows: {summary["between_block_edge_rows"]}
- All within-block rows candidates: {summary["all_within_block_edges_are_candidates"]}
- All between-block rows non-candidates: {summary["all_between_block_edges_are_non_candidates"]}
- Strength profile status: `{summary["strength_profile_status"]}`

## Internal block strength profile

Within confirmed blocks, the observed strength range is {summary["strength_within_min"]} to {summary["strength_within_max"]}, with median {summary["strength_within_median"]} and mean {summary["strength_within_mean"]}. The internal components ordered by mean strength are recorded in `04_block_strength_summary.json`.

## Cross-block strength profile

Between confirmed blocks, the observed strength range is {summary["strength_between_min"]} to {summary["strength_between_max"]}, with median {summary["strength_between_median"]} and mean {summary["strength_between_mean"]}. The strongest cross-block row has strength {summary["top_cross_block_strength"]} and margin {summary["top_cross_block_margin"]}.

## Threshold-margin observations

Threshold margins are available for this run: {summary["threshold_margin_available"]}. Within-block margins range from {summary["margin_within_min"]} to {summary["margin_within_max"]}. Between-block margins range from {summary["margin_between_min"]} to {summary["margin_between_max"]}.

## Interpretation

This run numerically describes the edge weights of the already confirmed block structure. It checks whether candidate edges inside confirmed distance-class blocks can also be characterized as a weighted structure, and whether cross-block non-candidate edges lie near or below the threshold.

The result is descriptive only. It does not provide a physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Claim boundary

The `strength` values are treated only as numeric edge weights from the existing EXTRACT03 candidate logic. This note makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.

## Next-step gate

Any later use of these strength profiles should cite this run directory and keep the numeric descriptive claim boundary explicit. Further interpretation would require separate evidence and separate review.
"""
    (RUN_DIR / "12_block_strength_review_note.md").write_text(review_note, encoding="utf-8")

    if closure_summary.get("edge_candidate_rows_total") != len(enriched_rows):
        raise ValueError("Enriched edge row count differs from closure summary")
    if closure_summary.get("candidate_edge_count") != candidate_edge_count:
        raise ValueError("Candidate edge count differs from closure summary")
    if block_structure_summary.get("candidate_edge_count") != candidate_edge_count:
        raise ValueError("Candidate edge count differs from block-structure summary")
    if block_semantics_summary.get("node_count") != len(pair_semantics):
        raise ValueError("Node count differs from block-semantics summary")


if __name__ == "__main__":
    main()
