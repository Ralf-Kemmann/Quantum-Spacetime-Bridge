#!/usr/bin/env python3
"""
BMS-FU01 — C60 graph builder

Builds a combinatorial C60 / truncated-icosahedral graph from an icosahedron
and writes audited node, edge, face, and manifest artifacts.

No external graph library is required.

Outputs by default:
  data/bms_fu01_c60_nodes.csv
  data/bms_fu01_c60_edges.csv
  data/bms_fu01_c60_faces.csv
  data/bms_fu01_c60_graph_manifest.json

Interpretation boundary:
  This builder creates a topological / structural C60 reference graph for
  structure-information diagnostics. It is not a quantum-chemical calculation.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

IcoVertex = int
DirectedIcoEdge = Tuple[IcoVertex, IcoVertex]
C60Edge = Tuple[str, str]


ICOSAHEDRON_FACES: List[Tuple[int, int, int]] = [
    # top cap
    (0, 1, 2),
    (0, 2, 3),
    (0, 3, 4),
    (0, 4, 5),
    (0, 5, 1),
    # belt
    (1, 6, 2),
    (2, 6, 7),
    (2, 7, 3),
    (3, 7, 8),
    (3, 8, 4),
    (4, 8, 9),
    (4, 9, 5),
    (5, 9, 10),
    (5, 10, 1),
    (1, 10, 6),
    # bottom cap
    (11, 7, 6),
    (11, 8, 7),
    (11, 9, 8),
    (11, 10, 9),
    (11, 6, 10),
]


EDGE_TYPE_WEIGHTS = {
    "5_6": 0.85,
    "6_6": 1.00,
}


def canonical_edge(a: str, b: str) -> C60Edge:
    return (a, b) if a <= b else (b, a)


def ico_edge(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def face_edges(nodes: Sequence[str]) -> List[C60Edge]:
    return [canonical_edge(nodes[i], nodes[(i + 1) % len(nodes)]) for i in range(len(nodes))]


def build_icosahedron_edges(faces: Sequence[Tuple[int, int, int]]) -> List[Tuple[int, int]]:
    edges = set()
    for a, b, c in faces:
        edges.add(ico_edge(a, b))
        edges.add(ico_edge(b, c))
        edges.add(ico_edge(c, a))
    return sorted(edges)


def validate_icosahedron(faces: Sequence[Tuple[int, int, int]]) -> Dict[str, object]:
    vertices = sorted({v for face in faces for v in face})
    edges = build_icosahedron_edges(faces)

    face_incidence = defaultdict(int)
    for a, b, c in faces:
        for u, v in [(a, b), (b, c), (c, a)]:
            e = ico_edge(u, v)
            face_incidence[e] += 1

    degree = Counter()
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1

    checks = {
        "ico_vertex_count": len(vertices),
        "ico_edge_count": len(edges),
        "ico_face_count": len(faces),
        "ico_all_degrees_5": all(degree[v] == 5 for v in vertices),
        "ico_each_edge_has_two_faces": all(face_incidence[e] == 2 for e in edges),
    }
    checks["ico_valid"] = (
        checks["ico_vertex_count"] == 12
        and checks["ico_edge_count"] == 30
        and checks["ico_face_count"] == 20
        and checks["ico_all_degrees_5"]
        and checks["ico_each_edge_has_two_faces"]
    )
    return checks


def neighbor_cycle_for_vertex(u: int, faces: Sequence[Tuple[int, int, int]]) -> List[int]:
    """Return cyclic order of the five neighbors around icosahedron vertex u.

    This uses only the local face incidence. In a valid icosahedron, the graph
    induced among the five neighbors by faces containing u is a 5-cycle.
    """
    adjacency = defaultdict(set)
    neighbors = set()

    for face in faces:
        if u not in face:
            continue
        others = [x for x in face if x != u]
        if len(others) != 2:
            raise ValueError(f"Invalid face around vertex {u}: {face}")
        a, b = others
        neighbors.update([a, b])
        adjacency[a].add(b)
        adjacency[b].add(a)

    if len(neighbors) != 5:
        raise ValueError(f"Vertex {u} has {len(neighbors)} neighbors, expected 5.")

    for n in neighbors:
        if len(adjacency[n]) != 2:
            raise ValueError(f"Neighbor graph around vertex {u} is not a cycle.")

    # Walk cycle deterministically.
    start = min(neighbors)
    # choose the smaller of two possible next nodes for stable output
    current = start
    previous = None
    order = [current]
    for _ in range(4):
        candidates = sorted(adjacency[current] - ({previous} if previous is not None else set()))
        if not candidates:
            raise ValueError(f"Broken neighbor cycle around vertex {u}.")
        nxt = candidates[0]
        previous, current = current, nxt
        order.append(current)

    # Validate closure.
    if start not in adjacency[order[-1]]:
        # Try reverse branch if initial deterministic walk picked the wrong orientation.
        current = start
        previous = None
        order = [current]
        first_neighbors = sorted(adjacency[current])
        if len(first_neighbors) != 2:
            raise ValueError(f"Broken neighbor cycle around vertex {u}.")
        current = first_neighbors[1]
        previous = start
        order.append(current)
        for _ in range(3):
            candidates = sorted(adjacency[current] - {previous})
            if not candidates:
                raise ValueError(f"Broken neighbor cycle around vertex {u}.")
            nxt = candidates[0]
            previous, current = current, nxt
            order.append(current)

    if len(order) != 5 or len(set(order)) != 5 or start not in adjacency[order[-1]]:
        raise ValueError(f"Could not derive valid 5-cycle around vertex {u}: {order}")

    return order


def build_c60_graph() -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]], Dict[str, object]]:
    ico_validation = validate_icosahedron(ICOSAHEDRON_FACES)
    if not ico_validation["ico_valid"]:
        raise ValueError(f"Invalid base icosahedron: {ico_validation}")

    ico_edges = build_icosahedron_edges(ICOSAHEDRON_FACES)

    # Each directed edge of the icosahedron becomes one C60 vertex.
    directed_edges: List[DirectedIcoEdge] = []
    for a, b in ico_edges:
        directed_edges.append((a, b))
        directed_edges.append((b, a))
    directed_edges = sorted(directed_edges)

    directed_to_node: Dict[DirectedIcoEdge, str] = {
        de: f"c60_{i:03d}" for i, de in enumerate(directed_edges, start=1)
    }

    faces: List[Dict[str, object]] = []

    # 12 pentagons around original icosahedron vertices.
    for u in sorted({v for e in ico_edges for v in e}):
        cycle = neighbor_cycle_for_vertex(u, ICOSAHEDRON_FACES)
        node_ids = [directed_to_node[(u, v)] for v in cycle]
        faces.append({
            "face_id": f"P_{u:02d}",
            "face_type": "pentagon",
            "node_ids": node_ids,
            "notes": f"Pentagon generated around original icosahedron vertex {u}.",
        })

    # 20 hexagons from original triangular faces.
    for i, (a, b, c) in enumerate(ICOSAHEDRON_FACES, start=1):
        node_ids = [
            directed_to_node[(a, b)],
            directed_to_node[(b, a)],
            directed_to_node[(b, c)],
            directed_to_node[(c, b)],
            directed_to_node[(c, a)],
            directed_to_node[(a, c)],
        ]
        faces.append({
            "face_id": f"H_{i:02d}",
            "face_type": "hexagon",
            "node_ids": node_ids,
            "notes": f"Hexagon generated from original icosahedron face {(a, b, c)}.",
        })

    # Build edge incidence from faces.
    edge_to_faces: Dict[C60Edge, List[str]] = defaultdict(list)
    face_id_to_edge_ids: Dict[str, List[str]] = {}

    for f in faces:
        for e in face_edges(f["node_ids"]):  # type: ignore[arg-type]
            edge_to_faces[e].append(str(f["face_id"]))

    sorted_c60_edges = sorted(edge_to_faces.keys())
    edge_to_id = {e: f"e_{i:03d}" for i, e in enumerate(sorted_c60_edges, start=1)}

    for f in faces:
        f_edges = face_edges(f["node_ids"])  # type: ignore[arg-type]
        face_id_to_edge_ids[str(f["face_id"])] = [edge_to_id[e] for e in f_edges]

    # Face type lookup.
    face_type = {str(f["face_id"]): str(f["face_type"]) for f in faces}

    node_face_memberships: Dict[str, List[str]] = defaultdict(list)
    for f in faces:
        for n in f["node_ids"]:  # type: ignore[union-attr]
            node_face_memberships[str(n)].append(str(f["face_id"]))

    degree = Counter()
    edge_rows: List[Dict[str, object]] = []

    for e in sorted_c60_edges:
        a, b = e
        degree[a] += 1
        degree[b] += 1
        incident_faces = sorted(edge_to_faces[e])
        incident_types = sorted(face_type[x] for x in incident_faces)
        type_key = ",".join("P" if t == "pentagon" else "H" for t in incident_types)

        if type_key == "H,H":
            edge_type = "6_6"
        elif type_key == "H,P":
            edge_type = "5_6"
        else:
            edge_type = "unknown"

        weight = EDGE_TYPE_WEIGHTS.get(edge_type, 0.0)
        distance = (1.0 / weight - 1.0) if weight > 0 else ""

        edge_rows.append({
            "edge_id": edge_to_id[e],
            "source": a,
            "target": b,
            "edge_type": edge_type,
            "source_degree": "",  # filled after all degrees known
            "target_degree": "",
            "shared_face_count": len(incident_faces),
            "shared_faces": ";".join(incident_faces),
            "shared_face_types": type_key,
            "weight": weight,
            "distance": distance,
            "comment": "C60 combinatorial edge from truncated-icosahedral construction.",
        })

    node_rows: List[Dict[str, object]] = []
    node_to_de = {node: de for de, node in directed_to_node.items()}

    for node_id in sorted(node_to_de.keys()):
        source_ico, target_ico = node_to_de[node_id]
        memberships = sorted(node_face_memberships[node_id])
        membership_types = [face_type[x] for x in memberships]
        p_count = sum(1 for t in membership_types if t == "pentagon")
        h_count = sum(1 for t in membership_types if t == "hexagon")
        node_rows.append({
            "node_id": node_id,
            "c60_index": int(node_id.split("_")[1]),
            "element_symbol": "C",
            "source_icosa_vertex": source_ico,
            "target_icosa_vertex": target_ico,
            "source_icosa_edge": f"{min(source_ico, target_ico)}-{max(source_ico, target_ico)}",
            "degree": degree[node_id],
            "pentagon_membership_count": p_count,
            "hexagon_membership_count": h_count,
            "local_face_signature": f"P{p_count}_H{h_count}",
            "orbit_label": "Ih_vertex_orbit",
            "incident_faces": ";".join(memberships),
            "notes": "C60 vertex generated from directed edge of base icosahedron.",
        })

    degree_lookup = {r["node_id"]: r["degree"] for r in node_rows}
    for r in edge_rows:
        r["source_degree"] = degree_lookup[r["source"]]
        r["target_degree"] = degree_lookup[r["target"]]

    face_rows: List[Dict[str, object]] = []
    for f in faces:
        face_rows.append({
            "face_id": f["face_id"],
            "face_type": f["face_type"],
            "node_ids": ";".join(f["node_ids"]),  # type: ignore[arg-type]
            "edge_ids": ";".join(face_id_to_edge_ids[str(f["face_id"])]),
            "notes": f["notes"],
        })

    edge_type_counts = Counter(r["edge_type"] for r in edge_rows)
    face_type_counts = Counter(r["face_type"] for r in face_rows)
    degree_counts = Counter(r["degree"] for r in node_rows)
    local_signature_counts = Counter(r["local_face_signature"] for r in node_rows)

    validation = {
        **ico_validation,
        "node_count": len(node_rows),
        "edge_count": len(edge_rows),
        "face_count": len(face_rows),
        "pentagon_count": face_type_counts.get("pentagon", 0),
        "hexagon_count": face_type_counts.get("hexagon", 0),
        "degree_counts": dict(sorted(degree_counts.items())),
        "local_face_signature_counts": dict(sorted(local_signature_counts.items())),
        "edge_type_counts": dict(sorted(edge_type_counts.items())),
        "all_node_degrees_3": all(r["degree"] == 3 for r in node_rows),
        "all_nodes_P1_H2": all(r["local_face_signature"] == "P1_H2" for r in node_rows),
        "all_edges_have_two_faces": all(r["shared_face_count"] == 2 for r in edge_rows),
        "edge_type_counts_expected": edge_type_counts.get("5_6", 0) == 60 and edge_type_counts.get("6_6", 0) == 30,
    }

    validation["c60_valid"] = (
        validation["node_count"] == 60
        and validation["edge_count"] == 90
        and validation["face_count"] == 32
        and validation["pentagon_count"] == 12
        and validation["hexagon_count"] == 20
        and validation["all_node_degrees_3"]
        and validation["all_nodes_P1_H2"]
        and validation["all_edges_have_two_faces"]
        and validation["edge_type_counts_expected"]
    )

    manifest = {
        "dataset_id": "BMS-FU01_C60_truncated_icosahedral_graph_v1",
        "builder": "scripts/build_bms_fu01_c60_graph.py",
        "construction": "Combinatorial truncation of an audited icosahedron face list.",
        "interpretation_boundary": (
            "Topological / structural C60 reference graph for structure-information "
            "diagnostics; not a quantum-chemical calculation."
        ),
        "edge_weight_rule": EDGE_TYPE_WEIGHTS,
        "validation": validation,
        "expected_counts": {
            "node_count": 60,
            "edge_count": 90,
            "face_count": 32,
            "pentagon_count": 12,
            "hexagon_count": 20,
            "edge_type_5_6": 60,
            "edge_type_6_6": 30,
            "node_degree": 3,
        },
        "warnings": [] if validation["c60_valid"] else ["C60 validation failed."],
    }

    if not validation["c60_valid"]:
        raise ValueError(json.dumps(manifest, indent=2, sort_keys=True))

    return node_rows, edge_rows, face_rows, manifest


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser(description="Build audited C60 graph artifacts for BMS-FU01.")
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Output directory. Default: data",
    )
    parser.add_argument(
        "--prefix",
        default="bms_fu01_c60",
        help="Output filename prefix. Default: bms_fu01_c60",
    )
    args = parser.parse_args()

    outdir = Path(args.output_dir)
    prefix = args.prefix

    node_rows, edge_rows, face_rows, manifest = build_c60_graph()

    node_fields = [
        "node_id",
        "c60_index",
        "element_symbol",
        "source_icosa_vertex",
        "target_icosa_vertex",
        "source_icosa_edge",
        "degree",
        "pentagon_membership_count",
        "hexagon_membership_count",
        "local_face_signature",
        "orbit_label",
        "incident_faces",
        "notes",
    ]

    edge_fields = [
        "edge_id",
        "source",
        "target",
        "edge_type",
        "source_degree",
        "target_degree",
        "shared_face_count",
        "shared_faces",
        "shared_face_types",
        "weight",
        "distance",
        "comment",
    ]

    face_fields = [
        "face_id",
        "face_type",
        "node_ids",
        "edge_ids",
        "notes",
    ]

    nodes_path = outdir / f"{prefix}_nodes.csv"
    edges_path = outdir / f"{prefix}_edges.csv"
    faces_path = outdir / f"{prefix}_faces.csv"
    manifest_path = outdir / f"{prefix}_graph_manifest.json"

    write_csv(nodes_path, node_rows, node_fields)
    write_csv(edges_path, edge_rows, edge_fields)
    write_csv(faces_path, face_rows, face_fields)

    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print(json.dumps({
        "nodes_csv": str(nodes_path),
        "edges_csv": str(edges_path),
        "faces_csv": str(faces_path),
        "manifest_json": str(manifest_path),
        "validation": manifest["validation"],
        "warnings": manifest["warnings"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
