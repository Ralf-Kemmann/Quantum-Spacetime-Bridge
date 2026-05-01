#!/usr/bin/env python3
"""
BMS-FU01c — C60 Motif-Preserving Null and Topology-Only Extension Runner

Main question:
  Bleibt das C60-Signal, wenn die 6:6 / 5:6-Gewichtsinformation entfernt wird?

This runner evaluates C60 structure diagnostics across representation variants:
  1. bond_class_weighted
  2. topology_only_equal_weight
  3. graph_distance_similarity_d3

Interpretation boundary:
  This is a controlled graph-structure diagnostic. It does not perform quantum
  chemistry, does not recover a physical metric, and does not prove emergent
  spacetime.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


Edge = Tuple[str, str]

BASE_EDGE_TYPE_WEIGHTS = {
    "6_6": 1.00,
    "5_6": 0.85,
    "unknown": 0.0,
}


def edge_key(a: str, b: str) -> Edge:
    return (a, b) if a <= b else (b, a)


def as_float(x: Any, default: float = float("nan")) -> float:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def base_edge_weight(edge_type: str) -> float:
    return BASE_EDGE_TYPE_WEIGHTS.get(str(edge_type), 0.0)


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def parse_semicolon(value: Any) -> List[str]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    return [x for x in s.split(";") if x]


def load_inputs(cfg: Dict[str, Any], root: Path, warnings: List[Dict[str, str]]):
    nodes_path = root / cfg["inputs"]["nodes_csv"]
    edges_path = root / cfg["inputs"]["edges_csv"]
    faces_path = root / cfg["inputs"]["faces_csv"]
    manifest_path = root / cfg["inputs"]["graph_manifest_json"]

    for p in [nodes_path, edges_path, faces_path, manifest_path]:
        if not p.exists():
            raise SystemExit(f"Missing required input: {p}")

    nodes = read_csv(nodes_path)
    faces = read_csv(faces_path)
    edge_rows_in = read_csv(edges_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if not manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "Input C60 manifest does not report c60_valid=true."})

    if manifest.get("warnings", []) not in ([], None):
        warnings.append({"severity": "warning", "message": "Input C60 builder manifest contains warnings."})

    edges: Dict[Edge, Dict[str, Any]] = {}
    for r in edge_rows_in:
        a, b = r["source"], r["target"]
        e = edge_key(a, b)
        et = r.get("edge_type", "unknown")
        w = as_float(r.get("weight", ""), base_edge_weight(et))
        dist_default = (1.0 / w - 1.0) if w > 0 else float("inf")
        edges[e] = {
            "edge_id": r.get("edge_id", ""),
            "source": e[0],
            "target": e[1],
            "edge_type": et,
            "source_degree": r.get("source_degree", ""),
            "target_degree": r.get("target_degree", ""),
            "shared_face_count": r.get("shared_face_count", ""),
            "shared_faces": r.get("shared_faces", ""),
            "shared_face_types": r.get("shared_face_types", ""),
            "weight": w,
            "distance": as_float(r.get("distance", ""), dist_default),
            "graph_distance": 1,
            "is_bond_edge": True,
            "comment": r.get("comment", ""),
        }

    return nodes, edges, faces, manifest


def validate_loaded_graph(nodes: List[Dict[str, str]], edges: Dict[Edge, Dict[str, Any]], faces: List[Dict[str, str]]) -> Dict[str, Any]:
    degree = Counter()
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    face_types = Counter(f.get("face_type", "") for f in faces)
    edge_types = Counter(str(v.get("edge_type", "")) for v in edges.values())
    node_ids = {n["node_id"] for n in nodes}

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "face_count": len(faces),
        "pentagon_count": face_types.get("pentagon", 0),
        "hexagon_count": face_types.get("hexagon", 0),
        "degree_counts": dict(sorted(Counter(degree[n] for n in node_ids).items())),
        "edge_type_counts": dict(sorted(edge_types.items())),
        "all_node_degrees_3": all(degree[n] == 3 for n in node_ids),
        "expected_counts_ok": (
            len(nodes) == 60
            and len(edges) == 90
            and len(faces) == 32
            and face_types.get("pentagon", 0) == 12
            and face_types.get("hexagon", 0) == 20
            and edge_types.get("5_6", 0) == 60
            and edge_types.get("6_6", 0) == 30
        ),
    }


def build_adjacency(edges: Dict[Edge, Dict[str, Any]]) -> Dict[str, Set[str]]:
    adj: Dict[str, Set[str]] = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def all_pairs_shortest_paths(node_ids: List[str], bond_edges: Dict[Edge, Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    adj = build_adjacency(bond_edges)
    dist_all: Dict[str, Dict[str, int]] = {}
    for start in node_ids:
        dist = {start: 0}
        q = deque([start])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    q.append(y)
        dist_all[start] = dist
    return dist_all


def representation_weight(edge_type: str, rep: Dict[str, Any], graph_distance: int = 1) -> float:
    rep_id = rep["representation_id"]
    if rep_id == "bond_class_weighted":
        return base_edge_weight(edge_type)
    if rep_id == "topology_only_equal_weight":
        return 1.0
    if rep_id.startswith("graph_distance_similarity"):
        return 1.0 / (1.0 + float(graph_distance))
    return base_edge_weight(edge_type)


def build_representation_edges(
    rep: Dict[str, Any],
    node_ids: List[str],
    bond_edges: Dict[Edge, Dict[str, Any]],
    shortest_paths: Dict[str, Dict[str, int]],
) -> Dict[Edge, Dict[str, Any]]:
    edge_mode = rep["edge_mode"]
    rep_edges: Dict[Edge, Dict[str, Any]] = {}

    if edge_mode == "bond_edges_only":
        for e, info in bond_edges.items():
            et = str(info.get("edge_type", "unknown"))
            gd = 1
            w = representation_weight(et, rep, gd)
            row = dict(info)
            row.update({
                "weight": w,
                "distance": (1.0 / w - 1.0) if w > 0 else "",
                "graph_distance": gd,
                "is_bond_edge": True,
                "comment": f'{rep["representation_id"]} representation edge',
            })
            rep_edges[e] = row
        return rep_edges

    if edge_mode == "graph_distance_pairs":
        max_d = rep.get("max_graph_distance", None)
        max_d = int(max_d) if max_d is not None else None
        idx = 0
        for i, a in enumerate(node_ids):
            for b in node_ids[i + 1:]:
                gd = shortest_paths[a].get(b)
                if gd is None:
                    continue
                if max_d is not None and gd > max_d:
                    continue
                e = edge_key(a, b)
                base = bond_edges.get(e, {})
                et = str(base.get("edge_type", "nonbond"))
                is_bond = e in bond_edges
                idx += 1
                w = representation_weight(et, rep, gd)
                rep_edges[e] = {
                    "edge_id": base.get("edge_id", f"pair_{idx:04d}"),
                    "source": e[0],
                    "target": e[1],
                    "edge_type": et if is_bond else "nonbond",
                    "source_degree": base.get("source_degree", ""),
                    "target_degree": base.get("target_degree", ""),
                    "shared_face_count": base.get("shared_face_count", ""),
                    "shared_faces": base.get("shared_faces", ""),
                    "shared_face_types": base.get("shared_face_types", ""),
                    "weight": w,
                    "distance": (1.0 / w - 1.0) if w > 0 else "",
                    "graph_distance": gd,
                    "is_bond_edge": is_bond,
                    "comment": f'{rep["representation_id"]} representation edge',
                }
        return rep_edges

    raise SystemExit(f"Unsupported representation edge_mode: {edge_mode}")


def sorted_edges_by_type(edges: Dict[Edge, Dict[str, Any]], edge_type: str) -> List[Edge]:
    return sorted([e for e, info in edges.items() if info.get("edge_type") == edge_type])


def evenly_spaced(items: List[Edge], count: int) -> List[Edge]:
    if count <= 0:
        return []
    if count >= len(items):
        return list(items)
    if count == 1:
        return [items[0]]
    n = len(items)
    indices = sorted({round(i * (n - 1) / (count - 1)) for i in range(count)})
    if len(indices) < count:
        for idx in range(n):
            if idx not in indices:
                indices.append(idx)
                if len(indices) == count:
                    break
        indices = sorted(indices)
    return [items[i] for i in indices[:count]]


def connected_component_count_for_edges(node_ids: List[str], selected: Set[Edge]) -> int:
    adj: Dict[str, Set[str]] = defaultdict(set)
    for a, b in selected:
        adj[a].add(b)
        adj[b].add(a)

    if not node_ids:
        return 0

    seen = set()
    count = 0
    for n in node_ids:
        if n in seen:
            continue
        count += 1
        q = deque([n])
        seen.add(n)
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    q.append(y)
    return count


def core_face_span(core_edges: Set[Edge], edges: Dict[Edge, Dict[str, Any]]) -> Tuple[Set[str], Counter]:
    faces = set()
    face_type_counts = Counter()
    for e in core_edges:
        shared_faces = parse_semicolon(edges[e].get("shared_faces", ""))
        shared_types = str(edges[e].get("shared_face_types", "")).split(",")
        for fid in shared_faces:
            faces.add(fid)
        for ft in shared_types:
            ft = ft.strip()
            if ft:
                face_type_counts[ft] += 1
    return faces, face_type_counts


def build_core_variants(
    bond_edges: Dict[Edge, Dict[str, Any]],
    cfg: Dict[str, Any],
    warnings: List[Dict[str, str]],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    variant_rows: List[Dict[str, Any]] = []
    ref_edge_rows: List[Dict[str, Any]] = []

    for variant in cfg.get("core_variants", []):
        core_id = variant["core_variant_id"]
        mode = variant["mode"]
        etype = variant["edge_type"]
        count = int(variant["edge_count"])
        candidates = sorted_edges_by_type(bond_edges, etype)

        if mode == "first_sorted_edge_type":
            selected = candidates[:count]
            selection_rule = f"first_{count}_sorted_{etype}_edges"
        elif mode == "evenly_spaced_edge_type":
            selected = evenly_spaced(candidates, count)
            selection_rule = f"evenly_spaced_{count}_of_{len(candidates)}_{etype}_edges"
        else:
            warnings.append({"severity": "warning", "message": f"Unsupported core mode {mode} for {core_id}; skipped."})
            selected = []
            selection_rule = f"unsupported_mode_{mode}"

        if len(selected) != count:
            warnings.append({
                "severity": "warning",
                "message": f"Core {core_id} selected {len(selected)} edges, expected {count}.",
            })

        core_set = set(selected)
        core_nodes = sorted({x for e in core_set for x in e})
        face_ids, face_type_counts = core_face_span(core_set, bond_edges)
        et_counts = Counter(str(bond_edges[e].get("edge_type", "")) for e in core_set)
        cc = connected_component_count_for_edges(core_nodes, core_set) if core_nodes else 0

        variant_rows.append({
            "core_variant_id": core_id,
            "core_variant_mode": mode,
            "description": variant.get("description", ""),
            "selection_rule": selection_rule,
            "edge_count": len(core_set),
            "node_count": len(core_nodes),
            "edge_type_counts": json.dumps(dict(sorted(et_counts.items())), sort_keys=True),
            "face_span_count": len(face_ids),
            "pentagon_face_span_count": sum(1 for f in face_ids if f.startswith("P_")),
            "hexagon_face_span_count": sum(1 for f in face_ids if f.startswith("H_")),
            "face_type_incidence_counts": json.dumps(dict(sorted(face_type_counts.items())), sort_keys=True),
            "connected_component_count": cc,
        })

        for rank, e in enumerate(selected, start=1):
            info = bond_edges[e]
            ref_edge_rows.append({
                "core_variant_id": core_id,
                "core_variant_mode": mode,
                "core_edge_rank": rank,
                "source": e[0],
                "target": e[1],
                "edge_type": info.get("edge_type", ""),
                "weight": as_float(info.get("weight", ""), base_edge_weight(info.get("edge_type", ""))),
                "shared_faces": info.get("shared_faces", ""),
                "shared_face_types": info.get("shared_face_types", ""),
                "reference_core_rule": selection_rule,
            })

    return variant_rows, ref_edge_rows


def weights_dict(edges: Dict[Edge, Dict[str, Any]]) -> Dict[Edge, float]:
    return {e: as_float(info.get("weight", ""), 0.0) for e, info in edges.items()}


def top_edges(edges: Dict[Edge, Dict[str, Any]], n: int) -> Set[Edge]:
    return {
        e for e, _ in sorted(weights_dict(edges).items(), key=lambda kv: (abs(kv[1]), kv[0]), reverse=True)[:n]
    }


def threshold_edges(edges: Dict[Edge, Dict[str, Any]], t: float) -> Set[Edge]:
    return {e for e, w in weights_dict(edges).items() if abs(w) >= t}


def mutual_knn_edges(edges: Dict[Edge, Dict[str, Any]], node_ids: List[str], k: int) -> Set[Edge]:
    w = weights_dict(edges)
    neigh = {n: [] for n in node_ids}
    for (a, b), wt in w.items():
        if a in neigh and b in neigh:
            neigh[a].append((b, wt))
            neigh[b].append((a, wt))

    topn = {}
    for n, vals in neigh.items():
        topn[n] = {x for x, _ in sorted(vals, key=lambda t: (abs(t[1]), t[0]), reverse=True)[:k]}

    return {e for e in w if e[1] in topn.get(e[0], set()) and e[0] in topn.get(e[1], set())}


def mst_edges(edges: Dict[Edge, Dict[str, Any]], node_ids: List[str]) -> Set[Edge]:
    parent = {n: n for n in node_ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True

    out: Set[Edge] = set()
    for (a, b), wt in sorted(weights_dict(edges).items(), key=lambda kv: (abs(kv[1]), kv[0]), reverse=True):
        if union(a, b):
            out.add((a, b))
        if len(out) >= len(node_ids) - 1:
            break
    return out


def graph_distance_shell_edges(rep_edges: Dict[Edge, Dict[str, Any]], bond_edges: Dict[Edge, Dict[str, Any]], node_ids: List[str], shell_depth: int) -> Set[Edge]:
    anchor = "c60_001" if "c60_001" in node_ids else sorted(node_ids)[0]
    adj = build_adjacency(bond_edges)
    dist = {anchor: 0}
    q = deque([anchor])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)

    shell_nodes = {n for n, d in dist.items() if d <= shell_depth}
    return {e for e in rep_edges if e[0] in shell_nodes or e[1] in shell_nodes}


def construct_variants(rep_edges: Dict[Edge, Dict[str, Any]], bond_edges: Dict[Edge, Dict[str, Any]], node_ids: List[str], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    fams = cfg["construction_families"]
    variants = []

    if fams["top_strength"]["enabled"]:
        for n in fams["top_strength"]["edge_counts"]:
            variants.append({"construction_family": "top_strength", "construction_variant": f"top_edges_{n}", "edges": top_edges(rep_edges, int(n))})

    if fams["threshold"]["enabled"]:
        for t in fams["threshold"]["thresholds"]:
            variants.append({"construction_family": "threshold", "construction_variant": f"abs_weight_ge_{t}", "edges": threshold_edges(rep_edges, float(t))})

    if fams["mutual_knn"]["enabled"]:
        for k in fams["mutual_knn"]["k_values"]:
            variants.append({"construction_family": "mutual_knn", "construction_variant": f"k_{k}", "edges": mutual_knn_edges(rep_edges, node_ids, int(k))})

    if fams["maximum_spanning_tree"]["enabled"]:
        variants.append({"construction_family": "maximum_spanning_tree", "construction_variant": "abs_weight_mst", "edges": mst_edges(rep_edges, node_ids)})

    if fams["graph_distance_shells"]["enabled"]:
        for d in fams["graph_distance_shells"]["shell_depths"]:
            variants.append({"construction_family": "graph_distance_shells", "construction_variant": f"shell_depth_{d}", "edges": graph_distance_shell_edges(rep_edges, bond_edges, node_ids, int(d))})

    return variants


def edge_type_fraction(selected: Set[Edge], edges: Dict[Edge, Dict[str, Any]], edge_type: str) -> float:
    if not selected:
        return 0.0
    denom = sum(1 for e in selected if e in edges)
    if denom == 0:
        return 0.0
    return sum(1 for e in selected if edges.get(e, {}).get("edge_type") == edge_type) / denom


def mean_graph_distance(selected: Set[Edge], rep_edges: Dict[Edge, Dict[str, Any]]) -> float:
    vals = [as_float(rep_edges[e].get("graph_distance", ""), float("nan")) for e in selected if e in rep_edges]
    vals = [v for v in vals if math.isfinite(v)]
    return statistics.mean(vals) if vals else float("nan")


def metrics_for_object(
    representation_id: str,
    core_variant_id: str,
    object_id: str,
    null_family: str,
    repeat_index: int | str,
    rep_edges: Dict[Edge, Dict[str, Any]],
    bond_edges: Dict[Edge, Dict[str, Any]],
    node_ids: List[str],
    ref_core: Set[Edge],
    cfg: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ref_nodes = {x for e in ref_core for x in e}
    variants = construct_variants(rep_edges, bond_edges, node_ids, cfg)
    core_rows = []
    env_rows = []

    for var in variants:
        selected = var["edges"]
        selected_nodes = {x for e in selected for x in e}
        edge_cont = len(ref_core & selected) / len(ref_core) if ref_core else 0.0
        node_cont = len(ref_nodes & selected_nodes) / len(ref_nodes) if ref_nodes else 0.0
        frac_66 = edge_type_fraction(selected, rep_edges, "6_6")
        frac_56 = edge_type_fraction(selected, rep_edges, "5_6")
        bond_count = sum(1 for e in selected if rep_edges.get(e, {}).get("is_bond_edge", False))
        bond_frac = bond_count / len(selected) if selected else 0.0
        nonbond_frac = 1.0 - bond_frac if selected else 0.0
        mean_gd = mean_graph_distance(selected, rep_edges)
        cc = connected_component_count_for_edges(node_ids, selected) if selected else len(node_ids)

        base = {
            "representation_id": representation_id,
            "core_variant_id": core_variant_id,
            "object_id": object_id,
            "null_family": null_family,
            "repeat_index": repeat_index,
            "construction_family": var["construction_family"],
            "construction_variant": var["construction_variant"],
            "edge_count": len(selected),
            "node_count": len(selected_nodes),
        }

        metrics = [
            ("envelope_core_edge_containment", edge_cont),
            ("envelope_core_node_containment", node_cont),
            ("edge_type_6_6_fraction", frac_66),
            ("edge_type_5_6_fraction", frac_56),
            ("bond_edge_fraction", bond_frac),
            ("nonbond_edge_fraction", nonbond_frac),
            ("mean_graph_distance_selected", mean_gd),
            ("connected_component_count", cc),
        ]

        for name, value in metrics:
            row = dict(base)
            row["metric_name"] = name
            row["metric_value"] = value
            env_rows.append(row)
            if "core" in name:
                core_rows.append(row)

    return core_rows, env_rows


def degree_preserving_rewire_bond_graph(edges: Dict[Edge, Dict[str, Any]], rng: random.Random, attempts_factor: int) -> Dict[Edge, Dict[str, Any]]:
    edge_list = list(edges.keys())
    edge_set = set(edge_list)
    attempts = attempts_factor * len(edge_list)

    for _ in range(attempts):
        e1, e2 = rng.sample(edge_list, 2)
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) < 4:
            continue
        if rng.random() < 0.5:
            ne1, ne2 = edge_key(a, c), edge_key(b, d)
        else:
            ne1, ne2 = edge_key(a, d), edge_key(b, c)
        if ne1[0] == ne1[1] or ne2[0] == ne2[1] or ne1 == ne2:
            continue
        if ne1 in edge_set or ne2 in edge_set:
            continue
        edge_set.remove(e1)
        edge_set.remove(e2)
        edge_set.add(ne1)
        edge_set.add(ne2)
        edge_list = list(edge_set)

    attrs = [dict(v) for v in edges.values()]
    rng.shuffle(attrs)
    out = {}
    for i, e in enumerate(sorted(edge_set)):
        info = attrs[i % len(attrs)]
        et = str(info.get("edge_type", "unknown"))
        w = base_edge_weight(et)
        out[e] = {
            **info,
            "edge_id": f"null_e_{i+1:03d}",
            "source": e[0],
            "target": e[1],
            "weight": w,
            "distance": (1.0 / w - 1.0) if w > 0 else "",
            "graph_distance": 1,
            "is_bond_edge": True,
            "comment": "degree_preserving_rewire null edge",
        }
    return out


def edge_class_shuffle_bond_graph(edges: Dict[Edge, Dict[str, Any]], rng: random.Random) -> Dict[Edge, Dict[str, Any]]:
    attrs = [str(v.get("edge_type", "unknown")) for v in edges.values()]
    rng.shuffle(attrs)
    out = {}
    for i, e in enumerate(sorted(edges.keys())):
        base = dict(edges[e])
        et = attrs[i]
        w = base_edge_weight(et)
        base.update({
            "edge_type": et,
            "weight": w,
            "distance": (1.0 / w - 1.0) if w > 0 else "",
            "graph_distance": 1,
            "is_bond_edge": True,
            "comment": "edge_class_shuffle null edge",
        })
        out[e] = base
    return out


def motif_class_preserving_edge_swap_proxy(edges: Dict[Edge, Dict[str, Any]], rng: random.Random, attempts_factor: int) -> Dict[Edge, Dict[str, Any]]:
    # Proxy: rewire only pairs of edges with the same edge_type. This preserves
    # degree sequence and global edge-type counts, but not true fullerene planarity
    # or face cycles. It is intentionally labeled as a proxy.
    by_type: Dict[str, Set[Edge]] = defaultdict(set)
    for e, info in edges.items():
        by_type[str(info.get("edge_type", "unknown"))].add(e)

    result_edges: Dict[Edge, Dict[str, Any]] = {e: dict(info) for e, info in edges.items()}
    global_set = set(result_edges.keys())

    for et, edge_set in by_type.items():
        edge_list = list(edge_set)
        attempts = attempts_factor * max(1, len(edge_list))
        for _ in range(attempts):
            if len(edge_list) < 2:
                break
            e1, e2 = rng.sample(edge_list, 2)
            a, b = e1
            c, d = e2
            if len({a, b, c, d}) < 4:
                continue
            if rng.random() < 0.5:
                ne1, ne2 = edge_key(a, c), edge_key(b, d)
            else:
                ne1, ne2 = edge_key(a, d), edge_key(b, c)
            if ne1[0] == ne1[1] or ne2[0] == ne2[1] or ne1 == ne2:
                continue
            if ne1 in global_set or ne2 in global_set:
                continue

            info1 = result_edges.pop(e1)
            info2 = result_edges.pop(e2)
            global_set.remove(e1)
            global_set.remove(e2)
            edge_set.remove(e1)
            edge_set.remove(e2)

            for idx, ne in enumerate([ne1, ne2]):
                info = dict(info1 if idx == 0 else info2)
                w = base_edge_weight(et)
                info.update({
                    "edge_id": f"motif_proxy_{len(result_edges)+1:03d}",
                    "source": ne[0],
                    "target": ne[1],
                    "edge_type": et,
                    "weight": w,
                    "distance": (1.0 / w - 1.0) if w > 0 else "",
                    "graph_distance": 1,
                    "is_bond_edge": True,
                    "comment": "motif_class_preserving_edge_swap_proxy null edge",
                })
                result_edges[ne] = info
                global_set.add(ne)
                edge_set.add(ne)

            edge_list = list(edge_set)

    return result_edges


def core_seeded_decoy_bond_graph(edges: Dict[Edge, Dict[str, Any]], ref_core: Set[Edge], target_edge_type: str, rng: random.Random) -> Dict[Edge, Dict[str, Any]]:
    # Preserve topology and edge-type counts while assigning target edge type
    # to current reference-core edges.
    out = edge_class_shuffle_bond_graph(edges, rng)

    all_types = sorted({str(v.get("edge_type", "unknown")) for v in edges.values()})
    if target_edge_type not in all_types:
        return out

    other_types = [t for t in all_types if t != target_edge_type]
    fallback_other = other_types[0] if other_types else target_edge_type

    needed = [e for e in ref_core if e in out and out[e].get("edge_type") != target_edge_type]
    displaced = Counter(str(out[e].get("edge_type", fallback_other)) for e in needed)

    for e in needed:
        out[e]["edge_type"] = target_edge_type
        out[e]["weight"] = base_edge_weight(target_edge_type)
        out[e]["distance"] = (1.0 / base_edge_weight(target_edge_type) - 1.0) if base_edge_weight(target_edge_type) > 0 else ""
        out[e]["comment"] = f"core_seeded_decoy forced current core to {target_edge_type}"

    target_noncore = [e for e, info in out.items() if e not in ref_core and info.get("edge_type") == target_edge_type]
    rng.shuffle(target_noncore)

    cursor = 0
    for displaced_type, n in displaced.items():
        for e in target_noncore[cursor:cursor + n]:
            out[e]["edge_type"] = displaced_type
            out[e]["weight"] = base_edge_weight(displaced_type)
            out[e]["distance"] = (1.0 / base_edge_weight(displaced_type) - 1.0) if base_edge_weight(displaced_type) > 0 else ""
            out[e]["comment"] = "core_seeded_decoy count-preserving compensating flip"
        cursor += n

    return out


def summarize(real_rows: List[Dict[str, Any]], null_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    real_index = {
        (r["representation_id"], r["core_variant_id"], r["metric_name"], r["construction_family"], r["construction_variant"]): as_float(r["metric_value"])
        for r in real_rows
    }
    grouped = defaultdict(list)
    for r in null_rows:
        grouped[(
            r["representation_id"],
            r["core_variant_id"],
            r["null_family"],
            r["metric_name"],
            r["construction_family"],
            r["construction_variant"],
        )].append(as_float(r["metric_value"]))

    out = []
    for (rep_id, core_id, nfam, metric, cfam, cvar), vals in sorted(grouped.items()):
        vals = [v for v in vals if math.isfinite(v)]
        real = real_index.get((rep_id, core_id, metric, cfam, cvar), float("nan"))
        mean = statistics.mean(vals) if vals else float("nan")
        mn = min(vals) if vals else float("nan")
        mx = max(vals) if vals else float("nan")
        exceed = sum(1 for v in vals if v >= real) / len(vals) if vals and math.isfinite(real) else float("nan")
        delta = real - mean if math.isfinite(real) and math.isfinite(mean) else float("nan")

        if not math.isfinite(exceed):
            label = "inconclusive_due_to_scope_or_warnings"
        elif exceed >= 0.50:
            label = "null_reproduces_core_behavior" if "core" in metric else "null_reproduces_metric_behavior"
        elif exceed > 0.05:
            label = "mixed_family_dependent_result"
        else:
            label = "real_exceeds_tested_null_family"

        out.append({
            "representation_id": rep_id,
            "core_variant_id": core_id,
            "null_family": nfam,
            "metric_name": metric,
            "construction_family": cfam,
            "construction_variant": cvar,
            "real_value": real,
            "null_mean": mean,
            "null_min": mn,
            "null_max": mx,
            "real_minus_null_mean": delta,
            "empirical_exceedance_fraction": exceed,
            "null_count": len(vals),
            "interpretation_label": label,
        })
    return out


def edge_map_to_rows(
    representation_id: str,
    core_variant_id: str,
    object_id: str,
    null_family: str,
    repeat_index: int | str,
    edges: Dict[Edge, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    out = []
    for e, info in sorted(edges.items()):
        w = as_float(info.get("weight", ""), 0.0)
        out.append({
            "representation_id": representation_id,
            "core_variant_id": core_variant_id,
            "object_id": object_id,
            "null_family": null_family,
            "repeat_index": repeat_index,
            "edge_id": info.get("edge_id", ""),
            "source": e[0],
            "target": e[1],
            "edge_type": info.get("edge_type", ""),
            "source_degree": info.get("source_degree", ""),
            "target_degree": info.get("target_degree", ""),
            "shared_face_count": info.get("shared_face_count", ""),
            "shared_faces": info.get("shared_faces", ""),
            "shared_face_types": info.get("shared_face_types", ""),
            "weight": w,
            "distance": (1.0 / w - 1.0) if w > 0 else "",
            "graph_distance": info.get("graph_distance", ""),
            "is_bond_edge": info.get("is_bond_edge", ""),
            "comment": info.get("comment", ""),
        })
    return out


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    rng = random.Random(int(cfg["run"].get("random_seed", 0)))
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []
    nodes, bond_edges, faces, input_manifest = load_inputs(cfg, root, warnings)
    validation = validate_loaded_graph(nodes, bond_edges, faces)
    if not validation["expected_counts_ok"]:
        warnings.append({"severity": "warning", "message": f"Loaded graph validation failed: {validation}"})

    node_ids = sorted(n["node_id"] for n in nodes)
    shortest_paths = all_pairs_shortest_paths(node_ids, bond_edges)

    core_variant_rows, ref_edge_rows = build_core_variants(bond_edges, cfg, warnings)
    core_sets: Dict[str, Set[Edge]] = defaultdict(set)
    core_target_type: Dict[str, str] = {}
    for r in ref_edge_rows:
        core_id = r["core_variant_id"]
        core_sets[core_id].add(edge_key(r["source"], r["target"]))
        core_target_type[core_id] = str(r["edge_type"])

    representation_rows = []
    rep_edge_maps: Dict[str, Dict[Edge, Dict[str, Any]]] = {}
    for rep in cfg.get("representations", []):
        rep_id = rep["representation_id"]
        rep_edges = build_representation_edges(rep, node_ids, bond_edges, shortest_paths)
        rep_edge_maps[rep_id] = rep_edges
        representation_rows.append({
            "representation_id": rep_id,
            "edge_mode": rep.get("edge_mode", ""),
            "weight_rule_id": rep.get("weight_rule_id", ""),
            "max_graph_distance": rep.get("max_graph_distance", ""),
            "edge_count": len(rep_edges),
            "bond_edge_count": sum(1 for e in rep_edges if rep_edges[e].get("is_bond_edge", False)),
            "nonbond_edge_count": sum(1 for e in rep_edges if not rep_edges[e].get("is_bond_edge", False)),
            "min_weight": min([as_float(x.get("weight", ""), 0.0) for x in rep_edges.values()]) if rep_edges else "",
            "max_weight": max([as_float(x.get("weight", ""), 0.0) for x in rep_edges.values()]) if rep_edges else "",
        })

    all_edge_rows = []
    all_core, all_env = [], []
    real_env, null_env = [], []
    null_inventory = []

    nf = cfg["null_families"]

    # Generate null bond graphs per core variant, then project them into each representation.
    for core_row in core_variant_rows:
        core_id = core_row["core_variant_id"]
        ref_core = core_sets[core_id]
        target_type = core_target_type.get(core_id, "")

        null_bond_objects: List[Tuple[str, str, int | str, Dict[Edge, Dict[str, Any]]]] = [
            (f"{core_id}__real", "real", "real", bond_edges)
        ]

        if nf["degree_preserving_rewire"]["enabled"]:
            repeats = int(nf["degree_preserving_rewire"]["repeats"])
            factor = int(nf["degree_preserving_rewire"].get("swap_attempt_factor", 20))
            for i in range(repeats):
                emap = degree_preserving_rewire_bond_graph(bond_edges, rng, factor)
                oid = f"{core_id}__degree_preserving_rewire_{i:03d}"
                null_bond_objects.append((oid, "degree_preserving_rewire", i, emap))
                null_inventory.append({"core_variant_id": core_id, "object_id": oid, "null_family": "degree_preserving_rewire", "repeat_index": i})

        if nf["edge_class_shuffle"]["enabled"]:
            repeats = int(nf["edge_class_shuffle"]["repeats"])
            for i in range(repeats):
                emap = edge_class_shuffle_bond_graph(bond_edges, rng)
                oid = f"{core_id}__edge_class_shuffle_{i:03d}"
                null_bond_objects.append((oid, "edge_class_shuffle", i, emap))
                null_inventory.append({"core_variant_id": core_id, "object_id": oid, "null_family": "edge_class_shuffle", "repeat_index": i})

        if nf["motif_class_preserving_edge_swap_proxy"]["enabled"]:
            repeats = int(nf["motif_class_preserving_edge_swap_proxy"]["repeats"])
            factor = int(nf["motif_class_preserving_edge_swap_proxy"].get("swap_attempt_factor", 20))
            for i in range(repeats):
                emap = motif_class_preserving_edge_swap_proxy(bond_edges, rng, factor)
                oid = f"{core_id}__motif_class_preserving_edge_swap_proxy_{i:03d}"
                null_bond_objects.append((oid, "motif_class_preserving_edge_swap_proxy", i, emap))
                null_inventory.append({"core_variant_id": core_id, "object_id": oid, "null_family": "motif_class_preserving_edge_swap_proxy", "repeat_index": i})

        if nf["core_seeded_decoy"]["enabled"]:
            repeats = int(nf["core_seeded_decoy"]["repeats"])
            for i in range(repeats):
                emap = core_seeded_decoy_bond_graph(bond_edges, ref_core, target_type, rng)
                oid = f"{core_id}__core_seeded_decoy_{i:03d}"
                null_bond_objects.append((oid, "core_seeded_decoy", i, emap))
                null_inventory.append({"core_variant_id": core_id, "object_id": oid, "null_family": "core_seeded_decoy", "repeat_index": i})

        for rep in cfg.get("representations", []):
            rep_id = rep["representation_id"]
            for oid, nfam, rep_idx, null_bond_edges in null_bond_objects:
                # Recompute shortest paths for topology-perturbing nulls.
                if nfam in ("degree_preserving_rewire", "motif_class_preserving_edge_swap_proxy"):
                    sp = all_pairs_shortest_paths(node_ids, null_bond_edges)
                else:
                    sp = shortest_paths
                rep_edges = build_representation_edges(rep, node_ids, null_bond_edges, sp)

                all_edge_rows.extend(edge_map_to_rows(rep_id, core_id, oid, nfam, rep_idx, rep_edges))
                cr, er = metrics_for_object(rep_id, core_id, oid, nfam, rep_idx, rep_edges, null_bond_edges, node_ids, ref_core, cfg)
                all_core.extend(cr)
                all_env.extend(er)
                if nfam == "real":
                    real_env.extend(er)
                else:
                    null_env.extend(er)

    summary = summarize(real_env, null_env)

    rep_summary_rows = []
    grouped_rep = defaultdict(list)
    for r in summary:
        grouped_rep[(r["representation_id"], r["null_family"])].append(r)
    for (rep_id, nfam), rows in sorted(grouped_rep.items()):
        labels = Counter(r["interpretation_label"] for r in rows)
        core_rows_only = [r for r in rows if "core" in r["metric_name"]]
        rep_summary_rows.append({
            "representation_id": rep_id,
            "null_family": nfam,
            "summary_row_count": len(rows),
            "label_counts": json.dumps(dict(sorted(labels.items())), sort_keys=True),
            "core_metric_real_exceeds_count": sum(1 for r in core_rows_only if r["interpretation_label"] == "real_exceeds_tested_null_family"),
            "core_metric_null_reproduces_count": sum(1 for r in core_rows_only if r["interpretation_label"] == "null_reproduces_core_behavior"),
        })

    core_summary_rows = []
    grouped_core = defaultdict(list)
    for r in summary:
        grouped_core[(r["representation_id"], r["core_variant_id"], r["null_family"])].append(r)
    for (rep_id, core_id, nfam), rows in sorted(grouped_core.items()):
        labels = Counter(r["interpretation_label"] for r in rows)
        core_rows_only = [r for r in rows if "core" in r["metric_name"]]
        core_summary_rows.append({
            "representation_id": rep_id,
            "core_variant_id": core_id,
            "null_family": nfam,
            "summary_row_count": len(rows),
            "label_counts": json.dumps(dict(sorted(labels.items())), sort_keys=True),
            "core_metric_real_exceeds_count": sum(1 for r in core_rows_only if r["interpretation_label"] == "real_exceeds_tested_null_family"),
            "core_metric_null_reproduces_count": sum(1 for r in core_rows_only if r["interpretation_label"] == "null_reproduces_core_behavior"),
        })

    out = cfg["outputs"]

    node_fields = list(nodes[0].keys()) if nodes else []
    face_fields = list(faces[0].keys()) if faces else []
    representation_fields = [
        "representation_id", "edge_mode", "weight_rule_id", "max_graph_distance",
        "edge_count", "bond_edge_count", "nonbond_edge_count", "min_weight", "max_weight",
    ]
    core_variant_fields = [
        "core_variant_id", "core_variant_mode", "description", "selection_rule",
        "edge_count", "node_count", "edge_type_counts", "face_span_count",
        "pentagon_face_span_count", "hexagon_face_span_count",
        "face_type_incidence_counts", "connected_component_count",
    ]
    ref_fields = [
        "core_variant_id", "core_variant_mode", "core_edge_rank", "source",
        "target", "edge_type", "weight", "shared_faces", "shared_face_types",
        "reference_core_rule",
    ]
    edge_fields = [
        "representation_id", "core_variant_id", "object_id", "null_family",
        "repeat_index", "edge_id", "source", "target", "edge_type",
        "source_degree", "target_degree", "shared_face_count", "shared_faces",
        "shared_face_types", "weight", "distance", "graph_distance",
        "is_bond_edge", "comment",
    ]
    metric_fields = [
        "representation_id", "core_variant_id", "object_id", "null_family",
        "repeat_index", "construction_family", "construction_variant",
        "edge_count", "node_count", "metric_name", "metric_value",
    ]
    summary_fields = [
        "representation_id", "core_variant_id", "null_family", "metric_name",
        "construction_family", "construction_variant", "real_value",
        "null_mean", "null_min", "null_max", "real_minus_null_mean",
        "empirical_exceedance_fraction", "null_count", "interpretation_label",
    ]
    rep_summary_fields = [
        "representation_id", "null_family", "summary_row_count", "label_counts",
        "core_metric_real_exceeds_count", "core_metric_null_reproduces_count",
    ]
    core_summary_fields = [
        "representation_id", "core_variant_id", "null_family", "summary_row_count",
        "label_counts", "core_metric_real_exceeds_count",
        "core_metric_null_reproduces_count",
    ]

    write_csv(outdir / out["nodes_resolved_csv"], nodes, node_fields)
    write_csv(outdir / out["edges_csv"], all_edge_rows, edge_fields)
    write_csv(outdir / out["faces_csv"], faces, face_fields)
    write_csv(outdir / out["representations_csv"], representation_rows, representation_fields)
    write_csv(outdir / out["core_variants_csv"], core_variant_rows, core_variant_fields)
    write_csv(outdir / out["reference_core_edges_csv"], ref_edge_rows, ref_fields)
    write_csv(outdir / out["core_metrics_csv"], all_core, metric_fields)
    write_csv(outdir / out["envelope_metrics_csv"], all_env, metric_fields)
    write_csv(outdir / out["real_vs_null_summary_csv"], summary, summary_fields)
    write_csv(outdir / out["representation_summary_csv"], rep_summary_rows, rep_summary_fields)
    write_csv(outdir / out["core_variant_summary_csv"], core_summary_rows, core_summary_fields)
    write_csv(outdir / out["null_family_inventory_csv"], null_inventory, ["core_variant_id", "object_id", "null_family", "repeat_index"])

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_nodes_csv": cfg["inputs"]["nodes_csv"],
        "input_edges_csv": cfg["inputs"]["edges_csv"],
        "input_faces_csv": cfg["inputs"]["faces_csv"],
        "input_graph_valid": input_manifest.get("validation", {}).get("c60_valid", False),
        "loaded_graph_validation": validation,
        "node_count": len(nodes),
        "bond_edge_count": len(bond_edges),
        "face_count": len(faces),
        "representation_count": len(representation_rows),
        "representations": [r["representation_id"] for r in representation_rows],
        "core_variant_count": len(core_variant_rows),
        "core_variants": [r["core_variant_id"] for r in core_variant_rows],
        "reference_core_edge_count_total": len(ref_edge_rows),
        "object_count_per_representation": 1 + len(null_inventory),
        "null_family_counts": dict(Counter(r["null_family"] for r in null_inventory)),
        "row_counts": {
            "nodes_resolved": len(nodes),
            "edges": len(all_edge_rows),
            "faces": len(faces),
            "representations": len(representation_rows),
            "core_variants": len(core_variant_rows),
            "reference_core_edges": len(ref_edge_rows),
            "core_metrics": len(all_core),
            "envelope_metrics": len(all_env),
            "real_vs_null_summary": len(summary),
            "representation_summary": len(rep_summary_rows),
            "core_variant_summary": len(core_summary_rows),
            "null_family_inventory": len(null_inventory),
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
    parser = argparse.ArgumentParser(description="Run BMS-FU01c C60 motif/topology extension diagnostic.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
