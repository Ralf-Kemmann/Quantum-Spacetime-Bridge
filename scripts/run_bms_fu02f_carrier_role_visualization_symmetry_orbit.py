#!/usr/bin/env python3
"""
BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection

Purpose:
  Export visualization-ready node/edge/face tables and perform conservative
  graph-level shape/orbit inspection of the compact role-balanced C60 carrier region.

Scope:
  This is not a full C60 automorphism-group proof and not a physical geometry proof.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


Edge = Tuple[str, str]


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


def edge_key(a: str, b: str) -> Edge:
    return (a, b) if a <= b else (b, a)


def edge_key_str(e: Edge) -> str:
    return f"{e[0]}--{e[1]}"


def parse_edge_key(s: str) -> Edge:
    a, b = str(s).split("--", 1)
    return edge_key(a, b)


def parse_list_like(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    s = s.strip("[](){}")
    parts = re.split(r"[;,|\\s]+", s)
    return [p.strip().strip("'\"") for p in parts if p.strip().strip("'\"")]


def as_int(x: Any, default: int = 0) -> int:
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


def face_type(face_id: str) -> str:
    if face_id.startswith("H"):
        return "H"
    if face_id.startswith("P"):
        return "P"
    return ""


def id_index(face_id: str) -> int:
    m = re.search(r"(\\d+)$", face_id)
    return int(m.group(1)) if m else -1


def contiguous_intervals(ids: Iterable[str]) -> str:
    grouped = defaultdict(list)
    for fid in ids:
        prefix = fid.split("_")[0] if "_" in fid else re.sub(r"\\d+$", "", fid)
        idx = id_index(fid)
        if idx >= 0:
            grouped[prefix].append(idx)
    chunks = []
    for prefix, nums in sorted(grouped.items()):
        nums = sorted(set(nums))
        if not nums:
            continue
        start = prev = nums[0]
        for n in nums[1:]:
            if n == prev + 1:
                prev = n
            else:
                chunks.append(f"{prefix}_{start:02d}-{prefix}_{prev:02d}" if start != prev else f"{prefix}_{start:02d}")
                start = prev = n
        chunks.append(f"{prefix}_{start:02d}-{prefix}_{prev:02d}" if start != prev else f"{prefix}_{start:02d}")
    return ";".join(chunks)


def build_face_maps(c60_edges: List[Dict[str, str]]) -> Tuple[Dict[str, List[str]], Dict[str, Set[str]], List[Dict[str, str]]]:
    edge_to_faces: Dict[str, List[str]] = {}
    face_adj: Dict[str, Set[str]] = defaultdict(set)
    face_adj_rows: List[Dict[str, str]] = []
    for r in c60_edges:
        es = edge_key_str(edge_key(r["source"], r["target"]))
        faces = parse_list_like(r.get("shared_faces", ""))
        edge_to_faces[es] = faces
        if len(faces) >= 2:
            for i, a in enumerate(faces):
                for b in faces[i + 1:]:
                    if a == b:
                        continue
                    face_adj[a].add(b)
                    face_adj[b].add(a)
                    face_adj_rows.append({"edge_key": es, "face_a": a, "face_b": b})
    return edge_to_faces, face_adj, face_adj_rows


def graph_distances(seeds: Set[str], nodes: Set[str], adj: Dict[str, Set[str]]) -> Dict[str, int]:
    dist = {n: -1 for n in nodes}
    q = deque()
    for s in seeds:
        if s in dist:
            dist[s] = 0
            q.append(s)
    while q:
        x = q.popleft()
        for y in adj.get(x, set()):
            if y in dist and dist[y] < 0:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist


def classify_shape(summary: Dict[str, Any]) -> str:
    carrier_faces = summary["carrier_face_count"]
    face_count = summary["face_count"]
    comp = summary["carrier_face_component_count"]
    boundary_ratio = summary["carrier_face_boundary_adjacency_count"] / max(1, summary["carrier_face_internal_adjacency_count"])
    max_dist = summary["max_distance_to_mixed_core"]

    frac = carrier_faces / face_count if face_count else 0
    if comp != 1:
        return "distributed_region_candidate"
    if frac <= 0.35 and max_dist <= 2:
        return "compact_patch_candidate"
    if 0.35 < frac <= 0.60 and max_dist <= 2:
        return "connected_face_region_candidate"
    if 0.35 < frac <= 0.70 and boundary_ratio <= 1.25:
        return "cap_or_belt_like_candidate"
    if frac > 0.70:
        return "large_region_candidate"
    return "insufficient_for_shape_label"


def write_simple_svg(path: Path, face_rows: List[Dict[str, Any]], width: int, height: int) -> None:
    """
    Minimal non-geometric face map:
    Hexagons and pentagons are placed on separate rows by id.
    This is not a true 3D C60 visualization.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    faces = sorted(face_rows, key=lambda r: (r["face_type"], id_index(r["face_id"])))
    h_faces = [r for r in faces if r["face_type"] == "H"]
    p_faces = [r for r in faces if r["face_type"] == "P"]

    def color(label: str) -> str:
        return {
            "mixed_seam_boundary_face": "#f2b84b",
            "hp_boundary_face": "#64b5f6",
            "hh_seam_face": "#e57373",
            "carrier_adjacent_face": "#b0bec5",
            "noncarrier_face": "#eeeeee",
        }.get(label, "#dddddd")

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg.append('<rect width="100%" height="100%" fill="#111827"/>')
    svg.append('<text x="40" y="40" fill="#ffffff" font-family="sans-serif" font-size="24">BMS-FU02f C60 carrier-role face map</text>')
    svg.append('<text x="40" y="70" fill="#cbd5e1" font-family="sans-serif" font-size="14">Non-geometric layout for inspection only; not a true 3D C60 projection.</text>')

    def draw_row(rows: List[Dict[str, Any]], y: int, label: str, cols: int):
        svg.append(f'<text x="40" y="{y-25}" fill="#ffffff" font-family="sans-serif" font-size="18">{label}</text>')
        cell_w = (width - 100) / cols
        for i, r in enumerate(rows):
            x = 50 + (i % cols) * cell_w
            yy = y + (i // cols) * 80
            fill = color(r["face_carrier_role_label"])
            stroke = "#ffffff" if int(r["carrier_region_member"]) else "#475569"
            svg.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{cell_w-10:.1f}" height="55" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            svg.append(f'<text x="{x+8:.1f}" y="{yy+22:.1f}" fill="#111827" font-family="monospace" font-size="14">{r["face_id"]}</text>')
            svg.append(f'<text x="{x+8:.1f}" y="{yy+42:.1f}" fill="#111827" font-family="monospace" font-size="11">C={r["carrier_edge_count"]} HH={r["hh_consensus_edge_count"]} HP={r["hp_secondary_edge_count"]}</text>')

    draw_row(h_faces, 120, "Hexagons", 10)
    draw_row(p_faces, 360, "Pentagons", 6)

    legend_y = height - 150
    legend = [
        ("mixed seam-boundary", "#f2b84b"),
        ("H/P boundary", "#64b5f6"),
        ("carrier-adjacent", "#b0bec5"),
        ("noncarrier", "#eeeeee"),
    ]
    svg.append(f'<text x="40" y="{legend_y}" fill="#ffffff" font-family="sans-serif" font-size="18">Legend</text>')
    for i, (lab, col) in enumerate(legend):
        x = 40 + i * 250
        svg.append(f'<rect x="{x}" y="{legend_y+20}" width="28" height="18" fill="{col}"/>')
        svg.append(f'<text x="{x+36}" y="{legend_y+35}" fill="#ffffff" font-family="sans-serif" font-size="13">{lab}</text>')
    svg.append("</svg>")
    path.write_text("\\n".join(svg), encoding="utf-8")


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    fu02d1_dir = root / cfg["inputs"]["fu02d1_output_dir"]
    fu02d_dir = root / cfg["inputs"]["fu02d_output_dir"]
    fu02e1_dir = root / cfg["inputs"]["fu02e1_output_dir"]

    fu02d1_manifest = read_json(fu02d1_dir / "bms_fu02d1_run_manifest.json")
    fu02d1_faces = read_csv(fu02d1_dir / "bms_fu02d1_face_localization.csv")
    fu02d1_components = read_csv(fu02d1_dir / "bms_fu02d1_face_component_summary.csv")
    fu02d_edges = read_csv(fu02d_dir / "bms_fu02d_carrier_edge_geometry.csv")
    fu02d_nodes = read_csv(fu02d_dir / "bms_fu02d_carrier_node_geometry.csv")
    fu02e1_manifest = read_json(fu02e1_dir / "bms_fu02e1_run_manifest.json") if (fu02e1_dir / "bms_fu02e1_run_manifest.json").exists() else {}

    c60_edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    c60_nodes = read_csv(root / cfg["inputs"]["c60_nodes_csv"])
    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])

    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    edge_to_faces, face_adj, face_adj_rows = build_face_maps(c60_edges)
    all_faces = sorted({f for faces in edge_to_faces.values() for f in faces})

    # Node visualization
    node_rows = []
    carrier_nodes = set()
    for r in fu02d_nodes:
        if r.get("carrier_junction_label") != "noncarrier_node":
            carrier_nodes.add(r["node_id"])

    for r in fu02d_nodes:
        label = r.get("carrier_junction_label", "noncarrier_node")
        total = as_int(r.get("incident_total_carrier_count", 0))
        node_rows.append({
            "node_id": r["node_id"],
            "degree": r.get("degree", ""),
            "node_role_label": label,
            "incident_hh_consensus_count": r.get("incident_hh_consensus_count", 0),
            "incident_hp_secondary_count": r.get("incident_hp_secondary_count", 0),
            "incident_total_carrier_count": total,
            "carrier_region_member": int(r["node_id"] in carrier_nodes),
            "visual_size": 12 + 5 * total,
            "visual_layer": 3 if label == "mixed_role_junction" else 2 if label == "hp_boundary_node" else 1,
        })

    # Edge visualization
    edge_rows = []
    hh_edges = set()
    hp_edges = set()
    carrier_edges = set()
    for r in fu02d_edges:
        role = r.get("role_group", "OTHER")
        if role == "HH_CONSENSUS":
            hh_edges.add(r["edge_key"])
        if role == "HP_SECONDARY":
            hp_edges.add(r["edge_key"])
        if role in {"HH_CONSENSUS", "HP_SECONDARY"}:
            carrier_edges.add(r["edge_key"])

        edge_rows.append({
            "edge_key": r["edge_key"],
            "source": r["source"],
            "target": r["target"],
            "edge_type": r.get("edge_type", ""),
            "shared_face_types": r.get("shared_face_types", ""),
            "carrier_role": role,
            "is_hh_consensus": r.get("is_hh_consensus", 0),
            "is_hp_secondary": r.get("is_hp_secondary", 0),
            "is_role_carrier": r.get("is_role_carrier", 0),
            "shell_distance_to_hh_consensus": r.get("shell_distance_to_hh_consensus", ""),
            "visual_weight": 4 if role == "HH_CONSENSUS" else 3 if role == "HP_SECONDARY" else 1,
            "visual_layer": 3 if role == "HH_CONSENSUS" else 2 if role == "HP_SECONDARY" else 1,
        })

    # Face sets
    carrier_faces = {r["face_id"] for r in fu02d1_faces if as_int(r.get("carrier_edge_count", 0)) > 0}
    mixed_faces = {r["face_id"] for r in fu02d1_faces if r.get("face_carrier_role_label") == "mixed_seam_boundary_face"}
    hp_boundary_faces = {r["face_id"] for r in fu02d1_faces if r.get("face_carrier_role_label") == "hp_boundary_face"}
    carrier_adjacent_faces = {r["face_id"] for r in fu02d1_faces if r.get("face_carrier_role_label") == "carrier_adjacent_face"}
    noncarrier_faces = {r["face_id"] for r in fu02d1_faces if r.get("face_carrier_role_label") == "noncarrier_face"}

    dist_to_mixed = graph_distances(mixed_faces, set(all_faces), face_adj)

    face_rows = []
    for r in fu02d1_faces:
        fid = r["face_id"]
        label = r.get("face_carrier_role_label", "")
        carrier_count = as_int(r.get("carrier_edge_count", 0))
        face_rows.append({
            "face_id": fid,
            "face_type": r.get("face_type", face_type(fid)),
            "face_carrier_role_label": label,
            "carrier_edge_count": carrier_count,
            "hh_consensus_edge_count": r.get("hh_consensus_edge_count", 0),
            "hp_secondary_edge_count": r.get("hp_secondary_edge_count", 0),
            "mixed_role_junction_node_count": r.get("mixed_role_junction_node_count", 0),
            "carrier_region_member": int(fid in carrier_faces),
            "face_distance_to_mixed_core": dist_to_mixed.get(fid, -1),
            "visual_weight": 4 if label == "mixed_seam_boundary_face" else 3 if label == "hp_boundary_face" else 2 if label == "carrier_adjacent_face" else 1,
            "visual_layer": 3 if fid in carrier_faces else 2 if fid in carrier_adjacent_faces else 1,
            "carrier_edge_keys": r.get("carrier_edge_keys", ""),
            "boundary_node_ids": r.get("boundary_node_ids", ""),
        })

    # Region manifest
    region_manifest = {
        "carrier_face_ids": sorted(carrier_faces),
        "mixed_face_ids": sorted(mixed_faces),
        "hp_boundary_face_ids": sorted(hp_boundary_faces),
        "carrier_adjacent_face_ids": sorted(carrier_adjacent_faces),
        "noncarrier_face_ids": sorted(noncarrier_faces),
        "carrier_node_ids": sorted(carrier_nodes),
        "carrier_edge_ids": sorted(carrier_edges),
        "hh_consensus_edges": sorted(hh_edges),
        "hp_secondary_edges": sorted(hp_edges),
    }

    # Diagnostics
    carrier_internal = 0
    carrier_boundary = 0
    external_neighbors = set()
    for row in face_adj_rows:
        a, b = row["face_a"], row["face_b"]
        if a in carrier_faces and b in carrier_faces:
            carrier_internal += 1
        elif a in carrier_faces and b not in carrier_faces:
            carrier_boundary += 1
            external_neighbors.add(b)
        elif b in carrier_faces and a not in carrier_faces:
            carrier_boundary += 1
            external_neighbors.add(a)

    dvals = [d for f, d in dist_to_mixed.items() if f in carrier_faces and d >= 0]
    max_dist = max(dvals) if dvals else -1
    mean_dist = sum(dvals) / len(dvals) if dvals else -1

    carrier_hex = sorted(f for f in carrier_faces if face_type(f) == "H")
    carrier_pen = sorted(f for f in carrier_faces if face_type(f) == "P")

    inspection_rows = [
        {
            "diagnostic_name": "carrier_hexagon_intervals",
            "diagnostic_value": contiguous_intervals(carrier_hex),
            "note": "Face-id interval diagnostic; weak cue only, not physical coordinates.",
        },
        {
            "diagnostic_name": "carrier_pentagon_intervals",
            "diagnostic_value": contiguous_intervals(carrier_pen),
            "note": "Face-id interval diagnostic; weak cue only, not physical coordinates.",
        },
        {
            "diagnostic_name": "mixed_face_intervals",
            "diagnostic_value": contiguous_intervals(sorted(mixed_faces)),
            "note": "Mixed seam-boundary face id intervals.",
        },
        {
            "diagnostic_name": "carrier_face_internal_adjacency_count",
            "diagnostic_value": carrier_internal,
            "note": "Face adjacencies with both sides in carrier region.",
        },
        {
            "diagnostic_name": "carrier_face_boundary_adjacency_count",
            "diagnostic_value": carrier_boundary,
            "note": "Face adjacencies crossing carrier/noncarrier boundary.",
        },
        {
            "diagnostic_name": "carrier_face_external_neighbor_count",
            "diagnostic_value": len(external_neighbors),
            "note": "Distinct noncarrier faces adjacent to carrier region.",
        },
        {
            "diagnostic_name": "max_distance_to_mixed_core",
            "diagnostic_value": max_dist,
            "note": "Max face-adjacency distance from carrier faces to nearest mixed seam-boundary face.",
        },
        {
            "diagnostic_name": "mean_distance_to_mixed_core",
            "diagnostic_value": mean_dist,
            "note": "Mean face-adjacency distance from carrier faces to nearest mixed seam-boundary face.",
        },
    ]

    shape_summary = {
        "face_count": len(all_faces),
        "carrier_face_count": len(carrier_faces),
        "carrier_face_fraction": len(carrier_faces) / len(all_faces) if all_faces else 0,
        "carrier_hexagon_count": len(carrier_hex),
        "carrier_pentagon_count": len(carrier_pen),
        "mixed_core_face_count": len(mixed_faces),
        "hp_boundary_face_count": len(hp_boundary_faces),
        "carrier_adjacent_face_count": len(carrier_adjacent_faces),
        "noncarrier_face_count": len(noncarrier_faces),
        "carrier_face_component_count": as_int(fu02d1_manifest.get("carrier_face_component_count", 0)),
        "largest_carrier_face_component_count": as_int(fu02d1_manifest.get("largest_carrier_face_component_count", 0)),
        "carrier_face_internal_adjacency_count": carrier_internal,
        "carrier_face_boundary_adjacency_count": carrier_boundary,
        "carrier_face_external_neighbor_count": len(external_neighbors),
        "max_distance_to_mixed_core": max_dist,
        "mean_distance_to_mixed_core": mean_dist,
        "carrier_hexagon_intervals": contiguous_intervals(carrier_hex),
        "carrier_pentagon_intervals": contiguous_intervals(carrier_pen),
        "mixed_face_intervals": contiguous_intervals(sorted(mixed_faces)),
    }
    shape_summary["shape_label"] = classify_shape(shape_summary)
    shape_summary["scope_note"] = "Graph-level descriptive shape diagnostics only; not a full C60 automorphism or physical geometry proof."

    out = cfg["outputs"]
    write_csv(outdir / out["visualization_nodes_csv"], node_rows, [
        "node_id", "degree", "node_role_label", "incident_hh_consensus_count",
        "incident_hp_secondary_count", "incident_total_carrier_count",
        "carrier_region_member", "visual_size", "visual_layer",
    ])
    write_csv(outdir / out["visualization_edges_csv"], edge_rows, [
        "edge_key", "source", "target", "edge_type", "shared_face_types",
        "carrier_role", "is_hh_consensus", "is_hp_secondary", "is_role_carrier",
        "shell_distance_to_hh_consensus", "visual_weight", "visual_layer",
    ])
    write_csv(outdir / out["visualization_faces_csv"], face_rows, [
        "face_id", "face_type", "face_carrier_role_label", "carrier_edge_count",
        "hh_consensus_edge_count", "hp_secondary_edge_count",
        "mixed_role_junction_node_count", "carrier_region_member",
        "face_distance_to_mixed_core", "visual_weight", "visual_layer",
        "carrier_edge_keys", "boundary_node_ids",
    ])
    write_csv(outdir / out["symmetry_orbit_inspection_csv"], inspection_rows, [
        "diagnostic_name", "diagnostic_value", "note",
    ])

    with (outdir / out["region_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(region_manifest, f, indent=2, sort_keys=True)
    with (outdir / out["shape_diagnostic_summary_json"]).open("w", encoding="utf-8") as f:
        json.dump(shape_summary, f, indent=2, sort_keys=True)

    if cfg.get("visualization", {}).get("write_simple_svg", True):
        write_simple_svg(
            outdir / out["simple_region_map_svg"],
            face_rows,
            int(cfg["visualization"].get("svg_width", 1200)),
            int(cfg["visualization"].get("svg_height", 800)),
        )
    else:
        warnings.append({"severity": "info", "message": "Simple SVG output disabled by config."})

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu02d1_run_id": fu02d1_manifest.get("run_id", ""),
        "fu02e1_run_id": fu02e1_manifest.get("run_id", ""),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "node_count": len(node_rows),
        "edge_count": len(edge_rows),
        "face_count": len(face_rows),
        "carrier_node_count": len(carrier_nodes),
        "carrier_edge_count": len(carrier_edges),
        "carrier_face_count": len(carrier_faces),
        "mixed_face_count": len(mixed_faces),
        "hp_boundary_face_count": len(hp_boundary_faces),
        "shape_label": shape_summary["shape_label"],
        "shape_summary": shape_summary,
        "row_counts": {
            "visualization_nodes": len(node_rows),
            "visualization_edges": len(edge_rows),
            "visualization_faces": len(face_rows),
            "symmetry_orbit_inspection": len(inspection_rows),
            "warnings": len(warnings),
        },
        "scope_note": "FU02f exports visualization-ready artifacts and conservative graph shape diagnostics only.",
    }

    with (outdir / out["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    with (outdir / out["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)
    with (outdir / out["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02f carrier role visualization and symmetry-orbit inspection.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
