#!/usr/bin/env python3
"""
BMS-FU02g5g2 - Narrow Per-Index Replay/Photo Certification

Reconstruct the current scaffold/FU02g4c-style deterministic connected 17-face
patch enumeration from the repaired face graph, capture per-index node/edge
photos for configured targets, and compare those photos with FU02g5e1 candidate
node sets.

This runner does not write into runs/BMS-FU02g4c and does not claim full FU02g4c
raw-order replay certification unless exact original enumerator/full input
bundle reuse is explicitly configured.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: PyYAML. Install it in the project environment.") from exc


Graph = Dict[str, Set[str]]
Edge = Tuple[str, str]

PHOTO_CERTIFICATION_FIELDS = [
    "candidate_id",
    "target_raw_index",
    "expected_candidate_nodes",
    "replayed_candidate_nodes",
    "node_set_agreement",
    "edge_set_agreement",
    "per_index_photo_status",
    "prior_g5g_status",
    "g5e2_classification_primary",
    "exact_match",
    "near_distance",
    "h_count",
    "p_count",
    "connected",
    "internal_edge_count",
    "uncolored_isomorphic_to_reference",
    "face_type_preserving_isomorphic_to_reference",
    "mapping_count",
    "role_transport_allowed_under_g5c",
    "full_fu02g4c_replay_certification",
    "certification_basis",
    "warnings",
]

NODE_PHOTO_FIELDS = [
    "candidate_id",
    "target_raw_index",
    "node",
    "face_type",
    "in_expected_candidate",
    "photo_status",
]

EDGE_PHOTO_FIELDS = [
    "candidate_id",
    "target_raw_index",
    "edge_key",
    "node_a",
    "node_b",
    "in_expected_edge_set",
    "photo_status",
]

ISOMORPHISM_RECHECK_FIELDS = [
    "candidate_id",
    "target_raw_index",
    "node_set_agreement",
    "uncolored_isomorphic_to_reference",
    "face_type_preserving_isomorphic_to_reference",
    "mapping_count",
    "g5e2_uncolored_isomorphic_to_reference",
    "g5e2_face_type_preserving_isomorphic_to_reference",
    "g5e2_mapping_count",
    "g5e2_agrees_uncolored",
    "g5e2_agrees_face_type_preserving",
    "g5e2_agrees_mapping_count",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMS-FU02g5g2 narrow per-index photo certification."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5g2_narrow_per_index_replay_photo_certification_config.yaml",
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
    return None


def parse_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_node_list(value: Any) -> List[str]:
    if isinstance(value, list):
        raw_nodes = [str(node).strip() for node in value]
    else:
        raw_nodes = [part.strip() for part in str(value).split(";")]
    return sorted(node for node in raw_nodes if node)


def face_type(node: str) -> str:
    if node.startswith("H_"):
        return "H"
    if node.startswith("P_"):
        return "P"
    return "unknown"


def set_key(nodes: Iterable[str]) -> str:
    return ";".join(sorted(str(node) for node in nodes))


def edge_key(edge: Edge) -> str:
    return f"{edge[0]}--{edge[1]}"


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
            a = str(row["face_a"]).strip()
            b = str(row["face_b"]).strip()
            if not a or not b:
                continue
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)
    return graph


def enumerate_connected_subsets(vertices: List[str], adj: Graph, target_size: int) -> Iterator[Set[str]]:
    order = {v: i for i, v in enumerate(vertices)}
    seen: Set[Tuple[str, ...]] = set()

    def extend(root_idx: int, current: Set[str], candidates: Set[str], excluded: Set[str]) -> Iterator[Set[str]]:
        if len(current) == target_size:
            key = tuple(sorted(current, key=lambda x: order[x]))
            if key not in seen:
                seen.add(key)
                yield set(current)
            return

        cand_list = sorted(candidates, key=lambda x: order[x])
        local_excluded = set(excluded)
        for vertex in cand_list:
            if vertex in local_excluded or vertex in current:
                continue

            new_current = set(current)
            new_current.add(vertex)
            new_candidates = set(candidates)
            new_candidates.discard(vertex)

            for neighbor in adj.get(vertex, set()):
                if order[neighbor] >= root_idx and neighbor not in new_current and neighbor not in local_excluded:
                    new_candidates.add(neighbor)

            yield from extend(root_idx, new_current, new_candidates, local_excluded)
            local_excluded.add(vertex)

    for root_idx, root in enumerate(vertices):
        candidates = {neighbor for neighbor in adj.get(root, set()) if order[neighbor] >= root_idx}
        yield from extend(root_idx, {root}, candidates, set())


def induced_subgraph(graph: Graph, nodes: Sequence[str]) -> Graph:
    node_set = set(nodes)
    return {
        node: {neighbor for neighbor in graph.get(node, set()) if neighbor in node_set}
        for node in sorted(node_set)
    }


def edge_set(graph: Graph) -> Set[Edge]:
    edges: Set[Edge] = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edges.add(tuple(sorted((node, neighbor))))
    return edges


def is_connected(graph: Graph) -> bool:
    if not graph:
        return False
    start = next(iter(graph))
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, set()):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == len(graph)


def enumerate_isomorphisms(
    reference_subgraph: Graph,
    candidate_subgraph: Graph,
    preserve_face_type: bool,
    stop_after_first: bool = False,
) -> List[Dict[str, str]]:
    if len(reference_subgraph) != len(candidate_subgraph):
        return []
    if len(edge_set(reference_subgraph)) != len(edge_set(candidate_subgraph)):
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


def build_result_note(summary: Mapping[str, Any], certification_rows: Sequence[Mapping[str, Any]]) -> str:
    lines = []
    for row in sorted(certification_rows, key=lambda r: str(r["candidate_id"])):
        lines.append(
            f"- {row['candidate_id']} / raw_index {row['target_raw_index']}: "
            f"{row['per_index_photo_status']} "
            f"(node_set_agreement={row['node_set_agreement']}, edge_set_agreement={row['edge_set_agreement']})"
        )
    c005 = summary["candidate_005"]
    c008 = summary["candidate_008_positive_control"]
    return f"""# BMS-FU02g5g2 - Narrow Per-Index Replay/Photo Certification Result Note

