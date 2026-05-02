#!/usr/bin/env python3
"""
BMS-FU02 — Load-Bearing Pattern Analysis Runner

Purpose:
  Identify candidate relational structure carriers in FU01c C60 outputs.

Scope:
  v0 uses FU01c outputs and validated C60 audit artifacts.
  It computes edge/node load-bearing scores, cross-representation persistence,
  null-resistance profiles and motif summaries.

Interpretation boundary:
  Candidate carriers are methodological structure-carrier candidates, not
  physical spacetime atoms and not proof of emergent spacetime.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

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


def parse_semicolon(s: Any) -> List[str]:
    if s is None:
        return []
    txt = str(s).strip()
    if not txt:
        return []
    return [x for x in txt.split(";") if x]


def parse_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes", "y"}


def load_required(path: Path, label: str) -> List[Dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing required {label}: {path}")
    return read_csv(path)


def build_adjacency(edges: Set[Edge]) -> Dict[str, Set[str]]:
    adj: Dict[str, Set[str]] = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def shortest_paths(node_ids: List[str], edges: Set[Edge]) -> Dict[str, Dict[str, int]]:
    adj = build_adjacency(edges)
    out: Dict[str, Dict[str, int]] = {}
    for start in node_ids:
        dist = {start: 0}
        q = deque([start])
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1
                    q.append(y)
        out[start] = dist
    return out


def closeness_proxy(node_id: str, dists: Dict[str, Dict[str, int]]) -> float:
    vals = [v for k, v in dists.get(node_id, {}).items() if k != node_id and v > 0]
    if not vals:
        return 0.0
    return (len(vals) / sum(vals)) if sum(vals) else 0.0


def edge_betweenness_proxy(edge: Edge, node_ids: List[str], dists: Dict[str, Dict[str, int]]) -> float:
    # Small unweighted proxy: count shortest-path pairs where edge endpoints can
    # sit consecutively on one shortest path. Not exact betweenness with path
    # multiplicity; deliberately simple and auditable for v0.
    a, b = edge
    count = 0
    total = 0
    for i, s in enumerate(node_ids):
        for t in node_ids[i + 1:]:
            dst = dists.get(s, {}).get(t)
            if dst is None:
                continue
            total += 1
            via_ab = dists[s].get(a, 10**9) + 1 + dists[b].get(t, 10**9)
            via_ba = dists[s].get(b, 10**9) + 1 + dists[a].get(t, 10**9)
            if via_ab == dst or via_ba == dst:
                count += 1
    return count / total if total else 0.0


def build_edge_features(
    c60_edges: List[Dict[str, str]],
    node_ids: List[str],
    bond_edge_set: Set[Edge],
    dists: Dict[str, Dict[str, int]],
) -> List[Dict[str, Any]]:
    features = []
    adj = build_adjacency(bond_edge_set)

    for r in c60_edges:
        e = edge_key(r["source"], r["target"])
        shared_faces = parse_semicolon(r.get("shared_faces", ""))
        shared_types_raw = str(r.get("shared_face_types", ""))
        shared_types = [x.strip() for x in shared_types_raw.split(",") if x.strip()]
        p_count = sum(1 for x in shared_types if x == "P")
        h_count = sum(1 for x in shared_types if x == "H")
        endpoint_c = [closeness_proxy(e[0], dists), closeness_proxy(e[1], dists)]
        shell_sig = f"{e[0]}:{dists.get('c60_001', {}).get(e[0], '')};{e[1]}:{dists.get('c60_001', {}).get(e[1], '')}"
        line_degree = (len(adj[e[0]]) - 1) + (len(adj[e[1]]) - 1)

        features.append({
            "edge_key": edge_key_str(e),
            "source": e[0],
            "target": e[1],
            "edge_type": r.get("edge_type", ""),
            "shared_faces": r.get("shared_faces", ""),
            "shared_face_types": r.get("shared_face_types", ""),
            "pentagon_incident": bool(p_count > 0),
            "hexagon_hexagon_edge": r.get("edge_type", "") == "6_6",
            "local_face_signature": r.get("shared_face_types", ""),
            "cycle5_proxy_count": p_count,
            "cycle6_proxy_count": h_count,
            "line_graph_degree": line_degree,
            "edge_betweenness_proxy": edge_betweenness_proxy(e, node_ids, dists),
            "mean_endpoint_shortest_path_centrality": sum(endpoint_c) / len(endpoint_c),
            "endpoint_shell_signature": shell_sig,
        })

    return features


def build_node_features(
    c60_nodes: List[Dict[str, str]],
    c60_edges: List[Dict[str, str]],
    dists: Dict[str, Dict[str, int]],
) -> List[Dict[str, Any]]:
    inc_66 = Counter()
    inc_56 = Counter()
    degree = Counter()

    for r in c60_edges:
        e = edge_key(r["source"], r["target"])
        degree[e[0]] += 1
        degree[e[1]] += 1
        if r.get("edge_type") == "6_6":
            inc_66[e[0]] += 1
            inc_66[e[1]] += 1
        if r.get("edge_type") == "5_6":
            inc_56[e[0]] += 1
            inc_56[e[1]] += 1

    out = []
    anchor = "c60_001"
    for n in c60_nodes:
        node_id = n["node_id"]
        out.append({
            "node_id": node_id,
            "degree": degree[node_id],
            "incident_6_6_count": inc_66[node_id],
            "incident_5_6_count": inc_56[node_id],
            "pentagon_membership_count": n.get("pentagon_membership_count", ""),
            "hexagon_membership_count": n.get("hexagon_membership_count", ""),
            "shortest_path_closeness_proxy": closeness_proxy(node_id, dists),
            "shell_signature": f"{anchor}:{dists.get(anchor, {}).get(node_id, '')}",
            "retained_edge_incidence_count": 0,
        })
    return out


def selected_edges_for_row(edge_rows_by_object: Dict[Tuple[str, str, str, str], List[Dict[str, str]]], key: Tuple[str, str, str, str], construction_family: str, construction_variant: str) -> Set[Edge]:
    # Reconstruct selected envelope edges according to the same deterministic
    # construction logic used in FU01c, but only for the object/representation/core.
    rows = edge_rows_by_object.get(key, [])
    if not rows:
        return set()

    def weight(row: Dict[str, str]) -> float:
        return as_float(row.get("weight", ""), 0.0)

    if construction_family == "top_strength":
        n = int(str(construction_variant).split("_")[-1])
        chosen = sorted(rows, key=lambda r: (abs(weight(r)), edge_key(r["source"], r["target"])), reverse=True)[:n]
        return {edge_key(r["source"], r["target"]) for r in chosen if parse_bool(r.get("is_bond_edge", "true"))}

    if construction_family == "threshold":
        t = float(str(construction_variant).split("_")[-1])
        return {edge_key(r["source"], r["target"]) for r in rows if abs(weight(r)) >= t and parse_bool(r.get("is_bond_edge", "true"))}

    if construction_family == "maximum_spanning_tree":
        node_ids = sorted({r["source"] for r in rows} | {r["target"] for r in rows})
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

        selected = set()
        for r in sorted(rows, key=lambda rr: (abs(weight(rr)), edge_key(rr["source"], rr["target"])), reverse=True):
            e = edge_key(r["source"], r["target"])
            if union(e[0], e[1]):
                if parse_bool(r.get("is_bond_edge", "true")):
                    selected.add(e)
            if len(selected) >= max(0, len(node_ids) - 1):
                break
        return selected

    if construction_family == "mutual_knn":
        k = int(str(construction_variant).split("_")[-1])
        node_ids = sorted({r["source"] for r in rows} | {r["target"] for r in rows})
        neigh = {n: [] for n in node_ids}
        row_map = {}
        for r in rows:
            e = edge_key(r["source"], r["target"])
            row_map[e] = r
            neigh[e[0]].append((e[1], weight(r)))
            neigh[e[1]].append((e[0], weight(r)))
        topn = {}
        for n, vals in neigh.items():
            topn[n] = {x for x, _ in sorted(vals, key=lambda t: (abs(t[1]), t[0]), reverse=True)[:k]}
        return {e for e, r in row_map.items() if e[1] in topn.get(e[0], set()) and e[0] in topn.get(e[1], set()) and parse_bool(r.get("is_bond_edge", "true"))}

    if construction_family == "graph_distance_shells":
        depth = int(str(construction_variant).split("_")[-1])
        # For FU02-v0, use the selected rows from FU01c object inventory:
        # include bond edges if either endpoint shell from c60_001 <= depth.
        # We derive shells from graph_distance row values only when the row itself
        # is incident to the anchor; otherwise this is approximated by source/target
        # ids through C60 canonical distances unavailable here. The runner later
        # overwrites this with C60 distance information where possible.
        # Safer v0 fallback: reconstruct from explicit FU01c selected pattern
        # by selecting edges that the FU01c metrics implied through row object is
        # not directly available. Return empty here to avoid hidden approximation.
        return set()

    return set()


def group_edge_rows(fu_edges: List[Dict[str, str]]) -> Dict[Tuple[str, str, str, str], List[Dict[str, str]]]:
    grouped: Dict[Tuple[str, str, str, str], List[Dict[str, str]]] = defaultdict(list)
    for r in fu_edges:
        key = (r["representation_id"], r["core_variant_id"], r["object_id"], r["null_family"])
        grouped[key].append(r)
    return grouped


def object_index(fu_edges: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = {}
    for r in fu_edges:
        key = (r["representation_id"], r["core_variant_id"], r["object_id"], r["null_family"], r["repeat_index"])
        seen[key] = {
            "representation_id": r["representation_id"],
            "core_variant_id": r["core_variant_id"],
            "object_id": r["object_id"],
            "null_family": r["null_family"],
            "repeat_index": r["repeat_index"],
        }
    return list(seen.values())


def compute_load_scores(
    fu_summary: List[Dict[str, str]],
    fu_edges: List[Dict[str, str]],
    c60_edge_features: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    warnings: List[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    include_fams = set(cfg["selection"]["include_construction_families"])
    edge_features_by_key = {r["edge_key"]: r for r in c60_edge_features}
    bond_edge_keys = set(edge_features_by_key.keys())

    grouped_edges = group_edge_rows(fu_edges)
    objects = object_index(fu_edges)

    # Use FU01c summary rows as construction/null contexts; for each context,
    # reconstruct selected bond edges from the real object and from null repeats.
    edge_acc = defaultdict(lambda: {
        "real_hits": 0, "real_contexts": 0,
        "null_hits": Counter(), "null_contexts": Counter(),
        "null_families": set(), "representations_positive": set(),
        "topology_representations_positive": set(),
        "core_variants_positive": set(),
        "strong_contexts": 0,
    })

    node_acc = defaultdict(lambda: {
        "real_hits": 0, "real_contexts": 0,
        "null_hits": Counter(), "null_contexts": Counter(),
        "representations_positive": set(),
        "topology_representations_positive": set(),
        "core_variants_positive": set(),
        "strong_contexts": 0,
    })

    null_profile = defaultdict(lambda: defaultdict(list))
    topology_reps = set(cfg["labels"]["topology_sensitive_representations"])
    positive_threshold = float(cfg["selection"]["positive_delta_threshold"])
    strong_threshold = float(cfg["selection"]["strong_delta_threshold"])

    # Build object lookup by representation/core/null family
    obj_by_rcn = defaultdict(list)
    for o in objects:
        obj_by_rcn[(o["representation_id"], o["core_variant_id"], o["null_family"])].append(o)

    used_contexts = 0
    skipped_shell_contexts = 0

    for s in fu_summary:
        metric = s.get("metric_name", "")
        if metric != "envelope_core_edge_containment":
            continue

        cfam = s["construction_family"]
        if cfam not in include_fams:
            continue

        if cfam == "graph_distance_shells":
            # FU02-v0 deliberately skips reconstruction for shell contexts, because
            # the selected edge set is not fully represented in summary rows and
            # approximating would hide assumptions. Shell-specific FU02b can add it.
            skipped_shell_contexts += 1
            continue

        rep = s["representation_id"]
        core = s["core_variant_id"]
        nfam = s["null_family"]
        cvar = s["construction_variant"]

        real_key = (rep, core, f"{core}__real", "real")
        real_selected = selected_edges_for_row(grouped_edges, real_key, cfam, cvar)
        real_selected = {e for e in real_selected if edge_key_str(e) in bond_edge_keys}

        null_objects = obj_by_rcn.get((rep, core, nfam), [])
        null_selected_all = []
        for o in null_objects:
            nkey = (rep, core, o["object_id"], nfam)
            ns = selected_edges_for_row(grouped_edges, nkey, cfam, cvar)
            ns = {e for e in ns if edge_key_str(e) in bond_edge_keys}
            null_selected_all.append(ns)

        if not null_selected_all:
            continue

        used_contexts += 1
        null_count = len(null_selected_all)

        for edge_s in bond_edge_keys:
            e = parse_edge_key(edge_s)
            real_hit = 1 if e in real_selected else 0
            null_hit_rate = sum(1 for ns in null_selected_all if e in ns) / null_count
            delta = real_hit - null_hit_rate

            edge_acc[edge_s]["real_contexts"] += 1
            edge_acc[edge_s]["real_hits"] += real_hit
            edge_acc[edge_s]["null_contexts"][nfam] += 1
            edge_acc[edge_s]["null_hits"][nfam] += null_hit_rate
            edge_acc[edge_s]["null_families"].add(nfam)
            null_profile[edge_s][nfam].append(delta)

            if delta > positive_threshold:
                edge_acc[edge_s]["representations_positive"].add(rep)
                edge_acc[edge_s]["core_variants_positive"].add(core)
                if rep in topology_reps:
                    edge_acc[edge_s]["topology_representations_positive"].add(rep)
            if delta >= strong_threshold:
                edge_acc[edge_s]["strong_contexts"] += 1

            for node in e:
                node_acc[node]["real_contexts"] += 1
                node_acc[node]["real_hits"] += real_hit
                node_acc[node]["null_contexts"][nfam] += 1
                node_acc[node]["null_hits"][nfam] += null_hit_rate
                if delta > positive_threshold:
                    node_acc[node]["representations_positive"].add(rep)
                    node_acc[node]["core_variants_positive"].add(core)
                    if rep in topology_reps:
                        node_acc[node]["topology_representations_positive"].add(rep)
                if delta >= strong_threshold:
                    node_acc[node]["strong_contexts"] += 1

    if skipped_shell_contexts:
        warnings.append({
            "severity": "info",
            "message": f"FU02-v0 skipped {skipped_shell_contexts} graph_distance_shells contexts to avoid hidden reconstruction assumptions.",
        })

    edge_rows = []
    for edge_s, a in sorted(edge_acc.items()):
        contexts = a["real_contexts"]
        real_rate = a["real_hits"] / contexts if contexts else 0.0
        null_means = {}
        for nfam, total in a["null_hits"].items():
            nctx = a["null_contexts"][nfam]
            null_means[nfam] = total / nctx if nctx else 0.0
        mean_null = sum(null_means.values()) / len(null_means) if null_means else 0.0
        load_score = real_rate - mean_null
        rep_count = len(a["representations_positive"])
        topo_count = len(a["topology_representations_positive"])

        label = classify_candidate(load_score, rep_count, topo_count, null_means)

        edge_rows.append({
            "edge_key": edge_s,
            "real_retention_rate": real_rate,
            "mean_null_retention_rate": mean_null,
            "load_bearing_score": load_score,
            "positive_representation_count": rep_count,
            "positive_representations": ";".join(sorted(a["representations_positive"])),
            "positive_topology_representation_count": topo_count,
            "positive_topology_representations": ";".join(sorted(a["topology_representations_positive"])),
            "positive_core_variant_count": len(a["core_variants_positive"]),
            "positive_core_variants": ";".join(sorted(a["core_variants_positive"])),
            "strong_context_count": a["strong_contexts"],
            "null_retention_rates_json": json.dumps(null_means, sort_keys=True),
            "candidate_label": label,
        })

    node_rows = []
    for node, a in sorted(node_acc.items()):
        contexts = a["real_contexts"]
        real_rate = a["real_hits"] / contexts if contexts else 0.0
        null_means = {}
        for nfam, total in a["null_hits"].items():
            nctx = a["null_contexts"][nfam]
            null_means[nfam] = total / nctx if nctx else 0.0
        mean_null = sum(null_means.values()) / len(null_means) if null_means else 0.0
        load_score = real_rate - mean_null
        rep_count = len(a["representations_positive"])
        topo_count = len(a["topology_representations_positive"])
        label = classify_candidate(load_score, rep_count, topo_count, null_means)

        node_rows.append({
            "node_id": node,
            "real_retention_rate": real_rate,
            "mean_null_retention_rate": mean_null,
            "load_bearing_score": load_score,
            "positive_representation_count": rep_count,
            "positive_representations": ";".join(sorted(a["representations_positive"])),
            "positive_topology_representation_count": topo_count,
            "positive_topology_representations": ";".join(sorted(a["topology_representations_positive"])),
            "positive_core_variant_count": len(a["core_variants_positive"]),
            "positive_core_variants": ";".join(sorted(a["core_variants_positive"])),
            "strong_context_count": a["strong_contexts"],
            "null_retention_rates_json": json.dumps(null_means, sort_keys=True),
            "candidate_label": label,
        })

    profile_rows = []
    for edge_s, fams in sorted(null_profile.items()):
        row = {"edge_key": edge_s}
        for nfam, vals in sorted(fams.items()):
            row[f"{nfam}_mean_delta"] = sum(vals) / len(vals) if vals else 0.0
            row[f"{nfam}_positive_fraction"] = sum(1 for v in vals if v > positive_threshold) / len(vals) if vals else 0.0
        profile_rows.append(row)

    carrier_rows = [
        r for r in sorted(edge_rows, key=lambda x: (x["load_bearing_score"], x["positive_topology_representation_count"], x["strong_context_count"]), reverse=True)
        if r["candidate_label"] in {"cross_representation_structure_carrier", "topology_only_structure_carrier", "weighted_or_mixed_candidate"}
    ]

    motif_rows = motif_summary(edge_rows, edge_features_by_key)

    return edge_rows, node_rows, profile_rows, carrier_rows, motif_rows


def classify_candidate(load_score: float, rep_count: int, topo_count: int, null_means: Dict[str, float]) -> str:
    core_seeded = null_means.get("core_seeded_decoy", 0.0)
    motif_proxy = null_means.get("motif_class_preserving_edge_swap_proxy", 0.0)

    if load_score <= 0:
        return "inconclusive_or_tie_sensitive"
    if topo_count >= 2 and rep_count >= 2 and core_seeded < 0.75:
        return "cross_representation_structure_carrier"
    if topo_count >= 2:
        return "topology_only_structure_carrier"
    if core_seeded >= 0.75:
        return "decoy_reproducible_candidate"
    if motif_proxy >= 0.75:
        return "motif_proxy_reproducible_candidate"
    return "weighted_or_mixed_candidate"


def motif_summary(edge_rows: List[Dict[str, Any]], edge_features_by_key: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = defaultdict(list)
    for r in edge_rows:
        feat = edge_features_by_key.get(r["edge_key"], {})
        motif = feat.get("shared_face_types", "") or feat.get("edge_type", "unknown")
        grouped[motif].append(r)

    out = []
    for motif, rows in sorted(grouped.items()):
        scores = [as_float(r["load_bearing_score"], 0.0) for r in rows]
        labels = Counter(r["candidate_label"] for r in rows)
        out.append({
            "motif_signature": motif,
            "edge_count": len(rows),
            "mean_load_bearing_score": sum(scores) / len(scores) if scores else 0.0,
            "max_load_bearing_score": max(scores) if scores else 0.0,
            "candidate_label_counts": json.dumps(dict(sorted(labels.items())), sort_keys=True),
            "top_edges": ";".join(r["edge_key"] for r in sorted(rows, key=lambda x: x["load_bearing_score"], reverse=True)[:10]),
        })
    return out


def merge_features_scores(edge_features: List[Dict[str, Any]], edge_scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    score_by = {r["edge_key"]: r for r in edge_scores}
    out = []
    for f in edge_features:
        row = dict(f)
        row.update(score_by.get(f["edge_key"], {}))
        out.append(row)
    return out


def merge_node_features_scores(node_features: List[Dict[str, Any]], node_scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    score_by = {r["node_id"]: r for r in node_scores}
    out = []
    for f in node_features:
        row = dict(f)
        row.update(score_by.get(f["node_id"], {}))
        out.append(row)
    return out


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)
    warnings: List[Dict[str, str]] = []

    fu_dir = root / cfg["inputs"]["fu01c_output_dir"]
    fu_manifest_path = fu_dir / "bms_fu01c_run_manifest.json"
    fu_warnings_path = fu_dir / "bms_fu01c_warnings.json"
    if not fu_manifest_path.exists():
        raise SystemExit(f"Missing FU01c manifest: {fu_manifest_path}")
    fu_manifest = read_json(fu_manifest_path)
    fu_warnings = read_json(fu_warnings_path) if fu_warnings_path.exists() else []
    if fu_warnings:
        warnings.append({"severity": "warning", "message": f"FU01c warning count is {len(fu_warnings)}; FU02 continues but records this."})

    c60_manifest = read_json(root / cfg["inputs"]["c60_graph_manifest_json"])
    if not c60_manifest.get("validation", {}).get("c60_valid", False):
        warnings.append({"severity": "warning", "message": "C60 builder manifest does not report c60_valid=true."})

    c60_nodes = load_required(root / cfg["inputs"]["c60_nodes_csv"], "C60 nodes")
    c60_edges = load_required(root / cfg["inputs"]["c60_edges_csv"], "C60 edges")
    c60_faces = load_required(root / cfg["inputs"]["c60_faces_csv"], "C60 faces")

    fu_summary = load_required(fu_dir / "bms_fu01c_real_vs_null_summary.csv", "FU01c summary")
    fu_edges = load_required(fu_dir / "bms_fu01c_edges.csv", "FU01c edges")

    node_ids = sorted(r["node_id"] for r in c60_nodes)
    bond_edge_set = {edge_key(r["source"], r["target"]) for r in c60_edges}
    dists = shortest_paths(node_ids, bond_edge_set)

    edge_features = build_edge_features(c60_edges, node_ids, bond_edge_set, dists)
    node_features = build_node_features(c60_nodes, c60_edges, dists)

    edge_scores, node_scores, null_profiles, carrier_rows, motif_rows = compute_load_scores(
        fu_summary=fu_summary,
        fu_edges=fu_edges,
        c60_edge_features=edge_features,
        cfg=cfg,
        warnings=warnings,
    )

    edge_merged = merge_features_scores(edge_features, edge_scores)
    node_merged = merge_node_features_scores(node_features, node_scores)

    # Update retained_edge_incidence_count based on carrier edges only.
    carrier_edges = {parse_edge_key(r["edge_key"]) for r in carrier_rows}
    retained_inc = Counter()
    for a, b in carrier_edges:
        retained_inc[a] += 1
        retained_inc[b] += 1
    for row in node_merged:
        row["retained_edge_incidence_count"] = retained_inc[row["node_id"]]

    out = cfg["outputs"]

    edge_feature_fields = [
        "edge_key", "source", "target", "edge_type", "shared_faces", "shared_face_types",
        "pentagon_incident", "hexagon_hexagon_edge", "local_face_signature",
        "cycle5_proxy_count", "cycle6_proxy_count", "line_graph_degree",
        "edge_betweenness_proxy", "mean_endpoint_shortest_path_centrality",
        "endpoint_shell_signature",
    ]
    edge_score_fields = [
        "edge_key", "real_retention_rate", "mean_null_retention_rate",
        "load_bearing_score", "positive_representation_count",
        "positive_representations", "positive_topology_representation_count",
        "positive_topology_representations", "positive_core_variant_count",
        "positive_core_variants", "strong_context_count",
        "null_retention_rates_json", "candidate_label",
    ]
    edge_merged_fields = edge_feature_fields + [f for f in edge_score_fields if f != "edge_key"]

    node_feature_fields = [
        "node_id", "degree", "incident_6_6_count", "incident_5_6_count",
        "pentagon_membership_count", "hexagon_membership_count",
        "shortest_path_closeness_proxy", "shell_signature", "retained_edge_incidence_count",
    ]
    node_score_fields = [
        "node_id", "real_retention_rate", "mean_null_retention_rate",
        "load_bearing_score", "positive_representation_count",
        "positive_representations", "positive_topology_representation_count",
        "positive_topology_representations", "positive_core_variant_count",
        "positive_core_variants", "strong_context_count",
        "null_retention_rates_json", "candidate_label",
    ]
    node_merged_fields = node_feature_fields + [f for f in node_score_fields if f not in {"node_id", "retained_edge_incidence_count"}]

    # Null profile fields are dynamic.
    profile_fields = sorted({k for row in null_profiles for k in row.keys()})
    if "edge_key" in profile_fields:
        profile_fields = ["edge_key"] + [f for f in profile_fields if f != "edge_key"]

    motif_fields = [
        "motif_signature", "edge_count", "mean_load_bearing_score",
        "max_load_bearing_score", "candidate_label_counts", "top_edges",
    ]

    write_csv(outdir / out["edge_explanatory_features_csv"], edge_features, edge_feature_fields)
    write_csv(outdir / out["node_explanatory_features_csv"], node_features, node_feature_fields)
    write_csv(outdir / out["edge_load_bearing_scores_csv"], edge_merged, edge_merged_fields)
    write_csv(outdir / out["node_load_bearing_scores_csv"], node_merged, node_merged_fields)
    write_csv(outdir / out["null_resistance_profiles_csv"], null_profiles, profile_fields)
    write_csv(outdir / out["cross_representation_carriers_csv"], carrier_rows, edge_score_fields)
    write_csv(outdir / out["candidate_structure_carriers_csv"], carrier_rows, edge_score_fields)
    write_csv(outdir / out["motif_load_bearing_summary_csv"], motif_rows, motif_fields)

    label_counts = Counter(r.get("candidate_label", "") for r in edge_scores)
    motif_counts = {r["motif_signature"]: r["edge_count"] for r in motif_rows}

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_fu01c_output_dir": cfg["inputs"]["fu01c_output_dir"],
        "fu01c_run_id": fu_manifest.get("run_id", ""),
        "fu01c_warning_count": len(fu_warnings),
        "c60_valid": c60_manifest.get("validation", {}).get("c60_valid", False),
        "node_count": len(c60_nodes),
        "bond_edge_count": len(c60_edges),
        "face_count": len(c60_faces),
        "edge_score_count": len(edge_scores),
        "node_score_count": len(node_scores),
        "candidate_carrier_count": len(carrier_rows),
        "candidate_label_counts": dict(sorted(label_counts.items())),
        "motif_counts": motif_counts,
        "row_counts": {
            "edge_explanatory_features": len(edge_features),
            "node_explanatory_features": len(node_features),
            "edge_load_bearing_scores": len(edge_merged),
            "node_load_bearing_scores": len(node_merged),
            "null_resistance_profiles": len(null_profiles),
            "cross_representation_carriers": len(carrier_rows),
            "candidate_structure_carriers": len(carrier_rows),
            "motif_load_bearing_summary": len(motif_rows),
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
    parser = argparse.ArgumentParser(description="Run BMS-FU02 load-bearing pattern analysis.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
