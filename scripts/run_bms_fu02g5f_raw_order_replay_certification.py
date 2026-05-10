#!/usr/bin/env python3
"""
BMS-FU02g5f - Raw-Order Replay Certification and Candidate_005 Deep Inspection

This method/control runner revalidates FU02g5e1/FU02g5e2 candidates against the
repaired C60 face graph and records raw-order certification fields. It does not
re-use the original FU02g4c enumerator/input bundle, so the raw-order replay
certification status is not_certified.

Claim boundary: combinatorial/methodological audit only. No physical emergence,
spacetime emergence, global uniqueness, or global rarity claim is made.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: PyYAML. Install it in the project environment.") from exc


Graph = Dict[str, Set[str]]
Edge = Tuple[str, str]

RAW_ORDER_NOT_CERTIFIED_BASIS = (
    "This FU02g5f runner revalidates scaffold-localized candidates but does not "
    "re-use the original FU02g4c enumerator and input bundle."
)
SCAFFOLD_ORDER_WARNING = (
    "g5e1/g5e2 scaffold order is a localization aid only and is not a certified "
    "FU02g4c raw-order replay."
)

CANDIDATE_REVALIDATION_FIELDS = [
    "candidate_id",
    "window_id",
    "raw_index",
    "candidate_nodes",
    "candidate_node_count",
    "candidate_node_count_expected",
    "candidate_node_count_ok",
    "candidate_edge_count",
    "source_internal_edge_count",
    "candidate_edge_count_ok",
    "candidate_connected",
    "source_candidate_connected",
    "h_count",
    "p_count",
    "source_h_count",
    "source_p_count",
    "uncolored_isomorphic_to_reference",
    "face_type_preserving_isomorphic_to_reference",
    "mapping_count",
    "g5e2_uncolored_isomorphic_to_reference",
    "g5e2_face_type_preserving_isomorphic_to_reference",
    "g5e2_mapping_count",
    "exact_match",
    "near_distance",
    "classification_primary",
    "decision_basis",
    "raw_order_certification_status",
    "raw_order_certification_basis",
    "fu02g4c_order_guarantee",
    "scaffold_order_warning",
    "warnings",
]

NODE_DIFF_FIELDS = ["node", "diff_class", "face_type"]
EDGE_DIFF_FIELDS = ["edge_key", "node_a", "node_b", "diff_class"]

DEEP_INSPECTION_FIELDS = [
    "candidate_id",
    "raw_index",
    "candidate_nodes",
    "known_exact_candidate_nodes",
    "nodes_only_in_candidate_005",
    "nodes_only_in_known_exact_candidate",
    "candidate_005_edge_count",
    "known_exact_edge_count",
    "edges_only_in_candidate_005",
    "edges_only_in_known_exact_candidate",
    "candidate_005_degree_histogram",
    "known_exact_degree_histogram",
    "candidate_005_face_type_counts",
    "known_exact_face_type_counts",
    "candidate_005_carrier_signature",
    "known_exact_carrier_signature",
    "carrier_signature_equal",
    "candidate_005_role_colored_signature",
    "known_exact_role_colored_signature",
    "role_colored_signature_equal",
    "common_coarse_signature_components",
    "different_coarse_signature_components",
    "exact_match",
    "near_distance",
    "uncolored_isomorphic_to_reference",
    "face_type_preserving_isomorphic_to_reference",
    "mapping_count",
    "coarse_signature_degeneracy_case",
    "near_distance_zero_explanation",
    "raw_order_certification_status",
    "raw_order_certification_basis",
    "fu02g4c_order_guarantee",
    "scaffold_order_warning",
]

ISOMORPHISM_AUDIT_FIELDS = [
    "candidate_id",
    "raw_index",
    "candidate_node_count",
    "candidate_edge_count",
    "candidate_connected",
    "uncolored_isomorphic_to_reference",
    "face_type_preserving_isomorphic_to_reference",
    "mapping_count",
    "g5e2_agrees_uncolored",
    "g5e2_agrees_face_type_preserving",
    "g5e2_agrees_mapping_count",
    "audit_note",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMS-FU02g5f raw-order replay certification audit."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5f_raw_order_replay_certification_config.yaml",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must contain a mapping: {path}")
    return data


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root / path


def face_type(node: str) -> str:
    if node.startswith("H_"):
        return "H"
    if node.startswith("P_"):
        return "P"
    return "unknown"


def sorted_nodes(nodes: Iterable[str]) -> List[str]:
    return sorted(str(node) for node in nodes)


def set_key(nodes: Iterable[str]) -> str:
    return ";".join(sorted_nodes(nodes))


def edge_key(edge: Edge) -> str:
    return f"{edge[0]}--{edge[1]}"


def parse_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    if text == "":
        return None
    raise ValueError(f"Cannot parse boolean value: {value!r}")


def parse_int(value: Any, field: str) -> Optional[int]:
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(str(value).strip())
    except ValueError as exc:
        raise ValueError(f"Cannot parse integer field {field}: {value!r}") from exc


def parse_node_list(value: Any) -> List[str]:
    if isinstance(value, list):
        raw_nodes = [str(node).strip() for node in value]
    else:
        raw_nodes = [part.strip() for part in str(value).split(";")]
    return sorted(node for node in raw_nodes if node)


def read_face_edge_csv(path: Path) -> Graph:
    if not path.exists():
        raise FileNotFoundError(f"Face adjacency CSV not found: {path}")
    graph: Graph = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        missing = {"face_a", "face_b"} - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV must contain face_a / face_b; missing {sorted(missing)}")
        for row in reader:
            face_a = str(row["face_a"]).strip()
            face_b = str(row["face_b"]).strip()
            if not face_a or not face_b:
                continue
            graph.setdefault(face_a, set()).add(face_b)
            graph.setdefault(face_b, set()).add(face_a)
    return graph


def read_csv_rows(path: Path, required: Set[str]) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"CSV missing required columns {sorted(missing)}: {path}")
        return [{key: "" if value is None else str(value) for key, value in row.items()} for row in reader]


def induced_subgraph(graph: Graph, nodes: Sequence[str]) -> Graph:
    node_set = set(nodes)
    return {
        node: {neighbor for neighbor in graph.get(node, set()) if neighbor in node_set}
        for node in sorted_nodes(node_set)
    }


def edge_set(graph: Graph) -> Set[Edge]:
    edges: Set[Edge] = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edges.add(tuple(sorted((node, neighbor))))
    return edges


def edge_count(graph: Graph) -> int:
    return len(edge_set(graph))


def is_connected(graph: Graph) -> bool:
    if not graph:
        return False
    start = next(iter(graph))
    seen = {start}
    stack = [start]
    while stack:
        node = stack.pop()
        for neighbor in graph.get(node, set()):
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(graph)


def degree_histogram(graph: Graph) -> Dict[str, int]:
    return {str(degree): count for degree, count in sorted(Counter(len(v) for v in graph.values()).items())}


def face_type_counts(nodes: Iterable[str]) -> Dict[str, int]:
    return dict(sorted(Counter(face_type(node) for node in nodes).items()))


def validate_nodes(graph: Graph, nodes: Sequence[str], label: str) -> List[str]:
    warnings: List[str] = []
    counts = Counter(nodes)
    duplicates = sorted(node for node, count in counts.items() if count > 1)
    if duplicates:
        warnings.append(f"{label}: duplicate nodes: {duplicates}")
    missing = sorted(set(nodes) - set(graph))
    if missing:
        warnings.append(f"{label}: nodes missing from full graph: {missing}")
    return warnings


def enumerate_isomorphisms(
    reference_subgraph: Graph,
    candidate_subgraph: Graph,
    preserve_face_type: bool,
    stop_after_first: bool = False,
) -> List[Dict[str, str]]:
    if len(reference_subgraph) != len(candidate_subgraph):
        return []
    if edge_count(reference_subgraph) != edge_count(candidate_subgraph):
        return []

    ref_degrees = {node: len(neighbors) for node, neighbors in reference_subgraph.items()}
    cand_degrees = {node: len(neighbors) for node, neighbors in candidate_subgraph.items()}
    if Counter(ref_degrees.values()) != Counter(cand_degrees.values()):
        return []

    if preserve_face_type:
        ref_type_degree_hist = Counter((face_type(node), degree) for node, degree in ref_degrees.items())
        cand_type_degree_hist = Counter((face_type(node), degree) for node, degree in cand_degrees.items())
        if ref_type_degree_hist != cand_type_degree_hist:
            return []

    reference_nodes = sorted(reference_subgraph, key=lambda node: (-ref_degrees[node], face_type(node), node))
    candidate_nodes = sorted(candidate_subgraph)
    candidates_by_ref: Dict[str, List[str]] = {}
    for ref_node in reference_nodes:
        options = [
            cand_node
            for cand_node in candidate_nodes
            if cand_degrees[cand_node] == ref_degrees[ref_node]
            and (not preserve_face_type or face_type(cand_node) == face_type(ref_node))
        ]
        if not options:
            return []
        candidates_by_ref[ref_node] = options

    mappings: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    used_candidates: Set[str] = set()

    def compatible(ref_node: str, cand_node: str) -> bool:
        for mapped_ref, mapped_cand in current.items():
            ref_adjacent = mapped_ref in reference_subgraph[ref_node]
            cand_adjacent = mapped_cand in candidate_subgraph[cand_node]
            if ref_adjacent != cand_adjacent:
                return False
        return True

    def backtrack(position: int) -> bool:
        if position == len(reference_nodes):
            mappings.append(dict(current))
            return stop_after_first

        ref_node = reference_nodes[position]
        for cand_node in candidates_by_ref[ref_node]:
            if cand_node in used_candidates or not compatible(ref_node, cand_node):
                continue
            current[ref_node] = cand_node
            used_candidates.add(cand_node)
            should_stop = backtrack(position + 1)
            used_candidates.remove(cand_node)
            del current[ref_node]
            if should_stop:
                return True
        return False

    backtrack(0)
    return mappings


def parse_signature(signature: str) -> Dict[str, str]:
    components: Dict[str, str] = {}
    for part in str(signature).split("|"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        components[key.strip()] = value.strip()
    return components


def compare_signature_components(left: str, right: str) -> Tuple[List[str], List[str]]:
    left_components = parse_signature(left)
    right_components = parse_signature(right)
    common: List[str] = []
    different: List[str] = []
    for key in sorted(set(left_components) | set(right_components)):
        left_value = left_components.get(key, "<missing>")
        right_value = right_components.get(key, "<missing>")
        component = f"{key}={left_value}"
        if left_value == right_value:
            common.append(component)
        else:
            different.append(f"{key}: candidate_005={left_value}; known_exact={right_value}")
    return common, different


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, sort_keys=True)
    return value


def write_csv(path: Path, rows: Iterable[Mapping[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


def raw_order_fields(reuses_original_bundle: bool) -> Dict[str, str]:
    if reuses_original_bundle:
        return {
            "raw_order_certification_status": "certified",
            "raw_order_certification_basis": "Configured as reusing the original FU02g4c enumerator/input bundle.",
            "fu02g4c_order_guarantee": "true",
            "scaffold_order_warning": "",
        }
    return {
        "raw_order_certification_status": "not_certified",
        "raw_order_certification_basis": RAW_ORDER_NOT_CERTIFIED_BASIS,
        "fu02g4c_order_guarantee": "false",
        "scaffold_order_warning": SCAFFOLD_ORDER_WARNING,
    }


def decision_basis(
    exact_match: Optional[bool],
    near_distance: Optional[int],
    uncolored_iso: bool,
    typed_iso: bool,
    raw_status: str,
) -> str:
    parts = [
        f"exact_match={exact_match}",
        f"near_distance={near_distance} (coarse diagnostic)",
        f"uncolored_isomorphic={uncolored_iso}",
        f"face_type_preserving_isomorphic={typed_iso}",
        f"raw_order_certification={raw_status}",
    ]
    if near_distance == 0 and (not exact_match or not typed_iso):
        parts.append("near_distance=0 is not exact identity or isomorphism")
    return "; ".join(parts)


def build_result_note(summary: Mapping[str, Any]) -> str:
    created = str(summary["metadata"]["created_at_utc"])[:10]
    raw = summary["raw_order_certification"]
    c005 = summary["candidate_005"]
    counts = summary["candidate_counts"]

    return f"""# BMS-FU02g5f - Raw-Order Replay Certification Result Note

