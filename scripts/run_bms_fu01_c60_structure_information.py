#!/usr/bin/env python3
"""
BMS-FU01 — C60 Structure Information Diagnostic Runner

Runs a BMC-15h/ST01-style structured-specificity diagnostic on the audited
BMS-FU01 C60 / truncated-icosahedral graph artifacts.

Inputs:
  data/bms_fu01_c60_nodes.csv
  data/bms_fu01_c60_edges.csv
  data/bms_fu01_c60_faces.csv
  data/bms_fu01_c60_graph_manifest.json

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
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


Edge = Tuple[str, str]


EDGE_TYPE_WEIGHTS = {
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


def edge_weight(edge_type: str) -> float:
    return EDGE_TYPE_WEIGHTS.get(edge_type, 0.0)


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

    edges: Dict[Edge, Dict[str, Any]] = {}
    for r in edge_rows_in:
        a, b = r["source"], r["target"]
        e = edge_key(a, b)
        et = r.get("edge_type", "unknown")
        w = as_float(r.get("weight", ""), edge_weight(et))
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
            "distance": as_float(r.get("distance", ""), (1.0 / w - 1.0) if w > 0 else float("inf")),
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


def edge_map_to_rows(object_id: str, null_family: str, repeat_index: int | str, edges: Dict[Edge, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for e, info in sorted(edges.items()):
        w = as_float(info.get("weight", ""), edge_weight(str(info.get("edge_type", ""))))
        out.append({
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
            "comment": info.get("comment", ""),
        })
    return out


def build_adjacency(edges: Dict[Edge, Dict[str, Any]]) -> Dict[str, set[str]]:
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def connected_component_count(node_ids: List[str], edges: set[Edge]) -> int:
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

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


def select_reference_core(edges: Dict[Edge, Dict[str, Any]], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    settings = cfg["reference_core"]
    edge_type = settings.get("edge_type", "6_6")
    count = int(settings.get("edge_count", 12))

    candidates = []
    for e, info in edges.items():
        if info.get("edge_type") != edge_type:
            continue
        w = as_float(info.get("weight", ""), edge_weight(edge_type))
        candidates.append({
            "core_id": "edge_class_core",
            "source": e[0],
            "target": e[1],
            "edge_type": info.get("edge_type", ""),
            "weight": w,
            "shared_faces": info.get("shared_faces", ""),
            "shared_face_types": info.get("shared_face_types", ""),
            "reference_core_rule": f"first_{count}_{edge_type}_edges_sorted_by_id",
        })

    selected = sorted(candidates, key=lambda r: (r["source"], r["target"]))[:count]
    return selected


def weights_dict(edges: Dict[Edge, Dict[str, Any]]) -> Dict[Edge, float]:
    return {e: as_float(info.get("weight", ""), edge_weight(str(info.get("edge_type", "")))) for e, info in edges.items()}


def top_edges(edges: Dict[Edge, Dict[str, Any]], n: int) -> set[Edge]:
    return {
        e for e, _ in sorted(weights_dict(edges).items(), key=lambda kv: (abs(kv[1]), kv[0]), reverse=True)[:n]
    }


def threshold_edges(edges: Dict[Edge, Dict[str, Any]], t: float) -> set[Edge]:
    return {e for e, w in weights_dict(edges).items() if abs(w) >= t}


def mutual_knn_edges(edges: Dict[Edge, Dict[str, Any]], node_ids: List[str], k: int) -> set[Edge]:
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


def mst_edges(edges: Dict[Edge, Dict[str, Any]], node_ids: List[str]) -> set[Edge]:
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

    out = set()
    for (a, b), wt in sorted(weights_dict(edges).items(), key=lambda kv: (abs(kv[1]), kv[0]), reverse=True):
        if union(a, b):
            out.add((a, b))
        if len(out) >= len(node_ids) - 1:
            break
    return out


def graph_distance_shell_edges(edges: Dict[Edge, Dict[str, Any]], node_ids: List[str], shell_depth: int) -> set[Edge]:
    # Use the real/current graph adjacency and select all edges where at least one
    # endpoint is within shell_depth from the deterministic anchor c60_001.
    anchor = "c60_001" if "c60_001" in node_ids else sorted(node_ids)[0]
    adj = build_adjacency(edges)
    dist = {anchor: 0}
    q = deque([anchor])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                q.append(y)

    shell_nodes = {n for n, d in dist.items() if d <= shell_depth}
    return {e for e in edges if e[0] in shell_nodes or e[1] in shell_nodes}


def construct_variants(edges: Dict[Edge, Dict[str, Any]], node_ids: List[str], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    fams = cfg["construction_families"]
    variants = []

    if fams["top_strength"]["enabled"]:
        for n in fams["top_strength"]["edge_counts"]:
            variants.append({"construction_family": "top_strength", "construction_variant": f"top_edges_{n}", "edges": top_edges(edges, int(n))})

    if fams["threshold"]["enabled"]:
        for t in fams["threshold"]["thresholds"]:
            variants.append({"construction_family": "threshold", "construction_variant": f"abs_weight_ge_{t}", "edges": threshold_edges(edges, float(t))})

    if fams["mutual_knn"]["enabled"]:
        for k in fams["mutual_knn"]["k_values"]:
            variants.append({"construction_family": "mutual_knn", "construction_variant": f"k_{k}", "edges": mutual_knn_edges(edges, node_ids, int(k))})

    if fams["maximum_spanning_tree"]["enabled"]:
        variants.append({"construction_family": "maximum_spanning_tree", "construction_variant": "abs_weight_mst", "edges": mst_edges(edges, node_ids)})

    if fams["graph_distance_shells"]["enabled"]:
        for d in fams["graph_distance_shells"]["shell_depths"]:
            variants.append({"construction_family": "graph_distance_shells", "construction_variant": f"shell_depth_{d}", "edges": graph_distance_shell_edges(edges, node_ids, int(d))})

    return variants


def edge_type_fraction(selected: set[Edge], edges: Dict[Edge, Dict[str, Any]], edge_type: str) -> float:
    if not selected:
        return 0.0
    return sum(1 for e in selected if edges[e].get("edge_type") == edge_type) / len(selected)


def metrics_for_object(
    object_id: str,
    null_family: str,
    repeat_index: int | str,
    edges: Dict[Edge, Dict[str, Any]],
    node_ids: List[str],
    ref_core: set[Edge],
    cfg: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ref_nodes = {x for e in ref_core for x in e}
    variants = construct_variants(edges, node_ids, cfg)
    core_rows = []
    env_rows = []

    for var in variants:
        selected = var["edges"]
        selected_nodes = {x for e in selected for x in e}
        edge_cont = len(ref_core & selected) / len(ref_core) if ref_core else 0.0
        node_cont = len(ref_nodes & selected_nodes) / len(ref_nodes) if ref_nodes else 0.0
        frac_66 = edge_type_fraction(selected, edges, "6_6")
        frac_56 = edge_type_fraction(selected, edges, "5_6")
        cc = connected_component_count(node_ids, selected) if selected else len(node_ids)

        base = {
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


def degree_preserving_rewire(edges: Dict[Edge, Dict[str, Any]], rng: random.Random, attempts_factor: int) -> Dict[Edge, Dict[str, Any]]:
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

    # Preserve edge-type count by shuffling original edge types over rewired topology.
    attrs = [dict(v) for v in edges.values()]
    rng.shuffle(attrs)
    out = {}
    for i, e in enumerate(sorted(edge_set)):
        info = attrs[i % len(attrs)]
        et = str(info.get("edge_type", "unknown"))
        w = edge_weight(et)
        out[e] = {
            **info,
            "edge_id": f"null_e_{i+1:03d}",
            "source": e[0],
            "target": e[1],
            "weight": w,
            "distance": (1.0 / w - 1.0) if w > 0 else "",
            "comment": "degree_preserving_rewire null edge",
        }
    return out


def edge_class_shuffle(edges: Dict[Edge, Dict[str, Any]], rng: random.Random) -> Dict[Edge, Dict[str, Any]]:
    attrs = [str(v.get("edge_type", "unknown")) for v in edges.values()]
    rng.shuffle(attrs)
    out = {}
    for i, e in enumerate(sorted(edges.keys())):
        base = dict(edges[e])
        et = attrs[i]
        w = edge_weight(et)
        base.update({
            "edge_type": et,
            "weight": w,
            "distance": (1.0 / w - 1.0) if w > 0 else "",
            "comment": "edge_class_shuffle null edge",
        })
        out[e] = base
    return out


def core_seeded_decoy(edges: Dict[Edge, Dict[str, Any]], ref_core: set[Edge], rng: random.Random) -> Dict[Edge, Dict[str, Any]]:
    # Preserve topology and edge-type counts, but force reference-core edges to
    # receive high-priority 6_6 labels. To preserve counts, demote the same number
    # of non-core 6_6 edges to 5_6.
    out = edge_class_shuffle(edges, rng)
    needed = [e for e in ref_core if e in out and out[e].get("edge_type") != "6_6"]
    noncore_66 = [e for e, info in out.items() if e not in ref_core and info.get("edge_type") == "6_6"]
    rng.shuffle(noncore_66)

    for e in needed:
        out[e]["edge_type"] = "6_6"
        out[e]["weight"] = edge_weight("6_6")
        out[e]["distance"] = 0.0
        out[e]["comment"] = "core_seeded_decoy forced reference-core edge"

    for e in noncore_66[:len(needed)]:
        out[e]["edge_type"] = "5_6"
        out[e]["weight"] = edge_weight("5_6")
        out[e]["distance"] = (1.0 / edge_weight("5_6") - 1.0)
        out[e]["comment"] = "core_seeded_decoy count-preserving demotion"

    return out


def summarize(real_rows: List[Dict[str, Any]], null_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    real_index = {
        (r["metric_name"], r["construction_family"], r["construction_variant"]): as_float(r["metric_value"])
        for r in real_rows
    }
    grouped = defaultdict(list)
    for r in null_rows:
        grouped[(r["null_family"], r["metric_name"], r["construction_family"], r["construction_variant"])].append(as_float(r["metric_value"]))

    out = []
    for (nfam, metric, cfam, cvar), vals in sorted(grouped.items()):
        vals = [v for v in vals if math.isfinite(v)]
        real = real_index.get((metric, cfam, cvar), float("nan"))
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


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    rng = random.Random(int(cfg["run"].get("random_seed", 0)))
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []
    nodes, real_edges, faces, input_manifest = load_inputs(cfg, root, warnings)
    validation = validate_loaded_graph(nodes, real_edges, faces)
    if not validation["expected_counts_ok"]:
        warnings.append({"severity": "warning", "message": f"Loaded graph validation failed: {validation}"})

    node_ids = sorted(n["node_id"] for n in nodes)
    ref_rows = select_reference_core(real_edges, cfg)
    ref_core = {edge_key(r["source"], r["target"]) for r in ref_rows}

    object_edges: List[Tuple[str, str, int | str, Dict[Edge, Dict[str, Any]]]] = [("real", "real", "real", real_edges)]
    all_edge_rows = edge_map_to_rows("real", "real", "real", real_edges)
    null_inventory = []

    nf = cfg["null_families"]

    if nf["degree_preserving_rewire"]["enabled"]:
        repeats = int(nf["degree_preserving_rewire"]["repeats"])
        factor = int(nf["degree_preserving_rewire"].get("swap_attempt_factor", 20))
        for i in range(repeats):
            wmap = degree_preserving_rewire(real_edges, rng, factor)
            oid = f"degree_preserving_rewire_{i:03d}"
            object_edges.append((oid, "degree_preserving_rewire", i, wmap))
            all_edge_rows.extend(edge_map_to_rows(oid, "degree_preserving_rewire", i, wmap))
            null_inventory.append({"object_id": oid, "null_family": "degree_preserving_rewire", "repeat_index": i})

    if nf["edge_class_shuffle"]["enabled"]:
        repeats = int(nf["edge_class_shuffle"]["repeats"])
        for i in range(repeats):
            wmap = edge_class_shuffle(real_edges, rng)
            oid = f"edge_class_shuffle_{i:03d}"
            object_edges.append((oid, "edge_class_shuffle", i, wmap))
            all_edge_rows.extend(edge_map_to_rows(oid, "edge_class_shuffle", i, wmap))
            null_inventory.append({"object_id": oid, "null_family": "edge_class_shuffle", "repeat_index": i})

    if nf["core_seeded_decoy"]["enabled"]:
        repeats = int(nf["core_seeded_decoy"]["repeats"])
        for i in range(repeats):
            wmap = core_seeded_decoy(real_edges, ref_core, rng)
            oid = f"core_seeded_decoy_{i:03d}"
            object_edges.append((oid, "core_seeded_decoy", i, wmap))
            all_edge_rows.extend(edge_map_to_rows(oid, "core_seeded_decoy", i, wmap))
            null_inventory.append({"object_id": oid, "null_family": "core_seeded_decoy", "repeat_index": i})

    all_core, all_env = [], []
    real_env, null_env = [], []

    for oid, nfam, rep, emap in object_edges:
        cr, er = metrics_for_object(oid, nfam, rep, emap, node_ids, ref_core, cfg)
        all_core.extend(cr)
        all_env.extend(er)
        if nfam == "real":
            real_env.extend(er)
        else:
            null_env.extend(er)

    summary = summarize(real_env, null_env)

    out = cfg["outputs"]

    node_fields = list(nodes[0].keys()) if nodes else []
    face_fields = list(faces[0].keys()) if faces else []
    edge_fields = [
        "object_id", "null_family", "repeat_index", "edge_id", "source", "target",
        "edge_type", "source_degree", "target_degree", "shared_face_count",
        "shared_faces", "shared_face_types", "weight", "distance", "comment",
    ]
    ref_fields = [
        "core_id", "source", "target", "edge_type", "weight",
        "shared_faces", "shared_face_types", "reference_core_rule",
    ]
    metric_fields = [
        "object_id", "null_family", "repeat_index", "construction_family",
        "construction_variant", "edge_count", "node_count", "metric_name", "metric_value",
    ]
    summary_fields = [
        "null_family", "metric_name", "construction_family", "construction_variant",
        "real_value", "null_mean", "null_min", "null_max", "real_minus_null_mean",
        "empirical_exceedance_fraction", "null_count", "interpretation_label",
    ]

    write_csv(outdir / out["nodes_resolved_csv"], nodes, node_fields)
    write_csv(outdir / out["edges_csv"], all_edge_rows, edge_fields)
    write_csv(outdir / out["faces_csv"], faces, face_fields)
    write_csv(outdir / out["reference_core_edges_csv"], ref_rows, ref_fields)
    write_csv(outdir / out["core_metrics_csv"], all_core, metric_fields)
    write_csv(outdir / out["envelope_metrics_csv"], all_env, metric_fields)
    write_csv(outdir / out["real_vs_null_summary_csv"], summary, summary_fields)
    write_csv(outdir / out["null_family_inventory_csv"], null_inventory, ["object_id", "null_family", "repeat_index"])

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_nodes_csv": cfg["inputs"]["nodes_csv"],
        "input_edges_csv": cfg["inputs"]["edges_csv"],
        "input_faces_csv": cfg["inputs"]["faces_csv"],
        "input_graph_valid": input_manifest.get("validation", {}).get("c60_valid", False),
        "loaded_graph_validation": validation,
        "node_count": len(nodes),
        "real_edge_count": len(real_edges),
        "face_count": len(faces),
        "reference_core_edge_count": len(ref_core),
        "reference_core_mode": cfg["reference_core"]["mode"],
        "object_count": len(object_edges),
        "null_family_counts": dict(Counter(x[1] for x in object_edges if x[1] != "real")),
        "row_counts": {
            "nodes_resolved": len(nodes),
            "edges": len(all_edge_rows),
            "faces": len(faces),
            "reference_core_edges": len(ref_rows),
            "core_metrics": len(all_core),
            "envelope_metrics": len(all_env),
            "real_vs_null_summary": len(summary),
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
    parser = argparse.ArgumentParser(description="Run BMS-FU01 C60 structure information diagnostic.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
