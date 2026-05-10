#!/usr/bin/env python3
"""
BMS-FU02g5e2 - Near-Match Decoy Classification

Classify FU02g5e1 near-match scaffold-localization candidates. Reference roles
are transported only through explicit face-type-preserving isomorphisms between
the reference induced subgraph and the candidate induced subgraph.

Claim boundary: combinatorial / methodological classification only. No physical
emergence, spacetime emergence, global uniqueness, or FU02g4c replay
certification claim is made.
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

ROLE_MIXED_CORE = "mixed_core"
ROLE_PENTAGON_BOUNDARY = "pentagon_boundary"
ROLE_CARRIER_OTHER = "carrier_other"
CLASSIFICATION_BOUNDARY = "scaffold_only_candidate_pending_fu02g4c_replay_validation"

CANDIDATE_CLASSIFICATION_FIELDS = [
    "candidate_id",
    "window_id",
    "raw_index",
    "candidate_nodes",
    "exact_match",
    "near_distance",
    "candidate_node_count",
    "candidate_edge_count",
    "candidate_connected",
    "uncolored_isomorphic_to_reference",
    "face_type_preserving_isomorphic_to_reference",
    "mapping_count",
    "role_transport_allowed",
    "unique_transported_mixed_core_set_count",
    "unique_transported_pentagon_boundary_set_count",
    "mixed_core_transport_invariant",
    "pentagon_boundary_transport_invariant",
    "classification_primary",
    "classification_boundary",
    "scaffold_order_certification",
    "warnings",
]

MAPPING_FIELDS = [
    "candidate_id",
    "mapping_index",
    "reference_node",
    "candidate_node",
    "reference_face_type",
    "candidate_face_type",
    "transported_role",
]

TRANSPORTED_ROLE_SET_FIELDS = [
    "candidate_id",
    "mapping_index",
    "mixed_core_nodes",
    "pentagon_boundary_nodes",
    "mixed_core_key",
    "pentagon_boundary_key",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMS-FU02g5e2 near-match decoy classification."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5e2_near_match_decoy_classification_config.yaml",
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


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n", ""}:
        return False
    raise ValueError(f"Cannot parse boolean value: {value!r}")


def parse_int(value: Any, field: str) -> int:
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


Graph = Dict[str, Set[str]]


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
            raise ValueError(
                f"CSV must contain face_a / face_b columns; missing {sorted(missing)}"
            )
        for row in reader:
            face_a = str(row["face_a"]).strip()
            face_b = str(row["face_b"]).strip()
            if not face_a or not face_b:
                continue
            graph.setdefault(face_a, set()).add(face_b)
            graph.setdefault(face_b, set()).add(face_a)
    return graph


def read_candidate_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Near-match candidate CSV not found: {path}")

    required = {"window_id", "raw_index", "candidate_nodes", "exact_match", "near_distance"}
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Candidate CSV missing required columns: {sorted(missing)}")
        for row in reader:
            rows.append({key: str(value) for key, value in row.items()})
    return rows


def induced_subgraph(graph: Graph, nodes: Sequence[str]) -> Graph:
    node_set = set(nodes)
    return {
        node: {neighbor for neighbor in graph.get(node, set()) if neighbor in node_set}
        for node in sorted_nodes(node_set)
        if node in graph
    }


def edge_count(graph: Graph) -> int:
    return sum(len(neighbors) for neighbors in graph.values()) // 2


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


def validate_nodes(graph: Graph, nodes: Sequence[str], label: str) -> List[str]:
    warnings: List[str] = []
    counts = Counter(nodes)
    duplicates = sorted(node for node, count in counts.items() if count > 1)
    if duplicates:
        warnings.append(f"{label}: duplicate nodes: {duplicates}")
    missing = sorted(set(nodes) - set(graph))
    if missing:
        warnings.append(f"{label}: nodes missing from full graph: {missing}")
    present = [node for node in nodes if node in graph]
    if present:
        subgraph = induced_subgraph(graph, present)
        if not is_connected(subgraph):
            warnings.append(f"{label}: induced subgraph is not connected")
    return warnings


def graph_stats(graph: Graph) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for node in graph:
        ft = face_type(str(node))
        counts[ft] = counts.get(ft, 0) + 1
    return {
        "node_count": len(graph),
        "edge_count": edge_count(graph),
        "connected": is_connected(graph),
        "face_type_counts": dict(sorted(counts.items())),
    }


def role_for_reference_node(
    node: str,
    mixed_core_nodes: Set[str],
    pentagon_boundary_nodes: Set[str],
) -> str:
    if node in mixed_core_nodes:
        return ROLE_MIXED_CORE
    if node in pentagon_boundary_nodes:
        return ROLE_PENTAGON_BOUNDARY
    return ROLE_CARRIER_OTHER


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
    ref_degree_hist = Counter(ref_degrees.values())
    cand_degree_hist = Counter(cand_degrees.values())
    if ref_degree_hist != cand_degree_hist:
        return []

    if preserve_face_type:
        ref_type_degree_hist = Counter(
            (face_type(node), degree) for node, degree in ref_degrees.items()
        )
        cand_type_degree_hist = Counter(
            (face_type(node), degree) for node, degree in cand_degrees.items()
        )
        if ref_type_degree_hist != cand_type_degree_hist:
            return []

    reference_nodes = sorted(
        reference_subgraph,
        key=lambda node: (-ref_degrees[node], face_type(node), node),
    )
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


def enumerate_face_type_preserving_mappings(
    reference_subgraph: Graph,
    candidate_subgraph: Graph,
) -> List[Dict[str, str]]:
    return enumerate_isomorphisms(reference_subgraph, candidate_subgraph, True)


def uncolored_isomorphic(reference_subgraph: Graph, candidate_subgraph: Graph) -> bool:
    return bool(
        enumerate_isomorphisms(
            reference_subgraph,
            candidate_subgraph,
            preserve_face_type=False,
            stop_after_first=True,
        )
    )


def transported_sets_for_mapping(
    mapping: Mapping[str, str],
    mixed_core_nodes: Set[str],
    pentagon_boundary_nodes: Set[str],
) -> Tuple[List[str], List[str]]:
    mixed = [mapping[node] for node in mixed_core_nodes if node in mapping]
    boundary = [mapping[node] for node in pentagon_boundary_nodes if node in mapping]
    return sorted_nodes(mixed), sorted_nodes(boundary)


def invariant_flag(mapping_count: int, unique_set_count: int) -> Optional[bool]:
    if mapping_count == 0:
        return None
    return unique_set_count == 1


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
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


def classify_candidate(
    exact_match: bool,
    candidate_nodes: Sequence[str],
    known_exact_nodes: Set[str],
    face_type_preserving_iso: bool,
    near_distance: int,
) -> str:
    if exact_match and set(candidate_nodes) == known_exact_nodes:
        return "known_exact_spiegelklunker"
    if face_type_preserving_iso:
        return "automorphic_reference_twin_or_isomorphic_decoy"
    if near_distance == 0:
        return "coarse_signature_twin_but_not_exact"
    if near_distance == 1:
        return "local_near_decoy_distance_1"
    if near_distance == 2:
        return "near_decoy_distance_2"
    return "other_near_candidate"


def build_result_note(summary: Mapping[str, Any]) -> str:
    counts = summary["summary_counts"]
    mapping_counts = counts["mapping_state_counts"]
    invariant_counts = counts["role_transport_invariance_counts"]

    return f"""# BMS-FU02g5e2 - Near-Match Decoy Classification Result Note