Datum: {summary["metadata"]["created_at_local_date"]}

## Befund

FU02g5g2 reconstructed the current scaffold/FU02g4c-style connected 17-face
patch order from the repaired C60 face graph and captured per-index photos for
the configured targets.

Per-index photo agreement by candidate:

{chr(10).join(lines)}

Candidate_005 received a direct per-index photo:

```text
candidate_005_status = {c005.get("per_index_photo_status", "")}
candidate_005_node_set_agreement = {c005.get("node_set_agreement", "")}
candidate_005_coarse_signature_degeneracy_stress_case = true
```

The candidate_008 positive control reproduced:

```text
candidate_008_status = {c008.get("per_index_photo_status", "")}
candidate_008_node_set_agreement = {c008.get("node_set_agreement", "")}
```

## Interpretation

Per-index photo agreement and scaffold-order agreement are direct controls for
the current deterministic scaffold/FU02g4c-style enumeration. They do not by
themselves promote scaffold indices to fully certified FU02g4c raw-order
indices.

Full FU02g4c replay certification was not achieved:

```text
full_fu02g4c_replay_certification = {summary["runtime"]["full_fu02g4c_replay_certification"]}
```

## Hypothese

If all configured photos match their expected FU02g5e1 node sets, the g5e1 near
candidate table is consistent with the current scaffold/FU02g4c-style
per-index ordering. Candidate_005 remains a coarse-signature degeneracy stress
case because its photo can match the scaffold node set while `near_distance=0`
still does not imply exact match or isomorphism.

## Offene Luecke

The exact original FU02g4c enumerator and full original input bundle were not
certified as reused here. A full replay certification would require that exact
bundle, an isolated output surface, and a documented order guarantee.

## Claim Boundary

