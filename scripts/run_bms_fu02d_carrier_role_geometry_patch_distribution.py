#!/usr/bin/env python3
"""
BMS-FU02d — Carrier Role Geometry and Patch Distribution

Purpose:
  Map FU02c carrier roles on the validated C60 cage graph.

Core question:
  Wo sitzen H,H consensus carriers and H,P secondary carriers in the C60 cage?
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

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


def as_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def as_int(x: Any, default: int = 0) -> int:
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


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


def build_edge_adjacency(edges: Iterable[Edge]) -> Dict[str, Set[str]]:
    edge_list = sorted(edge_key_str(e) for e in edges)
    node_to_edges: Dict[str, Set[str]] = defaultdict(set)
    for es in edge_list:
        a, b = parse_edge_key(es)
        node_to_edges[a].add(es)
        node_to_edges[b].add(es)

    adj: Dict[str, Set[str]] = {es: set() for es in edge_list}
    for es in edge_list:
        a, b = parse_edge_key(es)
        adj[es] |= node_to_edges[a]
        adj[es] |= node_to_edges[b]
        adj[es].discard(es)
    return adj


def connected_components(edge_set: Set[str], edge_adj: Dict[str, Set[str]]) -> List[Set[str]]:
    seen = set()
    comps = []
    for e in sorted(edge_set):
        if e in seen:
            continue
        q = deque([e])
        seen.add(e)
        comp = set()
        while q:
            x = q.popleft()
            comp.add(x)
            for y in edge_adj.get(x, set()):
                if y in edge_set and y not in seen:
                    seen.add(y)
                    q.append(y)
        comps.append(comp)
    comps.sort(key=lambda c: (-len(c), sorted(c)[0] if c else ""))
    return comps


def edge_shell_distances(all_edges: Set[str], seed_edges: Set[str], edge_adj: Dict[str, Set[str]]) -> Dict[str, int]:
    dist = {e: -1 for e in all_edges}
    q = deque()
    for e in seed_edges:
        if e in dist:
            dist[e] = 0
            q.append(e)
    while q:
        x = q.popleft()
        for y in edge_adj.get(x, set()):
            if y in dist and dist[y] < 0:
                dist[y] = dist[x] + 1
                q.append(y)
    return dist


def parse_face_list(value: str) -> List[str]:
    if value is None:
        return []
    return [x.strip() for x in str(value).replace(",", ";").split(";") if x.strip()]


def face_type(face_id: str) -> str:
    if face_id.startswith("H"):
        return "H"
    if face_id.startswith("P"):
        return "P"
    return ""


def classify_node(hh: int, hp: int, total: int) -> str:
    if total <= 0:
        return "noncarrier_node"
    if hh > 0 and hp > 0:
        return "mixed_role_junction"
    if hh > 0:
        return "hh_spine_node"
    if hp > 0:
        return "hp_boundary_node"
    return "carrier_isolated_endpoint"


def classify_face(hh: int, hp: int, total: int) -> str:
    if total <= 0:
        return "noncarrier_face"
    if hh > 0 and hp > 0:
        return "mixed_patch_boundary_face"
    if hh > 0:
        return "hh_patch_face"
    if hp > 0:
        return "hp_boundary_face"
    return "carrier_sparse_face"


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []

    fu_dir = root / cfg["inputs"]["fu02c_output_dir"]
    consensus_path = fu_dir / "bms_fu02c_consensus_carriers.csv"
    summary_path = fu_dir / "bms_fu02c_edge_representation_summary.csv"
    fu_manifest_path = fu_dir / "bms_fu02c_run_manifest.json"
    fu_warnings_path = fu_dir / "bms_fu02c_warnings.json"

    consensus = read_csv(consensus_path)
    rep_summary = read_csv(summary_path) if summary_path.exists() else []
    fu_manifest = read_json(fu_manifest_path)
    fu_warnings = read_json(fu_warnings_path) if fu_warnings_path.exists() else []
    if fu_warnings:
        warnings.append({"severity": "info", "message": f"FU02c warnings carried forward: {len(fu_warnings)}"})

    c60_edges = read_csv(root / cfg["inputs"]["c60_edges_csv"])
    c60_nodes = read_csv(root / cfg["inputs"]["c60_nodes_csv"])
    c60_faces = read_csv(root / cfg["inputs"]["c60_faces_csv"])
    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])

    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 graph manifest does not report c60_valid=true."})

    labels = cfg["carrier_groups"]
    hh_label = labels["hh_consensus_label"]
    hp_label = labels["hp_secondary_label"]

    edge_meta = {}
    all_edges: Set[str] = set()
    for r in c60_edges:
        es = edge_key_str(edge_key(r["source"], r["target"]))
        all_edges.add(es)
        edge_meta[es] = r

    consensus_by_edge = {r["edge_key"]: r for r in consensus}
    hh_edges = {r["edge_key"] for r in consensus if r["consensus_label"] == hh_label}
    hp_edges = {r["edge_key"] for r in consensus if r["consensus_label"] == hp_label}
    carrier_edges = hh_edges | hp_edges

    edge_adj = build_edge_adjacency(parse_edge_key(e) for e in all_edges)
    shell_to_hh = edge_shell_distances(all_edges, hh_edges, edge_adj)

    hh_comps = connected_components(hh_edges, edge_adj)
    hp_comps = connected_components(hp_edges, edge_adj)
    combined_comps = connected_components(carrier_edges, edge_adj)

    # representation summary lookup
    rep_summary_by_edge = defaultdict(dict)
    for r in rep_summary:
        rep_summary_by_edge[r["edge_key"]][r["representation_id"]] = r

    # Edge geometry rows
    edge_rows: List[Dict[str, Any]] = []
    for es in sorted(all_edges):
        meta = edge_meta.get(es, {})
        c = consensus_by_edge.get(es, {})
        adjacent_hh = sorted(edge_adj.get(es, set()) & hh_edges)
        adjacent_hp = sorted(edge_adj.get(es, set()) & hp_edges)
        role = c.get("consensus_label", "not_in_consensus_table")
        role_group = (
            "HH_CONSENSUS" if role == hh_label else
            "HP_SECONDARY" if role == hp_label else
            "OTHER"
        )

        reps = rep_summary_by_edge.get(es, {})
        edge_rows.append({
            "edge_key": es,
            "source": parse_edge_key(es)[0],
            "target": parse_edge_key(es)[1],
            "edge_type": meta.get("edge_type", c.get("edge_type", "")),
            "shared_face_types": meta.get("shared_face_types", c.get("shared_face_types", "")),
            "faces": meta.get("faces", ""),
            "consensus_label": role,
            "role_group": role_group,
            "is_hh_consensus": int(es in hh_edges),
            "is_hp_secondary": int(es in hp_edges),
            "is_role_carrier": int(es in carrier_edges),
            "shell_distance_to_hh_consensus": shell_to_hh.get(es, -1),
            "adjacent_hh_consensus_count": len(adjacent_hh),
            "adjacent_hp_secondary_count": len(adjacent_hp),
            "adjacent_hh_consensus_edges": ";".join(adjacent_hh),
            "adjacent_hp_secondary_edges": ";".join(adjacent_hp),
            "bond_class_weighted_rank": reps.get("bond_class_weighted", {}).get("rank_mean_delta", ""),
            "topology_only_equal_weight_rank": reps.get("topology_only_equal_weight", {}).get("rank_mean_delta", ""),
            "graph_distance_similarity_d3_rank": reps.get("graph_distance_similarity_d3", {}).get("rank_mean_delta", ""),
        })

    # Node geometry
    node_incident_edges = defaultdict(list)
    for es in all_edges:
        a, b = parse_edge_key(es)
        node_incident_edges[a].append(es)
        node_incident_edges[b].append(es)

    node_rows: List[Dict[str, Any]] = []
    for n in sorted({r.get("node_id", "") or r.get("id", "") for r in c60_nodes} | set(node_incident_edges.keys())):
        if not n:
            continue
        inc = sorted(node_incident_edges[n])
        inc_hh = [e for e in inc if e in hh_edges]
        inc_hp = [e for e in inc if e in hp_edges]
        inc_carrier = [e for e in inc if e in carrier_edges]
        total = len(inc_carrier)
        node_rows.append({
            "node_id": n,
            "degree": len(inc),
            "incident_hh_consensus_count": len(inc_hh),
            "incident_hp_secondary_count": len(inc_hp),
            "incident_total_carrier_count": total,
            "carrier_junction_label": classify_node(len(inc_hh), len(inc_hp), total),
            "incident_hh_consensus_edges": ";".join(inc_hh),
            "incident_hp_secondary_edges": ";".join(inc_hp),
            "incident_carrier_edges": ";".join(inc_carrier),
        })

    # Face geometry. Prefer edge face annotations because face tables may differ.
    face_to_edges = defaultdict(list)
    for es, meta in edge_meta.items():
        for f in parse_face_list(meta.get("faces", "")):
            face_to_edges[f].append(es)

    all_faces = sorted(set(face_to_edges.keys()) | {r.get("face_id", "") or r.get("id", "") for r in c60_faces if (r.get("face_id", "") or r.get("id", ""))})
    face_rows: List[Dict[str, Any]] = []
    for fid in all_faces:
        if not fid:
            continue
        inc = sorted(face_to_edges.get(fid, []))
        inc_hh = [e for e in inc if e in hh_edges]
        inc_hp = [e for e in inc if e in hp_edges]
        inc_carrier = [e for e in inc if e in carrier_edges]
        face_rows.append({
            "face_id": fid,
            "face_type": face_type(fid),
            "incident_edge_count": len(inc),
            "incident_hh_consensus_edges": len(inc_hh),
            "incident_hp_secondary_edges": len(inc_hp),
            "incident_total_carrier_edges": len(inc_carrier),
            "face_carrier_role_label": classify_face(len(inc_hh), len(inc_hp), len(inc_carrier)),
            "hh_consensus_edge_keys": ";".join(inc_hh),
            "hp_secondary_edge_keys": ";".join(inc_hp),
            "carrier_edge_keys": ";".join(inc_carrier),
        })

    # Component summaries
    def comp_summary_rows(group_name: str, comps: List[Set[str]]) -> List[Dict[str, Any]]:
        rows = []
        for i, comp in enumerate(comps, start=1):
            nodes = sorted({n for es in comp for n in parse_edge_key(es)})
            hh_count = sum(1 for e in comp if e in hh_edges)
            hp_count = sum(1 for e in comp if e in hp_edges)
            rows.append({
                "carrier_group": group_name,
                "component_id": i,
                "component_edge_count": len(comp),
                "component_node_count": len(nodes),
                "hh_consensus_edge_count": hh_count,
                "hp_secondary_edge_count": hp_count,
                "edge_keys": ";".join(sorted(comp)),
                "node_ids": ";".join(nodes),
            })
        return rows

    component_rows = []
    component_rows.extend(comp_summary_rows("HH_CONSENSUS", hh_comps))
    component_rows.extend(comp_summary_rows("HP_SECONDARY", hp_comps))
    component_rows.extend(comp_summary_rows("HH_PLUS_HP", combined_comps))

    # Adjacency summary
    hp_adjacent_to_hh = [e for e in hp_edges if edge_adj.get(e, set()) & hh_edges]
    hh_adjacent_to_hp = [e for e in hh_edges if edge_adj.get(e, set()) & hp_edges]
    shell_counts = Counter(shell_to_hh.get(e, -1) for e in hp_edges)
    role_summary_rows = [
        {
            "metric_name": "hh_consensus_edge_count",
            "metric_value": len(hh_edges),
            "edge_keys": ";".join(sorted(hh_edges)),
            "note": "Number of H,H all-representation consensus carriers.",
        },
        {
            "metric_name": "hp_secondary_edge_count",
            "metric_value": len(hp_edges),
            "edge_keys": ";".join(sorted(hp_edges)),
            "note": "Number of H,P topology/distance secondary carriers.",
        },
        {
            "metric_name": "hp_edges_adjacent_to_hh_count",
            "metric_value": len(hp_adjacent_to_hh),
            "edge_keys": ";".join(sorted(hp_adjacent_to_hh)),
            "note": "H,P secondary edges sharing a node with an H,H consensus edge.",
        },
        {
            "metric_name": "hp_edges_adjacent_to_hh_fraction",
            "metric_value": len(hp_adjacent_to_hh) / len(hp_edges) if hp_edges else 0,
            "edge_keys": "",
            "note": "Fraction of H,P secondary edges adjacent to H,H consensus.",
        },
        {
            "metric_name": "hh_edges_with_adjacent_hp_count",
            "metric_value": len(hh_adjacent_to_hp),
            "edge_keys": ";".join(sorted(hh_adjacent_to_hp)),
            "note": "H,H consensus edges with at least one adjacent H,P secondary edge.",
        },
        {
            "metric_name": "hh_edges_with_adjacent_hp_fraction",
            "metric_value": len(hh_adjacent_to_hp) / len(hh_edges) if hh_edges else 0,
            "edge_keys": "",
            "note": "Fraction of H,H consensus edges adjacent to H,P secondary.",
        },
    ]
    for shell, count in sorted(shell_counts.items()):
        role_summary_rows.append({
            "metric_name": f"hp_secondary_shell_distance_{shell}_count",
            "metric_value": count,
            "edge_keys": ";".join(sorted(e for e in hp_edges if shell_to_hh.get(e, -1) == shell)),
            "note": "H,P secondary edge count by shell distance to nearest H,H consensus edge.",
        })

    # Visualization edges
    viz_rows = []
    for r in edge_rows:
        viz_rows.append({
            "source": r["source"],
            "target": r["target"],
            "edge_key": r["edge_key"],
            "edge_type": r["edge_type"],
            "shared_face_types": r["shared_face_types"],
            "role_group": r["role_group"],
            "consensus_label": r["consensus_label"],
            "shell_distance_to_hh_consensus": r["shell_distance_to_hh_consensus"],
            "visual_weight": 3 if r["role_group"] == "HH_CONSENSUS" else 2 if r["role_group"] == "HP_SECONDARY" else 1,
        })

    out = cfg["outputs"]
    write_csv(outdir / out["carrier_edge_geometry_csv"], edge_rows, [
        "edge_key", "source", "target", "edge_type", "shared_face_types", "faces",
        "consensus_label", "role_group", "is_hh_consensus", "is_hp_secondary",
        "is_role_carrier", "shell_distance_to_hh_consensus",
        "adjacent_hh_consensus_count", "adjacent_hp_secondary_count",
        "adjacent_hh_consensus_edges", "adjacent_hp_secondary_edges",
        "bond_class_weighted_rank", "topology_only_equal_weight_rank",
        "graph_distance_similarity_d3_rank",
    ])
    write_csv(outdir / out["carrier_node_geometry_csv"], node_rows, [
        "node_id", "degree", "incident_hh_consensus_count", "incident_hp_secondary_count",
        "incident_total_carrier_count", "carrier_junction_label",
        "incident_hh_consensus_edges", "incident_hp_secondary_edges", "incident_carrier_edges",
    ])
    write_csv(outdir / out["carrier_face_geometry_csv"], face_rows, [
        "face_id", "face_type", "incident_edge_count", "incident_hh_consensus_edges",
        "incident_hp_secondary_edges", "incident_total_carrier_edges",
        "face_carrier_role_label", "hh_consensus_edge_keys",
        "hp_secondary_edge_keys", "carrier_edge_keys",
    ])
    write_csv(outdir / out["carrier_component_summary_csv"], component_rows, [
        "carrier_group", "component_id", "component_edge_count", "component_node_count",
        "hh_consensus_edge_count", "hp_secondary_edge_count", "edge_keys", "node_ids",
    ])
    write_csv(outdir / out["carrier_role_adjacency_summary_csv"], role_summary_rows, [
        "metric_name", "metric_value", "edge_keys", "note",
    ])
    write_csv(outdir / out["visualization_edges_csv"], viz_rows, [
        "source", "target", "edge_key", "edge_type", "shared_face_types",
        "role_group", "consensus_label", "shell_distance_to_hh_consensus", "visual_weight",
    ])

    node_label_counts = Counter(r["carrier_junction_label"] for r in node_rows)
    face_label_counts = Counter(r["face_carrier_role_label"] for r in face_rows)
    component_counts = Counter(r["carrier_group"] for r in component_rows)
    largest_combined = max((r for r in component_rows if r["carrier_group"] == "HH_PLUS_HP"), key=lambda r: as_int(r["component_edge_count"]), default={})

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu02c_run_id": fu_manifest.get("run_id", ""),
        "fu02c_warning_count": len(fu_warnings),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "hh_consensus_edge_count": len(hh_edges),
        "hp_secondary_edge_count": len(hp_edges),
        "role_carrier_edge_count": len(carrier_edges),
        "node_label_counts": dict(sorted(node_label_counts.items())),
        "face_label_counts": dict(sorted(face_label_counts.items())),
        "component_group_row_counts": dict(sorted(component_counts.items())),
        "largest_combined_component_edge_count": as_int(largest_combined.get("component_edge_count", 0)),
        "largest_combined_component_node_count": as_int(largest_combined.get("component_node_count", 0)),
        "hp_edges_adjacent_to_hh_count": len(hp_adjacent_to_hh),
        "hp_edges_adjacent_to_hh_fraction": len(hp_adjacent_to_hh) / len(hp_edges) if hp_edges else 0,
        "hh_edges_with_adjacent_hp_count": len(hh_adjacent_to_hp),
        "hh_edges_with_adjacent_hp_fraction": len(hh_adjacent_to_hp) / len(hh_edges) if hh_edges else 0,
        "hp_shell_distance_to_hh_counts": dict(sorted(shell_counts.items())),
        "row_counts": {
            "carrier_edge_geometry": len(edge_rows),
            "carrier_node_geometry": len(node_rows),
            "carrier_face_geometry": len(face_rows),
            "carrier_component_summary": len(component_rows),
            "carrier_role_adjacency_summary": len(role_summary_rows),
            "visualization_edges": len(viz_rows),
            "warnings": len(warnings),
        },
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
    parser = argparse.ArgumentParser(description="Run BMS-FU02d carrier role geometry and patch distribution analysis.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