Datum: {summary["metadata"]["created_at_utc"][:10]}

## Befund

Dieser Lauf klassifiziert die {counts["candidate_count"]} Near-Match-Kandidaten aus FU02g5e1.
Die Auswertung basiert auf g5e1 scaffold localization.

```text
candidate_count = {counts["candidate_count"]}
face_type_preserving_isomorphic_candidates = {mapping_counts["face_type_preserving_isomorphic_candidates"]}
non_isomorphic_near_candidates = {mapping_counts["non_isomorphic_near_candidates"]}
role_transport_allowed_candidates = {mapping_counts["role_transport_allowed_candidates"]}
```

## Interpretation

Role transport is allowed only for face-type-preserving isomorphic candidates.
Non-isomorphic near candidates remain decoys without reference role transport.
Wenn mehrere gueltige Mappings existieren, bleibt die Mehrdeutigkeit sichtbar:

```text
mixed_core_transport_invariant_true = {invariant_counts["mixed_core_transport_invariant_true"]}
mixed_core_transport_invariant_false = {invariant_counts["mixed_core_transport_invariant_false"]}
pentagon_boundary_transport_invariant_true = {invariant_counts["pentagon_boundary_transport_invariant_true"]}
pentagon_boundary_transport_invariant_false = {invariant_counts["pentagon_boundary_transport_invariant_false"]}
```