This is a certification/control block only. No physical emergence, spacetime
emergence, global uniqueness, or global rarity claim follows.
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

    g5e1_path = resolve_path(repo_root, str(input_config["g5e1_candidates_csv"]))
    g5e2_path = resolve_path(repo_root, str(input_config["g5e2_classification_csv"]))
    g5f_path = resolve_path(repo_root, str(input_config["g5f_revalidation_csv"]))
    g5g_path = resolve_path(repo_root, str(input_config["g5g_replay_certification_csv"]))
    graph_path = resolve_path(repo_root, str(input_config["face_graph_edges_csv"]))

    g5e1_rows = read_csv_rows(g5e1_path, {"raw_index", "candidate_nodes", "exact_match", "near_distance"})
    g5e2_rows = read_csv_rows(g5e2_path, {"candidate_id", "raw_index", "classification_primary"})
    g5f_rows = read_csv_rows(g5f_path, {"candidate_id", "raw_index", "candidate_edge_count"})
    g5g_rows = read_csv_rows(g5g_path, {"candidate_id", "scaffold_raw_index", "replay_certification_status"})
    graph = read_face_edge_csv(graph_path)

    g5e1_by_raw = {int(str(row["raw_index"])): row for row in g5e1_rows}
    g5e2_by_id = {row["candidate_id"]: row for row in g5e2_rows}
    g5f_by_id = {row["candidate_id"]: row for row in g5f_rows}
    g5g_by_id = {row["candidate_id"]: row for row in g5g_rows}

    reference_nodes = parse_node_list(input_config["reference_carrier_nodes"])
    reference_subgraph = induced_subgraph(graph, reference_nodes)
    target_patch_size = int(run_config.get("target_patch_size", 17))
    max_runtime_seconds = float(run_config.get("max_runtime_seconds", 1200))
    full_fu02g4c_replay_certification = bool(run_config.get("full_fu02g4c_replay_certification", False))
    exact_original_reused = bool(run_config.get("exact_original_fu02g4c_enumerator_reused", False))
    full_bundle_reused = bool(run_config.get("full_original_input_bundle_reused", False))
    if not (exact_original_reused and full_bundle_reused):
        full_fu02g4c_replay_certification = False

    targets = [
        {
            "candidate_id": str(item["candidate_id"]),
            "target_raw_index": int(item["raw_index"]),
            "target_role": str(item.get("target_role", "")),
        }
        for item in config.get("targets", [])
    ]
    target_by_capture_ordinal = {item["target_raw_index"] + 1: item for item in targets}
    max_capture_ordinal = max(target_by_capture_ordinal) if target_by_capture_ordinal else 0

    vertices = sorted(graph)
    captured: Dict[str, Set[str]] = {}
    stop_reason = "complete"
    started = time.time()
    last_ordinal = 0

    for ordinal, patch in enumerate(enumerate_connected_subsets(vertices, graph, target_patch_size), start=1):
        last_ordinal = ordinal
        if ordinal in target_by_capture_ordinal:
            target = target_by_capture_ordinal[ordinal]
            captured[target["candidate_id"]] = set(patch)
            print(f"captured {target['candidate_id']} at target_raw_index={target['target_raw_index']}")
            if len(captured) == len(targets):
                stop_reason = "all_targets_captured"
                break
        if ordinal >= max_capture_ordinal:
            stop_reason = "max_target_ordinal_reached"
            break
        if time.time() - started > max_runtime_seconds:
            stop_reason = "timeout"
            break

    elapsed = time.time() - started
    certification_rows: List[Dict[str, Any]] = []
    node_photo_rows: List[Dict[str, Any]] = []
    edge_photo_rows: List[Dict[str, Any]] = []
    iso_rows: List[Dict[str, Any]] = []

    for target in targets:
        candidate_id = target["candidate_id"]
        target_raw_index = target["target_raw_index"]
        source_row = g5e1_by_raw.get(target_raw_index)
        if source_row is None:
            raise ValueError(f"Missing g5e1 row for target raw_index={target_raw_index}")

        expected_nodes = set(parse_node_list(source_row["candidate_nodes"]))
        expected_subgraph = induced_subgraph(graph, sorted(expected_nodes))
        expected_edges = edge_set(expected_subgraph)
        replayed_nodes = captured.get(candidate_id)
        warnings: List[str] = []

        if replayed_nodes is None:
            status = "timeout" if stop_reason == "timeout" else "replay_failed"
            replayed_nodes = set()
            node_set_agreement = False
            edge_set_agreement = False
            certification_basis = f"No photo captured before stop_reason={stop_reason}."
        else:
            node_set_agreement = replayed_nodes == expected_nodes
            replayed_edges = edge_set(induced_subgraph(graph, sorted(replayed_nodes)))
            edge_set_agreement = replayed_edges == expected_edges
            status = "matched_expected_nodes" if node_set_agreement else "node_mismatch"
            certification_basis = (
                "Current scaffold/FU02g4c-style per-index photo matched the expected node set."
                if node_set_agreement
                else "Current scaffold/FU02g4c-style per-index photo did not match the expected node set."
            )
            if target["target_role"] == "coarse_signature_degeneracy_stress_case":
                warnings.append("candidate_005 coarse-signature degeneracy stress case; near_distance=0 is not exact identity or isomorphism")
            if not full_fu02g4c_replay_certification:
                warnings.append("full FU02g4c replay certification is false; exact original enumerator/full bundle not certified as reused")

        replayed_subgraph = induced_subgraph(graph, sorted(replayed_nodes))
        replayed_edges = edge_set(replayed_subgraph)
        h_count = sum(1 for node in replayed_nodes if face_type(node) == "H")
        p_count = sum(1 for node in replayed_nodes if face_type(node) == "P")
        connected = is_connected(replayed_subgraph)
        internal_edge_count = len(replayed_edges)
        typed_mappings = enumerate_isomorphisms(reference_subgraph, replayed_subgraph, True)
        mapping_count = len(typed_mappings)
        typed_iso = bool(typed_mappings)
        uncolored_iso = bool(enumerate_isomorphisms(reference_subgraph, replayed_subgraph, False, stop_after_first=True))

        g5e2_row = g5e2_by_id.get(candidate_id, {})
        g5f_row = g5f_by_id.get(candidate_id, {})
        g5g_row = g5g_by_id.get(candidate_id, {})
        g5e2_uncolored = parse_bool(g5e2_row.get("uncolored_isomorphic_to_reference"))
        g5e2_typed = parse_bool(g5e2_row.get("face_type_preserving_isomorphic_to_reference"))
        g5e2_mapping_count = parse_int(g5e2_row.get("mapping_count"))
        g5f_edge_count = parse_int(g5f_row.get("candidate_edge_count"))
        if g5f_edge_count is not None and g5f_edge_count != len(expected_edges):
            warnings.append(f"expected induced edge count differs from g5f candidate_edge_count={g5f_edge_count}")

        certification_rows.append(
            {
                "candidate_id": candidate_id,
                "target_raw_index": target_raw_index,
                "expected_candidate_nodes": set_key(expected_nodes),
                "replayed_candidate_nodes": set_key(replayed_nodes),
                "node_set_agreement": node_set_agreement,
                "edge_set_agreement": edge_set_agreement,
                "per_index_photo_status": status,
                "prior_g5g_status": g5g_row.get("replay_certification_status", ""),
                "g5e2_classification_primary": g5e2_row.get("classification_primary", ""),
                "exact_match": parse_bool(source_row.get("exact_match")),
                "near_distance": parse_int(source_row.get("near_distance")),
                "h_count": h_count,
                "p_count": p_count,
                "connected": connected,
                "internal_edge_count": internal_edge_count,
                "uncolored_isomorphic_to_reference": uncolored_iso,
                "face_type_preserving_isomorphic_to_reference": typed_iso,
                "mapping_count": mapping_count,
                "role_transport_allowed_under_g5c": typed_iso,
                "full_fu02g4c_replay_certification": full_fu02g4c_replay_certification,
                "certification_basis": certification_basis,
                "warnings": "; ".join(warnings),
            }
        )

        for node in sorted(replayed_nodes):
            node_photo_rows.append(
                {
                    "candidate_id": candidate_id,
                    "target_raw_index": target_raw_index,
                    "node": node,
                    "face_type": face_type(node),
                    "in_expected_candidate": node in expected_nodes,
                    "photo_status": status,
                }
            )
        for edge in sorted(replayed_edges):
            edge_photo_rows.append(
                {
                    "candidate_id": candidate_id,
                    "target_raw_index": target_raw_index,
                    "edge_key": edge_key(edge),
                    "node_a": edge[0],
                    "node_b": edge[1],
                    "in_expected_edge_set": edge in expected_edges,
                    "photo_status": status,
                }
            )
        iso_rows.append(
            {
                "candidate_id": candidate_id,
                "target_raw_index": target_raw_index,
                "node_set_agreement": node_set_agreement,
                "uncolored_isomorphic_to_reference": uncolored_iso,
                "face_type_preserving_isomorphic_to_reference": typed_iso,
                "mapping_count": mapping_count,
                "g5e2_uncolored_isomorphic_to_reference": g5e2_uncolored,
                "g5e2_face_type_preserving_isomorphic_to_reference": g5e2_typed,
                "g5e2_mapping_count": g5e2_mapping_count,
                "g5e2_agrees_uncolored": g5e2_uncolored is None or g5e2_uncolored == uncolored_iso,
                "g5e2_agrees_face_type_preserving": g5e2_typed is None or g5e2_typed == typed_iso,
                "g5e2_agrees_mapping_count": g5e2_mapping_count is None or g5e2_mapping_count == mapping_count,
            }
        )

    output_paths = {
        "summary_json": output_dir / "summary.json",
        "per_index_photo_certification_csv": output_dir / "per_index_photo_certification.csv",
        "per_index_node_photos_csv": output_dir / "per_index_node_photos.csv",
        "per_index_edge_photos_csv": output_dir / "per_index_edge_photos.csv",
        "isomorphism_recheck_csv": output_dir / "isomorphism_recheck.csv",
        "result_note_md": output_dir / "result_note.md",
    }

    by_candidate = {row["candidate_id"]: row for row in certification_rows}
    summary = {
        "metadata": {
            "run_id": run_config["run_id"],
            "case_id": run_config["case_id"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "created_at_local_date": datetime.now().date().isoformat(),
            "script_path": "scripts/run_bms_fu02g5g2_narrow_per_index_replay_photo_certification.py",
            "config_path": str(config_path),
        },
        "inputs": {
            "g5e1_candidates_csv": str(g5e1_path),
            "g5e2_classification_csv": str(g5e2_path),
            "g5f_revalidation_csv": str(g5f_path),
            "g5g_replay_certification_csv": str(g5g_path),
            "face_graph_edges_csv": str(graph_path),
            "targets": targets,
            "reference_carrier_nodes": reference_nodes,
        },
        "runtime": {
            "enumeration_strategy": "single pass over deterministic connected subsets; capture target_raw_index + 1 ordinal photos",
            "index_semantics": run_config.get("index_semantics", ""),
            "target_patch_size": target_patch_size,
            "max_capture_ordinal": max_capture_ordinal,
            "last_ordinal_seen": last_ordinal,
            "captured_count": len(captured),
            "target_count": len(targets),
            "elapsed_seconds": elapsed,
            "stop_reason": stop_reason,
            "full_fu02g4c_replay_certification": full_fu02g4c_replay_certification,
            "exact_original_fu02g4c_enumerator_reused": exact_original_reused,
            "full_original_input_bundle_reused": full_bundle_reused,
        },
        "certification_counts": {
            "per_index_photo_status_counts": dict(Counter(str(row["per_index_photo_status"]) for row in certification_rows)),
            "node_set_agreement_true": sum(1 for row in certification_rows if row["node_set_agreement"]),
            "edge_set_agreement_true": sum(1 for row in certification_rows if row["edge_set_agreement"]),
            "full_fu02g4c_replay_certification_true": sum(
                1 for row in certification_rows if row["full_fu02g4c_replay_certification"]
            ),
        },
        "candidate_005": by_candidate.get("candidate_005", {}),
        "candidate_008_positive_control": by_candidate.get("candidate_008", {}),
        "outputs": {key: str(path) for key, path in output_paths.items()},
        "claim_boundary": {
            "certification_control_block_only": True,
            "no_physical_emergence_claim": True,
            "no_spacetime_emergence_claim": True,
            "no_global_uniqueness_claim": True,
            "no_global_rarity_claim": True,
            "scaffold_indices_not_silently_promoted_to_fu02g4c_certified_indices": True,
        },
    }

    write_csv(output_paths["per_index_photo_certification_csv"], certification_rows, PHOTO_CERTIFICATION_FIELDS)
    write_csv(output_paths["per_index_node_photos_csv"], node_photo_rows, NODE_PHOTO_FIELDS)
    write_csv(output_paths["per_index_edge_photos_csv"], edge_photo_rows, EDGE_PHOTO_FIELDS)
    write_csv(output_paths["isomorphism_recheck_csv"], iso_rows, ISOMORPHISM_RECHECK_FIELDS)
    write_json(output_paths["summary_json"], summary)
    output_paths["result_note_md"].write_text(build_result_note(summary, certification_rows), encoding="utf-8")

    print(f"Wrote FU02g5g2 outputs to {output_dir}")
    print(f"stop_reason={stop_reason}")
    print(f"captured_count={len(captured)}")
    print(f"full_fu02g4c_replay_certification={full_fu02g4c_replay_certification}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