Datum: {created}

## Befund

FU02g5f revalidiert {counts["candidate_count"]} Near-Match-Kandidaten aus
FU02g5e1/FU02g5e2 gegen den reparierten C60-Face-Graphen.

Raw-order replay certification was not achieved.

```text
raw_order_certification_status = {raw["raw_order_certification_status"]}
fu02g4c_order_guarantee = {raw["fu02g4c_order_guarantee"]}
candidate_005_raw_index = {c005["raw_index"]}
candidate_005_exact_match = {c005["exact_match"]}
candidate_005_near_distance = {c005["near_distance"]}
candidate_005_uncolored_isomorphic_to_reference = {c005["uncolored_isomorphic_to_reference"]}
candidate_005_face_type_preserving_isomorphic_to_reference = {c005["face_type_preserving_isomorphic_to_reference"]}
```

## Interpretation

Candidate_005 is treated as a coarse-signature degeneracy case:
`near_distance=0` occurs together with `exact_match=False`,
`uncolored_isomorphic_to_reference=False`, and
`face_type_preserving_isomorphic_to_reference=False`.

Therefore, `near_distance=0` is not equivalent to exact match or isomorphism.
It is a coarse diagnostic over selected signature components, not an identity
test for node sets, edge sets, or graph isomorphism.