## Hypothese

Face-type-preserving isomorphic candidates koennen als automorphe Referenz-Twins
oder isomorphe Decoys weiter kontrolliert werden. Kandidaten ohne solches
Mapping sind nur scaffold-nahe Decoys und tragen keine frei transportierten
Referenzrollen.

## Offene Luecke

FU02g4c raw-order replay certification is still open. Diese Klassifikation ist
daher eine scaffold-only Nachklassifikation der FU02g5e1-Lokalisierung und
keine FU02g4c Replay-Zertifizierung.

## Claim Boundary

Sauber behauptbar ist nur eine kombinatorisch-methodische Decoy-Klassifikation.

Nicht behaupten:

```text
physical emergence
spacetime emergence
global uniqueness
FU02g4c replay certification
reference role transport without face-type-preserving isomorphism
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
    full_graph = read_face_edge_csv(graph_path)
    candidate_source_rows = read_candidate_rows(candidates_path)

    reference_nodes = parse_node_list(input_config["reference_carrier_nodes"])
    mixed_core_nodes = set(parse_node_list(input_config["reference_mixed_core_nodes"]))
    pentagon_boundary_nodes = set(parse_node_list(input_config["reference_pentagon_boundary_nodes"]))
    known_exact_nodes = set(parse_node_list(input_config["known_exact_localized_fu02g4c_candidate_nodes"]))
    scaffold_order_certification = bool(run_config.get("scaffold_order_certification", False))

    warnings: List[str] = []
    warnings.extend(validate_nodes(full_graph, reference_nodes, "reference_carrier"))
    if not mixed_core_nodes <= set(reference_nodes):
        warnings.append("reference_mixed_core_nodes is not a subset of reference_carrier_nodes")
    if not pentagon_boundary_nodes <= set(reference_nodes):
        warnings.append("reference_pentagon_boundary_nodes is not a subset of reference_carrier_nodes")
    role_overlap = mixed_core_nodes & pentagon_boundary_nodes
    if role_overlap:
        warnings.append(f"reference role sets overlap: {sorted_nodes(role_overlap)}")

    reference_subgraph = induced_subgraph(full_graph, reference_nodes)

    classification_rows: List[Dict[str, Any]] = []
    mapping_rows: List[Dict[str, Any]] = []
    transported_role_rows: List[Dict[str, Any]] = []
    candidate_json_rows: List[Dict[str, Any]] = []

    for row_index, source_row in enumerate(candidate_source_rows):
        candidate_id = f"candidate_{row_index:03d}"
        candidate_nodes = parse_node_list(source_row["candidate_nodes"])
        exact_match = parse_bool(source_row["exact_match"])
        near_distance = parse_int(source_row["near_distance"], "near_distance")
        candidate_warnings = validate_nodes(full_graph, candidate_nodes, candidate_id)

        candidate_subgraph = induced_subgraph(full_graph, candidate_nodes)
        is_uncolored_iso = uncolored_isomorphic(reference_subgraph, candidate_subgraph)
        mappings = enumerate_face_type_preserving_mappings(reference_subgraph, candidate_subgraph)
        mapping_count = len(mappings)
        is_face_type_iso = mapping_count > 0

        mixed_keys: Set[str] = set()
        boundary_keys: Set[str] = set()
        for mapping_index, mapping in enumerate(mappings):
            mixed_nodes, boundary_nodes = transported_sets_for_mapping(
                mapping, mixed_core_nodes, pentagon_boundary_nodes
            )
            mixed_key = set_key(mixed_nodes)
            boundary_key = set_key(boundary_nodes)
            mixed_keys.add(mixed_key)
            boundary_keys.add(boundary_key)
            transported_role_rows.append(
                {
                    "candidate_id": candidate_id,
                    "mapping_index": mapping_index,
                    "mixed_core_nodes": mixed_key,
                    "pentagon_boundary_nodes": boundary_key,
                    "mixed_core_key": mixed_key,
                    "pentagon_boundary_key": boundary_key,
                }
            )
            for reference_node in sorted_nodes(reference_nodes):
                candidate_node = mapping.get(reference_node, "")
                mapping_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "mapping_index": mapping_index,
                        "reference_node": reference_node,
                        "candidate_node": candidate_node,
                        "reference_face_type": face_type(reference_node),
                        "candidate_face_type": face_type(candidate_node),
                        "transported_role": role_for_reference_node(
                            reference_node,
                            mixed_core_nodes,
                            pentagon_boundary_nodes,
                        ),
                    }
                )

        mixed_invariant = invariant_flag(mapping_count, len(mixed_keys))
        boundary_invariant = invariant_flag(mapping_count, len(boundary_keys))
        classification_primary = classify_candidate(
            exact_match,
            candidate_nodes,
            known_exact_nodes,
            is_face_type_iso,
            near_distance,
        )

        classification_row = {
            "candidate_id": candidate_id,
            "window_id": source_row["window_id"],
            "raw_index": parse_int(source_row["raw_index"], "raw_index"),
            "candidate_nodes": set_key(candidate_nodes),
            "exact_match": exact_match,
            "near_distance": near_distance,
            "candidate_node_count": len(candidate_nodes),
            "candidate_edge_count": edge_count(candidate_subgraph),
            "candidate_connected": is_connected(candidate_subgraph),
            "uncolored_isomorphic_to_reference": is_uncolored_iso,
            "face_type_preserving_isomorphic_to_reference": is_face_type_iso,
            "mapping_count": mapping_count,
            "role_transport_allowed": is_face_type_iso,
            "unique_transported_mixed_core_set_count": len(mixed_keys),
            "unique_transported_pentagon_boundary_set_count": len(boundary_keys),
            "mixed_core_transport_invariant": mixed_invariant,
            "pentagon_boundary_transport_invariant": boundary_invariant,
            "classification_primary": classification_primary,
            "classification_boundary": CLASSIFICATION_BOUNDARY,
            "scaffold_order_certification": scaffold_order_certification,
            "warnings": "; ".join(candidate_warnings),
        }
        classification_rows.append(classification_row)
        candidate_json_rows.append(
            {
                **classification_row,
                "unique_transported_mixed_core_sets": sorted(mixed_keys),
                "unique_transported_pentagon_boundary_sets": sorted(boundary_keys),
            }
        )

    write_csv(output_dir / "candidate_classification.csv", classification_rows, CANDIDATE_CLASSIFICATION_FIELDS)
    write_csv(output_dir / "candidate_mappings.csv", mapping_rows, MAPPING_FIELDS)
    write_csv(output_dir / "transported_role_sets.csv", transported_role_rows, TRANSPORTED_ROLE_SET_FIELDS)

    classification_counter = Counter(row["classification_primary"] for row in classification_rows)
    mapping_state_counts = {
        "face_type_preserving_isomorphic_candidates": sum(
            1 for row in classification_rows if row["face_type_preserving_isomorphic_to_reference"]
        ),
        "non_isomorphic_near_candidates": sum(
            1 for row in classification_rows if not row["face_type_preserving_isomorphic_to_reference"]
        ),
        "uncolored_isomorphic_candidates": sum(
            1 for row in classification_rows if row["uncolored_isomorphic_to_reference"]
        ),
        "role_transport_allowed_candidates": sum(
            1 for row in classification_rows if row["role_transport_allowed"]
        ),
    }
    invariance_counts = {
        "mixed_core_transport_invariant_true": sum(
            1 for row in classification_rows if row["mixed_core_transport_invariant"] is True
        ),
        "mixed_core_transport_invariant_false": sum(
            1 for row in classification_rows if row["mixed_core_transport_invariant"] is False
        ),
        "mixed_core_transport_invariant_null": sum(
            1 for row in classification_rows if row["mixed_core_transport_invariant"] is None
        ),
        "pentagon_boundary_transport_invariant_true": sum(
            1 for row in classification_rows if row["pentagon_boundary_transport_invariant"] is True
        ),
        "pentagon_boundary_transport_invariant_false": sum(
            1 for row in classification_rows if row["pentagon_boundary_transport_invariant"] is False
        ),
        "pentagon_boundary_transport_invariant_null": sum(
            1 for row in classification_rows if row["pentagon_boundary_transport_invariant"] is None
        ),
    }

    summary = {
        "metadata": {
            "run_id": run_config["run_id"],
            "case_id": run_config["case_id"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "script": "scripts/run_bms_fu02g5e2_near_match_decoy_classification.py",
            "mode_label": run_config.get("mode_label", "g5e1 scaffold localization"),
            "scaffold_order_certification": scaffold_order_certification,
        },
        "input": {
            "config_path": str(config_path),
            "near_match_candidates_csv": str(candidates_path),
            "full_face_graph_edges_csv": str(graph_path),
            "reference_carrier_nodes": sorted_nodes(reference_nodes),
            "reference_mixed_core_nodes": sorted_nodes(mixed_core_nodes),
            "reference_pentagon_boundary_nodes": sorted_nodes(pentagon_boundary_nodes),
            "known_exact_localized_fu02g4c_candidate_nodes": sorted_nodes(known_exact_nodes),
        },
        "graph": {
            "full_node_count": len(full_graph),
            "full_edge_count": edge_count(full_graph),
            "reference": graph_stats(reference_subgraph),
        },
        "method": {
            "candidate_source": "BMS-FU02g5e1 scaffold localization",
            "isomorphism_engine": "local induced-subgraph backtracking enumerator",
            "uncolored_isomorphism": "graph topology only",
            "face_type_preserving_isomorphism": "node_match=face_type",
            "role_transport_rule": "transport roles only along explicit face-type-preserving isomorphisms",
            "ambiguity_rule": "report mapping_count and transported role set invariance",
        },
        "summary_counts": {
            "candidate_count": len(classification_rows),
            "classification_primary_counts": dict(sorted(classification_counter.items())),
            "mapping_state_counts": mapping_state_counts,
            "role_transport_invariance_counts": invariance_counts,
            "mapping_row_count": len(mapping_rows),
            "transported_role_set_row_count": len(transported_role_rows),
        },
        "candidates": candidate_json_rows,
        "outputs": {
            "summary_json": str(output_dir / "summary.json"),
            "candidate_classification_csv": str(output_dir / "candidate_classification.csv"),
            "candidate_mappings_csv": str(output_dir / "candidate_mappings.csv"),
            "transported_role_sets_csv": str(output_dir / "transported_role_sets.csv"),
            "result_note_md": str(output_dir / "result_note.md"),
        },
        "warnings": warnings,
        "claim_boundary": {
            "physical_emergence_claim": False,
            "spacetime_emergence_claim": False,
            "global_uniqueness_claim": False,
            "fu02g4c_replay_certification_claim": False,
            "role_transport_without_face_type_preserving_isomorphism": False,
        },
    }

    write_json(output_dir / "summary.json", summary)
    with (output_dir / "result_note.md").open("w", encoding="utf-8") as handle:
        handle.write(build_result_note(summary))

    print(
        "BMS-FU02g5e2 complete: "
        f"candidate_count={len(classification_rows)}, "
        f"face_type_preserving_isomorphic={mapping_state_counts['face_type_preserving_isomorphic_candidates']}, "
        f"output_dir={output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
