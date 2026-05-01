#!/usr/bin/env python3
"""
BMS-ST01 — Structure Information Specificity Runner

This runner applies a BMC-15h-style structured-specificity diagnostic to an
already-built relational structure graph.

Input graph:
  data/baseline_relational_table_real.csv

Node metadata:
  data/node_metadata_real.csv

Interpretation boundary:
  This is a structure-information diagnostic on a proxy relational graph. It
  does not recover a physical metric and does not prove emergent spacetime.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


Edge = Tuple[str, str]


def as_float(value: Any, default: float = float("nan")) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def edge_key(a: str, b: str) -> Edge:
    return (a, b) if a <= b else (b, a)


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def load_nodes(cfg: Dict[str, Any], root: Path, warnings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    p = root / cfg["inputs"]["node_metadata"]
    if not p.exists():
        warnings.append({"severity": "warning", "message": f"Node metadata not found: {p}"})
        return []

    rows = []
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "node_id": r.get("node_id", ""),
                "shell_index": r.get("shell_index", ""),
                "node_label": r.get("node_label", ""),
                "node_family": r.get("node_family", ""),
                "origin_tag": r.get("origin_tag", ""),
                "comment": r.get("comment", ""),
                "feature_shape_factor": r.get("feature_shape_factor", ""),
                "feature_spectral_index": r.get("feature_spectral_index", ""),
            })

    if not rows:
        warnings.append({"severity": "warning", "message": "No node metadata rows loaded."})
    return rows


def load_real_edges(cfg: Dict[str, Any], root: Path, warnings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    p = root / cfg["inputs"]["edge_table"]
    if not p.exists():
        warnings.append({"severity": "warning", "message": f"Edge table not found: {p}"})
        return []

    c = cfg["columns"]
    rows = []
    with p.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            source = r.get(c["source"], "")
            target = r.get(c["target"], "")
            w = as_float(r.get(c["weight"], ""))
            if not source or not target or not math.isfinite(w):
                warnings.append({"severity": "warning", "message": f"Skipping invalid edge row: {r}"})
                continue
            rows.append({
                "object_id": "real",
                "null_family": "real",
                "repeat_index": "real",
                "source": source,
                "target": target,
                "weight": w,
                "distance": (1.0 / w - 1.0) if w > 0 else float("inf"),
                "edge_family": r.get(c.get("edge_family", "edge_family"), ""),
                "source_family": r.get(c.get("source_family", "source_family"), ""),
                "target_family": r.get(c.get("target_family", "target_family"), ""),
                "relation_type": r.get("relation_type", ""),
                "evidence_tag": r.get("evidence_tag", ""),
                "comment": r.get("comment", ""),
            })
    return rows


def edge_weights_map(edges: List[Dict[str, Any]]) -> Dict[Edge, float]:
    return {edge_key(e["source"], e["target"]): as_float(e["weight"]) for e in edges}


def map_to_edge_rows(weights: Dict[Edge, float], object_id: str, null_family: str, repeat_index: int | str) -> List[Dict[str, Any]]:
    rows = []
    for (a, b), w in weights.items():
        rows.append({
            "object_id": object_id,
            "null_family": null_family,
            "repeat_index": repeat_index,
            "source": a,
            "target": b,
            "weight": w,
            "distance": (1.0 / w - 1.0) if w > 0 else float("inf"),
            "edge_family": "",
            "source_family": "",
            "target_family": "",
            "relation_type": "null_weight_assignment",
            "evidence_tag": "BMS-ST01",
            "comment": "",
        })
    return rows


def top_edges(weights: Dict[Edge, float], count: int) -> Dict[Edge, float]:
    return dict(sorted(weights.items(), key=lambda kv: abs(kv[1]), reverse=True)[:count])


def threshold_edges(weights: Dict[Edge, float], threshold: float) -> Dict[Edge, float]:
    return {e: w for e, w in weights.items() if abs(w) >= threshold}


def mutual_knn_edges(weights: Dict[Edge, float], node_ids: List[str], k: int) -> Dict[Edge, float]:
    neigh = {n: [] for n in node_ids}
    for (a, b), w in weights.items():
        if a not in neigh or b not in neigh:
            continue
        neigh[a].append((b, w))
        neigh[b].append((a, w))

    topn = {}
    for n, vals in neigh.items():
        topn[n] = {x for x, _ in sorted(vals, key=lambda t: abs(t[1]), reverse=True)[:k]}

    return {(a, b): w for (a, b), w in weights.items() if a in topn and b in topn and b in topn[a] and a in topn[b]}


def mst_edges(weights: Dict[Edge, float], node_ids: List[str]) -> Dict[Edge, float]:
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

    out = {}
    for (a, b), w in sorted(weights.items(), key=lambda kv: abs(kv[1]), reverse=True):
        if a not in parent or b not in parent:
            continue
        if union(a, b):
            out[(a, b)] = w
        if len(out) >= max(0, len(node_ids) - 1):
            break
    return out


def construct_variants(weights: Dict[Edge, float], node_ids: List[str], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    fams = cfg["construction_families"]
    variants = []

    if fams["top_strength"]["enabled"]:
        for n in fams["top_strength"]["edge_counts"]:
            variants.append({
                "construction_family": "top_strength",
                "construction_variant": f"top_edges_{n}",
                "edges": top_edges(weights, int(n)),
            })

    if fams["threshold"]["enabled"]:
        for t in fams["threshold"]["thresholds"]:
            variants.append({
                "construction_family": "threshold",
                "construction_variant": f"abs_weight_ge_{t}",
                "edges": threshold_edges(weights, float(t)),
            })

    if fams["mutual_knn"]["enabled"]:
        for k in fams["mutual_knn"]["k_values"]:
            variants.append({
                "construction_family": "mutual_knn",
                "construction_variant": f"k_{k}",
                "edges": mutual_knn_edges(weights, node_ids, int(k)),
            })

    if fams["maximum_spanning_tree"]["enabled"]:
        variants.append({
            "construction_family": "maximum_spanning_tree",
            "construction_variant": "abs_weight_mst",
            "edges": mst_edges(weights, node_ids),
        })

    return variants


def select_reference_core(
    weights: Dict[Edge, float],
    nodes: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    warnings: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    meta = {n["node_id"]: n for n in nodes}
    settings = cfg["reference_core"]
    families = settings.get("families") or sorted({n["node_family"] for n in nodes})
    edges_per_family = int(settings.get("edges_per_family", 3))
    within_family_only = bool(settings.get("within_family_only", True))

    rows = []
    for fam in families:
        family_nodes = {n["node_id"] for n in nodes if n["node_family"] == fam}
        candidates = []
        for (a, b), w in weights.items():
            if a not in family_nodes or b not in family_nodes:
                if within_family_only:
                    continue
            if within_family_only and not (a in family_nodes and b in family_nodes):
                continue
            if a not in meta or b not in meta:
                continue
            candidates.append({
                "family_id": fam,
                "source": a,
                "target": b,
                "weight": w,
                "reference_core_rule": settings.get("mode", "family_balanced_within_family_top_edges"),
                "source_family": meta[a].get("node_family", ""),
                "target_family": meta[b].get("node_family", ""),
                "source_label": meta[a].get("node_label", ""),
                "target_label": meta[b].get("node_label", ""),
                "source_shape_factor": meta[a].get("feature_shape_factor", ""),
                "target_shape_factor": meta[b].get("feature_shape_factor", ""),
                "source_spectral_index": meta[a].get("feature_spectral_index", ""),
                "target_spectral_index": meta[b].get("feature_spectral_index", ""),
            })

        selected = sorted(candidates, key=lambda r: abs(as_float(r["weight"])), reverse=True)[:edges_per_family]
        if len(selected) < edges_per_family:
            warnings.append({
                "severity": "warning",
                "message": f"Family {fam} has only {len(selected)} eligible within-family core edges; requested {edges_per_family}.",
            })
        rows.extend(selected)
    return rows


def metrics_for_object(
    object_id: str,
    null_family: str,
    repeat_index: int | str,
    weights: Dict[Edge, float],
    nodes: List[Dict[str, Any]],
    ref_core_edges: set[Edge],
    cfg: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    node_ids = [n["node_id"] for n in nodes]
    family = {n["node_id"]: n["node_family"] for n in nodes}
    ref_nodes = {x for e in ref_core_edges for x in e}
    variants = construct_variants(weights, node_ids, cfg)

    core_rows = []
    env_rows = []

    for var in variants:
        env_edges = set(var["edges"].keys())
        env_nodes = {x for e in env_edges for x in e}

        edge_cont = len(ref_core_edges & env_edges) / len(ref_core_edges) if ref_core_edges else 0.0
        node_cont = len(ref_nodes & env_nodes) / len(ref_nodes) if ref_nodes else 0.0
        family_purity = (
            sum(1 for a, b in env_edges if family.get(a) == family.get(b)) / len(env_edges)
            if env_edges else 0.0
        )
        cross_family_fraction = (
            sum(1 for a, b in env_edges if family.get(a) != family.get(b)) / len(env_edges)
            if env_edges else 0.0
        )

        base = {
            "object_id": object_id,
            "null_family": null_family,
            "repeat_index": repeat_index,
            "construction_family": var["construction_family"],
            "construction_variant": var["construction_variant"],
            "edge_count": len(env_edges),
            "node_count": len(env_nodes),
        }

        for name, value in [
            ("envelope_core_edge_containment", edge_cont),
            ("envelope_core_node_containment", node_cont),
            ("family_purity", family_purity),
            ("cross_family_fraction", cross_family_fraction),
        ]:
            row = dict(base)
            row["metric_name"] = name
            row["metric_value"] = value
            env_rows.append(row)

        for name, value in [
            ("envelope_core_edge_containment", edge_cont),
            ("envelope_core_node_containment", node_cont),
        ]:
            row = dict(base)
            row["metric_name"] = name
            row["metric_value"] = value
            core_rows.append(row)

    return core_rows, env_rows


def summarize(real_rows: List[Dict[str, Any]], null_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    real_index = {
        (r["metric_name"], r["construction_family"], r["construction_variant"]): as_float(r["metric_value"])
        for r in real_rows
    }
    grouped = defaultdict(list)
    for r in null_rows:
        grouped[(r["null_family"], r["metric_name"], r["construction_family"], r["construction_variant"])].append(as_float(r["metric_value"]))

    out = []
    for (null_family, metric_name, cfam, cvar), vals in sorted(grouped.items()):
        vals = [v for v in vals if math.isfinite(v)]
        real = real_index.get((metric_name, cfam, cvar), float("nan"))
        mean = statistics.mean(vals) if vals else float("nan")
        mn = min(vals) if vals else float("nan")
        mx = max(vals) if vals else float("nan")
        exceed = sum(1 for v in vals if v >= real) / len(vals) if vals and math.isfinite(real) else float("nan")
        delta = real - mean if math.isfinite(real) and math.isfinite(mean) else float("nan")

        if not math.isfinite(exceed):
            label = "inconclusive_due_to_scope_or_warnings"
        elif exceed >= 0.50:
            label = "null_reproduces_core_behavior" if "core" in metric_name else "null_reproduces_metric_behavior"
        elif exceed > 0.05:
            label = "mixed_family_dependent_result"
        else:
            label = "real_exceeds_tested_null_family"

        out.append({
            "null_family": null_family,
            "metric_name": metric_name,
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

    warnings = []
    nodes = load_nodes(cfg, root, warnings)
    real_edges = load_real_edges(cfg, root, warnings)
    real_weights = edge_weights_map(real_edges)
    node_ids = [n["node_id"] for n in nodes]

    meta_ids = set(node_ids)
    edge_node_ids = {x for e in real_weights for x in e}
    missing_meta = sorted(edge_node_ids - meta_ids)
    if missing_meta:
        warnings.append({"severity": "warning", "message": f"{len(missing_meta)} edge nodes missing metadata: {missing_meta[:10]}"})

    ref_rows = select_reference_core(real_weights, nodes, cfg, warnings)
    ref_core_edges = {edge_key(r["source"], r["target"]) for r in ref_rows}

    all_edges = list(real_edges)
    object_weights = [("real", "real", "real", real_weights)]
    null_inventory = []

    pairs = list(real_weights.keys())
    weights_list = list(real_weights.values())
    nf = cfg["null_families"]

    if nf["degree_weight_preserving_rewire"]["enabled"]:
        for i in range(int(nf["degree_weight_preserving_rewire"]["repeats"])):
            shuffled = weights_list[:]
            rng.shuffle(shuffled)
            wmap = dict(zip(pairs, shuffled))
            oid = f"degree_weight_preserving_rewire_{i:03d}"
            object_weights.append((oid, "degree_weight_preserving_rewire", i, wmap))
            all_edges.extend(map_to_edge_rows(wmap, oid, "degree_weight_preserving_rewire", i))
            null_inventory.append({"object_id": oid, "null_family": "degree_weight_preserving_rewire", "repeat_index": i})

    if nf["feature_structured_shuffle"]["enabled"]:
        # Node-label shuffle within family: permute node identities within each family while preserving pair weights.
        by_family = defaultdict(list)
        for n in nodes:
            by_family[n["node_family"]].append(n["node_id"])

        for i in range(int(nf["feature_structured_shuffle"]["repeats"])):
            mapping = {}
            for fam, ids in by_family.items():
                shuffled_ids = ids[:]
                rng.shuffle(shuffled_ids)
                mapping.update(dict(zip(ids, shuffled_ids)))

            wmap = {}
            for (a, b), w in real_weights.items():
                aa = mapping.get(a, a)
                bb = mapping.get(b, b)
                if aa == bb:
                    continue
                wmap[edge_key(aa, bb)] = w

            oid = f"feature_structured_shuffle_{i:03d}"
            object_weights.append((oid, "feature_structured_shuffle", i, wmap))
            all_edges.extend(map_to_edge_rows(wmap, oid, "feature_structured_shuffle", i))
            null_inventory.append({"object_id": oid, "null_family": "feature_structured_shuffle", "repeat_index": i})

    if nf["core_seeded_decoy"]["enabled"]:
        sorted_weights = sorted(weights_list)
        q = float(nf["core_seeded_decoy"].get("seed_weight_quantile", 0.90))
        q_index = min(len(sorted_weights) - 1, max(0, int(q * (len(sorted_weights) - 1))))
        high_weights = [w for w in sorted_weights if w >= sorted_weights[q_index]]
        if not high_weights:
            high_weights = sorted_weights[-max(1, len(ref_core_edges)):]

        for i in range(int(nf["core_seeded_decoy"]["repeats"])):
            shuffled = weights_list[:]
            rng.shuffle(shuffled)
            wmap = dict(zip(pairs, shuffled))
            for e in ref_core_edges:
                wmap[e] = rng.choice(high_weights)
            oid = f"core_seeded_decoy_{i:03d}"
            object_weights.append((oid, "core_seeded_decoy", i, wmap))
            all_edges.extend(map_to_edge_rows(wmap, oid, "core_seeded_decoy", i))
            null_inventory.append({"object_id": oid, "null_family": "core_seeded_decoy", "repeat_index": i})

    all_core, all_env = [], []
    real_env, null_env = [], []

    for oid, nfam, rep, wmap in object_weights:
        cr, er = metrics_for_object(oid, nfam, rep, wmap, nodes, ref_core_edges, cfg)
        all_core.extend(cr)
        all_env.extend(er)
        if nfam == "real":
            real_env.extend(er)
        else:
            null_env.extend(er)

    summary = summarize(real_env, null_env)

    family_summary = []
    fam_counts = Counter(n["node_family"] for n in nodes)
    for fam, count in sorted(fam_counts.items()):
        family_summary.append({
            "node_family": fam,
            "node_count": count,
            "node_ids": ";".join(sorted(n["node_id"] for n in nodes if n["node_family"] == fam)),
        })

    out = cfg["outputs"]
    node_fields = [
        "node_id", "shell_index", "node_label", "node_family", "origin_tag",
        "comment", "feature_shape_factor", "feature_spectral_index",
    ]
    edge_fields = [
        "object_id", "null_family", "repeat_index", "source", "target",
        "weight", "distance", "edge_family", "source_family", "target_family",
        "relation_type", "evidence_tag", "comment",
    ]
    ref_fields = [
        "family_id", "source", "target", "weight", "reference_core_rule",
        "source_family", "target_family", "source_label", "target_label",
        "source_shape_factor", "target_shape_factor",
        "source_spectral_index", "target_spectral_index",
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
    write_csv(outdir / out["edges_csv"], all_edges, edge_fields)
    write_csv(outdir / out["reference_core_edges_csv"], ref_rows, ref_fields)
    write_csv(outdir / out["core_metrics_csv"], all_core, metric_fields)
    write_csv(outdir / out["envelope_metrics_csv"], all_env, metric_fields)
    write_csv(outdir / out["real_vs_null_summary_csv"], summary, summary_fields)
    write_csv(outdir / out["family_summary_csv"], family_summary, ["node_family", "node_count", "node_ids"])
    write_csv(outdir / out["null_family_inventory_csv"], null_inventory, ["object_id", "null_family", "repeat_index"])

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_edge_table": cfg["inputs"]["edge_table"],
        "input_node_metadata": cfg["inputs"]["node_metadata"],
        "node_count": len(nodes),
        "real_edge_count": len(real_edges),
        "reference_core_edge_count": len(ref_core_edges),
        "reference_core_mode": cfg["reference_core"]["mode"],
        "object_count": len(object_weights),
        "null_family_counts": dict(Counter(x[1] for x in object_weights if x[1] != "real")),
        "row_counts": {
            "nodes_resolved": len(nodes),
            "edges": len(all_edges),
            "reference_core_edges": len(ref_rows),
            "core_metrics": len(all_core),
            "envelope_metrics": len(all_env),
            "real_vs_null_summary": len(summary),
            "family_summary": len(family_summary),
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
    parser = argparse.ArgumentParser(description="Run BMS-ST01 structure information specificity diagnostic.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
