#!/usr/bin/env python3
"""
BMS-FU02g5d - Automorphy-Only Role Transport Check

This runner transports FU02f1 reference roles to a candidate patch only through
explicit face-type-preserving isomorphisms between induced face subgraphs.

Claim boundary: combinatorial / methodological control only. No physical
emergence, spacetime, uniqueness, or Lorentz claim is made.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: PyYAML. Install it in the project environment."
    ) from exc

try:
    import networkx as nx  # type: ignore
    from networkx.algorithms import isomorphism as iso  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: networkx. Install it in the project environment."
    ) from exc


ROLE_MIXED_CORE = "mixed_core"
ROLE_PENTAGON_BOUNDARY = "pentagon_boundary"
ROLE_CARRIER_OTHER = "carrier_other"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMS-FU02g5d automorphy-only role transport check."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bms_fu02g5d_automorphy_only_role_transport_config.yaml",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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


def resolve_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return repo_root / path


def read_face_edge_csv(path: Path) -> "nx.Graph":
    if not path.exists():
        raise FileNotFoundError(f"Face adjacency CSV not found: {path}")

    graph = nx.Graph()
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
            graph.add_node(face_a, face_type=face_type(face_a))
            graph.add_node(face_b, face_type=face_type(face_b))
            graph.add_edge(face_a, face_b)

    return graph


def validate_nodes(graph: "nx.Graph", nodes: Sequence[str], label: str) -> List[str]:
    warnings: List[str] = []
    duplicates = sorted({node for node in nodes if nodes.count(node) > 1})
    if duplicates:
        warnings.append(f"{label}: duplicate nodes: {duplicates}")
    missing = sorted(set(nodes) - set(graph.nodes()))
    if missing:
        warnings.append(f"{label}: nodes missing from full graph: {missing}")
    present = [node for node in nodes if node in graph.nodes()]
    if present:
        subgraph = graph.subgraph(present)
        if not nx.is_connected(subgraph):
            warnings.append(f"{label}: induced subgraph is not connected")
    return warnings


def induced_subgraph(graph: "nx.Graph", nodes: Sequence[str]) -> "nx.Graph":
    subgraph = graph.subgraph(nodes).copy()
    for node in subgraph.nodes():
        subgraph.nodes[node]["face_type"] = face_type(node)
    return subgraph


def graph_stats(graph: "nx.Graph") -> dict:
    counts: Dict[str, int] = {}
    for node in graph.nodes():
        ft = face_type(str(node))
        counts[ft] = counts.get(ft, 0) + 1
    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "connected": bool(nx.is_connected(graph)) if graph.number_of_nodes() else False,
        "face_type_counts": counts,
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


def enumerate_mappings(
    reference_subgraph: "nx.Graph",
    candidate_subgraph: "nx.Graph",
) -> List[Dict[str, str]]:
    node_match = iso.categorical_node_match("face_type", None)
    matcher = iso.GraphMatcher(reference_subgraph, candidate_subgraph, node_match=node_match)
    return [{str(k): str(v) for k, v in mapping.items()} for mapping in matcher.isomorphisms_iter()]


def write_mappings_csv(
    path: Path,
    mappings: Sequence[Mapping[str, str]],
    reference_nodes: Sequence[str],
    mixed_core_nodes: Set[str],
    pentagon_boundary_nodes: Set[str],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "mapping_index",
                "reference_node",
                "candidate_node",
                "reference_face_type",
                "candidate_face_type",
                "transported_role",
            ],
        )
        writer.writeheader()
        for mapping_index, mapping in enumerate(mappings):
            for reference_node in sorted_nodes(reference_nodes):
                candidate_node = mapping.get(reference_node, "")
                writer.writerow(
                    {
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


def transported_sets_for_mapping(
    mapping: Mapping[str, str],
    mixed_core_nodes: Set[str],
    pentagon_boundary_nodes: Set[str],
) -> Tuple[List[str], List[str]]:
    mixed = [mapping[node] for node in mixed_core_nodes if node in mapping]
    boundary = [mapping[node] for node in pentagon_boundary_nodes if node in mapping]
    return sorted_nodes(mixed), sorted_nodes(boundary)


def write_transported_role_sets_csv(
    path: Path,
    mappings: Sequence[Mapping[str, str]],
    mixed_core_nodes: Set[str],
    pentagon_boundary_nodes: Set[str],
) -> Tuple[Set[str], Set[str]]:
    mixed_keys: Set[str] = set()
    boundary_keys: Set[str] = set()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "mapping_index",
                "mixed_core_nodes",
                "pentagon_boundary_nodes",
                "mixed_core_key",
                "pentagon_boundary_key",
            ],
        )
        writer.writeheader()
        for mapping_index, mapping in enumerate(mappings):
            mixed, boundary = transported_sets_for_mapping(
                mapping, mixed_core_nodes, pentagon_boundary_nodes
            )
            mixed_key = set_key(mixed)
            boundary_key = set_key(boundary)
            mixed_keys.add(mixed_key)
            boundary_keys.add(boundary_key)
            writer.writerow(
                {
                    "mapping_index": mapping_index,
                    "mixed_core_nodes": mixed_key,
                    "pentagon_boundary_nodes": boundary_key,
                    "mixed_core_key": mixed_key,
                    "pentagon_boundary_key": boundary_key,
                }
            )
    return mixed_keys, boundary_keys


def invariant_flag(mapping_count: int, unique_set_count: int):
    if mapping_count == 0:
        return None
    return unique_set_count == 1


def build_result_note(summary: dict) -> str:
    mapping_count = summary["isomorphism"]["mapping_count"]
    transport_allowed = summary["role_transport"]["transport_allowed"]
    mixed_invariant = summary["role_transport"]["mixed_core_invariant_across_mappings"]
    boundary_invariant = summary["role_transport"][
        "pentagon_boundary_invariant_across_mappings"
    ]

    return f"""# BMS-FU02g5d - Automorphy-Only Role Transport Result Note

