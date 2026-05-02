#!/usr/bin/env python3
"""
BMS-FU02d1 — Face Parser Repair and Face-Level Carrier Localization

Purpose:
  Repair FU02d-v0 face parsing and map FU02d carrier roles onto C60 faces.

Core question:
  Auf welchen Faces liegt das 30-edge / 25-node seam-boundary carrier network?
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


Edge = Tuple[str, str]


def edge_key(a: str, b: str) -> Edge:
    return (a, b) if a <= b else (b, a)


def edge_key_str(e: Edge) -> str:
    return f"{e[0]}--{e[1]}"


def parse_edge_key(s: str) -> Edge:
    a, b = str(s).split("--", 1)
    return edge_key(a, b)


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


def parse_list_like(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    # Accept semicolon, comma, pipe, whitespace; strip simple brackets/quotes.
    s = s.strip("[](){}")
    parts = re.split(r"[;,|\\s]+", s)
    return [p.strip().strip("'\"") for p in parts if p.strip().strip("'\"")]


def face_type(face_id: str) -> str:
    if face_id.startswith("H"):
        return "H"
    if face_id.startswith("P"):
        return "P"
    if "hex" in face_id.lower():
        return "H"
    if "pent" in face_id.lower():
        return "P"
    return ""


def row_face_id(row: Dict[str, str], fallback_index: int) -> str:
    for key in ["face_id", "id", "face", "name"]:
        if row.get(key):
            return str(row[key])
    return f"face_{fallback_index:03d}"


def detect_edge_face_mapping(
    c60_edges: List[Dict[str, str]],
    c60_faces: List[Dict[str, str]],
    cfg: Dict[str, Any],
    warnings: List[Dict[str, str]],
) -> Tuple[Dict[str, List[str]], Dict[str, Any]]:
    audit: Dict[str, Any] = {
        "detected_edge_face_columns": [],
        "detected_face_node_column": "",
        "edge_face_mapping_source": "",
        "mapped_edge_count": 0,
        "unmapped_edge_count": 0,
        "face_count": len(c60_faces),
        "warnings": [],
    }

    if not c60_edges:
        warnings.append({"severity": "error", "message": "No C60 edge rows found."})
        audit["warnings"].append("No C60 edge rows found.")
        return {}, audit

    edge_cols = set(c60_edges[0].keys())
    mapping: Dict[str, List[str]] = {}

    # 1. Paired edge columns.
    for pair in cfg["parser"]["edge_face_column_candidates"]["paired"]:
        if all(col in edge_cols for col in pair):
            for r in c60_edges:
                es = edge_key_str(edge_key(r["source"], r["target"]))
                faces = [str(r[col]).strip() for col in pair if str(r.get(col, "")).strip()]
                mapping[es] = faces
            audit["detected_edge_face_columns"] = pair
            audit["edge_face_mapping_source"] = "edge_table_paired_columns"
            break

    # 2. List-like edge columns.
    if not mapping:
        for col in cfg["parser"]["edge_face_column_candidates"]["list_like"]:
            if col in edge_cols:
                trial = {}
                for r in c60_edges:
                    es = edge_key_str(edge_key(r["source"], r["target"]))
                    faces = parse_list_like(r.get(col, ""))
                    trial[es] = faces
                if sum(1 for v in trial.values() if v) > 0:
                    mapping = trial
                    audit["detected_edge_face_columns"] = [col]
                    audit["edge_face_mapping_source"] = "edge_table_list_column"
                    break

    # 3. Reconstruct from face node cycles.
    if not mapping:
        face_cols = set(c60_faces[0].keys()) if c60_faces else set()
        detected_face_node_col = ""
        for col in cfg["parser"]["face_node_column_candidates"]:
            if col in face_cols:
                detected_face_node_col = col
                break

        if detected_face_node_col:
            audit["detected_face_node_column"] = detected_face_node_col
            for idx, frow in enumerate(c60_faces, start=1):
                fid = row_face_id(frow, idx)
                nodes = parse_list_like(frow.get(detected_face_node_col, ""))
                if len(nodes) < 3:
                    continue
                for a, b in zip(nodes, nodes[1:] + nodes[:1]):
                    es = edge_key_str(edge_key(a, b))
                    mapping.setdefault(es, []).append(fid)
            audit["edge_face_mapping_source"] = "face_table_node_cycle_reconstruction"
        else:
            msg = "No usable edge face columns or face node-cycle column detected."
            warnings.append({"severity": "error", "message": msg})
            audit["warnings"].append(msg)

    all_edge_keys = {edge_key_str(edge_key(r["source"], r["target"])) for r in c60_edges}
    mapped = sum(1 for es in all_edge_keys if mapping.get(es))
    unmapped = len(all_edge_keys) - mapped
    audit["mapped_edge_count"] = mapped
    audit["unmapped_edge_count"] = unmapped

    if mapped < len(all_edge_keys):
        msg = f"Mapped {mapped}/{len(all_edge_keys)} C60 edges to faces; {unmapped} unmapped."
        warnings.append({"severity": "warning", "message": msg})
        audit["warnings"].append(msg)

    # Deduplicate face lists.
    mapping = {es: sorted(set(faces)) for es, faces in mapping.items()}

    return mapping, audit


def build_face_adjacency(edge_to_faces: Dict[str, List[str]]) -> Tuple[Dict[str, Set[str]], List[Dict[str, Any]]]:
    face_adj: Dict[str, Set[str]] = defaultdict(set)
    rows: List[Dict[str, Any]] = []
    for es, faces in sorted(edge_to_faces.items()):
        if len(faces) < 2:
            continue
        for i, a in enumerate(faces):
            for b in faces[i + 1:]:
                if a == b:
                    continue
                face_adj[a].add(b)
                face_adj[b].add(a)
                rows.append({
                    "edge_key": es,
                    "face_a": a,
                    "face_b": b,
                    "face_a_type": face_type(a),
                    "face_b_type": face_type(b),
                })
    return face_adj, rows


def connected_components(nodes: Set[str], adj: Dict[str, Set[str]]) -> List[Set[str]]:
    seen = set()
    comps = []
    for n in sorted(nodes):
        if n in seen:
            continue
        q = deque([n])
        seen.add(n)
        comp = set()
        while q:
            x = q.popleft()
            comp.add(x)
            for y in adj.get(x, set()):
                if y in nodes and y not in seen:
                    seen.add(y)
                    q.append(y)
        comps.append(comp)
    comps.sort(key=lambda c: (-len(c), sorted(c)[0] if c else ""))
    return comps


def classify_face(hh: int, hp: int, carriers: int, carrier_adjacent: bool) -> str:
    if hh > 0 and hp > 0:
        return "mixed_seam_boundary_face"
    if hh > 0:
        return "hh_seam_face"
    if hp > 0:
        return "hp_boundary_face"
    if carrier_adjacent:
        return "carrier_adjacent_face"
    if carriers == 0:
        return "noncarrier_face"
    return "parser_unresolved_face"


def region_label(carrier_face_count: int, component_count: int, largest_component_count: int, total_faces: int) -> str:
    if carrier_face_count == 0:
        return "no_carrier_faces_or_parser_failure"
    frac = carrier_face_count / total_faces if total_faces else 0
    if component_count == 1 and frac <= 0.35:
        return "localized_patch_candidate"
    if component_count == 1 and frac <= 0.75:
        return "connected_face_region_candidate"
    if component_count == 1 and frac > 0.75:
        return "face_belt_or_large_region_candidate"
    if component_count > 1 and largest_component_count >= max(2, carrier_face_count // 2):
        return "dominant_component_with_fragments_candidate"
    return "fragmented_face_region_candidate"


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []

    fu02d_dir = root / cfg["inputs"]["fu02d_output_dir"]
    fu02c_dir = root / cfg["inputs"]["fu02c_output_dir"]

    fu02d_edges = read_csv(fu02d_dir / "bms_fu02d_carrier_edge_geometry.csv")
    fu02d_nodes = read_csv(fu02d_dir / "bms_fu02d_carrier_node_geometry.csv")
    fu02d_manifest = read_json(fu02d_dir / "bms_fu02d_run_manifest.json")
    fu02d_warnings = read_json(fu02d_dir / "bms_fu02d_warnings.json") if (fu02d_dir / "bms_fu02d_warnings.json").exists() else []
    fu02c_consensus = read_csv(fu02c_dir / "bms_fu02c_consensus_carriers.csv")

    if fu02d_warnings:
        warnings.append({"severity": "info", "message": f"FU02d warnings carried forward: {len(fu02d_warnings)}"})

    c60_edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    c60_nodes = read_csv(root / cfg["inputs"]["c60_nodes_csv"])
    c60_faces = read_csv(root / cfg["inputs"]["c60_faces_csv"])
    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])

    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    edge_to_faces, audit = detect_edge_face_mapping(c60_edges, c60_faces, cfg, warnings)
    face_adj, face_adj_rows = build_face_adjacency(edge_to_faces)

    # Face ids from both face table and edge mapping
    face_ids = set()
    for i, row in enumerate(c60_faces, start=1):
        face_ids.add(row_face_id(row, i))
    for faces in edge_to_faces.values():
        face_ids.update(faces)

    # Carrier sets from FU02d
    hh_edges = {r["edge_key"] for r in fu02d_edges if r.get("role_group") == "HH_CONSENSUS"}
    hp_edges = {r["edge_key"] for r in fu02d_edges if r.get("role_group") == "HP_SECONDARY"}
    carrier_edges = hh_edges | hp_edges

    # Node mixed junctions from FU02d
    mixed_nodes = {r["node_id"] for r in fu02d_nodes if r.get("carrier_junction_label") == "mixed_role_junction"}
    carrier_nodes = {r["node_id"] for r in fu02d_nodes if r.get("carrier_junction_label") != "noncarrier_node"}

    # Face -> boundary edges
    face_to_edges: Dict[str, List[str]] = defaultdict(list)
    for es, faces in edge_to_faces.items():
        for f in faces:
            face_to_edges[f].append(es)

    # Carrier-adjacent faces = faces adjacent to carrier faces but without carrier edges
    face_carrier_raw = {}
    for fid in face_ids:
        inc = sorted(face_to_edges.get(fid, []))
        hh = sorted(e for e in inc if e in hh_edges)
        hp = sorted(e for e in inc if e in hp_edges)
        car = sorted(e for e in inc if e in carrier_edges)
        face_carrier_raw[fid] = (hh, hp, car)

    carrier_faces = {fid for fid, (_, _, car) in face_carrier_raw.items() if car}
    carrier_adjacent_faces = {nb for fid in carrier_faces for nb in face_adj.get(fid, set())} - carrier_faces

    # Face localization rows
    face_rows: List[Dict[str, Any]] = []
    for fid in sorted(face_ids):
        inc = sorted(face_to_edges.get(fid, []))
        hh, hp, car = face_carrier_raw[fid]
        face_nodes = sorted({n for es in inc for n in parse_edge_key(es)})
        mixed_count = len(set(face_nodes) & mixed_nodes)
        carrier_node_count = len(set(face_nodes) & carrier_nodes)
        label = classify_face(len(hh), len(hp), len(car), fid in carrier_adjacent_faces)
        face_rows.append({
            "face_id": fid,
            "face_type": face_type(fid),
            "boundary_edge_count": len(inc),
            "hh_consensus_edge_count": len(hh),
            "hp_secondary_edge_count": len(hp),
            "carrier_edge_count": len(car),
            "mixed_role_junction_node_count": mixed_count,
            "carrier_node_count": carrier_node_count,
            "face_carrier_role_label": label,
            "hh_consensus_edge_keys": ";".join(hh),
            "hp_secondary_edge_keys": ";".join(hp),
            "carrier_edge_keys": ";".join(car),
            "boundary_edge_keys": ";".join(inc),
            "boundary_node_ids": ";".join(face_nodes),
        })

    # Face components
    group_to_faces = {
        "HH_FACE_SET": {r["face_id"] for r in face_rows if as_int(r["hh_consensus_edge_count"]) > 0},
        "HP_FACE_SET": {r["face_id"] for r in face_rows if as_int(r["hp_secondary_edge_count"]) > 0},
        "MIXED_FACE_SET": {r["face_id"] for r in face_rows if as_int(r["hh_consensus_edge_count"]) > 0 and as_int(r["hp_secondary_edge_count"]) > 0},
        "CARRIER_FACE_SET": {r["face_id"] for r in face_rows if as_int(r["carrier_edge_count"]) > 0},
    }

    component_rows: List[Dict[str, Any]] = []
    for group, faces in group_to_faces.items():
        comps = connected_components(faces, face_adj)
        for i, comp in enumerate(comps, start=1):
            rows = [r for r in face_rows if r["face_id"] in comp]
            ftype_counts = Counter(r["face_type"] for r in rows)
            component_rows.append({
                "face_group": group,
                "component_id": i,
                "component_face_count": len(comp),
                "hexagon_count": ftype_counts.get("H", 0),
                "pentagon_count": ftype_counts.get("P", 0),
                "hh_consensus_edge_count": sum(as_int(r["hh_consensus_edge_count"]) for r in rows),
                "hp_secondary_edge_count": sum(as_int(r["hp_secondary_edge_count"]) for r in rows),
                "carrier_edge_count": sum(as_int(r["carrier_edge_count"]) for r in rows),
                "mixed_role_junction_node_count": sum(as_int(r["mixed_role_junction_node_count"]) for r in rows),
                "face_ids": ";".join(sorted(comp)),
            })

    carrier_face_count = len(group_to_faces["CARRIER_FACE_SET"])
    carrier_comps = [r for r in component_rows if r["face_group"] == "CARRIER_FACE_SET"]
    largest_carrier_comp = max((as_int(r["component_face_count"]) for r in carrier_comps), default=0)
    carrier_component_count = len(carrier_comps)

    # Summary rows
    face_label_counts = Counter(r["face_carrier_role_label"] for r in face_rows)
    face_type_carrier_counts = Counter(r["face_type"] for r in face_rows if as_int(r["carrier_edge_count"]) > 0)
    carrier_summary_rows = [
        {
            "metric_name": "face_parser_source",
            "metric_value": audit.get("edge_face_mapping_source", ""),
            "note": "How edge-to-face incidence was obtained.",
        },
        {
            "metric_name": "mapped_edge_count",
            "metric_value": audit.get("mapped_edge_count", 0),
            "note": "Number of C60 edges mapped to at least one face.",
        },
        {
            "metric_name": "unmapped_edge_count",
            "metric_value": audit.get("unmapped_edge_count", 0),
            "note": "Number of C60 edges without face mapping.",
        },
        {
            "metric_name": "carrier_face_count",
            "metric_value": carrier_face_count,
            "note": "Faces incident to at least one H,H or H,P carrier edge.",
        },
        {
            "metric_name": "carrier_face_fraction",
            "metric_value": carrier_face_count / len(face_ids) if face_ids else 0,
            "note": "Fraction of faces incident to carrier edges.",
        },
        {
            "metric_name": "carrier_face_component_count",
            "metric_value": carrier_component_count,
            "note": "Connected components in carrier-face adjacency graph.",
        },
        {
            "metric_name": "largest_carrier_face_component_count",
            "metric_value": largest_carrier_comp,
            "note": "Largest connected carrier-face component size.",
        },
        {
            "metric_name": "region_label",
            "metric_value": region_label(carrier_face_count, carrier_component_count, largest_carrier_comp, len(face_ids)),
            "note": "Descriptive graph-level region label; not a visual proof.",
        },
    ]

    for key, val in sorted(face_label_counts.items()):
        carrier_summary_rows.append({
            "metric_name": f"face_label_count__{key}",
            "metric_value": val,
            "note": "Face localization label count.",
        })
    for key, val in sorted(face_type_carrier_counts.items()):
        carrier_summary_rows.append({
            "metric_name": f"carrier_face_type_count__{key}",
            "metric_value": val,
            "note": "Carrier face count by face type.",
        })

    # Visualization faces
    viz_rows = []
    for r in face_rows:
        viz_rows.append({
            "face_id": r["face_id"],
            "face_type": r["face_type"],
            "face_carrier_role_label": r["face_carrier_role_label"],
            "carrier_edge_count": r["carrier_edge_count"],
            "hh_consensus_edge_count": r["hh_consensus_edge_count"],
            "hp_secondary_edge_count": r["hp_secondary_edge_count"],
            "mixed_role_junction_node_count": r["mixed_role_junction_node_count"],
            "visual_weight": 4 if r["face_carrier_role_label"] == "mixed_seam_boundary_face" else 3 if r["face_carrier_role_label"] in {"hh_seam_face", "hp_boundary_face"} else 2 if r["face_carrier_role_label"] == "carrier_adjacent_face" else 1,
            "carrier_edge_keys": r["carrier_edge_keys"],
            "boundary_node_ids": r["boundary_node_ids"],
        })

    out = cfg["outputs"]

    write_csv(outdir / out["face_localization_csv"], face_rows, [
        "face_id", "face_type", "boundary_edge_count", "hh_consensus_edge_count",
        "hp_secondary_edge_count", "carrier_edge_count",
        "mixed_role_junction_node_count", "carrier_node_count",
        "face_carrier_role_label", "hh_consensus_edge_keys",
        "hp_secondary_edge_keys", "carrier_edge_keys",
        "boundary_edge_keys", "boundary_node_ids",
    ])
    write_csv(outdir / out["face_component_summary_csv"], component_rows, [
        "face_group", "component_id", "component_face_count", "hexagon_count",
        "pentagon_count", "hh_consensus_edge_count", "hp_secondary_edge_count",
        "carrier_edge_count", "mixed_role_junction_node_count", "face_ids",
    ])
    write_csv(outdir / out["face_adjacency_edges_csv"], face_adj_rows, [
        "edge_key", "face_a", "face_b", "face_a_type", "face_b_type",
    ])
    write_csv(outdir / out["carrier_face_summary_csv"], carrier_summary_rows, [
        "metric_name", "metric_value", "note",
    ])
    write_csv(outdir / out["visualization_faces_csv"], viz_rows, [
        "face_id", "face_type", "face_carrier_role_label", "carrier_edge_count",
        "hh_consensus_edge_count", "hp_secondary_edge_count",
        "mixed_role_junction_node_count", "visual_weight",
        "carrier_edge_keys", "boundary_node_ids",
    ])

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu02d_run_id": fu02d_manifest.get("run_id", ""),
        "fu02d_warning_count": len(fu02d_warnings),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "face_parser_source": audit.get("edge_face_mapping_source", ""),
        "detected_edge_face_columns": audit.get("detected_edge_face_columns", []),
        "detected_face_node_column": audit.get("detected_face_node_column", ""),
        "mapped_edge_count": audit.get("mapped_edge_count", 0),
        "unmapped_edge_count": audit.get("unmapped_edge_count", 0),
        "face_count": len(face_ids),
        "carrier_face_count": carrier_face_count,
        "carrier_face_fraction": carrier_face_count / len(face_ids) if face_ids else 0,
        "carrier_face_component_count": carrier_component_count,
        "largest_carrier_face_component_count": largest_carrier_comp,
        "face_label_counts": dict(sorted(face_label_counts.items())),
        "carrier_face_type_counts": dict(sorted(face_type_carrier_counts.items())),
        "region_label": region_label(carrier_face_count, carrier_component_count, largest_carrier_comp, len(face_ids)),
        "row_counts": {
            "face_localization": len(face_rows),
            "face_component_summary": len(component_rows),
            "face_adjacency_edges": len(face_adj_rows),
            "carrier_face_summary": len(carrier_summary_rows),
            "visualization_faces": len(viz_rows),
            "warnings": len(warnings),
        },
    }

    with (outdir / out["face_parser_audit_json"]).open("w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, sort_keys=True)
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
    parser = argparse.ArgumentParser(description="Run BMS-FU02d1 face parser repair and face-level carrier localization.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
