#!/usr/bin/env python3
"""
QSB-BRIDGE-DATA-02A sp2 contrast testdata scaffold.

This script generates synthetic/reference-style benzene and C60 scaffold
tables. It uses no network access and downloads no external data.

The C60 scaffold is generated as the truncation of an icosahedron:
- one C60 node per directed icosahedron edge
- one 6_6 bond per undirected icosahedron edge
- five 5_6 bonds around each original icosahedron vertex
- one pentagon around each original icosahedron vertex
- one hexagon around each original icosahedron face

The scaffold is marked usable only if the exact C60 validation checks pass.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/QSB-BRIDGE-DATA-02A/sp2_contrast_config.json"

Vec3 = Tuple[float, float, float]
Edge = Tuple[str, str]


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def round_float(value: float, digits: int = 12) -> float:
    if abs(value) < 0.5 * 10 ** (-digits):
        return 0.0
    return round(value, digits)


def vec_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_scale(scalar: float, a: Vec3) -> Vec3:
    return (scalar * a[0], scalar * a[1], scalar * a[2])


def normalize(a: Vec3) -> Vec3:
    norm = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    return (a[0] / norm, a[1] / norm, a[2] / norm)


def canonical_edge(a: str, b: str) -> Edge:
    return (a, b) if a < b else (b, a)


def build_benzene() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    radius = 1.0
    for idx in range(6):
        angle = 2.0 * math.pi * idx / 6.0
        nodes.append(
            {
                "node_id": f"Bz_{idx:02d}",
                "system_id": "benzene",
                "atom_label": "C",
                "sp2_role": "planar_aromatic_carbon",
                "ring_index": idx,
                "x_ref": round_float(radius * math.cos(angle)),
                "y_ref": round_float(radius * math.sin(angle)),
                "z_ref": 0.0,
                "curvature_label": "planar",
                "local_environment_label": "uniform_aromatic_ring",
                "claim_role": "reference_control_only",
            }
        )
    for idx in range(6):
        source = f"Bz_{idx:02d}"
        target = f"Bz_{(idx + 1) % 6:02d}"
        edges.append(
            {
                "edge_id": f"Bz_e_{idx:02d}",
                "system_id": "benzene",
                "source": source,
                "target": target,
                "bond_class": "aromatic_uniform",
                "bond_order_proxy": 1.5,
                "edge_family": "benzene_uniform_aromatic_proxy",
                "is_ring_edge": "true",
                "reference_control_role": "synthetic_reference_control_only",
            }
        )
    return nodes, edges


def icosahedron_vertices() -> List[Vec3]:
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    raw = [
        (-1.0, phi, 0.0),
        (1.0, phi, 0.0),
        (-1.0, -phi, 0.0),
        (1.0, -phi, 0.0),
        (0.0, -1.0, phi),
        (0.0, 1.0, phi),
        (0.0, -1.0, -phi),
        (0.0, 1.0, -phi),
        (phi, 0.0, -1.0),
        (phi, 0.0, 1.0),
        (-phi, 0.0, -1.0),
        (-phi, 0.0, 1.0),
    ]
    return [normalize(vertex) for vertex in raw]


def icosahedron_faces() -> List[Tuple[int, int, int]]:
    return [
        (0, 11, 5),
        (0, 5, 1),
        (0, 1, 7),
        (0, 7, 10),
        (0, 10, 11),
        (1, 5, 9),
        (5, 11, 4),
        (11, 10, 2),
        (10, 7, 6),
        (7, 1, 8),
        (3, 9, 4),
        (3, 4, 2),
        (3, 2, 6),
        (3, 6, 8),
        (3, 8, 9),
        (4, 9, 5),
        (2, 4, 11),
        (6, 2, 10),
        (8, 6, 7),
        (9, 8, 1),
    ]


def face_normal(points: Sequence[Vec3], face: Sequence[int]) -> Vec3:
    a, b, c = [points[idx] for idx in face[:3]]
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ac = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
    return (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )


def orient_faces_outward(points: Sequence[Vec3], faces: Sequence[Tuple[int, int, int]]) -> List[Tuple[int, int, int]]:
    oriented: List[Tuple[int, int, int]] = []
    for face in faces:
        normal = face_normal(points, face)
        center = normalize(
            (
                points[face[0]][0] + points[face[1]][0] + points[face[2]][0],
                points[face[0]][1] + points[face[1]][1] + points[face[2]][1],
                points[face[0]][2] + points[face[1]][2] + points[face[2]][2],
            )
        )
        dot = normal[0] * center[0] + normal[1] * center[1] + normal[2] * center[2]
        oriented.append(face if dot > 0 else (face[0], face[2], face[1]))
    return oriented


def order_neighbors_around_vertex(center_idx: int, neighbors: Sequence[int], points: Sequence[Vec3]) -> List[int]:
    center = points[center_idx]
    axis = normalize(center)
    reference = points[neighbors[0]]
    tangent_x = normalize(
        (
            reference[0] - axis[0] * (reference[0] * axis[0] + reference[1] * axis[1] + reference[2] * axis[2]),
            reference[1] - axis[1] * (reference[0] * axis[0] + reference[1] * axis[1] + reference[2] * axis[2]),
            reference[2] - axis[2] * (reference[0] * axis[0] + reference[1] * axis[1] + reference[2] * axis[2]),
        )
    )
    tangent_y = (
        axis[1] * tangent_x[2] - axis[2] * tangent_x[1],
        axis[2] * tangent_x[0] - axis[0] * tangent_x[2],
        axis[0] * tangent_x[1] - axis[1] * tangent_x[0],
    )
    keyed = []
    for neighbor in neighbors:
        vec = points[neighbor]
        x = vec[0] * tangent_x[0] + vec[1] * tangent_x[1] + vec[2] * tangent_x[2]
        y = vec[0] * tangent_y[0] + vec[1] * tangent_y[1] + vec[2] * tangent_y[2]
        keyed.append((math.atan2(y, x), neighbor))
    return [neighbor for _, neighbor in sorted(keyed)]


def build_c60() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    points = icosahedron_vertices()
    faces_ico = orient_faces_outward(points, icosahedron_faces())

    ico_edges = sorted({tuple(sorted((a, b))) for face in faces_ico for a, b in [(face[0], face[1]), (face[1], face[2]), (face[2], face[0])]})
    adjacency: Dict[int, List[int]] = defaultdict(list)
    for a, b in ico_edges:
        adjacency[a].append(b)
        adjacency[b].append(a)

    directed_pairs = sorted((a, b) for a, b in [(a, b) for a, b in ico_edges] + [(b, a) for a, b in ico_edges])
    node_id_by_pair = {pair: f"C60_{idx:02d}" for idx, pair in enumerate(directed_pairs)}

    nodes: List[Dict[str, Any]] = []
    for pair in directed_pairs:
        idx = int(node_id_by_pair[pair].split("_")[1])
        a, b = pair
        coord = normalize(vec_add(vec_scale(2.0 / 3.0, points[a]), vec_scale(1.0 / 3.0, points[b])))
        nodes.append(
            {
                "node_id": node_id_by_pair[pair],
                "system_id": "c60",
                "atom_label": "C",
                "sp2_role": "fullerene_sp2_carbon",
                "degree_target": 3,
                "x_ref": round_float(coord[0]),
                "y_ref": round_float(coord[1]),
                "z_ref": round_float(coord[2]),
                "curvature_label": "curved_fullerene_reference",
                "local_environment_label": "one_pentagon_two_hexagon_vertex",
                "claim_role": "reference_control_only",
                "_sort": idx,
            }
        )

    edge_map: Dict[Edge, Dict[str, Any]] = {}
    edge_faces: Dict[Edge, List[str]] = defaultdict(list)

    for a, b in ico_edges:
        edge = canonical_edge(node_id_by_pair[(a, b)], node_id_by_pair[(b, a)])
        edge_map[edge] = {
            "system_id": "c60",
            "source": edge[0],
            "target": edge[1],
            "bond_class": "6_6",
            "bond_order_proxy": 1.40,
            "edge_family": "c60_bond_class_weighted_proxy",
            "face_pair_type": "hexagon_hexagon",
            "reference_control_role": "synthetic_reference_control_only",
        }
        edge_faces[edge].extend(["hexagon", "hexagon"])

    pentagon_faces: List[List[str]] = []
    for center_idx in range(12):
        ordered_neighbors = order_neighbors_around_vertex(center_idx, adjacency[center_idx], points)
        face_nodes = [node_id_by_pair[(center_idx, neighbor)] for neighbor in ordered_neighbors]
        pentagon_faces.append(face_nodes)
        for idx, source in enumerate(face_nodes):
            target = face_nodes[(idx + 1) % len(face_nodes)]
            edge = canonical_edge(source, target)
            edge_map[edge] = {
                "system_id": "c60",
                "source": edge[0],
                "target": edge[1],
                "bond_class": "5_6",
                "bond_order_proxy": 1.45,
                "edge_family": "c60_bond_class_weighted_proxy",
                "face_pair_type": "pentagon_hexagon",
                "reference_control_role": "synthetic_reference_control_only",
            }
            edge_faces[edge].append("pentagon")

    hexagon_faces: List[List[str]] = []
    for face in faces_ico:
        a, b, c = face
        face_nodes = [
            node_id_by_pair[(a, b)],
            node_id_by_pair[(b, a)],
            node_id_by_pair[(b, c)],
            node_id_by_pair[(c, b)],
            node_id_by_pair[(c, a)],
            node_id_by_pair[(a, c)],
        ]
        hexagon_faces.append(face_nodes)
        for idx, source in enumerate(face_nodes):
            target = face_nodes[(idx + 1) % len(face_nodes)]
            edge_faces[canonical_edge(source, target)].append("hexagon")

    edges: List[Dict[str, Any]] = []
    for idx, edge in enumerate(sorted(edge_map)):
        row = dict(edge_map[edge])
        row["edge_id"] = f"C60_e_{idx:03d}"
        edges.append(row)

    edge_id_by_nodes = {canonical_edge(row["source"], row["target"]): row["edge_id"] for row in edges}

    faces: List[Dict[str, Any]] = []
    for idx, face_nodes in enumerate(pentagon_faces):
        face_edges = [
            edge_id_by_nodes[canonical_edge(face_nodes[i], face_nodes[(i + 1) % len(face_nodes)])]
            for i in range(len(face_nodes))
        ]
        faces.append(
            {
                "face_id": f"C60_f_pentagon_{idx:02d}",
                "system_id": "c60",
                "face_type": "pentagon",
                "node_ids": ";".join(face_nodes),
                "edge_ids": ";".join(face_edges),
                "face_size": 5,
                "local_environment_label": "pentagon_surrounded_by_hexagons",
                "claim_role": "reference_control_only",
            }
        )
    for idx, face_nodes in enumerate(hexagon_faces):
        face_edges = [
            edge_id_by_nodes[canonical_edge(face_nodes[i], face_nodes[(i + 1) % len(face_nodes)])]
            for i in range(len(face_nodes))
        ]
        faces.append(
            {
                "face_id": f"C60_f_hexagon_{idx:02d}",
                "system_id": "c60",
                "face_type": "hexagon",
                "node_ids": ";".join(face_nodes),
                "edge_ids": ";".join(face_edges),
                "face_size": 6,
                "local_environment_label": "hexagon_with_three_pentagon_and_three_hexagon_edges",
                "claim_role": "reference_control_only",
            }
        )

    for node in nodes:
        node.pop("_sort", None)

    validation = validate_c60(nodes, edges, faces)
    return nodes, edges, faces, validation


def degree_distribution(edges: Sequence[Dict[str, Any]]) -> Dict[int, int]:
    degree: Counter[str] = Counter()
    for edge in edges:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    return dict(sorted(Counter(degree.values()).items()))


def validate_benzene(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    degree = Counter()
    for edge in edges:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    all_degrees_two = all(degree[node["node_id"]] == 2 for node in nodes)
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "degree_distribution": dict(sorted(Counter(degree.values()).items())),
        "all_degrees_2": all_degrees_two,
        "passed": len(nodes) == 6 and len(edges) == 6 and all_degrees_two,
    }


def validate_c60(
    nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]], faces: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    degree = Counter()
    for edge in edges:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    face_counts = Counter(face["face_type"] for face in faces)
    bond_counts = Counter(edge["bond_class"] for edge in edges)
    euler = len(nodes) - len(edges) + len(faces)
    all_degrees_three = all(degree[node["node_id"]] == 3 for node in nodes)
    passed = (
        len(nodes) == 60
        and len(edges) == 90
        and all_degrees_three
        and len(faces) == 32
        and face_counts.get("pentagon", 0) == 12
        and face_counts.get("hexagon", 0) == 20
        and euler == 2
        and bond_counts.get("6_6", 0) == 30
        and bond_counts.get("5_6", 0) == 60
    )
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "degree_distribution": dict(sorted(Counter(degree.values()).items())),
        "all_degrees_3": all_degrees_three,
        "face_count": len(faces),
        "pentagon_count": face_counts.get("pentagon", 0),
        "hexagon_count": face_counts.get("hexagon", 0),
        "euler_characteristic": euler,
        "bond_class_counts": dict(sorted(bond_counts.items())),
        "passed": passed,
    }


def count_by(rows: Sequence[Dict[str, Any]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def build_family_summary(
    benzene_nodes: Sequence[Dict[str, Any]],
    benzene_edges: Sequence[Dict[str, Any]],
    c60_nodes: Sequence[Dict[str, Any]],
    c60_edges: Sequence[Dict[str, Any]],
    c60_faces: Sequence[Dict[str, Any]],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    benzene_validation = validate_benzene(benzene_nodes, benzene_edges)
    c60_validation = validate_c60(c60_nodes, c60_edges, c60_faces)
    rows = []
    for family in config["families"]:
        if family.startswith("benzene"):
            system = "benzene"
            node_count = len(benzene_nodes)
            edge_count = len(benzene_edges)
            degree_dist = benzene_validation["degree_distribution"]
            aromatic_flag = "true" if family == "benzene_uniform_aromatic_proxy" else "control_or_reference"
            contrast = "planar_six_node_sp2_ring_scaffold"
        elif family.startswith("c60"):
            system = "c60"
            node_count = len(c60_nodes)
            edge_count = len(c60_edges)
            degree_dist = c60_validation["degree_distribution"]
            aromatic_flag = "not_applicable_curved_cage"
            contrast = "curved_sixty_node_sp2_cage_scaffold"
        else:
            system = "control"
            node_count = "declared_control_family"
            edge_count = "declared_control_family"
            degree_dist = "declared_control_family"
            aromatic_flag = "control"
            contrast = "declared_control_no_external_data"
        rows.append(
            {
                "family_id": family,
                "system_id": system,
                "node_count": node_count,
                "edge_count": edge_count,
                "degree_distribution": json.dumps(degree_dist, sort_keys=True),
                "aromatic_uniformity_flag": aromatic_flag,
                "curvature_proxy_summary": contrast,
                "proxy_smuggling_risk": "reference_control_or_synthetic_label_only",
                "benzene_vs_c60_contrast_summary": "method_level_planar_ring_vs_curved_cage_scaffold_only",
            }
        )
    return rows


def build_bond_class_summary(
    benzene_edges: Sequence[Dict[str, Any]], c60_edges: Sequence[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    rows = []
    for system_id, edges in [("benzene", benzene_edges), ("c60", c60_edges)]:
        for bond_class, count in count_by(edges, "bond_class").items():
            rows.append(
                {
                    "system_id": system_id,
                    "bond_class": bond_class,
                    "bond_class_count": count,
                    "reference_control_role": "synthetic_reference_control_only",
                    "notes": "controlled scaffold bond label; not validation",
                }
            )
    return rows


def build_face_environment_summary(c60_faces: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = [
        {
            "system_id": "benzene",
            "face_type": "planar_ring_placeholder",
            "face_count": 1,
            "local_environment_label": "single_planar_six_member_ring_reference",
            "claim_role": "reference_control_only",
        }
    ]
    grouped = Counter((face["face_type"], face["local_environment_label"]) for face in c60_faces)
    for (face_type, label), count in sorted(grouped.items()):
        rows.append(
            {
                "system_id": "c60",
                "face_type": face_type,
                "face_count": count,
                "local_environment_label": label,
                "claim_role": "reference_control_only",
            }
        )
    return rows


def build_proxy_risk_summary(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for proxy in config["proxy_families"]:
        rows.append(
            {
                "proxy_id": proxy["proxy_id"],
                "intended_use": proxy["intended_use"],
                "geometry_smuggling_risk": proxy["geometry_smuggling_risk"],
                "claim_boundary": proxy["claim_boundary"],
                "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            }
        )
    return rows


def markdown_table(headers: List[str], rows: List[Dict[str, Any]]) -> str:
    lines = [
        "|" + "|".join(headers) + "|",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(header, "")).replace("\n", " ") for header in headers) + "|")
    return "\n".join(lines)


def build_manifest(
    config: Dict[str, Any],
    benzene_validation: Dict[str, Any],
    c60_validation: Dict[str, Any],
    stop_go_outcome: str,
) -> Dict[str, Any]:
    data_dir = config["data_dir"]
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "external_data_downloaded": False,
        "stop_go_outcome": stop_go_outcome,
        "systems": ["benzene", "c60"],
        "families": config["families"],
        "proxy_families": config["proxy_families"],
        "tables": {
            "benzene_nodes": f"{data_dir}/benzene_nodes.csv",
            "benzene_edges": f"{data_dir}/benzene_edges.csv",
            "c60_nodes": f"{data_dir}/c60_nodes.csv",
            "c60_edges": f"{data_dir}/c60_edges.csv",
            "c60_faces": f"{data_dir}/c60_faces.csv",
        },
        "benzene_validation": benzene_validation,
        "c60_validation": c60_validation,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
    }


def build_readout(summary: Dict[str, Any], proxy_rows: List[Dict[str, Any]]) -> str:
    proxy_headers = ["proxy_id", "intended_use", "geometry_smuggling_risk", "claim_boundary"]
    c60 = summary["c60_validation"]
    benzene = summary["benzene_validation"]
    return "\n".join(
        [
            "# QSB-BRIDGE-DATA-02A Run Readout",
            "",
            "## Run",
            "",
            "```text",
            f"block_id: {summary['block_id']}",
            f"run_id: {summary['run_id']}",
            f"stop_go_outcome: {summary['stop_go_outcome']}",
            f"external_data_downloaded: {str(summary['external_data_downloaded']).lower()}",
            "```",
            "",
            "## Claim Boundary",
            "",
            "DATA-02A is a synthetic/reference-style scaffold only.",
            "",
            "It is not real-data validation, physical validation, or molecular validation.",
            "",
            "## Benzene Checks",
            "",
            "```text",
            f"node_count: {benzene['node_count']}",
            f"edge_count: {benzene['edge_count']}",
            f"degree_distribution: {benzene['degree_distribution']}",
            f"passed: {benzene['passed']}",
            "```",
            "",
            "## C60 Exact Scaffold Checks",
            "",
            "```text",
            f"node_count: {c60['node_count']}",
            f"edge_count: {c60['edge_count']}",
            f"degree_distribution: {c60['degree_distribution']}",
            f"all_degrees_3: {c60['all_degrees_3']}",
            f"face_count: {c60['face_count']}",
            f"pentagon_count: {c60['pentagon_count']}",
            f"hexagon_count: {c60['hexagon_count']}",
            f"euler_characteristic: {c60['euler_characteristic']}",
            f"bond_class_counts: {c60['bond_class_counts']}",
            f"passed: {c60['passed']}",
            "```",
            "",
            "## Proxy Risk Summary",
            "",
            markdown_table(proxy_headers, proxy_rows),
            "",
            "Coordinate- and graph-derived kernels are labeled reference/control only. They are not independent evidence.",
            "",
            "## 05C Warning Carried Forward",
            "",
            summary["qsb_bridge_num_05c_warning"],
            "",
            "## Future Result Discussion Requirement",
            "",
            "Create a separate DATA-02A result discussion only after reading these outputs. It must include a human-readable Bauchbild and remain scaffold-only, defensive, and method-level.",
            "",
            "A useful Bauchbild: benzene is the small flat ring tile, C60 is the exact curved cage tile, and DATA-02A checks the labels and controls on the bench before any real molecular-data claim is allowed.",
            "",
        ]
    )


def main() -> None:
    config = load_json(CONFIG_PATH)
    data_dir = project_path(config["data_dir"])
    output_dir = project_path(config["output_dir"])

    benzene_nodes, benzene_edges = build_benzene()
    c60_nodes, c60_edges, c60_faces, c60_validation = build_c60()
    benzene_validation = validate_benzene(benzene_nodes, benzene_edges)

    stop_go_outcome = (
        "go_scaffold_generated_with_exact_c60_validation"
        if benzene_validation["passed"] and c60_validation["passed"]
        else "requires_exact_c60_scaffold_before_use"
    )

    manifest = build_manifest(config, benzene_validation, c60_validation, stop_go_outcome)
    family_rows = build_family_summary(benzene_nodes, benzene_edges, c60_nodes, c60_edges, c60_faces, config)
    bond_rows = build_bond_class_summary(benzene_edges, c60_edges)
    face_rows = build_face_environment_summary(c60_faces)
    proxy_rows = build_proxy_risk_summary(config)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "external_data_downloaded": False,
        "network_policy": config["network_policy"],
        "stop_go_outcome": stop_go_outcome,
        "no_realdata_validation_claim": True,
        "no_physical_validation_claim": True,
        "no_molecular_validation_claim": True,
        "benzene_validation": benzene_validation,
        "c60_validation": c60_validation,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
    }

    write_csv(
        data_dir / "benzene_nodes.csv",
        [
            "node_id",
            "system_id",
            "atom_label",
            "sp2_role",
            "ring_index",
            "x_ref",
            "y_ref",
            "z_ref",
            "curvature_label",
            "local_environment_label",
            "claim_role",
        ],
        benzene_nodes,
    )
    write_csv(
        data_dir / "benzene_edges.csv",
        [
            "edge_id",
            "system_id",
            "source",
            "target",
            "bond_class",
            "bond_order_proxy",
            "edge_family",
            "is_ring_edge",
            "reference_control_role",
        ],
        benzene_edges,
    )
    write_csv(
        data_dir / "c60_nodes.csv",
        [
            "node_id",
            "system_id",
            "atom_label",
            "sp2_role",
            "degree_target",
            "x_ref",
            "y_ref",
            "z_ref",
            "curvature_label",
            "local_environment_label",
            "claim_role",
        ],
        c60_nodes,
    )
    write_csv(
        data_dir / "c60_edges.csv",
        [
            "edge_id",
            "system_id",
            "source",
            "target",
            "bond_class",
            "bond_order_proxy",
            "edge_family",
            "face_pair_type",
            "reference_control_role",
        ],
        c60_edges,
    )
    write_csv(
        data_dir / "c60_faces.csv",
        [
            "face_id",
            "system_id",
            "face_type",
            "node_ids",
            "edge_ids",
            "face_size",
            "local_environment_label",
            "claim_role",
        ],
        c60_faces,
    )
    write_json(data_dir / "sp2_contrast_manifest.json", manifest)

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "resolved_config.json", config)
    write_csv(
        output_dir / "sp2_family_summary.csv",
        [
            "family_id",
            "system_id",
            "node_count",
            "edge_count",
            "degree_distribution",
            "aromatic_uniformity_flag",
            "curvature_proxy_summary",
            "proxy_smuggling_risk",
            "benzene_vs_c60_contrast_summary",
        ],
        family_rows,
    )
    write_csv(
        output_dir / "bond_class_summary.csv",
        ["system_id", "bond_class", "bond_class_count", "reference_control_role", "notes"],
        bond_rows,
    )
    write_csv(
        output_dir / "face_environment_summary.csv",
        ["system_id", "face_type", "face_count", "local_environment_label", "claim_role"],
        face_rows,
    )
    write_csv(
        output_dir / "proxy_risk_summary.csv",
        [
            "proxy_id",
            "intended_use",
            "geometry_smuggling_risk",
            "claim_boundary",
            "qsb_bridge_num_05c_warning",
        ],
        proxy_rows,
    )
    (output_dir / "readout.md").write_text(build_readout(summary, proxy_rows), encoding="utf-8")


if __name__ == "__main__":
    main()