Datum: {summary["metadata"]["created_at_utc"][:10]}

## Befund

Der Runner hat die FU02f1-Referenz und den lokalisierten Kandidaten als
induzierte Teilgraphen des C60-Face-Graphen verglichen.

```text
mapping_count = {mapping_count}
transport_allowed = {str(transport_allowed).lower()}
mixed_core_invariant_across_mappings = {mixed_invariant}
pentagon_boundary_invariant_across_mappings = {boundary_invariant}
```

## Interpretation

Rollen-Transport ist in diesem Block nur ueber explizite
face-type-preserving Isomorphismen zulaessig. Falls `mapping_count = 0` ist,
werden keine `mixed_core`- oder `pentagon_boundary`-Rollen auf den Kandidaten
uebertragen.

Falls mehrere Mappings existieren, ist die Mehrdeutigkeit sichtbar zu halten.
Die Invarianzfelder zeigen, ob alle Mappings dieselben transportierten
Rollensets liefern.

## Hypothese

Wenn die transportierten Rollensets ueber alle Mappings invariant sind, kann
die automorphy-only Rollenlesart fuer diesen Kandidaten als methodisch stabil
behandelt werden. Wenn sie nicht invariant sind, bleibt die Rollenlesart
mapping-abhaengig.

## Offene Luecke

Dieser Lauf ersetzt keine lokale strukturelle Rollen-Transportregel fuer
nicht-isomorphe Patches. Ohne Mapping bleibt der Kandidat uncolored oder
face_type-only zu lesen.

## Claim Boundary

Sauber behauptbar ist nur ein kombinatorisch-methodischer Transportcheck.

Nicht behaupten:

