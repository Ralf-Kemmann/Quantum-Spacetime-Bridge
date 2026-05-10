#!/usr/bin/env python3
"""
BMS-FU02g2 — Carrier Diagnostic Transfer to Geometry-Class Controls

Purpose:
  Transfer a transparent cell-level carrier proxy diagnostic to C60, graphene,
  and repaired nanotube graph/cell controls.

Scope:
  Diagnostic transfer only. No chemistry, no spacetime claim, no formal p-values.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


CELL_DIAG_FIELDS = [
    "structure_id", "structure_class", "geometry_class", "cell_id", "cell_type",
    "boundary_cell", "periodic_cell", "cell_adjacency_degree", "mean_node_degree",
    "low_degree_node_fraction", "two_cell_edge_fraction", "carrier_score",
    "carrier_rank", "is_carrier_cell", "cell_role_label", "carrier_component_id",
    "distance_to_carrier_core", "distance_to_boundary", "fu02f1_reference_role",
]
SUMMARY_FIELDS = [
    "structure_id", "structure_class", "geometry_class", "cell_count",
    "carrier_cell_count", "carrier_cell_fraction", "carrier_cell_component_count",
    "largest_carrier_cell_component_count", "compactness_proxy",
    "boundary_cell_count", "boundary_cell_fraction", "carrier_boundary_cell_count",
    "carrier_boundary_overlap_fraction", "carrier_core_cell_count",
    "carrier_adjacent_cell_count", "noncarrier_cell_count", "cell_adjacency_edge_count",
    "carrier_internal_adjacency_count", "carrier_boundary_adjacency_count",
    "carrier_external_neighbor_count", "max_distance_to_carrier_core",
    "mean_distance_to_carrier_core", "carrier_min_distance_to_boundary",
    "carrier_mean_distance_to_boundary", "boundary_dependence_proxy",
    "adjacent_shell_ratio", "fu02f1_reference_overlap_count",
    "fu02f1_reference_overlap_fraction", "diagnostic_label",
]
COMPARISON_FIELDS = [
    "structure_id", "geometry_class", "carrier_cell_fraction", "compactness_proxy",
    "boundary_dependence_proxy", "adjacent_shell_ratio",
    "largest_carrier_component_fraction_of_all_cells", "diagnostic_label",
]


def read_yaml(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def parse_list(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    # Current project files use semicolons for node/edge lists.
    for ch in "[]{}()'\"":
        s = s.replace(ch, "")
    out: List[str] = []
    for part in s.replace(",", ";").replace("|", ";").split(";"):
        p = part.strip()
        if p:
            out.append(p)
    return out


def truthy(v: Any) -> bool:
    return str(v).strip().lower() in {"1", "true", "yes", "y"}


def to_float(v: Any, default: float = 0.0) -> float:
    try:
        if v == "" or v is None:
            return default
        return float(v)
    except Exception:
        return default


def normalize(values: Dict[str, float]) -> Dict[str, float]:
    if not values:
        return {}
    lo = min(values.values())
    hi = max(values.values())
    if math.isclose(lo, hi):
        return {k: 0.0 for k in values}
    return {k: (v - lo) / (hi - lo) for k, v in values.items()}


def build_cell_graph(edges: List[Dict[str, str]]) -> Tuple[Dict[str, Set[str]], Dict[str, List[str]]]:
    adj: Dict[str, Set[str]] = defaultdict(set)
    incident_edge_ids: Dict[str, List[str]] = defaultdict(list)
    for e in edges:
        left = e.get("cell_left", "")
        right = e.get("cell_right", "")
        eid = e.get("edge_id", "")
        if left:
            incident_edge_ids[left].append(eid)
        if right:
            incident_edge_ids[right].append(eid)
        if left and right and left != right:
            adj[left].add(right)
            adj[right].add(left)
    return adj, incident_edge_ids


def components(nodes: Set[str], adj: Dict[str, Set[str]]) -> List[Set[str]]:
    seen: Set[str] = set()
    comps: List[Set[str]] = []
    for n in sorted(nodes):
        if n in seen:
            continue
        q = deque([n])
        seen.add(n)
        comp = {n}
        while q:
            u = q.popleft()
            for v in adj.get(u, set()):
                if v in nodes and v not in seen:
                    seen.add(v)
                    comp.add(v)
                    q.append(v)
        comps.append(comp)
    return comps


def distances_from_sources(all_nodes: Set[str], sources: Set[str], adj: Dict[str, Set[str]]) -> Dict[str, int | None]:
    dist: Dict[str, int | None] = {n: None for n in all_nodes}
    q = deque()
    for s in sources:
        if s in all_nodes:
            dist[s] = 0
            q.append(s)
    while q:
        u = q.popleft()
        for v in adj.get(u, set()):
            if v in all_nodes and dist[v] is None:
                dist[v] = int(dist[u]) + 1
                q.append(v)
    return dist


def load_c60_reference_roles(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    rows = read_csv(path)
    roles: Dict[str, str] = {}
    for r in rows:
        cid = r.get("face_id") or r.get("cell_id")
        if not cid:
            continue
        roles[cid] = r.get("layout_role_shell") or r.get("face_carrier_role_label") or ""
    return roles


def diagnostic_for_structure(root: Path, scfg: Dict[str, Any], diagnostic_cfg: Dict[str, Any], c60_ref_roles: Dict[str, str], warnings: List[Dict[str, str]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    sid = scfg["structure_id"]
    nodes = read_csv(root / scfg["nodes_csv"])
    edges = read_csv(root / scfg["edges_csv"])
    cells = read_csv(root / scfg["cells_csv"])

    node_degree = {n["node_id"]: int(float(n.get("degree", 0) or 0)) for n in nodes}
    cell_adj, incident_edge_ids = build_cell_graph(edges)
    all_cells = {c["cell_id"] for c in cells}

    # Ensure isolated cells exist in adjacency map.
    for cid in all_cells:
        cell_adj.setdefault(cid, set())

    edge_by_id = {e["edge_id"]: e for e in edges}
    edge_cell_count = {e["edge_id"]: int(float(e.get("cell_count", 0) or 0)) for e in edges}

    raw_adj_degree: Dict[str, float] = {}
    raw_mean_node_degree: Dict[str, float] = {}
    raw_two_cell_fraction: Dict[str, float] = {}
    raw_low_degree_fraction: Dict[str, float] = {}

    for c in cells:
        cid = c["cell_id"]
        ns = parse_list(c.get("node_ids", ""))
        degs = [node_degree.get(n, 0) for n in ns]
        raw_adj_degree[cid] = float(len(cell_adj.get(cid, set())))
        raw_mean_node_degree[cid] = sum(degs) / len(degs) if degs else 0.0
        raw_low_degree_fraction[cid] = sum(1 for d in degs if d < 3) / len(degs) if degs else 0.0
        eids = parse_list(c.get("edge_ids", ""))
        raw_two_cell_fraction[cid] = sum(1 for eid in eids if edge_cell_count.get(eid, 0) >= 2) / len(eids) if eids else 0.0

    n_adj = normalize(raw_adj_degree)
    n_node = normalize(raw_mean_node_degree)
    n_two = normalize(raw_two_cell_fraction)
    # low-degree fraction is already [0,1].
    weights = diagnostic_cfg.get("score_weights", {})
    scores: Dict[str, float] = {}
    for c in cells:
        cid = c["cell_id"]
        boundary = 1.0 if truthy(c.get("boundary_cell", 0)) else 0.0
        scores[cid] = (
            float(weights.get("cell_adjacency_degree", 1.0)) * n_adj.get(cid, 0.0)
            + float(weights.get("mean_node_degree", 0.75)) * n_node.get(cid, 0.0)
            + float(weights.get("two_cell_edge_fraction", 0.5)) * n_two.get(cid, 0.0)
            - float(weights.get("boundary_cell_penalty", 0.75)) * boundary
            - float(weights.get("low_degree_node_fraction_penalty", 0.5)) * raw_low_degree_fraction.get(cid, 0.0)
        )

    top_fraction = float(diagnostic_cfg.get("top_fraction", 0.30))
    min_carriers = int(diagnostic_cfg.get("minimum_carrier_cells", 5))
    k = max(min_carriers, int(round(top_fraction * len(cells))))
    k = min(k, len(cells))
    ranked = sorted(scores, key=lambda cid: (-scores[cid], cid))
    carrier_set = set(ranked[:k])
    rank_index = {cid: i + 1 for i, cid in enumerate(ranked)}

    carrier_adjacent = set()
    for cid in carrier_set:
        carrier_adjacent.update(cell_adj.get(cid, set()))
    carrier_adjacent -= carrier_set

    carrier_components = components(carrier_set, cell_adj)
    comp_id: Dict[str, int] = {}
    for i, comp in enumerate(carrier_components, start=1):
        for cid in comp:
            comp_id[cid] = i

    boundary_cells = {c["cell_id"] for c in cells if truthy(c.get("boundary_cell", 0))}
    carrier_core = carrier_set - boundary_cells
    core_sources = carrier_core if carrier_core else carrier_set
    dist_to_core = distances_from_sources(all_cells, core_sources, cell_adj)
    dist_to_boundary = distances_from_sources(all_cells, boundary_cells, cell_adj) if boundary_cells else {cid: None for cid in all_cells}

    cell_rows: List[Dict[str, Any]] = []
    ref_overlap = 0
    for c in cells:
        cid = c["cell_id"]
        is_carrier = cid in carrier_set
        if is_carrier and cid in boundary_cells:
            label = "carrier_boundary_cell"
        elif is_carrier:
            label = "carrier_core_cell"
        elif cid in carrier_adjacent:
            label = "carrier_adjacent_cell"
        else:
            label = "noncarrier_cell"

        ref_role = c60_ref_roles.get(cid, "") if sid == "c60_reference" else ""
        if is_carrier and ref_role in {"mixed_seam_boundary_face", "hp_boundary_face"}:
            ref_overlap += 1

        cell_rows.append({
            "structure_id": sid,
            "structure_class": scfg.get("structure_class", ""),
            "geometry_class": scfg.get("geometry_class", ""),
            "cell_id": cid,
            "cell_type": c.get("cell_type", ""),
            "boundary_cell": 1 if cid in boundary_cells else 0,
            "periodic_cell": c.get("periodic_cell", ""),
            "cell_adjacency_degree": raw_adj_degree.get(cid, 0.0),
            "mean_node_degree": raw_mean_node_degree.get(cid, 0.0),
            "low_degree_node_fraction": raw_low_degree_fraction.get(cid, 0.0),
            "two_cell_edge_fraction": raw_two_cell_fraction.get(cid, 0.0),
            "carrier_score": scores.get(cid, 0.0),
            "carrier_rank": rank_index.get(cid, ""),
            "is_carrier_cell": 1 if is_carrier else 0,
            "cell_role_label": label,
            "carrier_component_id": comp_id.get(cid, ""),
            "distance_to_carrier_core": "" if dist_to_core.get(cid) is None else dist_to_core[cid],
            "distance_to_boundary": "" if dist_to_boundary.get(cid) is None else dist_to_boundary[cid],
            "fu02f1_reference_role": ref_role,
        })

    carrier_internal_adjacencies = 0
    carrier_boundary_adjacencies = 0
    adjacency_edges_count = 0
    seen_pairs = set()
    for a in all_cells:
        for b in cell_adj.get(a, set()):
            pair = tuple(sorted((a, b)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            adjacency_edges_count += 1
            if a in carrier_set and b in carrier_set:
                carrier_internal_adjacencies += 1
            elif (a in carrier_set) != (b in carrier_set):
                carrier_boundary_adjacencies += 1

    external_neighbors = set()
    for cid in carrier_set:
        external_neighbors.update(cell_adj.get(cid, set()) - carrier_set)

    finite_dists_core = [d for d in dist_to_core.values() if d is not None]
    carrier_boundary_distances = [dist_to_boundary[cid] for cid in carrier_set if dist_to_boundary.get(cid) is not None]

    carrier_boundary_count = len(carrier_set & boundary_cells)
    largest_comp = max((len(c) for c in carrier_components), default=0)
    compactness = largest_comp / len(carrier_set) if carrier_set else 0.0
    boundary_fraction = len(boundary_cells) / len(cells) if cells else 0.0
    carrier_fraction = len(carrier_set) / len(cells) if cells else 0.0
    boundary_dependence = carrier_boundary_count / len(carrier_set) if carrier_set else 0.0
    adjacent_shell_ratio = len(carrier_adjacent) / len(carrier_set) if carrier_set else 0.0

    if sid == "c60_reference" and c60_ref_roles:
        ref_fraction = ref_overlap / len(carrier_set) if carrier_set else 0.0
    else:
        ref_fraction = ""

    if boundary_dependence >= 0.5:
        label = "boundary_driven_candidate"
    elif compactness >= 0.9 and len(carrier_components) == 1:
        label = "compact_connected_carrier_candidate"
    elif len(carrier_components) > 1:
        label = "multi_component_carrier_candidate"
    else:
        label = "diffuse_or_mixed_carrier_candidate"

    summary = {
        "structure_id": sid,
        "structure_class": scfg.get("structure_class", ""),
        "geometry_class": scfg.get("geometry_class", ""),
        "cell_count": len(cells),
        "carrier_cell_count": len(carrier_set),
        "carrier_cell_fraction": carrier_fraction,
        "carrier_cell_component_count": len(carrier_components),
        "largest_carrier_cell_component_count": largest_comp,
        "compactness_proxy": compactness,
        "boundary_cell_count": len(boundary_cells),
        "boundary_cell_fraction": boundary_fraction,
        "carrier_boundary_cell_count": carrier_boundary_count,
        "carrier_boundary_overlap_fraction": boundary_dependence,
        "carrier_core_cell_count": len(carrier_set - boundary_cells),
        "carrier_adjacent_cell_count": len(carrier_adjacent),
        "noncarrier_cell_count": len(all_cells - carrier_set - carrier_adjacent),
        "cell_adjacency_edge_count": adjacency_edges_count,
        "carrier_internal_adjacency_count": carrier_internal_adjacencies,
        "carrier_boundary_adjacency_count": carrier_boundary_adjacencies,
        "carrier_external_neighbor_count": len(external_neighbors),
        "max_distance_to_carrier_core": max(finite_dists_core) if finite_dists_core else "",
        "mean_distance_to_carrier_core": sum(finite_dists_core) / len(finite_dists_core) if finite_dists_core else "",
        "carrier_min_distance_to_boundary": min(carrier_boundary_distances) if carrier_boundary_distances else "",
        "carrier_mean_distance_to_boundary": sum(carrier_boundary_distances) / len(carrier_boundary_distances) if carrier_boundary_distances else "",
        "boundary_dependence_proxy": boundary_dependence,
        "adjacent_shell_ratio": adjacent_shell_ratio,
        "fu02f1_reference_overlap_count": ref_overlap if sid == "c60_reference" and c60_ref_roles else "",
        "fu02f1_reference_overlap_fraction": ref_fraction,
        "diagnostic_label": label,
    }

    comparison = {
        "structure_id": sid,
        "geometry_class": scfg.get("geometry_class", ""),
        "carrier_cell_fraction": carrier_fraction,
        "compactness_proxy": compactness,
        "boundary_dependence_proxy": boundary_dependence,
        "adjacent_shell_ratio": adjacent_shell_ratio,
        "largest_carrier_component_fraction_of_all_cells": largest_comp / len(cells) if cells else 0.0,
        "diagnostic_label": label,
    }

    return cell_rows, summary, comparison


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    out_dir = root / cfg["run"]["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    ref_cfg = cfg.get("optional_reference", {})
    c60_ref_roles: Dict[str, str] = {}
    if ref_cfg.get("use_if_present", True):
        ref_path = root / ref_cfg.get("c60_fu02f1_face_layout_csv", "")
        if ref_path.exists():
            c60_ref_roles = load_c60_reference_roles(ref_path)
        else:
            warnings.append({"severity": "info", "message": f"C60 FU02f1 reference layout not found: {ref_path}; overlap output will be empty."})

    all_cells: List[Dict[str, Any]] = []
    summaries: List[Dict[str, Any]] = []
    comparisons: List[Dict[str, Any]] = []

    for key, scfg in cfg.get("structures", {}).items():
        if not scfg.get("enabled", False):
            continue
        try:
            cell_rows, summary, comparison = diagnostic_for_structure(root, scfg, cfg.get("diagnostic", {}), c60_ref_roles, warnings)
            all_cells.extend(cell_rows)
            summaries.append(summary)
            comparisons.append(comparison)
        except Exception as exc:
            warnings.append({"severity": "error", "message": f"Failed structure {key}: {exc}"})

    write_csv(out_dir / "bms_fu02g2_cell_diagnostics.csv", all_cells, CELL_DIAG_FIELDS)
    write_csv(out_dir / "bms_fu02g2_structure_summary.csv", summaries, SUMMARY_FIELDS)
    write_csv(out_dir / "bms_fu02g2_geometry_class_comparison.csv", comparisons, COMPARISON_FIELDS)

    run_manifest = {
        "run_id": cfg["run"]["run_id"],
        "structure_count": len(summaries),
        "structure_ids": [r["structure_id"] for r in summaries],
        "output_dir": str(out_dir),
        "cell_diagnostics_csv": "bms_fu02g2_cell_diagnostics.csv",
        "structure_summary_csv": "bms_fu02g2_structure_summary.csv",
        "geometry_class_comparison_csv": "bms_fu02g2_geometry_class_comparison.csv",
        "c60_fu02f1_reference_loaded": bool(c60_ref_roles),
        "warnings_count": len(warnings),
        "scope_note": "FU02g2 transfers cell-level carrier proxy diagnostics only; no final real-structure memory claim is made.",
    }
    write_json(out_dir / "bms_fu02g2_run_manifest.json", run_manifest)
    write_json(out_dir / "bms_fu02g2_warnings.json", warnings)
    (out_dir / "bms_fu02g2_config_resolved.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    print(json.dumps(run_manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02g2 carrier diagnostic transfer.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
