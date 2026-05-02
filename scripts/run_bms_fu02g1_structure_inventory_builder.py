#!/usr/bin/env python3
"""
BMS-FU02g1 — Structure Inventory Builder

Purpose:
  Build transparent graph/cell inventory artifacts for real-structure memory
  and symmetry-control tests.

Scope:
  This is not a chemical/electronic-structure model. Generated coordinates are
  inspection/layout coordinates only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


NODE_FIELDS = [
    "structure_id", "node_id", "source_node_id", "degree", "boundary_node", "periodic_node",
    "layout_x", "layout_y", "layout_z", "node_role_hint", "coordinate_status",
]
EDGE_FIELDS = [
    "structure_id", "edge_id", "source", "target", "source_source_id", "target_source_id",
    "edge_class", "boundary_edge", "periodic_edge", "cell_left", "cell_right", "cell_count",
    "edge_role_hint",
]
CELL_FIELDS = [
    "structure_id", "cell_id", "source_cell_id", "cell_type", "node_ids", "edge_ids",
    "boundary_cell", "periodic_cell", "cell_role_hint", "layout_x", "layout_y", "layout_z",
    "coordinate_status",
]
INVENTORY_FIELDS = [
    "structure_id", "structure_class", "geometry_class", "node_count", "edge_count", "cell_count",
    "boundary_present", "boundary_node_count", "boundary_edge_count", "periodic_dimension_count",
    "closure_class", "curvature_class", "pentagon_present", "hexagon_present", "chirality_label",
    "inversion_flag", "rotation_symmetry_label", "reflection_flag", "screw_symmetry_flag",
    "source_type", "source_note", "layout_coordinate_status", "diagnostic_scope_note",
]


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def parse_list_like(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    s = s.strip("[](){}")
    parts = re.split(r"[;,|\s]+", s)
    return [p.strip().strip("'\"") for p in parts if p.strip().strip("'\"")]


def edge_id(a: str, b: str) -> str:
    return f"{a}--{b}" if a <= b else f"{b}--{a}"


def degree_histogram(edges: List[Dict[str, Any]], node_ids: Iterable[str]) -> Dict[str, int]:
    deg = Counter({n: 0 for n in node_ids})
    for e in edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 1
    return {str(k): v for k, v in sorted(Counter(deg.values()).items())}


def validate_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], cells: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    node_ids = {n["node_id"] for n in nodes}
    if not nodes:
        warnings.append("node_count is zero")
    if not edges:
        warnings.append("edge_count is zero")
    if not cells:
        warnings.append("cell_count is zero")
    for e in edges:
        if e["source"] not in node_ids or e["target"] not in node_ids:
            warnings.append(f"edge {e.get('edge_id', '')} references invalid node")
    for c in cells:
        for nid in parse_list_like(c.get("node_ids", "")):
            if nid not in node_ids:
                warnings.append(f"cell {c.get('cell_id', '')} references invalid node {nid}")
    return ("valid_with_warnings" if warnings else "valid"), warnings


def build_manifest(structure_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], cells: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
    status, warnings = validate_graph(nodes, edges, cells)
    node_ids = [n["node_id"] for n in nodes]
    return {
        "structure_id": structure_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "cell_count": len(cells),
        "boundary_node_count": sum(1 for n in nodes if str(n.get("boundary_node", "0")) in {"1", "true", "True"}),
        "boundary_edge_count": sum(1 for e in edges if str(e.get("boundary_edge", "0")) in {"1", "true", "True"}),
        "degree_histogram": degree_histogram(edges, node_ids),
        "cell_type_counts": dict(Counter(c.get("cell_type", "") for c in cells)),
        "boundary_present": meta.get("boundary_present", False),
        "periodic_dimension_count": meta.get("periodic_dimension_count", 0),
        "closure_class": meta.get("closure_class", ""),
        "curvature_class": meta.get("curvature_class", ""),
        "hexagon_present": meta.get("hexagon_present", False),
        "pentagon_present": meta.get("pentagon_present", False),
        "validation_status": status,
        "warnings": warnings,
        "scope_note": meta.get("diagnostic_scope_note", ""),
    }


def normalize_c60(root: Path, cfg: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    structure_id = "c60_reference"
    raw_nodes = read_csv(root / cfg["inputs"]["c60_nodes_csv"])
    raw_edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    raw_faces = read_csv(root / cfg["inputs"]["c60_faces_csv"])

    deg = Counter()
    for e in raw_edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 1

    nodes = []
    for i, r in enumerate(raw_nodes):
        nid = r.get("node_id") or r.get("id") or f"c60_{i+1:03d}"
        theta = 2 * math.pi * i / max(1, len(raw_nodes))
        nodes.append({
            "structure_id": structure_id,
            "node_id": nid,
            "source_node_id": nid,
            "degree": deg[nid],
            "boundary_node": 0,
            "periodic_node": 0,
            "layout_x": math.cos(theta),
            "layout_y": math.sin(theta),
            "layout_z": 0.0,
            "node_role_hint": "c60_reference_node",
            "coordinate_status": "inspection_layout_only",
        })

    edges = []
    for r in raw_edges:
        s = r["source"]
        t = r["target"]
        faces = parse_list_like(r.get("shared_faces", ""))
        face_types = []
        for f in faces:
            if f.startswith("H"):
                face_types.append("H")
            elif f.startswith("P"):
                face_types.append("P")
        cls = r.get("edge_type") or ("_".join(sorted(face_types)) if face_types else "unknown")
        edges.append({
            "structure_id": structure_id,
            "edge_id": edge_id(s, t),
            "source": s,
            "target": t,
            "source_source_id": s,
            "target_source_id": t,
            "edge_class": cls,
            "boundary_edge": 0,
            "periodic_edge": 0,
            "cell_left": faces[0] if len(faces) > 0 else "",
            "cell_right": faces[1] if len(faces) > 1 else "",
            "cell_count": len(faces),
            "edge_role_hint": "c60_edge_class_reference",
        })

    cells = []
    for i, r in enumerate(raw_faces):
        cid = r.get("face_id") or r.get("cell_id") or f"face_{i:02d}"
        ctype = "hexagon" if cid.startswith("H") else "pentagon" if cid.startswith("P") else r.get("face_type", "")
        theta = 2 * math.pi * i / max(1, len(raw_faces))
        radius = 1.0 if ctype == "hexagon" else 0.65
        cells.append({
            "structure_id": structure_id,
            "cell_id": cid,
            "source_cell_id": cid,
            "cell_type": ctype,
            "node_ids": r.get("node_ids") or r.get("nodes") or "",
            "edge_ids": r.get("edge_ids", ""),
            "boundary_cell": 0,
            "periodic_cell": 0,
            "cell_role_hint": "c60_reference_face",
            "layout_x": radius * math.cos(theta),
            "layout_y": radius * math.sin(theta),
            "layout_z": 0.0,
            "coordinate_status": "inspection_layout_only",
        })

    meta = {
        "structure_class": "fullerene",
        "geometry_class": "closed_curved_cage",
        "boundary_present": False,
        "periodic_dimension_count": 0,
        "closure_class": "closed_cage",
        "curvature_class": "positive_closed_curvature_proxy",
        "pentagon_present": True,
        "hexagon_present": True,
        "chirality_label": "achiral_reference",
        "inversion_flag": True,
        "rotation_symmetry_label": "icosahedral_reference",
        "reflection_flag": True,
        "screw_symmetry_flag": False,
        "source_type": "validated_project_reference",
        "source_note": "Normalized from FU01 C60 graph artifacts.",
        "layout_coordinate_status": "inspection_layout_only",
        "diagnostic_scope_note": "C60 reference graph/cell inventory; not a new physical geometry derivation.",
    }
    return nodes, edges, cells, meta


def add_edge(edge_map: Dict[str, Dict[str, Any]], structure_id: str, a: str, b: str, edge_class: str, boundary_edge: int = 0, periodic_edge: int = 0) -> None:
    eid = edge_id(a, b)
    if eid not in edge_map:
        edge_map[eid] = {
            "structure_id": structure_id,
            "edge_id": eid,
            "source": a if a <= b else b,
            "target": b if a <= b else a,
            "source_source_id": a if a <= b else b,
            "target_source_id": b if a <= b else a,
            "edge_class": edge_class,
            "boundary_edge": boundary_edge,
            "periodic_edge": periodic_edge,
            "cell_left": "",
            "cell_right": "",
            "cell_count": 0,
            "edge_role_hint": edge_class,
        }
    else:
        edge_map[eid]["boundary_edge"] = int(edge_map[eid]["boundary_edge"]) and boundary_edge
        edge_map[eid]["periodic_edge"] = int(edge_map[eid]["periodic_edge"]) or periodic_edge


def attach_cell_to_edges(edge_map: Dict[str, Dict[str, Any]], cell_id: str, node_cycle: List[str]) -> None:
    for i, a in enumerate(node_cycle):
        b = node_cycle[(i + 1) % len(node_cycle)]
        eid = edge_id(a, b)
        if eid in edge_map:
            e = edge_map[eid]
            if not e["cell_left"]:
                e["cell_left"] = cell_id
            elif not e["cell_right"] and e["cell_left"] != cell_id:
                e["cell_right"] = cell_id
            e["cell_count"] = len([x for x in [e["cell_left"], e["cell_right"]] if x])


def build_hex_patch(structure_id: str, rows: int, cols: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    coord_to_id: Dict[Tuple[int, int], str] = {}
    node_coords: Dict[str, Tuple[float, float, float]] = {}
    cells: List[Dict[str, Any]] = []
    edge_map: Dict[str, Dict[str, Any]] = {}

    def get_node(x: float, y: float) -> str:
        key = (round(x * 1000000), round(y * 1000000))
        if key not in coord_to_id:
            nid = f"{structure_id}_n{len(coord_to_id)+1:04d}"
            coord_to_id[key] = nid
            node_coords[nid] = (x, y, 0.0)
        return coord_to_id[key]

    for r in range(rows):
        for c in range(cols):
            cx = math.sqrt(3) * (c + 0.5 * (r % 2))
            cy = 1.5 * r
            verts = []
            for k in range(6):
                angle = math.pi / 6 + k * math.pi / 3
                verts.append(get_node(cx + math.cos(angle), cy + math.sin(angle)))
            cid = f"{structure_id}_cell_{r:02d}_{c:02d}"
            boundary_cell = int(r == 0 or r == rows - 1 or c == 0 or c == cols - 1)
            cells.append({
                "structure_id": structure_id,
                "cell_id": cid,
                "source_cell_id": cid,
                "cell_type": "hexagon",
                "node_ids": ";".join(verts),
                "edge_ids": "",
                "boundary_cell": boundary_cell,
                "periodic_cell": 0,
                "cell_role_hint": "graphene_hex_cell",
                "layout_x": cx,
                "layout_y": cy,
                "layout_z": 0.0,
                "coordinate_status": "inspection_layout_only",
            })
            for i, a in enumerate(verts):
                add_edge(edge_map, structure_id, a, verts[(i + 1) % 6], "hex_hex_proxy")
            attach_cell_to_edges(edge_map, cid, verts)

    for e in edge_map.values():
        if int(e["cell_count"]) <= 1:
            e["boundary_edge"] = 1
            e["edge_class"] = "boundary_edge"

    deg = Counter()
    for e in edge_map.values():
        deg[e["source"]] += 1
        deg[e["target"]] += 1

    nodes = []
    for nid, (x, y, z) in sorted(node_coords.items()):
        nodes.append({
            "structure_id": structure_id,
            "node_id": nid,
            "source_node_id": nid,
            "degree": deg[nid],
            "boundary_node": int(deg[nid] < 3),
            "periodic_node": 0,
            "layout_x": x,
            "layout_y": y,
            "layout_z": z,
            "node_role_hint": "graphene_patch_node",
            "coordinate_status": "inspection_layout_only",
        })

    edges = list(edge_map.values())
    for cell in cells:
        verts = parse_list_like(cell["node_ids"])
        cell["edge_ids"] = ";".join(edge_id(a, verts[(i + 1) % len(verts)]) for i, a in enumerate(verts))

    meta = {
        "structure_class": "graphene_patch",
        "geometry_class": "flat_2d_open_hexagonal_patch",
        "boundary_present": True,
        "periodic_dimension_count": 0,
        "closure_class": "open_patch",
        "curvature_class": "flat_2d_proxy",
        "pentagon_present": False,
        "hexagon_present": True,
        "chirality_label": "not_applicable_flat_patch",
        "inversion_flag": "patch_dependent",
        "rotation_symmetry_label": "finite_patch_layout_dependent",
        "reflection_flag": "patch_dependent",
        "screw_symmetry_flag": False,
        "source_type": "generated_graph_control",
        "source_note": f"Generated finite hexagonal patch rows={rows}, cols={cols}.",
        "layout_coordinate_status": "inspection_layout_only",
        "diagnostic_scope_note": "Flat finite hexagonal graph/cell control; boundary effects explicit.",
    }
    return nodes, edges, cells, meta


def build_nanotube(structure_id: str, circumference_cells: int, length_cells: int, variant: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    coord_to_id: Dict[Tuple[int, int], str] = {}
    node_coords: Dict[str, Tuple[float, float, float]] = {}
    cells: List[Dict[str, Any]] = []
    edge_map: Dict[str, Dict[str, Any]] = {}
    period = math.sqrt(3) * circumference_cells
    radius = circumference_cells / (2 * math.pi)

    def get_node(x: float, y: float) -> str:
        wx = x % period
        key = (round(wx * 1000000), round(y * 1000000))
        if key not in coord_to_id:
            nid = f"{structure_id}_n{len(coord_to_id)+1:04d}"
            coord_to_id[key] = nid
            theta = 2 * math.pi * wx / period
            node_coords[nid] = (radius * math.cos(theta), radius * math.sin(theta), y)
        return coord_to_id[key]

    for r in range(length_cells):
        for c in range(circumference_cells):
            offset = 0.5 * (r % 2) if variant == "armchair" else 0.0
            cx = math.sqrt(3) * (c + offset)
            cy = 1.5 * r
            verts = []
            for k in range(6):
                angle = math.pi / 6 + k * math.pi / 3
                verts.append(get_node(cx + math.cos(angle), cy + math.sin(angle)))
            cid = f"{structure_id}_cell_{r:02d}_{c:02d}"
            cells.append({
                "structure_id": structure_id,
                "cell_id": cid,
                "source_cell_id": cid,
                "cell_type": "hexagon",
                "node_ids": ";".join(verts),
                "edge_ids": "",
                "boundary_cell": int(r == 0 or r == length_cells - 1),
                "periodic_cell": int(c == 0 or c == circumference_cells - 1),
                "cell_role_hint": f"{variant}_nanotube_hex_cell",
                "layout_x": radius * math.cos(2 * math.pi * c / circumference_cells),
                "layout_y": radius * math.sin(2 * math.pi * c / circumference_cells),
                "layout_z": cy,
                "coordinate_status": "inspection_layout_only",
            })
            for i, a in enumerate(verts):
                add_edge(edge_map, structure_id, a, verts[(i + 1) % 6], "tube_hex_hex_proxy", periodic_edge=int(c in {0, circumference_cells - 1}))
            attach_cell_to_edges(edge_map, cid, verts)

    for e in edge_map.values():
        if int(e["cell_count"]) <= 1:
            e["boundary_edge"] = 1
            e["edge_class"] = "tube_end_boundary_edge"
        elif int(e["periodic_edge"]) == 1:
            e["edge_class"] = "circumferential_periodic_join"

    deg = Counter()
    for e in edge_map.values():
        deg[e["source"]] += 1
        deg[e["target"]] += 1

    nodes = []
    for nid, (x, y, z) in sorted(node_coords.items()):
        nodes.append({
            "structure_id": structure_id,
            "node_id": nid,
            "source_node_id": nid,
            "degree": deg[nid],
            "boundary_node": int(deg[nid] < 3),
            "periodic_node": 1,
            "layout_x": x,
            "layout_y": y,
            "layout_z": z,
            "node_role_hint": f"{variant}_nanotube_node",
            "coordinate_status": "inspection_layout_only",
        })

    edges = list(edge_map.values())
    for cell in cells:
        verts = parse_list_like(cell["node_ids"])
        cell["edge_ids"] = ";".join(edge_id(a, verts[(i + 1) % len(verts)]) for i, a in enumerate(verts))

    meta = {
        "structure_class": "nanotube",
        "geometry_class": "open_curved_cylindrical_hexagonal_graph",
        "boundary_present": True,
        "periodic_dimension_count": 1,
        "closure_class": "circumferentially_closed_open_ends",
        "curvature_class": "cylindrical_curvature_proxy",
        "pentagon_present": False,
        "hexagon_present": True,
        "chirality_label": variant,
        "inversion_flag": "variant_dependent_proxy",
        "rotation_symmetry_label": f"{circumference_cells}-fold_cylindrical_proxy",
        "reflection_flag": "variant_dependent_proxy",
        "screw_symmetry_flag": "variant_dependent_proxy",
        "source_type": "generated_graph_control",
        "source_note": f"Generated {variant} cylindrical hexagonal graph with circumference_cells={circumference_cells}, length_cells={length_cells}.",
        "layout_coordinate_status": "inspection_layout_only",
        "diagnostic_scope_note": "Cylindrical graph/cell control; not validated molecular nanotube coordinates.",
    }
    return nodes, edges, cells, meta


def inventory_row(structure_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], cells: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "structure_id": structure_id,
        "structure_class": meta.get("structure_class", ""),
        "geometry_class": meta.get("geometry_class", ""),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "cell_count": len(cells),
        "boundary_present": meta.get("boundary_present", ""),
        "boundary_node_count": sum(1 for n in nodes if int(n.get("boundary_node", 0)) == 1),
        "boundary_edge_count": sum(1 for e in edges if int(e.get("boundary_edge", 0)) == 1),
        "periodic_dimension_count": meta.get("periodic_dimension_count", 0),
        "closure_class": meta.get("closure_class", ""),
        "curvature_class": meta.get("curvature_class", ""),
        "pentagon_present": meta.get("pentagon_present", ""),
        "hexagon_present": meta.get("hexagon_present", ""),
        "chirality_label": meta.get("chirality_label", ""),
        "inversion_flag": meta.get("inversion_flag", ""),
        "rotation_symmetry_label": meta.get("rotation_symmetry_label", ""),
        "reflection_flag": meta.get("reflection_flag", ""),
        "screw_symmetry_flag": meta.get("screw_symmetry_flag", ""),
        "source_type": meta.get("source_type", ""),
        "source_note": meta.get("source_note", ""),
        "layout_coordinate_status": meta.get("layout_coordinate_status", ""),
        "diagnostic_scope_note": meta.get("diagnostic_scope_note", ""),
    }


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    prefix = root / cfg["naming"]["output_prefix"]
    warnings: List[Dict[str, str]] = []
    inventory: List[Dict[str, Any]] = []
    manifests: Dict[str, Any] = {}

    structures = []

    try:
        structures.append(("c60_reference", *normalize_c60(root, cfg)))
    except Exception as exc:
        warnings.append({"severity": "error", "message": f"Failed to normalize C60 reference: {exc}"})

    gen = cfg.get("generated_structures", {})
    g = gen.get("graphene_patch", {})
    if g.get("enabled", False):
        structures.append((g.get("structure_id", "graphene_patch"), *build_hex_patch(g.get("structure_id", "graphene_patch"), int(g.get("rows", 4)), int(g.get("cols", 5)))))

    a = gen.get("nanotube_armchair", {})
    if a.get("enabled", False):
        sid = a.get("structure_id", "nanotube_armchair")
        structures.append((sid, *build_nanotube(sid, int(a.get("circumference_cells", 8)), int(a.get("length_cells", 5)), "armchair")))

    z = gen.get("nanotube_zigzag", {})
    if z.get("enabled", False):
        sid = z.get("structure_id", "nanotube_zigzag")
        structures.append((sid, *build_nanotube(sid, int(z.get("circumference_cells", 7)), int(z.get("length_cells", 6)), "zigzag")))

    for sid, nodes, edges, cells, meta in structures:
        write_csv(Path(f"{prefix}_{sid}_nodes.csv"), nodes, NODE_FIELDS)
        write_csv(Path(f"{prefix}_{sid}_edges.csv"), edges, EDGE_FIELDS)
        write_csv(Path(f"{prefix}_{sid}_cells.csv"), cells, CELL_FIELDS)
        manifest = build_manifest(sid, nodes, edges, cells, meta)
        manifest["meta"] = meta
        write_json(Path(f"{prefix}_{sid}_manifest.json"), manifest)
        inventory.append(inventory_row(sid, nodes, edges, cells, meta))
        manifests[sid] = manifest
        for w in manifest.get("warnings", []):
            warnings.append({"severity": "warning", "message": f"{sid}: {w}"})

    write_csv(root / cfg["outputs"]["inventory_csv"], inventory, INVENTORY_FIELDS)

    inventory_manifest = {
        "run_id": cfg["run"]["run_id"],
        "structure_count": len(structures),
        "structure_ids": [sid for sid, *_ in structures],
        "inventory_csv": cfg["outputs"]["inventory_csv"],
        "structure_manifests": manifests,
        "warnings_count": len(warnings),
        "scope_note": "FU02g1 builds graph/cell inventory controls only; no carrier specificity claim is made.",
    }
    write_json(root / cfg["outputs"]["inventory_manifest_json"], inventory_manifest)
    write_json(root / cfg["outputs"]["warnings_json"], warnings)
    (root / cfg["outputs"]["resolved_config_yaml"]).write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(inventory_manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Build BMS-FU02g1 structure inventory.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
