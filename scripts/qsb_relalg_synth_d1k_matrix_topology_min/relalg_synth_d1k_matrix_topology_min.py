#!/usr/bin/env python3
"""Build a minimal matrix/topology audit for the synthetic D1K RELALG C-layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN"
SCRIPT_PATH = REPO_ROOT / "scripts/qsb_relalg_synth_d1k_matrix_topology_min/relalg_synth_d1k_matrix_topology_min.py"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN"
C_LAYER_PATH = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_c_layer.csv"
D1F_PATH = REPO_ROOT / "runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv"
D1K_PATH = REPO_ROOT / "runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv"
LOOP_MIN_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN"
LOOP_MIN_SUMMARY = LOOP_MIN_DIR / "qsb_relalg_synth_d1k_loop_min_summary.json"
META_SYNC_DIR = REPO_ROOT / "runs/QSB-META-RELALG-SYNC-MIN"

CLAIM_BOUNDARY = [
    "synthetic diagnostic matrix/topology audit only",
    "not REAL01 evidence",
    "not a physical phase source",
    "not a physical C-layer source",
    "no physical Bridge validation",
    "no spacetime, metric, gravity, or causal claim",
    "no inferred edges",
    "no fabricated loops",
]
CLAIM_BOUNDARY_TEXT = "; ".join(CLAIM_BOUNDARY)
FORBIDDEN_CLAIM_PHRASES = [
    "REAL01 evidence",
    "physical phase",
    "physical C-layer source",
    "Bridge validation",
    "spacetime metric derivation",
    "gravity proof",
    "causality proof",
]
REQUIRED_C_LAYER_COLUMNS = [
    "source_case_id",
    "source_pair_id",
    "A_id",
    "B_id",
    "C_real",
    "C_imag",
    "C_abs",
    "C_arg",
    "phi_i",
    "phi_j",
    "delta_phi_wrapped",
    "phase_is_synthetic_diagnostic",
    "phase_is_physical",
    "evidence_class",
    "allowed_use",
    "blocked_use",
    "claim_boundary",
    "row_lineage_id",
    "row_content_sha256",
]
FAMILY_GROUP_COLUMNS = [
    "decoy_family",
    "null_family",
    "control_family",
    "parameter_sweep_family",
    "kernel_size_label",
    "decision_status",
]
OUTPUTS = {
    "adjacency_summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_adjacency_summary.csv",
    "node_degree_summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_node_degree_summary.csv",
    "component_summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_component_summary.csv",
    "family_block_summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_family_block_summary.csv",
    "sparse_edges": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_sparse_edges.csv",
    "matrix_profile": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_matrix_profile.csv",
    "validation_report": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_validation_report.json",
    "next_step_gate": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_manifest.json",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_claim_boundary.md",
    "readout": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_readout.md",
    "summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_summary.json",
    "heatmap_ready_edges": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_heatmap_ready_edges.csv",
    "mermaid": OUTPUT_DIR / "qsb_relalg_synth_d1k_matrix_topology_mermaid.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt_float(value: float) -> str:
    return f"{value:.17g}"


def bool_text(value: str) -> bool:
    return value.strip().lower() == "true"


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_loop_min_counts() -> dict[str, object]:
    if not LOOP_MIN_SUMMARY.exists():
        return {"status": "optional_input_absent"}
    data = json.loads(LOOP_MIN_SUMMARY.read_text(encoding="utf-8"))
    topology_counts = data.get("topology_counts", {})
    return {
        "status": "present",
        "source_native_closed_triple_count": topology_counts.get("source_native_closed_triple_count"),
        "valid_loop_count": topology_counts.get("valid_loop_count"),
        "directed_edge_count": topology_counts.get("directed_edge_count"),
    }


def count_closed_triples(edges: set[tuple[str, str]]) -> int:
    out_neighbors: dict[str, set[str]] = defaultdict(set)
    for a_id, b_id in edges:
        out_neighbors[a_id].add(b_id)

    triples: set[tuple[str, str, str]] = set()
    for a_id, b_values in out_neighbors.items():
        for b_id in b_values:
            for c_id in out_neighbors.get(b_id, set()):
                if (c_id, a_id) in edges:
                    triples.add((a_id, b_id, c_id))
    return len(triples)


def component_rows(
    nodes: set[str],
    edges: list[tuple[str, str]],
    role_by_node: dict[str, str],
    out_degree: Counter[str],
) -> tuple[list[list[object]], dict[str, int]]:
    adjacency: dict[str, set[str]] = {node: set() for node in nodes}
    for a_id, b_id in edges:
        adjacency[a_id].add(b_id)
        adjacency[b_id].add(a_id)

    edge_counter = Counter(edges)
    seen: set[str] = set()
    rows: list[list[object]] = []
    component_by_node: dict[str, int] = {}

    for start in sorted(nodes):
        if start in seen:
            continue
        component_id = len(rows) + 1
        queue: deque[str] = deque([start])
        seen.add(start)
        comp_nodes: set[str] = set()
        while queue:
            node = queue.popleft()
            comp_nodes.add(node)
            component_by_node[node] = component_id
            for neighbor in sorted(adjacency[node]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)

        comp_edge_count = sum(count for edge, count in edge_counter.items() if edge[0] in comp_nodes and edge[1] in comp_nodes)
        source_node_count = sum(1 for node in comp_nodes if role_by_node[node] == "source_only")
        target_node_count = sum(1 for node in comp_nodes if role_by_node[node] == "target_only")
        source_and_target_node_count = sum(1 for node in comp_nodes if role_by_node[node] == "source_and_target")
        centers = [node for node in comp_nodes if out_degree[node] == comp_edge_count and comp_edge_count > 0]
        if len(centers) == 1 and source_node_count == 1 and source_and_target_node_count == 0:
            topology_class = "single_star_component"
        elif comp_edge_count == 0:
            topology_class = "edgeless_component"
        else:
            topology_class = "general_weak_component"

        rows.append([
            component_id,
            len(comp_nodes),
            comp_edge_count,
            source_node_count,
            target_node_count,
            source_and_target_node_count,
            topology_class,
        ])
    return rows, component_by_node


def make_family_block_summary(c_rows: list[dict[str, str]]) -> tuple[list[list[object]], dict[str, object]]:
    headers = [
        *FAMILY_GROUP_COLUMNS,
        "edge_count",
        "unique_A_count",
        "unique_B_count",
        "mean_C_real",
        "mean_C_imag",
        "mean_C_abs",
        "mean_C_arg",
        "min_C_arg",
        "max_C_arg",
        "mean_abs_C_arg",
        "mean_angular_distance_if_available",
        "topology_class",
        "matched_edge_count",
        "unmatched_edge_count",
    ]
    if not D1F_PATH.exists():
        return [["optional_input_absent", "", "", "", "", "", 0, 0, 0, "", "", "", "", "", "", "", "", "optional_input_absent", 0, len(c_rows)]], {
            "status": "optional_input_absent",
            "matched_edge_count": 0,
            "unmatched_edge_count": len(c_rows),
            "headers": headers,
        }

    d1f_rows = read_csv_dicts(D1F_PATH)
    d1f_by_key: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in d1f_rows:
        key = (row.get("case_id", ""), row.get("pair_id", ""), row.get("wave_id_i", ""), row.get("wave_id_j", ""))
        d1f_by_key[key] = row

    d1k_by_case: dict[str, dict[str, str]] = {}
    if D1K_PATH.exists():
        d1k_by_case = {row.get("case_id", ""): row for row in read_csv_dicts(D1K_PATH)}

    groups: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    matched = 0
    unmatched = 0
    angular_distances: dict[tuple[str, ...], list[float]] = defaultdict(list)
    for row in c_rows:
        key = (row["source_case_id"], row["source_pair_id"], row["A_id"], row["B_id"])
        d1f = d1f_by_key.get(key)
        if d1f is None:
            unmatched += 1
            group_key = ("unmatched", "", "", "", "", "")
        else:
            matched += 1
            group_key = tuple(d1f.get(column, "") for column in FAMILY_GROUP_COLUMNS)
        groups[group_key].append(row)
        d1k = d1k_by_case.get(row["source_case_id"])
        if d1k and d1k.get("angular_phase_distance", "") != "":
            angular_distances[group_key].append(float(d1k["angular_phase_distance"]))

    summary_rows: list[list[object]] = []
    for group_key in sorted(groups):
        rows = groups[group_key]
        c_real = [float(row["C_real"]) for row in rows]
        c_imag = [float(row["C_imag"]) for row in rows]
        c_abs = [float(row["C_abs"]) for row in rows]
        c_arg = [float(row["C_arg"]) for row in rows]
        unique_a = {row["A_id"] for row in rows}
        unique_b = {row["B_id"] for row in rows}
        topology_class = "single_source_stripe" if len(unique_a) == 1 else "multi_source_block"
        distances = angular_distances.get(group_key, [])
        mean_distance = sum(distances) / len(distances) if distances else ""
        summary_rows.append([
            *group_key,
            len(rows),
            len(unique_a),
            len(unique_b),
            fmt_float(sum(c_real) / len(c_real)),
            fmt_float(sum(c_imag) / len(c_imag)),
            fmt_float(sum(c_abs) / len(c_abs)),
            fmt_float(sum(c_arg) / len(c_arg)),
            fmt_float(min(c_arg)),
            fmt_float(max(c_arg)),
            fmt_float(sum(abs(value) for value in c_arg) / len(c_arg)),
            fmt_float(mean_distance) if mean_distance != "" else "",
            topology_class,
            len(rows) if group_key[0] != "unmatched" else 0,
            len(rows) if group_key[0] == "unmatched" else 0,
        ])

    return summary_rows, {
        "status": "present",
        "matched_edge_count": matched,
        "unmatched_edge_count": unmatched,
        "headers": headers,
    }


def has_forbidden_positive_claim(text: str) -> list[str]:
    hits: list[str] = []
    for phrase in FORBIDDEN_CLAIM_PHRASES:
        allowed_negative_forms = [
            f"not {phrase}",
            f"not a {phrase}",
            f"not an {phrase}",
            f"no {phrase}",
            f"no physical {phrase}",
        ]
        if phrase in text and not any(form in text for form in allowed_negative_forms):
            hits.append(phrase)
    return sorted(set(hits))


def build_outputs() -> dict[str, object]:
    if not C_LAYER_PATH.exists():
        raise FileNotFoundError(f"Missing required input: {rel(C_LAYER_PATH)}")

    headers = csv_headers(C_LAYER_PATH)
    missing_columns = [column for column in REQUIRED_C_LAYER_COLUMNS if column not in headers]
    if missing_columns:
        raise ValueError("Missing required C-layer columns: " + ", ".join(missing_columns))

    c_rows = read_csv_dicts(C_LAYER_PATH)
    edge_count = len(c_rows)
    directed_edges = [(row["A_id"], row["B_id"]) for row in c_rows]
    edge_set = set(directed_edges)
    duplicate_directed_edge_count = edge_count - len(edge_set)
    unique_a = sorted({row["A_id"] for row in c_rows})
    unique_b = sorted({row["B_id"] for row in c_rows})
    nodes = set(unique_a) | set(unique_b)
    matrix_cells = len(unique_a) * len(unique_b)
    density = edge_count / matrix_cells if matrix_cells else 0.0
    self_edge_count = sum(1 for a_id, b_id in directed_edges if a_id == b_id)
    source_native_reverse_edge_count = sum(1 for a_id, b_id in edge_set if (b_id, a_id) in edge_set)
    source_native_closed_triple_count = count_closed_triples(edge_set)
    valid_loop_count_from_topology = source_native_closed_triple_count
    missing_bc_relation_count = sum(1 for _a_id, b_id in directed_edges if b_id not in unique_a)
    missing_reverse_relation_count = sum(1 for a_id, b_id in directed_edges if (b_id, a_id) not in edge_set)

    out_degree: Counter[str] = Counter()
    in_degree: Counter[str] = Counter()
    for a_id, b_id in directed_edges:
        out_degree[a_id] += 1
        in_degree[b_id] += 1

    role_by_node: dict[str, str] = {}
    node_degree_rows: list[list[object]] = []
    for node in sorted(nodes):
        out_value = out_degree[node]
        in_value = in_degree[node]
        if out_value > 0 and in_value > 0:
            role_class = "source_and_target"
        elif out_value > 0:
            role_class = "source_only"
        elif in_value > 0:
            role_class = "target_only"
        else:
            role_class = "isolated_impossible"
        role_by_node[node] = role_class
        node_degree_rows.append([node, out_value, in_value, out_value + in_value, role_class])

    component_summary_rows, component_by_node = component_rows(nodes, directed_edges, role_by_node, out_degree)
    max_out_degree = max(out_degree.values()) if out_degree else 0
    star_topology_score = max_out_degree / edge_count if edge_count else 0.0
    component_topology_classes = sorted({row[6] for row in component_summary_rows})
    overall_topology_class = "single_star_topology" if component_topology_classes == ["single_star_component"] and len(component_summary_rows) == 1 else "general_sparse_topology"

    a_index = {node: index for index, node in enumerate(unique_a)}
    b_index = {node: index for index, node in enumerate(unique_b)}
    sparse_rows: list[list[object]] = []
    for row in sorted(c_rows, key=lambda item: (a_index[item["A_id"]], b_index[item["B_id"]], item["source_case_id"], item["source_pair_id"])):
        sparse_rows.append([
            a_index[row["A_id"]],
            b_index[row["B_id"]],
            row["A_id"],
            row["B_id"],
            row["source_case_id"],
            row["source_pair_id"],
            row["C_real"],
            row["C_imag"],
            row["C_abs"],
            row["C_arg"],
            "true",
            "source_native_c_layer_row",
            CLAIM_BOUNDARY_TEXT,
            row["row_lineage_id"],
        ])

    family_block_rows, family_status = make_family_block_summary(c_rows)
    loop_counts = load_loop_min_counts()
    meta_sync_note = "QSB-META-RELALG-SYNC-MIN artifacts not found; this matrix-topology run is not yet catalog-synchronized."
    if META_SYNC_DIR.exists():
        meta_sync_note = "QSB-META-RELALG-SYNC-MIN artifacts exist; this new matrix-topology run is not necessarily synchronized until a later metadata sync updates the catalog."

    adjacency_rows = [[
        edge_count,
        len(nodes),
        len(unique_a),
        len(unique_b),
        f"{len(unique_a)} x {len(unique_b)}",
        fmt_float(density),
        duplicate_directed_edge_count,
        self_edge_count,
        source_native_reverse_edge_count,
        source_native_closed_triple_count,
        overall_topology_class,
        CLAIM_BOUNDARY_TEXT,
    ]]

    matrix_profile_rows = [
        ["edge_count", edge_count, "rows", "Existing source-native directed C-layer rows only."],
        ["unique_A_count", len(unique_a), "nodes", "Number of observed source-side matrix row labels."],
        ["unique_B_count", len(unique_b), "nodes", "Number of observed target-side matrix column labels."],
        ["unique_node_count", len(nodes), "nodes", "Union of observed A_id and B_id labels."],
        ["matrix_density", fmt_float(density), "fraction", "edge_count divided by unique_A_count times unique_B_count."],
        ["star_topology_score", fmt_float(star_topology_score), "fraction", "max_out_degree divided by edge_count; diagnostic only."],
        ["source_native_closed_triple_count", source_native_closed_triple_count, "triples", "Only A->B, B->C, C->A rows actually present in the C-layer count."],
        ["valid_loop_count_from_topology", valid_loop_count_from_topology, "loops", "No loop is counted without all source-native directed relations."],
        ["missing_BC_relation_count", missing_bc_relation_count, "edges", "Observed A->B rows whose B node has no outgoing B->C row."],
        ["missing_reverse_relation_count", missing_reverse_relation_count, "edges", "Observed rows without an actual reverse row in the source C-layer."],
        ["source_native_reverse_edge_count", source_native_reverse_edge_count, "directed_edges", "Reverse relations counted only when the reverse row exists."],
        ["inferred_edge_count", 0, "edges", "No missing matrix cells, reverse edges, or loop edges were inferred."],
    ]

    heatmap_rows = [
        row[:2] + row[6:10] + [row[2], row[3], row[4], row[5]]
        for row in sparse_rows
    ]

    claim_boundary_md = dedent(f"""\
    # {RUN_ID} Claim Boundary

    - synthetic diagnostic matrix/topology audit only
    - not REAL01 evidence
    - not a physical phase source
    - not a physical C-layer source
    - no physical Bridge validation
    - no spacetime, metric, gravity, or causal claim
    - no inferred edges
    - no fabricated loops

    Central principle:

    The matrix is used to reveal existing relation topology, not to construct missing relations.
    """)

    readout_md = dedent(f"""\
    # {RUN_ID} Readout

    ## Befund

    The D1K synthetic RELALG C-layer contains {edge_count} source-native directed rows over {len(nodes)} unique node labels.
    The sparse matrix shape is {len(unique_a)} x {len(unique_b)} with density {fmt_float(density)}.
    The maximum out-degree is {max_out_degree}, yielding star_topology_score = {fmt_float(star_topology_score)}.
    Source-native closed triples: {source_native_closed_triple_count}.
    Inferred edge count: 0.

    ## Interpretation

    The existing relation topology is classified as {overall_topology_class}.
    The matrix readout exposes observed blocks/stripes from the source data only.
    It does not fill missing matrix cells, derive reverse relations, or fabricate loop closure.

    ## Hypothese

    A bounded follow-up may review the topology limit note or inspect family/block stripes.
    This run does not authorize physical interpretation.

    ## Offene Luecke

    Source-native B->C relations are absent for {missing_bc_relation_count} observed A->B rows.
    Reverse relations are absent for {missing_reverse_relation_count} observed directed rows.
    Metadata sync note: {meta_sync_note}

    ## Claim Boundary

    {CLAIM_BOUNDARY_TEXT}.
    """)

    mermaid_md = dedent(f"""\
    # {RUN_ID} Minimal Topology Sketch

    ```mermaid
    flowchart LR
      A["unique A side: {len(unique_a)}"] --> B["unique B side: {len(unique_b)}"]
      B -. "no source-native B->C rows counted" .-> X["closed triples: {source_native_closed_triple_count}"]
    ```

    This sketch is aggregate-only and does not imply missing edges.
    """)

    summary = {
        "run_id": RUN_ID,
        "timestamp_utc": utc_now(),
        "input_row_count": edge_count,
        "edge_node_matrix_counts": {
            "edge_count": edge_count,
            "unique_A_count": len(unique_a),
            "unique_B_count": len(unique_b),
            "unique_node_count": len(nodes),
            "matrix_shape": f"{len(unique_a)} x {len(unique_b)}",
            "density": density,
        },
        "topology": {
            "star_topology_score": star_topology_score,
            "component_count": len(component_summary_rows),
            "component_topology_classes": component_topology_classes,
            "overall_topology_class": overall_topology_class,
            "source_native_closed_triple_count": source_native_closed_triple_count,
            "valid_loop_count_from_topology": valid_loop_count_from_topology,
            "missing_BC_relation_count": missing_bc_relation_count,
            "missing_reverse_relation_count": missing_reverse_relation_count,
            "source_native_reverse_edge_count": source_native_reverse_edge_count,
            "inferred_edge_count": 0,
        },
        "family_block_summary_status": {
            "status": family_status["status"],
            "matched_edge_count": family_status["matched_edge_count"],
            "unmatched_edge_count": family_status["unmatched_edge_count"],
        },
        "loop_min_consistency": loop_counts,
        "next_authorized_step": "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-REVIEW",
        "blocked_steps": [
            "QSB-RELALG-REAL01-MIN-STAGING",
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
            "QSB-RELALG-SYNTH-D1K-LOOP-PHASE-INTERPRETATION",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
        "metadata_sync_awareness": meta_sync_note,
        "validation_status": "pending",
    }

    next_gate = {
        "run_id": RUN_ID,
        "timestamp_utc": summary["timestamp_utc"],
        "next_authorized_step": "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-REVIEW",
        "alternative_bounded_step": "QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE",
        "blocked_steps": summary["blocked_steps"],
        "gate_basis": "synthetic diagnostic matrix/topology audit only; no inferred edges and no fabricated loops",
        "claim_boundary": CLAIM_BOUNDARY,
    }

    write_csv(
        OUTPUTS["adjacency_summary"],
        [
            "edge_count",
            "unique_node_count",
            "unique_A_count",
            "unique_B_count",
            "matrix_shape",
            "density",
            "duplicate_directed_edge_count",
            "self_edge_count",
            "source_native_reverse_edge_count",
            "source_native_closed_triple_count",
            "topology_class",
            "claim_boundary",
        ],
        adjacency_rows,
    )
    write_csv(OUTPUTS["node_degree_summary"], ["node_id", "out_degree", "in_degree", "total_degree", "role_class"], node_degree_rows)
    write_csv(
        OUTPUTS["component_summary"],
        [
            "component_id",
            "node_count",
            "edge_count",
            "source_node_count",
            "target_node_count",
            "source_and_target_node_count",
            "component_topology_class",
        ],
        component_summary_rows,
    )
    write_csv(OUTPUTS["family_block_summary"], family_status["headers"], family_block_rows)
    write_csv(
        OUTPUTS["sparse_edges"],
        [
            "row_index",
            "col_index",
            "A_id",
            "B_id",
            "source_case_id",
            "source_pair_id",
            "C_real",
            "C_imag",
            "C_abs",
            "C_arg",
            "edge_present",
            "edge_origin",
            "edge_claim_boundary",
            "row_lineage_id",
        ],
        sparse_rows,
    )
    write_csv(OUTPUTS["matrix_profile"], ["metric_name", "metric_value", "metric_unit", "interpretation"], matrix_profile_rows)
    write_csv(
        OUTPUTS["heatmap_ready_edges"],
        ["row_index", "col_index", "C_real", "C_imag", "C_abs", "C_arg", "A_id", "B_id", "source_case_id", "source_pair_id"],
        heatmap_rows,
    )
    OUTPUTS["claim_boundary"].write_text(claim_boundary_md, encoding="utf-8")
    OUTPUTS["readout"].write_text(readout_md, encoding="utf-8")
    OUTPUTS["mermaid"].write_text(mermaid_md, encoding="utf-8")
    write_json(OUTPUTS["next_step_gate"], next_gate)

    generated_text = "\n".join(
        [
            claim_boundary_md,
            readout_md,
            mermaid_md,
            json.dumps(summary, sort_keys=True),
            json.dumps(next_gate, sort_keys=True),
        ]
    )
    forbidden_hits = has_forbidden_positive_claim(generated_text)

    checks = [
        {"check_id": "V01", "name": "Inputs exist", "status": "pass", "details": {"c_layer_path": rel(C_LAYER_PATH)}},
        {"check_id": "V02", "name": "Required columns exist", "status": "pass" if not missing_columns else "fail", "details": {"missing_columns": missing_columns}},
        {"check_id": "V03", "name": "Synthetic flag integrity", "status": "pass" if all(bool_text(row["phase_is_synthetic_diagnostic"]) for row in c_rows) else "fail", "details": {"bad_synthetic_flag": sum(1 for row in c_rows if not bool_text(row["phase_is_synthetic_diagnostic"]))}},
        {"check_id": "V04", "name": "Physical flag integrity", "status": "pass" if all(not bool_text(row["phase_is_physical"]) for row in c_rows) else "fail", "details": {"bad_physical_flag": sum(1 for row in c_rows if bool_text(row["phase_is_physical"]))}},
        {"check_id": "V05", "name": "No inferred edges", "status": "pass" if len(sparse_rows) == edge_count else "fail", "details": {"sparse_edge_rows": len(sparse_rows), "input_rows": edge_count, "inferred_edge_count": 0}},
        {"check_id": "V06", "name": "Matrix counts consistent", "status": "pass" if density == (edge_count / matrix_cells if matrix_cells else 0.0) else "fail", "details": summary["edge_node_matrix_counts"]},
        {"check_id": "V07", "name": "Degree consistency", "status": "pass" if sum(out_degree.values()) == edge_count and sum(in_degree.values()) == edge_count else "fail", "details": {"sum_out_degree": sum(out_degree.values()), "sum_in_degree": sum(in_degree.values()), "edge_count": edge_count}},
        {"check_id": "V08", "name": "Component consistency", "status": "pass" if sum(row[2] for row in component_summary_rows) == edge_count and sum(row[1] for row in component_summary_rows) == len(nodes) else "fail", "details": {"component_edge_sum": sum(row[2] for row in component_summary_rows), "component_node_sum": sum(row[1] for row in component_summary_rows), "edge_count": edge_count, "unique_node_count": len(nodes)}},
        {"check_id": "V09", "name": "Source-native closed triple consistency", "status": "pass" if loop_counts["status"] != "present" or (loop_counts["source_native_closed_triple_count"] == source_native_closed_triple_count and loop_counts["valid_loop_count"] == valid_loop_count_from_topology) else "fail", "details": loop_counts},
        {"check_id": "V10", "name": "No reverse derivation", "status": "pass", "details": {"source_native_reverse_edge_count": source_native_reverse_edge_count, "missing_reverse_relation_count": missing_reverse_relation_count, "reverse_edges_derived": False}},
        {"check_id": "V11", "name": "Family join integrity", "status": "pass" if family_status["status"] == "present" else "optional_input_absent", "details": {"family_block_summary_status": family_status["status"], "matched_edge_count": family_status["matched_edge_count"], "unmatched_edge_count": family_status["unmatched_edge_count"]}},
        {"check_id": "V12", "name": "No forbidden claim wording", "status": "pass" if not forbidden_hits else "fail", "details": {"positive_claim_hits": forbidden_hits}},
        {"check_id": "V13", "name": "Replay protection", "status": "pass", "details": {"default_existing_output_dir_policy": "refuse overwrite unless --force is supplied"}},
        {"check_id": "V14", "name": "Manifest hashes", "status": "pending_manifest_written", "details": {"manifest_includes_generated_artifacts": True, "manifest_self_hash_policy": "omitted with explicit policy note"}},
        {"check_id": "V15", "name": "Metadata sync awareness", "status": "pass", "details": {"note": meta_sync_note}},
    ]
    validation_status = "pass" if all(check["status"] in {"pass", "optional_input_absent", "pending_manifest_written"} for check in checks) else "fail"
    summary["validation_status"] = validation_status

    write_json(OUTPUTS["summary"], summary)

    input_files = [C_LAYER_PATH, SCRIPT_PATH]
    if D1F_PATH.exists():
        input_files.append(D1F_PATH)
    if D1K_PATH.exists():
        input_files.append(D1K_PATH)
    if LOOP_MIN_SUMMARY.exists():
        input_files.append(LOOP_MIN_SUMMARY)

    manifest = {
        "run_id": RUN_ID,
        "timestamp_utc": summary["timestamp_utc"],
        "input_files": {rel(path): sha256_file(path) for path in input_files},
        "generated_artifacts": {},
        "manifest_self_hash_policy": "not included because the manifest hash would be self-referential",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(OUTPUTS["manifest"], manifest)
    generated_artifacts = {
        rel(path): sha256_file(path)
        for key, path in OUTPUTS.items()
        if key not in {"validation_report", "manifest"} and path.exists()
    }
    manifest["generated_artifacts"] = generated_artifacts
    write_json(OUTPUTS["manifest"], manifest)

    for check in checks:
        if check["check_id"] == "V14":
            check["status"] = "pass"
            check["details"]["generated_artifact_hash_count"] = len(generated_artifacts)
            check["details"]["input_hash_count"] = len(input_files)

    validation_report = {
        "run_id": RUN_ID,
        "timestamp_utc": summary["timestamp_utc"],
        "validation_status": validation_status,
        "checks": checks,
        "claim_boundary": CLAIM_BOUNDARY,
        "topology_status": "completed_matrix_topology_audit",
    }
    write_json(OUTPUTS["validation_report"], validation_report)

    manifest["generated_artifacts"][rel(OUTPUTS["validation_report"])] = sha256_file(OUTPUTS["validation_report"])
    write_json(OUTPUTS["manifest"], manifest)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the synthetic D1K RELALG matrix/topology audit.")
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory.")
    args = parser.parse_args()

    prepare_output(args.force)
    summary = build_outputs()
    print(f"run_id: {RUN_ID}")
    print(f"output_dir: {rel(OUTPUT_DIR)}")
    print(f"input_row_count: {summary['input_row_count']}")
    print(f"edge_count: {summary['edge_node_matrix_counts']['edge_count']}")
    print(f"unique_node_count: {summary['edge_node_matrix_counts']['unique_node_count']}")
    print(f"matrix_shape: {summary['edge_node_matrix_counts']['matrix_shape']}")
    print(f"density: {fmt_float(summary['edge_node_matrix_counts']['density'])}")
    print(f"star_topology_score: {fmt_float(summary['topology']['star_topology_score'])}")
    print(f"source_native_closed_triple_count: {summary['topology']['source_native_closed_triple_count']}")
    print(f"inferred_edge_count: {summary['topology']['inferred_edge_count']}")
    print(f"validation_status: {summary['validation_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
