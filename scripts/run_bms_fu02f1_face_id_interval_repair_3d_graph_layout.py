#!/usr/bin/env python3
"""
BMS-FU02f1 — Face-ID Interval Repair and 3D/Graph Layout Export

Purpose:
  Repair FU02f face-id interval diagnostics and export deterministic graph-layout
  artifacts for inspecting the compact role-balanced C60 carrier region.

Scope:
  Layout coordinates are inspection coordinates only, not physical C60 geometry.
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


def as_int(x: Any, default: int = 0) -> int:
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


def parse_face_id(face_id: str) -> Tuple[str, int]:
    """
    Robustly parse generated face ids such as H_17, P_09, H17, H-17,
    hex_17, pentagon_09.
    """
    s = str(face_id).strip()
    lower = s.lower()
    if lower.startswith("hex"):
        prefix = "H"
    elif lower.startswith("pent"):
        prefix = "P"
    elif lower.startswith("h"):
        prefix = "H"
    elif lower.startswith("p"):
        prefix = "P"
    else:
        prefix = re.sub(r"[^A-Za-z].*$", "", s).upper()[:1] or "?"

    m = re.search(r"(\d+)\s*$", s)
    idx = int(m.group(1)) if m else -1
    return prefix, idx


def canonical_face_id(prefix: str, idx: int) -> str:
    if idx < 0:
        return prefix
    return f"{prefix}_{idx:02d}"


def interval_string(face_ids: Iterable[str]) -> str:
    groups: Dict[str, List[int]] = {}
    unresolved: List[str] = []
    for fid in face_ids:
        prefix, idx = parse_face_id(fid)
        if idx < 0:
            unresolved.append(fid)
            continue
        groups.setdefault(prefix, []).append(idx)

    chunks: List[str] = []
    for prefix in sorted(groups):
        nums = sorted(set(groups[prefix]))
        if not nums:
            continue
        start = prev = nums[0]
        for n in nums[1:]:
            if n == prev + 1:
                prev = n
            else:
                chunks.append(
                    f"{canonical_face_id(prefix, start)}-{canonical_face_id(prefix, prev)}"
                    if start != prev else canonical_face_id(prefix, start)
                )
                start = prev = n
        chunks.append(
            f"{canonical_face_id(prefix, start)}-{canonical_face_id(prefix, prev)}"
            if start != prev else canonical_face_id(prefix, start)
        )

    chunks.extend(sorted(unresolved))
    return ";".join(chunks)


def face_type(face_id: str) -> str:
    prefix, _ = parse_face_id(face_id)
    return prefix if prefix in {"H", "P"} else ""


def role_radius(label: str) -> float:
    return {
        "mixed_seam_boundary_face": 1.0,
        "hp_boundary_face": 1.65,
        "carrier_adjacent_face": 2.35,
        "noncarrier_face": 3.05,
    }.get(label, 2.75)


def role_layer(label: str) -> int:
    return {
        "mixed_seam_boundary_face": 4,
        "hp_boundary_face": 3,
        "carrier_adjacent_face": 2,
        "noncarrier_face": 1,
    }.get(label, 1)


def role_color(label: str) -> str:
    return {
        "mixed_seam_boundary_face": "#f2b84b",
        "hp_boundary_face": "#64b5f6",
        "carrier_adjacent_face": "#b0bec5",
        "noncarrier_face": "#eeeeee",
    }.get(label, "#dddddd")


def deterministic_face_layout(face_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    # Group by role shell; sort each shell by face type and numeric id.
    groups: Dict[str, List[Dict[str, str]]] = {}
    for r in face_rows:
        groups.setdefault(r["face_carrier_role_label"], []).append(r)

    layout_rows: List[Dict[str, Any]] = []
    for label, rows in sorted(groups.items(), key=lambda kv: -role_layer(kv[0])):
        rows = sorted(rows, key=lambda r: (face_type(r["face_id"]), parse_face_id(r["face_id"])[1], r["face_id"]))
        n = len(rows)
        radius = role_radius(label)
        # Offset per shell to avoid perfect radial overlaps.
        offset = {
            "mixed_seam_boundary_face": -math.pi / 2,
            "hp_boundary_face": -math.pi / 2 + math.pi / 10,
            "carrier_adjacent_face": -math.pi / 2 + math.pi / 5,
            "noncarrier_face": -math.pi / 2 + math.pi / 7,
        }.get(label, 0.0)
        for i, r in enumerate(rows):
            angle = offset + 2 * math.pi * i / max(1, n)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            layout_rows.append({
                "face_id": r["face_id"],
                "face_type": r.get("face_type", face_type(r["face_id"])),
                "face_carrier_role_label": label,
                "carrier_edge_count": r.get("carrier_edge_count", 0),
                "hh_consensus_edge_count": r.get("hh_consensus_edge_count", 0),
                "hp_secondary_edge_count": r.get("hp_secondary_edge_count", 0),
                "mixed_role_junction_node_count": r.get("mixed_role_junction_node_count", 0),
                "face_distance_to_mixed_core": r.get("face_distance_to_mixed_core", ""),
                "layout_x": x,
                "layout_y": y,
                "layout_radius": radius,
                "layout_angle_rad": angle,
                "layout_role_shell": label,
                "visual_layer": role_layer(label),
                "visual_color_hint": role_color(label),
                "layout_scope_note": "Role-shell circular inspection layout; not physical C60 geometry.",
            })
    return sorted(layout_rows, key=lambda r: (r["visual_layer"], r["face_type"], parse_face_id(r["face_id"])[1]))


def deterministic_node_layout(node_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    # Fibonacci sphere-like deterministic index layout, based only on node order.
    rows = sorted(node_rows, key=lambda r: as_int(re.search(r"(\d+)$", r["node_id"]).group(1) if re.search(r"(\d+)$", r["node_id"]) else 0))
    n = len(rows)
    out = []
    golden = math.pi * (3 - math.sqrt(5))
    for i, r in enumerate(rows):
        y = 1 - (2 * i + 1) / max(1, n)
        rad = math.sqrt(max(0.0, 1 - y * y))
        theta = golden * i
        x = math.cos(theta) * rad
        z = math.sin(theta) * rad
        out.append({
            "node_id": r["node_id"],
            "node_role_label": r.get("node_role_label", ""),
            "carrier_region_member": r.get("carrier_region_member", 0),
            "layout_x": x,
            "layout_y": y,
            "layout_z": z,
            "layout_scope_note": "Deterministic spherical index layout; not physical C60 coordinates.",
        })
    return out


def write_svg(path: Path, face_layout: List[Dict[str, Any]], width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cx, cy = width / 2, height / 2
    scale = min(width, height) / 7.2

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg.append('<rect width="100%" height="100%" fill="#111827"/>')
    svg.append('<text x="40" y="42" fill="#ffffff" font-family="sans-serif" font-size="25">BMS-FU02f1 repaired carrier-role map</text>')
    svg.append('<text x="40" y="72" fill="#cbd5e1" font-family="sans-serif" font-size="14">Role-shell circular layout; not physical C60 geometry.</text>')

    # shell circles
    for radius, label in [(1.0, "mixed core"), (1.65, "boundary"), (2.35, "adjacent"), (3.05, "noncarrier")]:
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{radius*scale:.2f}" fill="none" stroke="#334155" stroke-width="1"/>')
        svg.append(f'<text x="{cx + radius*scale + 8:.1f}" y="{cy - 4:.1f}" fill="#94a3b8" font-family="sans-serif" font-size="11">{label}</text>')

    # faces
    for r in sorted(face_layout, key=lambda x: int(x["visual_layer"])):
        x = cx + float(r["layout_x"]) * scale
        y = cy + float(r["layout_y"]) * scale
        label = r["face_carrier_role_label"]
        fill = r["visual_color_hint"]
        stroke = "#ffffff" if int(r["visual_layer"]) >= 3 else "#64748b"
        size = 22 if label == "mixed_seam_boundary_face" else 19 if label == "hp_boundary_face" else 16
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        svg.append(f'<text x="{x:.1f}" y="{y+4:.1f}" fill="#111827" text-anchor="middle" font-family="monospace" font-size="11">{r["face_id"]}</text>')

    # legend
    legend = [
        ("mixed seam-boundary core", "#f2b84b"),
        ("H/P boundary layer", "#64b5f6"),
        ("carrier-adjacent", "#b0bec5"),
        ("noncarrier", "#eeeeee"),
    ]
    lx, ly = 40, height - 135
    svg.append(f'<text x="{lx}" y="{ly}" fill="#ffffff" font-family="sans-serif" font-size="18">Legend</text>')
    for i, (lab, col) in enumerate(legend):
        y = ly + 28 + i * 25
        svg.append(f'<rect x="{lx}" y="{y-14}" width="24" height="16" fill="{col}"/>')
        svg.append(f'<text x="{lx+34}" y="{y}" fill="#ffffff" font-family="sans-serif" font-size="13">{lab}</text>')

    svg.append('</svg>')
    path.write_text("\n".join(svg), encoding="utf-8")


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    fu02f_dir = root / cfg["inputs"]["fu02f_output_dir"]
    faces = read_csv(fu02f_dir / "bms_fu02f_visualization_faces.csv")
    nodes = read_csv(fu02f_dir / "bms_fu02f_visualization_nodes.csv")
    edges = read_csv(fu02f_dir / "bms_fu02f_visualization_edges.csv")
    fu02f_manifest = read_json(fu02f_dir / "bms_fu02f_run_manifest.json")
    fu02f_shape = read_json(fu02f_dir / "bms_fu02f_shape_diagnostic_summary.json")
    region_manifest = read_json(fu02f_dir / "bms_fu02f_region_manifest.json")

    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])
    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    carrier_faces = region_manifest.get("carrier_face_ids", [])
    mixed_faces = region_manifest.get("mixed_face_ids", [])
    hp_boundary_faces = region_manifest.get("hp_boundary_face_ids", [])
    adjacent_faces = region_manifest.get("carrier_adjacent_face_ids", [])
    noncarrier_faces = region_manifest.get("noncarrier_face_ids", [])

    interval_summary = {
        "carrier_hexagon_intervals": interval_string([f for f in carrier_faces if face_type(f) == "H"]),
        "carrier_pentagon_intervals": interval_string([f for f in carrier_faces if face_type(f) == "P"]),
        "mixed_face_intervals": interval_string(mixed_faces),
        "hp_boundary_face_intervals": interval_string(hp_boundary_faces),
        "carrier_adjacent_face_intervals": interval_string(adjacent_faces),
        "noncarrier_face_intervals": interval_string(noncarrier_faces),
        "carrier_face_count": len(carrier_faces),
        "mixed_face_count": len(mixed_faces),
        "hp_boundary_face_count": len(hp_boundary_faces),
        "carrier_adjacent_face_count": len(adjacent_faces),
        "noncarrier_face_count": len(noncarrier_faces),
        "scope_note": "Face-id intervals are generated-id diagnostics only, not physical coordinates.",
    }

    face_layout = deterministic_face_layout(faces)
    node_layout = deterministic_node_layout(nodes)

    # Edge layout joins 2D node coordinates by node id if possible.
    node2layout = {r["node_id"]: r for r in node_layout}
    edge_layout = []
    for e in edges:
        a = node2layout.get(e["source"], {})
        b = node2layout.get(e["target"], {})
        edge_layout.append({
            "edge_key": e["edge_key"],
            "source": e["source"],
            "target": e["target"],
            "carrier_role": e.get("carrier_role", ""),
            "edge_type": e.get("edge_type", ""),
            "shared_face_types": e.get("shared_face_types", ""),
            "source_layout_x": a.get("layout_x", ""),
            "source_layout_y": a.get("layout_y", ""),
            "source_layout_z": a.get("layout_z", ""),
            "target_layout_x": b.get("layout_x", ""),
            "target_layout_y": b.get("layout_y", ""),
            "target_layout_z": b.get("layout_z", ""),
            "layout_scope_note": "Endpoint coordinates are deterministic spherical index layout, not physical C60 coordinates.",
        })

    out = cfg["outputs"]
    with (outdir / out["repaired_interval_summary_json"]).open("w", encoding="utf-8") as f:
        json.dump(interval_summary, f, indent=2, sort_keys=True)

    write_csv(outdir / out["face_layout_csv"], face_layout, [
        "face_id", "face_type", "face_carrier_role_label", "carrier_edge_count",
        "hh_consensus_edge_count", "hp_secondary_edge_count", "mixed_role_junction_node_count",
        "face_distance_to_mixed_core", "layout_x", "layout_y", "layout_radius",
        "layout_angle_rad", "layout_role_shell", "visual_layer", "visual_color_hint",
        "layout_scope_note",
    ])
    write_csv(outdir / out["node_layout_csv"], node_layout, [
        "node_id", "node_role_label", "carrier_region_member", "layout_x", "layout_y", "layout_z", "layout_scope_note",
    ])
    write_csv(outdir / out["edge_layout_csv"], edge_layout, [
        "edge_key", "source", "target", "carrier_role", "edge_type", "shared_face_types",
        "source_layout_x", "source_layout_y", "source_layout_z",
        "target_layout_x", "target_layout_y", "target_layout_z", "layout_scope_note",
    ])

    layout_manifest = {
        "face_layout_mode": cfg["layout"]["face_layout_mode"],
        "node_layout_mode": cfg["layout"]["node_layout_mode"],
        "face_interval_repair_success": all(interval_summary[k] for k in [
            "carrier_hexagon_intervals",
            "carrier_pentagon_intervals",
            "mixed_face_intervals",
            "hp_boundary_face_intervals",
        ]),
        "interval_summary": interval_summary,
        "layout_scope_note": "All coordinates are deterministic inspection layouts unless replaced by true molecular coordinates in a later block.",
    }
    with (outdir / out["graph_layout_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(layout_manifest, f, indent=2, sort_keys=True)

    write_svg(
        outdir / out["repaired_region_map_svg"],
        face_layout,
        int(cfg["layout"]["svg_width"]),
        int(cfg["layout"]["svg_height"]),
    )

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu02f_run_id": fu02f_manifest.get("run_id", ""),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "face_count": len(faces),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "carrier_face_count": len(carrier_faces),
        "mixed_face_count": len(mixed_faces),
        "hp_boundary_face_count": len(hp_boundary_faces),
        "interval_repair_success": layout_manifest["face_interval_repair_success"],
        "repaired_intervals": interval_summary,
        "fu02f_shape_label": fu02f_shape.get("shape_label", ""),
        "row_counts": {
            "face_layout": len(face_layout),
            "node_layout": len(node_layout),
            "edge_layout": len(edge_layout),
            "warnings": len(warnings),
        },
        "scope_note": "FU02f1 repairs face-id intervals and exports graph-layout artifacts; not physical 3D geometry.",
    }

    with (outdir / out["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    with (outdir / out["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)
    with (outdir / out["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02f1 face-id interval repair and graph layout export.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