Role transport remains governed by the FU02g5c automorphy-only rule. Non-
isomorphic near candidates do not receive transported reference roles.

## Hypothese

The candidate_005 case indicates that the coarse signature used by FU02g5e1 can
collapse distinct induced subgraphs into the same near-distance class. This is a
diagnostic stress case for the scaffold-localization filter, not evidence for a
new physical or structural claim.

## Offene Luecke

Exact FU02g4c raw-order replay cannot be certified by this runner. The reason is
explicit:

```text
{raw["raw_order_certification_basis"]}
```

Certification would require a replay that reuses the original FU02g4c
enumerator/input bundle with a documented order guarantee.

## Claim Boundary

Sauber behauptbar ist nur ein kombinatorisch-methodischer Audit der
FU02g5e1/FU02g5e2 candidates and a deep inspection of candidate_005.

Nicht behaupten:

```text
physical emergence
spacetime emergence
global uniqueness
global rarity
FU02g4c raw-order replay certification
role transport outside the FU02g5c automorphy-only rule
```
"""


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    config_path = resolve_path(repo_root, args.config)
    config = load_yaml(config_path)

    run_config = config["run"]
    input_config = config["input"]
    output_dir = resolve_path(repo_root, str(run_config["output_dir"]))
    output_dir.mkdir(parents=True, exist_ok=True)

    graph_path = resolve_path(repo_root, str(input_config["full_face_graph_edges_csv"]))
    candidates_path = resolve_path(repo_root, str(input_config["near_match_candidates_csv"]))
    classifications_path = resolve_path(repo_root, str(input_config["candidate_classification_csv"]))

    graph = read_face_edge_csv(graph_path)
    candidate_rows = read_csv_rows(
        candidates_path,
        {"window_id", "raw_index", "candidate_nodes", "exact_match", "near_distance"},
    )
    classification_rows = read_csv_rows(
        classifications_path,
        {"candidate_id", "raw_index", "uncolored_isomorphic_to_reference", "face_type_preserving_isomorphic_to_reference", "mapping_count"},
    )
    classifications_by_raw_index = {str(row["raw_index"]): row for row in classification_rows}

    reference_nodes = parse_node_list(input_config["reference_carrier_nodes"])
    known_exact_nodes = parse_node_list(input_config["known_exact_localized_candidate_nodes"])
    configured_candidate_005_nodes = parse_node_list(input_config["candidate_005_nodes"])
    deep_candidate_id = str(input_config.get("deep_inspection_candidate_id", "candidate_005"))
    deep_raw_index = str(input_config.get("deep_inspection_raw_index", "26157530"))

    reuses_original_bundle = bool(run_config.get("reuses_original_fu02g4c_enumerator_input_bundle", False))
    raw_fields = raw_order_fields(reuses_original_bundle)

    warnings: List[str] = []
    warnings.extend(validate_nodes(graph, reference_nodes, "reference_carrier"))
    warnings.extend(validate_nodes(graph, known_exact_nodes, "known_exact_candidate"))
    warnings.extend(validate_nodes(graph, configured_candidate_005_nodes, "configured_candidate_005"))

    reference_subgraph = induced_subgraph(graph, reference_nodes)
    known_exact_subgraph = induced_subgraph(graph, known_exact_nodes)

    revalidation_rows: List[Dict[str, Any]] = []
    audit_rows: List[Dict[str, Any]] = []
    candidate_lookup: Dict[str, Dict[str, Any]] = {}

    for row_index, source_row in enumerate(candidate_rows):
        g5e2_row = classifications_by_raw_index.get(str(source_row["raw_index"]), {})
        candidate_id = str(g5e2_row.get("candidate_id") or f"candidate_{row_index:03d}")
        nodes = parse_node_list(source_row["candidate_nodes"])
        subgraph = induced_subgraph(graph, nodes)
        source_internal_edge_count = parse_int(source_row.get("internal_edge_count"), "internal_edge_count")
        source_connected = parse_bool(source_row.get("candidate_connected"))
        source_h_count = parse_int(source_row.get("h_count"), "h_count")
        source_p_count = parse_int(source_row.get("p_count"), "p_count")
        exact_match = parse_bool(source_row.get("exact_match"))
        near_distance = parse_int(source_row.get("near_distance"), "near_distance")

        candidate_warnings = validate_nodes(graph, nodes, candidate_id)
        candidate_node_count = len(nodes)
        candidate_edge_count = edge_count(subgraph)
        candidate_connected = is_connected(subgraph)
        h_count = sum(1 for node in nodes if face_type(node) == "H")
        p_count = sum(1 for node in nodes if face_type(node) == "P")

        face_mappings = enumerate_isomorphisms(reference_subgraph, subgraph, True)
        typed_iso = bool(face_mappings)
        uncolored_iso = bool(enumerate_isomorphisms(reference_subgraph, subgraph, False, stop_after_first=True))
        mapping_count = len(face_mappings)

        source_edge_ok = source_internal_edge_count is None or source_internal_edge_count == candidate_edge_count
        g5e2_uncolored = parse_bool(g5e2_row.get("uncolored_isomorphic_to_reference")) if g5e2_row else None
        g5e2_typed = parse_bool(g5e2_row.get("face_type_preserving_isomorphic_to_reference")) if g5e2_row else None
        g5e2_mapping_count = parse_int(g5e2_row.get("mapping_count"), "mapping_count") if g5e2_row else None

        row = {
            "candidate_id": candidate_id,
            "window_id": source_row["window_id"],
            "raw_index": source_row["raw_index"],
            "candidate_nodes": set_key(nodes),
            "candidate_node_count": candidate_node_count,
            "candidate_node_count_expected": len(reference_nodes),
            "candidate_node_count_ok": candidate_node_count == len(reference_nodes),
            "candidate_edge_count": candidate_edge_count,
            "source_internal_edge_count": source_internal_edge_count,
            "candidate_edge_count_ok": source_edge_ok,
            "candidate_connected": candidate_connected,
            "source_candidate_connected": source_connected,
            "h_count": h_count,
            "p_count": p_count,
            "source_h_count": source_h_count,
            "source_p_count": source_p_count,
            "uncolored_isomorphic_to_reference": uncolored_iso,
            "face_type_preserving_isomorphic_to_reference": typed_iso,
            "mapping_count": mapping_count,
            "g5e2_uncolored_isomorphic_to_reference": g5e2_uncolored,
            "g5e2_face_type_preserving_isomorphic_to_reference": g5e2_typed,
            "g5e2_mapping_count": g5e2_mapping_count,
            "exact_match": exact_match,
            "near_distance": near_distance,
            "classification_primary": g5e2_row.get("classification_primary", ""),
            "decision_basis": decision_basis(
                exact_match,
                near_distance,
                uncolored_iso,
                typed_iso,
                raw_fields["raw_order_certification_status"],
            ),
            "warnings": "; ".join(candidate_warnings),
            **raw_fields,
        }
        revalidation_rows.append(row)
        candidate_lookup[candidate_id] = {**row, "source_row": source_row, "nodes": nodes, "subgraph": subgraph}

        g5e2_agrees_uncolored = g5e2_uncolored is None or g5e2_uncolored == uncolored_iso
        g5e2_agrees_typed = g5e2_typed is None or g5e2_typed == typed_iso
        g5e2_agrees_mapping = g5e2_mapping_count is None or g5e2_mapping_count == mapping_count
        audit_note = "g5e2 agreement confirmed"
        if not (g5e2_agrees_uncolored and g5e2_agrees_typed and g5e2_agrees_mapping):
            audit_note = "g5e2 mismatch requires review"
        audit_rows.append(
            {
                "candidate_id": candidate_id,
                "raw_index": source_row["raw_index"],
                "candidate_node_count": candidate_node_count,
                "candidate_edge_count": candidate_edge_count,
                "candidate_connected": candidate_connected,
                "uncolored_isomorphic_to_reference": uncolored_iso,
                "face_type_preserving_isomorphic_to_reference": typed_iso,
                "mapping_count": mapping_count,
                "g5e2_agrees_uncolored": g5e2_agrees_uncolored,
                "g5e2_agrees_face_type_preserving": g5e2_agrees_typed,
                "g5e2_agrees_mapping_count": g5e2_agrees_mapping,
                "audit_note": audit_note,
            }
        )

    candidate_005 = candidate_lookup.get(deep_candidate_id)
    if candidate_005 is None:
        raise ValueError(f"Deep-inspection candidate not found: {deep_candidate_id}")
    if str(candidate_005["raw_index"]) != deep_raw_index:
        raise ValueError(
            f"{deep_candidate_id} raw_index mismatch: expected {deep_raw_index}, found {candidate_005['raw_index']}"
        )
    if set(candidate_005["nodes"]) != set(configured_candidate_005_nodes):
        warnings.append("Configured candidate_005 node set differs from source table candidate_005 row.")

    c005_nodes = set(candidate_005["nodes"])
    exact_nodes = set(known_exact_nodes)
    nodes_only_c005 = sorted_nodes(c005_nodes - exact_nodes)
    nodes_only_exact = sorted_nodes(exact_nodes - c005_nodes)
    node_diff_rows = [
        {"node": node, "diff_class": "only_in_candidate_005", "face_type": face_type(node)}
        for node in nodes_only_c005
    ]
    node_diff_rows.extend(
        {"node": node, "diff_class": "only_in_known_exact_candidate", "face_type": face_type(node)}
        for node in nodes_only_exact
    )
    node_diff_rows.extend(
        {"node": node, "diff_class": "in_both", "face_type": face_type(node)}
        for node in sorted_nodes(c005_nodes & exact_nodes)
    )

    c005_edges = edge_set(candidate_005["subgraph"])
    exact_edges = edge_set(known_exact_subgraph)
    edges_only_c005 = sorted(c005_edges - exact_edges)
    edges_only_exact = sorted(exact_edges - c005_edges)
    edge_diff_rows = [
        {"edge_key": edge_key(edge), "node_a": edge[0], "node_b": edge[1], "diff_class": "only_in_candidate_005"}
        for edge in edges_only_c005
    ]
    edge_diff_rows.extend(
        {"edge_key": edge_key(edge), "node_a": edge[0], "node_b": edge[1], "diff_class": "only_in_known_exact_candidate"}
        for edge in edges_only_exact
    )
    edge_diff_rows.extend(
        {"edge_key": edge_key(edge), "node_a": edge[0], "node_b": edge[1], "diff_class": "in_both"}
        for edge in sorted(c005_edges & exact_edges)
    )

    known_exact_source = next((row for row in candidate_rows if parse_bool(row.get("exact_match")) is True), {})
    c005_source = candidate_005["source_row"]
    common_carrier, different_carrier = compare_signature_components(
        c005_source.get("carrier_signature", ""),
        known_exact_source.get("carrier_signature", ""),
    )
    common_role, different_role = compare_signature_components(
        c005_source.get("role_colored_signature", ""),
        known_exact_source.get("role_colored_signature", ""),
    )
    common_components = [f"carrier:{item}" for item in common_carrier] + [f"role:{item}" for item in common_role]
    different_components = [f"carrier:{item}" for item in different_carrier] + [f"role:{item}" for item in different_role]

    near_zero_explanation = (
        "near_distance=0 means the coarse diagnostic distance used by FU02g5e1 "
        "matched selected signature components. It does not assert node-set "
        "identity, edge-set identity, exact_match=True, or graph isomorphism."
    )
    c005_degeneracy = (
        parse_int(str(candidate_005["near_distance"]), "near_distance") == 0
        and parse_bool(candidate_005["exact_match"]) is False
        and not bool(candidate_005["uncolored_isomorphic_to_reference"])
        and not bool(candidate_005["face_type_preserving_isomorphic_to_reference"])
    )

    deep_row = {
        "candidate_id": deep_candidate_id,
        "raw_index": candidate_005["raw_index"],
        "candidate_nodes": set_key(c005_nodes),
        "known_exact_candidate_nodes": set_key(exact_nodes),
        "nodes_only_in_candidate_005": set_key(nodes_only_c005),
        "nodes_only_in_known_exact_candidate": set_key(nodes_only_exact),
        "candidate_005_edge_count": len(c005_edges),
        "known_exact_edge_count": len(exact_edges),
        "edges_only_in_candidate_005": ";".join(edge_key(edge) for edge in edges_only_c005),
        "edges_only_in_known_exact_candidate": ";".join(edge_key(edge) for edge in edges_only_exact),
        "candidate_005_degree_histogram": degree_histogram(candidate_005["subgraph"]),
        "known_exact_degree_histogram": degree_histogram(known_exact_subgraph),
        "candidate_005_face_type_counts": face_type_counts(c005_nodes),
        "known_exact_face_type_counts": face_type_counts(exact_nodes),
        "candidate_005_carrier_signature": c005_source.get("carrier_signature", ""),
        "known_exact_carrier_signature": known_exact_source.get("carrier_signature", ""),
        "carrier_signature_equal": c005_source.get("carrier_signature", "") == known_exact_source.get("carrier_signature", ""),
        "candidate_005_role_colored_signature": c005_source.get("role_colored_signature", ""),
        "known_exact_role_colored_signature": known_exact_source.get("role_colored_signature", ""),
        "role_colored_signature_equal": c005_source.get("role_colored_signature", "") == known_exact_source.get("role_colored_signature", ""),
        "common_coarse_signature_components": "; ".join(common_components),
        "different_coarse_signature_components": "; ".join(different_components),
        "exact_match": candidate_005["exact_match"],
        "near_distance": candidate_005["near_distance"],
        "uncolored_isomorphic_to_reference": candidate_005["uncolored_isomorphic_to_reference"],
        "face_type_preserving_isomorphic_to_reference": candidate_005["face_type_preserving_isomorphic_to_reference"],
        "mapping_count": candidate_005["mapping_count"],
        "coarse_signature_degeneracy_case": c005_degeneracy,
        "near_distance_zero_explanation": near_zero_explanation,
        **raw_fields,
    }

    output_paths = {
        "summary_json": output_dir / "summary.json",
        "candidate_revalidation_csv": output_dir / "candidate_revalidation.csv",
        "candidate_005_node_diff_csv": output_dir / "candidate_005_node_diff.csv",
        "candidate_005_edge_diff_csv": output_dir / "candidate_005_edge_diff.csv",
        "candidate_005_deep_inspection_csv": output_dir / "candidate_005_deep_inspection.csv",
        "isomorphism_audit_csv": output_dir / "isomorphism_audit.csv",
        "result_note_md": output_dir / "result_note.md",
    }

    summary = {
        "metadata": {
            "run_id": run_config["run_id"],
            "case_id": run_config["case_id"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "script_path": "scripts/run_bms_fu02g5f_raw_order_replay_certification.py",
            "config_path": str(config_path),
        },
        "inputs": {
            "full_face_graph_edges_csv": str(graph_path),
            "near_match_candidates_csv": str(candidates_path),
            "candidate_classification_csv": str(classifications_path),
            "reference_carrier_nodes": reference_nodes,
            "known_exact_localized_candidate_nodes": known_exact_nodes,
            "deep_inspection_candidate_id": deep_candidate_id,
            "deep_inspection_raw_index": deep_raw_index,
        },
        "raw_order_certification": raw_fields,
        "graph": {
            "full_graph_node_count": len(graph),
            "full_graph_edge_count": edge_count(graph),
            "reference_node_count": len(reference_nodes),
            "reference_edge_count": edge_count(reference_subgraph),
            "reference_connected": is_connected(reference_subgraph),
        },
        "candidate_counts": {
            "candidate_count": len(revalidation_rows),
            "connected_count": sum(1 for row in revalidation_rows if row["candidate_connected"]),
            "uncolored_isomorphic_count": sum(1 for row in revalidation_rows if row["uncolored_isomorphic_to_reference"]),
            "face_type_preserving_isomorphic_count": sum(
                1 for row in revalidation_rows if row["face_type_preserving_isomorphic_to_reference"]
            ),
            "near_distance_zero_count": sum(1 for row in revalidation_rows if row["near_distance"] == 0),
            "exact_match_true_count": sum(1 for row in revalidation_rows if row["exact_match"] is True),
        },
        "candidate_005": {
            "candidate_id": deep_candidate_id,
            "raw_index": candidate_005["raw_index"],
            "exact_match": candidate_005["exact_match"],
            "near_distance": candidate_005["near_distance"],
            "nodes_only_in_candidate_005": nodes_only_c005,
            "nodes_only_in_known_exact_candidate": nodes_only_exact,
            "edges_only_in_candidate_005": [edge_key(edge) for edge in edges_only_c005],
            "edges_only_in_known_exact_candidate": [edge_key(edge) for edge in edges_only_exact],
            "uncolored_isomorphic_to_reference": candidate_005["uncolored_isomorphic_to_reference"],
            "face_type_preserving_isomorphic_to_reference": candidate_005["face_type_preserving_isomorphic_to_reference"],
            "mapping_count": candidate_005["mapping_count"],
            "coarse_signature_degeneracy_case": c005_degeneracy,
            "near_distance_zero_explanation": near_zero_explanation,
        },
        "outputs": {key: str(path) for key, path in output_paths.items()},
        "warnings": warnings,
        "claim_boundary": {
            "method_control_block_only": True,
            "no_physical_emergence_claim": True,
            "no_spacetime_emergence_claim": True,
            "no_global_uniqueness_claim": True,
            "no_global_rarity_claim": True,
            "near_distance_is_coarse_diagnostic_only": True,
            "role_transport_rule": "FU02g5c automorphy-only rule",
        },
    }

    write_csv(output_paths["candidate_revalidation_csv"], revalidation_rows, CANDIDATE_REVALIDATION_FIELDS)
    write_csv(output_paths["candidate_005_node_diff_csv"], node_diff_rows, NODE_DIFF_FIELDS)
    write_csv(output_paths["candidate_005_edge_diff_csv"], edge_diff_rows, EDGE_DIFF_FIELDS)
    write_csv(output_paths["candidate_005_deep_inspection_csv"], [deep_row], DEEP_INSPECTION_FIELDS)
    write_csv(output_paths["isomorphism_audit_csv"], audit_rows, ISOMORPHISM_AUDIT_FIELDS)
    write_json(output_paths["summary_json"], summary)
    output_paths["result_note_md"].write_text(build_result_note(summary), encoding="utf-8")

    print(f"Wrote FU02g5f outputs to {output_dir}")
    print(f"raw_order_certification_status={raw_fields['raw_order_certification_status']}")
    print(f"candidate_005_coarse_signature_degeneracy_case={c005_degeneracy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
