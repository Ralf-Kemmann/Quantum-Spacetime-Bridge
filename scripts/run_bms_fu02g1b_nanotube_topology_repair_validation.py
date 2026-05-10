#!/usr/bin/env python3
"""
BMS-FU02g1b — Nanotube Topology Repair and Validation

Purpose:
  Generate topology-repaired cylindrical hexagonal graph/cell controls for
  later FU02g2 carrier-diagnostic transfer.

Scope:
  Graph-geometric control only. Coordinates are inspection/layout coordinates.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
    "structure_id", "variant", "node_count", "edge_count", "cell_count",
    "degree_histogram", "boundary_node_count", "boundary_edge_count",
    "degree4_count", "max_degree", "validation_status", "geometry_class",
    "closure_class", "curvature_class", "diagnostic_scope_note",
]


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def parse_list_like(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip().strip("[]{}()")
    if not s:
        return []
    parts = re.split(r"[;,|\s]+", s)
    return [p.strip().strip("'\"") for p in parts if p.strip().strip("'\"")]


def edge_id(a: str, b: str) -> str:
    return f"{a}--{b}" if a <= b else f"{b}--{a}"


class DSU:
    def __init__(self) -> None:
        self.parent: Dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def build_strip_cells(structure_id: str, circumference_cells: int, length_cells: int, variant: str) -> Tuple[Dict[str, Tuple[float, float]], List[Dict[str, Any]]]:
    """
    Build an unwrapped finite hex-cell strip. The topology repair then performs
    conservative seam identifications.
    """
    coord_to_id: Dict[Tuple[int, int], str] = {}
    coords: Dict[str, Tuple[float, float]] = {}
    cells: List[Dict[str, Any]] = []

    def get_node(x: float, y: float) -> str:
        key = (round(x * 1000000), round(y * 1000000))
        if key not in coord_to_id:
            nid = f"{structure_id}_raw_n{len(coord_to_id)+1:05d}"
            coord_to_id[key] = nid
            coords[nid] = (x, y)
        return coord_to_id[key]

    for r in range(length_cells):
        for c in range(circumference_cells):
            # Two orientations give different seam/cell-sharing patterns.
            if variant == "armchair":
                cx = math.sqrt(3) * (c + 0.5 * (r % 2))
                cy = 1.5 * r
                start_angle = math.pi / 6
            elif variant == "zigzag":
                cx = 1.5 * c
                cy = math.sqrt(3) * (r + 0.5 * (c % 2))
                start_angle = 0.0
            else:
                raise ValueError(f"Unknown variant: {variant}")

            verts: List[str] = []
            for k in range(6):
                angle = start_angle + k * math.pi / 3
                verts.append(get_node(cx + math.cos(angle), cy + math.sin(angle)))

            cells.append({
                "raw_cell_id": f"{structure_id}_cell_{r:02d}_{c:02d}",
                "r": r,
                "c": c,
                "raw_nodes": verts,
            })

    return coords, cells


def identify_seam_nodes(
    coords: Dict[str, Tuple[float, float]],
    cells: List[Dict[str, Any]],
    structure_id: str,
    circumference_cells: int,
    variant: str,
) -> Dict[str, str]:
    """
    Conservative seam identification.

    We identify nodes on the left/right strip boundaries by matching transverse
    coordinate. This uses the unwrapped strip period as a quotient direction.
    """
    dsu = DSU()
    for nid in coords:
        dsu.find(nid)

    xs = [xy[0] for xy in coords.values()]
    min_x, max_x = min(xs), max(xs)
    span = max_x - min_x
    tol_x = 1e-5
    tol_y = 1e-5

    left = []
    right = []
    for nid, (x, y) in coords.items():
        if abs(x - min_x) < tol_x or x < min_x + 0.51:
            left.append((nid, x, y))
        if abs(x - max_x) < tol_x or x > max_x - 0.51:
            right.append((nid, x, y))

    # Match by y coordinate. Only merge pairs that are close in y.
    used_right = set()
    for lnid, lx, ly in left:
        candidates = [(abs(ly - ry), rnid) for rnid, rx, ry in right if rnid not in used_right and abs(ly - ry) < tol_y]
        if candidates:
            _, rnid = min(candidates)
            dsu.union(lnid, rnid)
            used_right.add(rnid)

    # Produce stable normalized ids.
    reps = sorted({dsu.find(nid) for nid in coords})
    rep_to_new = {rep: f"{structure_id}_n{i+1:04d}" for i, rep in enumerate(reps)}
    return {nid: rep_to_new[dsu.find(nid)] for nid in coords}


def build_edges_and_cells(
    structure_id: str,
    raw_coords: Dict[str, Tuple[float, float]],
    raw_cells: List[Dict[str, Any]],
    raw_to_node: Dict[str, str],
    circumference_cells: int,
    length_cells: int,
    variant: str,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    edge_map: Dict[str, Dict[str, Any]] = {}
    cell_rows: List[Dict[str, Any]] = []
    incident_cells: Dict[str, List[str]] = defaultdict(list)

    # First pass: cells and edges.
    for rc in raw_cells:
        nodes = [raw_to_node[n] for n in rc["raw_nodes"]]
        # Remove degenerate cells caused by over-identification.
        if len(set(nodes)) != 6:
            continue

        cid = rc["raw_cell_id"].replace("_raw_", "_")
        boundary_cell = int(rc["r"] == 0 or rc["r"] == length_cells - 1)
        periodic_cell = int(rc["c"] == 0 or rc["c"] == circumference_cells - 1)
        eids: List[str] = []
        for i, a in enumerate(nodes):
            b = nodes[(i + 1) % 6]
            eid = edge_id(a, b)
            eids.append(eid)
            if eid not in edge_map:
                edge_map[eid] = {
                    "structure_id": structure_id,
                    "edge_id": eid,
                    "source": a if a <= b else b,
                    "target": b if a <= b else a,
                    "source_source_id": a if a <= b else b,
                    "target_source_id": b if a <= b else a,
                    "edge_class": "tube_hex_hex_proxy",
                    "boundary_edge": 0,
                    "periodic_edge": periodic_cell,
                    "cell_left": "",
                    "cell_right": "",
                    "cell_count": 0,
                    "edge_role_hint": f"{variant}_repaired_tube_edge",
                }
            incident_cells[eid].append(cid)

        cell_rows.append({
            "structure_id": structure_id,
            "cell_id": cid,
            "source_cell_id": cid,
            "cell_type": "hexagon",
            "node_ids": ";".join(nodes),
            "edge_ids": ";".join(eids),
            "boundary_cell": boundary_cell,
            "periodic_cell": periodic_cell,
            "cell_role_hint": f"{variant}_repaired_tube_hex_cell",
            "layout_x": "",
            "layout_y": "",
            "layout_z": "",
            "coordinate_status": "inspection_layout_only",
        })

    for eid, e in edge_map.items():
        inc = incident_cells[eid]
        e["cell_left"] = inc[0] if len(inc) > 0 else ""
        e["cell_right"] = inc[1] if len(inc) > 1 else ""
        e["cell_count"] = len(inc)
        if len(inc) <= 1:
            e["boundary_edge"] = 1
            e["edge_class"] = "tube_end_boundary_edge"
        elif int(e["periodic_edge"]):
            e["edge_class"] = "circumferential_periodic_join"

    # Node degrees.
    degree = Counter()
    for e in edge_map.values():
        degree[e["source"]] += 1
        degree[e["target"]] += 1

    # Approximate node coordinates by averaging raw nodes mapped to each repaired node.
    node_to_raw: Dict[str, List[str]] = defaultdict(list)
    for raw, node in raw_to_node.items():
        node_to_raw[node].append(raw)

    node_rows: List[Dict[str, Any]] = []
    period = max(x for x, y in raw_coords.values()) - min(x for x, y in raw_coords.values())
    radius = max(1.0, circumference_cells / (2 * math.pi))

    for node in sorted(node_to_raw):
        raw_ids = node_to_raw[node]
        xs = [raw_coords[r][0] for r in raw_ids]
        ys = [raw_coords[r][1] for r in raw_ids]
        avg_x = sum(xs) / len(xs)
        avg_y = sum(ys) / len(ys)
        theta = 2 * math.pi * ((avg_x - min(x for x, y in raw_coords.values())) % period) / period if period else 0.0
        node_rows.append({
            "structure_id": structure_id,
            "node_id": node,
            "source_node_id": ";".join(sorted(raw_ids)),
            "degree": degree[node],
            "boundary_node": int(degree[node] < 3),
            "periodic_node": 1,
            "layout_x": radius * math.cos(theta),
            "layout_y": radius * math.sin(theta),
            "layout_z": avg_y,
            "node_role_hint": f"{variant}_repaired_tube_node",
            "coordinate_status": "inspection_layout_only",
        })

    node_coord_lookup = {r["node_id"]: (float(r["layout_x"]), float(r["layout_y"]), float(r["layout_z"])) for r in node_rows}
    for cell in cell_rows:
        ns = parse_list_like(cell["node_ids"])
        xyz = [node_coord_lookup[n] for n in ns if n in node_coord_lookup]
        if xyz:
            cell["layout_x"] = sum(v[0] for v in xyz) / len(xyz)
            cell["layout_y"] = sum(v[1] for v in xyz) / len(xyz)
            cell["layout_z"] = sum(v[2] for v in xyz) / len(xyz)

    meta = {
        "structure_class": "nanotube",
        "variant": variant,
        "geometry_class": "repaired_open_curved_cylindrical_hexagonal_graph",
        "boundary_present": True,
        "periodic_dimension_count": 1,
        "closure_class": "circumferentially_closed_open_ends",
        "curvature_class": "cylindrical_curvature_proxy",
        "pentagon_present": False,
        "hexagon_present": True,
        "chirality_label": variant,
        "source_type": "generated_graph_control_repaired",
        "layout_coordinate_status": "inspection_layout_only",
        "diagnostic_scope_note": "Topology-repaired cylindrical graph/cell control; not validated molecular nanotube coordinates.",
    }
    return node_rows, list(edge_map.values()), cell_rows, meta


def validate_structure(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], cells: List[Dict[str, Any]], cfg_validation: Dict[str, Any]) -> Tuple[str, List[str], Dict[str, Any]]:
    warnings: List[str] = []
    node_ids = {n["node_id"] for n in nodes}
    for e in edges:
        if e["source"] not in node_ids or e["target"] not in node_ids:
            warnings.append(f"invalid edge node reference: {e['edge_id']}")
    for c in cells:
        for n in parse_list_like(c["node_ids"]):
            if n not in node_ids:
                warnings.append(f"invalid cell node reference: {c['cell_id']} -> {n}")

    degree_counts = Counter(int(n["degree"]) for n in nodes)
    max_degree = max(degree_counts.keys()) if degree_counts else 0
    degree4_count = sum(v for d, v in degree_counts.items() if d >= 4)
    boundary_node_count = sum(1 for n in nodes if int(n["boundary_node"]) == 1)
    boundary_edge_count = sum(1 for e in edges if int(e["boundary_edge"]) == 1)

    if cfg_validation.get("require_no_degree4", True) and degree4_count != 0:
        warnings.append(f"degree>=4 nodes present: {degree4_count}")
    if max_degree > int(cfg_validation.get("max_allowed_degree", 3)):
        warnings.append(f"max_degree exceeds limit: {max_degree}")
    if cfg_validation.get("require_degree3_more_than_degree2", True) and degree_counts.get(3, 0) <= degree_counts.get(2, 0):
        warnings.append("degree-3 count is not greater than degree-2 count")
    if cfg_validation.get("require_boundary_not_dominant", True) and boundary_node_count >= len(nodes) / 2:
        warnings.append("boundary nodes are dominant or half of graph")

    status = "valid_for_fu02g2_candidate" if not warnings else "needs_review"
    metrics = {
        "degree_histogram": {str(k): v for k, v in sorted(degree_counts.items())},
        "max_degree": max_degree,
        "degree4_count": degree4_count,
        "boundary_node_count": boundary_node_count,
        "boundary_edge_count": boundary_edge_count,
    }
    return status, warnings, metrics


def build_repaired_nanotube(structure_id: str, variant: str, circumference_cells: int, length_cells: int, validation_cfg: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    raw_coords, raw_cells = build_strip_cells(structure_id, circumference_cells, length_cells, variant)
    raw_to_node = identify_seam_nodes(raw_coords, raw_cells, structure_id, circumference_cells, variant)
    nodes, edges, cells, meta = build_edges_and_cells(structure_id, raw_coords, raw_cells, raw_to_node, circumference_cells, length_cells, variant)
    status, warnings, metrics = validate_structure(nodes, edges, cells, validation_cfg)
    meta["validation_status"] = status
    meta["warnings"] = warnings
    meta.update(metrics)
    return nodes, edges, cells, meta


def manifest_for(structure_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], cells: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "structure_id": structure_id,
        "variant": meta.get("variant", ""),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "cell_count": len(cells),
        "degree_histogram": meta.get("degree_histogram", {}),
        "max_degree": meta.get("max_degree", ""),
        "degree4_count": meta.get("degree4_count", ""),
        "boundary_node_count": meta.get("boundary_node_count", ""),
        "boundary_edge_count": meta.get("boundary_edge_count", ""),
        "cell_type_counts": dict(Counter(c["cell_type"] for c in cells)),
        "validation_status": meta.get("validation_status", ""),
        "warnings": meta.get("warnings", []),
        "geometry_class": meta.get("geometry_class", ""),
        "closure_class": meta.get("closure_class", ""),
        "curvature_class": meta.get("curvature_class", ""),
        "diagnostic_scope_note": meta.get("diagnostic_scope_note", ""),
        "meta": meta,
    }


def run(config_path: Path) -> None:
    cfg = read_yaml(config_path)
    root = Path.cwd()
    prefix = root / cfg["naming"]["output_prefix"]
    validation_cfg = cfg.get("validation", {})

    inventory_rows: List[Dict[str, Any]] = []
    warnings_all: List[Dict[str, str]] = []
    manifests: Dict[str, Any] = {}

    for key, scfg in cfg.get("generated_structures", {}).items():
        if not scfg.get("enabled", False):
            continue
        sid = scfg["structure_id"]
        variant = scfg["variant"]
        nodes, edges, cells, meta = build_repaired_nanotube(
            sid,
            variant,
            int(scfg["circumference_cells"]),
            int(scfg["length_cells"]),
            validation_cfg,
        )

        write_csv(Path(f"{prefix}_{sid}_nodes.csv"), nodes, NODE_FIELDS)
        write_csv(Path(f"{prefix}_{sid}_edges.csv"), edges, EDGE_FIELDS)
        write_csv(Path(f"{prefix}_{sid}_cells.csv"), cells, CELL_FIELDS)

        manifest = manifest_for(sid, nodes, edges, cells, meta)
        write_json(Path(f"{prefix}_{sid}_manifest.json"), manifest)
        manifests[sid] = manifest

        inventory_rows.append({
            "structure_id": sid,
            "variant": variant,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "cell_count": len(cells),
            "degree_histogram": json.dumps(meta.get("degree_histogram", {}), sort_keys=True),
            "boundary_node_count": meta.get("boundary_node_count", ""),
            "boundary_edge_count": meta.get("boundary_edge_count", ""),
            "degree4_count": meta.get("degree4_count", ""),
            "max_degree": meta.get("max_degree", ""),
            "validation_status": meta.get("validation_status", ""),
            "geometry_class": meta.get("geometry_class", ""),
            "closure_class": meta.get("closure_class", ""),
            "curvature_class": meta.get("curvature_class", ""),
            "diagnostic_scope_note": meta.get("diagnostic_scope_note", ""),
        })

        for w in meta.get("warnings", []):
            warnings_all.append({"severity": "warning", "message": f"{sid}: {w}"})

    write_csv(root / cfg["outputs"]["inventory_csv"], inventory_rows, INVENTORY_FIELDS)

    repair_manifest = {
        "run_id": cfg["run"]["run_id"],
        "structure_count": len(inventory_rows),
        "structure_ids": [r["structure_id"] for r in inventory_rows],
        "inventory_csv": cfg["outputs"]["inventory_csv"],
        "warnings_count": len(warnings_all),
        "structure_manifests": manifests,
        "scope_note": "FU02g1b repairs nanotube topology controls only; no carrier diagnostic is run.",
    }
    write_json(root / cfg["outputs"]["repair_manifest_json"], repair_manifest)
    write_json(root / cfg["outputs"]["warnings_json"], warnings_all)
    (root / cfg["outputs"]["resolved_config_yaml"]).write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(repair_manifest, indent=2, sort_keys=True))
    if warnings_all:
        print("\nWarnings:")
        for w in warnings_all:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair nanotube topology controls for FU02g.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