```text
physikalische Emergenz
Raumzeit-Entstehung
Eindeutigkeit ausserhalb der getesteten Graphabbildungen
Lorentz-Kompatibilitaet
dynamische Notwendigkeit
```
"""


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    config_path = resolve_path(repo_root, args.config)
    config = load_yaml(config_path)

    run_config = config["run"]
    input_config = config["input"]
    output_dir = resolve_path(repo_root, run_config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    graph_path = resolve_path(repo_root, input_config["full_face_graph_edges_csv"])
    full_graph = read_face_edge_csv(graph_path)

    reference_nodes = [str(node) for node in input_config["reference_carrier_nodes"]]
    mixed_core_nodes = {
        str(node) for node in input_config["reference_mixed_core_nodes"]
    }
    pentagon_boundary_nodes = {
        str(node) for node in input_config["reference_pentagon_boundary_nodes"]
    }
    candidate_nodes = [str(node) for node in input_config["candidate_patch_nodes"]]

    warnings: List[str] = []
    warnings.extend(validate_nodes(full_graph, reference_nodes, "reference_carrier"))
    warnings.extend(validate_nodes(full_graph, candidate_nodes, "candidate_patch"))
    if not mixed_core_nodes <= set(reference_nodes):
        warnings.append("reference_mixed_core_nodes is not a subset of reference_carrier_nodes")
    if not pentagon_boundary_nodes <= set(reference_nodes):
        warnings.append(
            "reference_pentagon_boundary_nodes is not a subset of reference_carrier_nodes"
        )
    overlap = mixed_core_nodes & pentagon_boundary_nodes
    if overlap:
        warnings.append(f"reference role sets overlap: {sorted_nodes(overlap)}")

    reference_subgraph = induced_subgraph(full_graph, reference_nodes)
    candidate_subgraph = induced_subgraph(full_graph, candidate_nodes)
    mappings = enumerate_mappings(reference_subgraph, candidate_subgraph)
    mapping_count = len(mappings)

    mixed_keys, boundary_keys = write_transported_role_sets_csv(
        output_dir / "transported_role_sets.csv",
        mappings,
        mixed_core_nodes,
        pentagon_boundary_nodes,
    )
    write_mappings_csv(
        output_dir / "mappings.csv",
        mappings,
        reference_nodes,
        mixed_core_nodes,
        pentagon_boundary_nodes,
    )

    summary = {
        "metadata": {
            "run_id": run_config["run_id"],
            "case_id": run_config["case_id"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "script": "scripts/run_bms_fu02g5d_automorphy_only_role_transport.py",
        },
        "input": {
            "config_path": str(config_path),
            "full_face_graph_edges_csv": str(graph_path),
            "reference_carrier_nodes": sorted_nodes(reference_nodes),
            "reference_mixed_core_nodes": sorted_nodes(mixed_core_nodes),
            "reference_pentagon_boundary_nodes": sorted_nodes(pentagon_boundary_nodes),
            "candidate_patch_nodes": sorted_nodes(candidate_nodes),
        },
        "graph": {
            "full_node_count": full_graph.number_of_nodes(),
            "full_edge_count": full_graph.number_of_edges(),
            "reference": graph_stats(reference_subgraph),
            "candidate": graph_stats(candidate_subgraph),
        },
        "isomorphism": {
            "method": "networkx.algorithms.isomorphism.GraphMatcher",
            "node_match": "face_type",
            "mapping_exists": mapping_count > 0,
            "mapping_count": mapping_count,
        },
        "role_transport": {
            "transport_allowed": mapping_count > 0,
            "rule": "transport roles only along explicit face-type-preserving isomorphisms",
            "unique_mixed_core_set_count": len(mixed_keys),
            "unique_pentagon_boundary_set_count": len(boundary_keys),
            "unique_mixed_core_sets": sorted(mixed_keys),
            "unique_pentagon_boundary_sets": sorted(boundary_keys),
            "mixed_core_invariant_across_mappings": invariant_flag(
                mapping_count, len(mixed_keys)
            ),
            "pentagon_boundary_invariant_across_mappings": invariant_flag(
                mapping_count, len(boundary_keys)
            ),
        },
        "warnings": warnings,
        "claim_boundary": {
            "physical_emergence_claim": False,
            "spacetime_claim": False,
            "uniqueness_claim": False,
            "lorentz_claim": False,
        },
    }

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    result_note = build_result_note(summary)
    with (output_dir / "result_note.md").open("w", encoding="utf-8") as handle:
        handle.write(result_note)

    print(
        "BMS-FU02g5d complete: "
        f"mapping_count={mapping_count}, output_dir={output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
